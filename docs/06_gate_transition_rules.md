# 06. Gate Transition Rules

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

Gate transitions must be deterministic enough for the Control Session and future `taiko_cli loop` commands to decide whether a ticket can move forward.

A gate is not a discussion checkpoint. A gate is a pass/fail/block transition rule with required inputs, required commands, evidence, and next-ticket consequences.

## 2. Allowed gate verdicts

| Verdict | Meaning | Required next action |
|---|---|---|
| `pass` | All required evidence exists and criteria pass | Unlock listed dependent tickets or next gate |
| `reject` | Evidence exists and proves failure | Create or select repair ticket using failure feedback protocol |
| `block` | Required evidence is missing or prerequisite not satisfied | Keep dependent tickets Blocked and produce missing-evidence list |

No other verdict is allowed.

## 3. Required gate fields

Every gate file must contain:

- `Status`
- `Owner`
- `Reviewer`
- `Purpose`
- `Autonomy scorecard impact`
- `Required inputs`
- `Pass criteria`
- `Failure handling`
- `Output`
- `Next-ticket transition`

## 4. Required gate report fields

Every gate report must contain:

- Gate ID
- Verdict: `pass`, `reject`, or `block`
- Command log
- Required input checklist
- Pass criteria checklist
- Autonomy scorecard delta
- Failure category when verdict is `reject`
- Missing evidence when verdict is `block`
- Next ticket candidate list
- Single selected next ticket, or explicit reason no ticket may proceed

## 5. Ticket transition rules

| From | To | Allowed when |
|---|---|---|
| `Blocked` | `Ready` | All dependencies and gate prerequisites pass |
| `Ready` | `In Progress` | Control Session selects the ticket as the single next ticket |
| `In Progress` | `In Review` | Implementation evidence and command logs exist |
| `In Review` | `QA` | Design Review Session approves review scope and evidence sufficiency |
| `QA` | `Done` | QA / Regression Session returns `pass` using required machine evidence |
| `QA` | `Rejected` | QA / Regression Session returns `reject` with failure report |
| `Rejected` | `Blocked` | Control Session links or creates a repair ticket |
| `Blocked` | `Ready` | Repair dependency passes and original prerequisites are satisfied |

## 6. Next-ticket selection rule

The next ticket must be selected by this priority order:

1. Repair ticket for a current `reject` verdict.
2. Blocking infrastructure ticket required for machine evidence.
3. Lowest-numbered Ready ticket whose dependencies all pass.
4. No ticket selected when evidence is missing.

The selected ticket must be unique. When multiple tickets are possible, the dependency graph and gate state must break the tie. The Control Session may not choose a ticket solely by preference.

## 7. Evidence sufficiency rule

A gate cannot pass on prose alone when the relevant command can exist.

Before the Rust workspace exists, repository-local scripts are sufficient for bootstrap gates. After `taiko_cli` exists, loop/gate/fixture/timing evidence must use `taiko_cli` commands defined in `docs/40_loop_cli_contract.md` and later implementation contracts.
