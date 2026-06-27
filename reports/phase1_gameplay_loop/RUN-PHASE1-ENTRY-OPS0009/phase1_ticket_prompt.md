# Phase1 Gameplay Ticket Worker: TKT-0005

Run ID: `RUN-PHASE1-ENTRY-OPS0009`
Verdict: `block`
Next action: `wait_for_phase1_entry_evidence`

## Authorization

Do not implement. The Phase1 gameplay entry evidence is missing or invalid.

## Required reads

- `AGENTS.md`
- `prompts/72_phase1_gameplay_ticket_runner.md`
- `docs/95_phase1_gameplay_loop_start.md`
- `docs/24_phase1_normal_play_compatibility_contract.md`
- `docs/27_phase1_open_taiko_compatibility_boundary.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
- `operations/phase1_feature_ticket_manifest.toml`
- `.loop/tickets/TKT-0005.md`

## Work assignment

- Ticket: `TKT-0005`
- Title: BPM MEASURE DELAY OFFSET timeline
- Stage: `timeline`
- Category: `timing_model`
- Branch: `impl/TKT-0005-bpm-measure-delay-offset-timeline`
- Implementation worktree: `worktrees/impl/TKT-0005`
- Review worktree: `worktrees/review/TKT-0005`
- QA worktree: `worktrees/qa/TKT-0005`

## Required commands

- `cargo test --workspace`
- `taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json`
- `taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json`
- `taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json`
- `taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json`

## Hard stops

- Do not modify QA verdict files from an implementation session.
- Do not mark tickets Done.
- Do not pass gates.
- Do not use `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`.
- Route reject/block through the Step19 repair materialization path.
