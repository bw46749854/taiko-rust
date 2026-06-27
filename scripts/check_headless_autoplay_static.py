#!/usr/bin/env python3
"""Static validation for the Step9 Headless Autoplay MVP.

This script verifies that the package contains the headless-autoplay command
surface and contract. It does not replace cargo checks or running taiko_cli in a
Rust-enabled environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "docs/46_headless_autoplay_contract.md",
    ".loop/tickets/TKT-0003.md",
    ".loop/gates/GATE-0050-headless-autoplay-ready.md",
    "fixtures/synthetic/phase1_synthetic_manifest.toml",
    "crates/taiko_runtime/Cargo.toml",
    "crates/taiko_runtime/src/lib.rs",
    "crates/taiko_cli/Cargo.toml",
    "crates/taiko_cli/src/lib.rs",
    "crates/taiko_cli/src/bin/headless_autoplay.rs",
]

CLI_TERMS = [
    "headless autoplay --chart",
    "headless autoplay --manifest",
    "--mode perfect",
    "autoplay_chart",
    "autoplay_manifest",
    "render_headless_autoplay",
]

RUNTIME_TERMS = [
    "HeadlessAutoplayReport",
    "HeadlessFixtureResult",
    "HeadlessMode",
    "autoplay_chart",
    "autoplay_manifest",
    "note_count",
    "scheduled_event_count",
    "hit_count",
    "miss_count",
    "song_end_reached",
    "total_miss_count",
    "headless_no_scheduled_notes",
]

TICKET_TERMS = [
    "taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json",
    "taiko_cli headless autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json",
    "headless_autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json",
    "GATE-0050",
    "headless_cli_contract_error",
]

GATE_TERMS = [
    "fixture_count = 35",
    "failed_count = 0",
    "total_note_count > 0",
    "total_miss_count = 0",
    "song_end_reached = true",
    "reports/headless_autoplay/phase1_synthetic.perfect.json",
]

CONTRACT_TERMS = [
    "Required JSON fields",
    "MVP pass/fail rules",
    "Failure categories",
    "taiko_cli headless autoplay --chart",
    "taiko_cli headless autoplay --manifest",
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
            fail(f"missing required Step9 file: {rel}", failures)

    require_terms(ROOT / "crates/taiko_cli/src/lib.rs", CLI_TERMS, failures)
    require_terms(ROOT / "crates/taiko_runtime/src/lib.rs", RUNTIME_TERMS, failures)
    require_terms(ROOT / ".loop/tickets/TKT-0003.md", TICKET_TERMS, failures)
    require_terms(ROOT / ".loop/gates/GATE-0050-headless-autoplay-ready.md", GATE_TERMS, failures)
    require_terms(ROOT / "docs/46_headless_autoplay_contract.md", CONTRACT_TERMS, failures)

    runtime_manifest = ROOT / "crates/taiko_runtime/Cargo.toml"
    if runtime_manifest.is_file():
        text = runtime_manifest.read_text(encoding="utf-8")
        if 'taiko_chart = { path = "../taiko_chart" }' not in text:
            fail("taiko_runtime must depend on taiko_chart for chart inspection", failures)

    cli_manifest = ROOT / "crates/taiko_cli/Cargo.toml"
    if cli_manifest.is_file():
        text = cli_manifest.read_text(encoding="utf-8")
        if 'taiko_runtime = { path = "../taiko_runtime" }' not in text:
            fail("taiko_cli must depend on taiko_runtime for headless autoplay", failures)

    headless_binary = ROOT / "crates/taiko_cli/src/bin/headless_autoplay.rs"
    if headless_binary.is_file():
        text = headless_binary.read_text(encoding="utf-8")
        for term in ['"headless"', '"autoplay"', "taiko_cli::run_cli"]:
            if term not in text:
                fail(f"headless_autoplay binary missing alias term: {term}", failures)

    if failures:
        print("headless autoplay static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("headless autoplay static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
