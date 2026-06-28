# 27_phase1_open_taiko_compatibility_boundary: OpenTaiko互換境界

作成日: 2026-06-25
Status: adopted

## 1. 目的

この文書は、Rust版Phase1がOpenTaikoの何を参考にし、何を再現しないかを固定する。

Phase1では、OpenTaikoの通常プレイ譜面対応範囲を仕様抽出の情報源として扱う。OpenTaikoのUI、演出、アセット、全モード、C#構造の完全互換は目的ではない。

## 2. 参考にするもの

- `.tja` metadataの読み方
- COURSE選択
- note char mapping
- BPMCHANGE / MEASURE / DELAY / OFFSET
- SCROLL / NMSCROLL / BMSCROLL / HBSCROLL
- GOGO / BARLINE
- roll / balloon / BalloonEx
- branch commandとroute選択
- score / gauge / clearに必要な通常プレイ状態
- audio pathと音声開始時刻の扱い

## 3. 再現しないもの

- OpenTaikoのC#コード構造
- OpenTaikoのclass名、method名、状態名の逐語移植
- OpenTaikoのskin座標、texture、演出、描画順の完全再現
- OpenTaiko Hub連携
- Dan、Tower、AI Battle、Online等の通常プレイ外モード
- 商用ゲームのUI/演出/挙動の正確な複製
- 商用または権利不明アセットの同梱

## 4. 互換判断の優先順

1. Phase1 Compatibility Contract
2. OpenTaiko実装調査成果物
3. Rust版の検証可能性
4. 権利・配布・安全性
5. 実装容易性

実装容易性は最上位判断ではない。通常プレイ完走に必要なOpenTaiko対応譜面要素は、Phase1対象として扱う。

## 5. Compatibility report方針

Must parse / must not crash項目、Explicit non-scope項目を検出した場合、次の情報をreportする。

- file path
- course
- measure index
- line number
- command or note token
- classification
- action
- continued / blocked
- reason
- related ticket or backlog id

## 6. OpenTaiko research調査の境界

OpenTaiko researchでは、OpenTaiko実装から通常プレイ互換に必要な挙動を抽出する。抽出結果はRustへ直接翻訳するのではなく、Rust版のdomain model、testability、headless検証に合わせて採用判断する。

OpenTaiko researchで作成する調査成果物:

- `research/opentaiko/01_source_map.md`
- `research/opentaiko/02_tja_parser_commands.md`
- `research/opentaiko/03_note_type_mapping.md`
- `research/opentaiko/04_timing_and_measure_model.md`
- `research/opentaiko/05_roll_balloon_balloonex.md`
- `research/opentaiko/06_branching_model.md`
- `research/opentaiko/07_scroll_and_visual_timing.md`
- `research/opentaiko/08_score_gauge_clear_model.md`
- `research/opentaiko/09_course_audio_song_selection.md`
- `research/opentaiko/10_phase1_adoption_decisions.md`
