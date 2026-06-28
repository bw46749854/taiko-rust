# Canonical Repository Inventory

Status: canonical

`OPS-0002` removes legacy preparation logs from the runtime package and defines the active repository inventory.

## Active inventory classes

| Class | Paths |
|---|---|
| Operator instructions | `AGENTS.md`, `README.md` |
| Canonical docs | `docs/`, excluding no generated local evidence |
| Research summaries | `research/opentaiko/` |
| Operational policies | `operations/*.toml`, `operations/*.md` |
| Prompts | `prompts/*.md` |
| Tickets and gates | `.loop/tickets/`, `.loop/gates/` |
| Rust workspace | `Cargo.toml`, `rust-toolchain.toml`, `crates/` |
| GitHub automation | `.github/workflows/`, `.github/pull_request_template.md`, `.github/codex/` |
| Static and runtime scripts | `scripts/` |
| Fixtures | `fixtures/synthetic/`, `fixtures/user_selected/README.md` |
| Report directories | `reports/**/README.md` |
| Schemas and templates | `schemas/`, `templates/` |

## Removed legacy inventory

- Root-level preparation changelog and file-manifest markdown files.
- Legacy source conversation snapshots.

These removed files must not be required by any active gate, static checker, or workflow.
