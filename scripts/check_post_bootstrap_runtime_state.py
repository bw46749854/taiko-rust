#!/usr/bin/env python3
"""Validate post-bootstrap runtime state after the OPS migration rail.

This check is intentionally separate from check_bootstrap_consistency.sh:
bootstrap consistency validates package invariants, while this script validates
current operational state such as Ready-ticket count, automation arm state,
worker handoff freshness, and the Phase1 gate chain.
"""
from __future__ import annotations

import argparse
import json
import os
import re
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

FALSE_EQUIVALENTS = {"", "0", "false", "no", "off", "disarmed"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        fail(f"check failed: {' '.join(cmd)}\nstdout={result.stdout}\nstderr={result.stderr}")
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def status(path: Path) -> str:
    m = re.search(r"^Status:\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
    if not m:
        fail(f"missing Status line: {path.relative_to(ROOT).as_posix()}")
    return m.group(1).strip()


def ready_tickets() -> list[str]:
    return sorted(path.stem for path in (ROOT / ".loop/tickets").glob("*.md") if status(path) == "Ready")


def toml_policy(rel: str) -> dict:
    text = read(rel)
    if tomllib is None:
        return {}
    return tomllib.loads(text)


def automation_armed() -> bool:
    loop_policy = toml_policy("operations/loop_policy.toml")
    handoff_policy = toml_policy("operations/worker_handoff_policy.toml")
    env_value = os.environ.get("LOOP_AUTOMATION_ARMED", "")
    env_false = env_value.strip().lower() in FALSE_EQUIVALENTS
    policy_armed = bool(loop_policy.get("automation_armed", False)) and bool(handoff_policy.get("automation_armed", False))
    if env_value and not env_false and env_value.strip().lower() != "true":
        fail(f"LOOP_AUTOMATION_ARMED must be true or false-equivalent, got {env_value!r}")
    return policy_armed and env_value.strip().lower() == "true"


def run_handoff_probe(ticket_dir: Path, expected: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "handoff"
        cmd = [
            "scripts/loop_emit_worker_handoff.py",
            "--ticket-dir", str(ticket_dir),
            "--mode", "controller",
            "--run-id", "RUN-POST-BOOTSTRAP-PROBE",
            "--latest-json", str(out_dir / "latest.json"),
            "--latest-markdown", str(out_dir / "latest.md"),
            "--latest-issue", str(out_dir / "latest_issue.md"),
            "--latest-comment", str(out_dir / "latest_comment.md"),
            "--expect", expected,
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            fail(f"handoff probe failed: {' '.join(cmd)}\nstdout={result.stdout}\nstderr={result.stderr}")
        return json.loads((out_dir / "latest.json").read_text(encoding="utf-8"))


def validate_no_ready_controller_reason() -> None:
    if ready_tickets():
        return
    payload = run_handoff_probe(ROOT / ".loop/tickets", "block")
    if payload.get("next_action") != "wait_for_ready_ticket":
        fail(f"no-Ready controller/handoff must explicitly wait for ready ticket, got {payload.get('next_action')}")
    reason = str(payload.get("reason", ""))
    if "No Ready ticket" not in reason:
        fail(f"no-Ready controller/handoff must include explicit block reason, got {reason!r}")


def validate_disarmed_ready_preview_only() -> None:
    if automation_armed():
        return
    with tempfile.TemporaryDirectory() as tmp:
        ticket_dir = Path(tmp) / "tickets"
        shutil.copytree(ROOT / ".loop/tickets", ticket_dir)
        ticket = ticket_dir / "TKT-0005.md"
        text = ticket.read_text(encoding="utf-8")
        text = re.sub(r"^Status:\s*.+$", "Status: Ready", text, count=1, flags=re.M)
        ticket.write_text(text, encoding="utf-8")
        payload = run_handoff_probe(ticket_dir, "block")
    if payload.get("selected_ticket") not in (None, ""):
        fail("disarmed automation must not select an executable worker ticket")
    if payload.get("blocked_ticket") != "TKT-0005":
        fail(f"disarmed automation should block preview for TKT-0005, got {payload.get('blocked_ticket')}")
    if payload.get("next_action") != "wait_for_loop_automation_armed":
        fail(f"disarmed automation must wait for armed switch, got {payload.get('next_action')}")


def validate_ready_ticket_chain() -> None:
    ready = ready_tickets()
    if len(ready) > 1:
        fail(f"post-bootstrap runtime allows at most one Ready ticket, got {ready}")
    if len(ready) != 1:
        return
    ticket = ready[0]
    if ticket != "TKT-0005":
        fail(f"only TKT-0005 may be Ready at Phase1 entry, got {ticket}")
    required_status = {
        ".loop/tickets/TKT-0040.md": "Done",
        ".loop/gates/GATE-0070-failure-feedback-ready.md": "passed",
        ".loop/tickets/TKT-0050.md": "Done",
        ".loop/gates/GATE-0080-qa-regression-ready.md": "passed",
        ".loop/tickets/TKT-0060.md": "Done",
        ".loop/gates/GATE-0090-phase1-feature-loop-ready.md": "passed",
    }
    for rel, expected in required_status.items():
        actual = status(ROOT / rel)
        if actual != expected:
            fail(f"{ticket} Ready requires full prerequisite chain: {rel} must be {expected}, got {actual}")
    for rel in [
        "docs/90_session_metadata_and_path_policy.md",
        "reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_ticket_prompt.md",
        "reports/qa/phase1_loop.verdict.json",
        "reports/failure_feedback/TKT-0040.validate.json",
        "operations/worker_handoff_policy.toml",
    ]:
        if not (ROOT / rel).is_file():
            fail(f"{ticket} Ready requires session/handoff/QA/repair evidence: {rel}")


def validate_latest_handoff_freshness() -> None:
    latest = ROOT / "reports/loop/worker_handoff/latest.json"
    if not latest.is_file():
        return
    payload = json.loads(latest.read_text(encoding="utf-8"))
    ready = ready_tickets()
    selected = payload.get("selected_ticket")
    blocked = payload.get("blocked_ticket")
    if selected and selected not in ready:
        fail(f"stale worker_handoff latest.json selects {selected}, but current Ready tickets are {ready}")
    if not ready and payload.get("verdict") != "block":
        fail("stale worker_handoff latest.json is not a block while no tickets are Ready")
    if not ready and blocked:
        blocked_path = ROOT / ".loop/tickets" / f"{blocked}.md"
        if blocked_path.is_file() and payload.get("blocked_ticket_status") != status(blocked_path):
            fail(f"stale worker_handoff latest.json blocked_ticket_status disagrees with {blocked_path.relative_to(ROOT)}")
    if ready == ["TKT-0005"] and blocked == "TKT-0005" and payload.get("blocked_ticket_status") != "Ready":
        fail("stale worker_handoff latest.json blocks TKT-0005 with a status that no longer matches Ready")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Forward static-only mode to OPS readiness to avoid recursive dependent checks.",
    )
    args = parser.parse_args()

    ops_cmd = ["scripts/check_ops_migration_readiness.py"]
    if args.static_only:
        ops_cmd.append("--static-only")

    run(ops_cmd)
    run(["scripts/check_phase1_entry_state_consistency.py"])
    run(["scripts/check_phase1_gameplay_start_static.py"])
    validate_no_ready_controller_reason()
    validate_disarmed_ready_preview_only()
    validate_ready_ticket_chain()
    validate_latest_handoff_freshness()
    print("post-bootstrap runtime state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
