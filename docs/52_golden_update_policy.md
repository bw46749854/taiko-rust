# Golden Update Policy

Status: Step3 expanded policy

## 1. Rule

Golden expectations are review-controlled artifacts. They are not implementation conveniences.

## 2. Required approval

A golden update requires approval from a review session different from the implementation session.

## 3. Required evidence

Every golden update must include:

- affected fixture IDs;
- affected feature IDs;
- reason for update;
- reference to `research/opentaiko/10_phase1_adoption_decisions.md`;
- analyzer diff before/after;
- confirmation that user-song category coverage is unchanged or explicitly updated.

## 4. Prohibited updates

Do not update goldens to hide:

- parser panic;
- missing compatibility report;
- branch route loss;
- skipped score/gauge summary;
- scroll NaN/infinite position;
- missing song end;
- nondeterministic replay.

## 5. Rounding policy

Before final rounding policy is implemented, use rational beat positions and command order. Millisecond golden values are added after the timing model is stable.
