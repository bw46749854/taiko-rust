# Final Bootstrap Prompt

Status: canonical

## Mission

Canonical prompt for starting Codex loop from the Step23 package after the operations migration rail has been added.

The controlling objective is autonomous loop operation: separated AI sessions must read tickets, implement work, verify evidence, detect failure, route failure into repair tickets, and advance to the next ticket without extra human judgement.

The active start ticket in this package is `OPS-0008`. Do not start Phase1 gameplay implementation from this prompt.

## Mandatory read set

- `AGENTS.md`
- `docs/00_project_objective.md`
- `docs/04_loop_operational_maturity_model.md`
- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `docs/07_failure_feedback_protocol.md`
- `docs/40_loop_cli_contract.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/25_phase1_feature_classification.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`
- `docs/70_phase1_ticket_backlog.md`
- `docs/71_ticket_dependency_graph.md`
- `docs/73_first_execution_batch.md`
- `docs/83_codex_surface_decision.md`
- `docs/84_github_pr_loop_contract.md`
- `docs/85_rust_enabled_preflight_gate.md`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`
- `docs/88_auto_merge_loop_policy.md`
- `docs/89_loop_controller_state_machine.md`
- `operations/loop_policy.toml`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `operations/path_policy.toml`
- `operations/failure_classification_rules.toml`
- `operations/retry_budget.toml`
- `operations/codex_automation_policy.toml`
- `docs/93_github_actions_auto_merge_controller.md`
- `docs/94_e2e_smoke_loop_verification.md`
- `docs/95_phase1_gameplay_loop_start.md`
- `operations/auto_merge_policy.toml`
- `operations/e2e_smoke_policy.toml`
- `.loop/tickets/OPS-0001.md`
- `.loop/gates/GATE-OPS-0000-migration-ready.md`
- `.loop/tickets/TKT-0000.md`
- `.loop/gates/GATE-0000-spec-repair.md`

## Operating rules

- Use canonical crate names from `AGENTS.md`.
- Do not use deprecated crate names.
- Do not bundle user-selected song assets.
- Do not approve your own implementation.
- Record command outputs and remaining risks.
- Every ticket handoff must include next-ticket transition evidence.
- Every gate report must include autonomy scorecard axis delta.
- Treat parser crash, timing anomaly, branch route mismatch, score/gauge mismatch, and unclassified command report as blocking unless the ticket explicitly limits scope.
- Do not require `OPENAI_API_KEY` or `CODEX_API_KEY` for Step17 loop-controller operation.
- Do not require `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1` for Step20 Plus-plan automation operation.
- Run Step22 E2E smoke verification before starting Phase1 gameplay tickets.

## Step17 controller check

Run the no-Rust static checks first:

```bash
scripts/check_bootstrap_consistency.sh
scripts/ci_local_equivalent.sh --static-only
scripts/check_loop_controller_static.py
scripts/check_e2e_smoke_static.py
```

When Rust is available, run:

```bash
taiko_cli loop run-once --mode plan --format json
scripts/loop_run_once.sh --mode plan
```

Use `--mode apply` only to write controller artifacts under `reports/loop/<run_id>/`. Do not mark original `TKT-*` tickets Done, pass implementation gates, or merge branches from this prompt.

## Required handoff format

```text
Session:
Ticket/Gate:
Worktree:
Files changed or reviewed:
Commands run:
Result:
Autonomy scorecard delta:
Next-ticket transition evidence:
Blocking issues:
Next recommended action:
```

## Canonical first message to Codex Control Session

```text
You are the Control Session for OpenTaiko Phase1 Rust loop engineering.

Read AGENTS.md first.
Then read:
- docs/00_project_objective.md
- docs/05_autonomy_scorecard.md
- docs/06_gate_transition_rules.md
- docs/40_loop_cli_contract.md
- docs/73_first_execution_batch.md
- docs/83_codex_surface_decision.md
- docs/84_github_pr_loop_contract.md
- docs/85_rust_enabled_preflight_gate.md
- docs/86_codex_cloud_environment_setup.md
- docs/87_secret_and_network_policy.md
- docs/88_auto_merge_loop_policy.md
- docs/89_loop_controller_state_machine.md
- docs/92_codex_plus_automation_operation.md
- operations/loop_policy.toml
- operations/codex_automation_policy.toml
- .loop/tickets/OPS-0001.md
- .loop/gates/GATE-OPS-0000-migration-ready.md
- .loop/tickets/TKT-0000.md
- .loop/gates/GATE-0000-spec-repair.md

Do not start Phase1 gameplay implementation.
Do not mark TKT-0001 or GATE-0030 as passed from static inspection alone.
Do not introduce OPENAI_API_KEY, CODEX_API_KEY, or openai/codex-action@v1 as a Step20 requirement.

Task:
1. Confirm that only OPS-0008 is Ready.
2. Run scripts/check_bootstrap_consistency.sh.
3. Run scripts/ci_local_equivalent.sh --static-only.
4. Run scripts/check_loop_controller_static.py.
5. Run scripts/check_session_separation.py and scripts/check_role_path_policy.py.
6. Run scripts/check_repair_materialization_static.py.
7. Run scripts/check_codex_automation_static.py and scripts/render_next_codex_prompt.py --mode automation --dry-run.
8. When Rust is available, run taiko_cli loop run-once --mode plan --format json, scripts/loop_run_once.sh --mode plan, taiko_cli loop failure classify --input reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json, and taiko_cli loop retry-budget check --ticket TKT-9001 --format json.
9. Write .loop/session_logs/GATE-OPS-0000-bootstrap-freeze-report.md for OPS-0001 evidence.

