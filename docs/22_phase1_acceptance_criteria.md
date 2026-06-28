# 22_phase1_acceptance_criteria: Phase1受け入れ基準

作成日: 2026-06-25
Status: canonical
目的: Phase1の合格条件を、人間の目視判断ではなく機械判定可能な項目へ分解する。

## 1. 上位合格条件

Phase1は、次の全条件を満たしたときにPASSとする。

1. `docs/24_phase1_normal_play_compatibility_contract.md` のCompatibility Contractに違反していない。
2. `docs/25_phase1_feature_classification.md` のMust implement gameplay項目に対応している。
3. Must parse / must not crash項目でpanicせず、compatibility reportを生成する。
4. Explicit non-scope with report項目を実装scopeへ混入していない。
5. synthetic fixtures 25〜35譜面で仕様網羅を検証している。
6. user-selected real songs 標準10カテゴリで通常プレイ完走を検証している。
7. headless autoplay、timing log、timing log analyzer、result summaryがPASSしている。
8. QA/回帰検証Sessionが最終acceptance reportを作成している。

## 2. Command受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-CMD-001 | format | `cargo fmt --check` がPASS | command log |
| AC-CMD-002 | lint | `cargo clippy --all-targets --all-features -- -D warnings` がPASS | command log |
| AC-CMD-003 | unit/integration | `cargo test --all` がPASS | command log |
| AC-CMD-004 | all check | `cargo run --bin taiko_cli -- check all` がPASS | command log |
| AC-CMD-005 | synthetic fixture | 全synthetic fixtureがPASS | fixture report |
| AC-CMD-006 | user song validation | user-selected manifestの全曲がPASS | user song report |

## 3. Parser / metadata受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-TJA-001 | header | TITLE/SUBTITLE/BPM/WAVE/PATH_WAV/OFFSET/COURSE/LEVEL/BALLOON/SCOREINIT/SCOREDIFF/SCOREMODEをparse | parser tests |
| AC-TJA-002 | COURSE | 複数COURSEから指定COURSEを抽出 | multi-course fixture |
| AC-TJA-003 | START/END | 対象COURSEの `#START`〜`#END` を抽出 | parser tests |
| AC-TJA-004 | note line | 小節カンマ、空白、コメント、命令行を正しく区別 | parser tests |
| AC-TJA-005 | unknown handling | 未知header/command/noteでpanicしない | compatibility report test |
| AC-TJA-006 | report | parse warning、unsupported、non-scopeを区別 | report schema test |

## 4. Scheduler / timing受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-TIM-001 | 任意分割 | 1小節内の任意token数を正しいbeat/msへ配置 | scheduler unit |
| AC-TIM-002 | 4/8/12/16/24/36 | 代表分割がexpected timestampと一致 | synthetic fixtures |
| AC-TIM-003 | 混合n分 | 異なるn分が混在する譜面を正しく配置 | dense fixture |
| AC-TIM-004 | 32/48相当 | 高密度相当のtoken分割を処理 | high-density fixture |
| AC-TIM-005 | MEASURE | 変拍子でexpected timestampと一致 | timing fixture |
| AC-TIM-006 | BPMCHANGE | BPM変化後のtimestampが一致 | timing fixture |
| AC-TIM-007 | DELAY | delay後のtimestampが一致 | timing fixture |
| AC-TIM-008 | OFFSET | 正負OFFSETのchart/audio deltaが基準内 | analyzer |

## 5. Note / roll / balloon受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-NOTE-001 | Don/Ka | 1/2を正しく判定 | judgement fixture |
| AC-NOTE-002 | 大音符 | 3/4をbig noteとして扱う | big note fixture |
| AC-NOTE-003 | 通常連打 | 5〜8で打数加算 | roll fixture |
| AC-NOTE-004 | 大連打 | 6〜8でbig roll打数加算 | roll fixture |
| AC-NOTE-005 | 風船 | 7〜8でrequired hits、成功/失敗を出す | balloon fixture |
| AC-NOTE-006 | BalloonEx | 9をBalloonEx/くすだま相当として処理 | balloonex fixture |
| AC-NOTE-007 | BALLOON配列 | header配列と譜面上の風船が対応 | parser + fixture |
| AC-NOTE-008 | 分岐別BALLOON | N/E/M route別balloon countを扱う | branch balloon fixture |

## 6. Branch受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-BR-001 | command parse | SECTION/BRANCHSTART/N/E/M/LEVELHOLD/BRANCHENDをparse | branch parser test |
| AC-BR-002 | route model | N/E/M route別note streamを保持 | branch fixture |
| AC-BR-003 | 精度分岐 | 良/可/不可比率からrouteを選択 | evaluator test |
| AC-BR-004 | 連打分岐 | roll hit数からrouteを選択 | evaluator test |
| AC-BR-005 | 風船分岐 | balloon状態からrouteを選択 | evaluator test |
| AC-BR-006 | score分岐 | scoreからrouteを選択 | evaluator test |
| AC-BR-007 | LEVELHOLD | route維持が期待通り動作 | branch fixture |
| AC-BR-008 | branch coverage | synthetic fixtureでN/E/M各routeを通過 | coverage report |

## 7. Scroll / visual timing受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-SCR-001 | 正SCROLL | 表示位置計算がexpectedと一致 | scroll fixture |
| AC-SCR-002 | 負SCROLL | 逆方向/追い越し表示でpanicしない | scroll fixture |
| AC-SCR-003 | 0 SCROLL | 停止表示でも判定時刻が維持 | scroll fixture |
| AC-SCR-004 | 高速SCROLL | 高速/追い越しを検証 | scroll fixture |
| AC-SCR-005 | NMSCROLL | normal modeでexpected表示位置 | mode fixture |
| AC-SCR-006 | BMSCROLL | beat-based modeでexpected表示位置 | mode fixture |
| AC-SCR-007 | HBSCROLL | hybrid/beat-based modeでexpected表示位置 | mode fixture |
| AC-SCR-008 | parse/report | SUDDEN/DIRECTION/JPOSSCROLLでpanicしない | compatibility report |

