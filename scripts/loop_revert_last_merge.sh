#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

usage() {
  cat <<'USAGE'
usage: scripts/loop_revert_last_merge.sh --run-id RUN --reason TEXT [--commit SHA] [--out DIR] [--dry-run]

Creates regression evidence and, outside dry-run, creates a revert branch and PR.
USAGE
}

run_id=""
reason=""
commit=""
dry_run=0
out_dir="reports/regression"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-id) run_id="${2:?--run-id requires value}"; shift 2 ;;
    --reason) reason="${2:?--reason requires value}"; shift 2 ;;
    --commit) commit="${2:?--commit requires value}"; shift 2 ;;
    --out) out_dir="${2:?--out requires value}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -n "$run_id" ] || { echo "--run-id is required" >&2; exit 2; }
[ -n "$reason" ] || { echo "--reason is required" >&2; exit 2; }

mkdir -p "$out_dir"
report="$out_dir/${run_id}.json"
python3 - "$report" "$run_id" "$reason" "$commit" "$dry_run" <<'PY'
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
path, run_id, reason, commit, dry = sys.argv[1:6]
report = {
    "run_id": run_id,
    "verdict": "regression",
    "reason": reason,
    "target_commit": commit or None,
    "requested_action": "revert_pr",
    "dry_run": dry == "1",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
}
Path(path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
PY

branch="revert/${run_id}"
if [ "$dry_run" -eq 1 ]; then
  printf 'dry-run branch=%s\n' "$branch"
  printf 'dry-run command=git revert %s\n' "${commit:-<merge_commit>}"
  printf 'dry-run command=gh pr create --title "Revert autonomous merge %s" --body-file %s\n' "$run_id" "$report"
  exit 0
fi

[ -n "$commit" ] || { echo "--commit is required without --dry-run" >&2; exit 2; }
command -v gh >/dev/null 2>&1 || { echo "gh is required" >&2; exit 1; }

git checkout -b "$branch"
git revert --no-edit "$commit"
git add "$report"
git commit -m "revert: autonomous merge ${run_id}"
git push -u origin "$branch"
gh pr create --title "Revert autonomous merge ${run_id}" --body-file "$report"
