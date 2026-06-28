# User-selected Song Validation

This directory defines how the user supplies real songs for Phase1 validation.

The repository must not include copyrighted song/audio/chart assets. The user places local files outside the repository or in an ignored local directory and references them from the manifest.

## Required validation set

The standard set has 10 categories:

1. Basic chart
2. Mixed subdivision chart
3. BPM/measure/timing chart
4. Roll chart
5. Branch chart A: accuracy route
6. Branch chart B: roll/score/LEVELHOLD route
7. Scroll/overtake chart
8. HB/BM/special visual timing chart
9. Integrated gimmick chart
10. Long/high-load chart

## Workflow

1. Copy `fixtures/user_selected/manifests/user_song_manifest.example.md` to a local YAML/JSON/TOML manifest.
2. Fill local chart and audio paths.
3. Run `taiko_cli user-song validate`.
4. Review `fixtures/user_selected/reports/user_song_validation_report.schema.md` for expected report shape.
5. Commit only the schema and anonymized reports. Do not commit commercial assets.

## Required result

A Phase1 user-song run passes only when all 10 categories reach song end in headless autoplay and timing analyzer emits no fatal anomaly.
