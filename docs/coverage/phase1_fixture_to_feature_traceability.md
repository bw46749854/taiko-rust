# Phase1 Fixture to Feature Traceability

Status: adopted

## 1. Fixture inventory

The synthetic fixture baseline contains exactly 35 committed TJA fixtures. This satisfies the target range of 25–35 fixtures while keeping failure localization practical.

| Fixture ID | File | Primary target | Feature IDs |
|---|---|---|---|
| FX-CORE-001 | `fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja` | Don/Ka, default BPM, generated barline | F011,F021 |
| FX-CORE-002 | `fixtures/synthetic/phase1_core/fx_core_002_big_notes.tja` | big Don/Ka and big input context | F012,F013 |
| FX-CORE-003 | `fixtures/synthetic/phase1_core/fx_core_003_gogo_score_context.tja` | GOGO state with score context | F020,F044,F045 |
| FX-CORE-004 | `fixtures/synthetic/phase1_core/fx_core_004_barline_controls.tja` | BARLINEON/OFF and explicit #BARLINE | F022,F023 |
| FX-CORE-005 | `fixtures/synthetic/phase1_core/fx_core_005_special_notes_parse.tja` | mine/adlib/special note parse/report | F047 |
| FX-TIME-001 | `fixtures/synthetic/phase1_timing/fx_time_001_initial_bpm_offset_positive.tja` | initial BPM and positive OFFSET | F003,F004 |
| FX-TIME-002 | `fixtures/synthetic/phase1_timing/fx_time_002_offset_negative.tja` | negative OFFSET | F003 |
| FX-TIME-003 | `fixtures/synthetic/phase1_timing/fx_time_003_bpmchange.tja` | BPMCHANGE timeline | F005 |
| FX-TIME-004 | `fixtures/synthetic/phase1_timing/fx_time_004_measure.tja` | MEASURE ratios and barline schedule | F006 |
| FX-TIME-005 | `fixtures/synthetic/phase1_timing/fx_time_005_delay.tja` | DELAY timeline shift | F007 |
| FX-TIME-006 | `fixtures/synthetic/phase1_timing/fx_time_006_standard_subdivisions.tja` | 4/8/12/16/24/36 token counts | F008,F009 |
| FX-TIME-007 | `fixtures/synthetic/phase1_timing/fx_time_007_mixed_subdivisions.tja` | mixed subdivision measures | F008,F010 |
| FX-TIME-008 | `fixtures/synthetic/phase1_timing/fx_time_008_dense_32_48_like.tja` | dense arbitrary token counts | F008 |
| FX-ROLL-001 | `fixtures/synthetic/phase1_roll_balloon/fx_roll_001_normal_and_big_roll.tja` | normal roll, big roll, roll end | F014,F015,F019 |
| FX-ROLL-002 | `fixtures/synthetic/phase1_roll_balloon/fx_roll_002_balloon.tja` | BALLOON header and balloon event | F016 |
| FX-ROLL-003 | `fixtures/synthetic/phase1_roll_balloon/fx_roll_003_branch_balloon_arrays.tja` | BALLOONNOR/EXP/MAS branch counts | F017 |
| FX-ROLL-004 | `fixtures/synthetic/phase1_roll_balloon/fx_roll_004_balloonex.tja` | BalloonEx/kusudama classification | F018 |
| FX-BRANCH-001 | `fixtures/synthetic/phase1_branching/fx_branch_001_section_and_accuracy.tja` | SECTION and p branch condition | F024,F025,F029 |
| FX-BRANCH-002 | `fixtures/synthetic/phase1_branching/fx_branch_002_nem_and_branchend.tja` | N/E/M bodies and BRANCHEND merge | F026,F027 |
| FX-BRANCH-003 | `fixtures/synthetic/phase1_branching/fx_branch_003_levelhold.tja` | LEVELHOLD route lock | F028 |
| FX-BRANCH-004 | `fixtures/synthetic/phase1_branching/fx_branch_004_percent_perfect.tja` | pp branch condition | F029 |
| FX-BRANCH-005 | `fixtures/synthetic/phase1_branching/fx_branch_005_judge_count_conditions.tja` | jp/jg/jb counters | F030 |
| FX-BRANCH-006 | `fixtures/synthetic/phase1_branching/fx_branch_006_roll_score_conditions.tja` | r/rb/s conditions | F031,F032 |
| FX-SCROLL-001 | `fixtures/synthetic/phase1_scroll/fx_scroll_001_extreme_scroll_values.tja` | positive/negative/zero/high SCROLL | F033,F034,F035,F036 |
| FX-SCROLL-002 | `fixtures/synthetic/phase1_scroll/fx_scroll_002_complex_scroll.tja` | complex SCROLL x+yi | F037 |
| FX-SCROLL-003 | `fixtures/synthetic/phase1_scroll/fx_scroll_003_scroll_modes.tja` | NMSCROLL/BMSCROLL/HBSCROLL | F038,F039,F040 |
| FX-SCROLL-004 | `fixtures/synthetic/phase1_scroll/fx_scroll_004_special_visual_parse.tja` | SUDDEN/DIRECTION/JPOSSCROLL parse/report | F041,F042,F043 |
| FX-SCORE-001 | `fixtures/synthetic/phase1_course_audio/fx_score_001_scoremode_init_diff.tja` | SCOREMODE/SCOREINIT/SCOREDIFF | F044,F045 |
| FX-SCORE-002 | `fixtures/synthetic/phase1_course_audio/fx_score_002_gauge_clear.tja` | gauge update and clear summary | F046 |
| FX-COURSE-001 | `fixtures/synthetic/phase1_course_audio/fx_course_001_multi_course_selection.tja` | multi-COURSE selection | F001 |
| FX-AUDIO-001 | `fixtures/synthetic/phase1_course_audio/fx_audio_001_wave_path_offset.tja` | WAVE/PATH_WAV/audio reference | F002,F003 |
| FX-COMPAT-001 | `fixtures/synthetic/phase1_course_audio/fx_compat_001_nextsong_report.tja` | Dan/NEXTSONG report | F048 |
| FX-COMPAT-002 | `fixtures/synthetic/phase1_course_audio/fx_compat_002_bga_camera_lyrics_report.tja` | BGA/camera/object/lyrics report | F049 |
| FX-INTEGRATED-001 | `fixtures/synthetic/phase1_course_audio/fx_integrated_001_mixed_gimmick_smoke.tja` | integrated timing/scroll/roll/branch smoke | F005,F010,F014,F020,F024,F033 |
| FX-INTEGRATED-002 | `fixtures/synthetic/phase1_course_audio/fx_integrated_002_long_load_smoke.tja` | long/high-load deterministic smoke | F008,F036,F046 |

## 2. Assertion strategy

Every fixture must emit a `fixture_result` object containing:

- `fixture_id`
- `parse_status`
- `unsupported_reports`
- `scheduled_note_count`
- `event_count_by_type`
- `branch_routes_observed`
- `timing_anomalies`
- `score_summary`
- `gauge_summary`

Timing-sensitive fixtures must include expected rational positions, not only millisecond values. Milliseconds are derived from BPM/measure/offset and are checked with a strict tolerance after the rounding policy is implemented.

## 3. Golden policy

Golden files are not updated by implementation sessions. Golden updates require:

1. coverage reviewer approval;
2. reference to `research/opentaiko/10_phase1_adoption_decisions.md`;
3. fixture traceability update;
4. regenerated timing log schema compatibility check.
