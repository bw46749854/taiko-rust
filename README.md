# OpenTaiko Phase1 Codex Loop Bootstrap Package

Status: canonical
Last updated: 2026-06-26

## Purpose

This package prepares a Codex loop engineering workflow for implementing Phase1 of an OpenTaiko-compatible Rust rhythm game.

The controlling objective is autonomous loop operation: separated AI sessions must be able to read tickets, implement work, verify results, detect failures, route failures back into repair tickets, and advance to the next ticket without extra human judgement. See `docs/00_project_objective.md` and `docs/05_autonomy_scorecard.md`.

Phase1 means normal-play completion for OpenTaiko-supported TJA charts, including the gameplay features classified in `docs/25_phase1_feature_classification.md` and the adoption decisions in `research/opentaiko/10_phase1_adoption_decisions.md`.

## Documentation language policy

Canonical operational docs, prompts, tickets, scripts, schemas, and code comments are English. Japanese explanatory documents may exist only as explicitly marked translations or non-canonical explanations, such as `*.ja.md`, and must point to the English canonical source. Machine-readable keys, command names, gate IDs, ticket IDs, crate names, schema fields, and other identifiers remain English in all files. If a Japanese document is canonical today, create the English canonical version first, then mark the Japanese document as a translation, non-canonical explanation, or archive. See `docs/02_documentation_language_policy.md`.

## Current capabilities

| Surface | Current capability |
|---|---|
| Loop CLI | Provides machine-readable ticket, gate, status, controller, failure-route, retry-budget, and Phase1 feature-planning commands through `taiko_cli`. |
| Fixture validation | Validates the committed synthetic fixture manifest and inspects basic TJA structure through `taiko_cli fixture` without proving full gameplay behavior. |
| Headless autoplay | Provides deterministic, render-free, audio-free perfect-autoplay JSON evidence for synthetic fixtures and individual charts. |
| Timing analyzer | Reports machine-readable `max_error_ms`, `mean_error_ms`, `p95_error_ms`, threshold, and failure-category evidence over perfect-autoplay output. |
| Failure feedback | Ingests failure reports, classifies reject/block outcomes, previews repair tickets, materializes repair or blocker tickets, and validates ticket structure. |
| QA verdict | Produces machine-readable QA run, comparison, and verdict output so `pass`, `reject`, and `block` decisions do not rely on prose-only judgement. |
| Rust preflight | Converts cargo and `taiko_cli` runtime checks into pass/reject/block evidence under `reports/preflight/latest/`. |
| Session separation | Uses role-specific worktrees, session metadata, and path-policy checks to keep implementation, review, and QA responsibilities separated. |
| GitHub PR loop | Provides deterministic branch, worktree, PR, QA verdict application, merge, ticket advance, and handoff scripts. |
| Auto-merge controller | Uses GitHub Actions as a deterministic verifier/gate/controller surface for eligible PRs without AI-provider calls or OpenAI API keys. |
| E2E smoke verification | Exercises pass, reject, block, retry-budget, and revert controller routes in dry-run mode before gameplay implementation proceeds. |
| Phase1 gameplay handoff | Renders a deterministic worker start packet for the first gameplay ticket from the Phase1 feature manifest and gate evidence. |

## Current operational surfaces

### Loop orchestration

```bash
taiko_cli loop inspect tickets --format json
taiko_cli loop inspect gates --format json
taiko_cli loop next --format json
taiko_cli loop gate GATE-0000 --dry-run --format json
taiko_cli loop report status --format json
taiko_cli loop run-once --mode plan --format json
taiko_cli loop run-once --mode apply --format json
scripts/loop_run_once.sh --mode plan
scripts/loop_run_once.sh --mode apply
```

`--mode plan` is side-effect free. `--mode apply` writes controller artifacts under `reports/loop/<run_id>/`, including `controller_plan.json`, `controller_plan.md`, and `next_codex_prompt.md`. The controller emits one next action: `start_worker`, `classify_failure`, or `wait_for_ready_ticket`.

### Fixture and runtime evidence

```bash
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
taiko_cli headless autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json
headless_autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
timing_log_analyzer --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```

Fixture validation proves committed fixture readability and basic TJA structure. Headless autoplay and timing analyzer output provide deterministic evidence for QA / Regression Session, but they do not yet certify final OpenTaiko-compatible audio sync, visual scroll timing, or judgement-window precision.

### Failure feedback, repair, and QA verdicts

