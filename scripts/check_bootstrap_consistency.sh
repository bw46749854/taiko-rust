#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

required_files=(
  "AGENTS.md"
  "docs/00_project_objective.md"
  "docs/04_loop_operational_maturity_model.md"
  "docs/05_autonomy_scorecard.md"
  "docs/06_gate_transition_rules.md"
  "docs/07_failure_feedback_protocol.md"
  "docs/40_loop_cli_contract.md"
  "docs/45_fixture_validation_contract.md"
  "docs/46_headless_autoplay_contract.md"
  "docs/47_timing_log_analyzer_contract.md"
  "docs/48_failure_feedback_loop_contract.md"
  "docs/49_qa_regression_gate_contract.md"
  ".loop/gates/GATE-0000-spec-repair.md"
  ".loop/gates/GATE-0010-coverage-ready.md"
  ".loop/gates/GATE-0020-implementation-ready.md"
  ".loop/gates/GATE-0030-loop-cli-ready.md"
  ".loop/gates/GATE-0040-fixture-validation-ready.md"
  ".loop/gates/GATE-0050-headless-autoplay-ready.md"
  ".loop/gates/GATE-0060-timing-analyzer-ready.md"
  ".loop/gates/GATE-0070-failure-feedback-ready.md"
  ".loop/gates/GATE-0080-qa-regression-ready.md"
  ".loop/tickets/TKT-0000.md"
  ".loop/gates/GATE-OPS-0000-migration-ready.md"
  ".loop/tickets/OPS-0001.md"
  ".loop/tickets/OPS-0002.md"
  ".loop/tickets/OPS-0003.md"
  ".loop/tickets/OPS-0004.md"
  ".loop/tickets/OPS-0005.md"
  ".loop/tickets/OPS-0006.md"
  ".loop/tickets/OPS-0007.md"
  ".loop/tickets/OPS-0008.md"
  ".loop/tickets/OPS-0009.md"
  "docs/24_phase1_normal_play_compatibility_contract.md"
  "docs/25_phase1_feature_classification.md"
  "docs/26_phase1_user_selected_song_validation.md"
  "docs/27_phase1_open_taiko_compatibility_boundary.md"
  "research/opentaiko/10_phase1_adoption_decisions.md"
  "docs/coverage/phase1_acceptance_gate_matrix.md"
  "docs/coverage/phase1_fixture_to_feature_traceability.md"
  "fixtures/synthetic/phase1_synthetic_manifest.toml"
  "fixtures/synthetic/phase1_synthetic_manifest.schema.md"
  "prompts/60_final_bootstrap_prompt.md"
  "templates/ticket_template.md"
  "templates/plan_review_template.md"
  "templates/pr_review_template.md"
  "templates/qa_report_template.md"
  "templates/failure_report_template.md"
  "templates/gate_report_template.md"
  "reports/failures/FF-0001-sample-timing-cli-contract-error.md"
  "reports/qa/README.md"
  ".github/workflows/phase1-loop.yml"
  "scripts/check_reference_integrity.py"
  "scripts/check_autonomy_scorecard.py"
  "scripts/check_rust_workspace_static.py"
  "scripts/check_fixture_validation_static.py"
  "scripts/check_headless_autoplay_static.py"
  "scripts/check_timing_analyzer_static.py"
  "scripts/check_failure_feedback_static.py"
  "scripts/check_qa_regression_static.py"

  "docs/74_phase1_feature_loop_entry_contract.md"
  "docs/75_phase1_feature_ticket_manifest_schema.md"
  "docs/76_phase1_feature_acceptance_command_matrix.md"
  ".loop/gates/GATE-0090-phase1-feature-loop-ready.md"
  ".loop/tickets/TKT-0060.md"
  "operations/phase1_feature_ticket_manifest.toml"
  "reports/phase1_feature_loop/README.md"
  "scripts/check_phase1_feature_loop_static.py"
  "scripts/validate_synthetic_fixture_structure.py"
  "Cargo.toml"
  "crates/taiko_domain/Cargo.toml"
  "crates/taiko_domain/src/lib.rs"
  "crates/taiko_chart/Cargo.toml"
  "crates/taiko_chart/src/lib.rs"
  "crates/taiko_timing/Cargo.toml"
  "crates/taiko_timing/src/lib.rs"
  "crates/taiko_runtime/Cargo.toml"
  "crates/taiko_runtime/src/lib.rs"
  "crates/taiko_audio/Cargo.toml"
  "crates/taiko_audio/src/lib.rs"
  "crates/taiko_render/Cargo.toml"
  "crates/taiko_render/src/lib.rs"
  "crates/taiko_test_support/Cargo.toml"
  "crates/taiko_test_support/src/lib.rs"
  "crates/taiko_cli/Cargo.toml"
  "crates/taiko_cli/src/lib.rs"
  "crates/taiko_cli/src/bin/taiko_cli.rs"
  "crates/taiko_cli/src/bin/taiko_play.rs"
  "crates/taiko_cli/src/bin/headless_autoplay.rs"
  "crates/taiko_cli/src/bin/timing_log_analyzer.rs"
  "scripts/validate_fixture_manifest.py"
  "scripts/validate_no_user_assets.sh"
  "docs/83_codex_surface_decision.md"
  "docs/84_github_pr_loop_contract.md"
  ".github/pull_request_template.md"
  ".github/workflows/loop-pr-gate.yml"
  ".github/workflows/codex-review.yml"
  ".github/codex/prompts/review.md"
  "templates/session_run_metadata_template.toml"
  "scripts/loop_create_branch.sh"
  "scripts/loop_create_worktree.sh"
  "scripts/loop_open_pr.sh"
  "scripts/loop_apply_qa_verdict.py"
  "scripts/loop_merge_and_advance.sh"
  "scripts/check_github_pr_orchestration_static.py"
  "scripts/check_github_actions_gate_static.py"
  ".gitignore"
  "docs/85_rust_enabled_preflight_gate.md"
  "scripts/run_rust_preflight.sh"
  "scripts/check_runtime_evidence_files.py"
  "scripts/check_rust_preflight_static.py"
  ".github/workflows/rust-preflight.yml"
  "reports/preflight/README.md"
  "templates/rust_preflight_report_template.md"

  "rust-toolchain.toml"
  ".codex/config.toml"
  ".cargo/config.toml"
  "docs/86_codex_cloud_environment_setup.md"
  "docs/87_secret_and_network_policy.md"
  "scripts/codex_cloud_setup.sh"
  "scripts/ci_local_equivalent.sh"
  "scripts/check_codex_cloud_env_static.py"
  "docs/88_auto_merge_loop_policy.md"
  "docs/89_loop_controller_state_machine.md"
  "operations/loop_policy.toml"
  "scripts/loop_run_once.sh"
  "scripts/check_loop_controller_static.py"
  "reports/loop/README.md"
  "docs/90_session_metadata_and_path_policy.md"
  "operations/path_policy.toml"
  "schemas/session_metadata_schema.md"
  "reports/session_metadata/README.md"
  "scripts/check_session_separation.py"
  "scripts/check_role_path_policy.py"
  "docs/91_repair_materialization_and_retry_budget.md"
  "operations/failure_classification_rules.toml"
  "operations/retry_budget.toml"
  "templates/repair_ticket_template.md"
  "templates/blocker_ticket_template.md"
  "reports/retry_budget/README.md"
  "scripts/check_repair_materialization_static.py"

  "docs/92_codex_plus_automation_operation.md"
  "operations/codex_automation_policy.toml"
  "prompts/70_codex_automation_loop_runner.md"
  "prompts/71_codex_cloud_ticket_worker.md"
  "scripts/render_next_codex_prompt.py"
  "reports/loop_automation/README.md"
  "scripts/check_codex_automation_static.py"

  "docs/93_github_actions_auto_merge_controller.md"
  "operations/auto_merge_policy.toml"
  ".github/workflows/loop-controller.yml"
  "scripts/check_auto_merge_conditions.py"

  "scripts/select_auto_merge_candidate.py"
  "schemas/auto_merge_candidate_schema.md"
  "fixtures/loop_controller/pass_candidate.json"
  "fixtures/loop_controller/reject_candidate.json"
  "fixtures/loop_controller/block_candidate.json"
  "reports/loop/candidates/README.md"
  "operations/ticket_transition_policy.toml"
  "schemas/ticket_transition_schema.md"
  "scripts/loop_advance_ticket.py"
  "scripts/check_ticket_transition_static.py"
  "fixtures/loop_controller/merge_history_ops0006.json"
  "fixtures/loop_controller/merge_history_ops0007.json"
  "reports/loop/ticket_transitions/README.md"
  "scripts/loop_controller_github.sh"
  "scripts/loop_auto_merge_pr.sh"
  "scripts/loop_revert_last_merge.sh"
  "reports/loop/merge_history/README.md"
  "reports/regression/README.md"

  "docs/94_e2e_smoke_loop_verification.md"
  "operations/e2e_smoke_policy.toml"
  ".github/workflows/e2e-smoke-loop.yml"
  "scripts/run_e2e_smoke_loop.sh"
  "scripts/check_e2e_smoke_static.py"
  "reports/e2e_smoke/README.md"
  "docs/95_phase1_gameplay_loop_start.md"
  "docs/history/bootstrap_milestones.md"
  "docs/96_canonical_repository_inventory.md"
  "LICENSE"
  "NOTICE.md"
  "THIRD_PARTY_NOTICES.md"
  "SECURITY.md"
  "docs/97_public_repository_hardening.md"
  "operations/public_repository_policy.toml"
  "scripts/check_public_repository_static.py"
  ".github/dependabot.yml"
  "docs/98_content_root_and_asset_bundle_contract.md"
  "operations/dev_asset_bundle.example.toml"
  "schemas/dev_asset_bundle_schema.md"
  "scripts/fetch_dev_asset_bundle.py"
  "scripts/check_asset_bundle_manifest.py"
  "reports/assets/README.md"
  "docs/99_codex_worker_handoff_contract.md"
  "operations/worker_handoff_policy.toml"
  "schemas/worker_handoff_schema.md"
  "prompts/73_next_ticket_handoff.md"
  "scripts/loop_emit_worker_handoff.py"
  "scripts/check_worker_handoff_static.py"
  ".github/ISSUE_TEMPLATE/codex_ticket.md"
  ".github/workflows/loop-worker-handoff.yml"
  "reports/loop/worker_handoff/README.md"
  "operations/phase1_gameplay_loop_policy.toml"
  "prompts/72_phase1_gameplay_ticket_runner.md"
  "reports/phase1_gameplay_loop/README.md"
  "scripts/render_phase1_gameplay_ticket_prompt.py"
  "scripts/check_phase1_gameplay_start_static.py"
  ".github/workflows/phase1-gameplay-entry.yml"
  "operations/ops_migration_readiness_policy.toml"
  "schemas/ops_migration_readiness_schema.md"
  "scripts/check_ops_migration_readiness.py"
  "fixtures/loop_controller/merge_history_ops0009.json"
  "reports/loop/publication_readiness_report.json"
  "reports/loop/publication_readiness_report.md"
  ".loop/session_logs/GATE-OPS-0000-report.md"
  ".loop/session_logs/GATE-0090-report.md"

)

