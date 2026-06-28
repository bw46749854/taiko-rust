#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'operations/phase1_feature_ticket_manifest.toml'
REQUIRED_FILES = [
    'docs/74_phase1_feature_loop_entry_contract.md',
    'docs/75_phase1_feature_ticket_manifest_schema.md',
    'docs/76_phase1_feature_acceptance_command_matrix.md',
    '.loop/gates/GATE-0090-phase1-feature-loop-ready.md',
    '.loop/tickets/TKT-0060.md',
    'operations/phase1_feature_ticket_manifest.toml',
    'reports/phase1_feature_loop/README.md',
    'crates/taiko_cli/src/lib.rs',
]
DEPRECATED = {'taiko_core', 'taiko_input', 'taiko_telemetry', 'taiko_app', 'taiko_tools', 'taiko_headless', 'taiko_analyzer'}
REQUIRED_FEATURE_TICKETS = [
    'TKT-0005', 'TKT-0006', 'TKT-0007', 'TKT-0008', 'TKT-0009',
    'TKT-0010', 'TKT-0011', 'TKT-0012', 'TKT-0013', 'TKT-0014',
    'TKT-0015', 'TKT-0035', 'TKT-0075',
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def parse_manifest(text: str):
    top = {}
    entries = []
    current = None
    for raw_line in text.splitlines():
        line = raw_line.split('#', 1)[0].strip()
        if not line:
            continue
        if line == '[[tickets]]':
            if current is not None:
                entries.append(current)
            current = {}
            continue
        if '=' not in line:
            continue
        key, value = [part.strip() for part in line.split('=', 1)]
        target = current if current is not None else top
        target[key] = value
    if current is not None:
        entries.append(current)
    return top, entries


def string_value(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def array_values(value: str):
    value = value.strip()
    if not (value.startswith('[') and value.endswith(']')):
        return []
    return re.findall(r'"([^"]+)"', value)


def bool_value(value: str) -> bool:
    return value.strip().lower() == 'true'


def main() -> int:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f'missing: {rel}')

    text = MANIFEST.read_text(encoding='utf-8')
    for deprecated in DEPRECATED:
        if deprecated in text:
            fail(f'manifest contains deprecated crate name: {deprecated}')

    top, entries = parse_manifest(text)
    declared = int(top.get('feature_ticket_count', '0'))
    if declared != len(entries):
        fail(f'feature_ticket_count mismatch: declared {declared}, found {len(entries)}')
    if string_value(top.get('first_feature_ticket', '')) != 'TKT-0005':
        fail('first_feature_ticket must be TKT-0005')
    if string_value(top.get('required_entry_gate', '')) != 'GATE-0090':
        fail('required_entry_gate must be GATE-0090')
    if string_value(top.get('required_qa_gate', '')) != 'GATE-0080':
        fail('required_qa_gate must be GATE-0080')
    if not bool_value(top.get('failure_route_required', 'false')):
        fail('top-level failure_route_required must be true')
    if not bool_value(top.get('qa_verdict_required', 'false')):
        fail('top-level qa_verdict_required must be true')

    ticket_ids = [string_value(entry.get('ticket_id', '')) for entry in entries]
    if ticket_ids != REQUIRED_FEATURE_TICKETS:
        fail(f'feature ticket order mismatch: {ticket_ids}')

    for entry in entries:
        ticket_id = string_value(entry.get('ticket_id', ''))
        ticket_file = ROOT / f'.loop/tickets/{ticket_id}.md'
        if not ticket_file.is_file():
            fail(f'missing feature ticket file: {ticket_id}')
        if not bool_value(entry.get('qa_required', 'false')):
            fail(f'{ticket_id} qa_required must be true')
        if not bool_value(entry.get('failure_route_required', 'false')):
            fail(f'{ticket_id} failure_route_required must be true')
        commands = array_values(entry.get('required_commands', '[]'))
        joined = '\n'.join(commands)
        for term in ['cargo test --workspace', 'taiko_cli qa run', 'taiko_cli qa verdict']:
            if term not in joined:
                fail(f'{ticket_id} required_commands missing {term}')
        for rel in array_values(entry.get('acceptance_docs', '[]')):
            if not (ROOT / rel).exists():
                fail(f'{ticket_id} references missing acceptance doc: {rel}')
        for crate in array_values(entry.get('primary_crates', '[]')):
            if not (ROOT / 'crates' / crate / 'Cargo.toml').is_file():
                fail(f'{ticket_id} references missing canonical crate: {crate}')

        ticket_text = ticket_file.read_text(encoding='utf-8')
        for required in ['taiko_cli qa run', 'taiko_cli qa verdict', 'Next-ticket transition evidence']:
            if required not in ticket_text:
                fail(f'{ticket_id} ticket missing required evidence term: {required}')

    tkt5 = (ROOT / '.loop/tickets/TKT-0005.md').read_text(encoding='utf-8')
    for term in ['TKT-0060', 'GATE-0090', 'docs/74_phase1_feature_loop_entry_contract.md']:
        if term not in tkt5:
            fail(f'TKT-0005 missing Phase1 gameplay entry gate prerequisite term: {term}')

    tkt60 = (ROOT / '.loop/tickets/TKT-0060.md').read_text(encoding='utf-8')
    for term in ['TKT-0050', 'GATE-0080', 'GATE-0090', 'taiko_cli phase1 feature validate', 'taiko_cli phase1 feature plan']:
        if term not in tkt60:
            fail(f'TKT-0060 missing term: {term}')

    gate = (ROOT / '.loop/gates/GATE-0090-phase1-feature-loop-ready.md').read_text(encoding='utf-8')
    for term in ['pass', 'reject', 'block', 'taiko_cli phase1 feature validate', 'taiko_cli phase1 feature plan', 'TKT-0005']:
        if term not in gate:
            fail(f'GATE-0090 missing term: {term}')

    cli = (ROOT / 'crates/taiko_cli/src/lib.rs').read_text(encoding='utf-8')
    for term in ['phase1 feature validate', 'phase1 feature plan', 'Phase1FeatureTicket', 'Phase1FeaturePlanReport', 'render_phase1_feature_plan']:
        if term not in cli:
            fail(f'CLI missing feature-loop term: {term}')

    workflow = (ROOT / '.github/workflows/phase1-loop.yml').read_text(encoding='utf-8')
    for term in ['check_phase1_feature_loop_static.py', 'phase1 feature validate', 'phase1 feature plan']:
        if term not in workflow:
            fail(f'workflow missing Phase1 gameplay entry gate term: {term}')

    result = subprocess.run([sys.executable, str(ROOT / 'scripts/check_phase1_entry_state_consistency.py')], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        fail(result.stderr.strip() or result.stdout.strip() or 'phase1 entry state consistency check failed')

    print('phase1 feature loop static check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
