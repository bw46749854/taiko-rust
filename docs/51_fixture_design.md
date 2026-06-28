# Fixture Design

Status: adopted

## 1. Design goal

Synthetic fixtures are small `.tja` files designed to prove one primary behavior each. The baseline set contains exactly 35 fixtures, satisfying the required 25–35 range while keeping several parse/report and non-scope checks isolated.

## 2. Fixture conventions

- All fixtures use local dummy audio name `__dummy__.ogg`.
- Fixtures do not include actual audio assets.
- Fixtures are valid enough for parser/headless tests.
- Each fixture has a stable fixture ID.
- Each fixture must map to at least one feature ID from `docs/coverage/phase1_feature_coverage_matrix.md`.
- Expected assertions are defined by fixture ID, not inferred from file name.

## 3. Required fixture groups

| Group | Directory | Purpose |
|---|---|---|
| core | `fixtures/synthetic/phase1_core/` | notes, gogo, barlines, special parse |
| timing | `fixtures/synthetic/phase1_timing/` | BPM, measure, delay, offset, scheduler |
| roll_balloon | `fixtures/synthetic/phase1_roll_balloon/` | roll, big roll, balloon, BalloonEx |
| branching | `fixtures/synthetic/phase1_branching/` | SECTION, BRANCHSTART, N/E/M, LEVELHOLD |
| scroll | `fixtures/synthetic/phase1_scroll/` | SCROLL and visual timing modes |
| course_audio | `fixtures/synthetic/phase1_course_audio/` | COURSE, WAVE/PATH_WAV, score/gauge, non-scope report |

## 4. Fixture pass criteria

Each fixture passes when:

1. parser exits without panic;
2. all commands are classified;
3. required event types appear in timing log;
4. headless autoplay reaches song end, except explicit parse/report fixtures where gameplay is not required;
5. analyzer profile `phase1-synthetic` reports no fatal anomaly;
6. fixture result contains feature IDs and assertions.

## 5. Fixture manifest

The concrete TOML manifest is now committed at `fixtures/synthetic/phase1_synthetic_manifest.toml`. The schema remains documented at `fixtures/synthetic/phase1_synthetic_manifest.schema.md`. The manifest is validated by `scripts/validate_fixture_manifest.py`. Required fields are:

| Field | Meaning |
|---|---|
| `fixture_id` | stable ID such as FX-TIME-002 |
| `path` | TJA path |
| `primary_features` | feature IDs |
| `expected_event_types` | required timing log event types |
| `headless_required` | true/false |
| `expected_reports` | compatibility reports expected |
| `assertions` | fixture-specific analyzer rules |

## 6. Golden expectations

Do not store golden millisecond values before the rounding policy is implemented. Store rational positions and command-order expectations first. Millisecond goldens are added only after `docs/40_timing_model.md` rounding policy is fully implemented.
