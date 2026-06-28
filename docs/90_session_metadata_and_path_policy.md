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
implementation_worktree = "worktrees/impl/TKT-0005"
review_worktree = "worktrees/review/TKT-0005"
qa_worktree = "worktrees/qa/TKT-0005"
qa_verdict_path = "reports/qa/TKT-0005.verdict.json"
preflight_report_path = "reports/preflight/TKT-0005/rust_preflight_report.json"
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
- A QA verdict exists but its `session_id` differs from `qa_session_id`.
- A QA verdict exists but its `source_worktree` differs from `qa_worktree`.

## Role path policy

Role path policy is defined in `operations/path_policy.toml` and checked by:

```bash
scripts/check_role_path_policy.py --role impl --changed-file crates/taiko_runtime/src/lib.rs
scripts/check_role_path_policy.py --role qa --changed-file reports/qa/TKT-0005.verdict.json
```

The default policy is:

| Role | Write focus | Code writes |
|---|---|---|
| `impl` | `crates/`, `docs/`, `fixtures/synthetic/`, `reports/commands/`, metadata | allowed |
| `qa` | `reports/qa/`, `reports/regression/`, `reports/failures/` | denied |
| `review` | `reports/reviews/` | denied |
| `control` | `.loop/tickets/`, `.loop/session_logs/`, `reports/loop/`, `operations/` | denied |
| `test-infra` | `crates/taiko_test_support/`, `scripts/`, `fixtures/synthetic/`, QA/test docs | allowed |

## PR gate

`loop-pr-gate.yml` runs:

```bash
scripts/check_session_separation.py --pr-gate
scripts/check_role_path_policy.py --pr-gate
```

The scripts are intentionally Python-only so the separation gate can run even before Rust dynamic preflight succeeds.

## session separation boundary

Session separation does not auto-merge, does not materialize repair tickets, and does not start Phase1 gameplay work. It only makes later auto-merge decisions machine-checkable.
