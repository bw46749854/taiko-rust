# 25_phase1_feature_classification: Phase1機能分類正本

作成日: 2026-06-25  
状態: Step1新規・採用候補  
入力: `research/opentaiko/10_phase1_adoption_decisions.md`, `docs/24_phase1_normal_play_compatibility_contract.md`

## 1. 目的

この文書は、Phase1対象機能を3分類で固定する正本である。実装Session、仕様抽出Session、設計レビューSession、QA/回帰検証Sessionは、この文書の分類を参照して作業範囲を判断する。

## 2. 分類定義

| 分類 | 実装義務 | 検証義務 |
|---|---|---|
| Must implement gameplay | parser、runtime、headless、analyzer、resultで実装 | synthetic fixture + relevant user-selected song |
| Must parse / must not crash | parser/reportで認識し、panic禁止 | compatibility report test |
| Explicit non-scope with report | 実装対象に入れない。検出時にreport | non-scope report test |

## 3. Must implement gameplay

| Category | Items |
|---|---|
| Metadata / course | TITLE, SUBTITLE, BPM, WAVE, PATH_WAV, OFFSET, COURSE, LEVEL, 複数COURSE選択 |
| Score headers | BALLOON, SCOREINIT, SCOREDIFF, SCOREMODE |
| Chart bounds | `#START`, `#END` |
| Scheduler | 任意分割note scheduler、4/8/12/16/24/36、32/48相当、混合n分 |
| Timing commands | `#BPMCHANGE`, `#MEASURE`, `#DELAY`, OFFSET正負 |
| Notes | 0, 1, 2, 3, 4 |
| Roll / balloon | 5, 6, 7, 8, 9, 通常連打、大連打、風船、BalloonEx |
| GOGO / barline | `#GOGOSTART`, `#GOGOEND`, `#BARLINEON`, `#BARLINEOFF` |
| Scroll | `#SCROLL` 正/負/0/高速、追い越し、NMSCROLL, BMSCROLL, HBSCROLL |
| Branch | `#SECTION`, `#BRANCHSTART`, `#N`, `#E`, `#M`, `#LEVELHOLD`, `#BRANCHEND` |
| Branch conditions | 精度、良/可/不可、連打、風船、score |
| Scoring | 通常ノーツ、大音符、roll、balloon、BalloonEx、GOGO、combo |
| Gauge | gauge増減、clamp、clear判定 |
| Runtime | 1P通常プレイ、BGM再生、audio time、result |
| Validation | headless autoplay、timing log、timing log analyzer、synthetic fixture、user-selected song validation |

## 4. Must parse / must not crash

| Category | Items | Report action |
|---|---|---|
| Extended notes | A, B, C, D, F, G, H, I | `compatibility_warning` |
| Display commands | SUDDEN, DIRECTION, JPOSSCROLL | `compatibility_warning` または `visual_partial_support` |
| Complex scroll | 複素SCROLL | `compatibility_warning`、Step2採用判断待ち |
| Metadata extras | 通常プレイへ不要なheader | `metadata_ignored` |
| OpenTaiko-specific extension | 通常プレイへ不要な独自拡張 | `compatibility_warning` |

Must parse / must not crash項目は、panicを許容しない。通常プレイ完走に影響するcommandが出現した際は、reportへ対象command、位置、分類、継続可否を出す。

## 5. Explicit non-scope with report

| Category | Items | Report action |
|---|---|---|
| Modes | Dan/段位、Tower、AI Battle、Training、Online/Heya | `explicit_non_scope` |
| Multiplayer | 2P以上、対戦、同時プレイ | `explicit_non_scope` |
| Game type | Konga等Taiko以外 | `explicit_non_scope` |
| Presentation | BGA、動画、lyrics、camera、object、Lua演出 | `explicit_non_scope` |
| Skin | OpenTaiko skin完全互換、外部skin system | `explicit_non_scope` |
| Options | Reverse、Random、Hidden、Doron、Stealth、player speed option | `phase2_deferred` |
| Distribution | 曲、音源、画像、フォント、商用/権利不明assetの同梱 | `blocked_by_policy` |
| Code migration | OpenTaiko C#コードの逐語移植 | `blocked_by_policy` |

## 6. Ticket作成時の必須記載

各ticketは次を本文に含める。

- 対象分類
- 対象feature IDまたはcategory
- Must implement gameplay項目のfixture要求
- Must parse / must not crash項目のreport要求
- Explicit non-scope混入なしの確認
- 参照するOpenTaiko調査成果物
- 受け入れ基準ID

## 7. 分類変更ルール

分類変更は実装Sessionが単独で行わない。変更には次が必要である。

1. `research/opentaiko/` の調査成果物更新
2. `docs/25_phase1_feature_classification.md` の更新
3. `docs/22_phase1_acceptance_criteria.md` の更新
4. coverage matrix更新
5. 設計レビューSessionの承認
6. QA/回帰検証Sessionの検証観点更新
