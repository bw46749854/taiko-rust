# User Song Manifest Schema

Status: adopted for Step3 coverage design

This schema is written as Markdown so Codex can implement concrete YAML/JSON/TOML parsing later.

## Top-level fields

| Field | Type | Required | Meaning |
|---|---:|---:|---|
| `schema_version` | string | yes | must be `phase1-user-song-manifest/v1` |
| `suite_id` | string | yes | stable ID for this local validation suite |
| `created_by` | string | no | operator label, not personal data |
| `asset_policy` | object | yes | confirms assets are local and not committed |
| `songs` | array | yes | exactly 10 standard category entries unless using explicit override |

## `asset_policy`

| Field | Type | Required | Meaning |
|---|---:|---:|---|
| `assets_committed_to_repo` | boolean | yes | must be false |
| `local_paths_required` | boolean | yes | must be true |
| `allow_missing_audio_for_parse_only` | boolean | yes | false for final Phase1 validation |

## `songs[]`

| Field | Type | Required | Meaning |
|---|---:|---:|---|
| `song_id` | string | yes | local stable ID; no copyrighted title required |
| `display_name` | string | no | human-readable local name |
| `category_id` | enum | yes | one of C01..C10 |
| `chart_path` | path | yes | local path to `.tja` |
| `audio_root` | path | no | directory for WAVE/PATH_WAV resolution |
| `selected_course` | string/int | yes | COURSE value or difficulty index |
| `selected_branch_seed` | object | no | deterministic input profile for branch coverage |
| `declared_features` | array | yes | feature IDs from coverage matrix |
| `expected_branch_routes` | array | no | expected N/E/M routes observed during validation |
| `expected_unsupported_commands` | array | no | commands expected to be report-only |
| `pass_criteria` | object | yes | local thresholds for this song |

## `pass_criteria`

| Field | Type | Required | Default |
|---|---:|---:|---|
| `must_reach_song_end` | boolean | yes | true |
| `max_fatal_timing_anomalies` | integer | yes | 0 |
| `max_parse_errors` | integer | yes | 0 |
| `allow_parse_warnings` | boolean | yes | true |
| `require_score_summary` | boolean | yes | true |
| `require_gauge_summary` | boolean | yes | true |
| `require_deterministic_replay` | boolean | yes | true |

## Validation invariants

- Exactly one entry is required for each of C01..C10.
- All `chart_path` values must exist locally.
- `declared_features` must map to `docs/coverage/phase1_feature_coverage_matrix.md`.
- `expected_unsupported_commands` cannot contain Must implement gameplay features.
- Final validation cannot use parse-only mode.
