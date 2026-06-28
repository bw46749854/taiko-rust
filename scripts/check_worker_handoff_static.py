#!/usr/bin/env python3
"""Validate OPS-0008 worker handoff wiring."""
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
    "docs/99_codex_worker_handoff_contract.md",
    "operations/worker_handoff_policy.toml",
    "schemas/worker_handoff_schema.md",
    "prompts/73_next_ticket_handoff.md",
    "scripts/loop_emit_worker_handoff.py",
    "scripts/check_worker_handoff_static.py",
    ".github/ISSUE_TEMPLATE/codex_ticket.md",
    ".github/workflows/loop-worker-handoff.yml",
    "reports/loop/worker_handoff/README.md",
    "scripts/render_next_codex_prompt.py",
    "scripts/loop_controller_github.sh",
    ".github/workflows/loop-controller.yml",
    "operations/loop_policy.toml",
    "operations/auto_merge_policy.toml",
    "operations/ticket_transition_policy.toml",
    "README.md",
    "AGENTS.md",
    "docs/81_human_operator_minimal_steps.md",
    "docs/92_codex_plus_automation_operation.md",
    "prompts/70_codex_automation_loop_runner.md",
    "prompts/71_codex_cloud_ticket_worker.md",
]

REQUIRED_TERMS = {
    "docs/99_codex_worker_handoff_contract.md": [
        "Status: canonical",
        "OPS-0008",
        "scripts/loop_emit_worker_handoff.py",
        "reports/loop/worker_handoff/latest.json",
        "latest_issue.md",
        "api_key_required: false",
        "ai_worker_in_github_actions: false",
        "vars.LOOP_AUTOMATION_ARMED == 'true'",
        "Blocked",
    ],
    "operations/worker_handoff_policy.toml": [
        "status = \"canonical\"",
        "ticket = \"TKT-0005\"",
        "emitter = \"scripts/loop_emit_worker_handoff.py\"",
        "static_check = \"scripts/check_worker_handoff_static.py\"",
        "schema = \"schemas/worker_handoff_schema.md\"",
        "api_key_required = false",
        "ai_workers_in_github_actions = false",
        "current_ready_ticket = \"TKT-0005\"",
        "automation_armed = false",
        "workflow_run_handoff_requires_armed = true",
        "blocked_ticket_handoff_verdict = \"block\"",
    ],
    "schemas/worker_handoff_schema.md": [
        "Status: canonical",
        "latest.json",
        "selected_ticket",
        "allowed_paths",
        "forbidden_paths",
        "api_key_required",
        "ai_worker_in_github_actions",
    ],
    "scripts/loop_emit_worker_handoff.py": [
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "openai/codex-action@v1",
        "reports/loop/worker_handoff/latest.json",
        "selected_ticket",
        "required_reads",
        "allowed_paths",
        "forbidden_paths",
        "--expect",
        "blocked_ticket_status",
        "Preview plan for Ready ticket",
    ],
    "scripts/render_next_codex_prompt.py": [
        "OPS-0008 worker handoff",
        "reports/loop/worker_handoff/latest.md",
        "scripts/loop_emit_worker_handoff.py",
    ],
    "scripts/loop_controller_github.sh": [
        "scripts/loop_emit_worker_handoff.py",
        "reports/loop/worker_handoff",
        "GitHub Actions only gates",
    ],
    ".github/workflows/loop-controller.yml": [
        "scripts/check_worker_handoff_static.py",
        "scripts/loop_emit_worker_handoff.py --mode controller",
        "reports/loop/worker_handoff/",
        "vars.LOOP_AUTOMATION_ARMED == 'true'",
    ],
    ".github/workflows/loop-worker-handoff.yml": [
        "name: loop-worker-handoff",
        "workflow_run:",
        "github.event.workflow_run.conclusion == 'success'",
        "vars.LOOP_AUTOMATION_ARMED == 'true'",
        "scripts/check_worker_handoff_static.py",
        "scripts/loop_emit_worker_handoff.py --mode issue",
        "persist-credentials: false",
        "OPENAI_API_KEY",
    ],
    "prompts/73_next_ticket_handoff.md": [
        "Status: canonical",
        "reports/loop/worker_handoff/latest.json",
        "OPENAI_API_KEY",
        "Work on the selected ticket only",
    ],
    "README.md": [
        "OPS-0008",
        "worker handoff",
        "scripts/loop_emit_worker_handoff.py",
    ],
    "AGENTS.md": [
        "OPS-0008 Next Codex worker handoff",
        "Actions must not call AI providers",
    ],
    "docs/81_human_operator_minimal_steps.md": [
        "OPS-0008",
        "reports/loop/worker_handoff/latest.md",
    ],
    "docs/92_codex_plus_automation_operation.md": [
        "OPS-0008 worker handoff",
        "reports/loop/worker_handoff/latest.md",
        "scripts/loop_emit_worker_handoff.py",
    ],
    "prompts/70_codex_automation_loop_runner.md": [
        "reports/loop/worker_handoff/latest.md",
        "scripts/loop_emit_worker_handoff.py",
    ],
    "prompts/71_codex_cloud_ticket_worker.md": [
        "reports/loop/worker_handoff/latest.md",
        "prompts/73_next_ticket_handoff.md",
    ],
}

