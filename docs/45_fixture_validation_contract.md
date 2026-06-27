# 45. Fixture Validation Contract

Status: canonical
Last updated: 2026-06-25

## 1. Purpose

Fixture validation is the first executable test-harness layer for the autonomous loop. Its purpose is not to prove full gameplay correctness. Its purpose is to let AI sessions determine, without human inspection, whether the committed synthetic TJA fixtures are present, structurally readable, and safe to use as the next implementation substrate.

This contract supports the controlling objective in `docs/00_project_objective.md`: AI sessions must be able to read tickets, implement work, verify results, detect failures, route failures into repair tickets, and select the next ticket without extra human judgement.

## 2. Scope for Step8 MVP

Step8 implements the minimum fixture validation surface required before parser, scheduler, headless autoplay, and timing analyzer tickets proceed.

Required commands:

```bash
taiko_cli fixture validate --manifest fixtures/synthetic/phase1_synthetic_manifest.toml --format json
taiko_cli fixture inspect fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --format json
```

## 3. Validation responsibilities

`taiko_cli fixture validate` must:

- read `fixtures/synthetic/phase1_synthetic_manifest.toml`;
- verify that declared fixture count matches concrete fixture entries;
- detect duplicate `fixture_id` values;
- verify that every manifest path exists;
- inspect every referenced `.tja` file;
- return a single machine-readable `pass` or `fail` verdict;
- emit enough JSON detail for QA Session to reject a ticket without opening the chart manually.

`taiko_cli fixture inspect` must:

- read one `.tja` file as UTF-8;
- detect required headers used by Phase1 synthetic fixtures;
- count `#START` and `#END` blocks;
- count chart digit tokens and playable note tokens, including uppercase synthetic special-note tokens;
- classify known TJA commands used by the synthetic fixtures;
- report unknown commands as explicit validation errors;
- return a machine-readable JSON report.

## 4. Required JSON fields

Manifest validation JSON must include:

- `manifest_path`
- `verdict`
- `declared_fixture_count`
- `manifest_entry_count`
- `validated_count`
- `missing_count`
- `invalid_count`
- `duplicate_fixture_ids`
- `fixtures`
- `issues`

Single fixture inspection JSON must include:

- `path`
- `verdict`
- `title`
- `courses`
- `header_count`
- `command_count`
- `classified_command_count`
- `unknown_commands`
- `start_count`
- `end_count`
- `measure_count`
- `digit_token_count`
- `note_token_count`
- `issues`

## 5. MVP pass/fail rules

A fixture manifest passes only when:

- the manifest parses;
- declared fixture count equals the number of `[[fixtures]]` entries;
- all fixture IDs are unique;
- every fixture path exists;
- every fixture inspection verdict is `pass`.

A fixture inspection passes only when:

- required headers are present: `TITLE`, `BPM`, `WAVE`, `COURSE`, `LEVEL`;
- at least one `#START` exists;
- at least one `#END` exists;
- `#END` count is not less than `#START` count;
- at least one playable note token exists. In Step8 this includes non-zero digit tokens and uppercase synthetic special-note tokens such as `C`, `F`, and `G`;
- every TJA command in the fixture is classified by the Step8 known-command set;
- no invalid chart token appears inside chart data.

Warnings may be present, but any error severity issue makes the verdict `fail`.

## 6. Known-command set for Step8

The Step8 MVP must classify the commands already used by committed synthetic fixtures:

```text
#START
#END
#BPMCHANGE
#MEASURE
#DELAY
#SCROLL
#GOGOSTART
#GOGOEND
#BARLINE
#BARLINEON
#BARLINEOFF
#BRANCHSTART
#BRANCHEND
#SECTION
#LEVELHOLD
#N
#E
#M
#BMSCROLL
#HBSCROLL
#NMSCROLL
#SUDDEN
#DIRECTION
#JPOSSCROLL
#NEXTSONG
#BGAON
#CAMZOOM
#LYRIC
```

This set is intentionally fixture-facing. Full OpenTaiko command semantics remain owned by later parser and compatibility tickets.

## 7. Out of scope

Step8 does not implement:

- complete OpenTaiko parser semantics;
- course selection behavior beyond structural reporting;
- timing schedule calculation;
- branch evaluation;
- score or gauge logic;
- audio playback or audio scheduling;
- headless autoplay;
- timing log analysis.

Those behaviors must not be accepted as implicit merely because Step8 fixture validation passes.

## 8. Failure routing

A `fail` verdict from fixture validation must produce a failure report using `templates/failure_report_template.md`.

Recommended failure categories:

- `fixture_manifest_error`
- `fixture_file_missing`
- `fixture_tja_structure_error`
- `fixture_unknown_command`
- `fixture_cli_contract_error`

Repair tickets generated from these failures must include:

- the exact command that produced the failure;
- the JSON report path or embedded JSON excerpt;
- the fixture ID or file path;
- the expected pass criteria from this contract;
- the next command that proves the repair.

## 9. Gate linkage

`GATE-0040` is the fixture validation readiness gate. It may pass only after `TKT-0002` produces machine-readable evidence for both manifest validation and single-fixture inspection.

Passing `GATE-0040` unlocks parser-expansion and headless-readiness tickets. Rejecting `GATE-0040` routes to fixture validation repair before scheduler, autoplay, or timing analyzer tickets proceed.

## 9. External asset boundary

Synthetic fixtures remain committed test fixtures. User-selected charts, audio, skins, and other OpenTaiko-compatible assets are external and resolved only through the OPS-0004 content-root contract. Fixture validation must not require `.external_assets/` unless a command explicitly targets the development asset bundle.
