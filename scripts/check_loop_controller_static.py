#!/usr/bin/env python3
"""Static validation for loop run-once controller foundation.

This check intentionally does not require Rust. Runtime validation remains the
responsibility of Rust preflight in a Rust-enabled environment.
"""
from __future__ import annotations

import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/88_auto_merge_loop_policy.md",
    "docs/89_loop_controller_state_machine.md",
    "operations/loop_policy.toml",
    "scripts/loop_run_once.sh",
    "scripts/check_loop_controller_static.py",
    "crates/taiko_cli/src/lib.rs",
    "reports/loop/README.md",
]

REQUIRED_TERMS = {
    "crates/taiko_cli/src/lib.rs": [
        "LoopRunOncePlan",
        "loop run-once --mode plan",
        "loop run-once --mode apply",
        "build_loop_run_once_plan",
        "apply_loop_run_once_plan",
        "render_loop_run_once_plan",
        "next_codex_prompt",
        "start_worker",
        "classify_failure",
        "wait_for_ready_ticket",
        "Test Infrastructure Session",
    ],
    "docs/88_auto_merge_loop_policy.md": [
        "Status: canonical",
        "auto-merge",
        "loop run-once",
        "OPENAI_API_KEY",
        "Codex Cloud",
        "Codex App",
        "reports/loop/<run_id>/controller_plan.json",
    ],
    "docs/89_loop_controller_state_machine.md": [
        "Status: canonical",
        "ready_ticket",
        "open_failures",
        "no_ready_ticket",
        "taiko_cli loop run-once --mode plan --format json",
        "scripts/loop_run_once.sh --mode apply",
        "implementation_worktree",
        "next_codex_prompt",
    ],
    "operations/loop_policy.toml": [
        "canonical",
        "api_key_required = false",
        "auto_merge_target = true",
        "auto_merge_enabled_in_current_package = true",
        "max_worker_parallelism = 1",
    ],
    "scripts/loop_run_once.sh": [
        "set -euo pipefail",
        "loop run-once",
        "--mode plan|apply",
        "cargo run -p taiko_cli --bin taiko_cli",
    ],
    "README.md": [
        "loop run-once",
        "loop run-once",
        "scripts/loop_run_once.sh --mode plan",
    ],
    "AGENTS.md": [
        "Loop CLI command surface",
        "loop run-once",
        "OPENAI_API_KEY",
    ],
    "prompts/60_final_bootstrap_prompt.md": [
        "Status: canonical",
        "docs/88_auto_merge_loop_policy.md",
        "docs/89_loop_controller_state_machine.md",
        "scripts/loop_run_once.sh --mode plan",
    ],
}

DEPRECATED_ACTION_TERMS = [
    "openai/codex-action@v1 as the primary worker",
    "OPENAI_API_KEY as required for loop-controller",
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read_text(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    for rel, terms in REQUIRED_TERMS.items():
        text = read_text(rel)
        for term in terms:
            if term not in text:
                fail(f"{rel} missing required term: {term}")
        for term in DEPRECATED_ACTION_TERMS:
            if term in text:
                fail(f"{rel} contains deprecated loop-controller worker term: {term}")

    mode = (ROOT / "scripts/loop_run_once.sh").stat().st_mode
    if mode & stat.S_IXUSR == 0:
        fail("scripts/loop_run_once.sh must be executable")

    ci = read_text("scripts/ci_local_equivalent.sh")
    if "scripts/check_loop_controller_static.py" not in ci:
        fail("ci_local_equivalent.sh must run check_loop_controller_static.py")

    bootstrap = read_text("scripts/check_bootstrap_consistency.sh")
    for term in [
        "docs/88_auto_merge_loop_policy.md",
        "docs/89_loop_controller_state_machine.md",
        "operations/loop_policy.toml",
        "scripts/loop_run_once.sh",
        "scripts/check_loop_controller_static.py",
    ]:
        if term not in bootstrap:
            fail(f"check_bootstrap_consistency.sh missing loop-controller term: {term}")

    print("loop controller static check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
