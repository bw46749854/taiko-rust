#!/usr/bin/env python3
"""Validate OPS-0007 ticket advance engine wiring."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "operations/ticket_transition_policy.toml",
    "schemas/ticket_transition_schema.md",
    "scripts/loop_advance_ticket.py",
    "scripts/check_ticket_transition_static.py",
    "fixtures/loop_controller/merge_history_ops0006.json",
    "fixtures/loop_controller/merge_history_ops0007.json",
    "fixtures/loop_controller/merge_history_ops0009.json",
    "reports/loop/ticket_transitions/README.md",
    "scripts/loop_controller_github.sh",
    "scripts/loop_auto_merge_pr.sh",
    ".github/workflows/loop-controller.yml",
    "docs/63_ticket_lifecycle.md",
    "docs/88_auto_merge_loop_policy.md",
    "docs/89_loop_controller_state_machine.md",
    "docs/93_github_actions_auto_merge_controller.md",
    "operations/loop_policy.toml",
    "operations/auto_merge_policy.toml",
    "README.md",
    "AGENTS.md",
    "prompts/60_final_bootstrap_prompt.md",
]

REQUIRED_TERMS = {
    "operations/ticket_transition_policy.toml": [
        "status = \"canonical\"",
        "transition_engine = \"scripts/loop_advance_ticket.py\"",
        "static_check = \"scripts/check_ticket_transition_static.py\"",
        "transition_report_dir = \"reports/loop/ticket_transitions\"",
        "current_ready_ticket = \"TKT-0005\"",
        "forbid_tkt_ready_until_ops_complete = false",
        "api_key_required = false",
        "ai_workers_in_github_actions = false",
    ],
    "schemas/ticket_transition_schema.md": [
        "Status: canonical",
        "ticket_transition_plan.json",
        "scripts/loop_advance_ticket.py",
        "merged_ticket",
        "next_ready_ticket",
        "status_updates",
        "api_key_required",
        "ai_worker",
    ],
    "scripts/loop_advance_ticket.py": [
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "--merge-history",
        "--allow-dry-run-history",
        "forbid_tkt_ready_until_ops_complete",
        "ready_tickets_after",
        "schemas/ticket_transition_schema.md",
    ],
    "scripts/loop_controller_github.sh": [
        "scripts/loop_advance_ticket.py",
        "reports/loop/ticket_transitions",
        "candidate_verdict",
        "loop-controller",
    ],
    "scripts/loop_auto_merge_pr.sh": [
        "reports/loop/merge_history",
        "gh pr merge",
        "merged_at_utc",
        "dry-run command=gh pr merge",
    ],
    ".github/workflows/loop-controller.yml": [
        "scripts/check_ticket_transition_static.py",
        "reports/loop/ticket_transitions/",
        "scripts/loop_controller_github.sh --mode apply",
    ],
    "docs/63_ticket_lifecycle.md": [
        "Ticket advance engine",
        "Done",
        "Ready",
        "reports/loop/ticket_transitions/<run_id>.json",
    ],
    "docs/89_loop_controller_state_machine.md": [
        "OPS-0007 ticket advance states",
        "ticket_advance_pass",
        "ticket_advance_block",
        "ticket_advance_reject",
    ],
    "docs/93_github_actions_auto_merge_controller.md": [
        "scripts/loop_advance_ticket.py",
        "reports/loop/ticket_transitions/<run_id>.json",
        "merge history",
        "next ticket",
    ],
    "README.md": [
        "OPS-0007",
        "ticket advance engine",
        "scripts/loop_advance_ticket.py",
    ],
    "AGENTS.md": [
        "OPS-0007 Ticket advance engine",
        "Actions must not call AI providers",
    ],
    "prompts/60_final_bootstrap_prompt.md": [
        "OPS-0007",
        "scripts/loop_advance_ticket.py",
        "reports/loop/ticket_transitions",
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


def parse_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip()
    fail(f"missing Status line: {path}")


def validate_files_and_terms() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")
    for rel in ["scripts/loop_advance_ticket.py", "scripts/check_ticket_transition_static.py"]:
        if (ROOT / rel).stat().st_mode & 0o111 == 0:
            fail(f"{rel} must be executable")
    for rel, terms in REQUIRED_TERMS.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")


def validate_policy() -> None:
    if tomllib is None:
        return
    policy = tomllib.loads(read("operations/ticket_transition_policy.toml"))
    if policy.get("api_key_required") is not False:
        fail("ticket_transition_policy must not require API keys")
    if policy.get("ai_workers_in_github_actions") is not False:
        fail("ticket_transition_policy must keep AI workers out of GitHub Actions")
    if policy.get("max_ready_tickets") != 1:
        fail("ticket_transition_policy must enforce one Ready ticket")
    ops = policy.get("ops_migration") or {}
    if ops.get("current_ready_ticket") != "TKT-0005":
        fail("ops migration current_ready_ticket must be TKT-0005 after OPS migration")
    sequence = ops.get("sequence") or []
    if sequence[5:9] != ["OPS-0006", "OPS-0007", "OPS-0008", "OPS-0009"]:
        fail("OPS sequence around OPS-0007..OPS-0009 is not canonical")


def validate_current_ready_ticket() -> None:
    ready = []
    for ticket in sorted((ROOT / ".loop/tickets").glob("*.md")):
        if parse_status(ticket) == "Ready":
            ready.append(ticket.stem)
    if ready != ["TKT-0005"]:
        fail(f"expected only TKT-0005 to be Ready after OPS migration, got {ready}")
    for ticket in ["OPS-0007", "OPS-0008", "OPS-0009"]:
        if parse_status(ROOT / ".loop/tickets" / f"{ticket}.md") != "Done":
            fail(f"{ticket} must be Done after OPS migration")


def validate_transition_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        ticket_dir = tmpdir / "tickets"
        shutil.copytree(ROOT / ".loop/tickets", ticket_dir)
        # Fixture starts from the pre-advance state: OPS-0006 Ready, OPS-0007 Blocked.
        for ticket, status in [("OPS-0006", "Ready"), ("OPS-0007", "Blocked"), ("OPS-0008", "Blocked"), ("TKT-0005", "Blocked")]:
            path = ticket_dir / f"{ticket}.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(next(line for line in text.splitlines() if line.startswith("Status:")), f"Status: {status}", 1), encoding="utf-8")
        out = tmpdir / "transition.json"
        md = tmpdir / "transition.md"
        cmd = [
            str(ROOT / "scripts/loop_advance_ticket.py"),
            "--merge-history", str(ROOT / "fixtures/loop_controller/merge_history_ops0006.json"),
            "--ticket-dir", str(ticket_dir),
            "--mode", "apply",
            "--allow-dry-run-history",
            "--out", str(out),
            "--markdown", str(md),
            "--expect", "pass",
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            fail(f"loop_advance_ticket fixture failed: stdout={result.stdout} stderr={result.stderr}")
        plan = json.loads(out.read_text(encoding="utf-8"))
        if plan.get("merged_ticket") != "OPS-0006" or plan.get("next_ready_ticket") != "OPS-0007":
            fail("transition fixture did not advance OPS-0006 -> OPS-0007")
        if plan.get("ready_tickets_after") != ["OPS-0007"]:
            fail(f"transition fixture ready list mismatch: {plan.get('ready_tickets_after')}")
        if parse_status(ticket_dir / "OPS-0006.md") != "Done":
            fail("transition fixture did not mark OPS-0006 Done")
        if parse_status(ticket_dir / "OPS-0007.md") != "Ready":
            fail("transition fixture did not mark OPS-0007 Ready")

        # Final unlock fixture: OPS-0009 Done promotes TKT-0005 Ready after gate reports exist.
        ticket_dir2 = tmpdir / "tickets_final"
        shutil.copytree(ROOT / ".loop/tickets", ticket_dir2)
        for ticket, status in [("OPS-0009", "Ready"), ("TKT-0005", "Blocked")]:
            path = ticket_dir2 / f"{ticket}.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(next(line for line in text.splitlines() if line.startswith("Status:")), f"Status: {status}", 1), encoding="utf-8")
        out2 = tmpdir / "transition_final.json"
        md2 = tmpdir / "transition_final.md"
        cmd2 = [
            str(ROOT / "scripts/loop_advance_ticket.py"),
            "--merge-history", str(ROOT / "fixtures/loop_controller/merge_history_ops0009.json"),
            "--ticket-dir", str(ticket_dir2),
            "--mode", "apply",
            "--allow-dry-run-history",
            "--out", str(out2),
            "--markdown", str(md2),
            "--expect", "pass",
        ]
        result2 = subprocess.run(cmd2, cwd=ROOT, text=True, capture_output=True)
        if result2.returncode != 0:
            fail(f"final unlock fixture failed: stdout={result2.stdout} stderr={result2.stderr}")
        plan2 = json.loads(out2.read_text(encoding="utf-8"))
        if plan2.get("merged_ticket") != "OPS-0009" or plan2.get("next_ready_ticket") != "TKT-0005":
            fail("final unlock fixture did not advance OPS-0009 -> TKT-0005")
        if plan2.get("ready_tickets_after") != ["TKT-0005"]:
            fail(f"final unlock ready list mismatch: {plan2.get('ready_tickets_after')}")


def main() -> int:
    validate_files_and_terms()
    validate_policy()
    validate_current_ready_ticket()
    validate_transition_fixture()
    print("ticket transition static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
