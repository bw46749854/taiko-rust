# AGENTS.md - OpenTaiko Phase1 Codex Loop Operating Rules

Status: canonical
Last updated: 2026-06-26

## 1. Mission

This repository is prepared for Codex loop engineering of a Rust rhythm game with OpenTaiko-compatible normal-play coverage for Phase1.

The controlling mission is autonomous loop operation: separated AI sessions must read tickets, implement work, verify evidence, detect failure, route failure into repair tickets, and advance to the next ticket without extra human judgement. The mandatory evaluation model is `docs/05_autonomy_scorecard.md`.

Phase1 completion means that OpenTaiko-supported normal-play TJA charts can be parsed, scheduled, played through headless autoplay, judged, scored, gauged, analyzed, and regression-checked. The acceptance model is defined by:

- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/25_phase1_feature_classification.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`
- `docs/84_github_pr_loop_contract.md`
- `docs/85_rust_enabled_preflight_gate.md`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`

Commercial songs, audio files, images, videos, and copyrighted chart assets are not committed to this repository. User-selected songs are referenced by local manifest only.

## Documentation language policy

Canonical operational docs, prompts, tickets, scripts, schemas, and code comments are English. Japanese explanatory files may exist only as explicitly marked translations or non-canonical explanations, for example `*.ja.md`, and must point to the English canonical source. Machine-readable keys, command names, gate IDs, ticket IDs, crate names, and schema fields remain English. If a Japanese document is canonical today, create the English canonical version first, then mark the Japanese version as a translation or archive. `prompts/` must remain English by default. Detailed rules live in `docs/02_documentation_language_policy.md`.

## 2. Non-negotiable loop constraints

- Every ticket must include next-ticket transition evidence: which ticket or gate becomes eligible after pass/reject/block.
- Every gate must include autonomy scorecard impact and next-ticket transition rules.
- No single session may implement and approve its own work.
- Implementation work must be done in a separate Git worktree from review work.
- A ticket cannot move to Ready until its gate prerequisites are satisfied.
- A ticket cannot be accepted without machine-checkable evidence.
- Synthetic fixture results and timing analyzer output must be recorded for any ticket touching parser, scheduler, runtime, scoring, gauge, scroll, branch, audio timing, or fixture logic.
- User-selected song validation must never copy chart/audio/media data into the repository.
- Any unsupported OpenTaiko command observed in normal-play charts must be reported explicitly, not silently ignored.

- QA / Regression Session verdicts must be produced by `taiko_cli qa run`, `taiko_cli qa compare`, or `taiko_cli qa verdict`; prose-only QA conclusions are not sufficient.
- A `reject` verdict must be routed to failure feedback route before downstream gameplay tickets proceed.
- A `block` verdict must identify missing machine evidence rather than asking for ad hoc human judgement.
- PRs must use `docs/84_github_pr_loop_contract.md`; branch/worktree/PR/QA/merge/advance steps cannot be replaced by informal chat approval.
- PR cannot merge without separate review evidence, QA transition evidence, and no-user-asset confirmation.
- `TKT-0001` and `GATE-0030` cannot pass from static Rust workspace inspection alone; Rust preflight evidence is mandatory.
- Codex Cloud / CI environment changes must preserve `rust-toolchain.toml`, `scripts/codex_cloud_setup.sh`, `scripts/ci_local_equivalent.sh`, and `docs/87_secret_and_network_policy.md`.
- loop run-once controller work must preserve `docs/88_auto_merge_loop_policy.md`, `docs/89_loop_controller_state_machine.md`, `operations/loop_policy.toml`, `scripts/loop_run_once.sh`, and `scripts/check_loop_controller_static.py`.
- E2E smoke loop work must preserve `docs/94_e2e_smoke_loop_verification.md`, `operations/e2e_smoke_policy.toml`, `scripts/run_e2e_smoke_loop.sh`, and `scripts/check_e2e_smoke_static.py`. Actions must not call AI providers, `OPENAI_API_KEY`, or `openai/codex-action@v1`.

## 3. Canonical crate and binary names

