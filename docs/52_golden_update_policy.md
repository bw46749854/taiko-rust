# Golden Update Policy

Status: canonical

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

## 6. Timestamp golden schema

TKT-0005 introduces event timestamp goldens for synthetic BPM / MEASURE / DELAY / OFFSET fixtures. Each committed row must contain these machine-readable fields:

- `fixture_id`: manifest fixture identifier, for example `FX-TIME-005`;
- `event_index`: zero-based event order within the fixture timing evidence stream;
- `event_type`: timing evidence type, such as `note_scheduled`, `bpm_changed`, `measure_changed`, or `delay_applied`;
- `expected_ms`: expected event timestamp in milliseconds;
- `actual_ms`: actual event timestamp in milliseconds from the timing evidence path being reviewed;
- `error_ms`: absolute delta between `expected_ms` and `actual_ms`;
- `tolerance_ms`: per-event acceptance tolerance.

The canonical TKT-0005 synthetic timestamp golden is `fixtures/synthetic/goldens/phase1_timing_timestamp_golden.json`. Implementation PRs may add analyzer support for comparing this schema, but changes to existing expected timestamp values must be split into a dedicated golden update PR unless the implementation ticket explicitly authorizes new fixture adoption and includes the review-session approval evidence from this policy.
