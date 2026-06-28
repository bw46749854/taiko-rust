# 64. Review and QA Gates

Status: canonical

## Gate hierarchy

| Gate | Purpose | Owner | Reviewer |
|---|---|---|---|
| `GATE-0000` | Spec repair and consistency | Control Session | Design Review Session |
| `GATE-0010` | Coverage readiness | Test Infra Session | QA / Regression Session |
| `GATE-0020` | Implementation readiness | Control Session | Design Review + QA |

## Plan review gate

Before implementation, a plan must prove:

- required docs were read,
- OpenTaiko adoption decision is referenced,
- crate/binary names are canonical,
- fixture/analyzer impact is identified,
- out-of-scope items are not pulled into the ticket.

## Implementation review gate

After implementation, review must inspect:

- diff scope,
- tests added or updated,
- parser compatibility report,
- fixture output,
- timing analyzer output,
- score/gauge/branch/scroll risks.

## QA gate

QA checks:

- synthetic fixtures,
- timing log analyzer,
- user-selected manifest validation where available,
- no bundled copyrighted assets,
- no unclassified normal-play command.

## Blocking conditions

The following block acceptance:

- crash on valid OpenTaiko normal-play chart input,
- note scheduling drift outside tolerance,
- missing branch route coverage for branch tickets,
- score/gauge state missing for score/gauge tickets,
- silent ignore of a normal-play command,
- user-song local asset copied into repo,
- implementation session self-approves.


## QA verdict route gate

QA / Regression Session must produce machine-readable verdicts through:

```bash
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa compare --baseline reports/baseline --current reports/current --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

A prose-only approval is invalid. `pass` advances to the next eligible ticket, `reject` routes through failure feedback, and `block` identifies missing evidence.
