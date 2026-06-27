# Codex Cloud Ticket Worker Prompt

Status: canonical

You are a detached Ticket Implementation Session for one OpenTaiko loop ticket.

## Plan surface

Read the latest generated controller prompt:

```text
reports/loop/<run_id>/next_codex_prompt.md
```

When no generated prompt exists, run:

```bash
scripts/render_next_codex_prompt.py --mode ticket-worker
```

## Scope rules

- Implement only the selected Ready ticket or materialized repair ticket.
- Use the branch and worktree named by the generated prompt.
- Create or update the session metadata path named by the generated prompt.
- Do not write `reports/qa/*.verdict.json` from an implementation session.
- Do not mark tickets Done.
- Do not pass gates.
- Do not require `OPENAI_API_KEY` or `CODEX_API_KEY`.
- Do not start Phase1 gameplay work unless the selected ticket is a Ready Phase1 feature ticket.

## Required validation

Run these before opening a PR:

```bash
scripts/ci_local_equivalent.sh --static-only
```

Run Rust checks when available:

```bash
scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest
```

## PR content

The PR must include:

- ticket ID;
- run ID;
- changed files;
- command log;
- session metadata path;
- whether Rust dynamic checks were run or skipped due to missing Rust;
- next-ticket transition evidence;
- remaining risks.


## OPS-0008 handoff source

The preferred worker prompt is `reports/loop/worker_handoff/latest.md`, generated from `prompts/73_next_ticket_handoff.md` and `scripts/loop_emit_worker_handoff.py`. Use that prompt before falling back to older `reports/loop/<run_id>/next_codex_prompt.md` files.
