# GATE-0030: Loop CLI Ready Gate

Status: active
Owner: Control Session
Reviewer: Design Review Session and QA / Regression Session

## Purpose

Confirm that the Rust workspace and `taiko_cli loop` MVP can inspect tickets, inspect gates, select the next ticket, and dry-run gates before parser or gameplay implementation expands.

## Autonomy scorecard impact

A2 Ticket / gate machine-readability, A3 Buildable Rust substrate, A6 Regression / CI enforcement, and A7 Failure feedback loop.

## Required inputs

- Passed `GATE-0000`
- Passed `GATE-0010`
- Passed `GATE-0020`
- `docs/40_loop_cli_contract.md`
- `docs/85_rust_enabled_preflight_gate.md`
- `docs/86_codex_cloud_environment_setup.md`
- `docs/87_secret_and_network_policy.md`
- `docs/05_autonomy_scorecard.md`
- `docs/06_gate_transition_rules.md`
- `.loop/tickets/TKT-0001.md`
- `Cargo.toml`
- `crates/taiko_cli/`
- `crates/taiko_test_support/`

## Pass criteria

| Check | Required result |
|---|---|
| Static workspace check | `scripts/check_rust_workspace_static.py` confirms canonical crates, binaries, and Loop CLI command surface |
| Workspace builds | `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, and `scripts/check_rust_workspace_static.py` pass |
| Environment static evidence | `scripts/check_codex_cloud_env_static.py` and `scripts/ci_local_equivalent.sh --static-only` pass before runtime preflight is accepted |
| Rust preflight evidence | `scripts/run_rust_preflight.sh --scope current-package --out reports/preflight/latest` and `scripts/check_runtime_evidence_files.py --path reports/preflight/latest/rust_preflight_report.json --require-scope current-package --require-pass` pass |
| Ticket inspection | `taiko_cli loop inspect tickets --format json` returns ticket IDs, statuses, dependencies, checks, and evidence requirements |
| Gate inspection | `taiko_cli loop inspect gates --format json` returns gate IDs, inputs, pass criteria, scorecard impact, and next-ticket transitions |
| Next-ticket selection | `taiko_cli loop next --format json` returns exactly one selected ticket or a block verdict with reason |
| Gate dry-run | `taiko_cli loop gate GATE-0000 --dry-run --format json` reports pass/reject/block without mutating files |
| Report status | `taiko_cli loop report status --format json` includes Ready tickets, Blocked tickets, missing evidence, score estimate, and open failures |

## Failure handling

- CLI parse failure routes to a Loop CLI repair ticket.
- Missing JSON fields route to a command contract repair ticket.
- Cargo failure routes to workspace skeleton repair.
- Rust preflight `block` verdict routes to Codex Cloud or CI environment repair.
- Ambiguous next-ticket selection routes to gate transition rule repair.

## Next-ticket transition

Pass unlocks fixture validation implementation work. Reject creates or selects a repair ticket before parser implementation proceeds. Block keeps parser, timing, runtime, and QA implementation tickets Blocked.

## Output

A gate report must be written to `.loop/session_logs/GATE-0030-report.md` using `templates/gate_report_template.md`. The report must reference Rust preflight evidence in `reports/preflight/latest/rust_preflight_report.json` or the equivalent CI artifact.
