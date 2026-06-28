# Phase1 Gameplay Loop Reports

Status: canonical

This directory stores generated Step23 Phase1 gameplay-loop start packets.

Expected generated files:

- `reports/phase1_gameplay_loop/<run_id>/phase1_gameplay_start.json`
- `reports/phase1_gameplay_loop/<run_id>/phase1_gameplay_start.md`
- `reports/phase1_gameplay_loop/<run_id>/phase1_ticket_prompt.md`
- `reports/phase1_gameplay_loop/<run_id>/phase1_command_matrix.md`

Generated reports are not shipped as acceptance evidence in the bootstrap package. They are created by `scripts/render_phase1_gameplay_ticket_prompt.py` when the loop enters Phase1 gameplay work.