for path in "${required_files[@]}"; do
  test -f "$path" || { echo "missing: $path" >&2; exit 1; }
done

ready_count=$(rg "^Status: Ready" .loop/tickets || true)
ready_count=$(printf "%s\n" "$ready_count" | sed '/^$/d' | wc -l | tr -d ' ')
ready_ticket=$(rg "^Status: Ready" .loop/tickets || true)

if [ "$ready_count" != "0" ] && [ "$ready_count" != "1" ]; then
  echo "expected zero Ready tickets before Phase1 entry evidence, or exactly TKT-0005 when all entry prerequisites pass; found $ready_count" >&2
  echo "$ready_ticket" >&2
  exit 1
fi

if [ "$ready_count" = "1" ]; then
  echo "$ready_ticket" | rg -q "TKT-0005.md" || {
    echo "expected TKT-0005 to be the only Ready ticket after entry prerequisites pass" >&2
    echo "$ready_ticket" >&2
    exit 1
  }
fi

# Deprecated crate names may appear only in explicit deprecation statements.
suspicious_taiko_core=$(grep -R "taiko_core" docs prompts .loop AGENTS.md operations README.md 2>/dev/null \
  | grep -v "Do not use" \
  | grep -v "Deprecated" \
  | grep -v "deprecated" \
  | grep -v "旧文書" \
  | grep -v "廃止" \
  | grep -v "No stale" \
  || true)
