# GATE-0070: Failure feedback ready

Status: active
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that QA rejects and gate rejects can be converted into machine-readable failure records and repair-ticket proposals before gameplay feature implementation proceeds.

## Autonomy scorecard impact

- A2 Ticket / gate machine-readability: failure state becomes parseable JSON evidence.
- A6 Regression / CI enforcement: reject outputs can become deterministic CI and QA evidence.
- A7 Failure feedback loop: failures route back into repair tickets without ad hoc human judgement.

## Required inputs

- Passed `GATE-0060`
- `TKT-0040` Done
- `docs/48_failure_feedback_loop_contract.md`
- `docs/07_failure_feedback_protocol.md`
- `templates/failure_report_template.md`
- `reports/failures/FF-0001-sample-timing-cli-contract-error.md`
- `crates/taiko_cli/src/lib.rs`
- `scripts/check_failure_feedback_static.py`
- `reports/failure_feedback/FF-0001.ingest.json`
- `reports/failure_feedback/FF-0001.proposed_ticket.json`
- `reports/failure_feedback/TKT-0040.validate.json`

## Required commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_failure_feedback_static.py
taiko_cli loop failure ingest reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
```

## Pass criteria

| Check | Required result |
|---|---|
| Failure ingest verdict | JSON `verdict` is `pass` |
| Report count | `report_count >= 1` |
| Invalid count | `invalid_count = 0` |
| Duplicate keys | `duplicate_keys = []` |
| Proposed ticket | JSON contains `ticket_id`, `source_failure_id`, `repair_scope`, reproduction command, regression command, and body |
| Ticket validation | JSON `verdict` is `pass` for repair-ticket-shaped Markdown |
| QA evidence | QA / Regression Session can route a reject to a repair ticket using JSON reports only |
| Human judgement removal | No extra human design decision is required to identify repair scope, proof command, or next blocking ticket |

## Reject conditions

- failure reports cannot be parsed in a Rust-enabled environment;
- JSON output is missing required fields from `docs/48_failure_feedback_loop_contract.md`;
- duplicate failures create parallel repair tickets instead of a duplicate key;
- proposed tickets lack reproduction command, regression command, or acceptance criteria;
- QA Session must manually infer repair scope before routing.

## Failure handling

- `reject`: create a failure report using `templates/failure_report_template.md` and classify it as `ci_tooling_error`, `spec_ambiguity`, `coverage_gap`, or the most specific command-contract category.
- `block`: list the missing command output, gate report, or JSON evidence and keep downstream Phase1 gameplay tickets Blocked.
- Repair tickets must include the exact failure report path and command that proves the repair.

## Output

- failure ingest JSON;
- proposed ticket JSON or generated Markdown body;
- repair-ticket validation JSON;
- cargo command results;
- QA verdict.

## Next-ticket transition

- `pass`: Phase1 gameplay feature tickets beginning with `TKT-0005` may become eligible according to their dependency tables.
- `reject`: create or update a repair ticket using the failure feedback route command surface.
- `block`: keep Phase1 gameplay feature implementation tickets Blocked until failure feedback evidence is produced.