Canonical crates:

| Crate | Responsibility |
|---|---|
| `taiko_domain` | Domain types, note events, branch structures, score/gauge state, compatibility report types |
| `taiko_chart` | TJA parser, metadata parser, course selector, command parser |
| `taiko_timing` | BPM/MEASURE/DELAY/OFFSET timeline and arbitrary subdivision scheduler |
| `taiko_runtime` | Headless gameplay runtime, judgement, branch evaluation, score/gauge update |
| `taiko_audio` | Audio metadata abstraction, WAVE/PATH_WAV/OFFSET validation hooks |
| `taiko_render` | Optional visual-state projection used by smoke tests; no full UI requirement in Phase1 |
| `taiko_test_support` | Fixture loader, golden comparison, synthetic/user-song validation helpers |
| `taiko_cli` | Unified command entrypoint |

Canonical binaries:

| Binary | Responsibility |
|---|---|
| `taiko_cli` | Unified command interface |
| `taiko_play` | Minimal playable binary / smoke entrypoint |
| `headless_autoplay` | Headless autoplay execution for fixture and user-song validation |
| `timing_log_analyzer` | Analyzer for timing log, branch route, scroll anomaly, score/gauge, compatibility report |

Deprecated names in older docs and tickets must be treated as invalid: `taiko_core`, ad hoc analyzer names, and unqualified `check all` without `taiko_cli` context.

## 4. Session topology

| Session | Worktree | Responsibility | May approve implementation? |
|---|---|---|---|
| Control Session | `worktrees/control` | Select next ticket, check gates, collect evidence, produce loop summary | No |
| Spec Extraction Session | `worktrees/spec` | Extract OpenTaiko behavior, update research docs and adoption decisions | No |
| Design Review Session | `worktrees/review` | Review plans, architecture, specs, coverage, and implementation diffs | Yes, only review output |
| Test Infra Session | `worktrees/test-infra` | Maintain fixtures, harness, analyzer, CI command contract | No self-approval |
| Ticket Implementation Session | `worktrees/impl/<ticket-id>` | Implement one ticket only | No |
| QA / Regression Session | `worktrees/qa` | Run synthetic and user-selected validation, produce regression report | Yes, only QA output |

## 5. Required document read set by task type

### Any ticket

Read these before writing a plan:

