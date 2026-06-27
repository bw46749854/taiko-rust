# 85. Rust-enabled Preflight Gate

Status: canonical

## Purpose

Step15 defines the first dynamic verification gate for the bootstrap package. Static scripts can prove that files and command contracts exist, but they cannot prove that the Rust workspace builds or that `taiko_cli` emits the JSON evidence required by later autonomous-loop stages.

The Rust-enabled preflight gate is the first required non-static proof surface. It must run in GitHub Actions, Codex Cloud, or another Rust-enabled CI runner before `TKT-0001` can be accepted as Done.

## Authority

The preflight gate is evidence for:

- `.loop/tickets/TKT-0001.md`
- `.loop/gates/GATE-0030-loop-cli-ready.md`
- `docs/40_loop_cli_contract.md`
- `docs/53_ci_commands.md`
- `docs/84_github_pr_loop_contract.md`

It does not replace Design Review Session output or QA / Regression Session verdicts. It supplies machine evidence those sessions must inspect.

## Command surface

The canonical command is:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
```

For the narrow `TKT-0001` / `GATE-0030` acceptance path, the minimum scope is:

```bash
scripts/run_rust_preflight.sh --scope loop-cli --out reports/preflight/latest
```

The default scope is `current-package` because the Step15 package already includes Step7 through Step14 Rust command surfaces. The Control Session must prefer `current-package` in CI and Codex Cloud. The narrower `loop-cli` scope is reserved for diagnosing the first workspace/Loop CLI failure before fixture, autoplay, timing, QA, and phase1-feature commands are trusted.

## Scope definitions

### `loop-cli`

Required commands:

```bash
cargo --version
rustc --version
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_rust_workspace_static.py
cargo run -p taiko_cli --bin taiko_cli -- loop inspect tickets --format json
cargo run -p taiko_cli --bin taiko_cli -- loop inspect gates --format json
cargo run -p taiko_cli --bin taiko_cli -- loop next --format json
cargo run -p taiko_cli --bin taiko_cli -- loop gate GATE-0000 --dry-run --format json
cargo run -p taiko_cli --bin taiko_cli -- loop report status --format json
```

### `current-package`

`current-package` includes all `loop-cli` commands plus the runtime command surfaces added by Step8 through Step13:

```bash
cargo run -p taiko_cli --bin taiko_cli -- fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
cargo run -p taiko_cli --bin taiko_cli -- fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
cargo run -p taiko_cli --bin taiko_cli -- headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
cargo run -p taiko_cli --bin taiko_cli -- timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
cargo run -p taiko_cli --bin taiko_cli -- loop failure ingest reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
cargo run -p taiko_cli --bin taiko_cli -- loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
cargo run -p taiko_cli --bin taiko_cli -- loop ticket validate .loop/tickets/TKT-0040.md --format json
cargo run -p taiko_cli --bin taiko_cli -- qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
cargo run -p taiko_cli --bin taiko_cli -- qa verdict --input reports/preflight/latest/generated/phase1_loop.qa.json --format json
cargo run -p taiko_cli --bin taiko_cli -- phase1 feature validate --manifest operations/phase1_feature_ticket_manifest.toml --format json
cargo run -p taiko_cli --bin taiko_cli -- phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json
```

## Evidence files

The preflight command must create:

```text
reports/preflight/latest/rust_preflight_report.json
reports/preflight/latest/rust_preflight_report.md
reports/preflight/latest/commands.tsv
reports/preflight/latest/logs/<command-id>.stdout.log
reports/preflight/latest/logs/<command-id>.stderr.log
```

`reports/preflight/latest/` is a local or CI artifact path. The repository tracks `reports/preflight/README.md`, not generated logs.

The evidence JSON schema is intentionally small and stable:

```json
{
  "schema_version": "rust-preflight.v1",
  "scope": "current-package",
  "verdict": "pass",
  "summary": {"total": 0, "passed": 0, "failed": 0, "blocked": 0},
  "commands": [],
  "environment": {}
}
```

## Verdict rules

| Condition | Verdict | Required transition |
|---|---|---|
| Every command exits `0` | `pass` | `TKT-0001` may continue to review and `GATE-0030` may evaluate. |
| `cargo --version` or `rustc --version` fails | `block` | Fix Codex Cloud / CI Rust environment before implementation proceeds. |
| Rust toolchain exists but any cargo or `taiko_cli` command fails | `reject` | Route to failure feedback as `ci_tooling_error`, `workspace_skeleton_error`, or `loop_cli_contract_error`. |
| Evidence JSON is absent or malformed | `block` | Re-run preflight; do not infer pass from prose logs. |

A `block` verdict is not acceptance. A `reject` verdict is also not acceptance. Both must stop downstream parser and gameplay tickets.

## Gate integration

`GATE-0030` passes only when the Rust-enabled preflight evidence is valid and has verdict `pass` for at least `loop-cli` scope. The preferred gate report includes `current-package` scope because later Step8-Step13 command surfaces are already present in this package.

The required evidence validator is:

```bash
scripts/check_runtime_evidence_files.py \
  --path reports/preflight/latest/rust_preflight_report.json \
  --require-scope current-package \
  --require-pass
```

For first-failure diagnosis, omit `--require-pass` so the evidence contract itself can be checked even when a command fails.

## GitHub Actions integration

`.github/workflows/rust-preflight.yml` runs the preflight script with `current-package` scope, validates the evidence contract, uploads the report artifact, and fails the workflow when the preflight verdict is not `pass`.

`loop-pr-gate` remains the lightweight static and PR-contract gate. `rust-preflight` is the dynamic gate. Both are required for implementation PRs.

## Asset policy

The preflight must never read, copy, upload, or commit user-selected song assets. It uses committed synthetic fixtures only. User-selected song validation remains a later local or dedicated-runner validation surface using manifest paths.


## OPS-0005 required check name

For branch protection and auto-merge policy, this dynamic gate is identified as `rust-preflight / rust-preflight`. OPS-0005 validates that the workflow name, job id, and policy entry remain aligned.
