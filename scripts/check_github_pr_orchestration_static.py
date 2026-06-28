#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'docs/83_codex_surface_decision.md',
    'docs/84_github_pr_loop_contract.md',
    'scripts/loop_create_branch.sh',
    'scripts/loop_create_worktree.sh',
    'scripts/loop_open_pr.sh',
    'scripts/loop_apply_qa_verdict.py',
    'scripts/loop_merge_and_advance.sh',
    'scripts/check_github_pr_orchestration_static.py',
    '.github/pull_request_template.md',
    '.github/workflows/loop-pr-gate.yml',
    '.github/workflows/codex-review.yml',
    '.github/codex/prompts/review.md',
    'templates/session_run_metadata_template.toml',
    '.gitignore',
]

REQUIRED_TERMS = {
    'docs/83_codex_surface_decision.md': [
        'Codex Cloud', 'Codex CLI', 'GitHub Actions', 'Codex GitHub review', 'Rust environment rule'
    ],
    'docs/84_github_pr_loop_contract.md': [
        'scripts/loop_create_worktree.sh', 'scripts/loop_open_pr.sh', 'scripts/loop_apply_qa_verdict.py',
        'scripts/loop_merge_and_advance.sh', 'pass', 'reject', 'block', 'Self-approval prevention'
    ],
    '.github/pull_request_template.md': ['Ticket ID', 'QA transition', 'Asset policy', 'Self-approval prevention', 'Codex review'],
    '.github/workflows/loop-pr-gate.yml': ['check_github_pr_orchestration_static.py', 'validate_no_user_assets.sh'],
    '.github/workflows/codex-review.yml': ['Plus-plan deterministic review request', 'OPENAI_API_KEY is intentionally not used', 'prompt-file', 'codex-review-request.md'],
    'templates/session_run_metadata_template.toml': ['implementation_session_id', 'review_session_id', 'qa_session_id', 'self_approval_check'],
    'scripts/README.md': ['loop_create_worktree.sh', 'loop_open_pr.sh', 'loop_apply_qa_verdict.py', 'loop_merge_and_advance.sh'],
    'README.md': ['GitHub PR loop', 'ticket advance'],
    'AGENTS.md': ['GitHub PR / auto-merge / ticket advancement', 'PR cannot merge'],
}

EXECUTABLE = [
    'scripts/loop_create_branch.sh',
    'scripts/loop_create_worktree.sh',
    'scripts/loop_open_pr.sh',
    'scripts/loop_merge_and_advance.sh',
    'scripts/check_github_pr_orchestration_static.py',
    'scripts/loop_apply_qa_verdict.py',
]

DEPRECATED = {'taiko_core', 'taiko_input', 'taiko_telemetry', 'taiko_app', 'taiko_tools', 'taiko_headless', 'taiko_analyzer'}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def main() -> int:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f'missing: {rel}')

    for rel, terms in REQUIRED_TERMS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for term in terms:
            if term not in text:
                fail(f'{rel} missing required term: {term}')
        if rel.startswith('docs/8') or rel.startswith('.github/') or rel.startswith('templates/'):
            for deprecated in DEPRECATED:
                if deprecated in text:
                    fail(f'{rel} contains deprecated crate name: {deprecated}')

    for rel in EXECUTABLE:
        mode = (ROOT / rel).stat().st_mode
        if mode & 0o111 == 0:
            fail(f'not executable: {rel}')

    gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
    for term in ['worktrees/', 'target/', 'reports/session_metadata/*.local.toml']:
        if term not in gitignore:
            fail(f'.gitignore missing {term}')

    print('github pr orchestration static check passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