- `AGENTS.md`
- `docs/00_project_objective.md`
- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `.loop/tickets/<ticket-id>.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/25_phase1_feature_classification.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`
- `docs/84_github_pr_loop_contract.md`
- `docs/85_rust_enabled_preflight_gate.md`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`

### Parser / command ticket

Also read:

- `research/opentaiko/02_tja_parser_commands.md`
- `research/opentaiko/09_course_audio_song_selection.md`
- `docs/32_data_model.md`
- `docs/34_error_handling_and_logging.md`

### Timing / scroll ticket

Also read:

- `research/opentaiko/04_timing_and_measure_model.md`
- `research/opentaiko/07_scroll_and_visual_timing.md`
- `docs/40_timing_model.md`
- `docs/43_timing_log_schema.md`
- `docs/44_timing_log_analyzer_spec.md`

### Branch / score / gauge ticket

Also read:

- `research/opentaiko/06_branching_model.md`
- `research/opentaiko/08_score_gauge_clear_model.md`
- `docs/42_judgement_model.md`

### Fixture / QA ticket

Also read:

- `docs/50_test_harness_overview.md`
- `docs/51_fixture_design.md`
- `docs/45_fixture_validation_contract.md`
- `docs/coverage/phase1_feature_coverage_matrix.md`
- `docs/coverage/phase1_fixture_to_feature_traceability.md`
- `docs/coverage/phase1_user_song_category_matrix.md`

## 6. Gate policy

Gate files are authoritative:

- `.loop/gates/GATE-0000-spec-repair.md`
- `.loop/gates/GATE-0010-coverage-ready.md`
- `.loop/gates/GATE-0020-implementation-ready.md`
- `.loop/gates/GATE-0030-loop-cli-ready.md`

Current initial state:

- `OPS-0001` is Ready for the operations migration rail.
- `TKT-0000` and all implementation tickets are Blocked until the operations migration rail and required gates pass.
- Fixture-heavy implementation tickets remain Blocked until `GATE-0010` is passed.
- Broad runtime implementation remains Blocked until `GATE-0020` is passed.

## 7. Evidence requirements

Every completed ticket must include:

- Plan file or plan section.
- Plan review result from a separate session.
- Code or documentation diff summary.
- Commands run.
- Synthetic fixture result summary where relevant.
- Timing log analyzer result where relevant.
- Compatibility report deltas.
- Review result from a separate session.
- Remaining risk list.

## 8. Commit discipline

- One ticket per branch.
- One implementation worktree per ticket.
- No drive-by refactors outside ticket scope.
- No fixture golden update without `docs/52_golden_update_policy.md` compliance.
- No introduction of local copyrighted assets.

## 9. Failure handling

A failed ticket must be returned to Blocked or In Review with a concrete failure reason. Do not mark partial implementation as Done.

Failure classes:

- Spec ambiguity
- OpenTaiko evidence gap
- Coverage gap
- Parser crash
- Scheduler mismatch
- Timing anomaly
- Branch route mismatch
- Score/gauge mismatch
- Audio offset anomaly
- User-song manifest violation
- CI/tooling failure


## 10. Autonomy scoring rule

All work is evaluated by the scorecard in `docs/05_autonomy_scorecard.md`. A ticket may claim improvement only when another session can verify the evidence.

Required axes:

| Axis ID | Axis | Weight |
|---|---|---:|
| A1 | Session / worktree governance | 10 |
| A2 | Ticket / gate machine-readability | 15 |
| A3 | Buildable Rust substrate | 15 |
| A4 | Executable test harness | 15 |
| A5 | Timing / audio self-verification | 20 |
| A6 | Regression / CI enforcement | 15 |
| A7 | Failure feedback loop | 10 |

A completed ticket must state its axis deltas, evidence, and next-ticket consequence.



## Loop CLI command surface

The repository contains the canonical Rust workspace skeleton and `taiko_cli` Loop CLI MVP. The canonical crates are `taiko_domain`, `taiko_chart`, `taiko_timing`, `taiko_runtime`, `taiko_audio`, `taiko_render`, `taiko_test_support`, and `taiko_cli`.

The first Rust implementation goal is not gameplay. It is machine-readable loop orchestration. `taiko_cli loop inspect`, `taiko_cli loop next`, `taiko_cli loop gate --dry-run`, and `taiko_cli loop report status` exist to let Control, Ticket Implementation, Design Review, and QA Sessions move tickets without extra human design judgement.

`taiko_play` remains a compile-time skeleton. `headless_autoplay` provides the headless autoplay evidence surface, and `timing_log_analyzer` is a JSON evidence alias over `taiko_cli timing analyze`.

`loop run-once` is the canonical controller preview command:

```bash
taiko_cli loop run-once --mode plan --format json
taiko_cli loop run-once --mode apply --format json
scripts/loop_run_once.sh --mode plan
scripts/loop_run_once.sh --mode apply
```

The controller emits exactly one next action: `start_worker`, `classify_failure`, or `wait_for_ready_ticket`. `--mode apply` writes only controller artifacts under `reports/loop/<run_id>/`; it must not mark gameplay tickets Done, pass gates, or merge branches.

The loop run-once controller does not require `OPENAI_API_KEY` or `CODEX_API_KEY`. GitHub Actions may run deterministic validation and future auto-merge logic, but AI implementation remains on the ChatGPT-plan Codex Cloud / Codex App / CLI / Automations surface.

## Fixture validation evidence

Parser, fixture, and QA tickets must use the fixture validation command surface when fixture readability is relevant:

```bash
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
```

Passing these commands proves only committed fixture readability and basic TJA structure. It does not prove Phase1 timing, judgement, branch, score, gauge, audio, render, or autoplay behavior.

## Headless autoplay evidence

Headless autoplay evidence is part of the autonomous-loop evidence surface. Ticket Implementation Session must not rely on screenshots, audible playback, or subjective rhythm feel to pass `TKT-0003`. QA / Regression Session must use the JSON contract in `docs/46_headless_autoplay_contract.md` and the gate rules in `.loop/gates/GATE-0050-headless-autoplay-ready.md`.

The current MVP is intentionally limited to render-free, audio-free `perfect` mode. It is a runtime evidence path for later timing analyzer work, not a certification of OpenTaiko-compatible timing precision.

## Timing analyzer evidence

The `timing_log_analyzer` binary is an alias for `taiko_cli timing analyze` and must produce the JSON contract defined in `docs/47_timing_log_analyzer_contract.md`.

The current timing analysis is an MVP over perfect-autoplay evidence. Passing timing analysis proves that timing evidence has a machine-readable pass/reject surface with `max_error_ms`, `mean_error_ms`, `p95_error_ms`, `threshold_ms`, and failure categories. It does not prove final OpenTaiko-compatible audio latency, visual scroll timing, or judgement-window precision.

Any ticket touching parser timing, scheduler, scroll, judgement, runtime ticks, or audio sync must preserve the analyzer contract and add stronger evidence rather than replacing it with manual inspection.

## QA verdict route

The QA / Regression Session must prefer the following machine-readable commands over prose judgement:

```bash
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa compare --baseline reports/baseline --current reports/current --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

