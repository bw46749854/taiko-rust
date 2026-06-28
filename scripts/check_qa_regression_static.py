#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'docs/49_qa_regression_gate_contract.md',
    '.loop/gates/GATE-0080-qa-regression-ready.md',
    '.loop/tickets/TKT-0050.md',
    'reports/qa/README.md',
    '.github/workflows/phase1-loop.yml',
    'crates/taiko_cli/src/lib.rs',
]

for rel in REQUIRED_FILES:
    if not (ROOT / rel).is_file():
        print(f'missing: {rel}', file=sys.stderr)
        sys.exit(1)

cli = (ROOT / 'crates/taiko_cli/src/lib.rs').read_text(encoding='utf-8')
required_cli_terms = [
    'qa run',
    'qa compare',
    'qa verdict',
    'QaRunReport',
    'QaCompareReport',
    'QaVerdictReport',
    'render_qa_run',
    'render_qa_compare',
    'render_qa_verdict',
    'failure_report_required',
    'next_action',
]
for term in required_cli_terms:
    if term not in cli:
        print(f'missing QA CLI term: {term}', file=sys.stderr)
        sys.exit(1)

gate = (ROOT / '.loop/gates/GATE-0080-qa-regression-ready.md').read_text(encoding='utf-8')
for term in ['pass', 'reject', 'block', 'taiko_cli qa run', 'taiko_cli qa compare', 'taiko_cli qa verdict', 'worktree']:
    if term not in gate:
        print(f'GATE-0080 missing term: {term}', file=sys.stderr)
        sys.exit(1)

ticket = (ROOT / '.loop/tickets/TKT-0050.md').read_text(encoding='utf-8')
for term in ['TKT-0040', 'GATE-0070', 'GATE-0080', 'taiko_cli qa run', 'taiko_cli qa compare', 'taiko_cli qa verdict']:
    if term not in ticket:
        print(f'TKT-0050 missing term: {term}', file=sys.stderr)
        sys.exit(1)

tkt5 = (ROOT / '.loop/tickets/TKT-0005.md').read_text(encoding='utf-8')
for term in ['TKT-0060', 'GATE-0090']:
    if term not in tkt5:
        print(f'TKT-0005 does not depend on Phase1 gameplay entry gate prerequisite {term}', file=sys.stderr)
        sys.exit(1)

workflow = (ROOT / '.github/workflows/phase1-loop.yml').read_text(encoding='utf-8')
for term in ['cargo fmt --all --check', 'cargo clippy --workspace --all-targets -- -D warnings', 'cargo test --workspace', 'fixture validate', 'headless autoplay', 'timing analyze', 'qa run']:
    if term not in workflow:
        print(f'workflow missing command term: {term}', file=sys.stderr)
        sys.exit(1)

contract = (ROOT / 'docs/49_qa_regression_gate_contract.md').read_text(encoding='utf-8')
for term in ['failure_route_ready', 'required_reports', 'missing_current', 'missing_baseline', 'failure_report_required']:
    if term not in contract:
        print(f'QA contract missing term: {term}', file=sys.stderr)
        sys.exit(1)

print('qa regression static check passed')
