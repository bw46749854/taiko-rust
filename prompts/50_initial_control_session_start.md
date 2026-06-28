# Initial Control Session Start

Status: canonical

## Mission

Start the loop with TKT-0000 only and produce the first gate report.

## Mandatory read set

- `AGENTS.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/25_phase1_feature_classification.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
- `docs/coverage/phase1_acceptance_gate_matrix.md`
- `docs/70_phase1_ticket_backlog.md`
- `docs/71_ticket_dependency_graph.md`
- `docs/73_first_execution_batch.md`

## Operating rules

- Use canonical crate names from `AGENTS.md`.
- Do not use `taiko_core` as a crate name.
- Do not bundle user-selected song assets.
- Do not approve your own implementation.
- Record command outputs and remaining risks.
- Treat parser crash, timing anomaly, branch route mismatch, score/gauge mismatch, and unclassified command report as blocking unless the ticket explicitly limits scope.

## Session-specific procedure

1. Read the mandatory read set.
2. Read the current ticket or gate.
3. State the exact files to modify or review.
4. Perform only the session responsibility.
5. Write a concise handoff with evidence and risks.

## Required handoff format

```text
Session:
Ticket/Gate:
Worktree:
Files changed or reviewed:
Commands run:
Result:
Blocking issues:
Next recommended action:
```
