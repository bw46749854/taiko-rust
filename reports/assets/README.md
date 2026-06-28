# Asset Bundle Reports

Status: canonical
Migration ticket: OPS-0004

This directory stores generated evidence about development asset bundle validation and fetch operations.

Expected generated files include:

- `asset_bundle_manifest_check.json`
- `asset_bundle_fetch_dry_run.json`
- `asset_bundle_fetch_report.json`

These reports may contain file ids and sha256 values. They must not contain OAuth tokens, signed URLs, service-account JSON, or copied asset payloads.
