#!/usr/bin/env python3
"""Validate that the bootstrap package is governed by the autonomy scorecard.

This check intentionally validates operational documents only. Historical source material
and root-level legacy preparation logs are absent from the active package.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "docs/00_project_objective.md",
    "docs/04_loop_operational_maturity_model.md",
    "docs/05_autonomy_scorecard.md",
    "docs/06_gate_transition_rules.md",
    "docs/07_failure_feedback_protocol.md",
    "docs/40_loop_cli_contract.md",
    "AGENTS.md",
    "README.md",
    ".loop/gates/GATE-0000-spec-repair.md",
    ".loop/gates/GATE-0010-coverage-ready.md",
    ".loop/gates/GATE-0020-implementation-ready.md",
    ".loop/gates/GATE-0030-loop-cli-ready.md",
    ".loop/tickets/TKT-0000.md",
    ".loop/gates/GATE-OPS-0000-migration-ready.md",
    ".loop/tickets/OPS-0001.md",
    ".loop/tickets/OPS-0002.md",
    ".loop/tickets/OPS-0003.md",
    ".loop/tickets/OPS-0004.md",
    ".loop/tickets/OPS-0005.md",
    ".loop/tickets/OPS-0006.md",
    ".loop/tickets/OPS-0007.md",
    ".loop/tickets/OPS-0008.md",
    ".loop/tickets/OPS-0009.md",
    "docs/97_public_repository_hardening.md",
    "operations/public_repository_policy.toml",
    "scripts/check_public_repository_static.py",
    "operations/ticket_transition_policy.toml",
    "scripts/loop_advance_ticket.py",
    "scripts/check_ticket_transition_static.py",
    "operations/worker_handoff_policy.toml",
    "scripts/loop_emit_worker_handoff.py",
    "scripts/check_worker_handoff_static.py",
]

AXES = {
    "A1": ("Session / worktree governance", 10),
    "A2": ("Ticket / gate machine-readability", 15),
    "A3": ("Buildable Rust substrate", 15),
    "A4": ("Executable test harness", 15),
    "A5": ("Timing / audio self-verification", 20),
    "A6": ("Regression / CI enforcement", 15),
    "A7": ("Failure feedback loop", 10),
}

PROHIBITED_PATTERNS = [
    r"ask\s+(a\s+)?human\s+to\s+decide",
    r"wait\s+for\s+(a\s+)?human",
    r"human\s+approval\s+required",
    r"manual\s+approval\s+required",
    r"manual\s+decision\s+required",
    r"人間が判断",
    r"人間の判断が必要",
    r"人間承認",
    r"手動承認",
]

SCAN_DIRS = ["docs", "prompts", ".loop", "operations", "templates", "scripts"]
SCAN_FILES = ["AGENTS.md", "README.md"]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def operational_files() -> list[Path]:
    paths: list[Path] = []
    for rel in SCAN_FILES:
        p = ROOT / rel
        if p.is_file():
            paths.append(p)
    for rel in SCAN_DIRS:
        d = ROOT / rel
        if d.exists():
            for p in d.rglob("*"):
                if p.is_file() and p.suffix in {".md", ".py", ".sh"}:
                    paths.append(p)
    return paths


def main() -> int:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            failures.append(f"missing required autonomy file: {rel}")

    if not failures:
        objective = read("docs/00_project_objective.md")
        required_objective_terms = [
            "top-level objective",
            "self-driving AI session loop",
            "without additional human design or judgement",
        ]
        for term in required_objective_terms:
            if term not in objective:
                failures.append(f"docs/00_project_objective.md missing objective term: {term}")

        score = read("docs/05_autonomy_scorecard.md")
        for axis_id, (axis_name, weight) in AXES.items():
            if axis_id not in score:
                failures.append(f"scorecard missing axis id: {axis_id}")
            if axis_name not in score:
                failures.append(f"scorecard missing axis name: {axis_name}")
            if f"| {axis_id} | {axis_name} | {weight} |" not in score:
                failures.append(f"scorecard missing canonical row for {axis_id} weight {weight}")
        if sum(weight for _, weight in AXES.values()) != 100:
            failures.append("internal error: scorecard weights do not sum to 100")

        gate_rules = read("docs/06_gate_transition_rules.md")
        for required in ["pass", "reject", "block", "Next-ticket selection rule"]:
            if required not in gate_rules:
                failures.append(f"gate transition rules missing: {required}")

        failure_protocol = read("docs/07_failure_feedback_protocol.md")
        for required in ["Failure categories", "Required failure report fields", "Failure-to-ticket routing", "Duplicate prevention"]:
            if required not in failure_protocol:
                failures.append(f"failure feedback protocol missing: {required}")

        loop_cli = read("docs/40_loop_cli_contract.md")
        for cmd in [
            "taiko_cli loop inspect tickets",
            "taiko_cli loop inspect gates",
            "taiko_cli loop next",
            "taiko_cli loop gate GATE-0000 --dry-run",
            "taiko_cli loop report status",
            "--format json",
        ]:
            if cmd not in loop_cli:
                failures.append(f"loop CLI contract missing command or flag: {cmd}")

        for gate in sorted((ROOT / ".loop/gates").glob("GATE-*.md")):
            text = gate.read_text(encoding="utf-8")
            rel = gate.relative_to(ROOT).as_posix()
            for section in [
                "## Autonomy scorecard impact",
                "## Required inputs",
                "## Pass criteria",
                "## Failure handling",
                "## Output",
                "## Next-ticket transition",
            ]:
                if section not in text:
                    failures.append(f"{rel} missing section: {section}")
            if not any(axis in text for axis in AXES):
                failures.append(f"{rel} does not reference any autonomy scorecard axis")

        ready_tickets = []
        for ticket in sorted((ROOT / ".loop/tickets").glob("*.md")):
            text = ticket.read_text(encoding="utf-8")
            if re.search(r"^Status:\s*Ready\s*$", text, flags=re.MULTILINE):
                ready_tickets.append(ticket)
                if "Next-ticket transition evidence" not in text:
                    failures.append(f"{ticket.relative_to(ROOT)} is Ready but lacks Next-ticket transition evidence")
        if ready_tickets and (len(ready_tickets) != 1 or ready_tickets[0].name != "TKT-0005.md"):
            failures.append("expected no Ready gameplay ticket before entry evidence, or only TKT-0005 when entry prerequisites pass")

    for path in operational_files():
        if path.name == "check_autonomy_scorecard.py":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for pattern in PROHIBITED_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                failures.append(f"{rel} contains prohibited human-decision phrase matching: {pattern}")

    if failures:
        print("autonomy scorecard check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("autonomy scorecard check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
