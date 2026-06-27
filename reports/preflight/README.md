# Preflight Reports

Status: canonical

`reports/preflight/latest/` is the default local and CI output directory for Rust-enabled preflight evidence. Generated files are ignored by Git and uploaded as CI artifacts.

Expected generated files:

```text
reports/preflight/latest/rust_preflight_report.json
reports/preflight/latest/rust_preflight_report.md
reports/preflight/latest/commands.tsv
reports/preflight/latest/logs/<command-id>.stdout.log
reports/preflight/latest/logs/<command-id>.stderr.log
```

The repository must not commit generated preflight logs unless a later ticket explicitly requires a small redacted evidence sample. The preflight uses committed synthetic fixtures only and must not read, copy, upload, or commit user-selected assets.
