# Session Metadata Schema

Status: canonical

Canonical path:

```text
reports/session_metadata/<ticket-id>.toml
```

Required fields:

- `schema_version = 1`
- `run_id`
- `ticket_id`
- `implementation_session_id`
- `review_session_id`
- `qa_session_id`
- `implementation_branch`
- `implementation_worktree`
- `review_worktree`
- `qa_worktree`
- `qa_verdict_path`
- `preflight_report_path`
- `implementation_may_write_code`
- `review_may_write_code`
- `qa_may_write_code`
- `control_may_merge`
- `next_action`

Validation command:

```bash
scripts/check_session_separation.py --metadata reports/session_metadata/TKT-0005.toml
```
