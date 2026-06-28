# Scripts

Status: canonical

These scripts are lightweight bootstrap helpers. They do not replace the Rust CLI commands defined in `docs/40_loop_cli_contract.md` and `docs/53_ci_commands.md`. `TKT-0000` uses these scripts because Rust workspace and `taiko_cli` do not exist yet.

## Scripts

| Script | Purpose |
|---|---|
| `check_bootstrap_consistency.sh` | Runs the bootstrap consistency gate checks. |
| `check_reference_integrity.py` | Checks operational Markdown path references against committed files. |
| `check_autonomy_scorecard.py` | Checks that the package is governed by the autonomous loop scorecard and transition rules. |
| `validate_fixture_manifest.py` | Validates `fixtures/synthetic/phase1_synthetic_manifest.toml` against committed `.tja` fixtures. |
| `list_ready_tickets.sh` | Lists tickets with `Status: Ready`. |
| `validate_no_user_assets.sh` | Checks for common media/chart asset extensions under user-selected fixture directories. |
| `loop_create_branch.sh` | Creates a deterministic ticket branch. |
| `loop_create_worktree.sh` | Creates a deterministic ticket branch and isolated worktree. |
| `loop_open_pr.sh` | Pushes a ticket branch and opens a PR through GitHub CLI. |
| `loop_apply_qa_verdict.py` | Converts QA pass/reject/block JSON into ticket transition evidence. |
| `loop_merge_and_advance.sh` | Merges a passing ticket PR and runs next-ticket selection. |
| `check_github_pr_orchestration_static.py` | Validates GitHub orchestration wiring. |
| `check_github_actions_gate_static.py` | Validates OPS-0005 GitHub Actions gate normalization, required check names, workflow_run success guards, and controller concurrency. |
| `run_rust_preflight.sh` | Runs cargo and `taiko_cli` dynamic preflight and emits runtime evidence. |
| `check_runtime_evidence_files.py` | Validates Rust preflight JSON/Markdown/log evidence. |
| `check_rust_preflight_static.py` | Validates Rust preflight wiring without requiring Rust. |
| `codex_cloud_setup.sh` | Provisions the pinned Rust toolchain and checks Codex Cloud / CI setup. |
| `ci_local_equivalent.sh` | Runs static checks and, in runtime mode, the Rust preflight evidence path. |
| `check_codex_cloud_env_static.py` | Validates Codex Cloud, toolchain, secret/network, and CI wiring without requiring Rust. |
| `loop_run_once.sh` | Runs the loop run-once controller once through `taiko_cli loop run-once`. |
| `check_loop_controller_static.py` | Validates loop run-once controller wiring without requiring Rust. |
| `check_repair_materialization_static.py` | Validates repair materialization and retry-budget route, failure classification, and retry-budget wiring without requiring Rust. |
| `render_next_codex_prompt.py` | Renders a ChatGPT-plan Codex automation Codex Automation prompt without requiring Rust or API keys. |
| `check_codex_automation_static.py` | Validates ChatGPT-plan Codex operation Codex Cloud/App Automation wiring and forbids API-key AI workers in workflows. |
| `check_auto_merge_conditions.py` | Validates auto-merge controller wiring, candidate evidence, and OPS-0006 candidate fixtures. |
| `select_auto_merge_candidate.py` | Selects one `loop:automerge` PR candidate from GitHub PR JSON and emits pass/reject/block plans. |
| `loop_controller_github.sh` | Plans or applies the GitHub Actions loop-controller step without AI API calls. |
| `loop_auto_merge_pr.sh` | Validates candidate evidence, writes merge history, and squash-merges a PR. |
| `loop_revert_last_merge.sh` | Writes regression evidence and creates a revert PR outside dry-run mode. |
| `run_e2e_smoke_loop.sh` | Runs the E2E smoke loop pass/reject/block/retry/revert smoke loop without AI API calls. |
| `check_e2e_smoke_static.py` | Validates E2E smoke loop wiring and runs a temporary dry-run smoke scenario. |

## Policy

Scripts must not read, copy, or commit user-selected song assets. User-selected validation uses manifest paths only.

After `taiko_cli` exists, CLI JSON output becomes the source of truth for loop status, gate verdicts, fixture validation, headless autoplay, timing analysis, QA verdicts, and failure feedback.

## GitHub orchestration scripts

The GitHub orchestration scripts are intentionally thin wrappers around Git, GitHub CLI, and machine-readable QA verdict files. They do not approve tickets. They only enforce deterministic branch/worktree/PR/merge/advance mechanics defined in `docs/84_github_pr_loop_contract.md`.

Use `--dry-run` before allowing a Control Session to mutate GitHub state.

## Rust preflight scripts

