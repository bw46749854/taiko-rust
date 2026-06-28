# 02. Document Index

Status: canonical

## Core goal and preparation

- `docs/00_project_goal.md`
- `docs/00_project_objective.md`
- `docs/01_preparation_workplan.md`
- `docs/03_definition_of_ready.md`
- `docs/04_loop_operational_maturity_model.md`
- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `docs/07_failure_feedback_protocol.md`

## OpenTaiko research and scope

- `docs/10_opentaiko_research_plan.md`
- `docs/11_opentaiko_feature_taxonomy.md`
- `docs/12_opentaiko_phase1_research_questions.md`
- `research/opentaiko/01_source_map.md`
- `research/opentaiko/02_tja_parser_commands.md`
- `research/opentaiko/03_note_type_mapping.md`
- `research/opentaiko/04_timing_and_measure_model.md`
- `research/opentaiko/05_roll_balloon_balloonex.md`
- `research/opentaiko/06_branching_model.md`
- `research/opentaiko/07_scroll_and_visual_timing.md`
- `research/opentaiko/08_score_gauge_clear_model.md`
- `research/opentaiko/09_course_audio_song_selection.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`

## Phase1 contract

- `docs/20_phase1_scope.md`
- `docs/21_phase1_non_scope.md`
- `docs/22_phase1_acceptance_criteria.md`
- `docs/23_phase1_definition_of_done.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/25_phase1_feature_classification.md`
- `docs/26_phase1_user_selected_song_validation.md`
- `docs/27_phase1_open_taiko_compatibility_boundary.md`

## Architecture and runtime

- `docs/30_rust_architecture_overview.md`
- `docs/31_module_boundaries.md`
- `docs/32_data_model.md`
- `docs/33_runtime_loop.md`
- `docs/34_error_handling_and_logging.md`
- `docs/40_timing_model.md`
- `docs/41_audio_sync_model.md`
- `docs/42_judgement_model.md`

## Timing log and test harness

- `fixtures/synthetic/phase1_synthetic_manifest.toml`
- `fixtures/synthetic/phase1_synthetic_manifest.schema.md`

- `docs/43_timing_log_schema.md`
- `docs/44_timing_log_analyzer_spec.md`
- `docs/50_test_harness_overview.md`
- `docs/51_fixture_design.md`
- `docs/52_golden_update_policy.md`
- `docs/53_ci_commands.md`

## Coverage

- `docs/coverage/phase1_feature_coverage_matrix.md`
- `docs/coverage/phase1_fixture_to_feature_traceability.md`
- `docs/coverage/phase1_user_song_category_matrix.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`

## Loop engineering

