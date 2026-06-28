# 95. Phase1 Gameplay Loop Start

Status: canonical

## 1. Purpose

The Phase1 gameplay worker handoff opens the Phase1 gameplay implementation lane without bypassing the established autonomous-loop gates.

The package now has enough loop substrate to prepare the first gameplay ticket handoff. OPS-0009 does not by itself mark `TKT-0005` Ready; `TKT-0005` remains Blocked until `TKT-0060`, `GATE-0090`, and `GATE-OPS-0000` entry evidence have passed. This document defines the machine contract that makes `TKT-0005` the first selectable gameplay ticket after those prerequisites pass.

## 2. Scope

The Phase1 gameplay worker handoff adds:

- a Phase1 gameplay start policy;
- a deterministic ticket-prompt renderer for the first gameplay ticket;
- a dedicated Codex worker prompt for Phase1 feature implementation;
- a reports directory for generated gameplay-loop start packets;
- static validation that the gameplay loop cannot start from prose or manual ordering.

The Phase1 gameplay worker handoff does not add gameplay implementation logic. It does not implement BPM, MEASURE, DELAY, OFFSET, roll, branch, score, gauge, scroll, rendering, audio, or input.

## 3. Start rule

The first gameplay ticket is always `TKT-0005`.

`TKT-0005` may be rendered as an executable worker prompt only when the following evidence exists:

- `TKT-0060` is `Done`;
- `GATE-0090` has a gate report under `.loop/session_logs/GATE-0090-report.md`;
- `operations/phase1_feature_ticket_manifest.toml` validates;
- the first manifest ticket is `TKT-0005`;
- every manifest ticket requires QA run, QA verdict, and failure-route evidence;
- session metadata and path policy gates exist;
- repair materialization and retry-budget gates exist;
- auto-merge and E2E smoke loop checks exist.

When those conditions are missing, the renderer must emit a machine-readable `block` result. It must not silently produce an implementation prompt as if the ticket were ready.

## 4. Command surface

```bash
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --force-preview --dry-run
scripts/render_phase1_gameplay_ticket_prompt.py --ticket TKT-0005 --run-id RUN-YYYYMMDD-0001
scripts/check_phase1_gameplay_start_static.py
```

The default command is conservative. It reports `block` while bootstrap prerequisites are missing. `--force-preview` exists only to preview the prompt structure; it does not authorize implementation.

## 5. Generated artifacts

A non-dry-run execution writes the following files:

- `reports/phase1_gameplay_loop/<run_id>/phase1_gameplay_start.json`
- `reports/phase1_gameplay_loop/<run_id>/phase1_gameplay_start.md`
- `reports/phase1_gameplay_loop/<run_id>/phase1_ticket_prompt.md`
- `reports/phase1_gameplay_loop/<run_id>/phase1_command_matrix.md`

These files are generated evidence and are not shipped as completed acceptance evidence in the bootstrap package.

## 6. Worker constraints

A Phase1 gameplay worker must:

- work on one ticket only;
- read `AGENTS.md`, the target ticket, the manifest, and the relevant compatibility/research documents;
- create implementation diffs only under allowed implementation paths;
- never write QA verdict files;
- never mark tickets Done;
- never pass gates;
- never use `OPENAI_API_KEY`, `CODEX_API_KEY`, or `openai/codex-action@v1`;
- produce a PR only after scoped changes and local evidence exist.

## 7. Evidence floor for TKT-0005

`TKT-0005` must include, at minimum:

- implementation plan;
- plan review request;
- command log;
- fixture validation when parser/chart timing semantics changed;
- headless autoplay report;
- timing analyzer report;
- QA run JSON from a separate QA worktree;
- QA verdict JSON;
- failure report and materialized repair ticket on `reject`;
- blocker ticket on `block`;
- retry-budget evidence for repeated attempts;
- next-ticket transition evidence.

## 8. Transition to Phase1 implementation

After Phase1 gameplay worker handoff, the loop may enter Phase1 gameplay implementation only through the controller and the manifest. The first implementation PR generated from this lane must be for `TKT-0005`, and its auto-merge eligibility remains governed by session separation metadata, repair materialization and retry-budget route repair/retry, auto-merge controller, and E2E smoke-loop evidence.
