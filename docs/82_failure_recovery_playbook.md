# 82. Failure Recovery Playbook

Status: canonical

## Failure classes and recovery

| Failure | Recovery path |
|---|---|
| Spec ambiguity | Return to `docs/24-27` and `research/opentaiko/10_phase1_adoption_decisions.md` |
| OpenTaiko evidence gap | Spec Extraction Session updates `research/opentaiko/*.md` |
| Coverage gap | Test Infra Session updates coverage matrix and fixtures |
| Parser crash | Create parser bug ticket; attach input minimization |
| Scheduler mismatch | Attach timing log and expected beat/ms table; return to timing ticket |
| Branch route mismatch | Attach branch section log and condition counters |
| Scroll anomaly | Attach scroll mode, SCROLL value, visual timing log |
| Score/gauge mismatch | Attach score/gauge event log and judgement counts |
| Audio offset anomaly | Attach WAVE/PATH_WAV/OFFSET metadata and measured start time |
| User-song manifest violation | Reject local manifest; do not copy assets |
| CI/tooling failure | Separate tooling ticket from gameplay ticket |

## Required bug report fields

- Ticket id
- Fixture or user-song category
- Minimal TJA snippet when allowed
- Command run
- Timing log path
- Analyzer output
- Expected behavior
- Actual behavior
- Suspected component

## Repair loop

1. QA Session files failure report.
2. Control Session classifies failure.
3. Design Review Session assigns target ticket or creates follow-up.
4. Implementation Session fixes in a separate worktree.
5. QA Session reruns targeted and regression checks.
6. Control Session records closure.