FORBIDDEN_TERMS = [
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


def parse_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip()
    fail(f"missing Status line: {path}")


def validate_files_and_terms() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")
    for rel in ["scripts/loop_emit_worker_handoff.py", "scripts/check_worker_handoff_static.py"]:
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
    policy = tomllib.loads(read("operations/worker_handoff_policy.toml"))
    if policy.get("api_key_required") is not False:
        fail("worker handoff policy must not require API keys")
    if policy.get("ai_workers_in_github_actions") is not False:
        fail("worker handoff policy must keep AI workers out of GitHub Actions")
    if policy.get("current_ready_ticket") != "TKT-0005":
        fail("worker handoff current_ready_ticket must be TKT-0005 after OPS migration")
    if policy.get("max_selected_tickets") != 1:
        fail("worker handoff must select at most one ticket")
    if policy.get("automation_armed") is not False:
        fail("worker handoff automation must be disarmed by default")
    if policy.get("workflow_run_handoff_requires_armed") is not True:
        fail("workflow_run handoff must require the armed switch")
    if policy.get("blocked_ticket_handoff_verdict") != "block":
        fail("blocked ticket handoff must produce a block verdict")


def validate_current_ready_ticket() -> None:
    ready = []
    for ticket in sorted((ROOT / ".loop/tickets").glob("*.md")):
        if parse_status(ticket) == "Ready":
            ready.append(ticket.stem)
    if ready and ready != ["TKT-0005"]:
        fail(f"expected no Ready ticket before Phase1 entry evidence, or only TKT-0005 after entry prerequisites pass, got {ready}")
    for ticket in ["OPS-0007", "OPS-0008", "OPS-0009"]:
        if parse_status(ROOT / ".loop/tickets" / f"{ticket}.md") != "Done":
            fail(f"{ticket} must be Done after OPS migration")


def validate_no_ai_worker_workflow() -> None:
    workflows = ROOT / ".github/workflows"
    for path in workflows.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for term in FORBIDDEN_TERMS:
            if term in text:
                fail(f"{rel} contains forbidden AI worker/API key term: {term}")


def validate_handoff_execution() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        ticket_dir = tmpdir / "tickets"
        shutil.copytree(ROOT / ".loop/tickets", ticket_dir)
        out_dir = tmpdir / "handoff"
        expected = "plan" if any(parse_status(ticket) == "Ready" for ticket in ticket_dir.glob("*.md")) else "block"
        cmd = [
            str(ROOT / "scripts/loop_emit_worker_handoff.py"),
            "--ticket-dir", str(ticket_dir),
            "--mode", "plan",
            "--run-id", "RUN-HANDOFF-STATIC",
            "--latest-json", str(out_dir / "latest.json"),
            "--latest-markdown", str(out_dir / "latest.md"),
            "--latest-issue", str(out_dir / "latest_issue.md"),
            "--latest-comment", str(out_dir / "latest_comment.md"),
            "--expect", expected,
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            fail(f"worker handoff emitter failed: stdout={result.stdout} stderr={result.stderr}")
        payload = json.loads((out_dir / "latest.json").read_text(encoding="utf-8"))
        if expected == "plan" and payload.get("selected_ticket") != "TKT-0005":
            fail(f"handoff selected wrong ticket: {payload.get('selected_ticket')}")
        if expected == "block" and payload.get("selected_ticket") not in (None, ""):
            fail(f"blocked handoff must not select a ticket: {payload.get('selected_ticket')}")
        if payload.get("api_key_required") is not False:
            fail("handoff payload requires API key")
        if payload.get("ai_worker_in_github_actions") is not False:
            fail("handoff payload runs AI worker in GitHub Actions")
        for required in ["required_reads", "allowed_paths", "forbidden_paths", "required_commands"]:
            if not payload.get(required):
                fail(f"handoff payload missing non-empty {required}")
        if expected == "block":
            if payload.get("verdict") != "block":
                fail(f"blocked handoff must emit block verdict: {payload.get('verdict')}")
            if payload.get("blocked_ticket") == payload.get("selected_ticket"):
                fail("blocked handoff must not promote blocked_ticket to selected_ticket")
            if "Ready ticket selected" in json.dumps(payload):
                fail("blocked handoff must not use Ready-ticket selection wording")
        md = (out_dir / "latest.md").read_text(encoding="utf-8")
        issue = (out_dir / "latest_issue.md").read_text(encoding="utf-8")
        comment = (out_dir / "latest_comment.md").read_text(encoding="utf-8")
        for text, name in [(md, "latest.md"), (issue, "latest_issue.md"), (comment, "latest_comment.md")]:
            if expected == "plan" and "TKT-0005" not in text:
                fail(f"{name} missing TKT-0005")
            if expected == "block" and "@codex" in text:
                fail(f"{name} must not request @codex on blocked preview")
            if expected == "block" and "Do not implement" not in text and "Do not start implementation" not in text:
                fail(f"{name} missing blocked preview stop instruction")
            if "OPENAI_API_KEY" not in text:
                fail(f"{name} missing no-API-key boundary")


def main() -> int:
    validate_files_and_terms()
    validate_policy()
    validate_current_ready_ticket()
    validate_no_ai_worker_workflow()
    validate_handoff_execution()
    print("worker handoff static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
