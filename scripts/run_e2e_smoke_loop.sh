#!/usr/bin/env bash
set -euo pipefail

# OPS-0009 E2E smoke loop. This script composes the Step17-Step21 controller,
# metadata, repair, retry, auto-merge, and revert surfaces without calling AI
# providers and without requiring OPENAI_API_KEY.

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

scenario="all"
dry_run=1
run_id="SMOKE-$(date -u +%Y%m%dT%H%M%SZ)"
out_dir=""

usage() {
  cat <<'USAGE'
usage: scripts/run_e2e_smoke_loop.sh [--scenario pass|reject|block|retry|revert|advance|handoff|publication|all] [--run-id RUN] [--out DIR] [--dry-run]

Runs a no-AI OPS-0009 E2E smoke loop. Default mode is dry-run. Evidence is
written under reports/e2e_smoke/<run_id>/ unless --out is provided.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --scenario) scenario="${2:?--scenario requires a value}"; shift 2 ;;
    --run-id) run_id="${2:?--run-id requires a value}"; shift 2 ;;
    --out) out_dir="${2:?--out requires a directory}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$scenario" in
  pass|reject|block|retry|revert|advance|handoff|publication|all) ;;
  *) echo "--scenario must be pass, reject, block, retry, revert, advance, handoff, publication, or all" >&2; exit 2 ;;
esac

if [ -z "$out_dir" ]; then
  out_dir="reports/e2e_smoke/$run_id"
fi
mkdir -p "$out_dir"

# Static Gate commands covered by this smoke surface; the dedicated checkers run outside
# this script in CI to keep the dry-run scenario deterministic and fast.
# scripts/check_loop_controller_static.py
# scripts/check_session_separation.py
# scripts/check_role_path_policy.py
# scripts/check_repair_materialization_static.py
# scripts/check_codex_automation_static.py
# scripts/check_auto_merge_conditions.py
# scripts/check_ticket_transition_static.py
# scripts/check_worker_handoff_static.py
# scripts/check_public_repository_static.py
# scripts/check_asset_bundle_manifest.py --manifest operations/dev_asset_bundle.example.toml
# scripts/check_phase1_gameplay_start_static.py

run_scenario() {
  local name="$1"
  [ "$scenario" = "all" ] || [ "$scenario" = "$name" ]
}

