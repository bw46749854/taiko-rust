# OpenTaiko Phase1 Codex Loop Bootstrap Package

Status: canonical
Last updated: 2026-06-26

## Purpose

This package prepares a Codex loop engineering workflow for implementing Phase1 of an OpenTaiko-compatible Rust rhythm game.

The controlling objective is autonomous loop operation: separated AI sessions must be able to read tickets, implement work, verify results, detect failures, route failures back into repair tickets, and advance to the next ticket without extra human judgement. See `docs/00_project_objective.md` and `docs/05_autonomy_scorecard.md`.

Phase1 means normal-play completion for OpenTaiko-supported TJA charts, including the gameplay features classified in `docs/25_phase1_feature_classification.md` and the adoption decisions in `research/opentaiko/10_phase1_adoption_decisions.md`.

## Completed preparation steps

| Step | Result |
|---|---|
| Step1 | Compatibility Contract and Phase1 scope repaired |
| Step2 | OpenTaiko research findings and adoption decisions added |
| Step3 | Coverage matrices, synthetic fixtures, user-song validation docs added |
| Step4 | AGENTS, gates, ticket backlog, prompts, loop execution docs added |
| Step5 | Bootstrap repair: TKT-0000 executable checks, fixture manifest, reference validation, missing templates |
| Step6 | Autonomy scorecard: project objective, maturity model, gate transition rules, failure feedback protocol, Loop CLI contract |
| Step7 | Rust workspace skeleton and Loop CLI MVP added |
| Step8 | Fixture Validation MVP added: manifest and TJA structural inspection through `taiko_cli fixture` |
| Step9 | Headless Autoplay MVP added: render-free/audio-free perfect autoplay evidence |
| Step10 | Timing Analyzer MVP added: max/mean/p95 error and failure-category JSON evidence |
| Step11 | Failure Feedback Loop MVP added: failure ingest, repair-ticket proposal, and ticket validation JSON |
| Step12 | QA / Regression Gate MVP added: machine-readable pass/reject/block verdicts |
| Step13 | Phase1 feature-loop entry manifest and planner added |
| Step14 | GitHub PR Loop Orchestration added: branch/worktree/PR/review/QA verdict/merge/advance scripts |
| Step15 | Rust-enabled Preflight Gate added: cargo / `taiko_cli` runtime evidence JSON, CI artifact upload, and evidence validation |
| Step16 | Codex Cloud environment and CI hardening added: pinned Rust toolchain, setup script, local CI equivalent, secret/network policy, and static environment validation |
| Step17 | Loop run-once controller foundation added: auto-merge policy, state machine, controller plan/apply command, and next Codex prompt artifact generation |
| Step18 | Session metadata and path policy gate added: role worktrees, machine-readable metadata, and PR gate checks |
| Step19 | Repair materialization and retry budget added: failure classification, actual repair/blocker ticket creation, and retry-loop stop conditions |
| Step20 | Plus-plan Codex Automation operation added: no-API-key heartbeat prompts and detached review request workflow |
| Step21 | GitHub Actions auto-merge controller added: guarded squash merge, merge history, and revert evidence workflow |
| Step22 | E2E smoke loop verification added: pass/reject/block/retry/revert dry-run evidence and CI smoke workflow |
| Step23 | Phase1 gameplay loop start added: first gameplay ticket start packet renderer and `TKT-0005` worker handoff prompt |


## Operations migration rail

The current package is in the operations migration before Phase1 gameplay implementation starts. The only Ready ticket is `TKT-0005`. The `OPS-0001` ... `OPS-0009` rail performs cleanup canonicalization, public repository hardening, deterministic asset-bundle policy, GitHub Actions gate normalization, auto-merge candidate discovery, ticket advancement, Codex handoff materialization, and final E2E smoke verification. GitHub Actions remains a verifier/gate/controller and does not run AI worker code or require OpenAI API keys.

## Start here

