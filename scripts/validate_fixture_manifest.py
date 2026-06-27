#!/usr/bin/env python3
"""Validate the concrete Phase1 synthetic fixture manifest without external dependencies."""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "fixtures/synthetic/phase1_synthetic_manifest.toml"
TRACE = ROOT / "docs/coverage/phase1_fixture_to_feature_traceability.md"


def main() -> int:
    if not MANIFEST.is_file():
        print(f"missing manifest: {MANIFEST.relative_to(ROOT)}", file=sys.stderr)
        return 1
    data = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != "phase1-synthetic-manifest/v1":
        print("invalid schema_version", file=sys.stderr)
        return 1
    fixtures = data.get("fixtures") or []
    if data.get("fixture_count") != len(fixtures):
        print("fixture_count does not match manifest entries", file=sys.stderr)
        return 1
    tja_files = sorted((ROOT / "fixtures/synthetic").rglob("*.tja"))
    if len(fixtures) != len(tja_files):
        print(f"manifest has {len(fixtures)} entries but synthetic tree has {len(tja_files)} .tja files", file=sys.stderr)
        return 1
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    failures: list[str] = []
    for fx in fixtures:
        fid = fx.get("fixture_id")
        rel = fx.get("path")
        if not fid or not isinstance(fid, str):
            failures.append("fixture entry missing fixture_id")
            continue
        if fid in seen_ids:
            failures.append(f"duplicate fixture_id: {fid}")
        seen_ids.add(fid)
        if not rel or not isinstance(rel, str):
            failures.append(f"{fid}: missing path")
            continue
        if rel in seen_paths:
            failures.append(f"duplicate path: {rel}")
        seen_paths.add(rel)
        if not (ROOT / rel).is_file():
            failures.append(f"{fid}: missing fixture file {rel}")
        if not fx.get("primary_features"):
            failures.append(f"{fid}: primary_features is empty")
        if not fx.get("expected_event_types"):
            failures.append(f"{fid}: expected_event_types is empty")
        if "headless_required" not in fx:
            failures.append(f"{fid}: headless_required is missing")
        if "assertions" not in fx:
            failures.append(f"{fid}: assertions is missing")
    tja_rel = {p.relative_to(ROOT).as_posix() for p in tja_files}
    missing_from_manifest = sorted(tja_rel - seen_paths)
    if missing_from_manifest:
        failures.append("fixture files missing from manifest: " + ", ".join(missing_from_manifest))
    if TRACE.is_file():
        trace_text = TRACE.read_text(encoding="utf-8")
        for fid in seen_ids:
            if fid not in trace_text:
                failures.append(f"{fid}: not present in traceability document")
    if failures:
        print("fixture manifest validation failed", file=sys.stderr)
        for item in failures:
            print(item, file=sys.stderr)
        return 1
    print(f"fixture manifest validation passed: {len(fixtures)} fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
