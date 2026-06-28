# 07. Failure Feedback Protocol

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

Failures must not stop the loop. Failures must become categorized evidence that routes back into repair work.

This protocol defines the minimum information required to transform a QA rejection, regression failure, timing anomaly, parser crash, or gate rejection into a repair ticket.

## 2. Failure categories

| Category | Meaning | Typical repair owner |
|---|---|---|
| `spec_ambiguity` | Acceptance criteria are unclear or conflicting | Spec Extraction Session |
| `opentaiko_evidence_gap` | OpenTaiko behavior is not sufficiently researched | Spec Extraction Session |
| `coverage_gap` | Fixture or user-song category coverage is missing | Test Infra Session |
| `parser_error` | TJA parsing fails, crashes, or silently ignores required data | Ticket Implementation Session |
| `chart_time_error` | BPM/MEASURE/DELAY/OFFSET timeline differs from expectation | Ticket Implementation Session |
| `scroll_time_error` | Scroll or visual timing projection is inconsistent | Ticket Implementation Session |
| `judgement_window_error` | judgement windows or boundary behavior are wrong | Ticket Implementation Session |
| `autoplay_input_error` | headless input schedule does not match expected hits | Ticket Implementation Session |
| `runtime_tick_error` | runtime loop ordering or tick granularity is wrong | Ticket Implementation Session |
| `branch_route_error` | branch condition or route selection differs | Ticket Implementation Session |
| `score_gauge_error` | score, combo, clear, or gauge update differs | Ticket Implementation Session |
| `audio_offset_error` | WAVE/PATH_WAV/OFFSET handling or latency evidence is wrong | Ticket Implementation Session |
| `ci_tooling_error` | CI, scripts, or command contract is broken | Test Infra Session |

## 3. Required failure report fields

A failure report must include:

- Failure ID
- Source ticket or gate
- Detecting session
- Category from the fixed list
- Reproduction command
- Expected result
- Actual result
- Evidence files
- Suspected affected modules or documents
- Minimal repair scope
- Regression command that must pass after repair
- Proposed repair ticket ID or existing linked ticket

## 4. Failure-to-ticket routing

The Control Session routes a failure using this order:

1. Link to an existing open repair ticket when the category and reproduction command match.
2. Create a new repair ticket when no open ticket matches.
3. Block the original ticket until the repair ticket is Done.
4. Re-run the original QA command after repair.

## 5. Duplicate prevention

A failure is considered duplicate when these fields match an existing open failure:

- Category
- Reproduction command
- Failing fixture or manifest
- Expected result class
- Actual result class

Duplicate failures update the existing repair ticket rather than creating a new ticket.

## 6. Required future CLI behavior

Loop CLI MVP and failure feedback route must make this protocol executable through commands equivalent to:

```bash
taiko_cli loop failure ingest reports/failures/*.md
taiko_cli loop ticket propose --from-failure reports/failures/*.md
taiko_cli loop ticket validate .loop/tickets/TKT-XXXX.md
```

Until those commands exist, failure reports must still follow `templates/failure_report_template.md` so the future CLI can parse them.

## 7. Executable failure feedback route surface

Status: canonical

The failure feedback route makes the required future CLI behavior executable through these commands:

```bash
taiko_cli loop failure ingest reports/failures/*.md --format json
taiko_cli loop ticket propose --from-failure reports/failures/FF-0001-sample-timing-cli-contract-error.md --format json
taiko_cli loop ticket validate .loop/tickets/TKT-0040.md --format json
```

Failure-to-ticket routing is no longer only a manual protocol. The loop must treat the JSON output from these commands as the evidence source for Control Session and QA / Regression Session routing.

Additional fixture/autoplay/timing command-surface categories are approved for routing:

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

## Executable repair materialization update

Failure feedback now has two distinct stages.

1. `loop failure classify --input PATH` decides `reject` versus `block` and selects `REPAIR`, `ENV`, `SPEC`, or `TOOL` repair kind.
2. `loop ticket materialize --from-failure PATH` creates the actual `.loop/tickets/<id>.md` file.

`loop ticket propose --from-failure` remains a preview command for diagnostics. The autonomous loop must use materialized tickets, not proposals, before continuing downstream work.

Retry budget must be checked before repeated repair attempts:

```bash
taiko_cli loop retry-budget check --ticket TKT-xxxx --format json
```

A `block` retry-budget verdict stops the ticket and routes to Control Session.