```bash
taiko_cli loop failure ingest reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop failure classify --input reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket materialize --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
taiko_cli loop retry-budget check --ticket TKT-9001 --format json
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa compare --baseline reports/baseline --current reports/current --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

Reject verdicts route to failure feedback and repair-ticket materialization. Block verdicts identify missing machine evidence. Retry limits live in `operations/retry_budget.toml`.

### Rust preflight and static validation

```bash
scripts/check_rust_workspace_static.py
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
scripts/check_rust_preflight_static.py
```

`cargo` commands require a Rust-enabled environment. Static checks are fallback evidence only where Rust cannot execute; they are not acceptance evidence for the Rust substrate.

### GitHub controller, session, and handoff surfaces

```bash
scripts/check_session_separation.py
scripts/check_role_path_policy.py
scripts/loop_create_worktree.sh TKT-0050 --role test-infra --dry-run
scripts/check_github_pr_orchestration_static.py
scripts/loop_create_branch.sh TKT-0000 --dry-run
scripts/loop_create_worktree.sh TKT-0000 --dry-run
scripts/loop_open_pr.sh TKT-0000 --branch loop/TKT-0000-spec-repair-gate-and-bootstrap-consistency-check --dry-run
scripts/loop_apply_qa_verdict.py --ticket TKT-0000 --verdict reports/qa/TKT-0000.verdict.json
scripts/loop_merge_and_advance.sh TKT-0000 --pr 1 --verdict reports/qa/TKT-0000.verdict.json --dry-run
scripts/check_github_actions_gate_static.py
scripts/check_auto_merge_conditions.py
scripts/loop_controller_github.sh --mode plan
scripts/loop_auto_merge_pr.sh --ticket TKT-0005 --pr 12 --metadata reports/session_metadata/TKT-0005.toml --qa reports/qa/TKT-0005.verdict.json --dry-run
scripts/loop_revert_last_merge.sh --run-id RUN-20260626-0001 --reason regression --dry-run
scripts/check_e2e_smoke_static.py
scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
scripts/render_next_codex_prompt.py --mode automation --dry-run
scripts/loop_emit_worker_handoff.py --dry-run
```

GitHub Actions remains a deterministic verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator. Actions do not run Codex/GPT workers, call AI providers, require `OPENAI_API_KEY` or `CODEX_API_KEY`, or use `openai/codex-action@v1`.

### Phase1 gameplay entry surface

```bash
scripts/check_phase1_feature_loop_static.py
taiko_cli phase1 feature validate --manifest operations/phase1_feature_ticket_manifest.toml --format json
taiko_cli phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --force-preview --dry-run --format prompt
scripts/check_phase1_gameplay_start_static.py
```

`operations/phase1_feature_ticket_manifest.toml` is the machine-readable source for gameplay ticket order, required command evidence, QA evidence, and failure routing. The first gameplay ticket remains `TKT-0005`, but the ticket file currently remains Blocked and must not be started until the rendered start packet and governing gate evidence say it is ready.

## Operations migration rail

The operations migration rail is recorded as complete through `OPS-0001` through `OPS-0009`. GitHub Actions remains a verifier/gate/controller/handoff surface and does not run AI worker code or require OpenAI API keys. The current `.loop/tickets/*.md` files still mark all `TKT-*` tickets as Blocked, including `TKT-0005`; Control Session must rely on the machine-readable ticket and gate surfaces rather than prose-only ordering.

## Start here

1. Read `AGENTS.md`.
2. Read `docs/00_project_objective.md`.
3. Read `docs/05_autonomy_scorecard.md`.
4. Read `docs/73_first_execution_batch.md`.
5. Read `docs/86_codex_cloud_environment_setup.md` and `docs/87_secret_and_network_policy.md`.
6. Read `docs/88_auto_merge_loop_policy.md`, `docs/89_loop_controller_state_machine.md`, `docs/90_session_metadata_and_path_policy.md`, `docs/91_repair_materialization_and_retry_budget.md`, `docs/92_codex_plus_automation_operation.md`, `docs/93_github_actions_auto_merge_controller.md`, `docs/94_e2e_smoke_loop_verification.md`, and `docs/95_phase1_gameplay_loop_start.md`.
7. Inspect current machine state with `taiko_cli loop inspect tickets --format json`, `taiko_cli loop inspect gates --format json`, and `taiko_cli loop next --format json`.
8. Before starting gameplay work, render and validate the `TKT-0005` start packet with the Phase1 gameplay entry commands above and confirm the ticket/gate state is not Blocked.
9. Keep implementation, review, and QA evidence separated by role worktree and session metadata.

## Initial ticket state

| Ticket group | Status in `.loop/tickets/*.md` |
|---|---:|
| `OPS-0001` through `OPS-0009` | Done |
| `TKT-0000` through `TKT-0015` | Blocked |
| `TKT-0035`, `TKT-0040`, `TKT-0050`, `TKT-0060`, `TKT-0075` | Blocked |

## Public repository hardening

The public-readiness floor includes `LICENSE`, `NOTICE.md`, `THIRD_PARTY_NOTICES.md`, `SECURITY.md`, `docs/97_public_repository_hardening.md`, `operations/public_repository_policy.toml`, `.github/dependabot.yml`, and `scripts/check_public_repository_static.py`. GitHub Actions remains a verifier, gate, merge controller, ticket advancement controller, and handoff artifact generator. It does not run Codex or GPT workers and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.

## Asset policy

This package does not include commercial song, audio, chart, image, video, or skin assets. User-selected song validation uses the content-root contract. Development assets are provided by a Google Drive zip manifest, verified by sha256, and extracted to `.external_assets/opentaiko/`. Production reads the same OpenTaiko-compatible layout from `OPENTAIKO_CONTENT_ROOT` or `--content-root`.

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

The current executable loop surfaces improve A1 through session/worktree separation, A2 through machine-readable ticket and gate commands, A3 through Rust preflight, A4 through fixture and QA commands, A5 through headless autoplay and timing analysis, A6 through deterministic GitHub controller checks, and A7 through failure feedback, repair materialization, and retry-budget routing.
