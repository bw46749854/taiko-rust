#!/usr/bin/env bash
set -euo pipefail

# GitHub loop-controller. OPENAI_API_KEY is intentionally unused: GitHub
# GitHub Actions only gates, discovers candidates, merges, advances, emits worker handoff artifacts, and records evidence.

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

mode="plan"
dry_run=0
out_dir="reports/loop/github-controller"
pr_json=""

usage() {
  cat <<'USAGE'
usage: scripts/loop_controller_github.sh [--mode plan|apply] [--out DIR] [--pr-json PATH] [--dry-run]

Plans or applies the GitHub Actions auto-merge controller step. This script does
not call AI providers. It discovers open PR candidates using gh when available,
or a supplied --pr-json fixture/path, and writes controller evidence under
reports/loop/github-controller/ and reports/loop/candidates/.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      mode="${2:?--mode requires plan or apply}"
      shift 2
      ;;
    --out)
      out_dir="${2:?--out requires a directory}"
      shift 2
      ;;
    --pr-json)
      pr_json="${2:?--pr-json requires a path}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$mode" != "plan" ] && [ "$mode" != "apply" ]; then
  echo "--mode must be plan or apply" >&2
  exit 2
fi

scripts/check_auto_merge_conditions.py
mkdir -p "$out_dir" reports/loop/candidates reports/loop/merge_history reports/loop/ticket_transitions reports/loop/worker_handoff
run_id="${GITHUB_RUN_ID:-LOCAL}-$(date -u +%Y%m%dT%H%M%SZ)"
plan_json="$out_dir/controller_github_plan.json"
plan_md="$out_dir/controller_github_plan.md"
open_prs_json="reports/loop/candidates/open_prs.json"
candidate_json="reports/loop/candidates/candidate_plan.json"
candidate_md="reports/loop/candidates/candidate_plan.md"
transition_json="reports/loop/ticket_transitions/${run_id}.json"
transition_md="reports/loop/ticket_transitions/${run_id}.md"

if [ -n "$pr_json" ]; then
  cp "$pr_json" "$open_prs_json"
elif command -v gh >/dev/null 2>&1 && [ -n "${GITHUB_REPOSITORY:-}" ]; then
  gh pr list --state open --json number,title,body,baseRefName,headRefName,headRefOid,isDraft,labels,statusCheckRollup > "$open_prs_json"
else
  printf '[]\n' > "$open_prs_json"
fi

scripts/select_auto_merge_candidate.py --input "$open_prs_json" --out "$candidate_json" --markdown "$candidate_md"

python3 - "$run_id" "$mode" "$dry_run" "$plan_json" "$plan_md" "$candidate_json" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path

run_id, mode, dry_run, json_path, md_path, candidate_path = sys.argv[1:7]
candidate = json.loads(Path(candidate_path).read_text(encoding="utf-8"))
selected = candidate.get("selected_pr")
status = "planned"
if mode == "apply" and dry_run != "1" and candidate.get("verdict") == "pass":
    status = "apply-ready"
elif candidate.get("verdict") in {"block", "reject"}:
    status = candidate.get("verdict")

plan = {
    "controller": "loop-controller",
    "status": status,
    "run_id": run_id,
    "mode": mode,
    "dry_run": dry_run == "1",
    "ai_worker": "not_used",
    "api_key_required": False,
    "candidate_plan": candidate_path,
    "candidate_verdict": candidate.get("verdict"),
    "selected_pr_number": selected.get("number") if selected else None,
    "required_label": candidate.get("required_label"),
    "merge_method": "squash",
    "max_merge_candidates_per_run": candidate.get("max_merge_candidates_per_run"),
    "next_action": "merge_selected_candidate" if selected else "wait_or_repair_candidate_evidence",
    "evidence": [
        "scripts/select_auto_merge_candidate.py",
        "reports/loop/candidates/candidate_plan.json",
        "reports/loop/merge_history/<run_id>.json",
        "reports/loop/ticket_transitions/<run_id>.json",
        "reports/regression/<run_id>.json",
    ],
}
Path(json_path).write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
Path(md_path).write_text(
    "# GitHub Loop Controller Plan\n\n"
    f"- run_id: `{run_id}`\n"
    f"- mode: `{mode}`\n"
    f"- dry_run: `{dry_run == '1'}`\n"
    "- AI worker: not used\n"
    "- API key required: false\n"
    f"- candidate verdict: `{candidate.get('verdict')}`\n"
    f"- selected PR: `{selected.get('number') if selected else 'none'}`\n"
    f"- next_action: `{plan['next_action']}`\n",
    encoding="utf-8",
)
print(json.dumps(plan, ensure_ascii=False))
PY

candidate_verdict="$(python3 -c 'import json; print(json.load(open("reports/loop/candidates/candidate_plan.json", encoding="utf-8"))["verdict"])')"
if [ "$mode" = "apply" ] && [ "$dry_run" -ne 1 ] && [ "$candidate_verdict" = "pass" ]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh is required for apply mode in GitHub controller" >&2
    exit 1
  fi
  mapfile -t selected < <(python3 - <<'PY'
import json
p=json.load(open("reports/loop/candidates/candidate_plan.json", encoding="utf-8"))["selected_pr"]
print(p["ticket_id"])
print(p["number"])
print(p["metadata_path"])
print(p["qa_verdict_path"])
print(p["headRefOid"])
PY
)
  scripts/loop_auto_merge_pr.sh \
    --ticket "${selected[0]}" \
    --pr "${selected[1]}" \
    --metadata "${selected[2]}" \
    --qa "${selected[3]}" \
    --head-sha "${selected[4]}" \
    --run-id "$run_id"
  scripts/loop_advance_ticket.py \
    --merge-history "reports/loop/merge_history/${run_id}.json" \
    --mode apply \
    --out "$transition_json" \
    --markdown "$transition_md" \
    --expect pass

  scripts/loop_emit_worker_handoff.py \
    --mode controller \
    --run-id "$run_id" \
    --expect plan
else
  scripts/loop_emit_worker_handoff.py \
    --mode controller \
    --run-id "$run_id" \
    --expect plan || true
  echo "controller did not merge: mode=$mode dry_run=$dry_run candidate_verdict=$candidate_verdict"
fi
