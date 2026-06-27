# GATE-0080: QA regression ready

Status: active
Owner: Control Session
Reviewer: QA / Regression Session

## Purpose

Confirm that a separate QA / Regression Session can run the autonomous regression chain, produce `pass`, `reject`, or `block`, and route rejects into the Step11 failure-feedback loop without extra human judgement.

## Autonomy scorecard impact

- A1 Session / worktree governance: QA verdict requires a separate QA worktree and forbids implementation self-approval.
- A2 Ticket / gate machine-readability: QA verdicts are normalized JSON values.
- A5 Timing / audio self-verification: timing analyzer evidence is consumed by QA rather than manually inspected.
- A6 Regression / CI enforcement: the minimum regression chain is represented as `qa run`, `qa compare`, and CI workflow commands.
- A7 Failure feedback loop: `reject` must route to failure report and repair ticket proposal.

## Required inputs

- Passed `GATE-0070`
- `TKT-0050` Done
- `docs/49_qa_regression_gate_contract.md`
- `docs/48_failure_feedback_loop_contract.md`
- `.github/workflows/phase1-loop.yml`
- `crates/taiko_cli/src/lib.rs`
- `scripts/check_qa_regression_static.py`
- `reports/qa/README.md`
- `reports/qa/phase1_loop.qa.json`
- `reports/qa/phase1_loop.verdict.json`

## Required commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
scripts/check_qa_regression_static.py
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa compare --baseline reports/baseline --current reports/current --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

## Pass criteria

| Check | Required result |
|---|---|
| QA run verdict | JSON `verdict` is `pass` or a justified `reject` routed to failure feedback |
| QA compare verdict | JSON `verdict` is `pass`, or `block` with missing baseline/current listed explicitly |
| QA verdict normalization | JSON `verdict` is one of `pass`, `reject`, `block` |
| Failure route | Any `reject` has a failure report path and repair-ticket proposal path |
| Session separation | QA evidence declares a QA worktree distinct from the implementation worktree |
| CI enforcement | `.github/workflows/phase1-loop.yml` contains fmt, clippy, test, fixture, headless, timing, and qa commands |
| Human judgement removal | QA Session does not need to manually infer pass/reject/block from prose logs |

## Reject conditions

- QA command surface does not compile in a Rust-enabled environment;
- QA JSON output omits required fields from `docs/49_qa_regression_gate_contract.md`;
- a `reject` cannot be converted into a failure report and repair ticket;
- implementation worktree and QA worktree are the same;
- QA Session must inspect prose logs to infer verdict.

## Failure handling

- `reject`: create a failure report using `templates/failure_report_template.md`, then run `taiko_cli loop ticket propose --from-failure ... --format json`.
- `block`: list missing reports, missing baseline/current directories, missing command output, or missing worktree separation evidence.
- `pass`: archive QA JSON reports and allow Phase1 gameplay feature tickets to become eligible according to dependency tables.

## Output

- QA run JSON;
- QA compare JSON;
- QA verdict JSON;
- CI command log;
- worktree separation evidence;
- failure report and proposed repair ticket when rejected.

## Next-ticket transition

- `pass`: `TKT-0060` may become eligible to validate the Phase1 feature-loop manifest before `TKT-0005` can start.
- `reject`: route to Step11 failure feedback and proposed repair ticket.
- `block`: keep Phase1 gameplay feature tickets Blocked until QA evidence can be generated.