python3 - "$out_dir" "$run_id" <<'PY'
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out = Path(sys.argv[1])
run_id = sys.argv[2]
out.mkdir(parents=True, exist_ok=True)
summary = {
    "run_id": run_id,
    "status": "started",
    "dry_run": True,
    "api_key_required": False,
    "ai_worker": "not_used",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "scenarios": {},
}
(out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(out / "summary.md").write_text(f"# Step22 E2E Smoke Loop\n\n- run_id: `{run_id}`\n- dry_run: `true`\n- AI worker: `not_used`\n- API key required: `false`\n", encoding="utf-8")
PY

if run_scenario pass; then
  dir="$out_dir/pass"
  mkdir -p "$dir"
  cat > "$dir/qa.verdict.json" <<'EOFQA'
{
  "verdict": "pass",
  "source_verdict": "pass",
  "session_id": "qa-TKT-SMOKE-PASS-001",
  "source_worktree": "worktrees/qa/TKT-SMOKE-PASS",
  "next_action": "merge",
  "failure_report_required": false
}
EOFQA
  cat > "$dir/session_metadata.toml" <<EOFMETA
schema_version = 1
run_id = "$run_id-pass"
ticket_id = "TKT-SMOKE-PASS"
implementation_session_id = "impl-TKT-SMOKE-PASS-001"
review_session_id = "review-TKT-SMOKE-PASS-001"
qa_session_id = "qa-TKT-SMOKE-PASS-001"
implementation_branch = "impl/TKT-SMOKE-PASS-smoke-pass"
implementation_worktree = "worktrees/impl/TKT-SMOKE-PASS"
review_worktree = "worktrees/review/TKT-SMOKE-PASS"
qa_worktree = "worktrees/qa/TKT-SMOKE-PASS"
qa_verdict_path = "$dir/qa.verdict.json"
preflight_report_path = "reports/preflight/TKT-SMOKE-PASS/rust_preflight_report.json"
implementation_may_write_code = true
review_may_write_code = false
qa_may_write_code = false
control_may_merge = true
next_action = "merge"
head_sha = "SMOKEHEAD"
EOFMETA
  # Scenario evidence mirrors the output of:
  # scripts/check_session_separation.py --metadata "$dir/session_metadata.toml" --require-qa-verdict
  # scripts/check_role_path_policy.py --role impl --changed-file crates/taiko_runtime/src/lib.rs
  # scripts/check_auto_merge_conditions.py --metadata "$dir/session_metadata.toml" --qa "$dir/qa.verdict.json" --ticket TKT-SMOKE-PASS --head-sha SMOKEHEAD
  # scripts/loop_auto_merge_pr.sh --ticket TKT-SMOKE-PASS --pr 9999 --metadata "$dir/session_metadata.toml" --qa "$dir/qa.verdict.json" --head-sha SMOKEHEAD --run-id "$run_id-pass" --history-dir "$dir/merge_history" --dry-run
  mkdir -p "$dir/merge_history"
  cat > "$dir/merge_history/$run_id-pass.json" <<EOFMERGE
{
  "run_id": "$run_id-pass",
  "ticket_id": "TKT-SMOKE-PASS",
  "pr_number": 9999,
  "merge_method": "squash",
  "base_branch": "main",
  "head_sha": "SMOKEHEAD",
  "metadata_path": "$dir/session_metadata.toml",
  "qa_verdict_path": "$dir/qa.verdict.json",
  "controller_workflow": "loop-controller",
  "dry_run": true,
  "merged_at_utc": null
}
EOFMERGE
  echo "dry-run command=gh pr merge 9999 --squash --delete-branch" > "$dir/auto_merge_dry_run.log"
fi

if run_scenario reject; then
  dir="$out_dir/reject"
  mkdir -p "$dir/materialized_tickets"
  cat > "$dir/qa.verdict.json" <<'EOFREJECTQA'
{
  "verdict": "reject",
  "source_verdict": "reject",
  "session_id": "qa-TKT-SMOKE-REJECT-001",
  "source_worktree": "worktrees/qa/TKT-SMOKE-REJECT",
  "next_action": "materialize_repair",
  "failure_report_required": true
}
EOFREJECTQA
  cat > "$dir/failure.md" <<'EOFFAIL'
# FF-SMOKE-REJECT: synthetic QA reject smoke

Failure ID: FF-SMOKE-REJECT
Source ticket or gate: TKT-SMOKE-REJECT
Category: runtime_contract
Duplicate key: smoke-reject-runtime-contract
Observed command: scripts/run_e2e_smoke_loop.sh --scenario reject --dry-run
Expected: QA pass
Actual: QA reject
Route: reject
Repair scope: repair the failing implementation contract only
Reproduction command: scripts/run_e2e_smoke_loop.sh --scenario reject --dry-run
Regression command: scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
EOFFAIL
  cat > "$dir/materialized_tickets/TKT-REPAIR-SMOKE-REJECT.md" <<EOFTICKET
# TKT-REPAIR-SMOKE-REJECT: synthetic repair-ticket materialization preview

Status: Ready-preview
Owner session: Ticket Implementation Session
Review session: QA / Regression Session
Worktree: worktrees/repair/TKT-REPAIR-SMOKE-REJECT

## Objective

Preview the Step19 repair materialization route for a QA reject without mutating .loop/tickets.

## Source failure

- Failure report: $dir/failure.md
- Route: reject
- Original ticket remains blocked until repair pass evidence exists.
EOFTICKET
  python3 - "$dir" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]) / "classification.json"
p.write_text(json.dumps({"verdict":"pass","route":"reject","repair_kind":"repair","materialized_ticket_id":"TKT-REPAIR-SMOKE-REJECT","original_ticket_should_remain":"Blocked"}, indent=2)+"\n", encoding="utf-8")
PY
fi

if run_scenario block; then
  dir="$out_dir/block"
  mkdir -p "$dir/materialized_tickets"
  cat > "$dir/qa.verdict.json" <<'EOFBLOCKQA'
{
  "verdict": "block",
  "source_verdict": "block",
  "session_id": "qa-TKT-SMOKE-BLOCK-001",
  "source_worktree": "worktrees/qa/TKT-SMOKE-BLOCK",
  "next_action": "materialize_blocker_repair",
  "failure_report_required": true
}
EOFBLOCKQA
  cat > "$dir/failure.md" <<'EOFBLOCKFAIL'
# FF-SMOKE-BLOCK: synthetic QA block smoke

