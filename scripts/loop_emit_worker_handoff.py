#!/usr/bin/env python3
"""Emit deterministic Codex worker handoff artifacts.

GitHub Actions uses this script only to generate prompt, issue, and comment
artifacts. It intentionally does not call Codex, GPT, OpenAI APIs,
OPENAI_API_KEY, CODEX_API_KEY, or openai/codex-action@v1.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "operations/worker_handoff_policy.toml"
SCHEMA = "schemas/worker_handoff_schema.md"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_array(text: str, name: str) -> list[str]:
    # Minimal TOML array parser for the simple string arrays used here.
    m = re.search(rf"^{re.escape(name)}\s*=\s*\[(.*?)\]", text, re.M | re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def policy_value(text: str, name: str, default: str = "") -> str:
    m = re.search(rf'^' + re.escape(name) + r'\s*=\s*"([^"]*)"', text, re.M)
    return m.group(1) if m else default


def load_policy() -> dict[str, object]:
    text = read(POLICY_PATH)
    return {
        "report_dir": policy_value(text, "report_dir", "reports/loop/worker_handoff"),
        "latest_json": policy_value(text, "latest_json", "reports/loop/worker_handoff/latest.json"),
        "latest_markdown": policy_value(text, "latest_markdown", "reports/loop/worker_handoff/latest.md"),
        "latest_issue": policy_value(text, "latest_issue", "reports/loop/worker_handoff/latest_issue.md"),
        "latest_comment": policy_value(text, "latest_comment", "reports/loop/worker_handoff/latest_comment.md"),
        "current_ready_ticket": policy_value(text, "current_ready_ticket", "TKT-0005"),
        "required_reads": parse_array(text, "required_reads"),
        "allowed_paths_ops": parse_array(text, "allowed_paths_ops"),
        "allowed_paths_gameplay": parse_array(text, "allowed_paths_gameplay"),
        "forbidden_paths": parse_array(text, "forbidden_paths"),
    }


def parse_ticket(path: Path) -> dict[str, object]:
    text = read(path)
    title_match = re.search(r"^#\s+((?:OPS|TKT)-[^:]+):\s*(.+)$", text, re.M)
    status_match = re.search(r"^Status:\s*(.+)$", text, re.M)
    owner_match = re.search(r"^Owner session:\s*(.+)$", text, re.M)
    review_match = re.search(r"^Review session:\s*(.+)$", text, re.M)
    worktree_match = re.search(r"^Worktree:\s*`?([^`\n]+)`?", text, re.M)
    checks_block = ""
    m = re.search(r"## 5\. Required checks\n\n(.+?)(?:\n## |\Z)", text, re.S)
    if m:
        checks_block = m.group(1).strip()
    if not title_match:
        fail(f"ticket title must start with OPS-* or TKT-*: {path}")
    try:
        rel_path = path.relative_to(ROOT).as_posix()
    except ValueError:
        rel_path = f".loop/tickets/{path.name}"
    return {
        "id": title_match.group(1).strip(),
        "title": title_match.group(2).strip(),
        "status": status_match.group(1).strip() if status_match else "Unknown",
        "owner_session": owner_match.group(1).strip() if owner_match else "Ticket Implementation Session",
        "review_session": review_match.group(1).strip() if review_match else "Design Review Session",
        "worktree": worktree_match.group(1).strip() if worktree_match else f"worktrees/impl/{path.stem}",
        "required_checks_block": checks_block,
        "path": rel_path,
    }


def ready_tickets(ticket_dir: Path) -> list[dict[str, object]]:
    tickets: list[dict[str, object]] = []
    for path in sorted(ticket_dir.glob("*.md")):
        ticket = parse_ticket(path)
        if str(ticket["status"]).lower() == "ready":
            tickets.append(ticket)
    return tickets


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
    if "test" in low:
        return "test"
    if "qa" in low or "regression" in low:
        return "qa"
    return "impl"


def required_commands(ticket: dict[str, object] | None) -> list[str]:
    commands = [
        "scripts/ci_local_equivalent.sh --static-only",
        "scripts/check_worker_handoff_static.py",
    ]
    block = str(ticket.get("required_checks_block") if ticket else "")
    for line in block.splitlines():
        candidate = line.strip()
        if candidate and not candidate.startswith("```") and not candidate.startswith("#"):
            if candidate not in commands:
                commands.append(candidate)
    return commands


def build_handoff(args: argparse.Namespace) -> dict[str, object]:
    policy = load_policy()
    run_id = args.run_id or os.environ.get("OPENTAIKO_LOOP_RUN_ID") or f"RUN-HANDOFF-{int(time.time())}"
    ticket_dir = ROOT / args.ticket_dir
    selected_ticket: dict[str, object] | None = None
    if args.ticket:
        selected_ticket = parse_ticket(ROOT / args.ticket)
        if selected_ticket["status"] != "Ready":
            fail(f"selected ticket is not Ready: {args.ticket}")
    else:
        ready = ready_tickets(ticket_dir)
        if len(ready) > 1:
            return {
                "schema": SCHEMA,
                "run_id": run_id,
                "mode": args.mode,
                "verdict": "block",
                "reason": f"Expected one Ready ticket; found {[t['id'] for t in ready]}",
                "selected_ticket": None,
                "api_key_required": False,
                "ai_worker_in_github_actions": False,
            }
        selected_ticket = ready[0] if ready else None
    if selected_ticket is None:
        return {
            "schema": SCHEMA,
            "run_id": run_id,
            "mode": args.mode,
            "verdict": "block",
            "reason": "No Ready ticket found.",
            "selected_ticket": None,
            "api_key_required": False,
            "ai_worker_in_github_actions": False,
        }
    ticket_id = str(selected_ticket["id"])
    branch = f"{branch_prefix(str(selected_ticket['owner_session']))}/{ticket_id}-{slugify(str(selected_ticket['title']))}"
    required_reads = list(policy["required_reads"])
    if str(selected_ticket["path"]) not in required_reads:
        required_reads.append(str(selected_ticket["path"]))
    out_json = args.latest_json or str(policy["latest_json"])
    out_md = args.latest_markdown or str(policy["latest_markdown"])
    out_issue = args.latest_issue or str(policy["latest_issue"])
    out_comment = args.latest_comment or str(policy["latest_comment"])
    is_gameplay_ticket = ticket_id.startswith("TKT-")
    allowed_paths = policy["allowed_paths_gameplay"] if is_gameplay_ticket and policy.get("allowed_paths_gameplay") else policy["allowed_paths_ops"]
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "mode": args.mode,
        "verdict": "plan",
        "reason": f"Ready ticket selected: {ticket_id}",
        "selected_ticket": ticket_id,
        "selected_ticket_path": selected_ticket["path"],
        "selected_ticket_title": selected_ticket["title"],
        "owner_session": selected_ticket["owner_session"],
        "review_session": selected_ticket["review_session"],
        "branch": branch,
        "implementation_worktree": f"worktrees/impl/{ticket_id}",
        "review_worktree": f"worktrees/review/{ticket_id}",
        "qa_worktree": f"worktrees/qa/{ticket_id}",
        "session_metadata_path": f"reports/session_metadata/{ticket_id}.toml",
        "qa_verdict_path": f"reports/qa/{ticket_id}.verdict.json",
        "required_reads": required_reads,
        "allowed_paths": allowed_paths,
        "forbidden_paths": policy["forbidden_paths"],
        "required_commands": required_commands(selected_ticket),
        "latest_json_path": out_json,
        "next_prompt_path": out_md,
        "issue_body_path": out_issue,
        "comment_body_path": out_comment,
        "api_key_required": False,
        "ai_worker_in_github_actions": False,
        "github_actions_role": "emit_handoff_artifacts_only",
        "ticket_required_checks_block": selected_ticket.get("required_checks_block", ""),
    }


def render_prompt(h: dict[str, object]) -> str:
    ticket = h.get("selected_ticket") or "none"
    if h.get("verdict") != "plan":
        return f"# Codex Worker Handoff\n\nVerdict: `{h.get('verdict')}`\n\nReason: {h.get('reason')}\n\nDo not implement. GitHub Actions emitted this blocker without calling an AI worker.\n"
    lines = [
        f"# Codex Worker Handoff for {ticket}",
        "",
        f"Run ID: `{h.get('run_id')}`",
        f"Verdict: `{h.get('verdict')}`",
        f"Ticket: `{ticket}`",
        f"Ticket file: `{h.get('selected_ticket_path')}`",
        f"Branch: `{h.get('branch')}`",
        f"Implementation worktree: `{h.get('implementation_worktree')}`",
        f"Review worktree: `{h.get('review_worktree')}`",
        f"QA worktree: `{h.get('qa_worktree')}`",
        f"Session metadata: `{h.get('session_metadata_path')}`",
        f"Expected QA verdict path: `{h.get('qa_verdict_path')}`",
        "",
        "## Mandatory boundary",
        "",
        "GitHub Actions emitted this handoff deterministically. It did not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`.",
        "",
        "Use Codex Cloud, Codex App Automation, or Codex CLI signed in with ChatGPT. Work on one ticket only.",
        "",
        "## Required reads",
        "",
    ]
    lines += [f"- `{p}`" for p in h.get("required_reads", [])]
    lines += ["", "## Allowed paths", ""]
    lines += [f"- `{p}`" for p in h.get("allowed_paths", [])]
    lines += ["", "## Forbidden paths", ""]
    lines += [f"- `{p}`" for p in h.get("forbidden_paths", [])]
    lines += ["", "## Required commands", ""]
    lines += [f"- `{c}`" for c in h.get("required_commands", [])]
    lines += [
        "",
        "## Stop and PR rules",
        "",
        "- Do not mark tickets Done.",
        "- Do not pass gates.",
        "- Do not self-approve.",
        "- Do not author `reports/qa/*.verdict.json` from an implementation session.",
        "- Do not start gameplay implementation unless the selected ticket explicitly unlocks Phase1 gameplay.",
        "- Open a PR only after a scoped diff exists and the required commands have been run or explicitly blocked by environment limitations.",
    ]
    return "\n".join(lines) + "\n"


def render_issue(h: dict[str, object]) -> str:
    prompt_path = h.get("next_prompt_path", "reports/loop/worker_handoff/latest.md")
    return f"""# Codex worker handoff: {h.get('selected_ticket') or 'blocked'}

