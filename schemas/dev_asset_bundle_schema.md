# Dev Asset Bundle Manifest Schema

Status: canonical
Migration ticket: OPS-0004

The development asset bundle manifest is TOML. The canonical example is `operations/dev_asset_bundle.example.toml`.

## Required table

```toml
[dev_asset_bundle]
mode = "zip"
provider = "google_drive"
file_id = "<google-drive-file-id>"
sha256 = "<64 lowercase hex characters>"
layout = "opentaiko-compatible"
extract_to = ".external_assets/opentaiko"
content_root_env = "OPENTAIKO_CONTENT_ROOT"
content_root_arg = "--content-root"
allow_placeholder = true
```

## Field rules

| Field | Rule |
|---|---|
| `mode` | Must be `zip`. |
| `provider` | Must be `google_drive`. |
| `file_id` | Required. It may be a placeholder only when `allow_placeholder = true`. |
| `sha256` | Required. Must be 64 hexadecimal characters. The all-zero example value is valid only when `allow_placeholder = true`. |
| `layout` | Must be `opentaiko-compatible`. |
| `extract_to` | Must be `.external_assets/opentaiko` or a child of `.external_assets/`. |
| `content_root_env` | Must be `OPENTAIKO_CONTENT_ROOT`. |
| `content_root_arg` | Must be `--content-root`. |
| `allow_placeholder` | Optional boolean. It is allowed only for example manifests and must not be used for a real gate pass. |

## Forbidden content

The manifest must not contain OAuth secrets, service-account JSON, signed URLs, private local paths, or raw asset payloads. Repository workflows must not echo the real resolved download URL.
