# Loop Automation Reports

Status: canonical

This directory is reserved for Plus-plan Codex Automation run summaries.

Committed package artifacts must not include user-selected songs, commercial media, local machine paths, API keys, or Codex access tokens.

Expected generated files:

```text
reports/loop/<run_id>/controller_plan.json
reports/loop/<run_id>/controller_plan.md
reports/loop/<run_id>/next_codex_prompt.md
reports/loop/<run_id>/automation_runbook.md
reports/loop_automation/<run_id>.md
```

The generated files are execution evidence. They are normally committed only when a ticket explicitly requires transition evidence.
