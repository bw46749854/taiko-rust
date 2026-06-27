#!/usr/bin/env python3
"""Validate committed synthetic TJA fixture structure without Rust.

This mirrors the Step8 Fixture Validation MVP pass/fail rules closely enough for
bootstrap-only environments. Rust-enabled sessions must still run the actual
`taiko_cli fixture ...` commands before accepting TKT-0002.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "fixtures/synthetic/phase1_synthetic_manifest.toml"
REQUIRED_HEADERS = {"TITLE", "BPM", "WAVE", "COURSE", "LEVEL"}
KNOWN_COMMANDS = {
    "#START", "#END", "#BPMCHANGE", "#MEASURE", "#DELAY", "#SCROLL",
    "#GOGOSTART", "#GOGOEND", "#BARLINE", "#BARLINEON", "#BARLINEOFF",
    "#BRANCHSTART", "#BRANCHEND", "#SECTION", "#LEVELHOLD", "#N", "#E", "#M",
    "#BMSCROLL", "#HBSCROLL", "#NMSCROLL", "#SUDDEN", "#DIRECTION", "#JPOSSCROLL",
    "#NEXTSONG", "#BGAON", "#CAMZOOM", "#LYRIC",
}


def manifest_paths() -> list[tuple[str, str]]:
    text = MANIFEST.read_text(encoding="utf-8")
    ids = re.findall(r'^fixture_id\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    paths = re.findall(r'^path\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    declared = re.search(r'^fixture_count\s*=\s*(\d+)', text, flags=re.MULTILINE)
    if declared is None:
        raise ValueError("manifest missing fixture_count")
    declared_count = int(declared.group(1))
    if declared_count != 35:
        raise ValueError(f"manifest fixture_count must be 35, got {declared_count}")
    if len(ids) != declared_count or len(paths) != declared_count:
        raise ValueError(f"manifest entry mismatch: ids={len(ids)} paths={len(paths)} declared={declared_count}")
    if len(set(ids)) != len(ids):
        raise ValueError("manifest contains duplicate fixture_id")
    return list(zip(ids, paths))


def inspect_fixture(path: Path) -> list[str]:
    issues: list[str] = []
    headers: set[str] = set()
    starts = 0
    ends = 0
    notes = 0
    digits = 0
    inside_chart = False
    text = path.read_text(encoding="utf-8")
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            command = line.split()[0].split(":", 1)[0]
            if command not in KNOWN_COMMANDS:
                issues.append(f"line {line_no}: unknown command {command}")
            if command == "#START":
                starts += 1
                inside_chart = True
            elif command == "#END":
                ends += 1
                inside_chart = False
            continue
        if ":" in line:
            headers.add(line.split(":", 1)[0].strip().upper())
            continue
        if inside_chart:
            for char in line:
                if char.isdigit():
                    digits += 1
                    if char != "0":
                        notes += 1
                elif "A" <= char <= "Z":
                    notes += 1
                elif char in {",", " ", "\t"}:
                    pass
                else:
                    issues.append(f"line {line_no}: invalid chart token {char!r}")
    missing_headers = sorted(REQUIRED_HEADERS - headers)
    if missing_headers:
        issues.append(f"missing headers: {', '.join(missing_headers)}")
    if starts == 0:
        issues.append("missing #START")
    if ends == 0:
        issues.append("missing #END")
    if ends < starts:
        issues.append(f"#END count {ends} is less than #START count {starts}")
    if notes == 0:
        issues.append(f"no non-zero note tokens; digit tokens={digits}")
    return issues


def main() -> int:
    failures: list[str] = []
    try:
        entries = manifest_paths()
    except Exception as exc:  # noqa: BLE001 - command-line validator
        print(f"synthetic fixture structure validation failed: {exc}", file=sys.stderr)
        return 1

    for fixture_id, rel_path in entries:
        path = ROOT / rel_path
        if not path.is_file():
            failures.append(f"{fixture_id}: missing {rel_path}")
            continue
        for issue in inspect_fixture(path):
            failures.append(f"{fixture_id}: {rel_path}: {issue}")

    if failures:
        print("synthetic fixture structure validation failed", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"synthetic fixture structure validation passed: {len(entries)} fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
