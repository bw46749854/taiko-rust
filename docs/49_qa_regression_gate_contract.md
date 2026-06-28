# 49. QA Regression Gate Contract

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

The QA verdict route makes QA / Regression Session verdicts machine-readable.

The controlling objective is not to add another review checklist. The objective is to let a separate QA / Regression Session run deterministic commands, receive `pass`, `reject`, or `block`, and route the result back into the loop without additional human design judgement.

This contract is the first QA gate that consumes the Step8 fixture validator, Step9 headless autoplay evidence, Step10 timing analyzer, and failure-feedback route route as one verdict.

## 2. Required command surface

```bash
taiko_cli qa run --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --threshold-ms 1.0 --format json
taiko_cli qa compare --baseline reports/baseline --current reports/current --format json
taiko_cli qa verdict --input reports/qa/phase1_loop.qa.json --format json
```

The command surface belongs to `taiko_cli`. It is part of autonomous loop orchestration. It is not gameplay UI.

## 3. `qa run` contract

`qa run` executes the minimum autonomous regression chain available at QA verdict route.

Required internal checks:

1. fixture manifest validation;
2. synthetic fixture structure inspection through the chart crate;
3. perfect headless autoplay over manifest fixtures;
4. timing analyzer over the headless evidence;
5. failure-feedback route availability.

Required JSON fields:

| Field | Meaning |
|---|---|
| `verdict` | `pass`, `reject`, or `block` |
| `manifest` | Manifest path used by QA |
| `threshold_ms` | Timing threshold used by the analyzer |
| `fixture_verdict` | `pass` / `reject` outcome from fixture validation |
| `headless_verdict` | `pass` / `reject` outcome from headless autoplay |
| `timing_verdict` | `pass` / `reject` outcome from timing analyzer |
| `failure_route_ready` | Whether failure feedback route route exists |
| `required_reports` | Reports expected to be archived by QA Session |
| `issues` | Machine-readable issues that explain reject/block |

## 4. Verdict rules

| Condition | Verdict |
|---|---|
| All fixture/headless/timing checks pass and failure route exists | `pass` |
| Any executable check returns fail but failure route exists | `reject` |
| Required manifest, command surface, or failure route is missing | `block` |

A `reject` must be convertible into a failure report using `templates/failure_report_template.md` and then into a repair ticket using `taiko_cli loop ticket propose --from-failure`.

A `block` means the QA Session lacks the required evidence path to evaluate the ticket. It must not be treated as gameplay failure.

## 5. `qa compare` contract

`qa compare` compares a baseline report directory and a current report directory.

Required JSON fields:

- `verdict`
- `baseline`
- `current`
- `compared_files`
- `missing_current`
- `missing_baseline`
- `differing_files`

Verdict rules:

| Condition | Verdict |
|---|---|
| Both directories exist and no files differ or disappear | `pass` |
| Both directories exist and files differ or disappear | `reject` |
| Either directory is missing | `block` |

The QA verdict route only requires deterministic file comparison. OpenTaiko-equivalence tolerance policy remains the responsibility of timing and gameplay-specific later tickets.

## 6. `qa verdict` contract

`qa verdict` reads a QA JSON report and emits a normalized verdict for gate automation.

Required JSON fields:

- `verdict`
- `source`
- `source_verdict`
- `next_action`
- `failure_report_required`

Verdict mapping:

| Input report verdict | Normalized verdict | Next action |
|---|---|---|
| `pass` | `pass` | advance to next eligible ticket |
| `reject` | `reject` | create or update failure report and repair ticket |
| `block` | `block` | satisfy missing evidence before implementation continues |
| missing/unknown | `block` | repair QA report or CLI contract |

## 7. Gate evidence

`GATE-0080` requires:

- `taiko_cli qa run` JSON;
- `taiko_cli qa compare` JSON or an explicit block explaining missing baseline/current reports;
- `taiko_cli qa verdict` JSON;
- cargo command results in Rust-enabled sessions;
- evidence that QA Session ran in a different worktree from the implementation worktree;
- failure-feedback route confirmation from failure feedback route.

## 8. Non-goals

The QA verdict route does not require complete OpenTaiko timing equivalence, full chart feature implementation, automatic PR creation, or automatic branch mutation. It creates a deterministic QA verdict layer that later Phase1 feature tickets must satisfy.

## 9. Asset bundle verdict routing

QA gates that require user-selected assets must treat a missing or placeholder development asset bundle as `block`. A sha256 mismatch, unsafe zip member, or committed user-selected asset payload is also `block` or static-policy failure before gameplay evaluation. Gameplay `reject` is reserved for executable behavior failures after the content root is available.