The report must include pass/reject/block verdict, command log, autonomy scorecard delta, Rust dynamic evidence status, controller run-once status, and next-ticket transition evidence.
After writing the report, hand off to the Design Review Session for review. Keep TKT-0000 and Phase1 gameplay tickets Blocked during this migration step.
```


## Step18 required read additions

- `docs/90_session_metadata_and_path_policy.md`
- `operations/path_policy.toml`
- `schemas/session_metadata_schema.md`
- `scripts/check_session_separation.py`
- `scripts/check_role_path_policy.py`

Run these static checks before starting Phase1 gameplay work:

```bash
scripts/check_session_separation.py
scripts/check_role_path_policy.py
scripts/loop_create_worktree.sh TKT-0050 --role test-infra --dry-run
```


## Step19 required read additions

- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `operations/failure_classification_rules.toml`
- `operations/retry_budget.toml`
- `operations/codex_automation_policy.toml`
- `docs/93_github_actions_auto_merge_controller.md`
- `docs/94_e2e_smoke_loop_verification.md`
- `docs/95_phase1_gameplay_loop_start.md`
- `operations/auto_merge_policy.toml`
- `operations/e2e_smoke_policy.toml`
- `templates/repair_ticket_template.md`
- `templates/blocker_ticket_template.md`
- `scripts/check_repair_materialization_static.py`

Run this static check before Phase1 gameplay work:

```bash
scripts/check_repair_materialization_static.py
```


## Step20 required read additions

- `docs/92_codex_plus_automation_operation.md`
- `operations/codex_automation_policy.toml`
- `docs/93_github_actions_auto_merge_controller.md`
- `docs/94_e2e_smoke_loop_verification.md`
- `docs/95_phase1_gameplay_loop_start.md`
- `operations/auto_merge_policy.toml`
- `operations/e2e_smoke_policy.toml`
- `prompts/70_codex_automation_loop_runner.md`
- `prompts/71_codex_cloud_ticket_worker.md`
- `scripts/render_next_codex_prompt.py`
- `scripts/check_codex_automation_static.py`

Run this static check before Phase1 gameplay work:

```bash
scripts/check_codex_automation_static.py
scripts/render_next_codex_prompt.py --mode automation --dry-run
```

Step20 is Plus-plan operation only. GitHub Actions must not call `openai/codex-action@v1`.


## Step21 auto-merge controller read set

Before starting gameplay implementation, read:

- `docs/93_github_actions_auto_merge_controller.md`
- `operations/auto_merge_policy.toml`
- `.github/workflows/loop-controller.yml`
- `scripts/check_auto_merge_conditions.py`
- `scripts/loop_controller_github.sh`
- `scripts/loop_auto_merge_pr.sh`
- `scripts/loop_revert_last_merge.sh`

Run:

```bash
scripts/check_auto_merge_conditions.py
scripts/loop_controller_github.sh --mode plan
```

Do not add `OPENAI_API_KEY` or GitHub Actions AI worker usage. GitHub Actions may gate, merge, advance, and revert only.


## Step22 smoke verification

Before starting Phase1 gameplay implementation, run:

```bash
scripts/check_e2e_smoke_static.py
scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
```

The smoke loop must pass pass/reject/block/retry/revert routes without live GitHub mutation and without API-key AI workers.


## Step23 note

Do not start Phase1 gameplay implementation from prose. Use `scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run` and proceed only from a machine-readable `verdict = ready` start packet.


## OPS-0003 public hardening read set

Before any Phase1 gameplay ticket starts, read `docs/97_public_repository_hardening.md`, `operations/public_repository_policy.toml`, and run `scripts/check_public_repository_static.py`. GitHub Actions must remain a deterministic verifier/gate/controller and must not use OpenAI API keys.


## OPS-0005 GitHub Actions gate normalization read set

Before auto-merge candidate discovery begins, read `operations/auto_merge_policy.toml`, `.github/workflows/loop-controller.yml`, `docs/93_github_actions_auto_merge_controller.md`, and run `scripts/check_github_actions_gate_static.py`. GitHub Actions remains deterministic and must not run Codex/GPT workers or require OpenAI API keys.


## OPS-0006 Auto-merge candidate discovery read set

Before ticket advancement begins, read `schemas/auto_merge_candidate_schema.md`, `scripts/select_auto_merge_candidate.py`, `operations/auto_merge_policy.toml`, and `docs/93_github_actions_auto_merge_controller.md`. GitHub Actions remains deterministic and must not run Codex/GPT workers or require OpenAI API keys.

## OPS-0007 Ticket advance engine read set

The active start ticket in this package is `OPS-0008`. Confirm that only OPS-0008 is Ready. Use `scripts/loop_advance_ticket.py` with `operations/ticket_transition_policy.toml` to validate merge-history driven ticket advancement, and write evidence under `reports/loop/ticket_transitions/`.


## OPS-0008 requirement

For worker handoff, run `scripts/loop_emit_worker_handoff.py --mode plan --expect plan` and inspect `reports/loop/worker_handoff/latest.md`. GitHub Actions must not call Codex/GPT or require `OPENAI_API_KEY` / `CODEX_API_KEY`.
