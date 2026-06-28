# repair materialization and retry-budget route Repair Materialization and Retry Budget

Status: canonical
Purpose: make failure feedback executable without human conversion from report to ticket.

## 1. Scope

The repair materialization and retry-budget route adds the missing link between QA failure evidence and the next runnable loop ticket.

It covers:

- `loop failure classify --input PATH`
- `loop ticket materialize --from-failure PATH`
- `loop retry-budget check --ticket TKT-xxxx`
- reject/block route separation
- repair/blocker ticket templates
- retry budget limits

It does not start Phase1 gameplay implementation. It does not call external AI APIs. It does not require `OPENAI_API_KEY`.

## 2. Classification contract

Failure reports are classified into two top-level routes.

| Route | Meaning | Ticket kind | Source item remains |
|---|---|---|---|
| `reject` | Concrete implementation, command contract, parser, runtime, timing, judgement, score, or fixture behavior failed. | `TKT-REPAIR-*` or proposed `TKT-*` | `Rejected` |
| `block` | Evidence, environment, fixture manifest, specification, or tooling is not sufficient to judge implementation. | `TKT-ENV-*`, `TKT-SPEC-*`, or `TKT-TOOL-*` | `Blocked` |

A failure report with missing required fields is always a `block` for tooling repair. The loop must not ask implementation sessions to repair ambiguous or incomplete evidence.

## 3. Materialization contract

`loop ticket propose --from-failure` remains a read-only preview command.

`loop ticket materialize --from-failure` creates the actual ticket file:

```bash
taiko_cli loop ticket materialize --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
```

Required side effect:

```text
.loop/tickets/<materialized-ticket-id>.md
```

The generated ticket must contain:

- `Status: Ready`
- source failure path
- source ticket or gate
- route
- repair kind
- duplicate key
- minimal repair scope
- required reproduction command
- required regression command
- retry-budget command
- acceptance criteria

Materialization is idempotent. When the ticket already exists, the command returns `already_exists: true` and does not overwrite the file.

## 4. Retry budget contract

The loop must stop repeated attempts before it becomes an infinite repair loop.

Default limits live in `operations/retry_budget.toml`:

```toml
max_repair_attempts_per_ticket = 3
max_block_attempts_per_gate = 2
max_same_failure_signature = 2
max_controller_runs_per_hour = 4
```

Command:

```bash
taiko_cli loop retry-budget check --ticket TKT-0005 --format json
```

`pass` means implementation or repair may continue.

`block` means the loop must stop the ticket and route to Control Session. This is a loop-quality stop, not a data-safety stop.

## 5. Controller use

`loop run-once` uses repair materialization outputs as follows:

```text
open failure exists
  -> classify failure
  -> reject: materialize repair ticket
  -> block: materialize ENV/SPEC/TOOL blocker ticket
  -> retry budget pass: continue
  -> retry budget block: stop and route to Control Session
```

ChatGPT-plan Codex operation may use the generated `next_codex_prompt.md` to ask Codex Cloud or Codex Automations to work on the materialized ticket. GitHub Actions still must not call Codex through `OPENAI_API_KEY`.

## 6. Acceptance criteria

| Check | Required result |
|---|---|
| `scripts/check_repair_materialization_static.py` | pass |
| `scripts/ci_local_equivalent.sh --static-only` | pass |
| `taiko_cli loop failure classify --input reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json` | returns `route` and `materialized_ticket_id` |
| `taiko_cli loop ticket materialize --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json` | creates or recognizes a ticket file |
| `taiko_cli loop retry-budget check --ticket TKT-9001 --format json` | returns budget verdict |
