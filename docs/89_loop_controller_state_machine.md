# 89. Loop Controller State Machine

Status: canonical

## Purpose

This document defines the Step17 `run-once` controller state machine. The state machine converts repository state into one next action so Codex Cloud, Codex Automations, CLI, or a future GitHub workflow can drive the loop repeatedly without ad hoc human judgement.

## Step17 state set

| State | Meaning | Step17 next action |
|---|---|---|
| `ready_ticket` | At least one `Status: Ready` ticket has satisfied dependencies. | `start_worker` |
| `open_failures` | Failure reports exist and no eligible Ready ticket can be selected. | `classify_failure` |
| `no_ready_ticket` | No Ready ticket is eligible and no failure route can be selected. | `wait_for_ready_ticket` |

## Future states reserved by policy

The Step17 output schema reserves room for later steps:

- `claimed`
- `implementation_running`
- `pull_request_open`
- `ci_pending`
- `qa_pending`
- `mergeable`
- `merged`
- `done`
- `rejected`
- `blocked`
- `repair_ready`

Step17 does not implement these transitions. They are introduced after session metadata, role worktree enforcement, repair materialization, and auto-merge workflows exist.

## Command contract

```bash
taiko_cli loop run-once --mode plan --format json
taiko_cli loop run-once --mode apply --format json
scripts/loop_run_once.sh --mode plan
scripts/loop_run_once.sh --mode apply
```

## JSON fields

The JSON output must include:

- `run_id`
- `mode`
- `state`
- `verdict`
- `selected_ticket`
- `next_action`
- `reason`
- `branch`
- `implementation_worktree`
- `review_worktree`
- `qa_worktree`
- `controller_report_json`
- `controller_report_markdown`
- `next_codex_prompt`
- `required_commands`
- `missing_gate_evidence`
- `open_failures`
- `artifacts_written`

## Branch and worktree preview

The controller previews deterministic branch and worktree names. These names are planning evidence in Step17 and become enforcement targets in Step18.

| Role | Path |
|---|---|
| Implementation | `worktrees/impl/<ticket-id>` |
| Review | `worktrees/review/<ticket-id>` |
| QA | `worktrees/qa/<ticket-id>` |
| Test Infrastructure | `worktrees/test-infra/<ticket-id>` |

Step17 fixes the controller's owner-session normalization so `Test Infrastructure Session` resolves to the `test/` branch prefix.

## Apply-mode artifact rule

The Rust `taiko_cli loop run-once --mode apply` command writes planning artifacts only under `reports/loop/<run_id>/`. GitHub Actions controller apply mode is separate: after OPS-0006/OPS-0007 it may merge a passing PR, write merge history, and advance tickets through `scripts/loop_advance_ticket.py`.


## Step20 prompt fallback

When Rust is unavailable, `scripts/render_next_codex_prompt.py --mode automation` may generate the same class of `reports/loop/<run_id>/next_codex_prompt.md` handoff artifact. This fallback is deterministic, does not call an OpenAI API, and exists only to keep Codex Cloud/App Automation setup usable before Rust runtime validation is available.


## Step21 update

Step21 adds `.github/workflows/loop-controller.yml`, `scripts/check_auto_merge_conditions.py`, `scripts/loop_auto_merge_pr.sh`, and `scripts/loop_revert_last_merge.sh`. GitHub Actions may perform gate/merge/advance mechanics but must not call AI providers or require `OPENAI_API_KEY`.

## OPS-0006 candidate discovery states

OPS-0006 extends the GitHub controller side with PR candidate states:

| State | Meaning | Controller action |
|---|---|---|
| `candidate_pass` | Exactly one `loop:automerge` PR satisfies policy and required checks. | Merge through `scripts/loop_auto_merge_pr.sh` in apply mode. |
| `candidate_block` | Evidence or required checks are pending, no labeled PR exists, or more than one PR is passable. | Wait or materialize follow-up evidence; do not merge. |
| `candidate_reject` | A labeled PR violates fixed policy or a required check failed. | Record rejection evidence; do not merge. |

The candidate plan is written to `reports/loop/candidates/candidate_plan.json`. It is deterministic, network-free after PR JSON capture, and does not invoke Codex/GPT workers.

## OPS-0007 ticket advance states

OPS-0007 extends the GitHub controller with post-merge ticket transition states:

| State | Meaning | Controller action |
|---|---|---|
| `ticket_advance_pass` | Merge history is valid, the merged ticket is or becomes `Done`, and exactly one next ticket is `Ready`. | Persist `reports/loop/ticket_transitions/<run_id>.json` and continue to the next controller phase. |
| `ticket_advance_block` | Merge history is missing, dry-run evidence was supplied to apply mode, dependencies are incomplete, or no next ticket is eligible. | Stop advancement and record blocker evidence. |
| `ticket_advance_reject` | Merge history violates fixed ticket policy or tries to advance a non-OPS ticket while OPS migration is active. | Reject advancement and require repair evidence. |

The transition engine is `scripts/loop_advance_ticket.py`. It does not invoke Codex/GPT workers and does not require API keys.


## OPS-0008 worker handoff states

After `ticket_advance_pass`, the controller enters `worker_handoff_plan`. It runs `scripts/loop_emit_worker_handoff.py` and writes `reports/loop/worker_handoff/latest.json` plus `latest.md`. Outcomes are:

- `worker_handoff_plan`: exactly one Ready ticket is selected and handoff artifacts are emitted.
- `worker_handoff_block`: no Ready ticket or multiple Ready tickets exist.
- `worker_handoff_reject`: handoff policy is violated, such as API-key worker requirements or missing required paths.
