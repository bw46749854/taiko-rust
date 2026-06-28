---
name: Codex ticket handoff
about: Deterministic handoff text for a detached Codex worker
labels: loop:handoff
---

<!-- Paste reports/loop/worker_handoff/latest_issue.md below. -->

## Handoff source

- `reports/loop/worker_handoff/latest.json`
- `reports/loop/worker_handoff/latest.md`
- `reports/loop/worker_handoff/latest_issue.md`

## Required rule

GitHub Actions emitted this handoff deterministically. It did not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`.
