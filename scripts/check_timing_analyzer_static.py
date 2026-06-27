#!/usr/bin/env python3
"""Static validation for the Step10 Timing Analyzer MVP.

This script verifies that the package contains the timing-analyzer command
surface and contract. It does not replace cargo checks or running taiko_cli in a
Rust-enabled environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "docs/47_timing_log_analyzer_contract.md",
    "docs/43_timing_log_schema.md",
    "docs/44_timing_log_analyzer_spec.md",
    ".loop/tickets/TKT-0004.md",
    ".loop/gates/GATE-0060-timing-analyzer-ready.md",
    "fixtures/synthetic/phase1_synthetic_manifest.toml",
    "crates/taiko_timing/Cargo.toml",
    "crates/taiko_timing/src/lib.rs",
    "crates/taiko_runtime/src/lib.rs",
    "crates/taiko_cli/Cargo.toml",
    "crates/taiko_cli/src/lib.rs",
    "crates/taiko_cli/src/bin/timing_log_analyzer.rs",
]

CLI_TERMS = [
    "timing analyze --input",
    "timing analyze --manifest",
    "--threshold-ms",
    "parse_headless_autoplay_json",
    "analyze_headless_input",
    "render_timing_analysis",
]

TIMING_TERMS = [
    "TimingAnalysisReport",
    "TimingFixtureResult",
    "HeadlessTimingInput",
    "max_error_ms",
    "mean_error_ms",
    "p95_error_ms",
    "threshold_ms",
    "failure_categories",
    "parser_error",
    "chart_time_error",
    "judgement_window_error",
    "runtime_tick_error",
]

TICKET_TERMS = [
    "taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json",
    "taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json",
    "timing_log_analyzer --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json",
    "GATE-0060",
    "timing_cli_contract_error",
]

GATE_TERMS = [
    "max_error_ms <= threshold_ms",
    "mean_error_ms <= threshold_ms",
    "p95_error_ms <= threshold_ms",
    "analyzed_event_count > 0",
    "reports/timing/phase1_synthetic.perfect.analysis.json",
]

CONTRACT_TERMS = [
    "Required JSON fields",
    "MVP pass/fail rules",
    "Failure categories",
    "taiko_cli timing analyze --input",
    "taiko_cli timing analyze --manifest",
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
            fail(f"missing required Step10 file: {rel}", failures)

    require_terms(ROOT / "crates/taiko_cli/src/lib.rs", CLI_TERMS, failures)
    require_terms(ROOT / "crates/taiko_timing/src/lib.rs", TIMING_TERMS, failures)
    require_terms(ROOT / ".loop/tickets/TKT-0004.md", TICKET_TERMS, failures)
    require_terms(ROOT / ".loop/gates/GATE-0060-timing-analyzer-ready.md", GATE_TERMS, failures)
    require_terms(ROOT / "docs/47_timing_log_analyzer_contract.md", CONTRACT_TERMS, failures)

    cli_manifest = ROOT / "crates/taiko_cli/Cargo.toml"
    if cli_manifest.is_file():
        text = cli_manifest.read_text(encoding="utf-8")
        if 'taiko_timing = { path = "../taiko_timing" }' not in text:
            fail("taiko_cli must depend on taiko_timing for timing analyzer", failures)

    timing_binary = ROOT / "crates/taiko_cli/src/bin/timing_log_analyzer.rs"
    if timing_binary.is_file():
        text = timing_binary.read_text(encoding="utf-8")
        for term in ['"timing"', '"analyze"', "taiko_cli::run_cli"]:
            if term not in text:
                fail(f"timing_log_analyzer binary missing alias term: {term}", failures)

    if failures:
        print("timing analyzer static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("timing analyzer static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
