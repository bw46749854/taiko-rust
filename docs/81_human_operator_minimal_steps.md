# 81. Human Operator Minimal Steps

Status: canonical

## Purpose

Human intervention is minimized. The human provides local song assets and reviews final artifacts, while Codex sessions handle implementation, testing, analysis, and repair loops.

## Required human actions

1. Push this package to the GitHub repository used for the operations migration.
2. Connect the repository to Codex Cloud.
3. Configure a Codex Cloud environment with setup command `bash scripts/codex_cloud_setup.sh`.
4. Confirm `scripts/check_codex_cloud_env_static.py` passes in CI or Codex Cloud.
5. Confirm the `rust-preflight` and public-readiness static checks run on the private repository before publication.
6. Configure native Codex GitHub review or the optional `codex-review` workflow secret.
7. Provide local user-selected song files outside the repository.
8. Create or edit a user-song manifest from `fixtures/user_selected/manifests/user_song_manifest.example.md`.
9. Start Control Session with `prompts/60_final_bootstrap_prompt.md` and select the single Ready OPS ticket only. In this package that ticket is `TKT-0005`.
10. Review final Phase1 QA report.

## User-selected song manifest rules

- Paths must be local to the human environment.
- Assets must not be copied into repository.
- Ten categories are used:
  1. basic chart
  2. high density
  3. BPM/measure/delay/offset
  4. roll/balloon
  5. branch A accuracy
  6. branch B roll/score/LEVELHOLD/SECTION
  7. scroll/overtake
  8. HB/BM/special display
  9. mixed comprehensive
  10. long/load chart

## Human does not need to do

- implement Rust code,
- manually inspect every timing log,
- manually calculate note timings,
- approve implementation session output without review evidence,
- manually create ticket branches after Step14 scripts are available,
- manually run Rust locally when GitHub Actions or Codex Cloud provides passing `rust-preflight` evidence,
- manually configure Rust toolchain details outside `rust-toolchain.toml`,
- manually decide next-ticket transition when QA verdict JSON exists.


## GitHub Actions role during operations migration

GitHub Actions verifies, gates, merges eligible PRs, advances tickets, and emits handoff artifacts. GitHub Actions does not run Codex or GPT workers and does not require `OPENAI_API_KEY` or `CODEX_API_KEY` for those gate duties.


## Public repository publication boundary

The repository remains private during `OPS-0003`. Public visibility is unlocked only after `GATE-OPS-0000` passes. GitHub Actions verifies public-readiness through `scripts/check_public_repository_static.py`; it does not run Codex or GPT workers and does not require `OPENAI_API_KEY` or `CODEX_API_KEY`.


## OPS-0004 note

During `OPS-0004`, the operator supplies no local assets. The repository defines only the manifest shape and scripts. Real asset values are provided later through a private manifest or environment-controlled file and are verified by sha256 before extraction to `.external_assets/opentaiko/`.


## OPS-0005 note

During `OPS-0005`, the operator does not configure any OpenAI API key for GitHub Actions. Actions normalize required checks, workflow permissions, `workflow_run` success guards, and controller concurrency. GitHub Actions remains a verifier/gate/controller; Codex or ChatGPT worker execution remains outside Actions.


## OPS-0008 note

During `OPS-0008`, GitHub Actions emits deterministic Codex worker handoff artifacts only. It does not call Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`. The human operator does not manually choose the next ticket; the handoff generator reads the single Ready ticket and writes `reports/loop/worker_handoff/latest.md` and `latest.json`.


## OPS-0009 note

After OPS migration, the human operator does not manually pick a gameplay ticket. The only Ready ticket is `TKT-0005`, selected by the manifest and verified by `scripts/check_ops_migration_readiness.py`. GitHub Actions still does not call AI providers or require OpenAI API keys.
