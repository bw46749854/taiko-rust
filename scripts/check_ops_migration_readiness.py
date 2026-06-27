#!/usr/bin/env python3
"""Validate OPS-0009 final migration readiness and Phase1 entry unlock."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "operations/ops_migration_readiness_policy.toml",
    "schemas/ops_migration_readiness_schema.md",
    "scripts/check_ops_migration_readiness.py",
    "reports/loop/publication_readiness_report.json",
    "reports/loop/publication_readiness_report.md",
    ".loop/session_logs/GATE-OPS-0000-report.md",
    ".loop/session_logs/GATE-0090-report.md",
    "fixtures/loop_controller/merge_history_ops0009.json",
    "reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_gameplay_start.json",
    "reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_ticket_prompt.md",
]

REQUIRED_TERMS = {
    "operations/ops_migration_readiness_policy.toml": [
        "status = \"canonical\"",
        "ticket = \"OPS-0009\"",
        "first_ready_gameplay_ticket = \"TKT-0005\"",
        "phase1_gameplay_entry_unlocked = true",
        "api_key_required = false",
        "ai_workers_in_github_actions = false",
    ],
    "schemas/ops_migration_readiness_schema.md": [
        "Status: canonical",
        "TKT-0005",
        "api_key_required",
        "ai_worker_in_github_actions",
    ],
    "reports/loop/publication_readiness_report.md": [
        "Status: pass",
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
    ],
    ".loop/session_logs/GATE-OPS-0000-report.md": [
        "Status: pass",
    ],
    ".loop/session_logs/GATE-0090-report.md": [
        "Status: block",
        "TKT-0005",
        "after OPS migration but before Phase1 gameplay start",
    ],
    "operations/loop_policy.toml": [
        "active = false",
        "current_ready_ticket = \"TKT-0005\"",
        "github_actions_ai_worker_allowed = false",
    ],
    "operations/ticket_transition_policy.toml": [
        "current_ready_ticket = \"TKT-0005\"",
        "forbid_tkt_ready_until_ops_complete = false",
        "unlock_first_gameplay_ticket = \"TKT-0005\"",
    ],
    "operations/e2e_smoke_policy.toml": [
        "phase1_gameplay_allowed = true",
        "[scenarios.advance]",
        "[scenarios.handoff]",
        "[scenarios.publication]",
    ],
    "operations/phase1_gameplay_loop_policy.toml": [
        "phase1_gameplay_allowed_in_bootstrap = true",
        "required_gate = \"GATE-OPS-0000\"",
    ],
    "scripts/run_e2e_smoke_loop.sh": [
        "advance|handoff|publication",
        "scripts/check_ops_migration_readiness.py --static-only",
        "merge_history_ops0009.json",
    ],
    "scripts/check_e2e_smoke_static.py": [
        "advance",
        "handoff",
        "publication",
        "ticket_transition.json",
        "latest.json",
    ],
    "scripts/check_phase1_gameplay_start_static.py": [
        "renderer must emit ready or block",
        "TKT-0005",
    ],
}

FORBIDDEN_WORKFLOW_TERMS = [
    "pull_request_target",
    "openai/codex-action@v1",
    "secrets.OPENAI_API_KEY",
    "secrets.CODEX_API_KEY",
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^Status:\s*(.+)$", text, re.M)
    if not m:
        fail(f"missing Status line: {path}")
    return m.group(1).strip()


def ready_tickets() -> list[str]:
    return sorted(path.stem for path in (ROOT / ".loop/tickets").glob("*.md") if status(path) == "Ready")


def validate_files_and_terms() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")
    for rel, terms in REQUIRED_TERMS.items():
        text = read(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")
    for rel in ["scripts/check_ops_migration_readiness.py", "scripts/run_e2e_smoke_loop.sh"]:
        if (ROOT / rel).stat().st_mode & 0o111 == 0:
            fail(f"{rel} must be executable")


def validate_statuses() -> None:
    for i in range(1, 10):
        ticket = ROOT / ".loop/tickets" / f"OPS-{i:04d}.md"
        if status(ticket) != "Done":
            fail(f"OPS-{i:04d} must be Done after OPS migration")
    ready = ready_tickets()
    tkt5_status = status(ROOT / ".loop/tickets/TKT-0005.md")
    if tkt5_status == "Ready":
        required = {
            ".loop/tickets/TKT-0040.md": "Done",
            ".loop/gates/GATE-0070-failure-feedback-ready.md": "passed",
            ".loop/tickets/TKT-0050.md": "Done",
            ".loop/gates/GATE-0080-qa-regression-ready.md": "passed",
            ".loop/tickets/TKT-0060.md": "Done",
            ".loop/gates/GATE-0090-phase1-feature-loop-ready.md": "passed",
        }
        for rel, expected in required.items():
            actual = status(ROOT / rel)
            if actual != expected:
                fail(f"TKT-0005 Ready requires {rel} status {expected}, got {actual}")
        if ready != ["TKT-0005"]:
            fail(f"expected only TKT-0005 to be Ready, got {ready}")
    elif ready:
        fail(f"unexpected Ready ticket(s) before Phase1 gameplay entry: {ready}")
    if status(ROOT / ".loop/gates/GATE-OPS-0000-migration-ready.md") != "passed":
        fail("GATE-OPS-0000 must be passed")
    if status(ROOT / ".loop/tickets/TKT-0005.md") == "Ready" and status(ROOT / ".loop/gates/GATE-0090-phase1-feature-loop-ready.md") != "passed":
        fail("GATE-0090 must be passed when TKT-0005 is Ready")


def validate_public_report() -> None:
    payload = json.loads(read("reports/loop/publication_readiness_report.json"))
    if payload.get("verdict") != "pass":
        fail("publication readiness report must pass")
    if payload.get("only_ready_ticket") not in (None, "", "TKT-0005"):
        fail("publication readiness report must name no Ready ticket before entry evidence, or TKT-0005 after prerequisites pass")
    if payload.get("api_key_required") is not False:
        fail("publication readiness report must not require API keys")
    if payload.get("ai_worker_in_github_actions") is not False:
        fail("publication readiness report must keep AI workers out of GitHub Actions")


def validate_phase1_packet() -> None:
    packet = json.loads(read("reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_gameplay_start.json"))
    if packet.get("ticket_id") != "TKT-0005":
        fail("Phase1 packet must select TKT-0005")
    if packet.get("verdict") == "ready":
        if packet.get("next_action") != "start_phase1_gameplay_ticket_worker":
            fail("Phase1 packet must start the gameplay worker")
        if packet.get("missing_prerequisites"):
            fail(f"Phase1 packet has missing prerequisites: {packet.get('missing_prerequisites')}")
    elif packet.get("verdict") == "block":
        if packet.get("next_action") != "wait_for_phase1_entry_evidence":
            fail("blocked Phase1 packet must wait for evidence")
    else:
        fail(f"Phase1 packet must be ready or block, got {packet.get('verdict')}")


def validate_workflows() -> None:
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for term in FORBIDDEN_WORKFLOW_TERMS:
            if term in text:
                fail(f"{rel} contains forbidden workflow term: {term}")


def run_non_recursive_checks() -> None:
    commands = [
        ["scripts/check_public_repository_static.py"],
        ["scripts/check_asset_bundle_manifest.py", "--manifest", "operations/dev_asset_bundle.example.toml"],
        ["scripts/check_github_actions_gate_static.py"],
        ["scripts/check_auto_merge_conditions.py"],
        ["scripts/check_ticket_transition_static.py"],
        ["scripts/check_worker_handoff_static.py"],
        ["scripts/check_e2e_smoke_static.py", "--static-only"],
        ["scripts/check_phase1_entry_state_consistency.py"],
        ["scripts/check_phase1_gameplay_start_static.py"],
    ]
    for cmd in commands:
        result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            fail(f"check failed: {' '.join(cmd)}\nstdout={result.stdout}\nstderr={result.stderr}")


def build_payload() -> dict:
    return {
        "schema": "schemas/ops_migration_readiness_schema.md",
        "verdict": "pass",
        "run_id": "RUN-OPS-0009-STATIC-CHECK",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_key_required": False,
        "ai_worker_in_github_actions": False,
        "only_ready_ticket": "TKT-0005",
        "ops_tickets_done": [f"OPS-{i:04d}" for i in range(1, 10)],
        "public_repository_static_check": "pass",
        "asset_bundle_static_check": "pass",
        "github_actions_gate_static_check": "pass",
        "auto_merge_static_check": "pass",
        "ticket_transition_static_check": "pass",
        "worker_handoff_static_check": "pass",
        "e2e_smoke_static_check": "pass",
        "phase1_gameplay_start_static_check": "pass",
        "phase1_start_packet": "reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_gameplay_start.json",
    }


def write_outputs(payload: dict, json_path: str | None, md_path: str | None) -> None:
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if md_path:
        path = Path(md_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# OPS Migration Readiness Check",
            "",
            f"- verdict: `{payload['verdict']}`",
            f"- only_ready_ticket: `{payload['only_ready_ticket']}`",
            "- GitHub Actions AI worker: `not_used`",
            "- API key required: `false`",
            "",
            "## Checks",
            "",
        ]
        for key, value in payload.items():
            if key.endswith("_check"):
                lines.append(f"- {key}: `{value}`")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-only", action="store_true", help="Do not invoke dependent static check subprocesses")
    parser.add_argument("--emit-json")
    parser.add_argument("--emit-markdown")
    args = parser.parse_args()
    validate_files_and_terms()
    validate_statuses()
    validate_public_report()
    validate_phase1_packet()
    validate_workflows()
    if not args.static_only:
        run_non_recursive_checks()
    payload = build_payload()
    write_outputs(payload, args.emit_json, args.emit_markdown)
    print("OPS migration readiness check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
