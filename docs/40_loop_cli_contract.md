# 40. Loop CLI Contract

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

`taiko_cli` is the machine interface for the autonomous loop. It converts Markdown ticket/gate state and validation reports into deterministic pass/fail/block decisions.

This document is the Step7 MVP contract. Step7 adds a Rust workspace and an initial `taiko_cli` implementation for the loop orchestration commands. Full gameplay, parser, headless autoplay, and timing analyzer behavior remains out of scope.

## 2. Scope for Step7 MVP

Step7 must implement the minimum loop orchestration commands before gameplay implementation expands.

Required commands:

```bash
taiko_cli loop inspect tickets
taiko_cli loop inspect gates
taiko_cli loop next
taiko_cli loop gate GATE-0000 --dry-run
taiko_cli loop report status
```

## 3. Required command behavior

### `taiko_cli loop inspect tickets`

Outputs a machine-readable list of tickets with:

- ticket ID
- title
- status
- owner session
- review session
- dependencies
- required gates
- required checks
- evidence requirements

### `taiko_cli loop inspect gates`

Outputs a machine-readable list of gates with:

- gate ID
- status
- owner
- reviewer
- required inputs
- pass criteria
- output path
- next-ticket transition
- autonomy scorecard impact

### `taiko_cli loop next`

Returns exactly one selected next ticket, or a block verdict explaining why none can proceed.

Selection priority:

1. Repair ticket required by a current reject verdict.
2. Blocking infrastructure ticket required for evidence generation.
3. Lowest-numbered Ready ticket with satisfied dependencies.
4. No selection when prerequisites are missing.

### `taiko_cli loop gate GATE-0000 --dry-run`

Checks whether gate inputs and pass criteria are present without mutating ticket state.

### `taiko_cli loop report status`

Outputs a concise current loop status report containing:

- current autonomy score estimate
- Ready tickets
- Blocked tickets
- missing gate evidence
- next selected ticket
- open failures

## 4. Output format

Every command must support JSON output by Step7 or Step8.

Required flag:

```bash
--format json
```

Human-readable Markdown output may also exist, but JSON is the source of truth for QA and CI.

## 5. Non-goals for Step7

Step7 does not need full parser, gameplay, audio, rendering, or timing analyzer implementation.

Step7 must create enough workspace and CLI substrate so later tickets can produce machine-readable loop evidence.

## 6. Acceptance criteria for TKT-0001 update

`TKT-0001` must be considered complete only when:

- Workspace compiles.
- Canonical crates exist.
- `taiko_cli` binary exists.
- Required `loop` subcommands exist.
- Commands can parse current `.loop/tickets` and `.loop/gates` files.
- `taiko_cli loop next --format json` returns `TKT-0000` before GATE-0000 is recorded as passed, or returns a block verdict after `TKT-0000` is In Progress/Done but gate reports are missing.
## 7. Step7 implementation payload

Step7 adds the canonical Rust workspace and the Loop CLI MVP substrate. The repository now contains:

- `Cargo.toml`
- `crates/taiko_domain/`
- `crates/taiko_chart/`
- `crates/taiko_timing/`
- `crates/taiko_runtime/`
- `crates/taiko_audio/`
- `crates/taiko_render/`
- `crates/taiko_test_support/`
- `crates/taiko_cli/`

Step7 intentionally uses only Rust standard-library code plus workspace-local crates. This keeps the first autonomous loop substrate independent of network package resolution.

The CLI must expose machine-readable JSON for these commands:

```bash
taiko_cli loop inspect tickets --format json
taiko_cli loop inspect gates --format json
taiko_cli loop next --format json
taiko_cli loop gate GATE-0000 --dry-run --format json
taiko_cli loop report status --format json
```

`headless_autoplay`, `timing_log_analyzer`, and `taiko_play` are compile-time skeleton binaries in Step7. Their behavioral implementation is owned by later tickets.

## 8. Step7 validation split

Rust-enabled sessions must execute the cargo commands from `TKT-0001`. Bootstrap-only validation environments may execute `scripts/check_rust_workspace_static.py` to verify the presence of the workspace, canonical crates, binaries, and Loop CLI command surface before Rust is available.


## 9. Step8 fixture validation command surface

Step8 extends `taiko_cli` with the first executable test-harness commands. These commands are part of the autonomous loop evidence surface, not full gameplay implementation.

Required commands:

```bash
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
```

`fixture validate` must read the synthetic manifest, inspect all referenced `.tja` files, and return a single JSON verdict. `fixture inspect` must return a structural report for one `.tja` file. The required fields and pass/fail rules are defined in `docs/45_fixture_validation_contract.md`.

Step8 still does not implement timing schedule calculation, branch execution, scoring, gauge, audio playback, rendering, headless autoplay, or timing log analysis.

## 10. Step9 headless autoplay command surface

Step9 extends `taiko_cli` with the first runtime execution commands. These commands are part of the autonomous loop evidence surface, not full OpenTaiko-compatible gameplay implementation.

Required commands:

```bash
taiko_cli headless autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
headless_autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
```

`headless autoplay` must load already-validated synthetic fixtures, run render-free and audio-free perfect autoplay, and return deterministic JSON with note, hit, miss, song-end, and fixture verdict fields. The required fields and pass/fail rules are defined in `docs/46_headless_autoplay_contract.md`.

