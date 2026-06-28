#!/usr/bin/env python3
"""Render a Plus-plan Codex Automation prompt without requiring Rust.

OPS-0008 worker handoff now has a canonical emitter at scripts/loop_emit_worker_handoff.py.
This legacy-compatible renderer also points workers to reports/loop/worker_handoff/latest.md.

This is the canonical fallback path for environments where `taiko_cli loop run-once`
cannot execute because Rust is unavailable. It is deterministic and does not call
OpenAI APIs. Codex plan exhaustion is treated as usage_wait, not reject.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_ticket(path: Path) -> dict[str, object]:
    text = read_text(path)
    title_match = re.search(r"^#\s+(TKT-[^:]+):\s*(.+)$", text, re.M)
    status_match = re.search(r"^Status:\s*(.+)$", text, re.M)
    owner_match = re.search(r"^Owner session:\s*(.+)$", text, re.M)
    worktree_match = re.search(r"^Worktree:\s*`?([^`\n]+)`?", text, re.M)
    checks_block = ""
    m = re.search(r"## 5\. Required checks\n\n(.+?)(?:\n## |\Z)", text, re.S)
    if m:
        checks_block = m.group(1).strip()
    return {
        "id": title_match.group(1).strip() if title_match else path.stem,
        "title": title_match.group(2).strip() if title_match else path.stem,
        "status": status_match.group(1).strip() if status_match else "Unknown",
        "owner_session": owner_match.group(1).strip() if owner_match else "Ticket Implementation Session",
        "worktree": worktree_match.group(1).strip() if worktree_match else f"worktrees/impl/{path.stem}",
        "required_checks": checks_block,
        "path": path.relative_to(ROOT).as_posix(),
    }


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or "ticket"


def branch_prefix(owner: str) -> str:
    low = owner.lower()
    if "control" in low:
        return "loop"
    if "spec" in low:
        return "spec"
    if "design" in low or "review" in low:
        return "review"
    if "test infra" in low or "test infrastructure" in low:
        return "test"
    if "qa" in low or "regression" in low:
        return "qa"
    return "impl"


def select_ready_ticket() -> dict[str, object] | None:
    tickets = []
    for path in sorted((ROOT / ".loop/tickets").glob("*.md")):
        ticket = parse_ticket(path)
        if str(ticket["status"]).lower() == "ready":
            tickets.append(ticket)
    return tickets[0] if tickets else None


def load_controller_plan(path: Path | None) -> dict[str, object] | None:
    if not path:
        return None
    if not path.is_file():
        raise SystemExit(f"controller plan not found: {path}")
    return json.loads(read_text(path))


def build_plan(args: argparse.Namespace) -> dict[str, object]:
    controller = load_controller_plan(Path(args.controller_plan) if args.controller_plan else None)
    if controller:
        return controller
    ticket = parse_ticket(ROOT / args.ticket) if args.ticket else select_ready_ticket()
    run_id = args.run_id or os.environ.get("OPENTAIKO_LOOP_RUN_ID") or f"RUN-CODEX-{int(time.time())}"
    report_dir = f"reports/loop/{run_id}"
    if not ticket:
        return {
            "run_id": run_id,
            "mode": args.mode,
            "state": "no_ready_ticket",
            "verdict": "block",
            "selected_ticket": None,
            "next_action": "wait_for_ready_ticket",
            "reason": "No Ready ticket was found.",
            "controller_report_json": f"{report_dir}/controller_plan.json",
            "controller_report_markdown": f"{report_dir}/controller_plan.md",
            "next_codex_prompt": f"{report_dir}/next_codex_prompt.md",
            "required_commands": [],
        }
    ticket_id = str(ticket["id"])
    title = str(ticket["title"])
    prefix = branch_prefix(str(ticket["owner_session"]))
    return {
        "run_id": run_id,
        "mode": args.mode,
        "state": "ready_ticket",
        "verdict": "plan",
        "selected_ticket": ticket_id,
        "selected_ticket_path": ticket["path"],
        "selected_ticket_title": title,
        "next_action": "start_worker",
        "reason": f"Ready ticket selected: {ticket_id}",
        "branch": f"{prefix}/{ticket_id}-{slugify(title)}",
        "implementation_worktree": f"worktrees/impl/{ticket_id}",
        "review_worktree": f"worktrees/review/{ticket_id}",
        "qa_worktree": f"worktrees/qa/{ticket_id}",
        "session_metadata_path": f"reports/session_metadata/{ticket_id}.toml",
        "controller_report_json": f"{report_dir}/controller_plan.json",
        "controller_report_markdown": f"{report_dir}/controller_plan.md",
        "next_codex_prompt": f"{report_dir}/next_codex_prompt.md",
        "required_commands": [
            "scripts/ci_local_equivalent.sh --static-only",
            "scripts/check_codex_automation_static.py",
        ],
        "ticket_required_checks_block": ticket.get("required_checks", ""),
    }


def render_prompt(plan: dict[str, object]) -> str:
    ticket = plan.get("selected_ticket") or "none"
    action = plan.get("next_action", "wait_for_ready_ticket")
    lines = [
        f"# Next Codex Automation Prompt for {ticket}",
        "",
        f"Run ID: `{plan.get('run_id')}`",
        f"Next action: `{action}`",
        f"Reason: {plan.get('reason')}",
        "",
        "## Mandatory operating rule",
        "",
        "Use Codex Cloud, Codex App Automations, or Codex CLI signed in with ChatGPT. Do not use `OPENAI_API_KEY`, `CODEX_API_KEY`, `openai/codex-action@v1`, or a metered API worker. Prefer the OPS-0008 worker handoff generated by `scripts/loop_emit_worker_handoff.py` at `reports/loop/worker_handoff/latest.md` when available.",
        "",
        "## Required reads",
        "",
        "- `AGENTS.md`",
        "- `docs/88_auto_merge_loop_policy.md`",
        "- `docs/89_loop_controller_state_machine.md`",
        "- `docs/90_session_metadata_and_path_policy.md`",
        "- `docs/91_repair_materialization_and_retry_budget.md`",
        "- `docs/92_codex_plus_automation_operation.md`",
        "- `operations/codex_automation_policy.toml`",
        "- `docs/99_codex_worker_handoff_contract.md`",
        "- `reports/loop/worker_handoff/latest.md` when present",
    ]
    if plan.get("selected_ticket_path"):
        lines.append(f"- `{plan['selected_ticket_path']}`")
    lines += ["", "## Selected work", ""]
    if ticket == "none":
        lines += [
            "No Ready ticket is available. Do not implement. Record a short automation summary and stop.",
        ]
    else:
        lines += [
            f"- Ticket: `{ticket}`",
            f"- Branch: `{plan.get('branch', 'none')}`",
            f"- Implementation worktree: `{plan.get('implementation_worktree', 'none')}`",
            f"- Review worktree: `{plan.get('review_worktree', 'none')}`",
            f"- QA worktree: `{plan.get('qa_worktree', 'none')}`",
            f"- Session metadata: `{plan.get('session_metadata_path', 'reports/session_metadata/<ticket>.toml')}`",
            "",
            "## Required commands",
            "",
        ]
        commands = plan.get("required_commands") or []
        if isinstance(commands, list) and commands:
            lines += [f"- `{cmd}`" for cmd in commands]
        else:
            lines.append("- `scripts/ci_local_equivalent.sh --static-only`")
        if plan.get("ticket_required_checks_block"):
            lines += ["", "Ticket required checks block:", "", str(plan["ticket_required_checks_block"])]
        lines += [
            "",
            "## Stop and PR rules",
            "",
            "- Work on one ticket only.",
            "- Do not mark a ticket Done.",
            "- Do not pass a gate.",
            "- Do not self-approve.",
            "- Do not write QA verdict files from an implementation session.",
            "- Create a PR only after a scoped implementation or repair diff exists.",
        ]
    return "\n".join(lines) + "\n"


def render_runbook(plan: dict[str, object]) -> str:
    return f"""# Codex Automation Runbook

