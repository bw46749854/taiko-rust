# Worker Handoff Schema

Status: canonical

`reports/loop/worker_handoff/latest.json` is the machine-readable handoff from GitHub Actions controller to the next Codex worker surface.

## Required fields

| Field | Type | Required value |
|---|---:|---|
| `schema` | string | `schemas/worker_handoff_schema.md` |
| `run_id` | string | controller or local run id |
| `mode` | string | `plan`, `controller`, or `issue` |
| `verdict` | string | `plan`, `block`, or `reject` |
| `selected_ticket` | string/null | the single Ready ticket id |
| `selected_ticket_path` | string/null | path to selected ticket |
| `selected_ticket_title` | string/null | selected ticket title |
| `branch` | string/null | worker branch |
| `implementation_worktree` | string/null | implementation worktree |
| `review_worktree` | string/null | detached review worktree |
| `qa_worktree` | string/null | QA worktree |
| `session_metadata_path` | string/null | implementation session metadata path |
| `qa_verdict_path` | string/null | expected QA verdict path, not authored by implementation session |
| `required_reads` | array | files the worker must read |
| `allowed_paths` | array | path prefixes allowed for this handoff |
| `forbidden_paths` | array | path prefixes or globs forbidden for this handoff |
| `required_commands` | array | deterministic checks the worker or PR must reference |
| `next_prompt_path` | string | `reports/loop/worker_handoff/latest.md` |
| `issue_body_path` | string | `reports/loop/worker_handoff/latest_issue.md` |
| `comment_body_path` | string | `reports/loop/worker_handoff/latest_comment.md` |
| `api_key_required` | boolean | `false` |
| `ai_worker_in_github_actions` | boolean | `false` |

## Invariants

- `OPENAI_API_KEY` and `CODEX_API_KEY` are forbidden as requirements.
- `openai/codex-action@v1` is forbidden.
- GitHub Actions emits handoff artifacts only.
- Exactly one Ready ticket is selected when `verdict = plan`.
- The selected worker must not self-approve, mark tickets Done, pass gates, or author QA verdict files.
