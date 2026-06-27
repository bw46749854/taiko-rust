#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mode="runtime"
out="reports/preflight/latest"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --static-only)
      mode="static"
      shift
      ;;
    --out)
      out="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'HELP'
Usage: scripts/ci_local_equivalent.sh [--static-only] [--out <preflight-output-dir>]

Runs the same validation families expected in CI/Codex Cloud.

Default mode requires Rust and runs the Step15 runtime preflight.
--static-only runs only Python/Bash static checks and does not require Rust.
HELP
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

run() {
  printf '\n==> %s\n' "$*"
  "$@"
}

run scripts/check_reference_integrity.py
run scripts/check_autonomy_scorecard.py
run scripts/check_rust_workspace_static.py
run scripts/check_fixture_validation_static.py
run scripts/check_headless_autoplay_static.py
run scripts/check_timing_analyzer_static.py
run scripts/check_failure_feedback_static.py
run scripts/check_qa_regression_static.py
run scripts/check_phase1_feature_loop_static.py
run scripts/check_github_pr_orchestration_static.py
run scripts/check_github_actions_gate_static.py
run scripts/check_rust_preflight_static.py
run scripts/check_codex_cloud_env_static.py
run scripts/check_loop_controller_static.py
run scripts/check_session_separation.py
run scripts/check_role_path_policy.py
run scripts/check_repair_materialization_static.py
run scripts/check_codex_automation_static.py
run scripts/check_auto_merge_conditions.py
run scripts/check_ticket_transition_static.py
run scripts/check_worker_handoff_static.py
run scripts/check_ops_migration_readiness.py --static-only
run scripts/select_auto_merge_candidate.py --input fixtures/loop_controller/pass_candidate.json --out reports/loop/candidates/pass_candidate_plan.json --markdown reports/loop/candidates/pass_candidate_plan.md --expect pass
run scripts/select_auto_merge_candidate.py --input fixtures/loop_controller/reject_candidate.json --out reports/loop/candidates/reject_candidate_plan.json --expect reject
run scripts/select_auto_merge_candidate.py --input fixtures/loop_controller/block_candidate.json --out reports/loop/candidates/block_candidate_plan.json --expect block
run scripts/loop_advance_ticket.py --merge-history fixtures/loop_controller/merge_history_ops0007.json --mode plan --allow-dry-run-history --out reports/loop/ticket_transitions/ops0007_to_ops0008_plan.json --markdown reports/loop/ticket_transitions/ops0007_to_ops0008_plan.md --expect pass
run scripts/loop_advance_ticket.py --merge-history fixtures/loop_controller/merge_history_ops0009.json --mode plan --allow-dry-run-history --out reports/loop/ticket_transitions/ops0009_to_tkt0005_plan.json --markdown reports/loop/ticket_transitions/ops0009_to_tkt0005_plan.md --expect pass
run scripts/loop_emit_worker_handoff.py --mode plan --run-id RUN-HANDOFF-CI --expect plan
run scripts/check_public_repository_static.py
run scripts/check_asset_bundle_manifest.py --manifest operations/dev_asset_bundle.example.toml
run scripts/fetch_dev_asset_bundle.py --manifest operations/dev_asset_bundle.example.toml --dry-run --emit-json reports/assets/asset_bundle_fetch_dry_run.json
run scripts/check_e2e_smoke_static.py --static-only
run scripts/check_phase1_gameplay_start_static.py
run scripts/validate_fixture_manifest.py
run scripts/validate_synthetic_fixture_structure.py
run scripts/validate_no_user_assets.sh

if [ "$mode" = "static" ]; then
  printf '\nstatic-only validation passed\n'
  exit 0
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo is required for runtime mode; run scripts/codex_cloud_setup.sh first or use --static-only" >&2
  exit 1
fi

run scripts/run_rust_preflight.sh --scope current-package --out "$out"
run scripts/check_runtime_evidence_files.py --path "$out/rust_preflight_report.json" --require-scope current-package --require-pass

printf '\nCI local equivalent passed\n'
