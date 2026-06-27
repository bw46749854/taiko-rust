# 11_opentaiko_feature_taxonomy: OpenTaiko Phase1機能分類

作成日: 2026-06-25  
状態: Step1改訂・Compatibility Contract対応  
入力: `research/opentaiko/10_phase1_adoption_decisions.md`, `docs/24_phase1_normal_play_compatibility_contract.md`

## 1. 目的

この文書は、OpenTaikoで通常プレイ中に遭遇する譜面要素を、Rust版Phase1でどの深度まで扱うかを分類するための正本である。

Phase1の「任意の曲」は、単一の簡単な `.tja` が起動することではない。OpenTaikoが通常プレイで対応している範囲の譜面要素を含む曲を、1P通常プレイとして最後まで進行し、結果を生成し、headless autoplayとtiming log analyzerで検証できる状態を指す。

## 2. 分類ラベル

Phase1では、全機能を同じ優先度で実装しない。分類は次の3段階で固定する。

| ラベル | 意味 | Phase1での扱い |
|---|---|---|
| Must implement gameplay | 通常プレイ完走、判定、スコア、ゲージ、表示、headless検証に必要 | 実装・自動テスト・fixture・timing log対象 |
| Must parse / must not crash | OpenTaiko譜面に現れるが、Phase1通常プレイ中核の完全再現対象ではない | parseし、互換reportまたはwarningを出し、panicしない |
| Explicit non-scope with report | 通常プレイ完走の中核外、Phase2以降、または権利・目的外 | 明示reportを出し、実装Sessionが勝手に実装しない |

旧分類の `Research` は、Step1以降は独立ラベルとして使わない。OpenTaiko調査が未完の項目は、一時的に `Must parse / must not crash` へ置き、Step2の採用判断で確定させる。

## 3. Phase1機能分類表

