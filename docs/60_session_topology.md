# 60. Session Topology

Status: canonical

## Purpose

The loop uses multiple Codex sessions and separate Git worktrees to reduce self-approval. The topology below is mandatory for Phase1.

## Sessions

| Session | Worktree | Primary outputs | Cannot approve |
|---|---|---|---|
| Control Session | `worktrees/control` | selected ticket, gate report, loop summary | its own gate changes |
| Spec Extraction Session | `worktrees/spec` | `research/opentaiko/*.md`, adoption decisions | implementation |
| Design Review Session | `worktrees/review` | plan review, design review, final review | its own implementation |
| Test Infra Session | `worktrees/test-infra` | fixtures, schemas, analyzer tests, CI commands | its own fixture acceptance |
| Ticket Implementation Session | `worktrees/impl/<ticket-id>` | code and docs for one ticket | acceptance of the same ticket |
| QA / Regression Session | `worktrees/qa` | regression report, fixture report, user-song validation report | implementation |

## Additional reviewer roles

| Role | Used by | Responsibility |
|---|---|---|
| Compatibility Reviewer | `GATE-0000` | Checks Phase1 scope, classification, adoption decisions |
| Coverage Reviewer | `GATE-0010` | Checks fixture and user-song traceability |
| Implementation Reviewer | Ticket final review | Checks diff, commands, fixture/analyzer evidence |

## Required separation

- Implementation and review must use different worktrees.
- A session that edits a file cannot be the only reviewer of that file.
- Control Session may coordinate but cannot mark a failed check as pass.
- QA Session may fail a ticket without asking the implementation session for approval.

## Handoff artifact

Every handoff must include:

- ticket id
- branch/worktree
- docs read
- commands run
- result summary
- remaining risks
