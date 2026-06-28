# 75. Phase1 Feature Ticket Manifest Schema

Status: canonical

## 1. Purpose

`operations/phase1_feature_ticket_manifest.toml` is the machine-readable source for Phase1 gameplay ticket ordering, dependency checks, command requirements, QA requirements, and failure-route requirements.

The manifest exists so Control Session does not infer ticket order from prose.

## 2. Top-level required fields

| Field | Required value |
|---|---|
| `schema_version` | string |
| `manifest_id` | string |
| `feature_ticket_count` | integer |
| `first_feature_ticket` | ticket id |
| `required_entry_gate` | `GATE-0090` |
| `required_qa_gate` | `GATE-0080` |
| `failure_route_required` | `true` |
| `qa_verdict_required` | `true` |

## 3. Per-ticket required fields

Each `[[tickets]]` entry must include:

| Field | Required value |
|---|---|
| `ticket_id` | existing `.loop/tickets/TKT-*.md` |
| `title` | non-empty string |
| `stage` | non-empty string |
| `category` | non-empty string |
| `depends_on` | array of `TKT-*` / `GATE-*` ids |
| `primary_crates` | array of canonical crates |
| `required_commands` | array containing cargo, qa, and feature-specific commands |
| `acceptance_docs` | array of existing docs/research/coverage paths |
| `qa_required` | `true` |
| `failure_route_required` | `true` |

## 4. Required command policy

Every gameplay feature ticket must include:

```bash
cargo test --workspace
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

Timing-sensitive tickets must also include:

```bash
taiko_cli timing analyze --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
```

Runtime-sensitive tickets must also include:

```bash
taiko_cli headless autoplay --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --mode perfect --format json
```

## 5. Validation failures

The manifest validator must reject the package when:

- `feature_ticket_count` does not match the number of `[[tickets]]` entries;
- a referenced ticket file is missing;
- a referenced doc or research path is missing;
- a deprecated crate name is used;
- a feature ticket omits QA verdict evidence;
- a feature ticket omits failure-route evidence;
- the first gameplay ticket is not `TKT-0005`;
- `TKT-0005` does not depend on `TKT-0060` and `GATE-0090`.
