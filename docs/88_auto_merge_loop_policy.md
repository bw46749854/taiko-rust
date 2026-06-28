# 88. Auto-Merge Loop Policy

Status: canonical

## Purpose

loop run-once controller establishes the controller foundation for an autonomous loop that can eventually merge passing work without human approval. The immediate implementation is `loop run-once`; later steps add metadata enforcement, repair-ticket materialization, Codex Automation operation, and auto-merge workflows.

This policy adopts auto-merge as the target state for this project. The repository does not contain production databases, commercial assets, or external API side effects that require human merge approval. The risk model is therefore loop-quality drift, history pollution, and unbounded execution, not data exfiltration or production destruction.

## Core rule

A merge is permitted only after machine evidence shows:

- selected ticket and branch metadata are consistent,
- static checks pass,
- Rust preflight passes when required,
- QA verdict is `pass` when the ticket touches implementation/runtime/test behavior,
- no user-selected assets are committed,
- session separation evidence exists,
- retry budget is not exceeded,
- next-ticket transition evidence exists.

loop run-once controller does not enable automatic merge by itself. It produces the state-machine and `run-once` plan surface that later steps use to drive merge decisions.

## Controller responsibility split

`taiko_cli loop run-once` owns only the next-action decision. It must not silently perform broad repository mutation.

| Mode | Responsibility |
|---|---|
| `--mode plan` | Inspect tickets, gates, failures, and return the next action as JSON/Markdown without side effects. |
| `--mode apply` | Write controller artifacts under `reports/loop/<run_id>/` and render the next Codex prompt. |

loop run-once controller `apply` does not mark gameplay tickets Ready, Done, or merged. Ticket mutation remains controlled by existing gate/QA/merge scripts until later steps add stronger metadata enforcement.

## Plus-plan operation rule

The core controller must not require `OPENAI_API_KEY`, `CODEX_API_KEY`, or API-metered Codex execution. Codex Cloud, Codex App, CLI, or Automations may read the generated prompt and perform the implementation using the ChatGPT plan surface. GitHub Actions may run deterministic checks and future auto-merge logic without invoking an API-key AI worker.

## Failure routing preview

The controller emits one of these next actions:

- `start_worker`: a Ready ticket with satisfied dependencies exists.
- `classify_failure`: open failure reports exist and no Ready ticket can be selected.
- `wait_for_ready_ticket`: no eligible Ready ticket exists.

Later steps extend this to `run_qa`, `merge`, `materialize_repair`, `materialize_blocker_repair`, and `revert_regression`.

## Generated artifacts

`loop run-once --mode apply` writes:

- `reports/loop/<run_id>/controller_plan.json`
- `reports/loop/<run_id>/controller_plan.md`
- `reports/loop/<run_id>/next_codex_prompt.md`

These artifacts are controller evidence, not acceptance evidence for Rust preflight, QA, or Phase1 gameplay.


## Codex automation handoff note

ChatGPT-plan Codex operation does not enable auto-merge. It ensures the worker handoff can run through Codex Cloud, Codex App Automations, or Codex CLI signed in with ChatGPT. GitHub Actions remain deterministic and must not invoke `openai/codex-action@v1`.


## auto-merge controller update

The auto-merge controller adds `.github/workflows/loop-controller.yml`, `scripts/check_auto_merge_conditions.py`, `scripts/loop_auto_merge_pr.sh`, and `scripts/loop_revert_last_merge.sh`. GitHub Actions may perform gate/merge/advance mechanics but must not call AI providers or require `OPENAI_API_KEY`.

## OPS-0006 candidate discovery update

OPS-0006 adds deterministic candidate discovery before merge execution. `loop-controller` may inspect open PR metadata through `gh pr list --state open --json number,title,body,baseRefName,headRefName,headRefOid,isDraft,labels,statusCheckRollup`, but it must not checkout untrusted PR head code.

The controller writes:

- `reports/loop/candidates/open_prs.json`
- `reports/loop/candidates/candidate_plan.json`
- `reports/loop/candidates/candidate_plan.md`

`reports/loop/candidates/candidate_plan.json` follows `schemas/auto_merge_candidate_schema.md`. The selector is `scripts/select_auto_merge_candidate.py`.

A `pass` candidate requires exactly one open PR with `loop:automerge`, base branch `main`, a PR head SHA, ticket id, session metadata path, QA verdict path, and every required check context in a successful state. A `block` verdict is used for pending evidence or multiple passing candidates. A `reject` verdict is used for fixed policy violations or failed required checks.

## OPS-0007 ticket advancement update

OPS-0007 links merge history to ticket lifecycle state. A candidate PR is not considered fully advanced until `scripts/loop_advance_ticket.py` consumes `reports/loop/merge_history/<run_id>.json` and writes `reports/loop/ticket_transitions/<run_id>.json`.

The fixed rule is: the merged ticket becomes `Done`, the next dependency-satisfied ticket becomes `Ready`, and gameplay implementation tickets remain blocked during the OPS migration rail.


## OPS-0008 handoff after merge

After a merge and ticket transition, the controller emits worker handoff artifacts with `scripts/loop_emit_worker_handoff.py`. The handoff appears under `reports/loop/worker_handoff/` and names the next Ready ticket, branch, worktrees, session metadata path, allowed paths, forbidden paths, and required commands. This is not an AI call; it is deterministic controller evidence.
