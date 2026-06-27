# TKT-ENV/SPEC/TOOL-xxxx: Blocker from <failure-id>

Status: Ready
Owner session: Test Infrastructure Session / Specification Extraction Session
Review session: QA / Regression Session
Worktree: `worktrees/<env|spec|tool>/<ticket-id>`

## 1. Objective

Repair a blocker before implementation work continues.

## 2. Source failure

- Failure report: `reports/failures/<failure>.md`
- Source ticket or gate: `<TKT/GATE>`
- Source item remains: `Blocked`
- Route: `block`
- Repair kind: `ENV` / `SPEC` / `TOOL`

## 3. Required reproduction command

```bash
<original failing command>
```

## 4. Required regression command

```bash
<required regression command>
```

## 5. Acceptance criteria

- The blocker is removed.
- The downstream implementation ticket remains blocked until this blocker ticket passes.
- The same failure report classifies to the same route after repair.
