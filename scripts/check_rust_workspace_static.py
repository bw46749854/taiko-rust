#!/usr/bin/env python3
"""Static validation for the canonical Rust workspace and Loop CLI MVP.

This script exists because bootstrap package validation must still run in
environments where Rust is not installed. It does not replace cargo checks;
TKT-0001 still requires cargo fmt, clippy, and test in a Rust-enabled session.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CRATES = [
    "taiko_domain",
    "taiko_chart",
    "taiko_timing",
    "taiko_runtime",
    "taiko_audio",
    "taiko_render",
    "taiko_test_support",
    "taiko_cli",
]

BINARIES = [
    "taiko_cli",
    "taiko_play",
    "headless_autoplay",
    "timing_log_analyzer",
]

LOOP_COMMAND_TERMS = [
    "loop inspect tickets",
    "loop inspect gates",
    "loop next",
    "loop gate GATE-0000 --dry-run",
    "loop report status",
    "fixture validate --manifest",
    "fixture inspect",
    "headless autoplay --chart",
    "headless autoplay --manifest",
    "--mode perfect",
    "--format json",
]

REQUIRED_OUTPUT_FIELDS = [
    "tickets",
    "gates",
    "verdict",
    "missing_inputs",
    "present_inputs",
    "autonomy_score_estimate",
    "ready_tickets",
    "blocked_tickets",
    "missing_gate_evidence",
    "next_selected_ticket",
]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []

    cargo = ROOT / "Cargo.toml"
    if not cargo.is_file():
        fail("missing root Cargo.toml", failures)
    else:
        cargo_text = cargo.read_text(encoding="utf-8")
        if "[workspace]" not in cargo_text:
            fail("root Cargo.toml lacks [workspace]", failures)
        for crate in CRATES:
            if f'"crates/{crate}"' not in cargo_text:
                fail(f"root Cargo.toml missing workspace member crates/{crate}", failures)
        if "resolver = \"2\"" not in cargo_text:
            fail("root Cargo.toml must set resolver = \"2\"", failures)

    for crate in CRATES:
        crate_dir = ROOT / "crates" / crate
        if not crate_dir.is_dir():
            fail(f"missing crate directory: crates/{crate}", failures)
            continue
        if not (crate_dir / "Cargo.toml").is_file():
            fail(f"missing crate manifest: crates/{crate}/Cargo.toml", failures)
        if not (crate_dir / "src/lib.rs").is_file():
            fail(f"missing crate library: crates/{crate}/src/lib.rs", failures)

    cli_manifest = ROOT / "crates/taiko_cli/Cargo.toml"
    if cli_manifest.is_file():
        cli_manifest_text = cli_manifest.read_text(encoding="utf-8")
        for binary in BINARIES:
            if f'name = "{binary}"' not in cli_manifest_text:
                fail(f"taiko_cli manifest missing binary: {binary}", failures)
            if not (ROOT / "crates/taiko_cli/src/bin" / f"{binary}.rs").is_file():
                fail(f"missing binary source: crates/taiko_cli/src/bin/{binary}.rs", failures)

    cli_source = ROOT / "crates/taiko_cli/src/lib.rs"
    if not cli_source.is_file():
        fail("missing taiko_cli/src/lib.rs", failures)
    else:
        cli_text = cli_source.read_text(encoding="utf-8")
        for term in LOOP_COMMAND_TERMS:
            if term not in cli_text:
                fail(f"taiko_cli source missing command term: {term}", failures)
        for field in REQUIRED_OUTPUT_FIELDS:
            if field not in cli_text:
                fail(f"taiko_cli source missing JSON/status field: {field}", failures)
        for disallowed in ["serde", "clap", "anyhow", "tokio"]:
            if disallowed in cli_text:
                fail(f"taiko_cli Loop CLI MVP must not depend on external crate token: {disallowed}", failures)

    tkt = ROOT / ".loop/tickets/TKT-0001.md"
    if tkt.is_file():
        tkt_text = tkt.read_text(encoding="utf-8")
        for term in [
            "cargo fmt --all --check",
            "cargo clippy --workspace --all-targets -- -D warnings",
            "cargo test --workspace",
            "taiko_cli loop inspect tickets --format json",
            "taiko_cli loop gate GATE-0000 --dry-run --format json",
        ]:
            if term not in tkt_text:
                fail(f"TKT-0001 missing required check: {term}", failures)

    if failures:
        print("rust workspace static check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("rust workspace static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
