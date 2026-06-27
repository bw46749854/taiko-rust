# Phase1 User-selected Song Category Matrix

Status: adopted for Step3 coverage design

## 1. Purpose

Synthetic fixtures prove isolated behavior. User-selected songs prove that real OpenTaiko-style charts survive normal-play integration.

The standard validation set is 10 local songs. The user supplies files and maps each local chart to one category in `fixtures/user_selected/manifests/user_song_manifest.yaml` or equivalent JSON/TOML.

No commercial song, chart, audio, jacket, video, or skin asset is committed to this project package.

## 2. Standard 10 categories

| Category ID | Required role | Required feature coverage | Recommended examples from assessment | Acceptance focus |
|---|---|---|---|---|
| C01 | Basic chart | Don/Ka, big notes, barlines, normal BPM, course selection, score/gauge | basic official-style chart | stable normal play, no parse warnings beyond known metadata |
| C02 | Mixed subdivision chart | 8/12/16/24, mixed n divisions, GOGO, barline gimmick | Sync Your World | arbitrary scheduler and gogo state |
| C03 | BPM/measure/timing chart | BPMCHANGE, MEASURE, DELAY, signed OFFSET | 美しく忙しきドナウ or equivalent | timing timeline and BGM/note alignment |
| C04 | Roll chart | normal roll, big roll, balloon, BalloonEx/kusudama | Destr0yer or equivalent | roll/balloon count and body lifecycle |
| C05 | Branch chart A | accuracy or p/pp branch, N/E/M route | メタルホーク BGM1 or equivalent | route decision from accuracy counters |
| C06 | Branch chart B | roll/score branch, SECTION, LEVELHOLD, branch balloon arrays | SHOGYO MUJO or equivalent | route decision from non-accuracy counters |
| C07 | Scroll/overtake chart | positive/negative/zero/high SCROLL, overtaking | ドンカマ2000 or equivalent | visual anomaly and gameplay timing separation |
| C08 | Special visual timing chart | HBSCROLL, BMSCROLL, SUDDEN, DIRECTION, JPOSSCROLL | Irregular Clock or equivalent | parse/report and visual-state logging |
| C09 | Integrated gimmick chart | BPM, scroll, branch, roll, gogo, barline combined | Calamity Fortune or equivalent | multi-subsystem regression |
| C10 | Long/high-load chart | high density, long duration, many notes, optional extreme scroll | 幽玄ノ乱 or equivalent | endurance, memory, deterministic log size |

The named examples are not bundled requirements. They are examples of the coverage intent from the assessment. Local substitutes are acceptable only when the manifest maps their features to the same category and the coverage validator agrees.

## 3. Required manifest fields per song

Each song entry must provide:

- local chart path;
- local audio root or audio file path;
- selected course/difficulty;
- category ID;
- declared feature tags;
- expected branch routes to exercise;
- expected unsupported/non-scope commands;
- pass criteria overrides, if any.

## 4. Pass criteria

A user-selected song passes when all conditions below are true:

1. Parser finishes without panic.
2. All unsupported commands are represented in compatibility report.
3. Selected course loads.
4. Headless autoplay reaches `song_end`.
5. Timing analyzer reports no fatal anomaly.
6. Required branch route coverage for the category is met or explicitly marked unreachable with report.
7. Score/gauge/clear summary is present.
8. The run is deterministic across two consecutive executions using the same manifest.

## 5. Failure classification

| Failure | Classification | Action |
|---|---|---|
| parse panic | blocker | create parser ticket |
| unknown command without report | blocker | create compatibility-report ticket |
| song does not reach end | blocker | create runtime/timing ticket |
| branch route not observable | conditional | check manifest route assumptions; then create branch ticket |
| visual scroll anomaly only | blocker for C07/C08/C09, warning otherwise | create scroll/analyzer ticket |
| audio missing | manifest error | user supplies local asset path; not implementation failure |
