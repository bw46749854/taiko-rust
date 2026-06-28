# 84. GitHub PR Loop Contract

Status: canonical

## Purpose

Define the concrete branch, worktree, PR, review, QA verdict, merge, and next-ticket transition path for autonomous loop operation.

This contract closes the gap between ticket execution and durable GitHub state.

## Required command surface

| Command | Purpose |
|---|---|
| `scripts/loop_create_branch.sh <ticket-id>` | Create a deterministic ticket branch without creating a worktree. |
| `scripts/loop_create_worktree.sh <ticket-id>` | Create a deterministic ticket branch and isolated worktree. |
| `scripts/loop_open_pr.sh <ticket-id>` | Push the ticket branch and open a PR with evidence checklist. |
| `scripts/loop_apply_qa_verdict.py --ticket <ticket-id> --verdict <json>` | Convert QA pass/reject/block JSON into ticket transition evidence. |
| `scripts/loop_merge_and_advance.sh <ticket-id>` | Merge a passing PR and print the next-ticket command. |
| `scripts/check_github_pr_orchestration_static.py` | Validate that this GitHub PR orchestration contract remains wired into the package. |

All commands must be safe to run with `--dry-run`.

## Branch naming

| Work type | Branch pattern |
|---|---|
| Bootstrap or gate repair | `loop/<ticket-id>-<slug>` |
| Ticket implementation | `impl/<ticket-id>-<slug>` |
| Test infrastructure | `test/<ticket-id>-<slug>` |
| QA evidence only | `qa/<ticket-id>-<slug>` |
| Review documentation only | `review/<ticket-id>-<slug>` |

The default branch type is inferred from ticket metadata:

- `Owner session: Test Infra Session` -> `test/`;
- `Owner session: QA / Regression Session` -> `qa/`;
- `Owner session: Control Session` -> `loop/`;
- all other implementation tickets -> `impl/`.

## Worktree layout

| Session | Worktree root |
|---|---|
| Control Session | `worktrees/control` |
| Spec Extraction Session | `worktrees/spec` |
| Design Review Session | `worktrees/review` |
| Test Infra Session | `worktrees/test-infra/<ticket-id>` |
| Ticket Implementation Session | `worktrees/impl/<ticket-id>` |
| QA / Regression Session | `worktrees/qa/<ticket-id>` |
| Repair ticket | `worktrees/repair/<ticket-id>` |

`worktrees/` is ignored by Git. Evidence must be copied into tracked text or JSON report files before PR creation.

## PR body requirements

Every ticket PR must contain:

- ticket ID and title;
- owner session and reviewer session;
- branch name and worktree path;
- scope summary;
- required checks copied from the ticket;
- command evidence summary;
- QA verdict path or block reason;
- no-user-asset confirmation;
- next-ticket transition statement.

The PR template is `.github/pull_request_template.md`.

## Review requirements

A PR cannot merge until all are true:

1. `loop-pr-gate` workflow passes;
2. `rust-preflight` workflow passes for implementation PRs touching Rust, runtime, CLI, fixtures, QA, or loop-command behavior;
3. `phase1-loop` workflow passes, or the PR is explicitly a docs-only/bootstrap PR whose required ticket checks do not include Rust commands;
4. Design Review Session or Codex GitHub review has reviewed the diff;
5. QA / Regression Session emits machine-readable verdict evidence for implementation/runtime changes;
6. the implementation session has not approved its own PR.

## QA verdict transition

`loop_apply_qa_verdict.py` maps verdict JSON to transition evidence:

| QA verdict | Ticket transition | Required next action |
|---|---|---|
| `pass` | `Done` candidate | Merge PR, update session log, run next-ticket selection. |
| `reject` | `Rejected` candidate | Create/update failure report, propose repair ticket, block downstream transition. |
| `block` | `Blocked` candidate | Produce missing machine evidence before another implementation attempt. |