1. Read `AGENTS.md`.
2. Read `docs/00_project_objective.md`.
3. Read `docs/05_autonomy_scorecard.md`.
4. Read `docs/73_first_execution_batch.md`.
5. Read `docs/86_codex_cloud_environment_setup.md` and `docs/87_secret_and_network_policy.md`.
6. Read `docs/88_auto_merge_loop_policy.md`, `docs/89_loop_controller_state_machine.md`, `docs/90_session_metadata_and_path_policy.md`, `docs/91_repair_materialization_and_retry_budget.md`, `docs/92_codex_plus_automation_operation.md`, `docs/93_github_actions_auto_merge_controller.md`, `docs/94_e2e_smoke_loop_verification.md`, and `docs/95_phase1_gameplay_loop_start.md`.
7. Start `TKT-0005` as the first Phase1 gameplay ticket after OPS migration.
8. Run `GATE-OPS-0000` according to `.loop/gates/GATE-OPS-0000-migration-ready.md` after OPS-0009 completes.
9. Keep `TKT-0000`, `TKT-0001`, and Phase1 gameplay tickets Blocked until the operations migration rail completes.

## Initial ticket state

| Ticket | Status |
|---|---:|
| `OPS-0001` | Done |
| `OPS-0002` | Done |
| `OPS-0003` | Done |
| `OPS-0004` | Done |
| `OPS-0005` | Done |
| `OPS-0006` | Done |
| `OPS-0007` | Done |
| `OPS-0008` | Done |
| `OPS-0009` | Done |
| `TKT-0000` and all implementation tickets | Blocked |

## Public repository hardening

`OPS-0003` adds the public-readiness floor: `LICENSE`, `NOTICE.md`, `THIRD_PARTY_NOTICES.md`, `SECURITY.md`, `docs/97_public_repository_hardening.md`, `operations/public_repository_policy.toml`, `.github/dependabot.yml`, and `scripts/check_public_repository_static.py`. GitHub Actions remains a verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator. It does not run Codex or GPT workers and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.

## Asset policy

This package does not include commercial song, audio, chart, image, video, or skin assets. User-selected song validation uses the OPS-0004 content-root contract. Development assets are provided by a Google Drive zip manifest, verified by sha256, and extracted to `.external_assets/opentaiko/`. Production reads the same OpenTaiko-compatible layout from `OPENTAIKO_CONTENT_ROOT` or `--content-root`.

## Canonical implementation names

- Domain crate: `taiko_domain`
- Unified CLI crate: `taiko_cli`
- Binaries: `taiko_cli`, `taiko_play`, `headless_autoplay`, `timing_log_analyzer`

## Final bootstrap prompt

Use `prompts/60_final_bootstrap_prompt.md` to start the Control Session.


## Autonomy scorecard

The package is evaluated against autonomous loop operational readiness, not document volume. The score axes are defined in `docs/05_autonomy_scorecard.md`:

- A1 Session / worktree governance
- A2 Ticket / gate machine-readability
- A3 Buildable Rust substrate
- A4 Executable test harness
- A5 Timing / audio self-verification
- A6 Regression / CI enforcement
- A7 Failure feedback loop

Step6 improves A2, A6, and A7 by making gate transitions, failure routing, and future Loop CLI behavior explicit.


## Step7 Loop CLI MVP

This package includes the first executable substrate for the autonomous loop:

```bash
scripts/check_rust_workspace_static.py
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
taiko_cli loop inspect tickets --format json
taiko_cli loop inspect gates --format json
taiko_cli loop next --format json
taiko_cli loop gate GATE-0000 --dry-run --format json
taiko_cli loop report status --format json
```

`cargo` commands require a Rust-enabled environment. `scripts/check_rust_workspace_static.py` is the bootstrap fallback for environments that can inspect files but cannot run Rust.


## Step8 Fixture Validation MVP

This package includes the first executable test-harness layer for synthetic fixtures:

```bash
scripts/check_fixture_validation_static.py
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
```

The contract is `docs/45_fixture_validation_contract.md`. These commands validate fixture presence and basic TJA structure. They do not prove timing, branch execution, score/gauge behavior, audio sync, rendering, or headless autoplay.

