# 12_opentaiko_phase1_research_questions: Phase1向けOpenTaiko調査質問

作成日: 2026-06-25
Status: adopted
入力: `docs/11_opentaiko_feature_taxonomy.md`, `docs/24_phase1_normal_play_compatibility_contract.md`

## 1. 目的

この文書は、OpenTaiko researchの仕様抽出SessionがOpenTaiko実装から回答すべき質問を定義する。回答は `research/opentaiko/` に保存し、`docs/25_phase1_feature_classification.md` の分類を確定させる。

## 2. 回答形式

各質問への回答は、次の形式で保存する。

```markdown
## <QID>: <質問タイトル>

- 優先度:
- 対象ファイル:
- 調査した関数/変数:
- 観測事実:
- Rust版Phase1への反映:
- 分類:
  - Must implement gameplay / Must parse / must not crash / Explicit non-scope with report
- 未対応時のreport挙動:
- 未解決:
- 参照:
```

参照には、commit、ファイルパス、行番号または検索語を残す。

## 3. 優先度

| 優先度 | 意味 | OpenTaiko researchでの扱い |
|---|---|---|
| P0 | Compatibility Contract確定に必須 | OpenTaiko research完了前に回答必須 |
| P1 | 設計・ticket化に必須 | coverage design開始前に回答必須 |
| P2 | 互換report精度向上に必要 | 実装ticket前に回答 |

## 4. `.tja` metadata / COURSE / audio質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| TJA-001 | P0 | Phase1で読むheader一覧は何か。TITLE, SUBTITLE, BPM, WAVE, PATH_WAV, OFFSET, COURSE, LEVEL, BALLOON, SCOREINIT, SCOREDIFF, SCOREMODEを確認する | `CTja.cs` |
| TJA-002 | P0 | 複数COURSEを含む `.tja` で、対象COURSEはどう抽出されるか | `CTja.cs`, song selection周辺 |
| TJA-003 | P0 | `#START` と `#END` はCOURSEごとにどう扱われるか | `CTja.cs` |
| TJA-004 | P0 | 譜面行はどの条件でnote token列になるか。空白、コメント、命令、カンマを確認する | `CTja.cs`, `NotesManager.cs` |
| TJA-005 | P0 | WAVE/PATH_WAVのpath解決と音声開始時刻はどこで決まるか | `CTja.cs`, SoundManager周辺 |
| TJA-006 | P1 | 未知header、未知command、未知note文字の扱いは何か | `CTja.cs`, logging周辺 |
| TJA-007 | P1 | BALLON/BALLOON typo等の互換表記は存在するか | `CTja.cs` |

## 5. note type / roll / balloon質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| NOTE-001 | P0 | NotesManagerのnote char mappingを完全に列挙する。0〜9, A, B, C, D, F, G, H, Iを確認する | `NotesManager.cs` |
| NOTE-002 | P0 | Don/Ka/大Don/大Kaは内部でどのchannelまたはenumへ写像されるか | `NotesManager.cs`, `CChip.cs` |
| NOTE-003 | P0 | 通常連打、大連打、EndRollの開始・終了はどう表現されるか | `NotesManager.cs`, `CTja.cs`, gameplay stage |
| NOTE-004 | P0 | Balloonのrequired hitsはBALLOON headerとどう対応するか | `CTja.cs`, `CChip.cs` |
| NOTE-005 | P0 | BalloonEx / くすだま相当の9は通常プレイでどう処理されるか | `NotesManager.cs`, gameplay stage |
| NOTE-006 | P1 | Bomb, BalloonFuze, ADLIB, Kadon, RollClap, RollPaはpanicなしに扱う最小情報として何を持つべきか | `NotesManager.cs` |
| NOTE-007 | P1 | big note判定に左右同種入力が必要か、autoplayではどう入力されるか | input/judgement周辺 |

## 6. timing / scheduler質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| TIM-001 | P0 | 1小節内のnote token数から発声時刻を決める計算式は何か | `CTja.cs` |
| TIM-002 | P0 | OpenTaikoの小節解像度、beat位置、ms位置の関係は何か | `CTja.cs`, `CChip.cs` |
| TIM-003 | P0 | BPMCHANGEはどの時点から反映されるか | `CTja.cs` |
| TIM-004 | P0 | MEASUREは発声時刻へどう反映されるか | `CTja.cs` |
| TIM-005 | P0 | DELAYはchart time上でどのように加算されるか | `CTja.cs` |
| TIM-006 | P0 | OFFSETの符号と適用順序は何か | `CTja.cs`, gameplay start |
| TIM-007 | P1 | 4/8/12/16/24/36分、32/48相当、混合n分を同じschedulerで扱える根拠は何か | `CTja.cs` |
| TIM-008 | P1 | 小節線chipまたはbarline eventは発声時刻とどう関連するか | `CTja.cs`, `CChip.cs` |

