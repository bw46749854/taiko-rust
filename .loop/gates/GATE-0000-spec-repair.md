# GATE-0000: Spec Repair Gate

Status: active
Owner: Control Session
Reviewer: Design Review Session

## Purpose

Prevent implementation from starting before the Phase1 compatibility contract, OpenTaiko research, and acceptance model are internally consistent.

## Autonomy scorecard impact

A1 Session / worktree governance, A2 Ticket / gate machine-readability, A6 Regression / CI enforcement, A7 Failure feedback loop.

## Required inputs

- `docs/00_project_objective.md`
- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `docs/07_failure_feedback_protocol.md`
- `docs/40_loop_cli_contract.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/25_phase1_feature_classification.md`
- `docs/26_phase1_user_selected_song_validation.md`
- `docs/27_phase1_open_taiko_compatibility_boundary.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`
- `docs/70_phase1_ticket_backlog.md`
- `.loop/tickets/TKT-0000.md`
- `fixtures/synthetic/phase1_synthetic_manifest.toml`
- `templates/pr_review_template.md`
- `templates/failure_report_template.md`
- `templates/gate_report_template.md`

## Pass criteria

| Check | Required result |
|---|---|
| Autonomous loop objective exists | `docs/00_project_objective.md` states autonomous AI session loop operation as the top-level objective |
| Autonomy scorecard exists | `docs/05_autonomy_scorecard.md` defines A1-A7 with total weight 100 |
| Phase1 meaning is unambiguous | Normal-play OpenTaiko-compatible completion is the stated target |
| Feature classification exists | Every Step1/Step2 feature is classified as gameplay, parse/report, or non-scope/report |
| Adoption decisions exist | Each major OpenTaiko command family has a Phase1 adoption decision |
| Coverage model exists | Synthetic and user-selected validation both exist |
| Synthetic manifest exists | All 35 synthetic `.tja` fixtures are listed in `fixtures/synthetic/phase1_synthetic_manifest.toml` |
| Operational templates exist | ticket, plan review, PR review, QA report, failure report, and gate report templates exist |
| Bootstrap checks are executable before Rust exists | `TKT-0000` uses repository-local scripts, not `taiko_cli` |
| Initial ticket state is safe | `GATE-0000` remains frozen during operations migration; `OPS-0001` is the only Ready ticket until `GATE-OPS-0000` passes |
| Crate names are canonical | `taiko_domain` is used; deprecated crate names are absent from canonical workspace definitions |
| Self-approval prevention exists | Session topology and worktree policy require separate review |

## Failure handling

- Missing classification returns to Step1 documents.
- Missing research evidence returns to Step2 documents.
- Missing coverage evidence returns to Step3 documents.
- Ticket or prompt mismatch returns to Step6 autonomy scorecard bootstrap documents.

## Next-ticket transition

Pass keeps `TKT-0001` Blocked until `GATE-0010` and `GATE-0020` pass. Reject routes to documentation or bootstrap repair work. Block lists missing inputs.

## Output

A gate report must be written to `.loop/session_logs/GATE-0000-report.md` using `templates/gate_report_template.md`.
