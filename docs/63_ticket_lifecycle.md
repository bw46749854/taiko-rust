# 63. Ticket Lifecycle

Status: canonical

## Status values

| Status | Meaning |
|---|---|
| Draft | Ticket exists but lacks complete scope or DoD |
| Blocked | Ticket is defined but cannot be started because dependencies or gates are missing |
| Ready | Ticket can be selected by Control Session |
| In Progress | Implementation worktree is active |
| Plan Review | Plan is waiting for Design Review Session |
| In Review | Diff and evidence are waiting for review |
| QA | QA / Regression Session is running checks |
| Done | Accepted with evidence |
| Rejected | Not accepted; needs replacement or major rewrite |

## Ready requirements

A ticket can become Ready only when:

- Dependencies are Done or the relevant gate has passed.
- Required read set is explicit.
- Scope is single-purpose.
- DoD is machine-checkable.
- Review session is separate from implementation session.
- Fixture/analyzer impact is declared.
- Copyright asset policy is not violated.

## Done requirements

A ticket can become Done only when:

- Plan review passed.
- Implementation diff is limited to the ticket scope.
- Required cargo commands passed.
- Required fixture/analyzer commands passed.
- Compatibility report was checked.
- QA or design review accepted the result.
- Remaining risks are documented.

## Reopening

A Done ticket must be reopened or followed by a corrective ticket when:

- synthetic fixture coverage regresses,
- user-selected song validation exposes a missing normal-play feature,
- timing anomaly exceeds acceptance threshold,
- OpenTaiko research contradicts the adopted behavior,
- a previously ignored command appears in normal-play charts.

## repair materialization and retry-budget route repair and blocker lifecycle

A `reject` or `block` verdict must not depend on human ticket drafting.

```text
QA reject
  -> failure report
  -> loop failure classify
  -> route = reject
  -> loop ticket materialize
  -> TKT-REPAIR-* or proposed TKT-* becomes Ready

QA block
  -> failure report
  -> loop failure classify
  -> route = block
  -> loop ticket materialize
  -> TKT-ENV-* / TKT-SPEC-* / TKT-TOOL-* becomes Ready
```

Before a repair ticket is implemented again, the controller checks:

```bash
taiko_cli loop retry-budget check --ticket <ticket-id> --format json
```

`pass` continues the loop. `block` stops the loop and writes control evidence instead of continuing to mutate implementation code.

## Ticket advance engine

OPS-0007 makes post-merge ticket advancement machine-owned. After a PR merge produces `reports/loop/merge_history/<run_id>.json`, `scripts/loop_advance_ticket.py` writes `reports/loop/ticket_transitions/<run_id>.json` and a Markdown report.

The engine applies these transitions:

```text
merged ticket -> Done
dependency-satisfied next ticket -> Ready
all other tickets -> unchanged
```

During the OPS migration rail, no `TKT-*` gameplay ticket may become `Ready`. Exactly one ticket must be `Ready` after the transition.
