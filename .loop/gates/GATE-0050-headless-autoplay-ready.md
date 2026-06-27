# GATE-0050: Headless autoplay ready

Status: active
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that synthetic fixtures can be executed through a render-free and audio-free perfect autoplay path, producing deterministic JSON evidence that QA Session can pass or reject without manual chart inspection.

## Autonomy scorecard impact

- A2 Ticket / gate machine-readability: autoplay readiness is represented by deterministic JSON evidence.
- A4 Executable test harness: synthetic fixtures become executable headless runtime inputs.
- A5 Timing / audio self-verification: the first timing-adjacent runtime evidence path exists before precision analyzer work.
- A6 Regression / CI enforcement: headless autoplay commands can be added to CI and PR evidence.
- A7 Failure feedback loop: headless failures have categories for repair-ticket routing.

## Required inputs

- Passed `GATE-0040`
- `TKT-0003` Done
- `docs/46_headless_autoplay_contract.md`
- `fixtures/synthetic/phase1_synthetic_manifest.toml`
- `crates/taiko_runtime/src/lib.rs`
- `crates/taiko_cli/src/lib.rs`
- `crates/taiko_cli/src/bin/headless_autoplay.rs`
- `scripts/check_headless_autoplay_static.py`
- `reports/headless_autoplay/phase1_synthetic.perfect.json`
- `reports/headless_autoplay/fx_core_001_basic_notes.perfect.json`

## Required commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_headless_autoplay_static.py
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
taiko_cli headless autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json
headless_autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
```

## Pass criteria

| Check | Required result |
|---|---|
| Manifest autoplay verdict | JSON `verdict` is `pass` |
| Manifest fixture count | `fixture_count = 35` |
| Manifest failed count | `failed_count = 0` |
| Manifest total note count | `total_note_count > 0` |
| Manifest total misses | `total_miss_count = 0` |
| Single chart autoplay verdict | JSON `verdict` is `pass` |
| Song end evidence | every fixture has `song_end_reached = true` |
| Headless binary alias | `headless_autoplay` returns the same JSON contract |
| QA evidence | QA / Regression Session can pass or reject using JSON reports only |

## Reject conditions

Reject this gate when:

- headless autoplay cannot run in a Rust-enabled environment;
- JSON output is missing required fields from `docs/46_headless_autoplay_contract.md`;
- any fixture has `fail` verdict;
- any fixture has `miss_count > 0` in perfect mode;
- any fixture lacks song-end evidence;
- QA Session needs visual observation, audio playback, or manual chart inspection to determine the verdict.

## Failure handling

- `reject`: create a failure report using `templates/failure_report_template.md` and classify it as `headless_cli_contract_error`, `headless_fixture_load_error`, `headless_chart_verdict_error`, `headless_no_scheduled_notes`, `headless_autoplay_result_error`, or `runtime_mvp_regression`.
- `block`: list the missing command output, gate report, or JSON evidence and keep downstream timing analyzer tickets Blocked.
- Repair tickets must include the exact failing fixture path or manifest field and the command that proves the repair.

## Output

Write the gate report to:

```text
.loop/session_logs/GATE-0050-report.md
```

The report must include links or copied command excerpts for:

- manifest headless autoplay JSON;
- single fixture headless autoplay JSON;
- cargo command results;
- QA verdict.

## Next-ticket transition

- `pass`: timing log and analyzer MVP tickets may become eligible according to their dependency tables.
- `reject`: create a repair ticket using `templates/failure_report_template.md` with one of the headless failure categories from `docs/46_headless_autoplay_contract.md`.
- `block`: keep downstream timing analyzer and precision tickets Blocked until missing evidence is produced.