`run_rust_preflight.sh` is the first non-static acceptance surface for the Rust workspace. It must run in GitHub Actions, Codex Cloud, or another Rust-enabled runner.

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
```

Generated reports remain under `reports/preflight/latest/` and are normally CI artifacts, not committed files.


## Codex Cloud / CI environment scripts

`codex_cloud_setup.sh` is the setup command to paste into the Codex Cloud environment. It installs the pinned Rust toolchain from `rust-toolchain.toml`, verifies `rustfmt` and `clippy`, and runs static environment checks.

`ci_local_equivalent.sh --static-only` is the no-Rust operator check. Running `ci_local_equivalent.sh` without `--static-only` requires Rust and invokes the runtime preflight.


## loop run-once controller scripts

`loop_run_once.sh` is the shell wrapper for the loop run-once controller command. Plan mode is read-only. Apply mode writes controller artifacts only under `reports/loop/<run_id>/`.

```bash
scripts/loop_run_once.sh --mode plan
scripts/loop_run_once.sh --mode apply
```

`check_loop_controller_static.py` is included in `ci_local_equivalent.sh --static-only` so bootstrap validation can confirm the controller surface without requiring Rust.


## session separation checks

```bash
scripts/check_session_separation.py
scripts/check_role_path_policy.py
scripts/loop_create_worktree.sh TKT-0005 --role impl --dry-run
scripts/loop_create_worktree.sh TKT-0005 --role review --dry-run
scripts/loop_create_worktree.sh TKT-0005 --role qa --dry-run
```


## repair materialization and retry-budget route scripts

```bash
scripts/check_repair_materialization_static.py
```

The repair materialization and retry-budget route static check validates that `taiko_cli` exposes `loop failure classify`, `loop ticket materialize --from-failure`, and `loop retry-budget check`, and that the supporting policy files and templates are committed.


## ChatGPT-plan Codex automation scripts

```bash
scripts/check_codex_automation_static.py
scripts/render_next_codex_prompt.py --mode automation --dry-run
scripts/render_next_codex_prompt.py --mode automation
```

`render_next_codex_prompt.py` is the no-Rust fallback for generating `reports/loop/<run_id>/next_codex_prompt.md`. It does not call OpenAI APIs and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.


## auto-merge controller controller scripts

```bash
scripts/check_auto_merge_conditions.py
scripts/loop_controller_github.sh --mode plan
scripts/loop_auto_merge_pr.sh --ticket TKT-0005 --pr 12 --metadata reports/session_metadata/TKT-0005.toml --qa reports/qa/TKT-0005.verdict.json --dry-run
scripts/loop_revert_last_merge.sh --run-id RUN-20260626-0001 --reason regression --dry-run
```

These scripts do not call OpenAI APIs. They only validate gates, record merge history, merge passing PRs, and create revert evidence.


## E2E smoke loop scripts

```bash
scripts/check_e2e_smoke_static.py
scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
```

The smoke script composes controller, metadata, repair, retry-budget, auto-merge dry-run, and revert dry-run surfaces. It does not call OpenAI APIs and does not require Rust.

## Phase1 gameplay worker handoff

| Script | Purpose |
|---|---|
| `render_phase1_gameplay_ticket_prompt.py` | Renders the first Phase1 gameplay ticket start packet for `TKT-0005` without calling OpenAI APIs. Defaults to `block` until `TKT-0060` and `GATE-0090` evidence exists. |
| `check_phase1_gameplay_start_static.py` | Validates Phase1 gameplay worker handoff docs, policy, prompt, renderer, and bootstrap/CI integration. |
| `check_runtime_step_terms_static.py` | Validates runtime-facing loop files use feature names instead of historical `StepXX` labels. |

Example:

```bash
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --force-preview --dry-run --format prompt
scripts/check_phase1_gameplay_start_static.py
```


| `check_public_repository_static.py` | Validates OPS-0003 public repository hardening: license/notice/security files, workflow safety, no AI worker API keys, no `pull_request_target`, no committed asset payloads, and no secret literals. |

## OPS-0004 asset bundle scripts

- `scripts/check_asset_bundle_manifest.py` validates the deterministic Google Drive zip manifest shape.
- `scripts/fetch_dev_asset_bundle.py` performs dry-run validation or real download, sha256 verification, safe zip extraction, and report emission.

Both scripts are API-key free. They are gate utilities, not AI worker entrypoints.


## OPS-0005 GitHub Actions gate scripts

```bash
scripts/check_github_actions_gate_static.py
```

This script validates required check context names, workflow permissions, `persist-credentials` policy, `workflow_run` success guards, and `loop-controller-main` concurrency. It does not call AI providers and does not require OpenAI API keys.


## OPS-0006 auto-merge candidate discovery scripts

`select_auto_merge_candidate.py` consumes `gh pr list` JSON or fixtures, writes `reports/loop/candidates/candidate_plan.json`, and never calls AI providers. `loop_controller_github.sh` calls it before any merge attempt.

## OPS-0007 ticket advance engine scripts

| Script | Purpose |
|---|---|
| `loop_advance_ticket.py` | Consumes merge history and writes ticket transition evidence under `reports/loop/ticket_transitions/`. |
| `check_ticket_transition_static.py` | Validates ticket transition policy, schema, current Ready ticket, and the OPS-0006 -> OPS-0007 fixture. |

These scripts do not call AI providers and do not require `OPENAI_API_KEY` or `CODEX_API_KEY`.


## OPS-0008 worker handoff

- `scripts/loop_emit_worker_handoff.py` emits `reports/loop/worker_handoff/latest.json`, `latest.md`, `latest_issue.md`, and `latest_comment.md`.
- `scripts/check_worker_handoff_static.py` validates the policy, schema, workflow integration, and no-API-key boundary.
