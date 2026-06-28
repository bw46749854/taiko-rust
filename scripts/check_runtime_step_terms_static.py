#!/usr/bin/env python3
"""Validate runtime-facing loop files use feature names instead of StepXX labels."""
from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEP_RE = re.compile(r"\bStep(?:7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23)\b")
PATTERNS = [
    "AGENTS.md",
    ".loop/tickets/*.md",
    ".loop/gates/*.md",
    "docs/*.md",
    "docs/**/*.md",
    "crates/**/*.rs",
    "scripts/*.py",
    "scripts/*.sh",
    "scripts/README.md",
    "operations/*.toml",
    "prompts/*.md",
    "templates/*.toml",
]
ALLOWLIST = [
    "docs/history/*",
    "docs/changelog*",
    "CHANGELOG*",
]


def iter_targets() -> list[Path]:
    seen: set[Path] = set()
    targets: list[Path] = []
    for pattern in PATTERNS:
        for path in ROOT.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                targets.append(path)
    return sorted(targets)


def allowed(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) for pattern in ALLOWLIST)


def main() -> int:
    failures: list[str] = []
    for path in iter_targets():
        rel = path.relative_to(ROOT).as_posix()
        if allowed(rel):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = STEP_RE.search(line)
            if match:
                failures.append(f"{rel}:{lineno}: runtime-facing StepXX term remains: {match.group(0)}")
    if failures:
        print("runtime StepXX terminology check failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("runtime StepXX terminology check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
