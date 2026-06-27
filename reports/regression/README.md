# Regression Reports

Status: canonical

Regression reports describe failures detected after an autonomous merge. They are input to `scripts/loop_revert_last_merge.sh` and to repair ticket materialization.

Expected path:

```text
reports/regression/<run_id>.json
```

The report must identify the autonomous merge run, the failing command, the failure signature, and the requested revert reason.
