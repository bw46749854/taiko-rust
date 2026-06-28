#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: scripts/loop_merge_and_advance.sh <ticket-id> --pr NUMBER [--base main] [--verdict PATH] [--docs-only] [--dry-run]

Merges a passing ticket PR and prints the next-ticket selection command.
Requires GitHub CLI (`gh`) unless --dry-run is used.
USAGE
}

base_branch="main"
pr_number=""
verdict_path=""
docs_only=0
dry_run=0

if [ "$#" -lt 1 ]; then
  usage >&2
  exit 2
fi

ticket_id="$1"
shift

while [ "$#" -gt 0 ]; do
  case "$1" in
    --base)
      base_branch="${2:?--base requires a value}"
      shift 2
      ;;
    --pr)
      pr_number="${2:?--pr requires a value}"
      shift 2
      ;;
    --verdict)
      verdict_path="${2:?--verdict requires a value}"
      shift 2
      ;;
    --docs-only)
      docs_only=1
      shift
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

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

[ -n "$pr_number" ] || { echo "--pr NUMBER is required" >&2; exit 2; }
[ -f ".loop/tickets/${ticket_id}.md" ] || { echo "missing ticket: ${ticket_id}" >&2; exit 1; }

if [ "$docs_only" -ne 1 ]; then
  [ -n "$verdict_path" ] || { echo "--verdict PATH is required unless --docs-only is set" >&2; exit 2; }
  [ -f "$verdict_path" ] || { echo "missing verdict file: $verdict_path" >&2; exit 1; }
  python3 - "$verdict_path" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, encoding='utf-8') as handle:
    data = json.load(handle)
if data.get('verdict') != 'pass':
    raise SystemExit(f"refusing to merge non-pass verdict: {data.get('verdict')}")
PY
fi

if [ "$dry_run" -eq 1 ]; then
  printf 'ticket_id=%s\npr=%s\nbase_branch=%s\nverdict=%s\ndocs_only=%s\n' "$ticket_id" "$pr_number" "$base_branch" "$verdict_path" "$docs_only"
  printf 'command=gh pr merge %s --squash --delete-branch\n' "$pr_number"
  printf 'next=cargo run -p taiko_cli --bin taiko_cli -- loop next --format json\n'
  exit 0
fi

command -v gh >/dev/null 2>&1 || { echo "gh is required" >&2; exit 1; }

gh pr merge "$pr_number" --squash --delete-branch
git checkout "$base_branch"
git pull --ff-only origin "$base_branch"

if command -v cargo >/dev/null 2>&1; then
  cargo run -p taiko_cli --bin taiko_cli -- loop next --format json
else
  scripts/list_ready_tickets.sh
fi
