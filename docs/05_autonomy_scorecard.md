# 05. Autonomy Scorecard

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

This scorecard is the controlling evaluation metric for the project.

It answers:

> How close is the repository to a state where AI sessions can read a ticket, implement it, verify it, detect failure, route failure back into repair work, and advance to the next ticket without additional human design or judgement?

## 2. Score axes

| Axis ID | Axis | Weight | What earns points |
|---|---|---:|---|
| A1 | Session / worktree governance | 10 | Separate roles, separate worktrees, no self-approval, scoped branches |
| A2 | Ticket / gate machine-readability | 15 | Status, dependencies, prerequisites, pass/fail criteria, and next-ticket selection are parseable |
| A3 | Buildable Rust substrate | 15 | Workspace, crates, binaries, cargo checks, and CLI entrypoint exist |
| A4 | Executable test harness | 15 | Fixtures, manifest validation, parser validation, JSON reports, and rerunnable commands exist |
| A5 | Timing / audio self-verification | 20 | Headless autoplay, timing logs, analyzer thresholds, and cause categories exist |
| A6 | Regression / CI enforcement | 15 | CI runs required gates and rejects regressions using machine-readable output |
| A7 | Failure feedback loop | 10 | QA failures become categorized reports and repair tickets without ad hoc judgement |

Total: 100.

## 3. Step5 baseline estimate

| Axis ID | Weight | Step5 estimate | Reason |
|---|---:|---:|---|
| A1 | 10 | 8 | Session topology and worktree policy exist |
| A2 | 15 | 7 | Ticket/gate files exist, but CLI orchestration is absent |
| A3 | 15 | 0 | Rust workspace does not exist |
| A4 | 15 | 4 | Fixtures and manifest exist; executable harness does not |
| A5 | 20 | 4 | Timing schema/spec exist; analyzer implementation does not |
| A6 | 15 | 2 | Bootstrap scripts exist; cargo/CI regression gate does not |
| A7 | 10 | 2 | Failure template exists; failure-to-ticket route does not |
| **Total** | **100** | **27** | Operationally still a document-and-fixture bootstrap package |

## 4. Step6 target estimate

| Axis ID | Weight | Step6 target | Reason |
|---|---:|---:|---|
| A1 | 10 | 8 | Governance remains stable |
| A2 | 15 | 9 | Scorecard, transition rules, and gate mappings become explicit |
| A3 | 15 | 0 | Rust workspace remains Step7 scope |
| A4 | 15 | 4 | Harness implementation remains Step8 scope |
| A5 | 20 | 4 | Analyzer implementation remains Step10 scope |
| A6 | 15 | 3 | Autonomy scorecard check joins bootstrap validation |
| A7 | 10 | 4 | Failure feedback protocol becomes explicit |
| **Total** | **100** | **32** | Step6 improves measurability, not runtime execution |

## 5. Required evidence by ticket type

| Ticket type | Required machine evidence |
|---|---|
| Documentation / contract | Reference integrity check, autonomy scorecard check, reviewer report |
| Workspace / CLI | `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, CLI command output |
| Parser / chart | Fixture validation JSON, compatibility report, parser unit tests |
| Timing / judgement | Timing log JSON, analyzer JSON, threshold summary |
| Runtime / headless | Headless autoplay JSON, note/hit/miss summary, panic-free run |
| Score / gauge | Golden comparison, boundary tests, regression summary |
| QA / regression | QA verdict JSON, failure report for every reject |

## 6. Score update protocol

Every gate report must include:

- Current score by axis.
- Axis deltas caused by the ticket or gate.
- Evidence supporting each delta.
- Remaining blockers for the next maturity level.
- The next ticket that can be selected after the gate result.

No ticket may claim score improvement without evidence that another session can verify.

## 7. Step7-Step10 operational estimate

The current package includes the first executable loop substrate and timing evidence path. Rust-enabled sessions must still prove the estimate with cargo and CLI output.

| Axis ID | Weight | Step10 estimate | Reason |
|---|---:|---:|---|
| A1 | 10 | 8 | Governance remains stable |
| A2 | 15 | 11 | Loop CLI, gate dry-run, next-ticket selection, and timing gate contracts exist |
| A3 | 15 | 10 | Canonical Rust workspace and CLI crates exist; cargo proof still requires Rust-enabled QA |
| A4 | 15 | 12 | Fixture validation and headless autoplay JSON evidence exist |
| A5 | 20 | 12 | Timing analyzer MVP emits threshold metrics and failure categories; final OpenTaiko timing precision remains downstream |
| A6 | 15 | 5 | Static checks cover loop/fixture/headless/timing command surfaces; CI is still future work |
| A7 | 10 | 5 | Failure categories and protocol exist; automatic failure-to-ticket generation is still future work |
| **Total** | **100** | **63** | Operational loop is now partially executable, but not yet fully self-repairing or CI-enforced |

Step10 raises operational readiness by adding the first machine-readable timing self-verification surface. It does not raise Phase1 gameplay completion by itself.

## 8. failure feedback route operational estimate

The failure feedback route package adds executable failure feedback routing. Rust-enabled sessions must still prove the estimate with cargo and CLI output.

| Axis ID | Weight | failure feedback route estimate | Reason |
|---|---:|---:|---|
| A1 | 10 | 8 | Governance remains stable |
| A2 | 15 | 12 | Failures and repair tickets now have machine-readable command surfaces |
| A3 | 15 | 10 | Workspace and CLI remain present; cargo proof still requires Rust-enabled QA |
| A4 | 15 | 12 | Fixture and headless evidence remain executable surfaces |
| A5 | 20 | 12 | Timing analyzer MVP remains the precision evidence surface |
| A6 | 15 | 6 | Static checks cover failure feedback; CI workflow enforcement remains future work |
| A7 | 10 | 8 | Failure reports can be ingested and converted into repair-ticket proposals |
| **Total** | **100** | **68** | Operational loop can now route rejects back into repair work, but is not yet CI-enforced |

The failure feedback route raises self-repair readiness. It does not raise Phase1 gameplay completion by itself.
