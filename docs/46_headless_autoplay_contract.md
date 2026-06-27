# Headless Autoplay Contract

Status: canonical

## Purpose

Headless autoplay is the first executable bridge between fixture validation and timing/audio self-verification. It lets AI Session groups run committed TJA fixtures without rendering, audio playback, or human observation, and receive a deterministic JSON verdict.

This contract supports the top-level objective from `docs/00_project_objective.md`: AI Session groups must read tickets, implement, validate, detect failure, route repair tickets, and advance to the next ticket without additional human design or judgement.

## Command surface

The Step9 MVP command surface is:

```bash
taiko_cli headless autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
headless_autoplay --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --mode perfect --format json
headless_autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
```

`headless_autoplay` is a binary alias that prepends `headless autoplay` and uses the same implementation as `taiko_cli`.

## Scope

Step9 implements only deterministic perfect autoplay for synthetic fixtures that already pass fixture validation.

Included:

- load one `.tja` fixture or a synthetic manifest;
- inspect chart structure through `taiko_chart`;
- schedule one synthetic event per non-zero note token;
- emit `hit_count = note_count` and `miss_count = 0` in `perfect` mode;
- emit `song_end_reached = true` when chart inspection passes and note count is positive;
- emit deterministic JSON for QA Session and CI.

Excluded:

- OpenTaiko-compatible BPM timeline semantics beyond structural note count;
- scroll, visual timing, audio scheduling, and render behavior;
- judgement windows and timing offset tolerances;
- score and gauge calculation;
- branch execution;
- golden expectation comparison.

Those remain later tickets. The Step9 MVP exists to make the autoplay execution path observable before detailed timing semantics are added.

## Required JSON fields

A headless autoplay report must include these top-level fields:

| Field | Required meaning |
|---|---|
| `scope` | Input chart path or manifest path. |
| `mode` | Currently `perfect`. |
| `verdict` | `pass` or `fail`. |
| `fixture_count` | Number of chart fixtures executed. |
| `passed_count` | Number of fixture results with `pass`. |
| `failed_count` | Number of fixture results with `fail`. |
| `total_note_count` | Sum of scheduled note tokens. |
| `total_scheduled_event_count` | Sum of synthetic runtime events. |
| `total_hit_count` | Sum of perfect-mode hits. |
| `total_miss_count` | Sum of misses. Must be zero for pass. |
| `fixtures` | Per-fixture result list. |
| `issues` | Top-level issues. Empty for pass. |

Each fixture result must include:

| Field | Required meaning |
|---|---|
| `fixture_id` | Manifest fixture id, or null for direct chart mode. |
| `path` | Fixture path. |
| `mode` | Currently `perfect`. |
| `verdict` | `pass` or `fail`. |
| `note_count` | Non-zero note token count from chart inspection. |
| `scheduled_event_count` | Synthetic event count. |
| `hit_count` | Perfect-mode hit count. |
| `miss_count` | Miss count. Must be zero for pass. |
| `song_end_reached` | Boolean song-end evidence. |
| `chart_verdict` | Underlying chart inspection verdict. |
| `issues` | Fixture-level issues. Empty for pass. |

## MVP pass/fail rules

A report passes only when all of these are true:

- `fixture_count > 0`;
- every fixture has `verdict = pass`;
- every fixture has `chart_verdict = pass`;
- every fixture has `note_count > 0`;
- every fixture has `hit_count = note_count`;
- every fixture has `miss_count = 0`;
- every fixture has `song_end_reached = true`;
- top-level `issues` is empty.

A report fails when any chart fails structural inspection, any chart has zero scheduled notes, any fixture does not reach song end, or any unsupported mode is requested.

## Failure categories

Step9 failures must be classified into one of these categories:

- `headless_cli_contract_error`
- `headless_fixture_load_error`
- `headless_chart_verdict_error`
- `headless_no_scheduled_notes`
- `headless_autoplay_result_error`
- `runtime_mvp_regression`

These categories must be usable by `templates/failure_report_template.md` and future `taiko_cli loop ticket propose --from-failure` work.

## QA usage

QA / Regression Session must be able to decide pass, reject, or block using only:

- command exit status;
- JSON report;
- cargo command output;
- `GATE-0050` report.

QA Session must not manually inspect the `.tja` file to decide whether the headless autoplay MVP passes.

## Transition rule

Passing `GATE-0050` permits detailed scheduler, timing log, and timing analyzer tickets to proceed. It does not certify OpenTaiko-compatible timing precision. Timing precision remains controlled by `docs/43_timing_log_schema.md`, `docs/44_timing_log_analyzer_spec.md`, and later timing analyzer gates.

## External content root

Headless autoplay over user-selected songs must accept `OPENTAIKO_CONTENT_ROOT` or `--content-root` and resolve OpenTaiko-compatible paths below that root. In development CI, `.external_assets/opentaiko/` is produced only by the verified Drive zip fetch step. Missing external assets produce a `block` verdict, not a gameplay `reject`.
