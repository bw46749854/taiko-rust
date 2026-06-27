#!/usr/bin/env python3
"""Apply a machine-readable QA verdict to ticket transition evidence.

The script is intentionally conservative. It can update the ticket status only
when --write is passed. Without --write it emits the deterministic transition
without mutating files.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TRANSITIONS = {
    "pass": ("Done", "merge PR and run next-ticket selection"),
    "reject": ("Rejected", "create failure report and materialize repair ticket before downstream work"),
    "block": ("Blocked", "produce missing machine-readable evidence before continuing"),
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing verdict file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid verdict JSON: {path}: {exc}")


def ticket_path(ticket_id: str) -> Path:
    return ROOT / ".loop" / "tickets" / f"{ticket_id}.md"


def update_status(text: str, status: str) -> str:
    if not re.search(r"^Status:\s*.+$", text, flags=re.MULTILINE):
        fail("ticket has no Status line")
    return re.sub(r"^Status:\s*.+$", f"Status: {status}", text, count=1, flags=re.MULTILINE)


def render_transition(ticket_id: str, verdict_path: Path, verdict: dict, target_status: str, next_action: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_verdict = verdict.get("verdict", "unknown")
    source = verdict.get("source", str(verdict_path.relative_to(ROOT) if verdict_path.is_relative_to(ROOT) else verdict_path))
    failure_required = verdict.get("failure_report_required", source_verdict == "reject")
    return f"""# {ticket_id} QA transition

Generated: {now}

| Field | Value |
|---|---|
| Ticket | `{ticket_id}` |
| Verdict source | `{source}` |
| Source file | `{verdict_path}` |
| QA verdict | `{source_verdict}` |
| Target ticket status | `{target_status}` |
| Failure report required | `{str(failure_required).lower()}` |
| Next action | {next_action} |

## Raw verdict

```json
{json.dumps(verdict, ensure_ascii=False, indent=2, sort_keys=True)}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--verdict", required=True)
    parser.add_argument("--write", action="store_true", help="mutate .loop/tickets/<ticket>.md Status line")
    parser.add_argument("--emit-transition", default="", help="write transition markdown to this path")
    args = parser.parse_args()

    tpath = ticket_path(args.ticket)
    if not tpath.is_file():
        fail(f"missing ticket: {tpath}")

    vpath = (ROOT / args.verdict).resolve() if not Path(args.verdict).is_absolute() else Path(args.verdict)
    verdict = load_json(vpath)
    source_verdict = verdict.get("verdict")
    if source_verdict not in TRANSITIONS:
        target_status, next_action = TRANSITIONS["block"]
        verdict = {**verdict, "verdict": "block", "normalization_reason": f"unsupported verdict {source_verdict!r}"}
    else:
        target_status, next_action = TRANSITIONS[source_verdict]

    transition = render_transition(args.ticket, vpath, verdict, target_status, next_action)

    if args.emit_transition:
        out = ROOT / args.emit_transition if not Path(args.emit_transition).is_absolute() else Path(args.emit_transition)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(transition, encoding="utf-8")

    if args.write:
        original = tpath.read_text(encoding="utf-8")
        tpath.write_text(update_status(original, target_status), encoding="utf-8")

    result = {
        "verdict": "pass",
        "ticket_id": args.ticket,
        "qa_verdict": verdict.get("verdict"),
        "target_status": target_status,
        "next_action": next_action,
        "ticket_updated": args.write,
        "transition_path": args.emit_transition,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