| ID | 機能 | 分類 | Phase1の採用範囲 | 検証要求 |
|---|---|---|---|---|
| F-001 | 1P通常プレイ | Must implement gameplay | 曲開始、譜面進行、曲終了、リザルト生成 | runtime smoke, headless autoplay |
| F-002 | `.tja` metadata | Must implement gameplay | TITLE, SUBTITLE, BPM, WAVE, OFFSET, COURSE, LEVEL | parser unit, fixture |
| F-003 | 複数COURSE選択 | Must implement gameplay | `.tja` 内の指定COURSEを選択して読み込む | multi-course fixture |
| F-004 | WAVE / PATH_WAV | Must implement gameplay | 音源path解決、音声開始時刻記録 | audio smoke, log analyzer |
| F-005 | OFFSET正負 | Must implement gameplay | chart/audio同期補正として扱う | offset fixture |
| F-006 | `#START` / `#END` | Must implement gameplay | 対象COURSEの譜面区間抽出 | parser unit |
| F-007 | 任意分割note scheduler | Must implement gameplay | 1小節内の任意個数tokenをMEASURE/BPMに従い配置 | scheduler unit, dense fixture |
| F-008 | 4/8/12/16/24/36分 | Must implement gameplay | 任意分割schedulerの代表ケースとして検証 | fixture coverage |
| F-009 | 32/48相当・混合n分 | Must implement gameplay | 個別caseではなく任意分割として配置 | high-density fixture |
| F-010 | `#MEASURE` | Must implement gameplay | 小節長をschedulerへ反映 | timing fixture |
| F-011 | `#BPMCHANGE` | Must implement gameplay | timelineへ反映 | timing fixture |
| F-012 | `#DELAY` | Must implement gameplay | chart time上の待機として反映 | timing fixture |
| F-013 | `#SCROLL` 正値 | Must implement gameplay | 表示速度・表示位置計算へ反映 | scroll fixture |
| F-014 | `#SCROLL` 負値 | Must implement gameplay | 逆方向または追い越し表示として扱う | scroll fixture |
| F-015 | `#SCROLL` 0 | Must implement gameplay | 停止表示として扱い、判定時刻は維持 | scroll fixture |
| F-016 | `#SCROLL` 高速 | Must implement gameplay | 高速表示と追い越しを検証 | scroll fixture |
| F-017 | 複素SCROLL | Must parse / must not crash | parserで認識し、Step2で数値表現を確定 | compatibility report |
| F-018 | NMSCROLL | Must implement gameplay | normal scroll modeとして扱う | scroll mode fixture |
| F-019 | BMSCROLL | Must implement gameplay | beat-based表示位置計算を実装対象に含める | scroll mode fixture |
| F-020 | HBSCROLL | Must implement gameplay | hybrid/beat-based表示互換を実装対象に含める | scroll mode fixture |
| F-021 | SUDDEN | Must parse / must not crash | 表示互換commandとしてparse/report対象 | parser/report test |
| F-022 | DIRECTION | Must parse / must not crash | 表示互換commandとしてparse/report対象 | parser/report test |
| F-023 | JPOSSCROLL | Must parse / must not crash | 判定ライン移動系としてparse/report対象 | parser/report test |
| F-024 | Don/Ka | Must implement gameplay | 1/2を通常ノーツとして判定 | judgement fixture |
| F-025 | 大Don/大Ka | Must implement gameplay | 3/4をbig noteとして判定 | big note fixture |
| F-026 | 通常連打 | Must implement gameplay | 5〜8のroll区間、打数加算 | roll fixture |
| F-027 | 大連打 | Must implement gameplay | 6〜8のbig roll区間、打数加算 | roll fixture |
| F-028 | 風船連打 | Must implement gameplay | 7〜8、BALLOON配列、成功/失敗 | balloon fixture |
| F-029 | BalloonEx / くすだま相当 | Must implement gameplay | 9を通常プレイ中のballoon系として扱う | balloonex fixture |
| F-030 | BALLOON header | Must implement gameplay | 風船必要打数配列として扱う | parser + balloon fixture |
| F-031 | 分岐別BALLOON配列 | Must implement gameplay | N/E/M route別balloon countを扱う | branch balloon fixture |
| F-032 | GOGOSTART/GOGOEND | Must implement gameplay | gogo stateをscore/log/renderへ反映 | gogo fixture |
| F-033 | BARLINEON/OFF | Must implement gameplay | 小節線表示状態を保持 | barline fixture |
| F-034 | SECTION | Must implement gameplay | 分岐評価区間の起点として扱う | branch fixture |
| F-035 | BRANCHSTART | Must implement gameplay | 分岐条件とN/E/M routeを保持 | branch fixture |
| F-036 | N/E/M | Must implement gameplay | 普通/玄人/達人routeとしてparse・実行 | branch fixture |
| F-037 | LEVELHOLD | Must implement gameplay | route維持として扱う | branch fixture |
| F-038 | BRANCHEND | Must implement gameplay | 分岐区間終端として扱う | branch fixture |
| F-039 | 精度分岐 | Must implement gameplay | 良/可/不可比率に基づくroute選択 | branch evaluator test |
| F-040 | 連打分岐 | Must implement gameplay | roll hit数に基づくroute選択 | branch evaluator test |
| F-041 | 風船分岐 | Must implement gameplay | balloon成功/打数に基づくroute選択 | branch evaluator test |
| F-042 | score分岐 | Must implement gameplay | scoreに基づくroute選択 | branch evaluator test |
| F-043 | SCOREINIT | Must implement gameplay | score configとして保持 | score unit |
| F-044 | SCOREDIFF | Must implement gameplay | score configとして保持 | score unit |
| F-045 | SCOREMODE | Must implement gameplay | Phase1 score modelの入力として保持 | score unit |
| F-046 | 配点 | Must implement gameplay | 通常ノーツ、roll、balloon、gogoを計算 | golden summary |
| F-047 | ゲージ | Must implement gameplay | 増減、clamp、clear threshold | gauge unit |
| F-048 | クリア判定 | Must implement gameplay | resultにclear/failを出す | result fixture |
| F-049 | 判定 | Must implement gameplay | 良/可/不可相当、early/late、miss | judgement fixture |
| F-050 | headless autoplay | Must implement gameplay | 通常ノーツ、roll、balloon、branch検証用入力生成 | analyzer |
| F-051 | timing log | Must implement gameplay | schedule/input/judge/scroll/branch/score/gaugeを記録 | schema test |
| F-052 | timing log analyzer | Must implement gameplay | synthetic/user songの合否判定 | analyzer test |
| F-053 | 描画あり通常プレイ | Must implement gameplay | 最小レーン、ノーツ、HUD、リザルト | visual smoke |
| F-054 | Mine | Must parse / must not crash | 通常プレイ中核外。parse/report対象 | compatibility report |
| F-055 | ADLIB | Must parse / must not crash | 通常プレイ中核外。parse/report対象 | compatibility report |
| F-056 | Bomb/Fuse/Kadon/Swap | Must parse / must not crash | OpenTaiko譜面出現時にpanicしない | compatibility report |
| F-057 | A/B 2P joint note | Must parse / must not crash | 1P通常プレイ外。parse/report対象 | compatibility report |
| F-058 | Konga系H/I | Must parse / must not crash | Taiko通常プレイ外。parse/report対象 | compatibility report |
| F-059 | 多人数プレイ | Explicit non-scope with report | 2P以上、対戦、同時プレイ | non-scope report |
| F-060 | 段位 | Explicit non-scope with report | Dan course、複数曲連結、exam条件 | non-scope report |
| F-061 | Tower / AI Battle | Explicit non-scope with report | 通常プレイ外モード | non-scope report |
| F-062 | BGA / lyrics / camera / object | Explicit non-scope with report | 演出・背景・歌詞・カメラ | non-scope report |
| F-063 | スキン完全互換 | Explicit non-scope with report | OpenTaiko skin座標・演出完全再現 | non-scope report |
| F-064 | プレイオプション | Explicit non-scope with report | Reverse, Random, Hidden, Speed option等 | Phase2 backlog |
| F-065 | 商用再現・権利不明アセット | Explicit non-scope with report | 商用UI/演出/資産の正確な複製、無断同梱 | implementation禁止 |

