# 74. Phase1 Feature Loop Entry Contract

Status: canonical

## 1. Purpose

This contract defines the point where the autonomous loop may move from loop-infrastructure tickets into Phase1 gameplay feature implementation.

The purpose is not to approve gameplay by prose review. The purpose is to prove that Control Session can select the next gameplay ticket, Ticket Implementation Session can execute it, QA / Regression Session can reject it from a separate worktree, and any reject can return to a repair ticket without additional human design judgement.

## 2. Entry rule

Phase1 gameplay feature tickets must remain Blocked until all of the following are true:

- `TKT-0050` is Done.
- `GATE-0080` has passed.
- `TKT-0060` is Done.
- `GATE-0090` has passed.
- `operations/phase1_feature_ticket_manifest.toml` validates.
- `taiko_cli phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json` emits exactly one first eligible gameplay ticket or a machine-readable `block` verdict.

## 3. Required command surface

```bash
taiko_cli phase1 feature validate --manifest operations/phase1_feature_ticket_manifest.toml --format json
taiko_cli phase1 feature plan --manifest operations/phase1_feature_ticket_manifest.toml --format json
taiko_cli loop next --format json
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

## 4. Feature ticket evidence floor

Every Phase1 gameplay feature ticket must require the following evidence:

- implementation plan;
- Design Review Session plan verdict;
- cargo command log;
- fixture validation JSON when parser/chart behavior changed;
- headless autoplay JSON when runtime behavior changed;
- timing analyzer JSON when timing, judgement, scroll, or autoplay behavior changed;
- QA run JSON from a QA worktree different from the implementation worktree;
- QA verdict JSON with `pass`, `reject`, or `block`;
- failure report path and proposed repair ticket path when QA verdict is `reject`;
- next-ticket transition evidence.

## 5. Verdict semantics

| Verdict | Meaning | Next action |
|---|---|---|
| `pass` | The ticket meets its acceptance criteria and QA evidence floor. | Mark ticket Done and let Control Session recompute next ticket. |
| `reject` | Evidence exists and proves a defect or contract mismatch. | Create or update a failure report, propose a repair ticket, and keep downstream tickets Blocked. |
| `block` | Required evidence is missing or environment cannot execute required commands. | Do not approve the ticket. Produce missing-evidence list. |

## 6. Human judgement removal

A Phase1 gameplay ticket must not require manual approval based on whether the feature is "good enough" from logs, screenshots, or subjective play feel. The required output is machine-readable JSON from the feature plan, QA run, QA verdict, timing analyzer, and failure feedback commands.

OpenTaiko parity questions that are not yet encoded must become explicit research findings or adoption decisions before they can be used as pass criteria.

## 7. Required reports

The loop may write reports under:

- `reports/phase1_feature_loop/phase1_feature_plan.json`
- `reports/phase1_feature_loop/phase1_feature_validate.json`
- `reports/qa/phase1_loop.qa.json`
- `reports/qa/phase1_loop.verdict.json`
- `reports/failures/*.md`

These reports are generated outputs and are intentionally not shipped as pass evidence in the bootstrap package.
