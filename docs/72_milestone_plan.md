# 72. Milestone Plan

Status: canonical

## Milestone M0: Bootstrap consistency

Target tickets:

- TKT-0000
- GATE-0000
- GATE-0010
- GATE-0020

Output:

- implementation tickets can safely move to Ready.

## Milestone M1: Parser and scheduler foundation

Target tickets:

- TKT-0001
- TKT-0002
- TKT-0003
- TKT-0004
- TKT-0005

Output:

- Rust workspace exists.
- TJA metadata/course parser exists.
- arbitrary subdivision note scheduler exists.
- core note mapping exists.
- BPM/MEASURE/DELAY/OFFSET timeline exists.

## Milestone M2: Runtime normal-play mechanics

Target tickets:

- TKT-0006
- TKT-0007
- TKT-0008
- TKT-0009
- TKT-0010
- TKT-0011
- TKT-0012
- TKT-0013

Output:

- rolls, balloons, branch, score, gauge, scroll, and parse/report compatibility exist.
- headless autoplay can complete implemented fixture groups.

## Milestone M3: Analyzer and synthetic coverage

Target tickets:

- TKT-0014
- TKT-0015
- TKT-0035

Output:

- timing log schema is complete for Phase1.
- analyzer can accept/reject Phase1 fixture runs.
- all 35 synthetic fixtures are wired.

## Milestone M4: User-selected song validation

Target ticket:

- TKT-0075

Output:

- local-only manifest validation supports 10 user-selected song categories.
- Phase1 completion evidence can include real-song validation without bundling assets.
