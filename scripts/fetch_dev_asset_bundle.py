#!/usr/bin/env python3
"""Fetch, verify, and extract the deterministic development asset bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_FILE_ID = "REPLACE_WITH_GOOGLE_DRIVE_FILE_ID"
PLACEHOLDER_SHA = "0" * 64


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_manifest(path: Path) -> dict:
    if tomllib is None:
        fail("Python 3.11+ tomllib is required")
    if not path.is_file():
        fail(f"manifest not found: {path}")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    bundle = data.get("dev_asset_bundle")
    if not isinstance(bundle, dict):
        fail("manifest must contain [dev_asset_bundle]")
    return bundle


def validate_bundle(bundle: dict, *, dry_run: bool) -> None:
    expected = {
        "mode": "zip",
        "provider": "google_drive",
        "layout": "opentaiko-compatible",
        "extract_to": ".external_assets/opentaiko",
        "content_root_env": "OPENTAIKO_CONTENT_ROOT",
        "content_root_arg": "--content-root",
    }
    for key, value in expected.items():
        if bundle.get(key) != value:
            fail(f"dev_asset_bundle.{key} must be {value!r}")
    file_id = str(bundle.get("file_id", ""))
    sha256 = str(bundle.get("sha256", ""))
    if file_id == PLACEHOLDER_FILE_ID or sha256 == PLACEHOLDER_SHA:
        if dry_run:
            return
        fail("placeholder file_id/sha256 cannot be used for real fetch")
    if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
        fail("sha256 must be 64 lowercase hex characters")


def google_drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_safe_zip(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            name = info.filename
            if name.startswith("/") or ".." in Path(name).parts:
                fail(f"unsafe zip member path: {name}")


def download_file(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "opentaiko-asset-fetch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as response, out.open("wb") as fh:
            shutil.copyfileobj(response, fh)
    except urllib.error.URLError as exc:
        fail(f"download failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="operations/dev_asset_bundle.example.toml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--emit-json", default="reports/assets/asset_bundle_fetch_report.json")
    args = parser.parse_args()

    manifest = (ROOT / args.manifest).resolve()
    try:
        manifest_rel = manifest.relative_to(ROOT).as_posix()
    except ValueError:
        fail("manifest path must stay inside repository")
    bundle = read_manifest(manifest)
    validate_bundle(bundle, dry_run=args.dry_run)

    extract_to = (ROOT / str(bundle["extract_to"])).resolve()
    try:
        extract_rel = extract_to.relative_to(ROOT).as_posix()
    except ValueError:
        fail("extract path must stay inside repository")
    if not extract_rel.startswith(".external_assets/"):
        fail("extract path must be under .external_assets/")

    report = {
        "verdict": "pass",
        "manifest": manifest_rel,
        "mode": bundle["mode"],
        "provider": bundle["provider"],
        "extract_to": extract_rel,
        "content_root_env": bundle["content_root_env"],
        "content_root_arg": bundle["content_root_arg"],
        "dry_run": args.dry_run,
        "downloaded": False,
        "extracted": False,
    }

    if args.dry_run:
        out = ROOT / args.emit_json
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("asset bundle fetch dry-run passed")
        return 0

    if extract_to.exists() and not args.force:
        fail(f"extract destination already exists; use --force: {extract_rel}")
    if extract_to.exists() and args.force:
        shutil.rmtree(extract_to)
    extract_to.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="opentaiko-assets-") as tmp:
        zip_path = Path(tmp) / "bundle.zip"
        download_file(google_drive_download_url(str(bundle["file_id"])), zip_path)
        actual = sha256_file(zip_path)
        if actual != str(bundle["sha256"]):
            fail(f"sha256 mismatch: expected {bundle['sha256']} actual {actual}")
        assert_safe_zip(zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_to)
        report["downloaded"] = True
        report["extracted"] = True
        report["sha256"] = actual

    out = ROOT / args.emit_json
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"asset bundle fetched and extracted to {extract_rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
