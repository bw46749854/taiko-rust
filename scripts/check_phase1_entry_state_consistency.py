#!/usr/bin/env python3
"""Validate Phase1 entry state consistency after OPS migration."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PREREQUISITES = [
    (".loop/tickets/TKT-0040.md", "Done", "TKT-0040 Done"),
    (".loop/gates/GATE-0070-failure-feedback-ready.md", "passed", "GATE-0070 passed"),
    (".loop/tickets/TKT-0050.md", "Done", "TKT-0050 Done"),
    (".loop/gates/GATE-0080-qa-regression-ready.md", "passed", "GATE-0080 passed"),
    (".loop/tickets/TKT-0060.md", "Done", "TKT-0060 Done"),
    (".loop/gates/GATE-0090-phase1-feature-loop-ready.md", "passed", "GATE-0090 passed"),
]

REQUIRED_EVIDENCE = {
    "TKT-0040/GATE-0070": [
        "reports/failure_feedback/FF-0001.ingest.json",
        "reports/failure_feedback/FF-0001.proposed_ticket.json",
        "reports/failure_feedback/TKT-0040.validate.json",
    ],
    "TKT-0050/GATE-0080": [
        "reports/qa/phase1_loop.qa.json",
        "reports/qa/phase1_loop.verdict.json",
    ],
    "TKT-0060/GATE-0090": [
        "reports/phase1_feature_loop/phase1_feature_validate.json",
        "reports/phase1_feature_loop/phase1_feature_plan.json",
        ".loop/session_logs/GATE-0090-report.md",
    ],
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def status(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing state file: {rel}")
    m = re.search(r"^Status:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    if not m:
        fail(f"missing Status line: {rel}")
    return m.group(1).strip()


def missing_prerequisites() -> list[str]:
    missing = []
    for rel, expected, label in PREREQUISITES:
        actual = status(rel)
        if actual != expected:
            missing.append(f"{label} (actual: {actual})")
    return missing


def require_evidence_when_passed() -> None:
    if status(".loop/tickets/TKT-0040.md") == "Done" or status(".loop/gates/GATE-0070-failure-feedback-ready.md") == "passed":
        for rel in REQUIRED_EVIDENCE["TKT-0040/GATE-0070"]:
            if not (ROOT / rel).is_file():
                fail(f"TKT-0040/GATE-0070 cannot be complete without evidence: {rel}")
    if status(".loop/tickets/TKT-0050.md") == "Done" or status(".loop/gates/GATE-0080-qa-regression-ready.md") == "passed":
        for rel in REQUIRED_EVIDENCE["TKT-0050/GATE-0080"]:
            if not (ROOT / rel).is_file():
                fail(f"TKT-0050/GATE-0080 cannot be complete without evidence: {rel}")
    if status(".loop/tickets/TKT-0060.md") == "Done" or status(".loop/gates/GATE-0090-phase1-feature-loop-ready.md") == "passed":
        for rel in REQUIRED_EVIDENCE["TKT-0060/GATE-0090"]:
            if not (ROOT / rel).is_file():
                fail(f"TKT-0060/GATE-0090 cannot be complete without evidence: {rel}")


def require_policy_alignment() -> None:
    policy = (ROOT / "operations/ticket_transition_policy.toml").read_text(encoding="utf-8")
    manifest = (ROOT / "operations/phase1_feature_ticket_manifest.toml").read_text(encoding="utf-8")
    ready = status(".loop/tickets/TKT-0005.md") == "Ready"
    expected = 'current_ready_ticket = "TKT-0005"'
    if ready and expected not in policy:
        fail("ticket transition policy must name TKT-0005 as current_ready_ticket when TKT-0005 is Ready")
    for term in ['first_feature_ticket = "TKT-0005"', 'required_entry_gate = "GATE-0090"', 'required_qa_gate = "GATE-0080"']:
        if term not in manifest:
            fail(f"phase1 feature manifest missing {term}")


def main() -> int:
    require_evidence_when_passed()
    require_policy_alignment()
    if status(".loop/tickets/TKT-0005.md") == "Ready":
        missing = missing_prerequisites()
        if missing:
            fail("TKT-0005 Ready requires all Phase1 entry prerequisites: " + "; ".join(missing))
    print("phase1 entry state consistency check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
