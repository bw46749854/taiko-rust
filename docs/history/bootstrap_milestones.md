# Bootstrap Milestones

Status: canonical-history

This file is the compact historical record for the preparation work that was previously represented by root-level changelog and manifest files. The historical files were removed during `OPS-0002` so active operation depends only on canonical docs, operations files, prompts, scripts, gates, tickets, and reports.

## Canonicalized preparation milestones

| Milestone | Canonical evidence now used |
|---|---|
| Compatibility contract | `docs/20_phase1_scope.md`, `docs/24_phase1_normal_play_compatibility_contract.md` |
| OpenTaiko research | `research/opentaiko/`, especially `research/opentaiko/10_phase1_adoption_decisions.md` |
| Coverage design | `docs/coverage/` and `fixtures/synthetic/` |
| Loop bootstrap | `.loop/`, `prompts/`, `docs/60_session_topology.md`, `docs/62_loop_engineering_flow.md` |
| Rust workspace and CLI | `Cargo.toml`, `crates/`, `scripts/check_rust_workspace_static.py` |
| Fixture, autoplay, timing, failure, QA gates | `docs/45_*` through `docs/49_*`, `scripts/check_*_static.py`, `reports/` |
| GitHub PR orchestration and preflight | `docs/84_github_pr_loop_contract.md`, `docs/85_rust_enabled_preflight_gate.md`, `.github/workflows/` |
| Codex Cloud and no-API-key operation | `docs/86_codex_cloud_environment_setup.md`, `docs/87_secret_and_network_policy.md`, `docs/92_codex_plus_automation_operation.md` |
| Loop controller, auto-merge, E2E smoke | `docs/88_*`, `docs/89_*`, `docs/93_*`, `docs/94_*`, `operations/*_policy.toml` |
| Phase1 gameplay loop start | `docs/95_phase1_gameplay_loop_start.md`, `operations/phase1_gameplay_loop_policy.toml`, `prompts/72_phase1_gameplay_ticket_runner.md` |

## Active rule

Historical milestone files are not required by bootstrap checks. Active checks must cite the canonical evidence files above.
