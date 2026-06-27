# Rust Preflight Report

Status: draft-template

## Verdict

- Schema: `rust-preflight.v1`
- Scope: `loop-cli` or `current-package`
- Verdict: `pass`, `reject`, or `block`
- Generated UTC:
- Git SHA:

## Environment

- Runner OS:
- Rust version:
- Cargo version:

## Command evidence

| Command ID | Phase | Status | Exit code | Logs |
|---|---|---:|---:|---|
| `cargo_fmt` | cargo |  |  |  |
| `cargo_clippy` | cargo |  |  |  |
| `cargo_test` | cargo |  |  |  |
| `loop_inspect_tickets` | loop_cli |  |  |  |
| `loop_gate_0000` | loop_cli |  |  |  |

## Transition decision

- `pass`: continue detached review and gate evaluation.
- `reject`: route failing command logs to failure feedback and repair-ticket selection.
- `block`: repair the Rust-enabled CI or Codex Cloud environment before accepting implementation work.

## Remaining risk

List only machine-verifiable risks. Do not use prose-only acceptance.