`pass` advances to the next eligible ticket, `reject` routes to failure feedback and repair-ticket proposal, and `block` requires missing evidence to be produced before implementation continues.

## Failure feedback and repair route

The failure feedback loop is part of the executable autonomous-loop substrate. `taiko_cli` must expose:

```bash
taiko_cli loop failure ingest reports/failures/*.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
```

No gameplay feature ticket may use manual QA judgement as the only repair route after `GATE-0060`. Phase1 feature work beginning with `TKT-0005` remains Blocked until `TKT-0040` is Done and `GATE-0070` passes.

Failure reports must be classified before downstream work continues. Use `taiko_cli loop failure classify --input <failure-report> --format json` to decide `reject` versus `block`.

Use `taiko_cli loop ticket materialize --from-failure <failure-report> --format json` to create the actual repair or blocker ticket. Do not continue from proposal text alone.

Use `taiko_cli loop retry-budget check --ticket <ticket-id> --format json` before repeated repair attempts. A `block` retry-budget verdict stops the loop and routes to Control Session.

The repair materialization and retry-budget route does not require API-key based Codex execution. AI work remains on Codex Cloud/App/CLI/Automations under the ChatGPT plan, while GitHub Actions handles gate checks and transitions.

## Rust preflight and CI evidence

Rust preflight is mandatory for the first dynamic acceptance of the Rust workspace and `taiko_cli` command surface. Use:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
```

`TKT-0001` may not become Done and `GATE-0030` may not pass without valid `reports/preflight/latest/rust_preflight_report.json` evidence. A `block` verdict repairs the Rust-enabled Codex Cloud or CI environment. A `reject` verdict routes to failure feedback and a repair ticket. Static scripts are fallback evidence only in environments where Rust cannot be executed; they are not acceptance evidence for the Rust substrate.

Codex Cloud / CI environment setup is a governed loop surface. Use:

```bash
scripts/codex_cloud_setup.sh
scripts/ci_local_equivalent.sh --static-only
scripts/ci_local_equivalent.sh --out reports/preflight/latest
```

`rust-toolchain.toml` is the canonical Rust version contract. Do not rely on floating `stable` as ticket acceptance evidence. Codex Cloud agent internet access remains off by default; setup-script internet is only for installing the pinned Rust toolchain and dependencies. No implementation ticket may introduce job-level `OPENAI_API_KEY` or `CODEX_API_KEY` in workflows that check out or run repository-controlled code.

ChatGPT-plan Codex operation uses ChatGPT-plan Codex surfaces. Codex Cloud, Codex App Automations, or Codex CLI signed in with ChatGPT are the AI execution surfaces. GitHub Actions must not invoke `openai/codex-action@v1`, must not require `OPENAI_API_KEY` or `CODEX_API_KEY`, and must remain deterministic. Use `prompts/70_codex_automation_loop_runner.md`, `prompts/71_codex_cloud_ticket_worker.md`, and `scripts/render_next_codex_prompt.py` for automation handoff.

## GitHub PR / auto-merge / ticket advancement

GitHub is the durable loop-control surface for ticket branches, PRs, CI status, Codex review, QA verdict application, merge, and next-ticket transition. Use:

```bash
scripts/loop_create_worktree.sh <ticket-id>
scripts/loop_open_pr.sh <ticket-id>
scripts/loop_apply_qa_verdict.py --ticket <ticket-id> --verdict <path>
scripts/loop_merge_and_advance.sh <ticket-id> --pr <number> --verdict <path>
```

PR cannot merge when implementation, review, and QA are not separated, when no machine-readable QA verdict exists for implementation/runtime changes, or when user-selected assets are committed. Native `@codex review`, automatic Codex review, or `.github/workflows/codex-review.yml` supplies the detached design/diff review surface; it does not replace QA / Regression Session evidence.

Session separation is a machine-readable gate. Any PR that advances a ticket must provide `reports/session_metadata/<ticket-id>.toml`. Implementation, Review, and QA session IDs must be distinct. Implementation Sessions must not write QA verdict files. QA Sessions must not modify `crates/`. Use role-specific worktrees through `scripts/loop_create_worktree.sh <ticket-id> --role <role>`.

GitHub Actions auto-merge controller is the only automated merge surface for the autonomous loop. Actions must not call AI providers, must not require `OPENAI_API_KEY`, and must not use `openai/codex-action@v1`.

The controller may merge only when `scripts/check_auto_merge_conditions.py` passes with ticket metadata, QA verdict, session separation, role path policy, no-user-asset validation, retry budget, and required gate evidence. QA `reject` and QA `block` are never mergeable.

Autonomous merge records belong in `reports/loop/merge_history/<run_id>.json`. Regression evidence belongs in `reports/regression/<run_id>.json` and is handled through a revert PR, not by direct force-push or manual history rewrite.

The E2E smoke loop verifies the autonomous controller substrate. The smoke loop must cover pass, reject, block, retry, and revert routes in dry-run mode before Phase1 gameplay tickets begin. Actions must not call AI providers; Codex Cloud/App/CLI remains the worker surface, and GitHub Actions remains the gate, merge, advance, and smoke-verification surface.

## Phase1 gameplay worker handoff

The first Phase1 gameplay feature ticket is `TKT-0005`. It must not be selected until `TKT-0060` is Done and `GATE-0090` has passed.

Control Session must use `operations/phase1_feature_ticket_manifest.toml` plus `taiko_cli phase1 feature plan --format json` to identify the next gameplay feature ticket. Manual ordering from prose is not allowed.

Every Phase1 gameplay feature ticket must include QA run evidence, QA verdict evidence, failure-route evidence, and next-ticket transition evidence. A QA `reject` must be routed through failure feedback route before downstream tickets proceed.

The Phase1 gameplay worker handoff opens the Phase1 gameplay lane through a deterministic start packet. Use:

```bash
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --force-preview --dry-run --format prompt
scripts/check_phase1_gameplay_start_static.py
```

`TKT-0005` is the first gameplay ticket. Do not start implementation unless the rendered start packet says `verdict = ready`. In the current post-OPS state, the start packet remains `block` until `TKT-0060`, `GATE-0090`, and the required entry evidence are complete.

Implementation sessions must not write QA verdict files, mark tickets Done, pass gates, or use `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`. Codex Cloud/App/CLI remains the worker surface under the ChatGPT plan; GitHub Actions remains deterministic.


## Operations migration rail

- Start with `OPS-0001` only.
- Keep `TKT-0000`, `TKT-0001`, and all Phase1 gameplay tickets Blocked during the operations migration.
- Use GitHub Actions as verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator.
- Do not introduce `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1` as a requirement for GitHub Actions gate execution.
- The first gameplay entry remains `TKT-0005`, and it can be evaluated only after `OPS-0009` and `GATE-OPS-0000` pass.


## OPS-0003 public repository hardening note

Public repository hardening is active. Do not add `OPENAI_API_KEY`, `CODEX_API_KEY`, `openai/codex-action@v1`, `pull_request_target`, committed assets, private Drive links, `.env` files, OAuth credentials, or service-account JSON. GitHub Actions remains a verifier/gate/controller and not an AI worker. Run `scripts/check_public_repository_static.py` with the standard static checks.

## OPS-0004 asset bundle rule

Use `operations/dev_asset_bundle.example.toml` as the canonical development asset manifest shape. Do not commit songs, charts, skins, Drive signed URLs, OAuth tokens, service account JSON, or private local paths. Development assets are supplied as a Google Drive zip with sha256 verification and extracted to `.external_assets/opentaiko/`. Runtime code must accept `OPENTAIKO_CONTENT_ROOT` and `--content-root`; production mode reads the same OpenTaiko-compatible layout directly from the user-provided content root.


## OPS-0005 GitHub Actions gate normalization

GitHub Actions gate normalization is active. Keep Actions as verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator only. Do not add Codex/GPT worker execution, `OPENAI_API_KEY`, `CODEX_API_KEY`, `openai/codex-action@v1`, or `pull_request_target`.

Required PR check contexts are `loop-pr-gate / loop-pr-gate`, `rust-preflight / rust-preflight`, `phase1-loop / phase1-loop`, and `phase1-gameplay-entry / phase1-gameplay-entry`. `loop-controller.yml` must keep `concurrency: loop-controller-main`, must proceed from `workflow_run` only when `github.event.workflow_run.conclusion == 'success'`, and must not checkout untrusted PR head code in privileged context. Run `scripts/check_github_actions_gate_static.py` with the standard static checks.


## OPS-0006 Auto-merge candidate discovery

Auto-merge candidate discovery is active. Keep no gameplay Ready ticket until the Phase1 entry prerequisite chain passes; after that, keep exactly one Ready ticket: `TKT-0005`. Use `scripts/select_auto_merge_candidate.py` to classify `loop:automerge` PRs from GitHub PR metadata. The controller must not checkout untrusted PR head code and must not call AI providers. Candidate reports are written under `reports/loop/candidates/`; the canonical schema is `schemas/auto_merge_candidate_schema.md`. Run `scripts/check_auto_merge_conditions.py` with the standard static checks.

## OPS-0007 Ticket advance engine

Ticket advance is active. Keep no gameplay Ready ticket until the Phase1 entry prerequisite chain passes; after that, keep exactly one Ready ticket: `TKT-0005`. The merge controller must use `scripts/loop_advance_ticket.py` after merge history exists, write `reports/loop/ticket_transitions/<run_id>.json`, and preserve the OPS migration guard that prevents `TKT-*` gameplay tickets from becoming Ready before `OPS-0009` and `GATE-OPS-0000` pass.

Actions must not call AI providers. GitHub Actions remains the verifier/gate/controller and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.


## OPS-0008 Next Codex worker handoff

Actions must not call AI providers. During `OPS-0008`, GitHub Actions emits deterministic worker handoff artifacts only through `scripts/loop_emit_worker_handoff.py`. The next worker reads `reports/loop/worker_handoff/latest.md`, works on the selected ticket only, and must not self-approve, mark tickets Done, pass gates, or author QA verdict files.


## OPS-0009 final migration state

`OPS-0009` is complete, but `TKT-0005` remains Blocked until `TKT-0060` is Done and `GATE-0090` passes. Actions must not call AI providers. They may verify, gate, merge, advance tickets, and emit handoff artifacts. Use `scripts/check_ops_migration_readiness.py`, `scripts/check_e2e_smoke_static.py --static-only`, and `scripts/check_phase1_gameplay_start_static.py` before starting the Phase1 gameplay worker.
