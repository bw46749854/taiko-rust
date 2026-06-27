# Ticket Transition Schema

Status: canonical

## Purpose

`ticket_transition_plan.json` records how the GitHub Actions loop-controller advances ticket state after an accepted merge. It is deterministic and does not call AI providers.

## Producer

```bash
scripts/loop_advance_ticket.py \
  --merge-history reports/loop/merge_history/<run_id>.json \
  --mode plan \
  --out reports/loop/ticket_transitions/<run_id>.json \
  --markdown reports/loop/ticket_transitions/<run_id>.md
```

## Required JSON fields

| Field | Meaning |
|---|---|
| `schema` | Always `schemas/ticket_transition_schema.md` |
| `verdict` | `pass`, `block`, or `reject` |
| `mode` | `plan` or `apply` |
| `run_id` | Controller run id from merge history |
| `merged_ticket` | Ticket id read from merge history |
| `next_ready_ticket` | Promoted ticket id, or null |
| `status_updates` | Ordered status updates that would be or were applied |
| `ready_tickets_after` | Ready ticket list after applying the transition model |
| `reasons` | Machine-readable reasons for pass/block/reject |
| `api_key_required` | Always false |
| `ai_worker` | Always `not_used` |

## Verdicts

- `pass`: the merged ticket is or becomes `Done`, and exactly one valid next ticket is `Ready`.
- `block`: merge evidence is missing, dry-run history is supplied to apply mode, dependencies are incomplete, or no next ticket is eligible.
- `reject`: merge history or ticket ids violate fixed policy.

## Status updates

Each update uses this shape:

```json
{
  "ticket_id": "OPS-0006",
  "path": ".loop/tickets/OPS-0006.md",
  "from": "Ready",
  "to": "Done",
  "changed": true
}
```

## Safety rules

- GitHub Actions remains a verifier/gate/controller and must not call Codex/GPT.
- `OPENAI_API_KEY` and `CODEX_API_KEY` are not required.
- During OPS migration, `TKT-*` gameplay tickets must not become `Ready`.
- At most one ticket may be `Ready` after an apply transition.
- Re-applying an already completed transition is idempotent when the policy permits it.
