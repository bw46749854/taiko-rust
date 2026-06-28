# Phase1 Synthetic Manifest Schema

The concrete TOML manifest is committed at `fixtures/synthetic/phase1_synthetic_manifest.toml`. Required fields:

```toml
schema_version = "phase1-synthetic-manifest/v1"

[[fixtures]]
fixture_id = "FX-CORE-001"
path = "fixtures/synthetic/phase1_core/fx_core_001_basic_don_ka.tja"
primary_features = ["F011"]
expected_event_types = ["course_selected", "note_scheduled", "judgement", "score_update", "gauge_update", "song_end"]
headless_required = true
expected_reports = []
```
