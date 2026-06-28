# Command Matrix for TKT-0005

Category: `timing_model`

| Command | Required |
|---|---:|
| `cargo test --workspace` | yes |
| `taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json` | yes |
| `taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json` | yes |
| `taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json` | yes |
| `taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json` | yes |