## Step9 addition: Headless Autoplay MVP

Step9 adds the first render-free and audio-free runtime execution path:

```bash
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
taiko_cli headless autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json
headless_autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
```

The output is deterministic JSON for QA / Regression Session. It proves that committed synthetic fixtures can be executed in perfect-autoplay mode and that pass/reject can be decided without visual inspection, audio playback, or manual chart inspection. Full timing precision and timing-log analysis remain later gates.

## Step10 addition: Timing Analyzer MVP

Step10 adds the first machine-readable timing self-verification layer over Step9 headless autoplay evidence:

```bash
taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
timing_log_analyzer --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```

The contract is `docs/47_timing_log_analyzer_contract.md`. The Step10 MVP reports deterministic `max_error_ms`, `mean_error_ms`, `p95_error_ms`, threshold, and failure-category evidence from perfect-autoplay results. It does not yet certify final OpenTaiko-compatible audio sync, visual scroll timing, or judgement-window precision.

## Step11 addition: Failure Feedback Loop MVP

Step11 adds the first executable self-repair route for the autonomous loop:

```bash
taiko_cli loop failure ingest reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
```

The contract is `docs/48_failure_feedback_loop_contract.md`. Step11 does not implement automatic branch creation, PR creation, or CI mutation. It makes failure ingestion, duplicate prevention, repair-ticket proposal, and repair-ticket validation machine-readable so Control Session and QA / Regression Session can route rejects without additional human design judgement.


## Step12 QA / Regression Gate MVP

Step12 adds the first machine-readable QA verdict layer. The package now defines and statically checks:

```bash
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa compare --baseline reports/baseline --current reports/current --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

The goal is to let the QA / Regression Session return `pass`, `reject`, or `block` without manual log interpretation. `reject` must route to Step11 failure feedback. `block` must name missing machine evidence.

## Step13 phase1 feature-loop entry

Step13 adds the Phase1 gameplay feature-loop entry layer. The package now treats `operations/phase1_feature_ticket_manifest.toml` as the machine-readable source for gameplay ticket order, command evidence, QA evidence, and failure routing.

Gameplay tickets beginning with `TKT-0005` must remain Blocked until `TKT-0060` is Done and `GATE-0090` has passed. This prevents Control Session from starting Phase1 feature implementation by prose interpretation.

Required Step13 checks:

```bash
scripts/check_phase1_feature_loop_static.py
taiko_cli phase1 feature validate --manifest operations/phase1_feature_ticket_manifest.toml --format json
taiko_cli phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json
```


## Step14 GitHub PR Loop Orchestration

Step14 adds the missing durable GitHub transition layer around the existing loop contracts:

```bash
scripts/loop_create_branch.sh TKT-0000 --dry-run
scripts/loop_create_worktree.sh TKT-0000 --dry-run
scripts/loop_open_pr.sh TKT-0000 --branch loop/TKT-0000-spec-repair-gate-and-bootstrap-consistency-check --dry-run
scripts/loop_apply_qa_verdict.py --ticket TKT-0000 --verdict reports/qa/TKT-0000.verdict.json
scripts/loop_merge_and_advance.sh TKT-0000 --pr 1 --verdict reports/qa/TKT-0000.verdict.json --dry-run
scripts/check_github_pr_orchestration_static.py
```

The contract is `docs/84_github_pr_loop_contract.md`. The execution-surface decision is `docs/83_codex_surface_decision.md`. Step14 does not replace Rust/QA evidence; it makes PR creation, review, QA verdict application, merge, and next-ticket selection deterministic.

## Step15 Rust-enabled Preflight Gate

Step15 adds the first dynamic verification gate that must run in a Rust-enabled environment:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
scripts/check_rust_preflight_static.py
```

The contract is `docs/85_rust_enabled_preflight_gate.md`. The generated evidence path is `reports/preflight/latest/`, uploaded by `.github/workflows/rust-preflight.yml` as the `rust-preflight-report` artifact. This gate converts the first cargo / `taiko_cli` execution into a `pass`, `reject`, or `block` verdict so `TKT-0001` and `GATE-0030` cannot be accepted from static inspection alone.


