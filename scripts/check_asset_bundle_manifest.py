#!/usr/bin/env python3
"""Validate deterministic development asset bundle manifest for OPS-0004."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER_FILE_IDS = {"", "REPLACE_WITH_GOOGLE_DRIVE_FILE_ID", "<google-drive-file-id>"}
FORBIDDEN_SUBSTRINGS = [
    "client_secret",
    "private_key",
    "refresh_token",
    "access_token",
    "service_account",
    "-----BEGIN",
    "https://drive.google.com/",
    "https://docs.google.com/",
    "file://",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_manifest(path: Path) -> dict:
    if tomllib is None:
        fail("Python 3.11+ tomllib is required")
    if not path.is_file():
        fail(f"manifest not found: {path}")
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    for term in FORBIDDEN_SUBSTRINGS:
        if term.lower() in lowered:
            fail(f"manifest contains forbidden secret/url marker: {term}")
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:  # type: ignore[attr-defined]
        fail(f"invalid TOML: {exc}")
    bundle = data.get("dev_asset_bundle")
    if not isinstance(bundle, dict):
        fail("manifest must contain [dev_asset_bundle]")
    return bundle


def validate_bundle(bundle: dict, *, allow_example_placeholders: bool) -> dict:
    required_exact = {
        "mode": "zip",
        "provider": "google_drive",
        "layout": "opentaiko-compatible",
        "content_root_env": "OPENTAIKO_CONTENT_ROOT",
        "content_root_arg": "--content-root",
    }
    for key, expected in required_exact.items():
        if bundle.get(key) != expected:
            fail(f"dev_asset_bundle.{key} must be {expected!r}")

    file_id = str(bundle.get("file_id", ""))
    sha256 = str(bundle.get("sha256", ""))
    extract_to = str(bundle.get("extract_to", ""))
    allow_placeholder = bool(bundle.get("allow_placeholder", False))

    if not extract_to:
        fail("dev_asset_bundle.extract_to is required")
    extract_path = Path(extract_to)
    if extract_path.is_absolute():
        fail("dev_asset_bundle.extract_to must be repository-relative")
    parts = extract_path.parts
    if not parts or parts[0] != ".external_assets":
        fail("dev_asset_bundle.extract_to must be under .external_assets/")
    if extract_to.rstrip("/") != ".external_assets/opentaiko":
        fail("dev_asset_bundle.extract_to must be .external_assets/opentaiko for OPS-0004")

    placeholder_file_id = file_id in PLACEHOLDER_FILE_IDS
    placeholder_sha = sha256 == "0" * 64
    if placeholder_file_id and not allow_placeholder:
        fail("placeholder file_id requires allow_placeholder = true")
    if placeholder_file_id and not allow_example_placeholders:
        fail("placeholder file_id is not allowed for real gate execution")
    if not HEX64.fullmatch(sha256):
        fail("dev_asset_bundle.sha256 must be 64 lowercase hex characters")
    if placeholder_sha and not allow_placeholder:
        fail("placeholder sha256 requires allow_placeholder = true")
    if placeholder_sha and not allow_example_placeholders:
        fail("placeholder sha256 is not allowed for real gate execution")

    return {
        "verdict": "pass",
        "mode": bundle["mode"],
        "provider": bundle["provider"],
        "layout": bundle["layout"],
        "extract_to": extract_to,
        "content_root_env": bundle["content_root_env"],
        "content_root_arg": bundle["content_root_arg"],
        "placeholder_file_id": placeholder_file_id,
        "placeholder_sha256": placeholder_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="operations/dev_asset_bundle.example.toml")
    parser.add_argument("--no-example-placeholders", action="store_true", help="reject placeholder file_id/sha256")
    parser.add_argument("--emit-json", default=None)
    args = parser.parse_args()

    manifest_path = (ROOT / args.manifest).resolve()
    try:
        manifest_path.relative_to(ROOT)
    except ValueError:
        fail("manifest path must stay inside repository")

    bundle = load_manifest(manifest_path)
    report = validate_bundle(bundle, allow_example_placeholders=not args.no_example_placeholders)
    report["manifest"] = manifest_path.relative_to(ROOT).as_posix()
    if args.emit_json:
        out = (ROOT / args.emit_json).resolve()
        try:
            out.relative_to(ROOT)
        except ValueError:
            fail("emit path must stay inside repository")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("asset bundle manifest check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
