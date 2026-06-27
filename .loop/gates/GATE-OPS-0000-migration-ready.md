# GATE-OPS-0000: Operations migration ready

Status: passed
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that repository cleanup, public-readiness hardening, asset-bundle policy, GitHub Actions controller behavior, auto-merge candidate discovery, ticket advancement, and Codex handoff are complete before Phase1 gameplay tickets can start.

## Autonomy scorecard impact

- A1 Session / worktree governance: OPS tickets keep implementation, review, and QA roles separated during migration.
- A2 Ticket / gate machine-readability: OPS tickets define deterministic migration order and machine-checkable completion evidence.
- A6 Regression / CI enforcement: GitHub Actions remains the verifier and gate for every migration PR.
- A7 Failure feedback loop: failed migration checks produce repair or blocker tickets before gameplay resumes.

## Required inputs

- `.loop/tickets/OPS-0001.md` through `.loop/tickets/OPS-0009.md`
- `operations/manifest.md`
- `operations/loop_policy.toml`
- `docs/02_document_index.md`
- `docs/81_human_operator_minimal_steps.md`
- `prompts/60_final_bootstrap_prompt.md`
- `scripts/check_bootstrap_consistency.sh`
- `scripts/ci_local_equivalent.sh`

## Required commands

```bash
scripts/check_bootstrap_consistency.sh
scripts/ci_local_equivalent.sh --static-only
scripts/list_ready_tickets.sh
```

## Pass criteria

| Check | Required result |
|---|---|
| OPS ticket rail | OPS-0001 through OPS-0009 exist and exactly one OPS ticket is Ready at migration start |
| Gameplay freeze | TKT-0005 and downstream gameplay tickets remain Blocked until OPS-0009 completes |
| API-key policy | GitHub Actions does not require OpenAI API keys for verification, gate, merge, or ticket transition control |
| Controller scope | Actions may verify, gate, merge, advance tickets, and emit handoff artifacts, but must not run AI worker code |
| Evidence | Static-only CI and ready-ticket listing are recorded |

## Failure handling

- `reject`: create a repair ticket for inconsistent migration state, stale legacy-preparation dependency, or unsafe workflow privilege.
- `block`: record missing evidence, missing OPS ticket, or missing static check output.
- `pass`: allow the final OPS transition to unlock Phase1 gameplay entry evaluation.

## Output

- Gate report at `.loop/session_logs/GATE-OPS-0000-report.md`.
- Command log.
- Ready-ticket listing.
- Migration risk summary.

## Next-ticket transition

- `pass`: `TKT-0005` may be evaluated by `phase1-gameplay-entry` after OPS-0009 completes.
- `reject`: route to a repair ticket and keep gameplay tickets Blocked.
- `block`: keep exactly one OPS ticket Ready and prevent Phase1 gameplay start.
