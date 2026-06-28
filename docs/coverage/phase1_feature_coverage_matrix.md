# Phase1 Feature Coverage Matrix

Status: adopted
Scope source: compatibility contract Compatibility Contract, OpenTaiko research OpenTaiko research, `research/opentaiko/10_phase1_adoption_decisions.md`

## 1. Purpose

This matrix defines the minimum coverage required before Phase1 implementation tickets can be marked Ready.

Phase1 completion is not proven by a single playable chart. Completion requires both layers below:

1. Synthetic fixture coverage: small, controlled TJA files that isolate parser, scheduler, branch, scroll, score/gauge, and audio/course behavior.
2. User-selected real song validation: locally supplied songs selected by the user to represent real-world OpenTaiko normal-play compatibility.

Commercial song/audio/chart assets must not be committed to this bundle. User-selected charts are referenced by local path in a manifest.

## 2. Coverage status legend

| Status | Meaning |
|---|---|
| Required | Must be covered by at least one synthetic fixture and at least one automated assertion |
| Required-real | Must also be exercised by user-selected real songs |
| Parse/report | Must parse or report without crash; exact gameplay reproduction is not required in Phase1 |
| Non-scope/report | Must be reported as explicit non-scope when encountered |

## 3. Feature matrix

| ID | Feature | Phase1 class | Synthetic fixture IDs | User song category | Required assertions |
|---|---|---|---|---|---|
| F001 | COURSE selection from multi-course TJA | Required | FX-COURSE-001 | C01,C10 | chosen course loads; other courses ignored without parse failure |
| F002 | WAVE / PATH_WAV / BGM chip | Required | FX-AUDIO-001 | all | BGM reference resolved; missing local audio reports warning in headless mode |
| F003 | OFFSET positive / negative | Required | FX-TIME-001, FX-TIME-002, FX-AUDIO-001 | C03 | first note/BGM relation matches signed offset model |
| F004 | BPM header and initial BPM point | Required | FX-TIME-001 | all | first note ms from BPM timeline is deterministic |
| F005 | BPMCHANGE mid-chart | Required-real | FX-TIME-003, FX-INTEGRATED-001 | C03,C09 | event timeline changes future note time/visual state only after command |
| F006 | MEASURE changes | Required-real | FX-TIME-004 | C03,C08 | arbitrary measure ratio affects note spacing and barline schedule |
| F007 | DELAY | Required-real | FX-TIME-005 | C03 | time cursor and scroll cursor update consistently |
| F008 | Arbitrary note-token scheduler | Required-real | FX-TIME-006, FX-TIME-007, FX-TIME-008, FX-INTEGRATED-002 | C02,C06,C10 | n tokens in measure are evenly distributed for any n >= 1 |
| F009 | 4/8/12/16/24/36 split examples | Required-real | FX-TIME-006 | C02 | token-to-beat mapping matches expected rational positions |
| F010 | Mixed subdivision measure | Required-real | FX-TIME-007, FX-INTEGRATED-001 | C02,C09 | adjacent measures with different token counts preserve absolute order |
| F011 | Don / Ka | Required | FX-CORE-001 | C01 | note type, lane, judgement, score update |
| F012 | Big Don / Big Ka | Required-real | FX-CORE-002 | C01 | note type, big flag, score multiplier/logging |
| F013 | Big note dual-hand acceptance | Required | FX-CORE-002 | C01 | left/right paired input is accepted in configured model |
| F014 | Normal roll | Required-real | FX-ROLL-001, FX-INTEGRATED-001 | C04,C06 | roll body active between start/end; hits counted |
| F015 | Big roll | Required-real | FX-ROLL-001 | C04 | big roll type parsed and logged |
| F016 | Balloon | Required-real | FX-ROLL-002 | C04,C07 | BALLOON header maps required count to balloon event |
| F017 | Branch-specific balloon arrays | Required-real | FX-ROLL-003 | C04,C06 | BALLOONNOR/EXP/MAS select correct counts per branch |
| F018 | BalloonEx / kusudama / potato-equivalent | Required-real | FX-ROLL-004 | C04 | type 9 parsed; not downgraded to normal roll |
| F019 | Roll end token 8 | Required | FX-ROLL-001, FX-ROLL-002, FX-ROLL-003, FX-ROLL-004 | C04 | end event links to matching roll/balloon start |
| F020 | GOGOSTART / GOGOEND | Required-real | FX-CORE-003, FX-INTEGRATED-001 | C02,C09 | gogo state changes; score/log marks gogo state |
| F021 | BARLINE default measure line | Required | FX-CORE-001 | C01 | generated barline events have expected measure index |
| F022 | BARLINEON/OFF | Required-real | FX-CORE-004 | C02 | visibility state affects subsequent generated barlines |
| F023 | #BARLINE explicit command | Required | FX-CORE-004 | C01 | explicit barline event appears at command position |
| F024 | SECTION | Required-real | FX-BRANCH-001, FX-INTEGRATED-001 | C06 | branch counters reset at SECTION |
| F025 | BRANCHSTART parser | Required-real | FX-BRANCH-001, FX-INTEGRATED-001 | C05,C06 | condition type/range/thresholds parsed |
| F026 | N/E/M branch bodies | Required-real | FX-BRANCH-002 | C05,C06 | branch-specific notes are loaded per route |
| F027 | BRANCHEND merge | Required-real | FX-BRANCH-002 | C05,C09 | route merges into common section without duplicate notes |
| F028 | LEVELHOLD | Required-real | FX-BRANCH-003 | C06 | branch route remains locked after level-hold point |
| F029 | Accuracy branch condition p/pp | Required-real | FX-BRANCH-001, FX-BRANCH-004 | C05 | branch decision uses judgement counters |
| F030 | Judge-count branch condition jp/jg/jb | Required | FX-BRANCH-005 | C05 | perfect/good/bad counters available to evaluator |
| F031 | Roll branch condition r/rb | Required-real | FX-BRANCH-006 | C06 | roll/balloon hit counts feed branch decision |
| F032 | Score branch condition s | Required-real | FX-BRANCH-006 | C06 | score at branch point feeds route decision |
| F033 | SCROLL positive | Required-real | FX-SCROLL-001, FX-INTEGRATED-001 | C07 | visual offset uses scroll multiplier |
| F034 | SCROLL negative | Required-real | FX-SCROLL-001 | C07 | reverse/overtake visual position is logged and non-crashing |
| F035 | SCROLL zero | Required-real | FX-SCROLL-001 | C07 | stationary note visual path is logged; gameplay timing unaffected |
| F036 | SCROLL high speed | Required-real | FX-SCROLL-001, FX-INTEGRATED-002 | C07,C10 | large scroll values do not overflow/anomaly |
| F037 | Complex SCROLL x+yi | Required-real | FX-SCROLL-002 | C07,C09 | x/y scroll parsed; y component logged |
| F038 | NMSCROLL | Required-real | FX-SCROLL-003 | C07 | scroll mode normal selected |
| F039 | BMSCROLL | Required-real | FX-SCROLL-003 | C08 | visual position uses beat-scroll mode |
| F040 | HBSCROLL | Required-real | FX-SCROLL-003 | C08 | visual position uses hybrid beat-scroll mode |
| F041 | SUDDEN | Parse/report | FX-SCROLL-004 | C08 | parsed to compatibility event or reported non-fatal |
| F042 | DIRECTION | Parse/report | FX-SCROLL-004 | C08 | parsed to compatibility event or reported non-fatal |
| F043 | JPOSSCROLL | Parse/report | FX-SCROLL-004 | C08 | parsed/logged; exact lane animation may remain non-core |
| F044 | SCOREMODE | Required | FX-CORE-003, FX-SCORE-001 | C01,C06 | score mode selected and reported |
| F045 | SCOREINIT / SCOREDIFF | Required-real | FX-CORE-003, FX-SCORE-001 | C01,C06 | base/additive score values parsed and used by model |
| F046 | Gauge update and clear judgement | Required-real | FX-SCORE-002, FX-INTEGRATED-002 | all | gauge changes per judgement; clear threshold report emitted |
| F047 | Mine / ADLIB / special note parse | Parse/report | FX-CORE-005 | optional | parse without crash; log classification |
| F048 | Dan/NEXTSONG | Non-scope/report | FX-COMPAT-001 | none | explicit non-scope report; no silent acceptance as Phase1 pass |
| F049 | BGA/camera/object/lyrics | Non-scope/report | FX-COMPAT-002 | optional | explicit report; no crash |

## 4. Minimum gate

`GATE-0010-coverage-ready` passes only when:

- every Required and Required-real feature has at least one synthetic fixture;
- every Required-real feature maps to one or more user-selected song categories;
- every Parse/report feature has a fixture proving non-fatal handling;
- every Non-scope/report feature has a report path;
- timing log schema includes all assertion fields used by the matrix.
