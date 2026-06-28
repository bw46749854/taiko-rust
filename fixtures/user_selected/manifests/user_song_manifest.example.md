# User Song Manifest Example

The concrete parser may accept YAML, JSON, or TOML. This example uses YAML-like notation for readability.

```yaml
schema_version: phase1-user-song-manifest/v1
suite_id: local-phase1-standard-10
asset_policy:
  assets_committed_to_repo: false
  local_paths_required: true
  allow_missing_audio_for_parse_only: false
songs:
  - song_id: c01_basic
    display_name: Local basic chart
    category_id: C01
    chart_path: /absolute/local/path/basic_chart.tja
    audio_root: /absolute/local/path/audio
    selected_course: Oni
    declared_features: [F001, F002, F011, F012, F021, F044, F045, F046]
    expected_branch_routes: []
    expected_unsupported_commands: []
    pass_criteria:
      must_reach_song_end: true
      max_fatal_timing_anomalies: 0
      max_parse_errors: 0
      allow_parse_warnings: true
      require_score_summary: true
      require_gauge_summary: true
      require_deterministic_replay: true

  - song_id: c02_mixed_subdivision
    category_id: C02
    chart_path: /absolute/local/path/mixed_subdivision.tja
    selected_course: Oni
    declared_features: [F008, F009, F010, F020, F022]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c03_timing
    category_id: C03
    chart_path: /absolute/local/path/bpm_measure_offset.tja
    selected_course: Oni
    declared_features: [F003, F004, F005, F006, F007]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c04_roll
    category_id: C04
    chart_path: /absolute/local/path/roll_balloon.tja
    selected_course: Oni
    declared_features: [F014, F015, F016, F017, F018, F019]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c05_branch_accuracy
    category_id: C05
    chart_path: /absolute/local/path/branch_accuracy.tja
    selected_course: Oni
    declared_features: [F024, F025, F026, F027, F029, F030]
    expected_branch_routes: [N, E, M]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c06_branch_roll_score
    category_id: C06
    chart_path: /absolute/local/path/branch_roll_score.tja
    selected_course: Oni
    declared_features: [F024, F025, F026, F027, F028, F031, F032]
    expected_branch_routes: [N, E, M]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c07_scroll
    category_id: C07
    chart_path: /absolute/local/path/scroll_overtake.tja
    selected_course: Oni
    declared_features: [F033, F034, F035, F036, F037, F038]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c08_hb_bm_special
    category_id: C08
    chart_path: /absolute/local/path/hb_bm_special.tja
    selected_course: Oni
    declared_features: [F039, F040, F041, F042, F043]
    expected_unsupported_commands: []
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c09_integrated
    category_id: C09
    chart_path: /absolute/local/path/integrated_gimmicks.tja
    selected_course: Oni
    declared_features: [F005, F010, F014, F020, F024, F025, F033, F037]
    expected_branch_routes: [N, E, M]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }

  - song_id: c10_long_high_load
    category_id: C10
    chart_path: /absolute/local/path/long_high_load.tja
    selected_course: Oni
    declared_features: [F008, F036, F046]
    pass_criteria: { must_reach_song_end: true, max_fatal_timing_anomalies: 0, max_parse_errors: 0, allow_parse_warnings: true, require_score_summary: true, require_gauge_summary: true, require_deterministic_replay: true }
```
