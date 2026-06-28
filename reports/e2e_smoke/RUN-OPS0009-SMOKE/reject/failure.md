# FF-SMOKE-REJECT: synthetic QA reject smoke

Failure ID: FF-SMOKE-REJECT
Source ticket or gate: TKT-SMOKE-REJECT
Category: runtime_contract
Duplicate key: smoke-reject-runtime-contract
Observed command: scripts/run_e2e_smoke_loop.sh --scenario reject --dry-run
Expected: QA pass
Actual: QA reject
Route: reject
Repair scope: repair the failing implementation contract only
Reproduction command: scripts/run_e2e_smoke_loop.sh --scenario reject --dry-run
Regression command: scripts/run_e2e_smoke_loop.sh --scenario all --dry-run
