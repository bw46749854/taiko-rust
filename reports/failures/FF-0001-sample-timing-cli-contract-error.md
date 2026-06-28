# Failure Report: FF-0001 sample timing CLI contract error

Status: sample-contract-fixture
Purpose: validate Step11 failure feedback ingestion and repair-ticket proposal.

## 1. Failure metadata

| Field | Value |
|---|---|
| Failure ID | FF-0001 |
| Source ticket or gate | GATE-0060 |
| Session reporting failure | QA / Regression Session |
| Worktree/branch | worktrees/qa/sample |
| Commit/range | sample-only |
| Date | 2026-06-25 |
| Category | timing_cli_contract_error |

## 2. Failing command

```bash
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```

Exit code:

```text
2
```

stderr/stdout summary:

```text
sample: timing analyzer JSON did not include p95_error_ms
```

## 3. Reproduction steps

1. Run the failing command from the repository root.
2. Inspect the JSON output.
3. Confirm that the required field is missing.

## 4. Evidence files

| Artifact | Path | Required? | Notes |
|---|---|---:|---|
| command log | reports/failure_feedback/sample_command.log | yes | synthetic contract fixture |
| analyzer JSON | reports/timing/phase1_synthetic.perfect.analysis.json | yes | expected analyzer output path |

## 5. Expected vs actual

| Area | Expected | Actual |
|---|---|---|
| loop orchestration | timing analyzer JSON includes p95_error_ms | timing analyzer JSON omits p95_error_ms |
| compatibility report | GATE-0060 can pass using JSON fields only | QA cannot decide from JSON contract |

## 6. Suspected affected scope

| Module or document | Reason |
|---|---|
| crates/taiko_cli/src/lib.rs | command JSON rendering owns the missing field |
| docs/47_timing_log_analyzer_contract.md | contract defines required timing fields |

## 7. Minimal repair scope

- Restore the missing timing analyzer JSON field and add a regression check that fails when it is absent.

## 8. Failure-to-ticket routing

| Field | Value |
|---|---|
| Existing matching repair ticket | none |
| Proposed new repair ticket ID | TKT-9001 |
| Duplicate prevention key | category + reproduction command + failing fixture/manifest + expected class + actual class |
| Original ticket should remain | Rejected |

## 9. Regression command required after repair

```bash
taiko_cli timing analyze --input reports/headless_autoplay/phase1_synthetic.perfect.json --threshold-ms 1.0 --format json
```
