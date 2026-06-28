#!/usr/bin/env python3
"""Static and evidence validation for the auto-merge controller.

Default invocation is a no-network static check. Optional --metadata/--qa validates
candidate evidence files before an auto-merge attempt. OPS-0006 also validates
candidate discovery fixtures without requiring GitHub network access.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import check_session_separation

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/93_github_actions_auto_merge_controller.md",
    "operations/auto_merge_policy.toml",
    ".github/workflows/loop-controller.yml",
    "scripts/check_auto_merge_conditions.py",
    "scripts/select_auto_merge_candidate.py",
    "scripts/loop_controller_github.sh",
    "scripts/loop_auto_merge_pr.sh",
    "scripts/loop_revert_last_merge.sh",
    "schemas/auto_merge_candidate_schema.md",
    "schemas/qa_verdict_schema.md",
    "fixtures/loop_controller/pass_candidate.json",
    "fixtures/loop_controller/reject_candidate.json",
    "fixtures/loop_controller/block_candidate.json",
    "reports/loop/candidates/README.md",
    "reports/loop/merge_history/README.md",
    "reports/loop/ticket_transitions/README.md",
    "scripts/check_ticket_transition_static.py",
    "scripts/loop_advance_ticket.py",
    "schemas/ticket_transition_schema.md",
    "operations/ticket_transition_policy.toml",
    "reports/regression/README.md",
    "scripts/check_github_actions_gate_static.py",
]

REQUIRED_TERMS = {
    "docs/93_github_actions_auto_merge_controller.md": [
        "Status: canonical",
        "GitHub Actions Auto-Merge Controller",
        "OPENAI_API_KEY",
        "openai/codex-action@v1",
        "reports/loop/merge_history/<run_id>.json",
        "scripts/loop_auto_merge_pr.sh",
        "scripts/select_auto_merge_candidate.py",
        "reports/loop/candidates/candidate_plan.json",
        "scripts/loop_advance_ticket.py",
        "reports/loop/ticket_transitions/<run_id>.json",
        "QA verdict is `reject`",
        "QA verdict is `block`",
    ],
    "operations/auto_merge_policy.toml": [
        "canonical",
        "auto_merge_enabled = true",
        "ai_workers_in_github_actions = false",
        "api_key_required = false",
        "openai_codex_action_allowed = false",
        "required_label = \"loop:automerge\"",
        "merge_method = \"squash\"",
        "max_merge_candidates_per_run = 1",
        "candidate_plan_path = \"reports/loop/candidates/candidate_plan.json\"",
        "reports/loop/merge_history",
        "reports/regression",
        "ticket_transition_engine = \"scripts/loop_advance_ticket.py\"",
        "ticket_transition_report_dir = \"reports/loop/ticket_transitions\"",
        "workflow_run_success_guard_required = true",
        "privileged_workflow_may_checkout_pr_head = false",
        "loop-pr-gate / loop-pr-gate",
        "rust-preflight / rust-preflight",
        "phase1-loop / phase1-loop",
        "phase1-gameplay-entry / phase1-gameplay-entry",
    ],
    ".github/workflows/loop-controller.yml": [
        "name: loop-controller",
        "workflow_run:",
        "workflow_dispatch:",
        "schedule:",
        "scripts/check_auto_merge_conditions.py",
        "scripts/loop_controller_github.sh --mode plan",
        "scripts/loop_controller_github.sh --mode apply",
        "contents: write",
        "pull-requests: write",
        "concurrency:",
        "group: loop-controller-main",
        "github.event.workflow_run.conclusion == 'success'",
        "scripts/check_github_actions_gate_static.py",
        "scripts/check_ticket_transition_static.py",
    ],
    "scripts/select_auto_merge_candidate.py": [
        "loop:automerge",
        "statusCheckRollup",
        "max_merge_candidates_per_run",
        "reports/session_metadata/",
        "reports/qa/",
        "--expect",
        "--require-pass",
    ],
    "scripts/loop_controller_github.sh": [
        "set -euo pipefail",
        "loop-controller",
        "scripts/check_auto_merge_conditions.py",
        "scripts/select_auto_merge_candidate.py",
        "reports/loop/candidates/candidate_plan.json",
        "scripts/loop_advance_ticket.py",
        "reports/loop/ticket_transitions",
        "OPENAI_API_KEY is intentionally unused",
    ],
    "scripts/loop_auto_merge_pr.sh": [
        "set -euo pipefail",
        "gh pr merge",
        "--squash",
        "reports/loop/merge_history",
        "scripts/check_auto_merge_conditions.py",
    ],

    "scripts/loop_advance_ticket.py": [
        "--merge-history",
        "ready_tickets_after",
        "schemas/ticket_transition_schema.md",
        "api_key_required",
        "ai_worker",
    ],
    "schemas/auto_merge_candidate_schema.md": [
        "Status: canonical",
        "candidate_plan.json",
        "loop:automerge",
        "max_merge_candidates_per_run",
        "pass",
        "reject",
        "block",
    ],
    "README.md": [
        "OPS-0006",
        "OPS-0007",
        "auto-merge candidate discovery",
        "ticket advance engine",
        "scripts/select_auto_merge_candidate.py",
        "scripts/loop_advance_ticket.py",
    ],
    "AGENTS.md": [
        "OPS-0006 Auto-merge candidate discovery",
        "OPS-0007 Ticket advance engine",
        "GitHub Actions auto-merge controller",
        "Actions must not call AI providers",
    ],
    "prompts/60_final_bootstrap_prompt.md": [
        "Status: canonical",
        "OPS-0006",
        "OPS-0007",
        "scripts/select_auto_merge_candidate.py",
        "scripts/loop_advance_ticket.py",
    ],
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def parse_toml(path: Path) -> dict:
    if tomllib is None:
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def validate_static() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    for rel in ["scripts/select_auto_merge_candidate.py", "scripts/check_auto_merge_conditions.py", "scripts/loop_controller_github.sh"]:
        if (ROOT / rel).stat().st_mode & 0o111 == 0:
            fail(f"{rel} must be executable")

    for rel, terms in REQUIRED_TERMS.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")

    workflow_text = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / ".github/workflows").glob("*.yml"))
    for term in ["openai/codex-action@v1", "secrets.OPENAI_API_KEY", "secrets.CODEX_API_KEY"]:
        if term in workflow_text:
            fail(f"workflow contains forbidden AI API worker term: {term}")

    bootstrap = read("scripts/check_bootstrap_consistency.sh")
    ci = read("scripts/ci_local_equivalent.sh")
    for term in [
        "docs/93_github_actions_auto_merge_controller.md",
        "operations/auto_merge_policy.toml",
        ".github/workflows/loop-controller.yml",
        "scripts/check_auto_merge_conditions.py",
        "scripts/select_auto_merge_candidate.py",
        "schemas/auto_merge_candidate_schema.md",
    "schemas/qa_verdict_schema.md",
        "fixtures/loop_controller/pass_candidate.json",
        "reports/loop/candidates/README.md",
        "scripts/loop_controller_github.sh",
        "scripts/loop_auto_merge_pr.sh",
        "scripts/loop_revert_last_merge.sh",
    ]:
        if term not in bootstrap:
            fail(f"check_bootstrap_consistency.sh missing auto-merge candidate term: {term}")
    if "scripts/select_auto_merge_candidate.py" not in ci:
        fail("ci_local_equivalent.sh must run select_auto_merge_candidate.py fixture checks")
    if "scripts/check_ticket_transition_static.py" not in ci or "scripts/loop_advance_ticket.py" not in ci:
        fail("ci_local_equivalent.sh must run ticket transition fixture checks")

    policy = parse_toml(ROOT / "operations/auto_merge_policy.toml")
    if policy:
        if policy.get("api_key_required") is not False:
            fail("auto_merge_policy.toml must set api_key_required = false")
        if policy.get("ai_workers_in_github_actions") is not False:
            fail("auto_merge_policy.toml must set ai_workers_in_github_actions = false")
        if policy.get("merge_method") != "squash":
            fail("auto_merge_policy.toml must set merge_method = squash")
        if policy.get("max_merge_candidates_per_run") != 1:
            fail("auto_merge_policy.toml must set max_merge_candidates_per_run = 1")
        if policy.get("candidate_plan_path") != "reports/loop/candidates/candidate_plan.json":
            fail("auto_merge_policy.toml must set candidate_plan_path")
        if policy.get("ticket_transition_engine") != "scripts/loop_advance_ticket.py":
            fail("auto_merge_policy.toml must set ticket_transition_engine")
        required = {"loop-pr-gate / loop-pr-gate", "rust-preflight / rust-preflight", "phase1-loop / phase1-loop", "phase1-gameplay-entry / phase1-gameplay-entry"}
        found = set(policy.get("required_checks") or [])
        missing = sorted(required - found)
        if missing:
            fail("auto_merge_policy.toml missing required checks: " + ", ".join(missing))


def parse_simple_toml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_candidate(metadata: str | None, qa: str | None, ticket: str | None, head_sha: str | None) -> None:
    if not metadata and not qa and not ticket:
        return
    if not metadata:
        fail("--metadata is required for candidate validation")
    metadata_path = ROOT / metadata
    if not metadata_path.is_file():
        fail(f"missing metadata file: {metadata}")
    meta = parse_simple_toml(metadata_path)
    required = [
        "ticket_id",
        "implementation_session_id",
        "review_session_id",
        "qa_session_id",
        "implementation_worktree",
        "review_worktree",
        "qa_worktree",
        "implementation_branch",
        "qa_verdict_path",
    ]
    missing = [k for k in required if not meta.get(k)]
    if missing:
        fail("metadata missing required keys: " + ", ".join(missing))

    resolved_ticket = ticket or meta["ticket_id"]
    if meta["ticket_id"] != resolved_ticket:
        fail(f"ticket mismatch: arg={resolved_ticket} metadata={meta['ticket_id']}")
    if len({meta["implementation_session_id"], meta["review_session_id"], meta["qa_session_id"]}) != 3:
        fail("implementation/review/qa session IDs must be distinct")
    if len({meta["implementation_worktree"], meta["review_worktree"], meta["qa_worktree"]}) != 3:
        fail("implementation/review/qa worktrees must be distinct")
    if not meta["implementation_worktree"].endswith(f"/{resolved_ticket}") or "/impl/" not in meta["implementation_worktree"]:
        fail("implementation_worktree must be under worktrees/impl/<ticket>")
    if not meta["review_worktree"].endswith(f"/{resolved_ticket}") or "/review/" not in meta["review_worktree"]:
        fail("review_worktree must be under worktrees/review/<ticket>")
    if not meta["qa_worktree"].endswith(f"/{resolved_ticket}") or "/qa/" not in meta["qa_worktree"]:
        fail("qa_worktree must be under worktrees/qa/<ticket>")
    if head_sha and meta.get("head_sha") and meta["head_sha"] != head_sha:
        fail("metadata head_sha does not match PR head SHA")

    qa_path = ROOT / (qa or meta["qa_verdict_path"])
    if not qa_path.is_file():
        fail(f"missing QA verdict file: {qa_path.relative_to(ROOT)}")
    verdict = json.loads(qa_path.read_text(encoding="utf-8"))
    qa_issues = check_session_separation.validate_qa_verdict_payload(verdict, meta)
    if qa_issues:
        fail("QA verdict schema validation failed: " + "; ".join(qa_issues))
    if verdict.get("verdict") != "pass":
        fail(f"refusing auto-merge for QA verdict: {verdict.get('verdict')}")


def validate_candidate_fixtures() -> None:
    script = ROOT / "scripts/select_auto_merge_candidate.py"
    fixture_expectations = [
        ("fixtures/loop_controller/pass_candidate.json", "pass"),
        ("fixtures/loop_controller/reject_candidate.json", "reject"),
        ("fixtures/loop_controller/block_candidate.json", "block"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for fixture, expected in fixture_expectations:
            out = tmpdir / f"{Path(fixture).stem}.json"
            md = tmpdir / f"{Path(fixture).stem}.md"
            cmd = [str(script), "--input", str(ROOT / fixture), "--out", str(out), "--markdown", str(md), "--expect", expected]
            result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
            if result.returncode != 0:
                fail(f"candidate fixture {fixture} failed: stdout={result.stdout} stderr={result.stderr}")
            plan = json.loads(out.read_text(encoding="utf-8"))
            if plan.get("verdict") != expected:
                fail(f"candidate fixture {fixture} expected {expected}, got {plan.get('verdict')}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata")
    parser.add_argument("--qa")
    parser.add_argument("--ticket")
    parser.add_argument("--head-sha")
    parser.add_argument("--pr-gate", action="store_true")
    args = parser.parse_args()

    validate_static()
    validate_candidate_fixtures()
    validate_candidate(args.metadata, args.qa, args.ticket, args.head_sha)
    print("auto-merge conditions static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
