# OPS Migration Readiness Schema

Status: canonical

## Purpose

Defines the machine-readable evidence required by `OPS-0009` before Phase1 gameplay ticket `TKT-0005` may become the only Ready ticket.

## Required fields

- `schema`
- `verdict`
- `run_id`
- `api_key_required`
- `ai_worker_in_github_actions`
- `only_ready_ticket`
- `ops_tickets_done`
- `public_repository_static_check`
- `asset_bundle_static_check`
- `github_actions_gate_static_check`
- `auto_merge_static_check`
- `ticket_transition_static_check`
- `worker_handoff_static_check`
- `e2e_smoke_static_check`
- `phase1_gameplay_start_static_check`
- `phase1_start_packet`

## Verdicts

- `pass`: migration is complete and `TKT-0005` may be the only Ready ticket.
- `block`: evidence is missing or not yet generated.
- `reject`: repository state violates the no-AI-worker, no-secret, or single-Ready-ticket policy.