## Step17 addition: Loop run-once controller foundation

Step17 adds the first controller command that turns repository state into one machine-readable next action:

```bash
taiko_cli loop run-once --mode plan --format json
taiko_cli loop run-once --mode apply --format json
scripts/loop_run_once.sh --mode plan
scripts/loop_run_once.sh --mode apply
```

`--mode plan` is side-effect free. `--mode apply` writes controller artifacts under `reports/loop/<run_id>/`, including `controller_plan.json`, `controller_plan.md`, and `next_codex_prompt.md`. Step17 does not require `OPENAI_API_KEY` or any API-metered Codex worker. Codex Cloud, Codex App, CLI, or Automations may consume the generated prompt using the ChatGPT plan surface.

Auto-merge is now the target policy for this repository, but Step17 does not enable automatic merge. It only establishes the state-machine and controller evidence surface required by later metadata, repair, and merge-controller steps.


## Step18: session metadata and path policy

Step18 adds machine-readable session separation and role path policy. The new static checks are:

```bash
scripts/check_session_separation.py
scripts/check_role_path_policy.py
scripts/loop_create_worktree.sh TKT-0050 --role test-infra --dry-run
```

`taiko_cli loop run-once --mode apply` writes `reports/session_metadata/<ticket-id>.toml` alongside controller artifacts.


## Step19 addition: Repair Materialization and Retry Budget

Step19 closes the gap between failure reports and executable repair work. `loop ticket propose` remains a preview command, while `loop ticket materialize --from-failure` creates a real Ready ticket under `.loop/tickets/`.

```bash
taiko_cli loop failure classify --input reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket materialize --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop retry-budget check --ticket TKT-9001 --format json
```

Step19 distinguishes `reject` from `block`. Rejects become repair tickets. Blocks become ENV/SPEC/TOOL blocker tickets. Retry limits live in `operations/retry_budget.toml`.

This step still does not require `OPENAI_API_KEY` or `CODEX_API_KEY`, and it does not start Phase1 gameplay implementation.


## Step20 Plus-plan Codex Automation

Step20 keeps normal operation inside the ChatGPT-plan Codex surface. GitHub Actions do not call `openai/codex-action@v1`, do not require `OPENAI_API_KEY`, and do not run metered AI workers. Codex Cloud, Codex App Automations, or Codex CLI signed in with ChatGPT read `prompts/70_codex_automation_loop_runner.md` and the generated `reports/loop/<run_id>/next_codex_prompt.md`.

Useful commands:

```bash
scripts/check_codex_automation_static.py
scripts/render_next_codex_prompt.py --mode automation --dry-run
scripts/render_next_codex_prompt.py --mode automation
```

Step20 still does not enable auto-merge and does not start Phase1 gameplay implementation.


## Step21 Auto-Merge Controller

Step21 adds the GitHub Actions auto-merge controller. GitHub Actions remains a mechanical gate/merge/advance surface; it does not call AI providers and does not require `OPENAI_API_KEY`.

Primary files:

- `docs/93_github_actions_auto_merge_controller.md`
- `operations/auto_merge_policy.toml`
- `.github/workflows/loop-controller.yml`
- `scripts/check_auto_merge_conditions.py`
- `scripts/loop_controller_github.sh`
- `scripts/loop_auto_merge_pr.sh`
- `scripts/loop_revert_last_merge.sh`
- `reports/loop/merge_history/README.md`
- `reports/regression/README.md`

Representative commands:

```bash
scripts/check_auto_merge_conditions.py
scripts/loop_controller_github.sh --mode plan
scripts/loop_auto_merge_pr.sh --ticket TKT-0005 --pr 12 --metadata reports/session_metadata/TKT-0005.toml --qa reports/qa/TKT-0005.verdict.json --dry-run
scripts/loop_revert_last_merge.sh --run-id RUN-20260626-0001 --reason regression --dry-run
```

