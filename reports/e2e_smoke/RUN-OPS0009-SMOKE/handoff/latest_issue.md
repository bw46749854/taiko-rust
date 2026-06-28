# Codex worker handoff: TKT-0005

@codex read `reports/e2e_smoke/RUN-OPS0009-SMOKE/handoff/latest.md` and work only on the selected ticket described there.

## Deterministic boundary

GitHub Actions generated this issue body from `scripts/loop_emit_worker_handoff.py`. It did not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`.

## Selected ticket

- Ticket: `TKT-0005`
- Ticket file: `.loop/tickets/TKT-0005.md`
- Branch: `impl/TKT-0005-bpm-measure-delay-offset-timeline`
- Session metadata: `reports/session_metadata/TKT-0005.toml`

## Required artifact

- Prompt: `reports/e2e_smoke/RUN-OPS0009-SMOKE/handoff/latest.md`
- Machine contract: `reports/loop/worker_handoff/latest.json`
