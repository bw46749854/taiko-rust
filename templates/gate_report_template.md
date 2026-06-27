# Gate Report Template

Status: canonical
Purpose: standardize `.loop/session_logs/GATE-<id>-report.md` output for autonomous loop operation.

## 1. Gate metadata

| Field | Value |
|---|---|
| Gate |  |
| Owner session | Control Session |
| Reviewer session | Design Review Session |
| Date |  |
| Commit/range |  |

## 2. Verdict

Choose exactly one:

- [ ] pass
- [ ] reject
- [ ] block

## 3. Required inputs checked

| Input | Present | Notes |
|---|---:|---|
| `AGENTS.md` |  |  |
| gate file |  |  |
| relevant tickets |  |  |
| relevant docs |  |  |
| fixture manifest |  |  |
| templates |  |  |
| autonomy scorecard docs |  |  |

## 4. Commands run

```bash
scripts/check_bootstrap_consistency.sh
scripts/check_reference_integrity.py
scripts/check_autonomy_scorecard.py
scripts/validate_fixture_manifest.py
scripts/validate_no_user_assets.sh
```

## 5. Results

| Check | Result | Evidence |
|---|---|---|
| required files |  |  |
| ready ticket state |  |  |
| canonical crate names |  |  |
| document references |  |  |
| autonomy scorecard governance |  |  |
| gate transition rules |  |  |
| failure feedback protocol |  |  |
| fixture manifest |  |  |
| user asset policy |  |  |

## 6. Autonomy scorecard delta

| Axis ID | Axis | Before | After | Evidence |
|---|---|---:|---:|---|
| A1 | Session / worktree governance |  |  |  |
| A2 | Ticket / gate machine-readability |  |  |  |
| A3 | Buildable Rust substrate |  |  |  |
| A4 | Executable test harness |  |  |  |
| A5 | Timing / audio self-verification |  |  |  |
| A6 | Regression / CI enforcement |  |  |  |
| A7 | Failure feedback loop |  |  |  |

## 7. Failure or block details

Required when verdict is `reject` or `block`.

| Field | Value |
|---|---|
| Failure category |  |
| Missing evidence |  |
| Reproduction command |  |
| Required repair scope |  |
| Proposed repair ticket |  |

## 8. Next-ticket transition evidence

| Field | Value |
|---|---|
| Tickets unlocked by pass |  |
| Tickets kept Blocked |  |
| Repair ticket required by reject |  |
| Missing evidence required by block |  |
| Single selected next ticket |  |
| Reason |  |

## 9. Remaining risks

- 
