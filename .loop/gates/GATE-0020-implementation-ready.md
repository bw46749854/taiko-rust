# GATE-0020: Implementation Ready Gate

Status: active
Owner: Control Session
Reviewer: Design Review Session and QA / Regression Session

## Purpose

Allow implementation tickets to move from Blocked to Ready only after specification, research, coverage, session topology, and command contracts are aligned.

## Autonomy scorecard impact

A1 Session / worktree governance, A2 Ticket / gate machine-readability, A3 Buildable Rust substrate, A6 Regression / CI enforcement.

## Required inputs

- Passed `GATE-0000`
- Passed `GATE-0010`
- `AGENTS.md`
- `docs/00_project_objective.md`
- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `docs/07_failure_feedback_protocol.md`
- `docs/40_loop_cli_contract.md`
- `docs/60_session_topology.md`
- `docs/61_worktree_policy.md`
- `docs/62_loop_engineering_flow.md`
- `docs/63_ticket_lifecycle.md`
- `docs/64_review_and_qa_gates.md`
- `docs/70_phase1_ticket_backlog.md`
- `docs/71_ticket_dependency_graph.md`
- `docs/72_milestone_plan.md`
- `docs/73_first_execution_batch.md`
- `docs/80_codex_execution_checklist.md`
- `prompts/60_final_bootstrap_prompt.md`

## Pass criteria

| Check | Required result |
|---|---|
| Ticket dependencies | Parser, scheduler, runtime, analyzer, fixture, user-song tickets are ordered |
| Initial Ready set | `TKT-0001` may become Ready only after this gate passes |
| Review separation | Plan review and final review use separate sessions |
| Loop CLI contract | `docs/40_loop_cli_contract.md` defines machine-readable ticket/gate orchestration commands |
| Commands | Required cargo and validation commands are defined |
| Rollback | Failure recovery playbook covers parse, timing, branch, scroll, audio, score/gauge |

## Next-ticket transition

Pass allows `TKT-0001` to move from Blocked to Ready. Reject routes to loop design or ticket dependency repair. Block keeps all implementation tickets Blocked.

## Output

A gate report must be written to `.loop/session_logs/GATE-0020-report.md`.


## Failure handling

- Reject verdicts must produce a failure report using `templates/failure_report_template.md`.
