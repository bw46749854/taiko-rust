# Operations Manifest

Status: canonical
Migration status: active-ops-rail

## Package identity

Name: `opentaiko_phase1_ops0007_ticket_advance_package`
Purpose: Codex loop engineering bootstrap for OpenTaiko-compatible Rust Phase1 after public repository hardening, deterministic development asset bundle contract setup, GitHub Actions gate normalization, auto-merge candidate discovery, and ticket advance engine integration. The repository is still frozen behind the operations migration rail before gameplay implementation begins.

## Current operational state

| Field | Value |
|---|---|
| Active rail | `OPS-0001` ... `OPS-0009` |
| Completed migration tickets | `OPS-0001`, `OPS-0002`, `OPS-0003`, `OPS-0004`, `OPS-0005`, `OPS-0006` |
| Only Ready ticket | `TKT-0005` |
| Frozen tickets | `TKT-0000`, `TKT-0001`, all Phase1 gameplay implementation tickets |
| Migration gate | `GATE-OPS-0000` |
| GitHub Actions role | verifier, gate, merge controller, ticket advancement controller, handoff artifact generator |
| GitHub Actions AI worker role | forbidden |
| OpenAI API key requirement | false |

## Canonical preparation baseline

The repository now depends on canonical docs, operations files, prompts, scripts, gates, tickets, reports, schemas, templates, fixtures, and Rust workspace files. Historical root-level preparation changelogs and legacy source snapshots were removed by `OPS-0002`.

Historical context has been compacted into `docs/history/bootstrap_milestones.md`. Active file classes are listed in `docs/96_canonical_repository_inventory.md`.

## Migration ticket rail

| Ticket | Status | Scope |
|---|---:|---|
| OPS-0001 | Done | Migration ticket rail and bootstrap freeze |
| OPS-0002 | Done | Legacy cleanup canonicalization |
| OPS-0003 | Done | Public repository hardening |
| OPS-0004 | Done | Drive zip asset bundle contract |
| OPS-0005 | Done | GitHub Actions gate normalization |
| OPS-0006 | Done | Auto-merge candidate discovery |
| OPS-0007 | Done | Ticket advance engine |
| OPS-0008 | Done | Next Codex worker handoff |
| OPS-0009 | Done | E2E smoke and Phase1 entry unlock |
| TKT-0005 | Blocked | BPM MEASURE DELAY OFFSET timeline |

## Initial execution state

- Ready ticket: none until `TKT-0060` is Done and `GATE-0090` passes; then `TKT-0005` becomes the only Ready gameplay ticket
- Done migration tickets: `OPS-0001`, `OPS-0002`, `OPS-0003`, `OPS-0004`, `OPS-0005`, `OPS-0006`
- Blocked tickets: `TKT-0000` and downstream gameplay tickets whose dependencies are not yet satisfied
- First migration gate: `GATE-OPS-0000`
- First prompt: `prompts/60_final_bootstrap_prompt.md`
- Controller command: `taiko_cli loop run-once --mode plan --format json`

## Canonical implementation target

Language: Rust
Canonical domain crate: `taiko_domain`
Canonical CLI crate: `taiko_cli`

## Acceptance model

Phase1 acceptance requires:

- full Must implement gameplay synthetic coverage,
- user-selected song validation across 10 categories,
- timing analyzer pass,
- compatibility report without unclassified normal-play commands,
- QA / Regression Session acceptance,
- controller evidence for ticket selection and next-action routing,
- completion of `OPS-0001` through `OPS-0009` and `GATE-OPS-0000` before `TKT-0005` gameplay entry.

## Phase1 Gameplay Loop Start canonical files

- `docs/95_phase1_gameplay_loop_start.md`
- `operations/phase1_gameplay_loop_policy.toml`
- `prompts/72_phase1_gameplay_ticket_runner.md`
- `reports/phase1_gameplay_loop/README.md`
- `scripts/render_phase1_gameplay_ticket_prompt.py`
- `scripts/check_phase1_gameplay_start_static.py`
- `.github/workflows/phase1-gameplay-entry.yml`

## Public repository hardening canonical files

- `LICENSE`
- `NOTICE.md`
- `THIRD_PARTY_NOTICES.md`
- `SECURITY.md`
- `docs/97_public_repository_hardening.md`
- `operations/public_repository_policy.toml`
- `scripts/check_public_repository_static.py`
- `.github/dependabot.yml`


## Asset bundle canonical files

- `docs/98_content_root_and_asset_bundle_contract.md`
- `operations/dev_asset_bundle.example.toml`
- `schemas/dev_asset_bundle_schema.md`
- `scripts/fetch_dev_asset_bundle.py`
- `scripts/check_asset_bundle_manifest.py`
- `reports/assets/README.md`

The development asset substrate is Google Drive zip + sha256 manifest. Folder-share traversal is not a CI default. The extracted content root is `.external_assets/opentaiko/`, and runtime code must accept `OPENTAIKO_CONTENT_ROOT` or `--content-root` for both development and production modes.

## OPS-0005 GitHub Actions gate normalization

- Static check: `scripts/check_github_actions_gate_static.py`
- Policy: `operations/auto_merge_policy.toml`
- Controller workflow: `.github/workflows/loop-controller.yml`
- Required guard: `workflow_run` may proceed only when `github.event.workflow_run.conclusion == 'success'`.
- Required concurrency group: `loop-controller-main`.
- GitHub Actions remains a verifier/gate/controller and does not run Codex or GPT workers.


## OPS-0006 Auto-merge candidate discovery

- Candidate selector: `scripts/select_auto_merge_candidate.py`
- Candidate schema: `schemas/auto_merge_candidate_schema.md`
- Candidate reports: `reports/loop/candidates/candidate_plan.json` and `reports/loop/candidates/candidate_plan.md`
- Fixtures: `fixtures/loop_controller/pass_candidate.json`, `fixtures/loop_controller/reject_candidate.json`, and `fixtures/loop_controller/block_candidate.json`
- The controller may inspect `gh pr list` metadata, but it must not checkout untrusted PR head code.
- At most one passing `loop:automerge` candidate may be merged per controller run.


## OPS-0007 Ticket advance engine

- Engine: `scripts/loop_advance_ticket.py`
- Policy: `operations/ticket_transition_policy.toml`
- Schema: `schemas/ticket_transition_schema.md`
- Reports: `reports/loop/ticket_transitions/`
- Current Ready ticket: `TKT-0005`
- GitHub Actions role: verifier/gate/controller only; no AI worker and no OpenAI API key.


## OPS-0008 worker handoff inventory

- `docs/99_codex_worker_handoff_contract.md`
- `operations/worker_handoff_policy.toml`
- `schemas/worker_handoff_schema.md`
- `prompts/73_next_ticket_handoff.md`
- `scripts/loop_emit_worker_handoff.py`
- `scripts/check_worker_handoff_static.py`
- `.github/ISSUE_TEMPLATE/codex_ticket.md`
- `.github/workflows/loop-worker-handoff.yml`
- `reports/loop/worker_handoff/README.md`

## OPS-0009 final readiness inventory

- `operations/ops_migration_readiness_policy.toml`
- `schemas/ops_migration_readiness_schema.md`
- `scripts/check_ops_migration_readiness.py`
- `reports/loop/publication_readiness_report.md`
- `.loop/session_logs/GATE-OPS-0000-report.md`
- `.loop/session_logs/GATE-0090-report.md`
- `reports/phase1_gameplay_loop/RUN-PHASE1-ENTRY-OPS0009/phase1_gameplay_start.json`
