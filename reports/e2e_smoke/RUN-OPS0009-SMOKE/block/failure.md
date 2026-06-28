# FF-SMOKE-BLOCK: synthetic QA block smoke

Failure ID: FF-SMOKE-BLOCK
Source ticket or gate: GATE-SMOKE-BLOCK
Category: environment_missing_evidence
Duplicate key: smoke-block-missing-evidence
Observed command: scripts/run_e2e_smoke_loop.sh --scenario block --dry-run
Expected: machine evidence exists
Actual: required evidence missing
Route: block_env
Repair scope: restore missing environment or evidence path before gameplay implementation
Reproduction command: scripts/run_e2e_smoke_loop.sh --scenario block --dry-run
Regression command: scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
