# 99. Codex Worker Handoff Contract

Status: canonical

## Purpose

`OPS-0008` defines the deterministic handoff from the GitHub Actions loop-controller to the next Codex worker surface. GitHub Actions does not execute Codex, GPT, `openai/codex-action@v1`, `OPENAI_API_KEY`, or `CODEX_API_KEY`. It only emits reproducible artifacts that a Codex Cloud, Codex App Automation, or signed-in Codex CLI session can read.

## Boundary

| Component | Role |
|---|---|
| GitHub Actions | verify, gate, merge, advance tickets, emit handoff artifacts |
| Codex Cloud / App / CLI | read the handoff, implement or repair one ticket, open PR |
| Human operator | configure platform surfaces and inspect final reports only |

## Required handoff artifacts

The handoff generator writes these files:

```text
reports/loop/worker_handoff/latest.json
reports/loop/worker_handoff/latest.md
reports/loop/worker_handoff/latest_issue.md
reports/loop/worker_handoff/latest_comment.md
```

The JSON artifact is the machine-readable contract. The Markdown artifact is the prompt the worker reads. The issue/comment artifacts are deterministic GitHub text surfaces for `@codex` or detached worker request workflows.

## Handoff JSON required fields

```json
{
  "schema": "schemas/worker_handoff_schema.md",
  "run_id": "RUN-HANDOFF-...",
  "verdict": "plan",
  "selected_ticket": "OPS-0008",
  "selected_ticket_path": ".loop/tickets/OPS-0008.md",
  "branch": "loop/OPS-0008-next-codex-worker-handoff",
  "implementation_worktree": "worktrees/impl/OPS-0008",
  "review_worktree": "worktrees/review/OPS-0008",
  "qa_worktree": "worktrees/qa/OPS-0008",
  "session_metadata_path": "reports/session_metadata/OPS-0008.toml",
  "qa_verdict_path": "reports/qa/OPS-0008.verdict.json",
  "required_reads": [],
  "allowed_paths": [],
  "forbidden_paths": [],
  "required_commands": [],
  "api_key_required": false,
  "ai_worker_in_github_actions": false
}
```

## Required reads

Each handoff must include at least:

- `AGENTS.md`
- `README.md`
- `docs/99_codex_worker_handoff_contract.md`
- `docs/90_session_metadata_and_path_policy.md`
- `docs/91_repair_materialization_and_retry_budget.md`
- `operations/loop_policy.toml`
- `operations/ticket_transition_policy.toml`
- the selected ticket file

## Allowed and forbidden paths

The generated handoff must constrain the worker to one ticket. During the `OPS` migration rail, the allowed paths are documentation, operations, scripts, workflow, prompt, ticket, gate, schema, fixture, and report-control surfaces. Gameplay implementation files remain out of scope unless the selected ticket explicitly unlocks Phase1 gameplay.

Forbidden paths always include:

```text
.external_assets/
source_context/
STEP*.md
reports/qa/*.verdict.json
reports/regression/*.json
```

Implementation sessions may reference QA/regression paths in PR text, but they must not author QA verdict files.

## GitHub Issue / comment handoff

`latest_issue.md` and `latest_comment.md` may contain an `@codex` mention for repositories where native Codex GitHub integration is available. If `@codex` does not start a worker in the actual repository, the same `latest.md` prompt is used by Codex App Automation. This fallback is deterministic and does not change the gate model.

## Controller integration

After a successful merge and ticket advance, `loop-controller` runs:

```bash
scripts/loop_emit_worker_handoff.py --mode controller --run-id <run_id>
```

The controller uploads `reports/loop/worker_handoff/` as an artifact. It does not call an AI provider.

## Acceptance

`OPS-0008` is accepted when:

- `scripts/check_worker_handoff_static.py` passes;
- `latest.json`, `latest.md`, `latest_issue.md`, and `latest_comment.md` can be generated from the single Ready ticket;
- the generated payload states `api_key_required: false` and `ai_worker_in_github_actions: false`;
- `OPS-0008` is the only Ready ticket during this migration stage.
