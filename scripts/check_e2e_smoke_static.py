#!/usr/bin/env python3
"""Static and dry-run validation for E2E smoke loop loop."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/94_e2e_smoke_loop_verification.md",
    "operations/e2e_smoke_policy.toml",
    ".github/workflows/e2e-smoke-loop.yml",
    "scripts/run_e2e_smoke_loop.sh",
    "scripts/check_e2e_smoke_static.py",
    "reports/e2e_smoke/README.md",
]

REQUIRED_TERMS = {
    "docs/94_e2e_smoke_loop_verification.md": [
        "Status: canonical",
        "E2E Smoke Loop Verification",
        "pass",
        "reject",
        "block",
        "retry",
        "revert",
        "advance",
        "handoff",
        "publication",
        "scripts/run_e2e_smoke_loop.sh --scenario all --dry-run",
        "OPENAI_API_KEY",
        "openai/codex-action@v1",
    ],
    "operations/e2e_smoke_policy.toml": [
        "status = \"canonical\"",
        "api_key_required = false",
        "ai_workers_in_github_actions = false",
        "openai_codex_action_allowed = false",
        "phase1_gameplay_allowed = true",
        "default_mode = \"dry-run\"",
    ],
    ".github/workflows/e2e-smoke-loop.yml": [
        "name: e2e-smoke-loop",
        "workflow_dispatch:",
        "scripts/check_e2e_smoke_static.py",
        "scripts/run_e2e_smoke_loop.sh --scenario all --dry-run",
        "e2e-smoke-report",
    ],
    "scripts/run_e2e_smoke_loop.sh": [
        "set -euo pipefail",
        "--scenario pass|reject|block|retry|revert|advance|handoff|publication|all",
        "scripts/check_auto_merge_conditions.py",
        "scripts/loop_auto_merge_pr.sh",
        "scripts/loop_revert_last_merge.sh",
        "OPENAI_API_KEY",
        "TKT-REPAIR-SMOKE-REJECT",
        "TKT-ENV-SMOKE-BLOCK",
    ],
    "README.md": [
        "E2E smoke loop",
        "E2E smoke loop",
        "scripts/run_e2e_smoke_loop.sh --scenario all --dry-run",
    ],
    "AGENTS.md": [
        "E2E smoke loop operational note",
        "E2E smoke loop",
        "Actions must not call AI providers",
    ],
    "prompts/60_final_bootstrap_prompt.md": [
        "Status: canonical",
        "docs/94_e2e_smoke_loop_verification.md",
        "scripts/check_e2e_smoke_static.py",
    ],
    "scripts/ci_local_equivalent.sh": ["scripts/check_e2e_smoke_static.py"],
    "scripts/check_bootstrap_consistency.sh": [
        "docs/94_e2e_smoke_loop_verification.md",
        "operations/e2e_smoke_policy.toml",
        "scripts/run_e2e_smoke_loop.sh",
        "scripts/check_e2e_smoke_static.py",
    ],
}

FORBIDDEN_WORKFLOW_TERMS = ["openai/codex-action@v1", "secrets.OPENAI_API_KEY"]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def validate_static() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required E2E smoke loop file: {rel}")
    for rel, terms in REQUIRED_TERMS.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")
    workflows = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / ".github/workflows").glob("*.yml"))
    for term in FORBIDDEN_WORKFLOW_TERMS:
        if term in workflows:
            fail(f"workflow contains forbidden AI API worker term: {term}")
    script = ROOT / "scripts/run_e2e_smoke_loop.sh"
    if not (script.stat().st_mode & 0o111):
        fail("scripts/run_e2e_smoke_loop.sh must be executable")


def validate_smoke_run() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="opentaiko-step22-smoke-"))
    try:
        subprocess.check_call([
            str(ROOT / "scripts/run_e2e_smoke_loop.sh"),
            "--scenario", "all",
            "--run-id", "SMOKE-STATIC-CHECK",
            "--out", str(tmp),
            "--dry-run",
        ], cwd=ROOT)
        required = [
            "summary.json",
            "summary.md",
            "pass/session_metadata.toml",
            "pass/qa.verdict.json",
            "pass/merge_history/SMOKE-STATIC-CHECK-pass.json",
            "advance/ticket_transition.json",
            "handoff/latest.json",
            "publication/publication_readiness.json",
            "reject/failure.md",
            "reject/materialized_tickets/TKT-REPAIR-SMOKE-REJECT.md",
            "block/failure.md",
            "block/materialized_tickets/TKT-ENV-SMOKE-BLOCK.md",
            "retry/retry_budget.json",
            "revert/regression/SMOKE-STATIC-CHECK-revert.json",
        ]
        missing = [rel for rel in required if not (tmp / rel).is_file()]
        if missing:
            fail("smoke run missing evidence: " + ", ".join(missing))
        summary = json.loads((tmp / "summary.json").read_text(encoding="utf-8"))
        if summary.get("status") != "pass":
            fail("smoke summary did not pass")
        for scenario in ["pass", "reject", "block", "retry", "revert", "advance", "handoff", "publication"]:
            if summary.get("scenarios", {}).get(scenario) != "pass":
                fail(f"smoke scenario did not pass: {scenario}")
        retry = json.loads((tmp / "retry/retry_budget.json").read_text(encoding="utf-8"))
        if retry.get("verdict") != "block":
            fail("retry scenario must produce block verdict")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-only", action="store_true", help="Validate E2E smoke loop wiring without executing the temporary smoke run")
    args = parser.parse_args()
    validate_static()
    if not args.static_only:
        validate_smoke_run()
    print("E2E smoke loop static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
