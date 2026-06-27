# Next Ticket Handoff Prompt

Status: canonical

Use this prompt only after `scripts/loop_emit_worker_handoff.py` has generated:

```text
reports/loop/worker_handoff/latest.json
reports/loop/worker_handoff/latest.md
```

## Required rule

Do not use `OPENAI_API_KEY`, `CODEX_API_KEY`, `openai/codex-action@v1`, or any metered API worker. Use Codex Cloud, Codex App Automation, or Codex CLI signed in with ChatGPT.

## Worker instruction

1. Read `AGENTS.md`.
2. Read `reports/loop/worker_handoff/latest.md`.
3. Work on the selected ticket only.
4. Use the branch and worktree named by the handoff.
5. Produce session metadata at the handoff `session_metadata_path`.
6. Run the required commands listed by the handoff.
7. Open a PR only after producing a scoped diff.
8. Do not self-approve, mark tickets Done, pass gates, or author QA verdict files.

## Stop rule

If the handoff verdict is `block`, do not implement. Record the blocker in the PR or session log and stop.
