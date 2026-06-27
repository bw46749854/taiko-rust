# CI Commands

Status: canonical

## 1. Baseline code checks

```bash
cargo fmt --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

## 2. Synthetic fixture validation

```bash
taiko_cli fixture validate \
  --manifest fixtures/synthetic/phase1_synthetic_manifest.toml \
  --emit-report out/fixture_validation.json

taiko_cli headless autoplay \
  --manifest fixtures/synthetic/phase1_synthetic_manifest.toml \
  --emit-timing-log out/synthetic_timing.jsonl

taiko_cli timing analyze \
  --input out/synthetic_timing.jsonl \
  --profile phase1-synthetic \
  --emit-json out/synthetic_analyzer.json \
  --emit-md out/synthetic_analyzer.md
```

## 3. User-selected song validation

```bash
taiko_cli user-song validate \
  --manifest fixtures/user_selected/manifests/user_song_manifest.yaml \
  --emit-report out/user_song_validation.json \
  --emit-timing-log out/user_song_timing.jsonl

taiko_cli timing analyze \
  --input out/user_song_timing.jsonl \
  --profile phase1-user-selected \
  --emit-json out/user_song_analyzer.json \
  --emit-md out/user_song_analyzer.md
```

## 4. Coverage report

```bash
taiko_cli report coverage \
  --features docs/coverage/phase1_feature_coverage_matrix.md \
  --fixtures docs/coverage/phase1_fixture_to_feature_traceability.md \
  --user-songs docs/coverage/phase1_user_song_category_matrix.md \
  --emit-md out/phase1_coverage.md
```

## 5. Gate commands

| Gate | Commands |
|---|---|
| GATE-0010 | validate docs/coverage and schemas only |
| GATE-0100 | code checks + synthetic validation + analyzer |
| GATE-0200 | user-song validation + analyzer |

Final Phase1 CI requires GATE-0100 and GATE-0200 on the same commit.

## 6. Step15 Rust preflight command

The first dynamic CI command surface is:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
```

The generated report is the required runtime evidence for `TKT-0001` and `GATE-0030`.

`current-package` scope covers cargo checks, Loop CLI inspection, fixture validation, headless autoplay, timing analyzer, failure feedback, QA verdict, and Phase1 feature-planning commands already present in this bootstrap package.


## 7. Step16 Codex Cloud / CI environment commands

The setup and local CI-equivalent surfaces are:

```bash
scripts/codex_cloud_setup.sh
scripts/ci_local_equivalent.sh --static-only
scripts/ci_local_equivalent.sh --out reports/preflight/latest
```

`rust-toolchain.toml` is the canonical Rust version contract. CI and Codex Cloud setup must use the pinned channel from that file, not an implicit floating stable toolchain.

Secret and network policy is defined in `docs/87_secret_and_network_policy.md`. Workflows that check out or run repository-controlled code must not expose `OPENAI_API_KEY` or `CODEX_API_KEY` as job-level environment variables.

## 8. OPS-0004 asset bundle commands

```bash
scripts/check_asset_bundle_manifest.py --manifest operations/dev_asset_bundle.example.toml
scripts/fetch_dev_asset_bundle.py --manifest operations/dev_asset_bundle.example.toml --dry-run
```

Real development asset execution uses a private manifest with a real Google Drive file id and sha256. After verification, the zip is extracted to `.external_assets/opentaiko/` and commands may set `OPENTAIKO_CONTENT_ROOT=.external_assets/opentaiko` or pass `--content-root .external_assets/opentaiko`. GitHub Actions does not require an OpenAI API key for this gate.


## 9. OPS-0005 GitHub Actions gate normalization

GitHub Actions required check contexts are canonicalized by `operations/auto_merge_policy.toml` and validated by:

```bash
scripts/check_github_actions_gate_static.py
```

The required PR check contexts are:

- `loop-pr-gate / loop-pr-gate`
- `rust-preflight / rust-preflight`
- `phase1-loop / phase1-loop`
- `phase1-gameplay-entry / phase1-gameplay-entry`

`loop-controller.yml` uses `concurrency: loop-controller-main` and may proceed from a `workflow_run` event only when `github.event.workflow_run.conclusion == 'success'`. The controller is privileged for merge mechanics, so it must not checkout untrusted PR head code. GitHub Actions does not call AI providers and does not require OpenAI API keys.


## 10. OPS-0006 Auto-merge candidate discovery

```bash
scripts/check_auto_merge_conditions.py
scripts/select_auto_merge_candidate.py --input fixtures/loop_controller/pass_candidate.json --out reports/loop/candidates/pass_candidate_plan.json --expect pass
scripts/select_auto_merge_candidate.py --input fixtures/loop_controller/reject_candidate.json --out reports/loop/candidates/reject_candidate_plan.json --expect reject
scripts/select_auto_merge_candidate.py --input fixtures/loop_controller/block_candidate.json --out reports/loop/candidates/block_candidate_plan.json --expect block
scripts/loop_controller_github.sh --mode plan --pr-json fixtures/loop_controller/pass_candidate.json --dry-run
```


## 11. OPS-0007 Ticket advance engine

```bash
scripts/check_ticket_transition_static.py
scripts/loop_advance_ticket.py \
  --merge-history fixtures/loop_controller/merge_history_ops0006.json \
  --mode plan \
  --allow-dry-run-history \
  --out reports/loop/ticket_transitions/ops0006_to_ops0007_plan.json \
  --markdown reports/loop/ticket_transitions/ops0006_to_ops0007_plan.md \
  --expect pass
```

The ticket advance engine consumes merge history and writes `reports/loop/ticket_transitions/<run_id>.json`. It does not call Codex/GPT and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.


## OPS-0008 worker handoff commands

```bash
scripts/check_worker_handoff_static.py
scripts/loop_emit_worker_handoff.py --mode plan --run-id RUN-HANDOFF-LOCAL --expect plan
```

The outputs are `reports/loop/worker_handoff/latest.json`, `reports/loop/worker_handoff/latest.md`, `reports/loop/worker_handoff/latest_issue.md`, and `reports/loop/worker_handoff/latest_comment.md`.