## 7. scroll / visual timing質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| SCR-001 | P0 | SCROLL値は発声時刻を変えるか、表示位置だけを変えるか | `NotesManager.cs`, `CChip.cs` |
| SCR-002 | P0 | 正SCROLL、負SCROLL、0 SCROLL、高速SCROLLはOpenTaikoでどのように扱われるか | `CTja.cs`, `NotesManager.cs` |
| SCR-003 | P0 | 追い越しはどの状態の組み合わせで発生するか | `NotesManager.cs`, gameplay draw周辺 |
| SCR-004 | P0 | NMSCROLL/BMSCROLL/HBSCROLLの計算差分は何か | `NotesManager.cs` |
| SCR-005 | P1 | 複素SCROLLはparserでどの型・式として扱われるか | `CTja.cs` |
| SCR-006 | P1 | SUDDEN, DIRECTION, JPOSSCROLLは通常プレイ完走へどの程度影響するか | `CTja.cs`, draw周辺 |

## 8. branch質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| BR-001 | P0 | BRANCHSTARTの条件型と引数形式は何か | `CTja.cs` |
| BR-002 | P0 | N/E/M譜面は内部でどう保持され、どのrouteが選択されるか | `CTja.cs`, `CChip.cs` |
| BR-003 | P0 | SECTIONは分岐評価区間をどう区切るか | `CTja.cs`, gameplay stage |
| BR-004 | P0 | LEVELHOLDはroute遷移へどう影響するか | `CTja.cs`, gameplay stage |
| BR-005 | P0 | BRANCHEND後のroute合流はどう行われるか | `CTja.cs` |
| BR-006 | P0 | 精度条件 p/pp 系は良/可/不可からどう計算されるか | gameplay stage |
| BR-007 | P0 | 連打条件、風船条件、score条件の参照値は何か | gameplay stage |
| BR-008 | P1 | 分岐別BALLOON配列、分岐別score stateの扱いは何か | `CTja.cs`, gameplay stage |

## 9. score / gauge / clear質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| SCG-001 | P0 | SCOREINIT, SCOREDIFF, SCOREMODEはどう読み込まれるか | `CTja.cs`, score関連 |
| SCG-002 | P0 | 通常ノーツ、大音符、roll、balloon、BalloonExの配点はどこで決まるか | gameplay score関連 |
| SCG-003 | P0 | GOGO stateはscoreへどう影響するか | gameplay score関連 |
| SCG-004 | P0 | コンボ加算、切断、最大コンボはどの条件で更新されるか | gameplay stage |
| SCG-005 | P0 | ゲージ増減とclear thresholdはどこで決まるか | gauge関連 |
| SCG-006 | P1 | 分岐route別score/gaugeの同期に必要な状態は何か | branch + score関連 |

## 10. headless / log / report質問

| QID | 優先 | 質問 | 主対象 |
|---|---:|---|---|
| LOG-001 | P0 | headless autoplayが理論入力を生成するために必要なchip情報は何か | autoplay処理, `CChip.cs` |
| LOG-002 | P0 | timing logにbranch route、scroll mode、gogo、barline、score/gaugeを出す最小schemaは何か | Rust版独自設計 |
| LOG-003 | P0 | Must parse / must not crash項目のcompatibility reportに必要なfieldは何か | Rust版独自設計 |
| LOG-004 | P1 | user-selected song validation reportに必要なsummary fieldは何か | Rust版独自設計 |

## 11. OpenTaiko research成果物への割当

| 成果物 | 回答する質問群 |
|---|---|
| `research/opentaiko/01_source_map.md` | 全質問の参照map |
| `research/opentaiko/02_tja_parser_commands.md` | TJA-001〜007 |
| `research/opentaiko/03_note_type_mapping.md` | NOTE-001〜007 |
| `research/opentaiko/04_timing_and_measure_model.md` | TIM-001〜008 |
| `research/opentaiko/05_roll_balloon_balloonex.md` | NOTE-003〜006, SCG-002 |
| `research/opentaiko/06_branching_model.md` | BR-001〜008 |
| `research/opentaiko/07_scroll_and_visual_timing.md` | SCR-001〜006 |
| `research/opentaiko/08_score_gauge_clear_model.md` | SCG-001〜006 |
| `research/opentaiko/09_course_audio_song_selection.md` | TJA-002, TJA-005 |
| `research/opentaiko/10_phase1_adoption_decisions.md` | 全質問の最終分類 |
