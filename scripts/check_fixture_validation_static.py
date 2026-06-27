#!/usr/bin/env python3
"""Static validation for the Step8 Fixture Validation MVP.

This script verifies that the package contains the fixture-validation command
surface and contract. It does not replace cargo checks or running taiko_cli in a
Rust-enabled environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "docs/45_fixture_validation_contract.md",
    ".loop/tickets/TKT-0002.md",
    ".loop/gates/GATE-0040-fixture-validation-ready.md",
    "fixtures/synthetic/phase1_synthetic_manifest.toml",
    "crates/taiko_chart/src/lib.rs",
    "crates/taiko_cli/src/lib.rs",
    "crates/taiko_cli/Cargo.toml",
    "scripts/validate_synthetic_fixture_structure.py",
]

CLI_TERMS = [
    "fixture validate --manifest",
    "fixture inspect",
    "validate_fixture_manifest",
    "inspect_tja_file",
]

CHART_TERMS = [
    "parse_fixture_manifest",
    "validate_fixture_manifest",
    "inspect_tja_file",
    "inspect_tja_text",
    "manifest_count_mismatch",
    "unknown_command",
    "missing_required_header",
    "no_note_tokens",
    "'A'..='Z'",
    "ChartInspectionReport",
    "FixtureValidationReport",
    "validated_count",
    "invalid_count",
    "unknown_commands",
]

TICKET_TERMS = [
    "taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json",
    "taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json",
    "GATE-0040",
    "fixture_manifest_error",
]

GATE_TERMS = [
    "declared_fixture_count = 35",
    "manifest_entry_count = 35",
    "validated_count = 35",
    "missing_count = 0",
    "invalid_count = 0",
    "duplicate_fixture_ids = []",
    "reports/fixture_validation/phase1_synthetic.json",
]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def require_terms(path: Path, terms: list[str], failures: list[str]) -> None:
    if not path.is_file():
        fail(f"missing file for term check: {path.relative_to(ROOT)}", failures)
        return
    text = path.read_text(encoding="utf-8")
    for term in terms:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing term: {term}", failures)


def main() -> int:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required Step8 file: {rel}", failures)

    require_terms(ROOT / "crates/taiko_cli/src/lib.rs", CLI_TERMS, failures)
    require_terms(ROOT / "crates/taiko_chart/src/lib.rs", CHART_TERMS, failures)
    require_terms(ROOT / ".loop/tickets/TKT-0002.md", TICKET_TERMS, failures)
    require_terms(ROOT / ".loop/gates/GATE-0040-fixture-validation-ready.md", GATE_TERMS, failures)
    require_terms(ROOT / "docs/45_fixture_validation_contract.md", CLI_TERMS[:2] + ["Required JSON fields", "MVP pass/fail rules"], failures)

    manifest_text = (ROOT / "fixtures/synthetic/phase1_synthetic_manifest.toml").read_text(encoding="utf-8")
    if manifest_text.count("[[fixtures]]") != 35:
        fail("synthetic manifest must contain exactly 35 fixture entries", failures)

    cli_manifest = ROOT / "crates/taiko_cli/Cargo.toml"
    if cli_manifest.is_file():
        text = cli_manifest.read_text(encoding="utf-8")
        if 'taiko_chart = { path = "../taiko_chart" }' not in text:
            fail("taiko_cli must depend on taiko_chart for fixture validation", failures)

    if failures:
        print("fixture validation static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("fixture validation static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
