# Loop Controller Reports

Status: canonical

`taiko_cli loop run-once --mode apply` writes controller artifacts under `reports/loop/<run_id>/`:

- `controller_plan.json`
- `controller_plan.md`
- `next_codex_prompt.md`

These files are Step17 controller evidence. They do not replace Rust preflight, QA verdicts, review reports, or gate reports.