- `AGENTS.md`
- `docs/40_loop_cli_contract.md`
- `docs/60_session_topology.md`
- `docs/61_worktree_policy.md`
- `docs/62_loop_engineering_flow.md`
- `docs/63_ticket_lifecycle.md`
- `docs/64_review_and_qa_gates.md`
- `docs/70_phase1_ticket_backlog.md`
- `docs/71_ticket_dependency_graph.md`
- `docs/72_milestone_plan.md`
- `docs/73_first_execution_batch.md`
- `docs/80_codex_execution_checklist.md`
- `docs/81_human_operator_minimal_steps.md`
- `docs/82_failure_recovery_playbook.md`
- `docs/83_codex_surface_decision.md`
- `docs/84_github_pr_loop_contract.md`
- `docs/85_rust_enabled_preflight_gate.md`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`
- `docs/88_auto_merge_loop_policy.md`
- `docs/89_loop_controller_state_machine.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`

## Gates and tickets

- `.loop/gates/GATE-0000-spec-repair.md`
- `.loop/gates/GATE-0010-coverage-ready.md`
- `.loop/gates/GATE-0020-implementation-ready.md`
- `.loop/gates/GATE-0030-loop-cli-ready.md`
- `.loop/tickets/TKT-0000.md`
- `.loop/tickets/TKT-0001.md` ... `.loop/tickets/TKT-0015.md`
- `.loop/tickets/TKT-0035.md`
- `.loop/tickets/TKT-0075.md`

## Prompts and templates

- `prompts/*.md`
- `templates/*.md`

## Operations

- `operations/bootstrap_bundle_layout.md`
- `operations/manifest.md`
- `operations/loop_policy.toml`
- `operations/path_policy.toml`
- `operations/failure_classification_rules.toml`
- `operations/retry_budget.toml`

## Bootstrap repair scripts

- `scripts/check_bootstrap_consistency.sh`
- `scripts/check_reference_integrity.py`
- `scripts/validate_fixture_manifest.py`
- `scripts/validate_no_user_assets.sh`
- `scripts/check_autonomy_scorecard.py`


## GitHub orchestration

- `.github/pull_request_template.md`
- `.github/workflows/loop-pr-gate.yml`
- `.github/workflows/codex-review.yml`
- `.github/codex/prompts/review.md`
- `templates/session_run_metadata_template.toml`
- `scripts/loop_create_branch.sh`
- `scripts/loop_create_worktree.sh`
- `scripts/loop_open_pr.sh`
- `scripts/loop_apply_qa_verdict.py`
- `scripts/loop_merge_and_advance.sh`
- `scripts/check_github_pr_orchestration_static.py`

## Rust preflight evidence

- `docs/85_rust_enabled_preflight_gate.md`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`
- `docs/88_auto_merge_loop_policy.md`
- `docs/89_loop_controller_state_machine.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `.github/workflows/rust-preflight.yml`
- `reports/preflight/README.md`
- `templates/rust_preflight_report_template.md`
- `scripts/run_rust_preflight.sh`
- `scripts/check_runtime_evidence_files.py`
- `scripts/check_rust_preflight_static.py`


## Codex Cloud / CI environment

- `rust-toolchain.toml`
- `.codex/config.toml`
- `.cargo/config.toml`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`
- `docs/88_auto_merge_loop_policy.md`
- `docs/89_loop_controller_state_machine.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `scripts/codex_cloud_setup.sh`
- `scripts/ci_local_equivalent.sh`
- `scripts/check_codex_cloud_env_static.py`

## loop run-once controller loop controller

- `docs/88_auto_merge_loop_policy.md`
- `docs/89_loop_controller_state_machine.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `operations/loop_policy.toml`
- `operations/path_policy.toml`
- `operations/failure_classification_rules.toml`
- `operations/retry_budget.toml`
- `scripts/loop_run_once.sh`
- `scripts/check_loop_controller_static.py`


## session separation additions

- `docs/90_session_metadata_and_path_policy.md` — machine-readable session metadata, role worktree separation, and path policy gate.
- `operations/path_policy.toml` — role allow/deny path policy for PR gating.
- `schemas/session_metadata_schema.md` — metadata field contract.


## repair materialization and retry-budget route additions

- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md` — failure classification, repair/blocker ticket materialization, and retry budget contract.
- `operations/failure_classification_rules.toml` — reject/block route table.
- `operations/retry_budget.toml` — loop retry limits.
- `templates/repair_ticket_template.md` and `templates/blocker_ticket_template.md` — generated ticket shapes.
- `scripts/check_repair_materialization_static.py` — static validation for repair materialization and retry-budget route.

- `operations/codex_automation_policy.toml`
- `prompts/70_codex_automation_loop_runner.md`
- `prompts/71_codex_cloud_ticket_worker.md`
- `scripts/render_next_codex_prompt.py`
- `scripts/check_codex_automation_static.py`
- `reports/loop_automation/README.md`


## auto-merge controller controller

- `docs/93_github_actions_auto_merge_controller.md` — GitHub Actions gate/merge/advance controller contract.
- `operations/auto_merge_policy.toml` — machine-readable auto-merge policy.
- `.github/workflows/loop-controller.yml` — event-driven controller workflow.
- `scripts/check_auto_merge_conditions.py` — static and evidence validation for auto-merge candidates.
- `scripts/loop_controller_github.sh` — GitHub controller planning/apply wrapper.
- `scripts/loop_auto_merge_pr.sh` — guarded squash merge helper with merge history output.
- `scripts/loop_revert_last_merge.sh` — regression revert PR helper.
- `reports/loop/merge_history/README.md` — autonomous merge evidence directory.
- `reports/regression/README.md` — regression evidence directory.

## Autonomous loop controller and operations

- `docs/88_auto_merge_loop_policy.md`
- `docs/89_loop_controller_state_machine.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `docs/93_github_actions_auto_merge_controller.md`
- `docs/94_e2e_smoke_loop_verification.md`

## Phase1 gameplay worker handoff

- `docs/95_phase1_gameplay_loop_start.md`
- `operations/phase1_gameplay_loop_policy.toml`
- `prompts/72_phase1_gameplay_ticket_runner.md`
- `reports/phase1_gameplay_loop/README.md`
- `scripts/render_phase1_gameplay_ticket_prompt.py`
- `scripts/check_phase1_gameplay_start_static.py`


## Operations migration rail

- `.loop/gates/GATE-OPS-0000-migration-ready.md`
- `.loop/tickets/OPS-0001.md`
- `.loop/tickets/OPS-0002.md`
- `.loop/tickets/OPS-0003.md`
- `.loop/tickets/OPS-0004.md`
- `.loop/tickets/OPS-0005.md`
- `.loop/tickets/OPS-0006.md`
- `.loop/tickets/OPS-0007.md`
- `.loop/tickets/OPS-0008.md`
- `.loop/tickets/OPS-0009.md`

The OPS rail is active before Phase1 gameplay implementation. It handles cleanup, public repository hardening, asset bundle determinism, GitHub Actions gate normalization, auto-merge candidate discovery, ticket advancement, Codex handoff, and final E2E smoke verification.


## Public repository hardening

- `LICENSE`
- `NOTICE.md`
- `THIRD_PARTY_NOTICES.md`
- `SECURITY.md`
- `docs/97_public_repository_hardening.md`
- `operations/public_repository_policy.toml`
- `.github/dependabot.yml`
- `scripts/check_public_repository_static.py`

## Asset bundle and content root

- `docs/98_content_root_and_asset_bundle_contract.md`
- `operations/dev_asset_bundle.example.toml`
- `schemas/dev_asset_bundle_schema.md`
- `scripts/fetch_dev_asset_bundle.py`
- `scripts/check_asset_bundle_manifest.py`
- `reports/assets/README.md`

## OPS-0005 GitHub Actions gate normalization

- `scripts/check_github_actions_gate_static.py` — validates required check context names, workflow permissions, checkout credential policy, `workflow_run` success guards, and `loop-controller-main` concurrency.
- `operations/auto_merge_policy.toml` — canonical required check list and privileged workflow boundary.
- `.github/workflows/loop-controller.yml` — deterministic controller workflow; it does not run AI workers.


## OPS-0008 worker handoff documents

- `docs/99_codex_worker_handoff_contract.md` — canonical worker handoff contract.
- `schemas/worker_handoff_schema.md` — machine-readable handoff schema.
- `operations/worker_handoff_policy.toml` — policy for the deterministic handoff emitter.
- `prompts/73_next_ticket_handoff.md` — reusable worker prompt surface.


## OPS-0009 final readiness documents

- `operations/ops_migration_readiness_policy.toml`
- `schemas/ops_migration_readiness_schema.md`
- `scripts/check_ops_migration_readiness.py`
- `reports/loop/publication_readiness_report.md`
- `.loop/session_logs/GATE-OPS-0000-report.md`
- `.loop/session_logs/GATE-0090-report.md`
- `reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_gameplay_start.json`
