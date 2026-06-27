# 01_source_map: OpenTaiko参照箇所マップ

作成日: 2026-06-25  
状態: Step2正式採用  
上流文書: `docs/24_phase1_normal_play_compatibility_contract.md`, `docs/25_phase1_feature_classification.md`  
下流文書: `research/opentaiko/10_phase1_adoption_decisions.md`

## 1. 目的

この文書は、Phase1で参照するOpenTaiko実装箇所を固定する。Step2以降の仕様判断は、ここに列挙したsource mapを起点にする。

## 2. 採用する主要source

| ID | パス | 採用理由 | Phase1で読む観点 |
|---|---|---|---|
| SRC-CTJA | `OpenTaiko/src/Songs/CTja.cs` | TJA header、譜面body、command、branch、scroll、audio metadataの中心 | parser, scheduler, branch, scroll, course/audio |
| SRC-NOTES | `OpenTaiko/src/Stages/07.Game/Taiko/NotesManager.cs` | TJA note文字とnote種別、入力lane、scroll座標計算の中心 | note mapping, roll/balloon分類, scroll位置計算 |
| SRC-STAGE | `OpenTaiko/src/Stages/07.Game/CStage演奏画面共通.cs` | gameplay runtime、score/gauge、branch実行、autoplayの中心 | runtime loop, score/gauge, branch transition, autoplay |

## 3. 補助source候補

Step2では主要sourceだけで採用判断を固定する。Step3以降で実装ticketが詳細式を要求する箇所は、次を追加調査する。

| 候補 | 目的 | 調査タイミング |
|---|---|---|
| gauge actor / HGaugeMethods関連 | gauge増減量、clear/norma判定の詳細式 | score/gauge ticket開始前 |
| branch score / CBRANCHSCORE関連 | branch条件に使う良/可/不可、roll、score累積の詳細 | branch evaluator ticket開始前 |
| config timing zones関連 | judgement window、latency補正、auto判定window | judgement / headless autoplay ticket開始前 |
| audio backend関連 | WAVE再生開始、OFFSET、global offset、latency実測 | audio sync ticket開始前 |

## 4. 調査規則

- 仕様文書には、OpenTaiko実装箇所、観測結果、Rust版採用判断を分けて書く。
- OpenTaikoと同一の資産、商用曲、商用譜面はbundleへ含めない。
- 不明点は「推測で実装しない」。`10_phase1_adoption_decisions.md` の unresolved sectionへ残す。
- 採用しない機能も、parse/report方針を必ず定義する。

## 5. Step2での到達点

Step2では、Phase1を開始できる程度の仕様抽出を行った。式単位の完全移植はまだ行わない。式単位の検証は、TKTごとの実装前調査で実行する。
