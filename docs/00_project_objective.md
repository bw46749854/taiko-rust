# 00. Project Objective: Autonomous Phase1 Loop

Status: canonical
Last updated: 2026-06-25

## 1. Top-level objective

The top-level objective of this repository is not merely to prepare documents, and not merely to implement a Phase1 rhythm game by hand.

The top-level objective is:

> Build a self-driving AI session loop where separated AI sessions read tickets, implement work, verify results, detect failures, route failures back into repair tickets, and advance to the next ticket without additional human design or judgement.

All documentation, tickets, gates, prompts, fixtures, reports, scripts, and future Rust code are evaluated by whether they increase that autonomous loop operational capability.

## 2. Primary evaluation question

For every package revision, gate, and ticket, evaluate this question first:

> How much closer is the repository to a state where AI sessions can read a ticket, implement it, verify it, reject it when evidence fails, create or select the next repair ticket, and continue the loop without extra human judgement?

Bootstrap completeness is a supporting metric. Phase1 gameplay feature coverage is also a supporting metric. The controlling metric is autonomous loop operational readiness.

## 3. Non-goals for evaluation

The following are not sufficient success criteria:

- The repository contains many documents.
- The first ticket is readable.
- The bootstrap checks pass while no implementation substrate exists.
- A single implementation session reports success on its own work.
- A feature appears to work without machine-checkable regression evidence.

These may be useful intermediate facts, but they do not prove autonomous loop operation.

## 4. Required loop behavior

The target loop must support this sequence:

1. Control Session selects exactly one Ready ticket using machine-readable dependencies and gates.
2. Ticket Implementation Session creates a plan in a separate worktree.
3. Design Review Session reviews the plan before implementation.
4. Implementation Session changes only ticket-scoped files.
5. Required commands run and produce machine-readable evidence.
6. QA / Regression Session reruns validation in a separate worktree.
7. QA returns `pass`, `reject`, or `block`.
8. A reject result produces a failure report with category, reproduction command, expected result, actual result, and proposed repair scope.
9. Control Session routes the failure into an existing repair ticket or creates a new repair ticket.
10. The next ticket is selected by gate state, dependency state, and evidence, not by ad hoc judgement.

## 5. Implication for autonomy scorecard

autonomy scorecard changes the package from “bootstrap documents are healthy” to “all bootstrap documents are evaluated against autonomous loop operation.”

autonomy scorecard does not implement the Rust workspace. It defines the scorecard, gate transition rules, failure feedback protocol, and Loop CLI contract that make the next implementation step machine-checkable.
