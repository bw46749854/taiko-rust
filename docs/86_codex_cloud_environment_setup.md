# 86. Codex Cloud Environment Setup

Status: canonical

## Purpose

This document defines the environment contract for running the OpenTaiko Phase1 autonomous loop in Codex Cloud and CI. The goal is to remove local-machine dependency for the first non-static verification gate while keeping local CLI/App use as an optional operator aid.

The canonical hosted execution surface is:

```text
GitHub private repository
  -> Codex Cloud environment
  -> scripts/codex_cloud_setup.sh
  -> scripts/run_rust_preflight.sh
  -> PR + CI evidence
  -> QA verdict / failure feedback / next ticket
```

## Codex surface decision

Use Codex Cloud for the first controlled loop run. Use Codex CLI or Codex App only as auxiliary local surfaces for inspection, local worktree management, or user-selected song validation.

| Role | Required surface |
|---|---|
| Control Session bootstrap | Codex Cloud task on private GitHub repository |
| TKT-0000 static gate | Codex Cloud or GitHub Actions |
| TKT-0001 Rust preflight | Codex Cloud or GitHub Actions with Rust toolchain |
| Design review | Detached Codex Cloud task, native `@codex review`, or `codex-review.yml` |
| QA / Regression | Separate Cloud task or CI runner, never the implementation session |
| Local song/audio/input check | Codex CLI/App or dedicated local runner |

## Repository prerequisites

1. Create a private GitHub repository.
2. Push this package to the repository without user-selected song, audio, image, video, chart, or skin assets.
3. Confirm these workflows are visible in GitHub Actions:
   - `.github/workflows/loop-pr-gate.yml`
   - `.github/workflows/rust-preflight.yml`
   - `.github/workflows/phase1-loop.yml`
   - `.github/workflows/codex-review.yml`
4. Confirm `scripts/validate_no_user_assets.sh` passes.
5. Confirm `scripts/check_codex_cloud_env_static.py` passes.

## Rust toolchain contract

The repository owns the Rust version through `rust-toolchain.toml`.

```toml
[toolchain]
channel = "1.85.1"
profile = "minimal"
components = ["rustfmt", "clippy"]
```

Do not replace this with floating `stable` inside gate evidence. A version update is a separate tooling ticket because it can change clippy diagnostics, lockfile behavior, and preflight output.

## Codex Cloud environment creation

Create one Cloud environment with this policy:

| Field | Value |
|---|---|
| Environment name | `opentaiko-phase1-loop` |
| Repository | the private OpenTaiko Phase1 Rust loop repository |
| Default branch | `main` |
| Setup command | `bash scripts/codex_cloud_setup.sh` |
| Agent internet access | off by default |
| Secrets | none required for normal ticket implementation |
| Environment variables | none required by default |

The setup script performs the network-dependent toolchain installation while setup internet access is available. After setup, the agent phase must not need public internet for normal tickets.

## Setup script

The setup script is committed at:

```bash
scripts/codex_cloud_setup.sh
```

It performs these checks:

1. Reads `rust-toolchain.toml`.
2. Installs `rustup` only when missing.
3. Installs the pinned Rust channel with `rustfmt` and `clippy`.
4. Prints `rustc`, `cargo`, `cargo fmt`, and `cargo clippy` versions.
5. Runs `scripts/check_codex_cloud_env_static.py`.
6. Runs `scripts/check_bootstrap_consistency.sh`.

It intentionally does not mark any ticket pass. It only prepares the environment and proves that the environment contract is present.

## First dynamic run

After environment setup, run the Rust preflight preflight exactly:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
```

The first ticket allowed to rely on this runtime evidence is `TKT-0001`. The first gate that requires it is `GATE-0030`.

## Failure routing

Treat failures as follows:

| Failure class | Ticket outcome | Required next action |
|---|---|---|
| `scripts/codex_cloud_setup.sh` fails before Rust install | block | create environment repair ticket |
| Rust install fails | block | repair Codex Cloud setup or GitHub Actions setup |
| `cargo fmt` / `clippy` / `test` fails | reject | create repair ticket for Rust workspace |
| `taiko_cli` command fails | reject | create repair ticket for CLI contract |
| evidence JSON missing or invalid | reject | create repair ticket for preflight evidence contract |
| no artifact uploaded in CI | block | repair workflow artifact upload |

Do not proceed to Phase1 feature implementation when `TKT-0001` has no passing Rust preflight evidence.

## Local equivalent

Operators and Codex CLI sessions may run:

```bash
scripts/ci_local_equivalent.sh --static-only
```

This requires no Rust environment. To run the full equivalent, install Rust through the setup script and then run:

```bash
scripts/codex_cloud_setup.sh
scripts/ci_local_equivalent.sh --out reports/preflight/latest
```

## Evidence paths

The accepted runtime evidence paths are:

```text
reports/preflight/latest/rust_preflight_report.json
reports/preflight/latest/rust_preflight_report.md
reports/preflight/latest/logs/*.stdout.log
reports/preflight/latest/logs/*.stderr.log
```

These are normally CI artifacts, not committed files. Ticket evidence must link or copy the artifact reference into `.loop/session_logs/` or a gate report.

## Operator minimum

The human operator should only need to:

1. create the private GitHub repository;
2. connect the repository to Codex Cloud;
3. set the Cloud setup command to `bash scripts/codex_cloud_setup.sh`;
4. start `TKT-0000`;
5. start `TKT-0001` after `GATE-0000` passes.

All later pass/reject/block transitions must use ticket/gate evidence and the PR loop contract.
