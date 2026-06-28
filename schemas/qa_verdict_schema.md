# QA Verdict Schema

Status: canonical

Canonical path:

```text
reports/qa/<ticket-id>.verdict.json
```

Required fields:

- `ticket_id`
- `run_id`
- `qa_session_id`
- `source_worktree`
- `verdict` (`pass`, `reject`, or `block`)
- `next_action`
- `evidence_inputs` (non-empty array)
- `failure_route` (object)

Cross-file validation:

- `ticket_id`, `run_id`, `qa_session_id`, and `source_worktree` must match `reports/session_metadata/<ticket-id>.toml`.
- `source_worktree` must equal the metadata `qa_worktree`.
- The legacy `session_id` field may be present, but if present it must equal `qa_session_id`.

Verdict-specific requirements:

- `verdict = "reject"` requires `failure_route.classification_path`, `failure_route.materialization_path`, and `failure_route.repair_ticket_id`.
- `verdict = "block"` requires a non-empty `missing_evidence` array plus `failure_route.blocker_ticket_id` and `failure_route.blocker_route`.
- `verdict = "pass"` is the only mergeable verdict.

Validation commands:

```bash
scripts/check_session_separation.py --metadata reports/session_metadata/TKT-0005.toml --require-qa-verdict
scripts/check_auto_merge_conditions.py --metadata reports/session_metadata/TKT-0005.toml --qa reports/qa/TKT-0005.verdict.json --ticket TKT-0005
```
