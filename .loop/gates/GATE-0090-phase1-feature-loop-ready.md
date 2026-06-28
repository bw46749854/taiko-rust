# GATE-0090: Phase1 feature loop ready

Status: active
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that Phase1 gameplay feature tickets can be selected, executed, QA-reviewed, rejected, and routed back into repair tickets without extra human judgement.

## Autonomy scorecard impact

- A2 Ticket / gate machine-readability: the feature ticket manifest provides deterministic ticket ordering and dependency evidence.
- A4 Executable test harness: every gameplay feature ticket must declare command evidence.
- A5 Timing / audio self-verification: timing-sensitive tickets require timing analyzer evidence.
- A6 Regression / CI enforcement: QA run and QA verdict are mandatory for all gameplay feature tickets.
- A7 Failure feedback loop: rejects must route through failure reports and proposed repair tickets.

## Required inputs

- Passed `GATE-0080`
- `TKT-0060` Done
- `docs/74_phase1_feature_loop_entry_contract.md`
- `docs/75_phase1_feature_ticket_manifest_schema.md`
- `docs/76_phase1_feature_acceptance_command_matrix.md`
- `operations/phase1_feature_ticket_manifest.toml`
- `scripts/check_phase1_feature_loop_static.py`
- `crates/taiko_cli/src/lib.rs`
- `reports/phase1_feature_loop/phase1_feature_validate.json`
- `reports/phase1_feature_loop/phase1_feature_plan.json`

## Required commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_phase1_feature_loop_static.py
taiko_cli phase1 feature validate --manifest operations/phase1_feature_ticket_manifest.toml --format json
taiko_cli phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json
taiko_cli loop next --format json
```

## Pass criteria

| Check | Required result |
|---|---|
| Manifest validation | JSON `verdict` is `pass` |
| Feature count | `feature_ticket_count` equals manifest entry count |
| First feature ticket | first eligible gameplay ticket is `TKT-0005` or a machine-readable `block` caused only by missing prerequisite evidence |
| QA evidence floor | every feature ticket requires QA run and QA verdict commands |
| Failure route | every feature ticket has `failure_route_required = true` |
| Acceptance docs | all acceptance docs referenced by the manifest exist |
| Deprecated crates | no deprecated crate names appear in the manifest |
| Human judgement removal | no feature ticket can be approved without JSON QA verdict and next-ticket transition evidence |

## Reject conditions

- `operations/phase1_feature_ticket_manifest.toml` is missing or invalid;
- a manifest ticket references a missing ticket, missing doc, or deprecated crate;
- any gameplay feature ticket lacks QA verdict evidence;
- any gameplay feature ticket lacks failure-route evidence;
- `TKT-0005` can start without `TKT-0060` and `GATE-0090`;
- Control Session must infer ordering or acceptance from prose.

## Failure handling

- `reject`: create a failure report with category `phase1_feature_manifest_error` or `feature_ticket_transition_error`, then propose a repair ticket through failure feedback route.
- `block`: list missing gate reports or missing generated JSON reports and keep gameplay tickets Blocked.
- `pass`: allow `TKT-0005` to become eligible according to dependency checks.

## Output

- feature manifest validation JSON;
- feature plan JSON;
- command log;
- worktree separation evidence;
- gate report at `.loop/session_logs/GATE-0090-report.md`.

## Next-ticket transition

- `pass`: `TKT-0005` may become eligible as the first Phase1 gameplay feature ticket.
- `reject`: route to failure feedback route and proposed repair ticket.
- `block`: keep all gameplay feature tickets Blocked until missing evidence exists.
