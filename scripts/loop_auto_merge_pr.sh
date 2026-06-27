#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

usage() {
  cat <<'USAGE'
usage: scripts/loop_auto_merge_pr.sh --ticket TICKET --pr NUMBER --metadata PATH --qa PATH [--base main] [--head-sha SHA] [--run-id RUN] [--history-dir DIR] [--dry-run]

Validates auto-merge conditions, records merge history, and merges the PR with
squash merge when not in dry-run mode. Requires gh unless --dry-run is used.
GitHub Actions is a verifier/gate/controller only; this script does not call AI providers.
USAGE
}

ticket=""
pr=""
metadata=""
qa=""
base="main"
head_sha=""
run_id="RUN-$(date -u +%Y%m%dT%H%M%SZ)"
dry_run=0
history_dir="reports/loop/merge_history"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --ticket) ticket="${2:?--ticket requires value}"; shift 2 ;;
    --pr) pr="${2:?--pr requires value}"; shift 2 ;;
    --metadata) metadata="${2:?--metadata requires value}"; shift 2 ;;
    --qa) qa="${2:?--qa requires value}"; shift 2 ;;
    --base) base="${2:?--base requires value}"; shift 2 ;;
    --head-sha) head_sha="${2:?--head-sha requires value}"; shift 2 ;;
    --run-id) run_id="${2:?--run-id requires value}"; shift 2 ;;
    --history-dir) history_dir="${2:?--history-dir requires value}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -n "$ticket" ] || { echo "--ticket is required" >&2; exit 2; }
[ -n "$pr" ] || { echo "--pr is required" >&2; exit 2; }
[ -n "$metadata" ] || { echo "--metadata is required" >&2; exit 2; }
[ -n "$qa" ] || { echo "--qa is required" >&2; exit 2; }

args=(--metadata "$metadata" --qa "$qa" --ticket "$ticket")
if [ -n "$head_sha" ]; then args+=(--head-sha "$head_sha"); fi
scripts/check_auto_merge_conditions.py "${args[@]}"

mkdir -p "$history_dir"
history="$history_dir/${run_id}.json"

write_history() {
  local merged_at="$1"
  python3 - "$history" "$run_id" "$ticket" "$pr" "$base" "$metadata" "$qa" "$head_sha" "$dry_run" "$merged_at" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path
path, run_id, ticket, pr, base, metadata, qa, head_sha, dry, merged_at = sys.argv[1:11]
record = {
    "run_id": run_id,
    "ticket_id": ticket,
    "pr_number": int(pr),
    "merge_method": "squash",
    "base_branch": base,
    "head_sha": head_sha or None,
    "metadata_path": metadata,
    "qa_verdict_path": qa,
    "controller_workflow": "loop-controller",
    "dry_run": dry == "1",
    "merged_at_utc": None if merged_at == "" else merged_at,
}
Path(path).write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False))
PY
}

if [ "$dry_run" -eq 1 ]; then
  write_history ""
  printf 'dry-run command=gh pr merge %s --squash --delete-branch\n' "$pr"
  exit 0
fi

command -v gh >/dev/null 2>&1 || { echo "gh is required" >&2; exit 1; }
gh pr merge "$pr" --squash --delete-branch
merged_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
write_history "$merged_at"
