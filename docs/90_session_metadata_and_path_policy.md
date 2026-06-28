# 90. Session Metadata and Role Path Policy

Status: canonical

## Purpose

Session separation converts the self-approval prevention rule from prose into machine-checkable metadata and path policy.

The goal is not to protect confidential data. The goal is to stop the autonomous loop from accepting its own work without separate Implementation, Review, QA, and Control evidence.

## Required metadata

Every implementation PR that can advance a ticket must contain one metadata file:

```text
reports/session_metadata/<ticket-id>.toml
```

The file must contain non-empty values for:

```toml
schema_version = 1
run_id = "RUN-..."
ticket_id = "TKT-0005"
implementation_session_id = "codex-cloud-impl-..."
review_session_id = "codex-cloud-review-..."
qa_session_id = "codex-cloud-qa-..."
implementation_branch = "impl/TKT-0005-..."
review_branch = "review/TKT-0005-..."
qa_branch = "qa/TKT-0005-..."
control_branch = "control/TKT-0005-..."
implementation_worktree = "worktrees/impl/TKT-0005"
review_worktree = "worktrees/review/TKT-0005"
qa_worktree = "worktrees/qa/TKT-0005"
qa_verdict_path = "reports/qa/TKT-0005.verdict.json"
plan_path = "reports/plans/TKT-0005-plan.md"
command_log_path = "reports/commands/TKT-0005-command-log.md"
preflight_report_path = "reports/preflight/TKT-0005/rust_preflight_report.json"
gate_report_path = ".loop/session_logs/GATE-0005-report.md"
implementation_may_write_code = true
review_may_write_code = false
qa_may_write_code = false
control_may_merge = true
```

## Separation rules

The gate blocks when any of these are true:

- `implementation_session_id` equals `review_session_id`.
- `implementation_session_id` equals `qa_session_id`.
- `review_session_id` equals `qa_session_id`.
- `implementation_worktree` is not `worktrees/impl/<ticket-id>` for implementation work.
- `review_worktree` is not `worktrees/review/<ticket-id>`.
- `qa_worktree` is not `worktrees/qa/<ticket-id>`.
- A QA verdict exists but its `qa_session_id` differs from `qa_session_id`.
- A QA verdict exists but its legacy `session_id` differs from `qa_session_id`.
- A QA verdict exists but its `source_worktree` differs from `qa_worktree`.
- A QA verdict omits any field required by `schemas/qa_verdict_schema.md`.
- A `reject` QA verdict lacks failure classification, repair materialization, or repair-ticket evidence.
- A `block` QA verdict lacks a missing-evidence list or blocker-ticket route.

## Role path policy

Role path policy is defined in `operations/path_policy.toml` and checked by the commands below. The policy file is the canonical allowlist/denylist source for each role, including fixed branch prefixes and required worktree prefixes:

```bash
scripts/check_role_path_policy.py --role impl --branch impl/TKT-0005-example --worktree worktrees/impl/TKT-0005 --changed-file crates/taiko_runtime/src/lib.rs
scripts/check_role_path_policy.py --role qa --branch qa/TKT-0005-example --worktree worktrees/qa/TKT-0005 --changed-file reports/qa/TKT-0005.verdict.json
```

The default policy is:

| Role | Branch prefix | Write focus | Code writes | Deny focus |
|---|---|---|---|---|
| `impl` | `impl/<ticket-id>-...` | `crates/`, `docs/`, `fixtures/synthetic/`, `reports/commands/`, metadata | allowed | `reports/qa/`, `.loop/session_logs/*GATE*.md`, and gate status mutation |
| `qa` | `qa/<ticket-id>-...` | `reports/qa/`, `reports/regression/`, `reports/failures/` | denied | `crates/`, implementation source, gameplay implementation files |
| `review` | `review/<ticket-id>-...` | `reports/reviews/`, review metadata | denied | implementation files |
| `control` | `control/<ticket-id>-...` | `.loop/tickets/`, `.loop/session_logs/`, `reports/loop/`, `operations/` | denied | `crates/` |
| `test-infra` | `test-infra/<ticket-id>-...` | `crates/taiko_test_support/`, `scripts/`, `fixtures/synthetic/`, QA/test docs | allowed | `reports/qa/` |

## PR gate

`loop-pr-gate.yml` runs:

```bash
scripts/check_session_separation.py --pr-gate
scripts/check_role_path_policy.py --pr-gate --branch "$GITHUB_HEAD_REF"
```

The scripts are intentionally Python-only so the separation gate can run even before Rust dynamic preflight succeeds.

## session separation boundary

Session separation does not auto-merge, does not materialize repair tickets, and does not start Phase1 gameplay work. It only makes later auto-merge decisions machine-checkable.


## QA verdict coupling

`qa_verdict_path` points to a JSON file governed by `schemas/qa_verdict_schema.md`. Auto-merge validation treats that schema as mandatory mergeability evidence. A `pass` verdict may merge only when the verdict `ticket_id`, `run_id`, `qa_session_id`, and `source_worktree` match this metadata file. A `reject` verdict must include failure classification and repair materialization evidence. A `block` verdict must include missing evidence and a blocker-ticket route.

Auto-merge requires both `role_path_policy_required = true` and `branch_prefix_policy_required = true` in `operations/auto_merge_policy.toml`; `scripts/check_auto_merge_conditions.py` refuses mergeability when the implementation branch/worktree metadata does not pass `scripts/check_role_path_policy.py`.
