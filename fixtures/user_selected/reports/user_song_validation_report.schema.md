# User Song Validation Report Schema

Status: adopted for Step3 coverage design

## Top-level fields

| Field | Type | Required | Meaning |
|---|---:|---:|---|
| `schema_version` | string | yes | `phase1-user-song-validation-report/v1` |
| `suite_id` | string | yes | copied from manifest |
| `code_revision` | string | yes | git revision validated |
| `started_at` | string | yes | ISO timestamp |
| `finished_at` | string | yes | ISO timestamp |
| `overall_status` | enum | yes | pass / fail / blocked |
| `songs` | array | yes | one result per manifest song |
| `coverage_summary` | object | yes | category and feature coverage |
| `fatal_anomalies` | array | yes | suite-level fatal anomalies |

## `songs[]`

| Field | Type | Required | Meaning |
|---|---:|---:|---|
| `song_id` | string | yes | manifest song ID |
| `category_id` | string | yes | C01..C10 |
| `parse_status` | enum | yes | pass / fail |
| `headless_status` | enum | yes | reached_song_end / aborted / blocked |
| `timing_status` | enum | yes | pass / warning / fatal |
| `deterministic_replay_status` | enum | yes | pass / fail / skipped |
| `selected_course` | string | yes | resolved course |
| `feature_tags_observed` | array | yes | observed feature IDs |
| `branch_routes_observed` | array | yes | N/E/M routes observed |
| `unsupported_reports` | array | yes | parse/report non-scope records |
| `score_summary` | object | yes | final score and score-mode inputs |
| `gauge_summary` | object | yes | final gauge and clear/fail status |
| `roll_summary` | object | yes | roll/balloon counts |
| `timing_anomalies` | array | yes | analyzer anomaly records |

## Required invariant

`overall_status: pass` is allowed only when:

- all C01..C10 categories are present;
- every song has `headless_status: reached_song_end`;
- all `timing_status` values are pass or warning with no fatal anomalies;
- every song has score and gauge summaries;
- deterministic replay passes for every song;
- all unsupported/non-scope commands are reported.