Run ID: `{plan.get('run_id')}`
State: `{plan.get('state')}`
Next action: `{plan.get('next_action')}`

## Commands

```bash
scripts/ci_local_equivalent.sh --static-only
scripts/render_next_codex_prompt.py --mode automation --run-id {plan.get('run_id')}
```

## Output

- `{plan.get('next_codex_prompt')}`
- `{plan.get('controller_report_json')}`
- `{plan.get('controller_report_markdown')}`

This runbook is deterministic and does not call an OpenAI API.
"""


def write_outputs(plan: dict[str, object], prompt: str, dry_run: bool) -> None:
    if dry_run:
        print(prompt)
        return
    prompt_path = ROOT / str(plan["next_codex_prompt"])
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    runbook_path = prompt_path.parent / "automation_runbook.md"
    runbook_path.write_text(render_runbook(plan), encoding="utf-8")
    json_path = ROOT / str(plan["controller_report_json"])
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = ROOT / str(plan["controller_report_markdown"])
    md_path.write_text(render_runbook(plan), encoding="utf-8")
    print(prompt_path.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["automation", "ticket-worker", "plan"], default="automation")
    parser.add_argument("--run-id")
    parser.add_argument("--ticket", help="relative path to a ticket file")
    parser.add_argument("--controller-plan", help="existing controller_plan.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    plan = build_plan(args)
    prompt = render_prompt(plan)
    write_outputs(plan, prompt, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
