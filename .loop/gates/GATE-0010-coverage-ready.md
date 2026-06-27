# GATE-0010: Coverage Ready Gate

Status: active
Owner: Test Infra Session
Reviewer: QA / Regression Session

## Purpose

Prevent broad parser/runtime implementation from proceeding until fixture and user-selected validation requirements are machine-checkable.

## Autonomy scorecard impact

A4 Executable test harness, A5 Timing / audio self-verification, A6 Regression / CI enforcement.

## Required inputs

- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `docs/coverage/phase1_feature_coverage_matrix.md`
- `docs/coverage/phase1_fixture_to_feature_traceability.md`
- `docs/coverage/phase1_user_song_category_matrix.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`
- `fixtures/synthetic/phase1_synthetic_manifest.schema.md`
- `fixtures/user_selected/manifests/user_song_manifest.schema.md`
- `docs/43_timing_log_schema.md`
- `docs/44_timing_log_analyzer_spec.md`
- `docs/53_ci_commands.md`

## Pass criteria

| Check | Required result |
|---|---|
| Synthetic fixture inventory | 25-35 fixtures declared; Step3 package uses 35 |
| Feature traceability | Every Must implement gameplay feature maps to at least one synthetic fixture |
| User-song categories | 10 standard categories exist |
| Manifest schema | User local paths are referenced without copying assets |
| Analyzer schema | Timing, branch, scroll, score/gauge, compatibility report fields exist |
| CI commands | Synthetic and user-song commands are distinct |

## Next-ticket transition

Pass permits coverage-dependent implementation tickets to become eligible after `GATE-0020`. Reject routes to fixture, manifest, or analyzer-spec repair work. Block lists missing coverage evidence.

## Output

A gate report must be written to `.loop/session_logs/GATE-0010-report.md`.


## Failure handling

- Reject verdicts must produce a failure report using `templates/failure_report_template.md`.
