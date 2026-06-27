# Test Harness Overview

Status: Step3 expanded test harness plan

## 1. Purpose

The Phase1 test harness proves that the Rust implementation can parse, schedule, simulate, and validate OpenTaiko-compatible normal-play charts without human judgement during loop execution.

## 2. Two-layer validation

| Layer | Input | Purpose | Required before Phase1 pass |
|---|---|---|---|
| Synthetic fixtures | committed small `.tja` files | isolate each feature and make failures local | yes |
| User-selected songs | local manifest supplied by user | real-world chart compatibility | yes |

Synthetic fixtures are committed. User-selected commercial assets are not committed.

## 3. Components

| Component | Responsibility |
|---|---|
| `taiko_cli fixture validate` | parse synthetic manifest, verify fixture metadata, run controlled checks |
| `taiko_cli headless autoplay` | deterministic autoplay without renderer |
| `taiko_cli timing analyze` | evaluate timing log against selected profile |
| `taiko_cli user-song validate` | validate local manifest, local assets, real-song runs |
| `taiko_cli report coverage` | emit feature/category coverage report |

## 4. Harness data flow

```text
TJA fixture / user manifest
  -> parser
  -> domain chart
  -> arbitrary note scheduler
  -> headless runtime/autoplay
  -> timing JSONL
  -> analyzer
  -> Markdown + JSON report
```

## 5. Required harness outputs

Every run produces:

- timing JSONL;
- parse/compatibility report;
- fixture or user-song validation report;
- coverage summary;
- deterministic replay hash.

## 6. Separation of responsibilities

Implementation sessions may add runtime code. QA sessions own analyzer decisions and gate status. Golden expectations cannot be updated by the same session that implements code.