## 8. Score / gauge / result受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-SCG-001 | SCOREINIT/SCOREDIFF/SCOREMODE | score configへ保存 | parser/score unit |
| AC-SCG-002 | note score | 通常ノーツ、大音符の加点がexpectedと一致 | score unit |
| AC-SCG-003 | roll score | roll/balloon/BalloonEx加点がexpectedと一致 | score unit |
| AC-SCG-004 | GOGO | gogo state中のscore/logがexpectedと一致 | gogo fixture |
| AC-SCG-005 | combo | hit/missによるcombo/max comboが一致 | judgement fixture |
| AC-SCG-006 | gauge | 増減、clamp、clear thresholdが一致 | gauge unit |
| AC-SCG-007 | result | JSON summaryに必須fieldがある | schema test |

## 9. Audio / runtime受け入れ基準

| ID | 基準 | 合格条件 | 証跡 |
|---|---|---|---|
| AC-AUD-001 | WAVE | 音源pathを解決できる | audio smoke |
| AC-AUD-002 | PATH_WAV | base pathを反映できる | audio smoke |
| AC-AUD-003 | start time | audio_started eventを出す | timing log |
| AC-AUD-004 | audio delta | chart/audio deltaが閾値内 | analyzer |
| AC-RUN-001 | runtime | 描画ありで曲開始、進行、終了、リザルト遷移 | visual smoke |
| AC-RUN-002 | panic-free | supported譜面でpanicなし | smoke report |

## 10. Synthetic fixture受け入れ基準

Synthetic fixtureはcoverage designで25〜35譜面として確定する。compatibility contract時点の必須カテゴリは次で固定する。

| ID | カテゴリ | 主検証 |
|---|---|---|
| AC-FIX-001 | 基本note | Don/Ka/大Don/大Ka |
| AC-FIX-002 | 任意分割 | 4/8/12/16/24/36/32/48相当 |
| AC-FIX-003 | 混合n分 | 異なるn分音符の混在 |
| AC-FIX-004 | timing | BPMCHANGE/MEASURE/DELAY/OFFSET |
| AC-FIX-005 | roll/balloon | 通常連打/大連打/風船/BalloonEx |
| AC-FIX-006 | branch | N/E/M、SECTION、LEVELHOLD、条件分岐 |
| AC-FIX-007 | scroll | 正/負/0/高速/追い越し/NM/BM/HB |
| AC-FIX-008 | gogo/barline | GOGO START/END、BARLINE ON/OFF |
| AC-FIX-009 | course/audio | 複数COURSE、WAVE/PATH_WAV |
| AC-FIX-010 | compatibility report | parse/report対象command/note |
| AC-FIX-011 | long stability | 長尺・高ノーツ数 |
| AC-FIX-012 | integrated | 複合ギミック |

## 11. User-selected song受け入れ基準

User-selected songsはcoverage designでmanifest schemaへ落とす。compatibility contract時点の標準10カテゴリは次で固定する。

| ID | カテゴリ | 主検証 |
|---|---|---|
| AC-USR-001 | 基本譜面 | Don/Ka/大音符/小節線/通常BPM |
| AC-USR-002 | 高密度譜面 | 16/24/36分と混合n分 |
| AC-USR-003 | 変拍子・BPM譜面 | BPMCHANGE/MEASURE/DELAY/OFFSET |
| AC-USR-004 | 連打譜面 | 通常連打/大連打/風船/BalloonEx |
| AC-USR-005 | 分岐譜面A | 精度条件 p/pp 系 |
| AC-USR-006 | 分岐譜面B | 連打/score/LEVELHOLD/SECTION 系 |
| AC-USR-007 | scroll譜面 | 低速/高速/負SCROLL/0 SCROLL/追い越し |
| AC-USR-008 | HB/BM/特殊表示譜面 | HBSCROLL/BMSCROLL/SUDDEN/DIRECTION/JPOSSCROLL |
| AC-USR-009 | 総合混合譜面 | BPM変化/scroll/連打/分岐の同時出現 |
| AC-USR-010 | 長尺・負荷譜面 | 長時間/高ノーツ数/複数ギミック |

合格条件:

- 全曲がparseできる。
- Must implement gameplay対象でpanicしない。
- headless autoplayで曲終了まで進行する。
- timing log analyzerがPASSまたは明示BLOCKED理由を出す。
- BLOCKEDはPhase1完了判定ではFAILとして扱い、修正ticketへ紐づける。

## 12. Final acceptance report

Phase1完了判定では、次のMarkdownを `reports/phase1_acceptance_report.md` として作る。

```markdown
# Phase1 Acceptance Report

- date:
- commit:
- branch:
- reviewer session:
- qa session:

## Command Results

| command | status | log |
|---|---|---|

## Synthetic Fixture Results

| fixture | category | headless | analyzer | digest |
|---|---|---|---|---|

## User-selected Song Results

| song id | category | course | headless | analyzer | digest |
|---|---|---|---|---|---|

## Coverage Summary

| feature | synthetic coverage | user song coverage | status |
|---|---|---|---|

## Compatibility Reports

| item | classification | action | status |
|---|---|---|---|

## Final Decision

- status: PASS / FAIL / BLOCKED
- decision owner: QA/回帰検証Session
```
