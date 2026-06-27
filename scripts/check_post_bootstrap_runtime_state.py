#!/usr/bin/env python3
"""Validate post-bootstrap runtime state after the OPS migration rail.

This check is intentionally separate from check_bootstrap_consistency.sh:
bootstrap consistency validates package invariants, while this script validates
current operational state such as the single Ready gameplay ticket and its gate
chain.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        fail(f"check failed: {' '.join(cmd)}\nstdout={result.stdout}\nstderr={result.stderr}")
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Forward static-only mode to OPS readiness to avoid recursive dependent checks.",
    )
    args = parser.parse_args()

    ops_cmd = ["scripts/check_ops_migration_readiness.py"]
    if args.static_only:
        ops_cmd.append("--static-only")

    # OPS readiness owns the TKT-0005 Ready prerequisite gate chain. The
    # Phase1 entry checks own rendered start-packet validity.
    run(ops_cmd)
    run(["scripts/check_phase1_entry_state_consistency.py"])
    run(["scripts/check_phase1_gameplay_start_static.py"])
    print("post-bootstrap runtime state check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
