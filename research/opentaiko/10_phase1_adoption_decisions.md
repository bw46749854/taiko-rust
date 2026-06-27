# 10_phase1_adoption_decisions: Phase1採用判断

作成日: 2026-06-25  
状態: Step2正式採用  
上流文書: `docs/24_phase1_normal_play_compatibility_contract.md`, `research/opentaiko/01_source_map.md`〜`09_course_audio_song_selection.md`

## 1. 最終判断

Step2では、OpenTaiko通常プレイ互換に必要な中核機能をPhase1へ採用する。Phase1は、parserだけでなくheadless autoplay、score/gauge、branch、scroll、audio offsetを含む通常play完走を目標にする。

## 2. Must implement gameplay

| 領域 | 採用項目 |
|---|---|
| note | Don, Ka, DonBig, KaBig, Roll, BigRoll, Balloon, BalloonEx, RollEnd |
| scheduler | 任意分割note scheduler、BPM、BPMCHANGE、MEASURE、DELAY、OFFSET |
| branch | SECTION, BRANCHSTART, N/E/M, LEVELHOLD, BRANCHEND, branch condition evaluator |
| scroll | SCROLL正/負/0/高速/複素、NMSCROLL、BMSCROLL、HBSCROLL |
| state | GOGOSTART/GOGOEND、BARLINE/BARLINEON/BARLINEOFF |
| score | SCOREMODE、SCOREINIT、SCOREDIFF、GOGO倍率、大音符bonus |
| gauge | GAUGEINCR、clear/norma判定、basic gauge update |
| roll/balloon | BALLOON、BALLOONNOR/EXP/MAS、required hits、roll hit count |
| course/audio | COURSE選択、WAVE、PATH_WAV、OFFSET正負 |

## 3. Must parse / must not crash

| 領域 | 採用項目 |
|---|---|
| note | A, B, C, D, F, G, H, I |
| visual | SUDDEN、DIRECTION、JPOSSCROLL |
| metadata | GAME/GAMETYPE、HEADSCROLL、HIDDENBRANCH、SONGVOL、LIFE、.FORCEGAUGE、.BOOMRULE |
| compatibility | unknown custom header beginning with `.` |

## 4. Explicit non-scope with report

| 領域 | 項目 |
|---|---|
| dan | NEXTSONG、EXAM*、段位認定固有処理 |
| media | BGA、AVI、movie、lyrics |
| camera/object | CAM*, OBJ*, ADDOBJECT, REMOVEOBJECT, CHANGETEXTURE, RESETTEXTURE |
| skin/config演出 | BORDERCOLOR, SETCONFIG, ENABLEDORON, DISABLEDORON |
| multiplayer/special | 2P固有処理、Konga完全互換、Tower専用clear/fail |

## 5. Rust moduleへの反映

| Module | 追加責務 |
|---|---|
| `taiko_chart` | metadata parser、body parser、command分類、course selection |
| `taiko_domain` | note/timing/branch/scroll/score/gaugeのpure model |
| `taiko_runtime` | gameplay state machine、branch transition、autoplay |
| `taiko_audio` | audio path resolution、offset、silent adapter |
| `taiko_headless` | deterministic autoplay、roll/balloon auto hits |
| `taiko_analyzer` | timing log、branch coverage、scroll anomaly、score/gauge validation |
| `taiko_cli` | check、fixture、user-song validate入口 |

## 6. Ticketへ渡す未解決事項

| ID | 未解決事項 | 担当ticket |
|---|---|---|
| U-001 | branch judge chip timeの完全式 | TKT-0008/TKT-0009 |
| U-002 | gauge増減量とforce gauge詳細式 | TKT-0011 |
| U-003 | score mode 1/2/legacyの完全式 | TKT-0011 |
| U-004 | SUDDEN/DIRECTION/JPOSSCROLLの描画完全再現 | TKT-0012/TKT-0013 |
| U-005 | audio backendのlatency実測 | TKT-0010以降 |
| U-006 | Bomb/Adlib/Kadon等の通常play内扱い | Step3 fixture分類で最終化 |

## 7. Step2完了条件の判定

- OpenTaiko主要source mapを作成済み。
- TJA command分類を作成済み。
- note type mappingを作成済み。
- timing、roll/balloon、branch、scroll、score/gauge、course/audioの採用判断を作成済み。
- Architecture系文書へStep2 amendmentを反映する。

Step2は完了と判定する。Step3では、ここで固定した採用判断をcoverage matrixとfixture設計へ接続する。