## 4. Phase1中核集合

Phase1の中核は次で固定する。

1. `.tja` metadata / COURSE / audio path parser
2. 任意分割note scheduler
3. BPM / MEASURE / DELAY / OFFSET timeline
4. Don / Ka / 大Don / 大Ka
5. 通常連打 / 大連打 / 風船 / BalloonEx
6. GOGO / BARLINE display state
7. N/E/M譜面分岐と分岐条件評価
8. SCROLL / NMSCROLL / BMSCROLL / HBSCROLL
9. score / combo / gauge / clear
10. 1P input / judgement
11. minimal rendering
12. headless autoplay
13. timing log / analyzer
14. synthetic fixtures and user-selected song validation

## 5. Phase2へ送る機能集合

Phase2では、通常プレイ成立後にプレイオプションを組み合わせて変更できる状態を扱う。

- Reverse
- Random系
- プレイヤー指定のscroll speed option
- Hidden / Doron / Stealth系
- 判定補正UI
- 音量設定UI
- gameplay中のAuto切替
- 表示オプション

## 6. Phase3以降へ送る機能集合

- 多人数プレイ
- AI Battle
- 段位
- Tower
- 高度な曲選択UI
- 高度なスキン/演出
- Lua拡張
- 動画/歌詞/背景演出
- Hub連携
- オンライン機能
- 配布パッケージ/ランチャー

## 7. 対象外に固定する項目

- 商用ゲームのUI、演出、挙動の正確な複製
- 商用ゲーム由来のアセット取り込み
- 権利不明の曲、譜面、画像、音源、フォントの同梱
- OpenTaiko外部アセットの無断再配布
- 既存C#コードの逐語的なRust移植

## 8. レビュー基準

設計レビューSessionは次を確認する。

- 分岐譜面、score/gauge、BalloonEx、BMSCROLL/HBSCROLLがPhase1から漏れていない。
- Must parse / must not crash項目がpanicを許容していない。
- Explicit non-scope with report項目が実装ticketへ混入していない。
- fixtureまたはuser-selected songで検証できないMust implement gameplay項目が残っていない。
