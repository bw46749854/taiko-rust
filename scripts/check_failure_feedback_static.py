#!/usr/bin/env python3
"""Static validation for failure feedback route MVP."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = [
    "docs/48_failure_feedback_loop_contract.md",
    "docs/07_failure_feedback_protocol.md",
    "docs/40_loop_cli_contract.md",
    "templates/failure_report_template.md",
    "reports/failures/FF-0001-sample-timing-cli-contract-error.md",
    ".loop/tickets/TKT-0040.md",
    ".loop/gates/GATE-0070-failure-feedback-ready.md",
    "crates/taiko_cli/src/lib.rs",
]
CHECKS = [
    ("crates/taiko_cli/src/lib.rs", ["loop failure ingest", "loop ticket propose", "loop ticket validate", "--from-failure", "FailureReport", "FailureIngestReport", "ProposedTicket", "TicketValidationReport", "duplicate_key", "parse_failure_report_file", "propose_ticket_from_failure", "validate_repair_ticket", "render_failure_ingest"]),
    ("docs/48_failure_feedback_loop_contract.md", ["loop failure ingest", "loop ticket propose --from-failure", "loop ticket validate", "duplicate_key", "failure_id", "reproduction_command", "regression_command"]),
    ("docs/40_loop_cli_contract.md", ["failure feedback route command surface"]),
    (".loop/tickets/TKT-0040.md", ["taiko_cli loop failure ingest reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json", "taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json", "taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json", "GATE-0070"]),
    (".loop/gates/GATE-0070-failure-feedback-ready.md", ["Failure ingest verdict", "Proposed ticket", "Ticket validation", "reports/failure_feedback/FF-0001.ingest.json"]),
    ("reports/failures/FF-0001-sample-timing-cli-contract-error.md", ["Failure ID | FF-0001", "Category | timing_cli_contract_error", "Proposed new repair ticket ID | TKT-9001", "Regression command required after repair"]),
]

def main() -> int:
    failures = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            failures.append(f"missing required failure feedback file: {rel}")
    for rel, terms in CHECKS:
        path = ROOT / rel
        if not path.is_file():
            failures.append(f"missing file for term check: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                failures.append(f"{rel} missing term: {term}")
    bootstrap = ROOT / "scripts/check_bootstrap_consistency.sh"
    if bootstrap.is_file():
        text = bootstrap.read_text(encoding="utf-8")
        for term in ["docs/48_failure_feedback_loop_contract.md", "scripts/check_failure_feedback_static.py", "GATE-0070-failure-feedback-ready.md"]:
            if term not in text:
                failures.append(f"bootstrap consistency script missing failure feedback term: {term}")
    if failures:
        print("failure feedback static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("failure feedback static check passed")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
