#!/usr/bin/env python3
"""Static validation for canonical Rust preflight wiring."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'docs/85_rust_enabled_preflight_gate.md',
    'scripts/run_rust_preflight.sh',
    'scripts/check_runtime_evidence_files.py',
    'scripts/check_rust_preflight_static.py',
    '.github/workflows/rust-preflight.yml',
    'reports/preflight/README.md',
    'templates/rust_preflight_report_template.md',
]

REQUIRED_TERMS = {
    'docs/85_rust_enabled_preflight_gate.md': [
        'Rust-enabled preflight gate',
        'scripts/run_rust_preflight.sh --scope current-package',
        'reports/preflight/latest/rust_preflight_report.json',
        'scripts/check_runtime_evidence_files.py',
        'GATE-0030',
        'block',
        'reject',
        'pass',
    ],
    'scripts/run_rust_preflight.sh': [
        'cargo fmt --all --check',
        'cargo clippy --workspace --all-targets -- -D warnings',
        'cargo test --workspace',
        'loop inspect tickets --format json',
        'qa verdict --input',
        'phase1 feature plan',
        'rust_preflight_report.json',
    ],
    'scripts/check_runtime_evidence_files.py': [
        'rust-preflight.v1',
        'current-package',
        '--require-pass',
        'loop_gate_0000',
        'phase1_feature_plan',
    ],
    '.github/workflows/rust-preflight.yml': [
        'scripts/run_rust_preflight.sh --scope current-package',
        'scripts/check_runtime_evidence_files.py',
        'upload-artifact',
        'rust-preflight-report',
    ],
    'reports/preflight/README.md': [
        'reports/preflight/latest',
        'rust_preflight_report.json',
        'user-selected assets',
    ],
    'templates/rust_preflight_report_template.md': [
        'Rust Preflight Report',
        'Verdict',
        'Command evidence',
    ],
    '.loop/tickets/TKT-0001.md': [
        'scripts/run_rust_preflight.sh --scope current-package',
        'scripts/check_runtime_evidence_files.py',
        'rust_preflight_report.json',
    ],
    '.loop/gates/GATE-0030-loop-cli-ready.md': [
        'Rust preflight evidence',
        'scripts/run_rust_preflight.sh --scope current-package',
        'scripts/check_runtime_evidence_files.py',
    ],
    'scripts/README.md': [
        'run_rust_preflight.sh',
        'check_runtime_evidence_files.py',
        'check_rust_preflight_static.py',
    ],
    'README.md': [
        'Rust-enabled Preflight Gate',
    ],
    'AGENTS.md': [
        'Rust preflight',
    ],
}

EXECUTABLE = [
    'scripts/run_rust_preflight.sh',
    'scripts/check_runtime_evidence_files.py',
    'scripts/check_rust_preflight_static.py',
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f'missing: {rel}')

    for rel, terms in REQUIRED_TERMS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for term in terms:
            if term not in text:
                fail(f'{rel} missing required term: {term}')

    for rel in EXECUTABLE:
        if (ROOT / rel).stat().st_mode & 0o111 == 0:
            fail(f'not executable: {rel}')

    gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
    if 'reports/preflight/latest/' not in gitignore:
        fail('.gitignore missing reports/preflight/latest/')

    bootstrap = (ROOT / 'scripts/check_bootstrap_consistency.sh').read_text(encoding='utf-8')
    for rel in REQUIRED_FILES:
        if rel not in bootstrap:
            fail(f'bootstrap consistency does not require {rel}')
    if 'scripts/check_rust_preflight_static.py' not in bootstrap:
        fail('bootstrap consistency does not run check_rust_preflight_static.py')

    print('rust preflight static check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
