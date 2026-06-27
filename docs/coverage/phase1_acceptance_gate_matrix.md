# Phase1 Acceptance Gate Matrix

Status: adopted for Step3 coverage design

## 1. Gate sequence

| Gate | Name | Owner session | Input | Output |
|---|---|---|---|---|
| GATE-0000 | Spec repair | Design review session | Step1/Step2 docs | Phase1 scope accepted |
| GATE-0010 | Coverage ready | QA/regression session | Step3 docs + fixture inventory | fixture/user-song coverage accepted |
| GATE-0020 | Implementation ready | Control session | gates 0000/0010 + tickets | implementation batch can start |
| GATE-0100 | Synthetic regression pass | QA/regression session | implemented code + synthetic fixtures | all controlled behavior passes |
| GATE-0200 | User-song validation pass | QA/regression session | local user manifest + implemented code | Phase1 real-song compatibility accepted |

## 2. GATE-0010: coverage-ready checklist

GATE-0010 passes only when every item is true:

- `docs/coverage/phase1_feature_coverage_matrix.md` has no Required feature without a synthetic fixture.
- `docs/coverage/phase1_user_song_category_matrix.md` defines all 10 user song categories.
- `fixtures/user_selected/manifests/user_song_manifest.schema.md` exists.
- `fixtures/user_selected/manifests/user_song_manifest.example.md` exists.
- `fixtures/user_selected/reports/user_song_validation_report.schema.md` exists.
- `docs/43_timing_log_schema.md` includes branch, scroll, gogo, barline, roll, balloon, score, gauge, and compatibility-report fields.
- `docs/44_timing_log_analyzer_spec.md` can evaluate timing, branch, scroll, roll, balloon, score/gauge, and deterministic replay checks.
- `docs/51_fixture_design.md` defines at least 25 synthetic fixtures.
- `docs/53_ci_commands.md` separates synthetic fixture validation from user-selected song validation.

## 3. GATE-0100: synthetic regression pass

Synthetic regression passes when:

```text
cargo fmt --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --emit-timing-log out/synthetic.jsonl
taiko_cli timing analyze --input out/synthetic.jsonl --profile phase1-synthetic
```

All commands must exit 0. The analyzer must report zero fatal anomalies.

## 4. GATE-0200: user-song validation pass

User-song validation passes when:

```text
taiko_cli user-song validate --manifest fixtures/user_selected/manifests/user_song_manifest.yaml --emit-report out/user_song_validation.json
taiko_cli timing analyze --input out/user_song_timing.jsonl --profile phase1-user-selected
```

The validator must confirm:

- 10 categories are present;
- all referenced local chart/audio paths exist;
- all 10 songs reach `song_end` in headless autoplay;
- no fatal timing anomaly is reported;
- score/gauge/clear summaries exist for every song;
- unsupported commands are reported, not silently ignored.

## 5. Phase1 final acceptance

Phase1 is accepted only after both GATE-0100 and GATE-0200 pass on the same code revision.
