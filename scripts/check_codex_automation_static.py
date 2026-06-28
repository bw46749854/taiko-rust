#!/usr/bin/env python3
"""Static validation for ChatGPT-plan Codex automation Codex Automation operation."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "docs/92_codex_plus_automation_operation.md",
    "operations/codex_automation_policy.toml",
    "prompts/70_codex_automation_loop_runner.md",
    "prompts/71_codex_cloud_ticket_worker.md",
    "scripts/render_next_codex_prompt.py",
    "reports/loop_automation/README.md",
    ".github/workflows/codex-review.yml",
]

CHECKS = [
    ("docs/92_codex_plus_automation_operation.md", [
        "Status: canonical",
        "ChatGPT Plus",
        "Codex App Automations",
        "scripts/render_next_codex_prompt.py",
        "openai/codex-action@v1",
        "must not invoke",
        "usage_wait",
    ]),
    ("operations/codex_automation_policy.toml", [
        "status = \"canonical\"",
        "api_key_required = false",
        "openai_codex_action_allowed = false",
        "github_actions_may_call_ai = false",
        "recommended_minutes = 60",
        "max_parallel_codex_workers = 1",
    ]),
    ("prompts/70_codex_automation_loop_runner.md", [
        "Status: canonical",
        "scripts/render_next_codex_prompt.py --mode automation",
        "reports/loop/<run_id>/next_codex_prompt.md",
        "Do not require `OPENAI_API_KEY`",
    ]),
    ("prompts/71_codex_cloud_ticket_worker.md", [
        "Status: canonical",
        "scripts/render_next_codex_prompt.py --mode ticket-worker",
        "Do not require `OPENAI_API_KEY`",
        "Do not write `reports/qa/*.verdict.json`",
    ]),
    ("scripts/render_next_codex_prompt.py", [
        "does not call",
        "OPENTAIKO_LOOP_RUN_ID",
        "next_codex_prompt.md",
        "usage_wait",
        "openai/codex-action@v1",
    ]),
    (".github/workflows/codex-review.yml", [
        "Plus-plan deterministic review request",
        "OPENAI_API_KEY is intentionally not used",
        "prompt-file",
        "codex-review-request.md",
    ]),
    ("docs/87_secret_and_network_policy.md", [
        "Plus-plan ChatGPT-plan Codex operation rule",
        "openai/codex-action@v1",
        "not used",
        "GitHub Actions must not call AI workers",
    ]),
    ("docs/83_codex_surface_decision.md", [
        "ChatGPT-plan Codex automation update",
        "Codex App Automations",
        "API-key GitHub Action worker is not the primary surface",
    ]),
    ("scripts/ci_local_equivalent.sh", ["scripts/check_codex_automation_static.py"]),
    ("scripts/check_bootstrap_consistency.sh", [
        "docs/92_codex_plus_automation_operation.md",
        "operations/codex_automation_policy.toml",
        "scripts/check_codex_automation_static.py",
    ]),
]

FORBIDDEN_IN_WORKFLOWS = [
    "uses: openai/codex-action@v1",
    "openai-api-key:",
    "secrets.OPENAI_API_KEY",
    "secrets.CODEX_API_KEY",
]


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            failures.append(f"missing required Codex automation file: {rel}")
    for rel, terms in CHECKS:
        path = ROOT / rel
        if not path.is_file():
            failures.append(f"missing file for term check: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                failures.append(f"{rel} missing term: {term}")
    for wf in (ROOT / ".github/workflows").glob("*.yml"):
        text = wf.read_text(encoding="utf-8")
        for term in FORBIDDEN_IN_WORKFLOWS:
            if term in text:
                failures.append(f"{wf.relative_to(ROOT)} contains forbidden Plus-plan workflow term: {term}")
    script = ROOT / "scripts/render_next_codex_prompt.py"
    if script.is_file() and not (script.stat().st_mode & 0o111):
        failures.append("scripts/render_next_codex_prompt.py must be executable")
    check = ROOT / "scripts/check_codex_automation_static.py"
    if check.is_file() and not (check.stat().st_mode & 0o111):
        failures.append("scripts/check_codex_automation_static.py must be executable")
    if failures:
        print("codex automation static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("codex automation static check passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
