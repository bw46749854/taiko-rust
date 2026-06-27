# 76. Phase1 Feature Acceptance Command Matrix

Status: canonical

## 1. Purpose

This matrix maps Phase1 gameplay ticket categories to the minimum command evidence required before QA / Regression Session may return `pass`.

## 2. Matrix

| Category | Required command evidence |
|---|---|
| `timing_model` | cargo, fixture validate, headless autoplay, timing analyze, QA run, QA verdict |
| `note_state` | cargo, fixture validate, headless autoplay, QA run, QA verdict |
| `chart_events` | cargo, fixture validate, headless autoplay, QA run, QA verdict |
| `chart_parser` | cargo, fixture validate, headless autoplay, QA run, QA verdict |
| `runtime_logic` | cargo, headless autoplay, timing analyze, QA run, QA verdict |
| `test_harness` | cargo, fixture validate, headless autoplay, timing analyze, QA run, QA verdict |
| `score_gauge` | cargo, headless autoplay, QA run, QA verdict |
| `scroll_model` | cargo, headless autoplay, timing analyze, QA run, QA verdict |
| `phase1_parse_report` | cargo, fixture validate, QA run, QA verdict |
| `telemetry_schema` | cargo, timing analyze, QA run, QA verdict |
| `analyzer` | cargo, timing analyze, QA run, QA verdict |
| `fixture_coverage` | fixture manifest validation, fixture structure validation, QA run, QA verdict |
| `external_input_validation` | user-selected validation report, QA run, QA verdict |

## 3. Reject routing

Any command failure in the matrix must route to Step11 failure feedback. The failure category should be selected from the existing failure taxonomy:

- `parser_error`
- `chart_time_error`
- `scroll_time_error`
- `judgement_window_error`
- `autoplay_input_error`
- `runtime_tick_error`
- `headless_autoplay_result_error`
- `timing_cli_contract_error`
- `qa_regression_contract_error`
- `phase1_feature_manifest_error`
- `feature_ticket_transition_error`

## 4. Block routing

A missing command, missing report, unavailable Rust toolchain, missing worktree separation evidence, or absent baseline/current comparison must produce `block`, not `pass`.
