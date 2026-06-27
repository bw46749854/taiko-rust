# 04. Loop Operational Maturity Model

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

This model classifies how close the repository is to autonomous Phase1 loop operation.

The model is intentionally stricter than bootstrap package health. A package can be well organized and still have low operational maturity when the CLI, test harness, analyzer, and failure feedback loop do not yet exist.

## 2. Maturity levels

| Level | Name | Operational meaning | Typical score range |
|---:|---|---|---:|
| 0 | Document-only concept | Objective exists, but no ticket/gate structure | 0-10 |
| 1 | Bootstrap-ready package | Documents, tickets, gates, prompts, fixture inventory, and scripts exist | 10-30 |
| 2 | Machine-readable orchestration | CLI can inspect tickets, gates, dependencies, and next ticket | 30-45 |
| 3 | Executable validation substrate | Rust workspace, fixture validation, and reports run under cargo/CLI | 45-60 |
| 4 | Headless verification loop | Headless autoplay and timing analyzer produce pass/fail evidence | 60-75 |
| 5 | Failure feedback loop | QA rejects generate repair tickets and rerun paths | 75-85 |
| 6 | Sustained Phase1 autonomous loop | Multiple tickets advance through implementation, QA, repair, and regression without extra human judgement | 85-100 |

## 3. Current Step6 target

Step6 targets Level 1 completion and prepares Level 2.

The expected score after Step6 remains low relative to the final goal because Rust implementation and CLI execution are still absent. Step6 raises quality by making the objective measurable and by making future tickets accountable to the autonomous loop scorecard.

## 4. Mandatory promotion rules

A package or ticket may not claim a maturity level unless the following evidence exists.

| Claimed level | Required evidence |
|---:|---|
| Level 1 | Bootstrap checks, reference checks, fixture manifest validation, no user asset validation, autonomy scorecard check |
| Level 2 | `taiko_cli loop inspect tickets`, `taiko_cli loop inspect gates`, and `taiko_cli loop next` pass |
| Level 3 | `cargo fmt`, `cargo clippy`, `cargo test`, and `taiko_cli fixture validate` pass |
| Level 4 | `taiko_cli headless autoplay` and `taiko_cli timing analyze` produce pass/fail JSON reports |
| Level 5 | `taiko_cli loop failure ingest` and `taiko_cli loop ticket propose` work from QA failure reports |
| Level 6 | At least three implementation tickets complete through separate implementation and QA worktrees with regression evidence |

## 5. Demotion rules

A package or branch must be demoted when any of these occur:

- A Ready ticket lacks machine-checkable acceptance criteria.
- A ticket can be marked Done without separate review or QA evidence.
- A gate requires undocumented judgement rather than explicit pass/fail evidence.
- A failure report cannot be routed to a repair ticket.
- A timing-sensitive change lacks timing log analyzer evidence.
- A fixture-affecting change lacks fixture validation evidence.

## 6. Relationship to Phase1 game completion

Phase1 game implementation completion and loop operational maturity are separate.

A repository can have 0% Phase1 gameplay implementation and still improve loop maturity by adding orchestration, validation, and failure feedback. Conversely, a repository can implement gameplay features while still being immature if QA and regression cannot reject failures independently.
