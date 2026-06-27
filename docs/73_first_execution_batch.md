# 73. First Execution Batch

Status: canonical

## Batch 0

Only one ticket is Ready:

| Ticket | Status | Reason |
|---|---:|---|
| OPS-0001 | Ready | Creates the operational migration rail and freezes gameplay implementation tickets |

`OPS-0002` through `OPS-0009`, `TKT-0000`, and all implementation tickets are Blocked.

## Batch 0 instructions

Control Session performs:

1. Read `AGENTS.md`.
2. Read `docs/00_project_objective.md`.
3. Read `docs/05_autonomy_scorecard.md`.
4. Read `docs/06_gate_transition_rules.md`.
5. Read `docs/07_failure_feedback_protocol.md`.
6. Read `docs/40_loop_cli_contract.md`.
7. Read `.loop/tickets/OPS-0001.md`.
8. Read `.loop/gates/GATE-OPS-0000-migration-ready.md`.
9. Run `scripts/check_bootstrap_consistency.sh`.
10. Run `scripts/check_autonomy_scorecard.py`.
11. Run `scripts/list_ready_tickets.sh` and confirm only `OPS-0001` is Ready.
12. Produce `.loop/session_logs/GATE-0000-report.md` using `templates/gate_report_template.md`.
13. The report must include pass/reject/block verdict, command log, autonomy scorecard delta, and next-ticket transition evidence.
14. Ask Design Review Session to review the gate report.

## Batch 1 unlock

After `OPS-0001` is Done, Control Session may move `OPS-0002` to Ready. After `OPS-0009` and `GATE-OPS-0000` pass, the original implementation gate sequence may resume. After `GATE-0000`, `GATE-0010`, and `GATE-0020` pass, Control Session may move `TKT-0001` to Ready.

`TKT-0001` now includes the Rust workspace skeleton and Loop CLI MVP. It is the next infrastructure ticket because autonomous loop operation requires machine-readable ticket/gate orchestration before parser/runtime implementation expands.

No parser/runtime ticket moves to Ready before `TKT-0001` is Done and `GATE-0030` passes.
