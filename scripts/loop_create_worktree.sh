#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: scripts/loop_create_worktree.sh <ticket-id> [--role impl|review|qa|control|test-infra|spec] [--base main] [--branch NAME] [--path PATH] [--dry-run]

Creates a deterministic branch and isolated Git worktree for one ticket and role.
USAGE
}

base_branch="main"
custom_branch=""
custom_path=""
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
    --path)
      custom_path="${2:?--path requires a value}"
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
  control) prefix="control"; default_root="worktrees/control/${ticket_id}" ;;
  test-infra) prefix="test-infra"; default_root="worktrees/test-infra/${ticket_id}" ;;
  review) prefix="review"; default_root="worktrees/review/${ticket_id}" ;;
  qa) prefix="qa"; default_root="worktrees/qa/${ticket_id}" ;;
  spec) prefix="spec"; default_root="worktrees/spec/${ticket_id}" ;;
  impl) prefix="impl"; default_root="worktrees/impl/${ticket_id}" ;;
  *) echo "unknown normalized role: $role" >&2; exit 2 ;;
esac

branch="${custom_branch:-${prefix}/${ticket_id}-${slug}}"
worktree_path="${custom_path:-${default_root}}"

case "$branch" in
  ${prefix}/${ticket_id}-*) ;;
  *) echo "branch must match ${prefix}/${ticket_id}-... for role ${role}: ${branch}" >&2; exit 2 ;;
esac
case "$worktree_path" in
  ${default_root}|${default_root}/*) ;;
  *) echo "worktree path must be under ${default_root} for role ${role}: ${worktree_path}" >&2; exit 2 ;;
esac

if [ -e "$worktree_path" ]; then
  echo "worktree path already exists: ${worktree_path}" >&2
  exit 1
fi

if [ "$dry_run" -eq 1 ]; then
  printf 'ticket_id=%s\nbase_branch=%s\nrole=%s\nbranch=%s\nworktree=%s\n' "$ticket_id" "$base_branch" "$role" "$branch" "$worktree_path"
  printf 'command=git worktree add -b %s %s %s\n' "$branch" "$worktree_path" "$base_branch"
  exit 0
fi

mkdir -p "$(dirname "$worktree_path")"
git worktree add -b "$branch" "$worktree_path" "$base_branch"
printf 'created worktree %s on branch %s from %s for %s as role %s\n' "$worktree_path" "$branch" "$base_branch" "$ticket_id" "$role"
