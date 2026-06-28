# 62. Loop Engineering Flow

Status: canonical

## Overview

Phase1 loop engineering proceeds through four pre-implementation gates and then ticket loops.

```text
A0 Compatibility Contract Loop
 -> A1 OpenTaiko Source Extraction Loop
 -> A2 Coverage Design Loop
 -> B Ticket Implementation Loop
 -> C QA / Regression Loop
```

## A0. Compatibility Contract Loop

1. Read compatibility contract compatibility documents.
2. Check feature classification completeness.
3. Check `research/opentaiko/10_phase1_adoption_decisions.md` alignment.
4. Check ticket and prompt references.
5. Run `GATE-0000` review.
6. Produce `.loop/session_logs/GATE-0000-report.md`.

## A1. OpenTaiko Source Extraction Loop

1. Select one OpenTaiko source area.
2. Record source map and observed behavior.
3. Update research findings.
4. Update adoption decision.
5. Design Review Session checks evidence sufficiency.
6. Missing evidence returns to the Spec Extraction Session.

## A2. Coverage Design Loop

1. Read feature matrix.
2. Read fixture traceability.
3. Read user-song category matrix.
4. Validate timing log and analyzer fields.
5. Run `GATE-0010` review.
6. Produce `.loop/session_logs/GATE-0010-report.md`.

## B. Ticket Implementation Loop

1. Control Session selects the next Ready ticket.
2. Implementation Session reads required docs.
3. Implementation Session writes a plan.
4. Design Review Session approves or rejects the plan.
5. Implementation Session implements.
6. Implementation Session runs required commands.
7. QA Session runs fixture/analyzer checks as required.
8. Design Review Session reviews the diff.
9. Control Session records outcome.

## C. QA / Regression Loop

1. Run full synthetic fixtures.
2. Run timing log analyzer.
3. Run user-selected song validation when local manifest exists.
4. Check branch route coverage.
5. Check score/gauge/clear outcomes.
6. Check compatibility reports.
7. Produce QA report.

## Loop stop condition

Phase1 is complete only after:

- all Must implement gameplay features pass synthetic fixture coverage,
- user-selected song validation passes for the 10 standard categories,
- timing analyzer has no blocking anomalies,
- parser compatibility report contains no unclassified normal-play commands,
- QA / Regression Session accepts the milestone.