@codex read `{prompt_path}` and work only on the selected ticket described there.

## Deterministic boundary

GitHub Actions generated this issue body from `scripts/loop_emit_worker_handoff.py`. It did not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`.

## Selected ticket

- Ticket: `{h.get('selected_ticket')}`
- Ticket file: `{h.get('selected_ticket_path')}`
- Branch: `{h.get('branch')}`
- Session metadata: `{h.get('session_metadata_path')}`

## Required artifact

- Prompt: `{prompt_path}`
- Machine contract: `reports/loop/worker_handoff/latest.json`
"""


def render_comment(h: dict[str, object]) -> str:
    return f"""@codex detached worker request.

Read `reports/loop/worker_handoff/latest.md` and implement only `{h.get('selected_ticket')}`. Do not self-approve, mark tickets Done, pass gates, or author QA verdict files. GitHub Actions only emitted this handoff; it did not call an AI worker or require `OPENAI_API_KEY` / `CODEX_API_KEY`.
"""


def write_outputs(h: dict[str, object], dry_run: bool) -> None:
    prompt = render_prompt(h)
    issue = render_issue(h)
    comment = render_comment(h)
    if dry_run:
        print(json.dumps(h, indent=2, ensure_ascii=False))
        print("\n--- latest.md ---\n")
        print(prompt)
        return
    paths = [h.get("next_prompt_path"), h.get("issue_body_path"), h.get("comment_body_path")]
    json_path = h.get("next_prompt_path", "reports/loop/worker_handoff/latest.md")
    del json_path
    for raw in paths:
        if raw:
            (ROOT / str(raw)).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / str(h.get("next_prompt_path"))).write_text(prompt, encoding="utf-8")
    (ROOT / str(h.get("issue_body_path"))).write_text(issue, encoding="utf-8")
    (ROOT / str(h.get("comment_body_path"))).write_text(comment, encoding="utf-8")
    latest_json = ROOT / str(h.get("latest_json_path", "reports/loop/worker_handoff/latest.json"))
    latest_json.parent.mkdir(parents=True, exist_ok=True)
    latest_json.write_text(json.dumps(h, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        print(latest_json.relative_to(ROOT).as_posix())
    except ValueError:
        print(latest_json.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["plan", "controller", "issue"], default="plan")
    parser.add_argument("--run-id")
    parser.add_argument("--ticket", help="relative path to a specific Ready ticket")
    parser.add_argument("--ticket-dir", default=".loop/tickets")
    parser.add_argument("--latest-json")
    parser.add_argument("--latest-markdown")
    parser.add_argument("--latest-issue")
    parser.add_argument("--latest-comment")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--expect", choices=["plan", "block", "reject"])
    args = parser.parse_args()
    handoff = build_handoff(args)
    if args.expect and handoff.get("verdict") != args.expect:
        fail(f"expected {args.expect}, got {handoff.get('verdict')}: {handoff.get('reason')}")
    write_outputs(handoff, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
