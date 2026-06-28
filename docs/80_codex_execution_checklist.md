# 80. Codex Execution Checklist

Status: canonical

## Before starting Codex loop

- [ ] Clone repository.
- [ ] Create separate worktrees for control, spec, review, test-infra, qa, and implementation.
- [ ] Confirm no user-selected song assets are committed.
- [ ] Read `AGENTS.md`.
- [ ] Read `docs/73_first_execution_batch.md`.
- [ ] Start with `OPS-0001` only during the operations migration.

## TKT-0000 checklist

- [ ] Read `.loop/gates/GATE-0000-spec-repair.md`.
- [ ] Confirm only `OPS-0001` is Ready.
- [ ] Confirm canonical crate names.
- [ ] Confirm compatibility/research/coverage documents exist.
- [ ] Confirm coverage matrix exists.
- [ ] Confirm `fixtures/synthetic/phase1_synthetic_manifest.toml` exists and validates.
- [ ] Confirm user-selected song manifest docs exist.
- [ ] Confirm required templates exist.
- [ ] Run `scripts/check_bootstrap_consistency.sh`.
- [ ] Write gate report using `templates/gate_report_template.md`.
- [ ] Request Design Review Session review.

## Per-ticket checklist

- [ ] Read required docs in ticket.
- [ ] Create implementation plan.
- [ ] Obtain plan review from Design Review Session.
- [ ] Implement only ticket scope.
- [ ] Run required cargo commands.
- [ ] Run fixture/analyzer commands listed in ticket.
- [ ] Write evidence summary.
- [ ] Request final review.
- [ ] Move ticket status only after review.

## Required command families

```bash
cargo fmt --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --emit-report out/fixture_validation.json
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --emit-timing-log out/synthetic_timing.jsonl
taiko_cli timing analyze --input out/synthetic_timing.jsonl --profile phase1-synthetic --emit-json out/synthetic_analyzer.json --emit-md out/synthetic_analyzer.md
taiko_cli user-song validate --manifest fixtures/user_selected/manifests/user_song_manifest.yaml --emit-report out/user_song_validation.json --emit-timing-log out/user_song_timing.jsonl
```

Commands that do not exist yet are command contracts for implementation tickets. Early tickets must create them as stubs or real commands according to ticket scope.


## GitHub PR orchestration PR orchestration checklist

Before the first implementation PR:

- [ ] Push the package to a private GitHub repository.
- [ ] Connect the repository to Codex Cloud.
- [ ] Configure a Rust-capable Codex Cloud environment.
- [ ] Confirm `.github/workflows/loop-pr-gate.yml` is active.
- [ ] Confirm `.github/workflows/phase1-loop.yml` is active.
- [ ] Confirm `.github/workflows/rust-preflight.yml` is active.
- [ ] Configure native Codex GitHub review or use `.github/workflows/codex-review.yml`.
- [ ] Confirm `scripts/check_github_pr_orchestration_static.py` passes.
- [ ] Confirm `scripts/check_rust_preflight_static.py` passes.

Per ticket PR:

```bash
scripts/loop_create_worktree.sh <ticket-id>
# implementation session works only inside that worktree
scripts/loop_open_pr.sh <ticket-id>
# review + QA run separately
scripts/loop_apply_qa_verdict.py --ticket <ticket-id> --verdict <qa-verdict-json> --emit-transition .loop/session_logs/<ticket-id>-qa-transition.md
scripts/loop_merge_and_advance.sh <ticket-id> --pr <number> --verdict <qa-verdict-json>
```

A docs-only/bootstrap PR may use `--docs-only` for merge only when the ticket's own required checks do not include Rust runtime commands.


## Codex Cloud / CI environment Codex Cloud / CI environment checklist

Before starting `TKT-0001`:

- [ ] Private GitHub repository is connected to Codex Cloud.
- [ ] Codex Cloud setup command is `bash scripts/codex_cloud_setup.sh`.
- [ ] `rust-toolchain.toml` is present and pinned.
- [ ] `scripts/check_codex_cloud_env_static.py` passes.
- [ ] `scripts/ci_local_equivalent.sh --static-only` passes.
- [ ] Codex Cloud agent internet access is off by default.
- [ ] No workflow exposes `OPENAI_API_KEY` or `CODEX_API_KEY` as a job-level environment variable in a job that checks out or runs repository-controlled code.
- [ ] `docs/87_secret_and_network_policy.md` is referenced in the first gate report.

## Rust preflight Rust preflight checklist

Before accepting `TKT-0001` or passing `GATE-0030`:

- [ ] Run `scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest` in GitHub Actions or Codex Cloud.
- [ ] Validate `reports/preflight/latest/rust_preflight_report.json` with `scripts/check_runtime_evidence_files.py --require-scope current-package --require-pass`.
- [ ] Attach or reference the `rust-preflight-report` CI artifact in the ticket evidence.
- [ ] Route `reject` verdicts through failure feedback.
- [ ] Route `block` verdicts to environment repair before implementation continues.


## OPS-0001 checklist

- [ ] Read `.loop/tickets/OPS-0001.md`.
- [ ] Read `.loop/gates/GATE-OPS-0000-migration-ready.md`.
- [ ] Confirm `TKT-0000` and all implementation tickets remain Blocked.
- [ ] Run `scripts/check_bootstrap_consistency.sh`.
- [ ] Run `scripts/ci_local_equivalent.sh --static-only`.
- [ ] Record next-ticket transition evidence for `OPS-0002`.


## OPS-0008 worker checklist

Before implementing, read `reports/loop/worker_handoff/latest.md` generated by `scripts/loop_emit_worker_handoff.py`. Use the selected ticket, branch, worktrees, required reads, allowed paths, forbidden paths, and required commands listed there.
