# Failure Report Template

Status: canonical
Purpose: provide machine-usable failure handoff data for loop repair.

## 1. Failure metadata

| Field | Value |
|---|---|
| Failure ID |  |
| Source ticket or gate |  |
| Session reporting failure |  |
| Worktree/branch |  |
| Commit/range |  |
| Date |  |
| Category | spec_ambiguity / opentaiko_evidence_gap / coverage_gap / parser_error / chart_time_error / scroll_time_error / judgement_window_error / autoplay_input_error / runtime_tick_error / branch_route_error / score_gauge_error / audio_offset_error / ci_tooling_error / fixture_manifest_error / fixture_file_missing / fixture_tja_structure_error / fixture_unknown_command / fixture_cli_contract_error / headless_cli_contract_error / headless_fixture_load_error / headless_chart_verdict_error / headless_no_scheduled_notes / headless_autoplay_result_error / runtime_mvp_regression / timing_cli_contract_error |

## 2. Failing command

```bash

```

Exit code:

```text

```

stderr/stdout summary:

```text

```

## 3. Reproduction steps

1. 
2. 
3. 

## 4. Evidence files

| Artifact | Path | Required? | Notes |
|---|---|---:|---|
| command log |  | yes |  |
| timing log |  | no |  |
| analyzer JSON |  | no |  |
| analyzer Markdown |  | no |  |
| fixture validation report |  | no |  |
| user-song validation report |  | no |  |
| QA verdict JSON |  | no |  |
| trace log |  | no |  |

## 5. Expected vs actual

| Area | Expected | Actual |
|---|---|---|
| parser |  |  |
| scheduler/timing |  |  |
| judgement |  |  |
| branch |  |  |
| score/gauge |  |  |
| audio offset |  |  |
| compatibility report |  |  |
| loop orchestration |  |  |

## 6. Suspected affected scope

| Module or document | Reason |
|---|---|
|  |  |

## 7. Minimal repair scope

- 

## 8. Failure-to-ticket routing

| Field | Value |
|---|---|
| Existing matching repair ticket |  |
| Proposed new repair ticket ID |  |
| Duplicate prevention key | category + reproduction command + failing fixture/manifest + expected class + actual class |
| Original ticket should remain | Blocked / Rejected / In Review |

## 9. Regression command required after repair

```bash

```
