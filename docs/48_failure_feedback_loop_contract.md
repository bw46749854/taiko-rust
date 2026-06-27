# 48. Failure Feedback Loop Contract

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

Step11 makes the failure feedback loop executable enough for autonomous AI sessions.

The controlling objective is not merely to store failure reports. The objective is to convert a QA reject, timing anomaly, parser error, gate block, or CLI contract failure into a machine-readable failure record and a repair-ticket proposal without additional human design judgement.

## 2. Required command surface

```bash
taiko_cli loop failure ingest reports/failures/*.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
```

The command surface belongs to `taiko_cli`. It is part of loop orchestration, not gameplay.

## 3. `loop failure ingest` contract

`loop failure ingest` reads one or more Markdown failure reports that follow `templates/failure_report_template.md`.

Required JSON fields:

| Field | Meaning |
|---|---|
| `verdict` | `pass` when all reports are parseable, complete, and non-duplicate; otherwise `reject` |
| `report_count` | Number of reports read |
| `valid_count` | Number of reports with all required fields |
| `invalid_count` | Number of reports missing required fields |
| `duplicate_keys` | Duplicate-prevention keys that appear more than once |
| `reports[]` | Parsed failure records |

Each parsed failure record must include:

- `failure_id`
- `source_ticket_or_gate`
- `category`
- `reproduction_command`
- `expected_class`
- `actual_class`
- `proposed_ticket_id`
- `regression_command`
- `duplicate_key`
- `missing_fields`
- `path`

## 4. Duplicate key

A duplicate key is derived from:

```text
category + reproduction command + expected class + actual class
```

When two open failures share this key, the loop must update or reference the existing repair ticket instead of creating a parallel duplicate ticket.

## 5. `loop ticket propose --from-failure` contract

`loop ticket propose --from-failure` converts one parsed failure report into a repair-ticket proposal.

Required JSON fields:

- `ticket_id`
- `title`
- `status`
- `category`
- `source_failure_id`
- `repair_scope`
- `reproduction_command`
- `regression_command`
- `body`

The generated ticket body must include source failure ID, source ticket or gate, duplicate key, minimal repair scope, reproduction command, regression command, and acceptance criteria that allow QA Session to re-evaluate without manual judgement.

## 6. `loop ticket validate` contract

`loop ticket validate` checks whether a repair ticket contains the fields required to re-enter the loop.

Required JSON fields:

- `verdict`
- `ticket_id`
- `missing_fields`
- `path`

A valid repair ticket must include Source failure, Required reproduction command, Required regression command, Acceptance criteria, status, and ticket ID.

## 7. Approved categories

Step11 accepts all categories from `docs/07_failure_feedback_protocol.md` plus command-surface categories introduced by Step8-Step10:

- `fixture_manifest_error`
- `fixture_file_missing`
- `fixture_tja_structure_error`
- `fixture_unknown_command`
- `fixture_cli_contract_error`
- `headless_cli_contract_error`
- `headless_fixture_load_error`
- `headless_chart_verdict_error`
- `headless_no_scheduled_notes`
- `headless_autoplay_result_error`
- `runtime_mvp_regression`
- `timing_cli_contract_error`

Unknown categories are not silently accepted by QA policy. They must be routed to a protocol repair ticket or mapped to an approved category before downstream work continues.

## 8. Pass/fail/block rules

| Situation | Verdict |
|---|---|
| All reports parse, all required fields exist, duplicate keys are unique | `pass` |
| A report is missing required fields | `reject` |
| Two open reports share a duplicate key | `reject` |
| Required report path does not exist | `block` at gate level |
| Proposed repair ticket lacks source failure, reproduction command, regression command, or acceptance criteria | `reject` |

## 9. Gate evidence

`GATE-0070` requires failure ingest JSON, proposed repair-ticket JSON or Markdown body, repair-ticket validation JSON, cargo command results in Rust-enabled sessions, and QA verdict.

Passing `GATE-0070` permits Phase1 gameplay implementation tickets such as `TKT-0005` to proceed with a self-repairing failure route available.

## 10. Non-goals

Step11 does not need automatic file mutation, automatic branch creation, or automatic PR creation. It must make failure-to-ticket routing deterministic and machine-readable. Later CI and QA work may consume this command surface to create files automatically.

## Step19 materialization contract

Step19 upgrades the failure feedback loop from proposal-only to executable ticket creation.

New required commands:

```bash
taiko_cli loop failure classify --input reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket materialize --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop retry-budget check --ticket TKT-9001 --format json
```

`loop failure classify` must emit:

- `route`: `reject` or `block`
- `repair_kind`: `REPAIR`, `ENV`, `SPEC`, or `TOOL`
- `materialized_ticket_id`
- `original_ticket_should_remain`: `Rejected` or `Blocked`

`loop ticket materialize --from-failure` must create `.loop/tickets/<materialized_ticket_id>.md` with `Status: Ready` and must be idempotent.

`loop retry-budget check` must read `operations/retry_budget.toml` and block repeated attempts that exceed the configured budget.