The script must not invent acceptance. It only records a deterministic transition from the QA JSON source.

## Merge and advance

`loop_merge_and_advance.sh` may merge only when:

- the PR exists;
- the branch matches the ticket branch pattern;
- the QA verdict source is `pass`, unless the caller passes an explicit docs-only override;
- protected-branch checks have passed in GitHub.

After merge, Control Session runs:

```bash
cargo run -p taiko_cli --bin taiko_cli -- loop next --format json
```

If Rust is unavailable in the control environment, Control Session records the limitation and runs:

```bash
scripts/list_ready_tickets.sh
```

as a bootstrap fallback only.

## Reject and repair path

A rejected PR follows this path:

```text
QA verdict reject
  -> failure report in reports/failures/
  -> taiko_cli loop failure ingest ... --format json
  -> taiko_cli loop ticket propose --from-failure ... --format json
  -> repair ticket materialized under .loop/tickets/
  -> repair branch/worktree
  -> repair PR
  -> QA verdict
```

Downstream gameplay tickets remain Blocked while the reject path has no materialized repair ticket or no passing repair PR.

## Self-approval prevention

Each PR must include `templates/session_run_metadata_template.toml`-compatible metadata. At minimum:

- `ticket_id`;
- `implementation_session_id`;
- `review_session_id`;
- `qa_session_id`;
- `branch`;
- `worktree`;
- `qa_verdict_path`.

`implementation_session_id`, `review_session_id`, and `qa_session_id` must not all be identical. A missing metadata file is a block condition for implementation PRs.

## Initial manual steps

The human operator performs only the following bootstrap actions:

1. create a private GitHub repository;
2. push this package;
3. connect the repository to Codex Cloud;
4. configure Rust in the Codex Cloud environment;
5. add `OPENAI_API_KEY` only if the optional `codex-review` workflow is used;
6. start the first Codex Cloud task with `prompts/60_final_bootstrap_prompt.md`.

After that, ticket selection, PR creation, QA verdict handling, and next-ticket transition must use this contract.

## Rust preflight requirement

Implementation PRs that touch Rust code, `Cargo.toml`, `taiko_cli`, fixture execution, timing analysis, QA verdicts, or Phase1 feature planning must include `rust-preflight` evidence.

Required command:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass
```

A failing `rust-preflight` workflow is not bypassed by prose review. A `block` verdict repairs the CI or Codex Cloud environment. A `reject` verdict routes to failure feedback and repair-ticket selection.


## session separation machine-readable gate

PR prose remains useful for humans, but machine control must use tracked metadata. Implementation PRs that can advance a ticket must include:

```text
reports/session_metadata/<ticket-id>.toml
```

`loop-pr-gate.yml` runs:

```bash
scripts/check_session_separation.py --pr-gate
scripts/check_role_path_policy.py --pr-gate
```

The gate blocks self-approval by requiring distinct implementation, review, and QA session IDs. It also blocks role/path violations such as an Implementation Session writing `reports/qa/*.verdict.json` or a QA Session writing `crates/`.


## auto-merge controller update

The auto-merge controller adds `.github/workflows/loop-controller.yml`, `scripts/check_auto_merge_conditions.py`, `scripts/loop_auto_merge_pr.sh`, and `scripts/loop_revert_last_merge.sh`. GitHub Actions may perform gate/merge/advance mechanics but must not call AI providers or require `OPENAI_API_KEY`.


## OPS-0005 GitHub Actions gate normalization

The normalized required PR check contexts are:

- `loop-pr-gate / loop-pr-gate`
- `rust-preflight / rust-preflight`
- `phase1-loop / phase1-loop`
- `phase1-gameplay-entry / phase1-gameplay-entry`

`operations/auto_merge_policy.toml` is the canonical source for these names. `scripts/check_github_actions_gate_static.py` validates that workflow names, job names, permissions, checkout credential policy, and controller guards stay aligned.
