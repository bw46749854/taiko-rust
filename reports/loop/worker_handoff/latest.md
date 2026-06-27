# Codex Worker Handoff for TKT-0005

Run ID: `RUN-HANDOFF-TKT0005`
Verdict: `plan`
Ticket: `TKT-0005`
Ticket file: `.loop/tickets/TKT-0005.md`
Branch: `impl/TKT-0005-bpm-measure-delay-offset-timeline`
Implementation worktree: `worktrees/impl/TKT-0005`
Review worktree: `worktrees/review/TKT-0005`
QA worktree: `worktrees/qa/TKT-0005`
Session metadata: `reports/session_metadata/TKT-0005.toml`
Expected QA verdict path: `reports/qa/TKT-0005.verdict.json`

## Mandatory boundary

GitHub Actions emitted this handoff deterministically. It did not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`.

Use Codex Cloud, Codex App Automation, or Codex CLI signed in with ChatGPT. Work on one ticket only.

## Required reads

- `AGENTS.md`
- `README.md`
- `docs/99_codex_worker_handoff_contract.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `operations/loop_policy.toml`
- `operations/ticket_transition_policy.toml`
- `.loop/tickets/TKT-0005.md`

## Allowed paths

- `.loop/tickets/TKT-0005.md`
- `AGENTS.md`
- `README.md`
- `crates/`
- `docs/`
- `fixtures/synthetic/`
- `operations/phase1_feature_ticket_manifest.toml`
- `prompts/72_phase1_gameplay_ticket_runner.md`
- `reports/phase1_gameplay_loop/`
- `reports/session_metadata/`
- `reports/preflight/`
- `reports/failures/`
- `scripts/`

## Forbidden paths

- `.external_assets/`
- `source_context/`
- `STEP*.md`
- `reports/qa/*.verdict.json`
- `reports/regression/*.json`

## Required commands

- `scripts/ci_local_equivalent.sh --static-only`
- `scripts/check_worker_handoff_static.py`
- `- `cargo test --workspace``
- `- `taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json``
- `- `taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json``
- `- `taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json``
- `- `taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json``

## Stop and PR rules

- Do not mark tickets Done.
- Do not pass gates.
- Do not self-approve.
- Do not author `reports/qa/*.verdict.json` from an implementation session.
- Do not start gameplay implementation unless the selected ticket explicitly unlocks Phase1 gameplay.
- Open a PR only after a scoped diff exists and the required commands have been run or explicitly blocked by environment limitations.