if [ -n "$suspicious_taiko_core" ]; then
  echo "found suspicious taiko_core reference" >&2
  echo "$suspicious_taiko_core" >&2
  exit 1
fi

# These legacy crate names were folded into the canonical crates.
for deprecated in taiko_input taiko_telemetry taiko_app taiko_tools taiko_headless taiko_analyzer; do
  hit=$(grep -R "$deprecated" docs prompts .loop AGENTS.md operations README.md 2>/dev/null || true)
  if [ -n "$hit" ]; then
    echo "found deprecated crate name reference: $deprecated" >&2
    echo "$hit" >&2
    exit 1
  fi
done

scripts/check_reference_integrity.py
scripts/check_autonomy_scorecard.py
scripts/check_rust_workspace_static.py
scripts/check_fixture_validation_static.py
scripts/check_headless_autoplay_static.py
scripts/check_timing_analyzer_static.py
scripts/check_failure_feedback_static.py
scripts/check_qa_regression_static.py
scripts/check_phase1_entry_state_consistency.py
scripts/check_phase1_feature_loop_static.py
scripts/validate_fixture_manifest.py
scripts/validate_synthetic_fixture_structure.py
scripts/validate_no_user_assets.sh
scripts/check_github_pr_orchestration_static.py
scripts/check_github_actions_gate_static.py
scripts/check_rust_preflight_static.py
scripts/check_codex_cloud_env_static.py
scripts/check_loop_controller_static.py
scripts/check_session_separation.py
scripts/check_role_path_policy.py
scripts/check_repair_materialization_static.py
scripts/check_codex_automation_static.py
scripts/check_auto_merge_conditions.py
scripts/check_ticket_transition_static.py
scripts/check_worker_handoff_static.py
scripts/check_public_repository_static.py
scripts/check_asset_bundle_manifest.py --manifest operations/dev_asset_bundle.example.toml
scripts/check_ops_migration_readiness.py --static-only

scripts/check_phase1_gameplay_start_static.py

echo "bootstrap consistency check passed"
