#!/usr/bin/env python3
"""Check that operational Markdown path references point to existing files or directories.

Legacy preparation logs are intentionally absent from the active scan set.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ["docs", "prompts", ".loop", "operations", "templates", "scripts"]
SCAN_FILES = ["AGENTS.md", "README.md"]
PATH_PREFIXES = (
    "docs/", "prompts/", "templates/", "fixtures/", ".loop/", "scripts/",
    "operations/", "research/", "AGENTS.md", "README.md",
)
# Paths that are generated as outputs by the loop rather than pre-existing inputs.
ALLOW_MISSING = {
    ".loop/session_logs/GATE-0000-report.md",
    ".loop/session_logs/GATE-0010-report.md",
    ".loop/session_logs/GATE-0020-report.md",
    ".loop/session_logs/GATE-0030-report.md",
    ".loop/session_logs/GATE-0040-report.md",
    "out/fixture_validation.json",
    "out/synthetic_timing.jsonl",
    "out/synthetic_analyzer.json",
    "out/synthetic_analyzer.md",
    "out/user_song_validation.json",
    "out/user_song_timing.jsonl",
    "out/user_song_analyzer.json",
    "out/user_song_analyzer.md",
    "out/phase1_coverage.md",
}
ALLOW_PREFIXES = (
    "target/", "worktrees/", "crates/", "bins/", "out/", "reports/", "fixtures/user_selected/manifests/",
)
TOKEN_RE = re.compile(r"`([^`]+)`|\(([^)]+)\)")


def iter_scan_files():
    for rel in SCAN_FILES:
        path = ROOT / rel
        if path.is_file():
            yield path
    for rel_dir in SCAN_DIRS:
        d = ROOT / rel_dir
        if not d.exists():
            continue
        for path in d.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".sh", ".py"}:
                yield path


def extract_candidate(token: str) -> str | None:
    token = token.strip().strip('"').strip("'")
    if not token or "<" in token or ">" in token:
        return None
    # Drop line anchors or markdown anchors.
    token = token.split("#", 1)[0]
    if not token:
        return None
    if token.endswith(":"):
        token = token[:-1]
    if token.startswith(("http://", "https://", "mailto:")):
        return None
    if "*" in token or ".." in token or "-" in token:
        return None
    if token.startswith(ALLOW_PREFIXES):
        return None
    if token in ALLOW_MISSING:
        return None
    if not (token.startswith(PATH_PREFIXES) or token in {"AGENTS.md", "README.md"}):
        return None
    # Short index references such as docs/00 or docs/24-27 are headings, not file paths.
    if Path(token).suffix == "" and not (ROOT / token).exists():
        return None
    return token


def main() -> int:
    failures: list[str] = []
    for path in iter_scan_files():
        text = path.read_text(encoding="utf-8")
        rel_source = path.relative_to(ROOT).as_posix()
        for match in TOKEN_RE.finditer(text):
            raw = match.group(1) or match.group(2) or ""
            # Some command examples contain multiple args in one backtick; check only clean path-like tokens.
            for part in re.split(r"\s+", raw):
                cand = extract_candidate(part.rstrip(",.;"))
                if not cand:
                    continue
                target = ROOT / cand
                if not target.exists():
                    failures.append(f"{rel_source}: missing reference: {cand}")
    if failures:
        print("reference integrity check failed", file=sys.stderr)
        for item in failures:
            print(item, file=sys.stderr)
        return 1
    print("reference integrity check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
