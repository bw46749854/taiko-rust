# GitHub Actions Auto-Merge Controller

Status: canonical

## Purpose

Step21 adds the GitHub Actions side of the autonomous loop. Codex Cloud, Codex App Automations, or Codex CLI remain responsible for implementation and repair work under the ChatGPT plan. GitHub Actions does not call OpenAI APIs, does not require `OPENAI_API_KEY`, and does not run `openai/codex-action@v1`.

The controller's responsibility is mechanical:

1. inspect PR/gate state,
2. verify auto-merge conditions,
3. merge a passing PR,
4. record merge history,
5. advance loop state,
6. prepare a deterministic revert path for regressions.

## Boundary

GitHub Actions may:

- run static checks,
- run Rust preflight in a Rust-enabled runner,
- run QA gate commands,
- validate session metadata and path policy,
- validate retry budget,
- merge a PR that satisfies every required condition,
- create a revert branch/PR when regression evidence points to the last autonomous merge.

GitHub Actions must not:

- call AI providers,
- use `OPENAI_API_KEY`,
- start Codex API workers,
- bypass required checks,
- mark tickets Done without merge evidence,
- merge when QA verdict is `reject` or `block`.

## Required auto-merge conditions

A PR is mergeable by the loop controller only when all of these are true:

- `loop-pr-gate` passed,
- `rust-preflight` passed or the ticket is explicitly docs-only,
- `phase1-loop` passed when the ticket touches Phase1 feature work,
- QA verdict exists and is `pass`,
- `reports/session_metadata/<ticket-id>.toml` exists,
- implementation, review, and QA session IDs are distinct,
- role path policy passes,
- `scripts/validate_no_user_assets.sh` passes,
- retry budget permits the transition,
- metadata `head_sha` equals the PR head SHA when a live PR context is available,
- PR branch, metadata, and PR body resolve to the same `ticket_id`,
- PR carries the auto-merge label defined in `operations/auto_merge_policy.toml`.

A PR is never merged when any of these are true:

- missing metadata,
- missing QA verdict,
- QA verdict is `reject`,
- QA verdict is `block`,
- required check failed,
- role path violation,
- user-selected asset payload detected,
- retry limit exceeded,
- forbidden workflow contains AI API worker usage,
- ticket id mismatch.

## Commands

```bash
scripts/check_auto_merge_conditions.py
scripts/check_auto_merge_conditions.py --metadata reports/session_metadata/TKT-0005.toml --qa reports/qa/TKT-0005.verdict.json
scripts/loop_controller_github.sh --mode plan
scripts/loop_controller_github.sh --mode apply
scripts/loop_auto_merge_pr.sh --ticket TKT-0005 --pr 12 --metadata reports/session_metadata/TKT-0005.toml --qa reports/qa/TKT-0005.verdict.json --dry-run
scripts/loop_revert_last_merge.sh --run-id RUN-20260626-0001 --reason regression --dry-run
```

## Workflow

`.github/workflows/loop-controller.yml` is event-driven and scheduled. It runs after the gate workflows complete and can also be started manually.

The workflow never invokes Codex through an API key. It only runs repository scripts and GitHub CLI operations permitted by `GITHUB_TOKEN`.

## Merge history

Successful autonomous merges must write:

```text
reports/loop/merge_history/<run_id>.json
```

The record must contain ticket id, PR number, merge method, base branch, head branch, head SHA, workflow run id, and the evidence paths used by the controller.

## Revert path

Regression evidence after an autonomous merge produces:

```text
reports/regression/<run_id>.json
```

`loop_revert_last_merge.sh` creates a revert branch and opens a revert PR when not in dry-run mode. The revert PR goes through the same gate path as normal changes.

## Step21 non-goals

Step21 does not implement gameplay features. Step21 does not start Codex workers. Step21 does not require API billing. Step21 only makes auto-merge and revert mechanically controllable.


## OPS-0005 controller guard normalization

OPS-0005 makes the controller boundary explicit. `loop-controller.yml` must use `concurrency: loop-controller-main`; a `workflow_run` success guard is mandatory before controller work proceeds. The privileged workflow must not checkout PR head code from untrusted pull requests. It checks out the trusted default branch controller scripts and evaluates GitHub state mechanically.

The canonical required PR checks are `loop-pr-gate / loop-pr-gate`, `rust-preflight / rust-preflight`, `phase1-loop / phase1-loop`, and `phase1-gameplay-entry / phase1-gameplay-entry`. `e2e-smoke-loop / e2e-smoke-loop` is controller-substrate smoke evidence and is not treated as a PR-head required check in this package.

Static checker keywords: workflow_run success guard; privileged workflow must not checkout PR head code.

## OPS-0006 auto-merge candidate discovery

OPS-0006 adds `scripts/select_auto_merge_candidate.py` and the candidate report path `reports/loop/candidates/candidate_plan.json`. The controller first captures open PR metadata to `reports/loop/candidates/open_prs.json`, then classifies PRs into `pass`, `reject`, `block`, or `ignored` without checking out PR head code.

The selector requires:

- `loop:automerge` label,
- base branch `main`,
- non-draft PR,
- PR head SHA,
- ticket id in PR body/title/branch,
- `reports/session_metadata/...` path in PR body,
- `reports/qa/...` path in PR body,
- exact required checks from `operations/auto_merge_policy.toml`.

Only one passing candidate may be selected per controller run. Multiple passing candidates produce `block`. Failed required checks or fixed policy violations produce `reject`. Pending checks or missing eligible PRs produce `block`.

Fixture coverage is stored in:

- `fixtures/loop_controller/pass_candidate.json`,
- `fixtures/loop_controller/reject_candidate.json`,
- `fixtures/loop_controller/block_candidate.json`.

Static validation is performed by `scripts/check_auto_merge_conditions.py`; direct selector validation is performed by `scripts/select_auto_merge_candidate.py --expect pass|reject|block`.

## OPS-0007 ticket advance integration

After `scripts/loop_auto_merge_pr.sh` merges a passing candidate and writes merge history, `loop-controller` calls:

```bash
scripts/loop_advance_ticket.py \
  --merge-history reports/loop/merge_history/<run_id>.json \
  --mode apply \
  --out reports/loop/ticket_transitions/<run_id>.json \
  --markdown reports/loop/ticket_transitions/<run_id>.md \
  --expect pass
```

The resulting ticket transition report records the merged ticket, the next ticket, status updates, and the Ready ticket list after the transition. GitHub Actions remains a verifier/gate/controller and does not call Codex/GPT.


## OPS-0008 worker handoff integration

`loop-controller.yml` runs `scripts/check_worker_handoff_static.py` and emits `reports/loop/worker_handoff/` through `scripts/loop_emit_worker_handoff.py --mode controller`. The controller may upload the handoff as an artifact or feed it to `loop-worker-handoff.yml`. It does not checkout PR head code for privileged logic and does not call an AI worker.
