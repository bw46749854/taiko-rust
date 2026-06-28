#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: scripts/loop_create_branch.sh <ticket-id> [--role impl|review|qa|control|test-infra|spec] [--base main] [--branch NAME] [--dry-run]

Creates a deterministic ticket branch from the base branch.
USAGE
}

base_branch="main"
custom_branch=""
custom_role=""
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
    --branch)
      custom_branch="${2:?--branch requires a value}"
      shift 2
      ;;
    --role)
      custom_role="${2:?--role requires a value}"
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

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

ticket_file=".loop/tickets/${ticket_id}.md"
if [ ! -f "$ticket_file" ]; then
  echo "missing ticket file: $ticket_file" >&2
  exit 1
fi

heading=$(grep -m1 '^# ' "$ticket_file" | sed 's/^# //')
title=$(printf '%s' "$heading" | sed -E 's/^TKT-[0-9A-Z-]+:[[:space:]]*//')
owner=$(grep -m1 '^Owner session:' "$ticket_file" | sed 's/^Owner session:[[:space:]]*//')

slug=$(printf '%s' "$title" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' \
  | cut -c1-64)

normalize_role() {
  case "$1" in
    impl|implementation|"Ticket Implementation Session") echo "impl" ;;
    review|design|"Design Review Session") echo "review" ;;
    qa|regression|"QA / Regression Session") echo "qa" ;;
    control|loop|"Control Session") echo "control" ;;
    test|test-infra|"Test Infra Session"|"Test Infrastructure Session") echo "test-infra" ;;
    spec|"Spec Extraction Session") echo "spec" ;;
    *)
      case "$1" in
        *"Control Session"*) echo "control" ;;
        *"Spec"*) echo "spec" ;;
        *"Design"*|*"Review"*) echo "review" ;;
        *"Test Infra"*|*"Test Infrastructure"*) echo "test-infra" ;;
        *"QA"*|*"Regression"*) echo "qa" ;;
        *) echo "impl" ;;
      esac
      ;;
  esac
}

role="$(normalize_role "${custom_role:-$owner}")"

case "$role" in
  control) prefix="loop" ;;
  test-infra) prefix="test" ;;
  review) prefix="review" ;;
  qa) prefix="qa" ;;
  spec) prefix="spec" ;;
  impl) prefix="impl" ;;
  *) echo "unknown normalized role: $role" >&2; exit 2 ;;
esac

branch="${custom_branch:-${prefix}/${ticket_id}-${slug}}"

if git rev-parse --git-dir >/dev/null 2>&1; then
  if git show-ref --verify --quiet "refs/heads/${branch}"; then
    echo "branch already exists: ${branch}" >&2
    exit 1
  fi
fi

if [ "$dry_run" -eq 1 ]; then
  printf 'ticket_id=%s\nbase_branch=%s\nrole=%s\nbranch=%s\n' "$ticket_id" "$base_branch" "$role" "$branch"
  printf 'command=git checkout -b %s %s\n' "$branch" "$base_branch"
  exit 0
fi

git checkout "$base_branch"
git checkout -b "$branch"
printf 'created branch %s from %s for %s as role %s\n' "$branch" "$base_branch" "$ticket_id" "$role"