Step9 still does not implement OpenTaiko-compatible timing precision, judgement windows, score, gauge, audio scheduling, render behavior, branch execution, or golden comparison. Those remain downstream tickets that must consume the headless JSON evidence surface.

## 11. Step10 timing analyzer command surface

Step10 extends `taiko_cli` with the first timing self-verification commands. These commands analyze Step9 headless autoplay evidence and return deterministic JSON metrics for QA / Regression Session.

Required commands:

```bash
taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
timing_log_analyzer --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```

`timing analyze` must emit `max_error_ms`, `mean_error_ms`, `p95_error_ms`, `threshold_ms`, `failed_count`, `analyzed_event_count`, and `failure_categories`. The required fields and pass/fail rules are defined in `docs/47_timing_log_analyzer_contract.md`.

Step10 still does not implement final OpenTaiko-compatible audio sync, judgement windows, scroll timing, or golden comparison. Those remain downstream tickets that must consume the timing analyzer JSON evidence surface.

## 12. failure feedback route command surface

The failure feedback route extends `taiko_cli` with the first executable failure-to-ticket routing commands. These commands are part of loop orchestration and must not require gameplay, audio, rendering, or manual QA interpretation.

Required commands:

```bash
taiko_cli loop failure ingest reports/failures/*.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
```

`loop failure ingest` parses failure reports that follow `templates/failure_report_template.md` and emits `verdict`, report counts, duplicate keys, missing fields, and parsed failure records.

`loop ticket propose --from-failure` emits a repair-ticket proposal with source failure, duplicate key, minimal repair scope, reproduction command, regression command, and acceptance criteria.

`loop ticket validate` verifies that a repair ticket can re-enter the autonomous loop without additional human design judgement.

The full field contract is defined in `docs/48_failure_feedback_loop_contract.md`.


## 16. loop run-once controller loop run-once controller command surface

loop run-once controller extends `taiko_cli` with the first controller command that chooses exactly one next action from current repository state. This command is orchestration evidence, not gameplay evidence.

Required commands:

```bash
taiko_cli loop run-once --mode plan --format json
taiko_cli loop run-once --mode apply --format json
scripts/loop_run_once.sh --mode plan
scripts/loop_run_once.sh --mode apply
```

`--mode plan` must have no side effects. `--mode apply` writes controller artifacts under `reports/loop/<run_id>/`:

- `controller_plan.json`
- `controller_plan.md`
- `next_codex_prompt.md`

The JSON contract includes `run_id`, `state`, `verdict`, `selected_ticket`, `next_action`, branch/worktree preview fields, required commands, open failures, missing gate evidence, and artifact paths.

The loop run-once controller supports only the initial state actions: `start_worker`, `classify_failure`, and `wait_for_ready_ticket`. Later steps add QA execution, repair materialization, auto-merge, ticket advancement, and rollback actions.


## session separation metadata output

`taiko_cli loop run-once --mode apply --format json` now writes a starter session metadata file when a ticket is selected:

```text
reports/session_metadata/<ticket-id>.toml
```

The metadata path is also emitted as `session_metadata_path` in the run-once JSON response. The file is validated by:

```bash
scripts/check_session_separation.py --metadata reports/session_metadata/<ticket-id>.toml
scripts/check_role_path_policy.py --role impl --changed-file crates/taiko_runtime/src/lib.rs
```

## 18. repair materialization and retry-budget command surface

The repair materialization and retry-budget route extends `taiko_cli` so the loop no longer stops at repair-ticket proposals.

Required commands:

```bash
taiko_cli loop failure classify --input reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket materialize --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop retry-budget check --ticket TKT-9001 --format json
```

`loop failure classify` returns `route`, `repair_kind`, `materialized_ticket_id`, and whether the source item remains `Rejected` or `Blocked`.

`loop ticket materialize --from-failure` creates the actual `.loop/tickets/<id>.md` file and is idempotent. It returns `already_exists: true` when the target ticket already exists.

`loop retry-budget check` reads `operations/retry_budget.toml` and returns whether the loop may continue or must stop and route to Control Session.

The repair materialization and retry-budget route still does not run Codex through `OPENAI_API_KEY` and does not begin Phase1 gameplay implementation.


## ChatGPT-plan Codex automation handoff surface

ChatGPT-plan Codex operation keeps AI execution on ChatGPT-plan Codex surfaces and keeps GitHub Actions deterministic. The fallback renderer is available when Rust is not installed:

```bash
scripts/render_next_codex_prompt.py --mode automation --dry-run
scripts/render_next_codex_prompt.py --mode automation
scripts/check_codex_automation_static.py
```

The renderer writes `reports/loop/<run_id>/next_codex_prompt.md` and does not require `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`.

## Phase1 gameplay worker handoff support

The Phase1 gameplay worker handoff adds a deterministic Python renderer rather than a new Rust CLI surface, because the first gameplay-ticket handoff must remain available in environments where Rust has not yet been dynamically proven.

```bash
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --force-preview --dry-run --format prompt
scripts/check_phase1_gameplay_start_static.py
```

The renderer returns `block` while Phase1 entry evidence is missing and returns `ready` only after `TKT-0060` and `GATE-0090` prerequisites are satisfied.
