# GATE-0060: Timing analyzer ready

Status: active
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that Step9 headless autoplay evidence can be analyzed as deterministic timing evidence, producing JSON pass/reject reports with threshold metrics and failure categories. This gate is the first machine-verifiable timing self-check before OpenTaiko-compatible scheduling, audio sync, and judgement precision work proceeds.

## Autonomy scorecard impact

- A2 Ticket / gate machine-readability: timing readiness is represented by deterministic JSON evidence.
- A4 Executable test harness: headless runtime evidence becomes analyzable regression input.
- A5 Timing / audio self-verification: max/mean/p95 error metrics and threshold verdicts become machine-readable.
- A6 Regression / CI enforcement: timing analyzer commands can be added to CI and PR evidence.
- A7 Failure feedback loop: timing failures have categories for repair-ticket routing.

## Required inputs

- Passed `GATE-0050`
- `TKT-0004` Done
- `docs/47_timing_log_analyzer_contract.md`
- `docs/43_timing_log_schema.md`
- `docs/44_timing_log_analyzer_spec.md`
- `fixtures/synthetic/phase1_synthetic_manifest.toml`
- `crates/taiko_timing/src/lib.rs`
- `crates/taiko_runtime/src/lib.rs`
- `crates/taiko_cli/src/lib.rs`
- `crates/taiko_cli/src/bin/timing_log_analyzer.rs`
- `scripts/check_timing_analyzer_static.py`
- `reports/timing/phase1_synthetic.perfect.analysis.json`
- `reports/timing/fx_core_001_basic_notes.perfect.analysis.json`

## Required commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_timing_analyzer_static.py
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
timing_log_analyzer --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```

## Pass criteria

| Check | Required result |
|---|---|
| Manifest timing verdict | JSON `verdict` is `pass` |
| Manifest fixture count | `fixture_count = 35` |
| Timing failed count | `failed_count = 0` |
| Analyzed events | `analyzed_event_count > 0` |
| Max error | `max_error_ms <= threshold_ms` |
| Mean error | `mean_error_ms <= threshold_ms` |
| P95 error | `p95_error_ms <= threshold_ms` |
| Failure categories | `failure_categories` is empty on pass |
| Binary alias | `timing_log_analyzer` returns the same JSON contract |
| QA evidence | QA / Regression Session can pass or reject using JSON reports only |

## Reject conditions

Reject this gate when:

- timing analyzer cannot run in a Rust-enabled environment;
- JSON output is missing required fields from `docs/47_timing_log_analyzer_contract.md`;
- `max_error_ms`, `mean_error_ms`, or `p95_error_ms` exceeds `threshold_ms`;
- any fixture has a `fail` timing verdict;
- analyzer output cannot classify failures into approved categories;
- QA Session needs visual observation, audio playback, or manual chart inspection to determine the verdict.

## Failure handling

- `reject`: create a failure report using `templates/failure_report_template.md` and classify it as `parser_error`, `chart_time_error`, `scroll_time_error`, `judgement_window_error`, `autoplay_input_error`, `runtime_tick_error`, `headless_autoplay_result_error`, or `timing_cli_contract_error`.
- `block`: list the missing command output, gate report, or JSON evidence and keep downstream precision and Phase1 feature tickets Blocked.
- Repair tickets must include the exact failing fixture path, timing metric, threshold, and command that proves the repair.

## Output

Write the gate report to:

```text
.loop/session_logs/GATE-0060-report.md
```

The report must include links or copied command excerpts for:

- manifest headless autoplay JSON;
- manifest timing analyzer JSON;
- input-file timing analyzer JSON;
- `timing_log_analyzer` alias JSON;
- cargo command results;
- QA verdict.

## Next-ticket transition

- `pass`: `TKT-0040` Failure Feedback Loop MVP may become eligible. Gameplay feature tickets remain Blocked until `GATE-0070` passes.
- `reject`: create a repair ticket using `templates/failure_report_template.md` with one of the timing failure categories from `docs/47_timing_log_analyzer_contract.md`.
- `block`: keep downstream failure feedback, precision, and feature implementation tickets Blocked until missing evidence is produced.
