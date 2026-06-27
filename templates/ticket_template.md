# <TICKET-ID>: <Title>

Status: <Ready | Blocked | In Progress | In Review | Done>
Owner session: <session>
Review session: <session>
Worktree: <worktree-path>

## 1. Objective

<Concrete objective. One ticket, one outcome.>

## 2. Required read set

- `AGENTS.md`
- `.loop/tickets/<TICKET-ID>.md`
- <docs>
- <research>
- <coverage>

## 3. Dependencies

| Dependency | Required state |
|---|---|
| <ticket/gate/doc> | <state> |

## 4. Scope

### In scope

- <item>

### Out of scope

- <item>

## 5. Implementation notes

<Constraints, canonical crate names, binary names, expected modules.>

## 6. Required checks

- `cargo fmt --all --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace`
- <fixture/analyzer commands>

## 7. Acceptance criteria

- <machine-checkable criterion>

## 8. Evidence to attach

- Plan
- Plan review result
- Command log
- Fixture report
- Timing analyzer report
- Review result
- Remaining risks
