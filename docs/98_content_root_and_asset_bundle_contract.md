# 98. Content Root and Asset Bundle Contract

Status: canonical
Migration ticket: OPS-0004

## 1. Purpose

This contract defines how development-time song, chart, and skin assets are provided to Codex Cloud and GitHub Actions without committing copyrighted or user-selected assets to the repository.

GitHub Actions remains a verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator. It does not call an OpenAI or Codex API. The asset bundle mechanism therefore uses repository scripts, Google Drive public or access-controlled file download, and sha256 verification only.

## 2. Adopted substrate

The development substrate is a single Google Drive zip file described by `operations/dev_asset_bundle.example.toml` or a private copy with real values.

The default CI substrate is not a shared Google Drive folder traversal. Folder traversal is rejected because file additions, deletions, permission changes, and filename changes can alter test inputs without changing a committed manifest. A zip with a committed sha256 value gives the loop a fixed evidence boundary.

## 3. Required layout

The zip must extract to an OpenTaiko-compatible content tree under:

```text
.external_assets/opentaiko/
```

The expected top-level layout inside the content root follows OpenTaiko-style names. The exact files are supplied by the user-selected development bundle and are not committed.

```text
.external_assets/opentaiko/
  Songs/
  System/
  Skins/
```

`Songs/` contains TJA charts and audio according to the OpenTaiko-compatible directory arrangement. `Skins/` and `System/` contain visual/system material used by smoke tests when required. Missing optional directories may be reported as `block` rather than `reject` until a gameplay ticket explicitly requires them.

## 4. Canonical runtime input

Runtime, test, CI, and production all use the same content-root input contract:

- environment variable: `OPENTAIKO_CONTENT_ROOT`
- CLI argument: `--content-root`
- default development extraction path: `.external_assets/opentaiko/`

Production mode does not use Drive. Production mode reads the user-provided OpenTaiko-compatible directory directly through the same content-root contract.

## 5. Manifest contract

The machine-readable manifest is defined by `schemas/dev_asset_bundle_schema.md`. The example file is `operations/dev_asset_bundle.example.toml`. Required fields are:

- `mode = "zip"`
- `provider = "google_drive"`
- `file_id`
- `sha256`
- `layout = "opentaiko-compatible"`
- `extract_to = ".external_assets/opentaiko"`
- `content_root_env = "OPENTAIKO_CONTENT_ROOT"`
- `content_root_arg = "--content-root"`

The manifest must not contain OAuth secrets, service account JSON, signed URLs, or private local paths.

## 6. Scripts

Static validation:

```bash
scripts/check_asset_bundle_manifest.py --manifest operations/dev_asset_bundle.example.toml
```

Dry-run fetch validation:

```bash
scripts/fetch_dev_asset_bundle.py --manifest operations/dev_asset_bundle.example.toml --dry-run
```

Real fetch in Codex Cloud or GitHub Actions uses a private manifest or repository variable that contains a real Drive file id and the expected sha256. The script verifies sha256 before extraction.

## 7. Gate behavior

A missing or placeholder development bundle is a `block`, not a gameplay `reject`. A sha256 mismatch is a hard `block` and must stop the gate before extraction. Committed user-selected assets are rejected by `scripts/validate_no_user_assets.sh` and `scripts/check_public_repository_static.py`.

## 8. Non-goals

This contract does not grant redistribution rights for songs, skins, images, videos, or charts. It does not require GitHub Actions to invoke an AI worker. It does not certify that a selected asset set covers Phase1 gameplay requirements; coverage remains owned by the Phase1 user-selected song validation and gameplay tickets.
