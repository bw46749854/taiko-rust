#!/usr/bin/env python3
"""Static validation for Step19 repair-ticket materialization and retry budget."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "docs/91_repair_materialization_and_retry_budget.md",
    "operations/failure_classification_rules.toml",
    "operations/retry_budget.toml",
    "templates/repair_ticket_template.md",
    "templates/blocker_ticket_template.md",
    "reports/retry_budget/README.md",
    "crates/taiko_cli/src/lib.rs",
]

CHECKS = [
    ("crates/taiko_cli/src/lib.rs", [
        "loop failure classify",
        "loop ticket materialize --from-failure",
        "loop retry-budget check",
        "FailureClassificationReport",
        "MaterializedTicketReport",
        "RetryBudgetReport",
        "classify_failure_report",
        "materialize_ticket_from_failure",
        "check_retry_budget",
        "render_failure_classification",
        "render_materialized_ticket",
        "render_retry_budget_report",
        "operations/retry_budget.toml",
        "Status: Ready",
        "already_exists",
        "original_ticket_should_remain",
    ]),
    ("docs/91_repair_materialization_and_retry_budget.md", [
        "loop failure classify --input",
        "loop ticket materialize --from-failure",
        "loop retry-budget check --ticket",
        "reject",
        "block",
        "TKT-REPAIR",
        "TKT-ENV",
        "TKT-SPEC",
        "TKT-TOOL",
        "max_repair_attempts_per_ticket",
    ]),
    ("operations/failure_classification_rules.toml", [
        "route.reject",
        "route.block_spec",
        "route.block_tool",
        "route.block_env",
        "timing_cli_contract_error",
        "spec_ambiguity",
    ]),
    ("operations/retry_budget.toml", [
        "max_repair_attempts_per_ticket = 3",
        "max_block_attempts_per_gate = 2",
        "max_same_failure_signature = 2",
        "max_controller_runs_per_hour = 4",
    ]),
    ("docs/40_loop_cli_contract.md", [
        "Step19 repair materialization and retry-budget command surface",
        "taiko_cli loop failure classify --input",
        "taiko_cli loop ticket materialize --from-failure",
        "taiko_cli loop retry-budget check --ticket",
    ]),
    ("docs/48_failure_feedback_loop_contract.md", [
        "Step19 materialization contract",
        "materialized_ticket_id",
        "original_ticket_should_remain",
    ]),
    ("scripts/ci_local_equivalent.sh", ["scripts/check_repair_materialization_static.py"]),
    ("scripts/check_bootstrap_consistency.sh", [
        "docs/91_repair_materialization_and_retry_budget.md",
        "operations/retry_budget.toml",
        "scripts/check_repair_materialization_static.py",
    ]),
]


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            failures.append(f"missing required Step19 file: {rel}")
    for rel, terms in CHECKS:
        path = ROOT / rel
        if not path.is_file():
            failures.append(f"missing file for term check: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                failures.append(f"{rel} missing term: {term}")
    script = ROOT / "scripts/check_repair_materialization_static.py"
    if script.is_file() and not (script.stat().st_mode & 0o111):
        failures.append("scripts/check_repair_materialization_static.py must be executable")
    if failures:
        print("repair materialization static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("repair materialization static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
