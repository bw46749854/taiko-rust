# 47. Timing Log Analyzer Contract

Status: canonical
Last updated: 2026-06-25

## Purpose

The timing analyzer is the machine-verifiable precision evidence layer for the autonomous Phase1 loop. It converts headless autoplay evidence into pass/reject JSON so QA / Regression Session can detect timing-adjacent failures and route them to repair tickets without listening to audio, watching rendering, or manually inspecting TJA charts.

timing analyzer is an MVP over headless autoplay perfect-autoplay evidence. It intentionally reports deterministic zero-error timing for passing perfect-autoplay fixtures. Later tickets replace this MVP model with real chart-time samples, OpenTaiko-compatible scheduling, audio latency handling, judgement-window boundaries, and golden regression baselines.

## Required commands

```bash
taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
timing_log_analyzer --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```

The `timing_log_analyzer` binary is an alias for `taiko_cli timing analyze` and must return the same JSON contract.

## Required JSON fields

The top-level JSON report must include:

| Field | Meaning |
|---|---|
| `scope` | analyzed chart, manifest, or input report scope |
| `source` | source evidence type, such as `headless_autoplay_manifest` or `headless_autoplay_json` |
| `verdict` | `pass` or `fail` |
| `threshold_ms` | numeric threshold used for pass/reject |
| `fixture_count` | number of fixture results represented by the analysis |
| `passed_count` | number of timing fixture results with `pass` verdict |
| `failed_count` | number of timing fixture results with `fail` verdict |
| `analyzed_event_count` | number of note/timing events analyzed |
| `max_error_ms` | maximum absolute timing error in milliseconds |
| `mean_error_ms` | mean absolute timing error in milliseconds |
| `p95_error_ms` | p95 absolute timing error in milliseconds |
| `failure_categories` | list of approved categories present in failed fixture results |
| `fixtures` | per-fixture timing analysis objects |
| `issues` | top-level analyzer issues |

Each fixture object must include:

| Field | Meaning |
|---|---|
| `fixture_id` | manifest fixture ID or null for input-only analysis |
| `path` | fixture path or input scope |
| `verdict` | `pass` or `fail` |
| `expected_event_count` | expected note/timing event count |
| `actual_event_count` | observed note/timing event count |
| `max_error_ms` | fixture-level maximum error |
| `mean_error_ms` | fixture-level mean error |
| `p95_error_ms` | fixture-level p95 error |
| `failure_category` | approved category or null on pass |
| `issues` | fixture-level issues |

## MVP pass/fail rules

A timing analysis report passes only when all conditions hold:

- source headless report verdict is `pass`;
- `analyzed_event_count > 0`;
- `failed_count = 0`;
- `max_error_ms <= threshold_ms`;
- `mean_error_ms <= threshold_ms`;
- `p95_error_ms <= threshold_ms`;
- `failure_categories` is empty;
- top-level `issues` is empty.

A report fails when any fixture has mismatched expected/actual event count, miss count, missing song-end evidence, source headless failure, threshold violation, or unknown input shape.

## Failure categories

timing analyzer failures must be classified into one of these categories:

- `parser_error`
- `chart_time_error`
- `scroll_time_error`
- `judgement_window_error`
- `autoplay_input_error`
- `runtime_tick_error`
- `headless_autoplay_result_error`
- `timing_cli_contract_error`

These categories must be usable by `templates/failure_report_template.md` and future `taiko_cli loop ticket propose --from-failure` work.

## QA usage

QA / Regression Session must be able to decide pass, reject, or block using only:

- command exit status;
- timing analyzer JSON report;
- cargo command output;
- `GATE-0060` report.

QA Session must not manually inspect `.tja` files, listen to audio, or watch rendering to decide whether the timing analyzer MVP passes.

## Transition rule

Passing `GATE-0060` permits detailed scheduler, OpenTaiko-compatible chart time, judgement-window, scroll timing, and precision-tuning tickets to proceed. It does not certify final OpenTaiko timing compatibility. It certifies that timing evidence has a machine-readable pass/reject surface that downstream tickets must preserve and strengthen.

## Non-goals

timing analyzer does not implement:

- audio device latency measurement;
- OpenTaiko-compatible input latency compensation;
- real BPM/measure-derived note timestamps beyond headless autoplay MVP evidence;
- visual scroll timing analysis;
- judgement-window boundary testing;
- score, gauge, branch execution, or rendering;
- golden baseline update policy enforcement.

Those are downstream tickets that must consume the timing analyzer analyzer contract.
