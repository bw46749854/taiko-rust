# Phase1 Gameplay Ticket Runner Prompt

Status: canonical

You are the Ticket Implementation Session for one Phase1 gameplay ticket in the OpenTaiko-compatible Rust implementation loop.

## Required reads

Read these files before planning:

- `AGENTS.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/27_phase1_open_taiko_compatibility_boundary.md`
- `docs/74_phase1_feature_loop_entry_contract.md`
- `docs/76_phase1_feature_acceptance_command_matrix.md`
- `docs/88_auto_merge_loop_policy.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `docs/92_codex_plus_automation_operation.md`
- `docs/93_github_actions_auto_merge_controller.md`
- `docs/94_e2e_smoke_loop_verification.md`
- `docs/95_phase1_gameplay_loop_start.md`
- `operations/phase1_feature_ticket_manifest.toml`
- `operations/phase1_gameplay_loop_policy.toml`
- the selected `.loop/tickets/<ticket-id>.md`

## Hard constraints

- Work on exactly one ticket.
- The first gameplay ticket is `TKT-0005`.
- Do not start gameplay implementation unless the rendered start packet says `verdict = ready`.
- Do not mark any ticket Done.
- Do not pass any gate.
- Do not write `reports/qa/*.json` or `reports/qa/*.verdict.json` from an implementation session.
- Do not use `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`.
- Keep GitHub Actions deterministic; AI work stays on Codex Cloud/App/CLI signed in with ChatGPT.

## Required workflow

1. Read the selected ticket and the manifest entry.
2. Produce a brief implementation plan.
3. Keep changes scoped to the ticket.
4. Run the required static checks available in the environment.
5. Run Rust and `taiko_cli` checks when Rust is available.
6. Write session metadata for the PR.
7. Stop after creating the PR. QA and review are separate sessions.

## Default command

```bash
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
```

The command must report `block` while entry evidence is missing. Use `--force-preview` only to inspect the generated prompt structure; it does not authorize implementation.
