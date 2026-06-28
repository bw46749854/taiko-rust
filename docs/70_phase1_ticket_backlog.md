# 70. Phase1 Ticket Backlog

Status: canonical

## Initial state

Only `OPS-0001` is Ready during the operations migration. `TKT-0000` and all implementation tickets are Blocked until the migration rail and the relevant gates pass.

## Ticket list

| Ticket | Title | Initial status | Primary gate/dependency |
|---|---|---:|---|
| TKT-0000 | Spec repair gate and bootstrap consistency check | Blocked | OPS migration completion |
| TKT-0001 | Rust workspace skeleton and Loop CLI MVP | Blocked | GATE-0020, TKT-0000 |
| TKT-0002 | Fixture validation MVP and basic TJA inspection | Blocked | TKT-0001, GATE-0030 |
| TKT-0003 | Headless autoplay MVP | Blocked | TKT-0002, GATE-0040 |
| TKT-0004 | Timing log analyzer MVP | Blocked | TKT-0003, GATE-0050 |
| TKT-0040 | Failure feedback loop MVP | Blocked | TKT-0004, GATE-0060 |
| TKT-0050 | QA regression gate MVP | Blocked | TKT-0040, GATE-0070 |
| TKT-0060 | Phase1 feature loop entry manifest and planner | Blocked | TKT-0050, GATE-0080 |
| TKT-0005 | BPM MEASURE DELAY OFFSET timeline | Blocked | TKT-0060, GATE-0090 |
| TKT-0006 | Roll big-roll balloon and BalloonEx | Blocked | TKT-0005 |
| TKT-0007 | GOGO and BARLINE display-state events | Blocked | TKT-0005 |
| TKT-0008 | Branch parser N/E/M SECTION LEVELHOLD | Blocked | TKT-0005, TKT-0006 |
| TKT-0009 | Branch condition evaluator | Blocked | TKT-0008, TKT-0011 |
| TKT-0010 | Headless autoplay baseline expansion | Blocked | TKT-0005, TKT-0006, TKT-0007 |
| TKT-0011 | Score gauge and clear model | Blocked | TKT-0010, TKT-0007 |
| TKT-0012 | SCROLL and scroll mode model | Blocked | TKT-0005, TKT-0010 |
| TKT-0013 | SUDDEN DIRECTION JPOSSCROLL parse/report | Blocked | TKT-0012 |
| TKT-0014 | Timing log schema expansion | Blocked | TKT-0010, TKT-0011, TKT-0012 |
| TKT-0015 | Timing log analyzer expansion | Blocked | TKT-0014 |
| TKT-0035 | Synthetic fixture coverage pack | Blocked | GATE-0010, TKT-0015 |
| TKT-0075 | User-selected song validation harness | Blocked | TKT-0035 |

## Backlog policy

- The backlog is intentionally ordered around loop infrastructure -> feature-loop entry -> parser/timeline -> runtime -> analyzer -> coverage -> user-song validation.
- `TKT-0060` and `GATE-0090` are mandatory before `TKT-0005`; this prevents gameplay implementation from starting before QA verdict and failure-route evidence are machine-readable.
- Branch condition evaluation waits for score/gauge because score and judgement counters can affect branch decisions.
- User-selected real-song validation is last because it requires the synthetic coverage harness and analyzer to be stable.


## Operations migration backlog

| Ticket | Title | Initial status | Primary dependency |
|---|---|---:|---|
| OPS-0001 | Migration ticket rail and bootstrap freeze | Ready | none |
| OPS-0002 | Legacy cleanup canonicalization | Blocked | OPS-0001 |
| OPS-0003 | Public repository hardening | Done | OPS-0002 |
| OPS-0004 | Drive zip asset bundle contract | Done | OPS-0003 |
| OPS-0005 | GitHub Actions gate normalization | Done | OPS-0004 |
| OPS-0006 | Auto-merge candidate discovery | Done | OPS-0005 |
| OPS-0007 | Ticket advance engine | Done | OPS-0006 |
| OPS-0008 | Next Codex worker handoff | Ready | OPS-0007 |
| OPS-0009 | E2E smoke and Phase1 entry unlock | Blocked | OPS-0008 |

The OPS rail is the active migration backlog. Gameplay implementation remains frozen until `OPS-0009` completes and `GATE-OPS-0000` passes.


## OPS-0008 migration note

During `OPS-0008`, gameplay implementation tickets remain Blocked. The handoff generator may emit preview worker prompts, but Phase1 gameplay implementation tickets remain Blocked until `OPS-0009`, `GATE-OPS-0000`, `TKT-0060`, and `GATE-0090` pass.


## OPS-0009 migration completion note

After `OPS-0009`, `GATE-OPS-0000`, `TKT-0060`, and `GATE-0090` pass, the only Ready ticket is `TKT-0005`. Downstream gameplay tickets remain Blocked until `TKT-0005` and their manifest dependencies are completed.