Step21 does not implement gameplay features. It prepares automatic squash merge, merge history, and revert evidence for PRs that already passed the loop gates.


## Step22 E2E smoke loop verification

Step22 adds a no-AI, no-API-key smoke verification layer for the controller substrate:

```bash
scripts/check_e2e_smoke_static.py
scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
```

The smoke loop exercises pass, reject, block, retry-budget, and revert routes without committing smoke-only Ready tickets and without starting Phase1 gameplay implementation. Evidence is generated under `reports/e2e_smoke/<run_id>/` or a caller-provided `--out` directory.


## Step23 Phase1 gameplay loop start

Step23 opens the Phase1 gameplay implementation lane through a machine-readable start packet. It does not mark `TKT-0005` Ready in the bootstrap package and does not implement gameplay features.

Use:

```bash
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --force-preview --dry-run --format prompt
scripts/check_phase1_gameplay_start_static.py
```

The default renderer returns `ready` after `TKT-0060`, `GATE-0090`, and `GATE-OPS-0000` entry evidence exists. After entry evidence exists, the same command renders the worker handoff for the first gameplay ticket, `TKT-0005`.


## OPS-0005 GitHub Actions gate normalization

OPS-0005 normalizes GitHub Actions as the deterministic verifier/gate/controller surface. It does not introduce Codex or GPT execution inside Actions and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.

The normalized required check contexts are:

- `loop-pr-gate / loop-pr-gate`
- `rust-preflight / rust-preflight`
- `phase1-loop / phase1-loop`
- `phase1-gameplay-entry / phase1-gameplay-entry`

`loop-controller.yml` uses `concurrency: loop-controller-main`, requires `workflow_run` success before controller work, and must not checkout untrusted PR head code from privileged workflow context. Static validation is `scripts/check_github_actions_gate_static.py`.


## OPS-0006 Auto-merge candidate discovery

OPS-0006 teaches `loop-controller` to discover merge candidates without a human-provided PR number. The controller reads GitHub PR metadata through `gh pr list`, filters `loop:automerge` labeled PRs, checks base branch, PR head SHA, ticket id, session metadata path, QA verdict path, and exact required check contexts, then writes `reports/loop/candidates/candidate_plan.json`.

The deterministic selector is `scripts/select_auto_merge_candidate.py`. It is fixture-tested with pass, reject, and block cases under `fixtures/loop_controller/`. GitHub Actions remains a verifier/gate/controller and does not call Codex/GPT workers.

## OPS-0007 Ticket advance engine

OPS-0007 adds the ticket advance engine. After `scripts/loop_auto_merge_pr.sh` writes `reports/loop/merge_history/<run_id>.json`, `scripts/loop_advance_ticket.py` reads that merge history and writes `reports/loop/ticket_transitions/<run_id>.json` plus a Markdown report. The controller marks the merged ticket `Done`, promotes exactly one dependency-satisfied next ticket to `Ready`, and keeps all `TKT-*` gameplay tickets blocked while the OPS migration rail is active.

GitHub Actions remains a verifier/gate/controller. Actions must not call AI providers and must not require `OPENAI_API_KEY` or `CODEX_API_KEY`.


## OPS-0008 worker handoff

`OPS-0008` adds the worker handoff layer. GitHub Actions remains a verifier/gate/controller and emits deterministic handoff artifacts with `scripts/loop_emit_worker_handoff.py`; it does not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`. The canonical outputs are `reports/loop/worker_handoff/latest.json`, `latest.md`, `latest_issue.md`, and `latest_comment.md`.


## OPS-0009 final migration state

`OPS-0009` completes the operations migration. The repository now keeps exactly one Ready ticket: `TKT-0005`. GitHub Actions remains a verifier/gate/controller/handoff emitter and does not call Codex/GPT workers or require `OPENAI_API_KEY` / `CODEX_API_KEY`. Public-readiness evidence is recorded in `reports/loop/publication_readiness_report.md`, and the first Phase1 start packet is recorded in `reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/`.