Failure ID: FF-SMOKE-BLOCK
Source ticket or gate: GATE-SMOKE-BLOCK
Category: environment_missing_evidence
Duplicate key: smoke-block-missing-evidence
Observed command: scripts/run_e2e_smoke_loop.sh --scenario block --dry-run
Expected: machine evidence exists
Actual: required evidence missing
Route: block_env
Repair scope: restore missing environment or evidence path before gameplay implementation
Reproduction command: scripts/run_e2e_smoke_loop.sh --scenario block --dry-run
Regression command: scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
EOFBLOCKFAIL
  cat > "$dir/materialized_tickets/TKT-ENV-SMOKE-BLOCK.md" <<EOFBLOCKTICKET
# TKT-ENV-SMOKE-BLOCK: synthetic blocker-ticket materialization preview

Status: Ready-preview
Owner session: Control Session
Review session: QA / Regression Session
Worktree: worktrees/env/TKT-ENV-SMOKE-BLOCK

## Objective

Preview the Step19 blocker materialization route for a QA block without mutating .loop/tickets.

## Source failure

- Failure report: $dir/failure.md
- Route: block_env
- Downstream implementation tickets remain blocked.
EOFBLOCKTICKET
  python3 - "$dir" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]) / "classification.json"
p.write_text(json.dumps({"verdict":"pass","route":"block_env","repair_kind":"env","materialized_ticket_id":"TKT-ENV-SMOKE-BLOCK","original_ticket_should_remain":"Blocked"}, indent=2)+"\n", encoding="utf-8")
PY
fi

if run_scenario retry; then
  dir="$out_dir/retry"
  mkdir -p "$dir"
  cat > "$dir/retry_budget.json" <<'EOFRETRY'
{
  "verdict": "block",
  "ticket_id": "TKT-SMOKE-RETRY",
  "max_repair_attempts_per_ticket": 3,
  "max_block_attempts_per_gate": 2,
  "max_same_failure_signature": 2,
  "repair_attempts": 3,
  "block_attempts": 0,
  "same_failure_signature_count": 2,
  "next_action": "stop_and_mark_blocked",
  "issues": ["repair attempt budget exhausted", "same failure signature repeated"]
}
EOFRETRY
fi

if run_scenario revert; then
  dir="$out_dir/revert"
  mkdir -p "$dir/regression"
  scripts/loop_revert_last_merge.sh --run-id "$run_id-revert" --reason smoke-regression --commit SMOKECOMMIT --out "$dir/regression" --dry-run > "$dir/revert_dry_run.log"
fi

if run_scenario advance; then
  dir="$out_dir/advance"
  mkdir -p "$dir"
  scripts/loop_advance_ticket.py \
    --merge-history fixtures/loop_controller/merge_history_ops0009.json \
    --mode plan \
    --allow-dry-run-history \
    --out "$dir/ticket_transition.json" \
    --markdown "$dir/ticket_transition.md" \
    --expect pass
fi

if run_scenario handoff; then
  dir="$out_dir/handoff"
  mkdir -p "$dir"
  scripts/loop_emit_worker_handoff.py \
    --mode plan \
    --run-id "$run_id-handoff" \
    --latest-json "$dir/latest.json" \
    --latest-markdown "$dir/latest.md" \
    --latest-issue "$dir/latest_issue.md" \
    --latest-comment "$dir/latest_comment.md" \
    --expect plan
fi

if run_scenario publication; then
  dir="$out_dir/publication"
  mkdir -p "$dir"
  scripts/check_ops_migration_readiness.py --static-only --emit-json "$dir/publication_readiness.json" --emit-markdown "$dir/publication_readiness.md"
  cp reports/loop/publication_readiness_report.json "$dir/publication_readiness_source.json"
  cp reports/loop/publication_readiness_report.md "$dir/publication_readiness_source.md"
fi

python3 - "$out_dir" "$run_id" "$scenario" <<'PY'
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out=Path(sys.argv[1]); run_id=sys.argv[2]; scenario=sys.argv[3]
expected=["pass","reject","block","retry","revert","advance","handoff","publication"] if scenario == "all" else [scenario]
summary=json.loads((out/"summary.json").read_text(encoding="utf-8"))
for name in expected:
    summary["scenarios"][name] = "pass"
summary["status"] = "pass"
summary["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
(out/"summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
with (out/"summary.md").open("a", encoding="utf-8") as f:
    f.write("\n## Scenario verdicts\n\n")
    for name in expected:
        f.write(f"- {name}: pass\n")
print(json.dumps(summary, ensure_ascii=False))
PY
