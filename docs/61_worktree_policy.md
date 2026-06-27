# 61. Worktree Policy

Status: canonical

## Purpose

Each session operates in a separate Git worktree. This prevents a single Codex thread from implementing, reviewing, and approving its own changes.

## Required worktrees

```text
worktrees/control
worktrees/spec
worktrees/review
worktrees/test-infra
worktrees/qa
worktrees/impl/TKT-0000
worktrees/impl/TKT-0001
...
```

## Branch naming

| Work type | Branch pattern |
|---|---|
| Gate repair | `loop/TKT-0000-spec-repair` |
| Ticket implementation | `impl/<ticket-id>-<slug>` |
| Fixture/analyzer | `test/<ticket-id>-<slug>` |
| Review-only docs | `review/<gate-or-ticket>` |

## Rules

- One ticket per implementation branch.
- No ticket implementation in `main`.
- No review edits in implementation worktree except explicit review notes committed separately.
- No user-selected song assets committed from any worktree.
- Generated reports may be committed only when they are text/JSON summaries without copyrighted asset payloads.

## Cleanup

A completed ticket worktree can be removed after:

- PR is merged or explicitly abandoned.
- command log and QA report are preserved.
- remaining risks are transferred to follow-up tickets.


## Step14 executable orchestration

`docs/84_github_pr_loop_contract.md` is the authoritative GitHub branch/worktree/PR contract. The worktree policy is now enforced by:

```bash
scripts/loop_create_branch.sh <ticket-id> --dry-run
scripts/loop_create_worktree.sh <ticket-id> --dry-run
scripts/loop_open_pr.sh <ticket-id> --dry-run
scripts/check_github_pr_orchestration_static.py
```

`worktrees/` is ignored by Git. Any evidence produced inside a worktree must be copied to tracked text or JSON files before PR creation.


## Step18 role-specific worktree commands

The worktree script now accepts an explicit role:

```bash
scripts/loop_create_worktree.sh TKT-0005 --role impl --dry-run
scripts/loop_create_worktree.sh TKT-0005 --role review --dry-run
scripts/loop_create_worktree.sh TKT-0005 --role qa --dry-run
scripts/loop_create_worktree.sh TKT-0050 --role test-infra --dry-run
```

Canonical role roots are:

```text
worktrees/impl/<ticket-id>
worktrees/review/<ticket-id>
worktrees/qa/<ticket-id>
worktrees/control/<ticket-id>
worktrees/test-infra/<ticket-id>
worktrees/spec/<ticket-id>
```

`Test Infrastructure Session` and `Test Infra Session` are normalized to `test-infra` to remove the Step16/17 branch/worktree mismatch.
