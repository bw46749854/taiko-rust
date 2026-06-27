# Timing Log Analyzer Spec

Status: Step3 expanded analyzer specification

## 1. Purpose

The analyzer is the independent QA component that determines whether generated timing logs satisfy Phase1 requirements. It must be runnable by a QA/regression session separate from the implementation session.

## 2. Profiles

| Profile | Input | Purpose |
|---|---|---|
| `phase1-synthetic` | synthetic fixture JSONL | strict feature assertions |
| `phase1-user-selected` | user-selected song JSONL | real-song compatibility checks |
| `phase1-debug` | any JSONL | verbose diagnostics without gate decisions |

## 3. Common checks

The analyzer must check:

1. schema version is supported;
2. event indexes are monotonic;
3. timestamps are finite and non-NaN;
4. note schedule is strictly ordered within each branch where required;
5. all `note_id` references are valid;
6. song end appears for every source;
7. no fatal compatibility report exists;
8. deterministic replay hashes match when a repeated run is supplied.

## 4. Timing checks

For fixtures with expected rational positions:

- compare `rational_beat_position` exactly;
- compare derived milliseconds within configured tolerance;
- verify BPMCHANGE affects only events after its command point;
- verify DELAY shifts the time cursor;
- verify MEASURE changes measure length and barline timing;
- verify OFFSET changes BGM/note relation according to signed offset model.

Default tolerances:

| Check | Tolerance |
|---|---:|
| rational beat position | exact |
| note scheduled ms | <= 0.5 ms after final rounding policy is implemented |
| scroll sample finite check | exact finite/non-NaN |
| deterministic replay event hash | exact |

## 5. Branch checks

The analyzer must verify:

- every branch section has start and end records;
- branch route decisions are one of N/E/M;
- N/E/M bodies do not duplicate common notes;
- SECTION resets counters used by branch condition;
- LEVELHOLD prevents later branch switching in the same locked region;
- p/pp/jp/jg/jb/r/rb/s conditions have required counters in snapshot;
- branch route coverage expected by fixture/manifest is observed.

## 6. Roll/balloon checks

The analyzer must verify:

- each roll/balloon start has matching end token;
- roll hit events occur only while roll body is active;
- balloon required count comes from the correct BALLOON header array;
- branch-specific balloon arrays select the correct route count;
- BalloonEx is classified distinctly from normal balloon;
- roll counters used for branch decision are present.

## 7. Scroll/visual checks

The analyzer must verify:

- SCROLL values are parsed as finite x/y components;
- negative, zero, high, and complex scroll produce non-fatal visual samples;
- NMSCROLL/BMSCROLL/HBSCROLL mode changes are logged;
- visual timing does not change judgement timing;
- overtake candidates are reported for negative/high scroll fixtures;
- parse/report features SUDDEN/DIRECTION/JPOSSCROLL appear as compatibility or visual-state records.

## 8. Score/gauge checks

The analyzer must verify:

- score mode/config records exist before first score update;
- GOGO state is present when score update occurs during gogo period;
- big note multiplier context is logged for big notes;
- gauge updates exist for hit and miss cases;
- final clear/fail state is present;
- score/gauge summary exists in fixture and user-song reports.

## 9. Exit codes

| Exit code | Meaning |
|---:|---|
| 0 | pass |
| 1 | validation failed |
| 2 | invalid analyzer invocation |
| 3 | malformed log/schema mismatch |
| 4 | missing required fixture/user-song coverage |

## 10. Output

Analyzer output is a JSON summary and a human-readable Markdown report.

Required summary fields:

- `profile`
- `overall_status`
- `source_count`
- `feature_coverage`
- `fatal_anomaly_count`
- `warning_count`
- `deterministic_replay_status`
- `failed_sources`
