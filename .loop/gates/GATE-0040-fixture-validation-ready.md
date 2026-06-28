# GATE-0040: Fixture validation ready

Status: active
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that committed synthetic fixtures can be validated by machine-readable CLI evidence before parser expansion, scheduler, headless autoplay, or timing analyzer implementation proceeds.

## Autonomy scorecard impact

- A2 Ticket / gate machine-readability: fixture readiness is represented as deterministic JSON evidence.
- A4 Executable test harness: committed fixtures become executable validation inputs rather than passive files.
- A6 Regression / CI enforcement: fixture validation commands can be added to CI and PR evidence.
- A7 Failure feedback loop: fixture failures have defined categories for repair-ticket routing.

## Required inputs

- Passed `GATE-0030`
- `TKT-0002` Done
- `docs/45_fixture_validation_contract.md`
- `fixtures/synthetic/phase1_synthetic_manifest.toml`
- `crates/taiko_chart/src/lib.rs`
- `crates/taiko_cli/src/lib.rs`
- `scripts/check_fixture_validation_static.py`
- `reports/fixture_validation/phase1_synthetic.json`
- `reports/fixture_validation/fx_core_001_basic_notes.inspect.json`

## Required commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_fixture_validation_static.py
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
```

## Pass criteria

| Check | Required result |
|---|---|
| `taiko_cli fixture validate` | JSON `verdict` is `pass` |
| Manifest declared count | `declared_fixture_count = 35` |
| Manifest entry count | `manifest_entry_count = 35` |
| Validated fixture count | `validated_count = 35` |
| Missing fixture count | `missing_count = 0` |
| Invalid fixture count | `invalid_count = 0` |
| Duplicate fixture IDs | `duplicate_fixture_ids = []` |
| Single fixture inspection | JSON `verdict` is `pass` |
| Unknown commands | Unknown command list is empty for committed fixtures |
| QA evidence | QA / Regression Session can pass or reject using JSON reports only |

## Reject conditions

Reject this gate when:

- fixture validation cannot run in a Rust-enabled environment;
- JSON output is missing required fields from `docs/45_fixture_validation_contract.md`;
- any committed manifest fixture is missing;
- any committed fixture has `fail` verdict;
- unknown commands are ignored instead of reported;
- QA Session needs manual chart inspection to determine the verdict.


## Failure handling

- `reject`: create a failure report using `templates/failure_report_template.md` and classify it as `fixture_manifest_error`, `fixture_file_missing`, `fixture_tja_structure_error`, `fixture_unknown_command`, or `fixture_cli_contract_error`.
- `block`: list the missing command output, gate report, or JSON evidence and keep downstream parser/headless/timing tickets Blocked.
- Repair tickets must include the exact failing fixture path or manifest field and the command that proves the repair.

## Output

Write the gate report to:

```text
.loop/session_logs/GATE-0040-report.md
```

The report must include links or copied command excerpts for:

- manifest validation JSON;
- single fixture inspection JSON;
- cargo command results;
- QA verdict.

## Next-ticket transition

- `pass`: parser expansion and scheduler tickets that depend on synthetic fixture readability may become eligible according to their dependency tables.
- `reject`: create a repair ticket using `templates/failure_report_template.md` with one of the fixture validation failure categories from `docs/45_fixture_validation_contract.md`.
- `block`: keep downstream parser, scheduler, headless autoplay, and timing analyzer tickets Blocked until missing evidence is produced.
