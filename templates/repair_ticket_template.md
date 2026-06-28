# TKT-REPAIR-xxxx: Repair <category> from <failure-id>

Status: Ready
Owner session: Ticket Implementation Session
Review session: QA / Regression Session
Worktree: `worktrees/repair/TKT-REPAIR-xxxx`

## 1. Objective

Repair concrete failing evidence without broadening the original scope.

## 2. Source failure

- Failure report: `reports/failures/<failure>.md`
- Source ticket or gate: `<TKT/GATE>`
- Source item remains: `Rejected`
- Route: `reject`
- Repair kind: `REPAIR`

## 3. Minimal repair scope

- Keep the change limited to the failing command and its regression evidence.

## 4. Required reproduction command

```bash
<original failing command>
```

## 5. Required regression command

```bash
<required regression command>
```

## 6. Retry budget

```bash
taiko_cli loop retry-budget check --ticket TKT-REPAIR-xxxx --format json
```

## 7. Acceptance criteria

- The reproduction command no longer fails.
- The regression command returns a `pass` verdict.
- QA can re-evaluate the original ticket or gate without manual judgement.
