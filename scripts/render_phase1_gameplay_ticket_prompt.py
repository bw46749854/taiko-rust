#!/usr/bin/env python3
"""Render the Step23 Phase1 gameplay ticket start packet.

This script is deterministic and does not call OpenAI APIs. It is the bridge
between the feature-ticket manifest and a Codex Cloud/App/CLI worker prompt.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = "operations/phase1_feature_ticket_manifest.toml"
DEFAULT_TICKET = "TKT-0005"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def string_value(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def array_values(value: str | None) -> list[str]:
    if not value:
        return []
    return re.findall(r'"([^"]+)"', value)


def bool_value(value: str | None) -> bool:
    return (value or "").strip().lower() == "true"


def parse_manifest(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    top: dict[str, str] = {}
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in read(path).splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line == "[[tickets]]":
            if current is not None:
                entries.append(current)
            current = {}
            continue
        if "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        target = current if current is not None else top
        target[key] = value
    if current is not None:
        entries.append(current)
    return top, entries


def parse_ticket(path: Path) -> dict[str, Any]:
    text = read(path)
    title_match = re.search(r"^#\s+(TKT-[^:]+):\s*(.+)$", text, re.M)
    status_match = re.search(r"^Status:\s*(.+)$", text, re.M)
    owner_match = re.search(r"^Owner session:\s*(.+)$", text, re.M)
    worktree_match = re.search(r"^Worktree:\s*`?([^`\n]+)`?", text, re.M)
    required_checks = ""
    m = re.search(r"## 5\. Required checks\n\n(.+?)(?:\n## |\Z)", text, re.S)
    if m:
        required_checks = m.group(1).strip()
    return {
        "ticket_id": title_match.group(1) if title_match else path.stem,
        "title": title_match.group(2).strip() if title_match else path.stem,
        "status": status_match.group(1).strip() if status_match else "Unknown",
        "owner_session": owner_match.group(1).strip() if owner_match else "Ticket Implementation Session",
        "worktree": worktree_match.group(1).strip() if worktree_match else f"worktrees/impl/{path.stem}",
        "required_checks_block": required_checks,
        "path": path.relative_to(ROOT).as_posix(),
    }


def status_of_ticket(ticket_id: str) -> str:
    path = ROOT / ".loop" / "tickets" / f"{ticket_id}.md"
    if not path.is_file():
        return "missing"
    m = re.search(r"^Status:\s*(.+)$", read(path), re.M)
    return m.group(1).strip() if m else "Unknown"


def status_of_gate(gate_id: str) -> str:
    suffix = {"GATE-0070": "failure-feedback-ready", "GATE-0080": "qa-regression-ready", "GATE-0090": "phase1-feature-loop-ready"}.get(gate_id)
    if not suffix:
        return "missing"
    path = ROOT / ".loop" / "gates" / f"{gate_id}-{suffix}.md"
    if not path.is_file():
        return "missing"
    m = re.search(r"^Status:\s*(.+)$", read(path), re.M)
    return m.group(1).strip() if m else "Unknown"


def gate_report_exists(gate_id: str) -> bool:
    return (ROOT / ".loop" / "session_logs" / f"{gate_id}-report.md").is_file()


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or "phase1-ticket"


def manifest_entry(entries: list[dict[str, str]], ticket_id: str) -> dict[str, Any] | None:
    for entry in entries:
        if string_value(entry.get("ticket_id")) == ticket_id:
            return {
                "ticket_id": ticket_id,
                "title": string_value(entry.get("title")),
                "stage": string_value(entry.get("stage")),
                "category": string_value(entry.get("category")),
                "depends_on": array_values(entry.get("depends_on")),
                "primary_crates": array_values(entry.get("primary_crates")),
                "required_commands": array_values(entry.get("required_commands")),
                "acceptance_docs": array_values(entry.get("acceptance_docs")),
                "qa_required": bool_value(entry.get("qa_required")),
                "failure_route_required": bool_value(entry.get("failure_route_required")),
            }
    return None


def build_start_packet(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = ROOT / args.manifest
    issues: list[str] = []
    missing_prerequisites: list[str] = []
    if not manifest_path.is_file():
        raise SystemExit(f"missing manifest: {args.manifest}")
    top, entries = parse_manifest(manifest_path)
    ticket_id = args.ticket
    first_feature_ticket = string_value(top.get("first_feature_ticket"))
    if first_feature_ticket != DEFAULT_TICKET:
        issues.append(f"first_feature_ticket must be {DEFAULT_TICKET}, got {first_feature_ticket or 'missing'}")
    if ticket_id != DEFAULT_TICKET:
        issues.append("Step23 only opens the first gameplay lane; selected ticket must be TKT-0005")
    entry = manifest_entry(entries, ticket_id)
    if entry is None:
        issues.append(f"manifest entry missing: {ticket_id}")
        entry = {
            "ticket_id": ticket_id,
            "title": "missing",
            "stage": "missing",
            "category": "missing",
            "depends_on": [],
            "primary_crates": [],
            "required_commands": [],
            "acceptance_docs": [],
            "qa_required": False,
            "failure_route_required": False,
        }
    ticket_path = ROOT / ".loop" / "tickets" / f"{ticket_id}.md"
    if not ticket_path.is_file():
        issues.append(f"ticket file missing: {ticket_id}")
        ticket = {"ticket_id": ticket_id, "title": entry.get("title", "missing"), "status": "missing", "path": str(ticket_path)}
    else:
        ticket = parse_ticket(ticket_path)
    if not entry.get("qa_required"):
        issues.append(f"{ticket_id} qa_required must be true")
    if not entry.get("failure_route_required"):
        issues.append(f"{ticket_id} failure_route_required must be true")
    for term in ["taiko_cli qa run", "taiko_cli qa verdict"]:
        if term not in "\n".join(entry.get("required_commands", [])):
            issues.append(f"{ticket_id} required_commands missing {term}")
    for doc in entry.get("acceptance_docs", []):
        if not (ROOT / doc).exists():
            issues.append(f"acceptance doc missing: {doc}")
    for crate in entry.get("primary_crates", []):
        if not (ROOT / "crates" / crate / "Cargo.toml").is_file():
            issues.append(f"primary crate missing: {crate}")

    if ticket.get("status") != "Ready":
        missing_prerequisites.append(f"{ticket_id}: required Ready, actual {ticket.get('status')}")

    for dep in entry.get("depends_on", []):
        if dep.startswith("TKT-") and status_of_ticket(dep) != "Done":
            missing_prerequisites.append(f"{dep}: required Done, actual {status_of_ticket(dep)}")
        elif dep.startswith("GATE-"):
            actual_gate_status = status_of_gate(dep)
            if actual_gate_status != "passed":
                missing_prerequisites.append(f"{dep}: required passed, actual {actual_gate_status}")
            if not gate_report_exists(dep):
                missing_prerequisites.append(f"{dep}: missing .loop/session_logs/{dep}-report.md")

    required_support_files = [
        "docs/95_phase1_gameplay_loop_start.md",
        "operations/phase1_gameplay_loop_policy.toml",
        "prompts/72_phase1_gameplay_ticket_runner.md",
        "scripts/render_phase1_gameplay_ticket_prompt.py",
        "scripts/check_phase1_gameplay_start_static.py",
        "docs/90_session_metadata_and_path_policy.md",
        "docs/91_repair_materialization_and_retry_budget.md",
        "docs/93_github_actions_auto_merge_controller.md",
        "docs/94_e2e_smoke_loop_verification.md",
    ]
    for rel in required_support_files:
        if not (ROOT / rel).is_file():
            issues.append(f"support file missing: {rel}")

    run_id = args.run_id or os.environ.get("OPENTAIKO_PHASE1_RUN_ID") or f"RUN-PHASE1-{int(time.time())}"
    report_dir = f"reports/phase1_gameplay_loop/{run_id}"
    ready = not issues and not missing_prerequisites
    if ready:
        verdict = "ready"
        next_action = "start_phase1_gameplay_ticket_worker"
    elif args.force_preview and not issues:
        verdict = "preview_blocked"
        next_action = "render_prompt_preview_only"
    else:
        verdict = "block"
        next_action = "wait_for_phase1_entry_evidence"

    branch = f"impl/{ticket_id}-{slugify(str(ticket.get('title') or entry.get('title') or ticket_id))}"
    return {
        "schema_version": "phase1-gameplay-start/v1",
        "status": "canonical",
        "run_id": run_id,
        "ticket_id": ticket_id,
        "ticket_title": ticket.get("title") or entry.get("title"),
        "ticket_status": ticket.get("status"),
        "manifest": args.manifest,
        "manifest_first_feature_ticket": first_feature_ticket,
        "verdict": verdict,
        "next_action": next_action,
        "force_preview": bool(args.force_preview),
        "branch": branch,
        "implementation_worktree": f"worktrees/impl/{ticket_id}",
        "review_worktree": f"worktrees/review/{ticket_id}",
        "qa_worktree": f"worktrees/qa/{ticket_id}",
        "session_metadata_path": f"reports/session_metadata/{ticket_id}.toml",
        "report_dir": report_dir,
        "start_json": f"{report_dir}/phase1_gameplay_start.json",
        "start_markdown": f"{report_dir}/phase1_gameplay_start.md",
        "ticket_prompt": f"{report_dir}/phase1_ticket_prompt.md",
        "command_matrix": f"{report_dir}/phase1_command_matrix.md",
        "entry": entry,
        "ticket": ticket,
        "missing_prerequisites": missing_prerequisites,
        "issues": issues,
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Phase1 Gameplay Start Packet",
        "",
        f"- run_id: `{packet['run_id']}`",
        f"- ticket: `{packet['ticket_id']}`",
        f"- verdict: `{packet['verdict']}`",
        f"- next_action: `{packet['next_action']}`",
        f"- branch: `{packet['branch']}`",
        f"- implementation_worktree: `{packet['implementation_worktree']}`",
        f"- review_worktree: `{packet['review_worktree']}`",
        f"- qa_worktree: `{packet['qa_worktree']}`",
        "",
        "## Missing prerequisites",
        "",
    ]
    missing = packet.get("missing_prerequisites") or []
    lines += [f"- {item}" for item in missing] or ["- none"]
    lines += ["", "## Issues", ""]
    issues = packet.get("issues") or []
    lines += [f"- {item}" for item in issues] or ["- none"]
    return "\n".join(lines) + "\n"


def render_prompt(packet: dict[str, Any]) -> str:
    entry = packet["entry"]
    lines = [
        f"# Phase1 Gameplay Ticket Worker: {packet['ticket_id']}",
        "",
        f"Run ID: `{packet['run_id']}`",
        f"Verdict: `{packet['verdict']}`",
        f"Next action: `{packet['next_action']}`",
        "",
        "## Authorization",
        "",
    ]
    if packet["verdict"] == "ready":
        lines.append("This start packet is ready. You may implement exactly this ticket and create a PR after evidence is produced.")
    elif packet["verdict"] == "preview_blocked":
        lines.append("This is a preview only. Do not implement. The entry evidence is still missing.")
    else:
        lines.append("Do not implement. The Phase1 gameplay entry evidence is missing or invalid.")
    lines += [
        "",
        "## Required reads",
        "",
        "- `AGENTS.md`",
        "- `prompts/72_phase1_gameplay_ticket_runner.md`",
        "- `docs/95_phase1_gameplay_loop_start.md`",
        "- `docs/24_phase1_normal_play_compatibility_contract.md`",
        "- `docs/27_phase1_open_taiko_compatibility_boundary.md`",
        "- `research/opentaiko/10_phase1_adoption_decisions.md`",
        "- `operations/phase1_feature_ticket_manifest.toml`",
        f"- `.loop/tickets/{packet['ticket_id']}.md`",
        "",
        "## Work assignment",
        "",
        f"- Ticket: `{packet['ticket_id']}`",
        f"- Title: {packet.get('ticket_title')}",
        f"- Stage: `{entry.get('stage')}`",
        f"- Category: `{entry.get('category')}`",
        f"- Branch: `{packet['branch']}`",
        f"- Implementation worktree: `{packet['implementation_worktree']}`",
        f"- Review worktree: `{packet['review_worktree']}`",
        f"- QA worktree: `{packet['qa_worktree']}`",
        "",
        "## Required commands",
        "",
    ]
    for command in entry.get("required_commands", []):
        lines.append(f"- `{command}`")
    lines += [
        "",
        "## Hard stops",
        "",
        "- Do not modify QA verdict files from an implementation session.",
        "- Do not mark tickets Done.",
        "- Do not pass gates.",
        "- Do not use `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`.",
        "- Route reject/block through the Step19 repair materialization path.",
    ]
    return "\n".join(lines) + "\n"


def render_command_matrix(packet: dict[str, Any]) -> str:
    entry = packet["entry"]
    lines = [
        f"# Command Matrix for {packet['ticket_id']}",
        "",
        f"Category: `{entry.get('category')}`",
        "",
        "| Command | Required |",
        "|---|---:|",
    ]
    for command in entry.get("required_commands", []):
        lines.append(f"| `{command}` | yes |")
    return "\n".join(lines) + "\n"


def write_outputs(packet: dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    out = ROOT / packet["report_dir"]
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / packet["start_json"]).write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / packet["start_markdown"]).write_text(render_markdown(packet), encoding="utf-8")
    (ROOT / packet["ticket_prompt"]).write_text(render_prompt(packet), encoding="utf-8")
    (ROOT / packet["command_matrix"]).write_text(render_command_matrix(packet), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Phase1 gameplay ticket start packet.")
    parser.add_argument("--ticket", default=DEFAULT_TICKET)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--run-id")
    parser.add_argument("--force-preview", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=["json", "markdown", "prompt"], default="json")
    args = parser.parse_args()
    packet = build_start_packet(args)
    if args.format == "json":
        print(json.dumps(packet, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(render_markdown(packet), end="")
    else:
        print(render_prompt(packet), end="")
    write_outputs(packet, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
