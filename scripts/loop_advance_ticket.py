#!/usr/bin/env python3
"""Advance ticket state from a merge-history record.

This controller helper is deterministic and network-free. GitHub Actions uses it
only after merge evidence exists. It does not call AI providers and does not
require OPENAI_API_KEY or CODEX_API_KEY.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "operations" / "ticket_transition_policy.toml"
STATUS_RE = re.compile(r"^Status:\s*(.+?)\s*$", re.MULTILINE)
TICKET_RE = re.compile(r"^(?:OPS|TKT)-\d{4}$")


@dataclass
class StatusUpdate:
    ticket_id: str
    path: str
    old: str
    new: str
    changed: bool

    def to_json(self) -> dict:
        return {
            "ticket_id": self.ticket_id,
            "path": self.path,
            "from": self.old,
            "to": self.new,
            "changed": self.changed,
        }


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_policy(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing transition policy: {path}")
    if tomllib is None:
        text = path.read_text(encoding="utf-8")
        seq = re.findall(r'"((?:OPS|TKT)-\d{4})"', text)
        current = re.search(r'current_ready_ticket\s*=\s*"([^"]+)"', text)
        return {
            "transition_report_dir": "reports/loop/ticket_transitions",
            "max_ready_tickets": 1,
            "idempotent_reapply_allowed": True,
            "ops_migration": {
                "active": True,
                "sequence": seq,
                "current_ready_ticket": current.group(1) if current else "OPS-0007",
                "freeze_gameplay_tickets": True,
            },
            "guards": {
                "require_non_dry_run_history_for_apply": True,
                "forbid_tkt_ready_until_ops_complete": True,
            },
        }
    return tomllib.loads(path.read_text(encoding="utf-8"))


def ticket_path(ticket_id: str, ticket_dir: Path) -> Path:
    return ticket_dir / f"{ticket_id}.md"


def read_ticket_status(path: Path) -> str:
    if not path.is_file():
        fail(f"missing ticket file: {path}")
    text = path.read_text(encoding="utf-8")
    match = STATUS_RE.search(text)
    if not match:
        fail(f"ticket has no Status line: {path}")
    return match.group(1).strip()


def set_ticket_status(path: Path, status: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not STATUS_RE.search(text):
        fail(f"ticket has no Status line: {path}")
    path.write_text(STATUS_RE.sub(f"Status: {status}", text, count=1), encoding="utf-8")


def ready_tickets(ticket_dir: Path) -> list[str]:
    ready: list[str] = []
    for path in sorted(ticket_dir.glob("*.md")):
        try:
            status = read_ticket_status(path)
        except SystemExit:
            raise
        if status == "Ready":
            ready.append(path.stem)
    return ready


def next_ticket_id(merged_ticket: str, policy: dict) -> str | None:
    ops = policy.get("ops_migration") or {}
    completion = policy.get("ops_completion") or {}
    sequence = list(ops.get("sequence") or [])
    if merged_ticket in sequence:
        index = sequence.index(merged_ticket)
        if index + 1 < len(sequence):
            return sequence[index + 1]
        if merged_ticket == completion.get("completion_ticket", "OPS-0009"):
            return completion.get("unlock_first_gameplay_ticket") or ops.get("unlock_first_gameplay_ticket")
        return None
    return None


def validate_merge_history(history: dict, mode: str, allow_dry_run_history: bool) -> list[str]:
    reasons: list[str] = []
    ticket_id = history.get("ticket_id")
    if not ticket_id or not isinstance(ticket_id, str) or not TICKET_RE.match(ticket_id):
        reasons.append("merge history ticket_id is missing or invalid")
    if history.get("merge_method") != "squash":
        reasons.append("merge history merge_method must be squash")
    if history.get("base_branch") != "main":
        reasons.append("merge history base_branch must be main")
    if not history.get("run_id"):
        reasons.append("merge history run_id is missing")
    if mode == "apply" and history.get("dry_run") is True and not allow_dry_run_history:
        reasons.append("apply mode refuses dry-run merge history")
    return reasons


def build_plan(history: dict, policy: dict, ticket_dir: Path, mode: str, allow_dry_run_history: bool) -> dict:
    reasons: list[str] = validate_merge_history(history, mode, allow_dry_run_history)
    merged_ticket = history.get("ticket_id") if isinstance(history.get("ticket_id"), str) else None
    next_ticket = next_ticket_id(merged_ticket, policy) if merged_ticket else None
    updates: list[StatusUpdate] = []

    if merged_ticket:
        merged_path = ticket_path(merged_ticket, ticket_dir)
        if merged_path.is_file():
            old = read_ticket_status(merged_path)
            updates.append(StatusUpdate(merged_ticket, merged_path.relative_to(ROOT).as_posix() if merged_path.is_relative_to(ROOT) else merged_path.as_posix(), old, "Done", old != "Done"))
        else:
            reasons.append(f"merged ticket file does not exist: {merged_ticket}")

    if next_ticket:
        next_path = ticket_path(next_ticket, ticket_dir)
        if next_path.is_file():
            old = read_ticket_status(next_path)
            if old not in {"Blocked", "Ready"}:
                reasons.append(f"next ticket {next_ticket} has non-promotable status {old!r}")
            updates.append(StatusUpdate(next_ticket, next_path.relative_to(ROOT).as_posix() if next_path.is_relative_to(ROOT) else next_path.as_posix(), old, "Ready", old != "Ready"))
        else:
            reasons.append(f"next ticket file does not exist: {next_ticket}")
    else:
        reasons.append("no dependency-satisfied next ticket is defined by transition policy")

    simulated: dict[str, str] = {}
    for path in sorted(ticket_dir.glob("*.md")):
        simulated[path.stem] = read_ticket_status(path)
    for update in updates:
        simulated[update.ticket_id] = update.new

    ready_after = sorted(ticket for ticket, status in simulated.items() if status == "Ready")
    max_ready = int(policy.get("max_ready_tickets", 1) or 1)
    if len(ready_after) != max_ready:
        reasons.append(f"expected exactly {max_ready} Ready ticket after transition, found {ready_after}")

    ops = policy.get("ops_migration") or {}
    completion = policy.get("ops_completion") or {}
    guards = policy.get("guards") or {}
    if guards.get("forbid_tkt_ready_until_ops_complete", True) and ops.get("active", True):
        gameplay_ready = [ticket for ticket in ready_after if ticket.startswith("TKT-")]
        if gameplay_ready:
            reasons.append("gameplay tickets may not become Ready during OPS migration: " + ", ".join(gameplay_ready))

    if merged_ticket == completion.get("completion_ticket", "OPS-0009"):
        for rel in [completion.get("completion_gate_report"), completion.get("phase1_gate_report")]:
            if rel and not (ROOT / rel).is_file():
                reasons.append(f"missing final unlock gate report: {rel}")

    verdict = "pass" if not reasons else "block"
    if merged_ticket and not str(merged_ticket).startswith("OPS-") and ops.get("active", False):
        verdict = "reject"
        reasons.append("non-OPS ticket cannot be advanced while OPS migration is active")

    return {
        "schema": "schemas/ticket_transition_schema.md",
        "verdict": verdict,
        "mode": mode,
        "run_id": history.get("run_id"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_key_required": False,
        "ai_worker": "not_used",
        "merge_history": history,
        "merged_ticket": merged_ticket,
        "next_ready_ticket": next_ticket,
        "status_updates": [u.to_json() for u in updates],
        "ready_tickets_after": ready_after,
        "reasons": reasons or ["ticket transition policy satisfied"],
    }


def apply_plan(plan: dict, ticket_dir: Path) -> None:
    if plan.get("verdict") != "pass":
        fail("refusing to apply non-pass ticket transition")
    for item in plan.get("status_updates") or []:
        path = ticket_dir / f"{item['ticket_id']}.md"
        if item.get("changed"):
            set_ticket_status(path, item["to"])


def write_markdown(path: Path, plan: dict) -> None:
    lines = [
        "# Ticket Transition Plan",
        "",
        f"- verdict: `{plan['verdict']}`",
        f"- mode: `{plan['mode']}`",
        f"- run_id: `{plan.get('run_id')}`",
        f"- merged_ticket: `{plan.get('merged_ticket')}`",
        f"- next_ready_ticket: `{plan.get('next_ready_ticket')}`",
        "- AI worker: not used",
        "- API key required: false",
        "",
        "## Status updates",
        "",
    ]
    for item in plan.get("status_updates") or []:
        lines.append(f"- {item['ticket_id']}: `{item['from']}` -> `{item['to']}` changed=`{item['changed']}`")
    lines += ["", "## Ready tickets after", ""]
    for ticket in plan.get("ready_tickets_after") or []:
        lines.append(f"- {ticket}")
    lines += ["", "## Reasons", ""]
    for reason in plan.get("reasons") or []:
        lines.append(f"- {reason}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merge-history", required=True)
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--ticket-dir", default=str(ROOT / ".loop" / "tickets"))
    parser.add_argument("--mode", choices=["plan", "apply"], default="plan")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--expect", choices=["pass", "block", "reject"])
    parser.add_argument("--allow-dry-run-history", action="store_true")
    args = parser.parse_args()

    history_path = Path(args.merge_history)
    if not history_path.is_absolute():
        history_path = ROOT / history_path
    if not history_path.is_file():
        fail(f"missing merge history: {history_path}")
    history = json.loads(history_path.read_text(encoding="utf-8"))
    if not isinstance(history, dict):
        fail("merge history must be a JSON object")

    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = ROOT / policy_path
    policy = load_policy(policy_path)

    ticket_dir = Path(args.ticket_dir)
    if not ticket_dir.is_absolute():
        ticket_dir = ROOT / ticket_dir
    if not ticket_dir.is_dir():
        fail(f"missing ticket directory: {ticket_dir}")

    plan = build_plan(history, policy, ticket_dir, args.mode, args.allow_dry_run_history)
    if args.mode == "apply" and plan.get("verdict") == "pass":
        apply_plan(plan, ticket_dir)
        # Recompute ready list after file writes for exact evidence.
        plan["ready_tickets_after"] = ready_tickets(ticket_dir)

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        md = Path(args.markdown)
        if not md.is_absolute():
            md = ROOT / md
        write_markdown(md, plan)

    print(json.dumps({"verdict": plan.get("verdict"), "merged_ticket": plan.get("merged_ticket"), "next_ready_ticket": plan.get("next_ready_ticket"), "ready_tickets_after": plan.get("ready_tickets_after")}, ensure_ascii=False))
    if args.expect and plan.get("verdict") != args.expect:
        fail(f"expected verdict {args.expect}, got {plan.get('verdict')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
