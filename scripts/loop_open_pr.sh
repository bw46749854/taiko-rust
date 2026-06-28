#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: scripts/loop_open_pr.sh <ticket-id> [--base main] [--branch NAME] [--draft] [--dry-run]

Pushes the current or specified ticket branch and opens a GitHub pull request with the loop template.
Requires GitHub CLI (`gh`) unless --dry-run is used.
USAGE
}

base_branch="main"
branch=""
draft_flag=""
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
      branch="${2:?--branch requires a value}"
      shift 2
      ;;
    --draft)
      draft_flag="--draft"
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

ticket_file=".loop/tickets/${ticket_id}.md"
if [ ! -f "$ticket_file" ]; then
  echo "missing ticket file: $ticket_file" >&2
  exit 1
fi

if [ -z "$branch" ]; then
  branch=$(git rev-parse --abbrev-ref HEAD)
fi

if [ "$branch" = "$base_branch" ] || [ "$branch" = "main" ]; then
  echo "refusing to open PR from base/main branch: ${branch}" >&2
  exit 1
fi

heading=$(grep -m1 '^# ' "$ticket_file" | sed 's/^# //')
status=$(grep -m1 '^Status:' "$ticket_file" | sed 's/^Status:[[:space:]]*//')
owner=$(grep -m1 '^Owner session:' "$ticket_file" | sed 's/^Owner session:[[:space:]]*//')
reviewer=$(grep -m1 '^Review session:' "$ticket_file" | sed 's/^Review session:[[:space:]]*//')
worktree=$(grep -m1 '^Worktree:' "$ticket_file" | sed -E 's/^Worktree:[[:space:]]*`?([^`]+)`?.*/\1/')

body_file=$(mktemp)
cat > "$body_file" <<BODY
## Ticket

- Ticket ID: ${ticket_id}
- Ticket file: \`${ticket_file}\`
- Owner session: ${owner}
- Review session: ${reviewer}
- Branch: \`${branch}\`
- Worktree: \`${worktree}\`
- Starting ticket status: ${status}

## Scope

See \`${ticket_file}\`.

## Required checks

Copy the command evidence from the ticket and from the implementation session command log before marking this PR ready for review.

## Evidence

- Plan:
- Plan review:
- Command log:
- QA verdict JSON:
- Gate report / session log:
- Session metadata:

## QA transition

- Verdict: block until QA / Regression Session records pass/reject/block JSON
- Verdict source:
- Next-ticket transition:

## Asset policy

- [ ] No commercial song, audio, image, video, skin, or chart asset was committed.
- [ ] User-selected song validation uses local manifest paths only.
- [ ] \`scripts/validate_no_user_assets.sh\` passed or is not relevant to this docs-only PR.

## Self-approval prevention

- [ ] Implementation Session is not the same as Design Review Session.
- [ ] Implementation Session is not the same as QA / Regression Session.
- [ ] Review/QA evidence is recorded in text or JSON.

## Codex review

- [ ] Native \`@codex review\` requested, automatic Codex review enabled, or \`.github/workflows/codex-review.yml\` run manually.
BODY

if [ "$dry_run" -eq 1 ]; then
  printf 'ticket_id=%s\nbase_branch=%s\nbranch=%s\ntitle=%s\nbody_file=%s\n' "$ticket_id" "$base_branch" "$branch" "$heading" "$body_file"
  cat "$body_file"
  exit 0
fi

command -v gh >/dev/null 2>&1 || { echo "gh is required" >&2; exit 1; }

git push -u origin "$branch"
gh pr create --base "$base_branch" --head "$branch" --title "${ticket_id}: ${heading#${ticket_id}: }" --body-file "$body_file" $draft_flag
