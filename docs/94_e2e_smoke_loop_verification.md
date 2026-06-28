# 94. E2E Smoke Loop Verification

Status: canonical

## Purpose

The E2E smoke loop verifies that the autonomous loop substrate can be exercised end-to-end without starting Phase1 gameplay implementation and without calling AI providers from GitHub Actions.

This is a smoke verification layer, not the final Phase1 gameplay acceptance test. It proves that the controller surfaces added in Steps17-21 can be composed into deterministic pass, reject, block, retry-budget, and revert evidence.

## Scope

The smoke loop covers these routes:

| Scenario | Route | Expected result |
|---|---|---|
| `pass` | metadata + QA pass + auto-merge dry-run | merge candidate evidence is accepted |
| `reject` | QA reject + failure report | repair ticket preview is produced |
| `block` | QA block + missing evidence report | blocker ticket preview is produced |
| `retry` | repeated repair/block attempts | retry budget stop evidence is produced |
| `revert` | regression after autonomous merge | revert evidence and dry-run PR command are produced |

## Non-scope

The E2E smoke loop does not:

- run Codex workers,
- require `OPENAI_API_KEY`,
- call `openai/codex-action@v1`,
- create live GitHub PRs by default,
- mutate `.loop/tickets/` with smoke-only Ready tickets,
- start Phase1 gameplay implementation.

## Command surface

```bash
scripts/check_e2e_smoke_static.py
scripts/run_e2e_smoke_loop.sh --scenario all --dry-run --out /tmp/opentaiko-e2e-smoke
scripts/run_e2e_smoke_loop.sh --scenario pass --dry-run
scripts/run_e2e_smoke_loop.sh --scenario reject --dry-run
scripts/run_e2e_smoke_loop.sh --scenario block --dry-run
scripts/run_e2e_smoke_loop.sh --scenario retry --dry-run
scripts/run_e2e_smoke_loop.sh --scenario revert --dry-run
```

## Evidence layout

Default evidence is written under `reports/e2e_smoke/<run_id>/`. Static validation uses a temporary out directory so committed package checks do not leave smoke artifacts in the repository.

Required smoke evidence:

```text
reports/e2e_smoke/<run_id>/summary.json
reports/e2e_smoke/<run_id>/summary.md
reports/e2e_smoke/<run_id>/pass/session_metadata.toml
reports/e2e_smoke/<run_id>/pass/qa.verdict.json
reports/e2e_smoke/<run_id>/pass/merge_history/<run_id>-pass.json
reports/e2e_smoke/<run_id>/reject/failure.md
reports/e2e_smoke/<run_id>/reject/materialized_tickets/TKT-REPAIR-SMOKE-REJECT.md
reports/e2e_smoke/<run_id>/block/failure.md
reports/e2e_smoke/<run_id>/block/materialized_tickets/TKT-ENV-SMOKE-BLOCK.md
reports/e2e_smoke/<run_id>/retry/retry_budget.json
reports/e2e_smoke/<run_id>/revert/regression/<run_id>-revert.json
```

## Acceptance criteria

The E2E smoke loop passes when:

1. `scripts/check_e2e_smoke_static.py` passes.
2. `scripts/run_e2e_smoke_loop.sh --scenario all --dry-run --out /tmp/...` produces all required scenario evidence.
3. The pass scenario validates session metadata, role path policy, and auto-merge candidate evidence.
4. The reject scenario produces repair-ticket materialization preview without modifying `.loop/tickets/`.
5. The block scenario produces blocker-ticket materialization preview without modifying `.loop/tickets/`.
6. The retry scenario produces stop evidence for excessive attempts.
7. The revert scenario produces regression/revert evidence through `scripts/loop_revert_last_merge.sh --dry-run`.
8. No workflow contains `openai/codex-action@v1` or `secrets.OPENAI_API_KEY` as an executable dependency.

## Relationship to Phase1 gameplay worker handoff

Phase1 gameplay worker handoff may start Phase1 gameplay tickets only after E2E smoke evidence passes in GitHub Actions or an equivalent local static environment. This prevents gameplay implementation from starting on an unproven controller/merge/repair substrate.

## OPS-0009 final smoke extension

`OPS-0009` extends the canonical smoke surface beyond `pass`, `reject`, `block`, `retry`, and `revert`.

Additional scenarios:

- `advance`: verifies ticket-transition evidence from `OPS-0009` to `TKT-0005` with `scripts/loop_advance_ticket.py` and `fixtures/loop_controller/merge_history_ops0009.json`.
- `handoff`: verifies deterministic worker handoff artifacts for the single Ready ticket using `scripts/loop_emit_worker_handoff.py`.
- `publication`: verifies public-readiness, asset-readiness, GitHub Actions Gate readiness, and Phase1 start-packet readiness using `scripts/check_ops_migration_readiness.py --static-only`.

The full dry-run remains:

```bash
scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
```

GitHub Actions remains a verifier/gate/controller/handoff emitter. It does not run Codex/GPT workers and does not require `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`.
