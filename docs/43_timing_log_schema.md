# Timing Log Schema

Status: Step3 expanded schema

## 1. Purpose

The timing log is the machine-readable evidence used by headless autoplay, fixture validation, and timing analyzer. It must be deterministic and sufficiently rich to let a separate QA session detect timing, branch, scroll, roll, score, gauge, and compatibility regressions.

Format: JSON Lines. One JSON object per event.

## 2. Common fields

Every record includes:

| Field | Type | Meaning |
|---|---:|---|
| `schema_version` | string | `phase1-timing-log/v1` |
| `run_id` | string | deterministic run identifier |
| `source_kind` | enum | synthetic_fixture / user_selected_song |
| `source_id` | string | fixture ID or user song ID |
| `event_index` | integer | monotonic event sequence |
| `event_type` | enum | one of the event types below |
| `tja_time_ms` | number | TJA-domain time after OFFSET/DELAY model |
| `game_time_ms` | number | runtime/game-domain time |
| `measure_index` | integer | zero-based measure index if applicable |
| `measure_pos_384` | integer | 384 ticks per 4/4 measure reference, when applicable |
| `branch` | enum/null | N / E / M / common |
| `course` | string/null | selected COURSE/difficulty |

## 3. Event types

| Event type | Required for |
|---|---|
| `parse_command` | command compatibility and report checks |
| `compatibility_report` | parse/report and non-scope coverage |
| `course_selected` | multi-course validation |
| `audio_reference` | WAVE/PATH_WAV/OFFSET validation |
| `bpm_change` | BPM timeline |
| `measure_change` | MEASURE timeline |
| `delay` | DELAY timeline |
| `note_scheduled` | arbitrary scheduler and note mapping |
| `roll_scheduled` | roll/balloon lifecycle |
| `roll_hit` | roll counter and branch condition |
| `balloon_hit` | balloon counter and branch condition |
| `barline_state` | generated and explicit barline validation |
| `gogo_state` | GOGO state and score multiplier context |
| `scroll_state` | SCROLL, NMSCROLL, BMSCROLL, HBSCROLL |
| `visual_position_sample` | scroll/overtake analyzer |
| `branch_section_start` | SECTION/BRANCHSTART |
| `branch_route_selected` | N/E/M route decision |
| `branch_section_end` | BRANCHEND merge validation |
| `judgement` | Perfect/Great/Good/Bad/Miss counters |
| `score_update` | SCOREMODE/SCOREINIT/SCOREDIFF validation |
| `gauge_update` | gauge/clear validation |
| `song_end` | completion gate |
| `fixture_result` | final fixture summary |

## 4. `note_scheduled`

Additional fields:

| Field | Type | Meaning |
|---|---:|---|
| `note_id` | string | stable note identifier |
| `note_char` | string | TJA token |
| `note_type` | string | domain note type |
| `lane` | enum | don / ka / roll / balloon / special |
| `is_big` | boolean | big note or big roll |
| `token_index_in_measure` | integer | zero-based token index |
| `token_count_in_measure` | integer | arbitrary scheduler denominator |
| `rational_beat_position` | string | exact rational position, e.g. `7/24` |
| `expected_ms` | number | deterministic scheduled time |

## 5. `scroll_state` and `visual_position_sample`

`scroll_state` fields:

- `scroll_x`
- `scroll_y`
- `scroll_mode`: normal / bm / hb
- `direction`
- `sudden_show_offset_ms`
- `sudden_move_offset_ms`
- `jposscroll_id`

`visual_position_sample` fields:

- `note_id`
- `x`
- `y`
- `velocity_ref`
- `is_overtake_candidate`
- `is_stationary_candidate`
- `sample_reason`

## 6. Branch fields

`branch_section_start` and `branch_route_selected` include:

- `branch_section_id`
- `condition_type`: p / pp / jp / jg / jb / r / rb / s / none
- `condition_range`: more / less
- `threshold_expert`
- `threshold_master`
- `levelhold_active`
- `route_before`
- `route_after`
- `counters_snapshot`

## 7. Score/gauge fields

`score_update` includes:

- `score_mode`
- `score_init`
- `score_diff`
- `combo_before`
- `gogo_active`
- `big_note_multiplier_applied`
- `score_delta`
- `score_total`

`gauge_update` includes:

- `judge`
- `gauge_before`
- `gauge_after`
- `clear_threshold`
- `is_clear`
- `is_failed`

## 8. Compatibility report fields

`compatibility_report` includes:

- `command`
- `classification`: parse_report / non_scope_report / unsupported_error
- `severity`: info / warning / fatal
- `reason`
- `source_line`
- `phase1_action`

Fatal compatibility reports fail synthetic and user-song validation.
