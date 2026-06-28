# 01_preparation_workplan: Codex作業開始準備計画

作成日: 2026-06-25
Status: adopted

## 1. 準備計画のゴール

この準備計画のゴールは、CodexへPhase1実装開始を指示しても、設計不備、検証不備、Session混線による大きな手戻りが起きない状態を作ることである。

実装開始前に、Codexが読むべき仕様、設計、検証仕様、Session運用、チケット形式、レビュー基準を揃える。Phase1本体実装は、準備完了判定を通過してから開始する。

## 2. 全体分割

準備作業は9回で完了させる。

| 回 | 名称 | 主成果物 | 完了判定 |
|---:|---|---|---|
| 1 | 作業計画・成果物構成の確定 | `docs/00`〜`docs/03` | 準備全体の文書体系とDefinition of Readyが固定されている |
| 2 | OpenTaiko調査設計 | `docs/10`〜`docs/12`, `prompts/10_spec_extraction_session.md` | 仕様抽出Sessionが調査を開始できる |
| 3 | Phase1スコープ定義 | `docs/20`〜`docs/23` | Phase1の対象・非対象・合格条件が明文化されている |
| 4 | Rustアーキテクチャ方針 | `docs/30`〜`docs/34` | module境界とruntime data flowが固定されている |
| 5 | Timing / Audio / Judgement検証設計 | `docs/40`〜`docs/44` | 時刻、音声同期、判定、ログ、analyzerの仕様が固定されている |
| 6 | テストハーネス・回帰検証設計 | `docs/50`〜`docs/54` | fixture、golden log、CIコマンドが固定されている |
| 7 | Session分離・worktree・PR運用 | `docs/60`〜`docs/64` | 自己承認を避ける運用導線が固定されている |
| 8 | Codex用プロンプト・テンプレート整備 | `AGENTS.md`, `prompts/*`, `templates/*` | 各Sessionをそのまま起動できる |
| 9 | Codex作業開始パッケージ | `docs/90`〜`docs/93`, `scripts/*` | 初回Codex投入手順と初回バックログが揃っている |

## 3. 準備計画: 作業計画・成果物構成の確定

### 3.1 目的

以後の作業範囲、文書体系、準備完了判定を固定する。

### 3.2 成果物

- `docs/00_project_goal.md`
- `docs/01_preparation_workplan.md`
- `docs/02_document_index.md`
- `docs/03_definition_of_ready.md`

### 3.3 決定事項

- Phase1実装開始前に必須となる文書群
- 各文書の責務
- 準備完了判定
- OpenTaiko調査設計以降の作業順序

### 3.4 準備計画では扱わない内容

- OpenTaiko内部コードの詳細解析
- `.tja`仕様の詳細化
- Rust crate構成の詳細化
- timing log schemaのフィールド確定
- 実装チケットの作成

## 4. OpenTaiko調査設計: OpenTaiko調査設計

### 4.1 目的

OpenTaikoから何を調べ、何を参考仕様にし、何をPhase1対象外へ送るかを固定する。

### 4.2 成果物

- `docs/10_opentaiko_research_plan.md`
- `docs/11_opentaiko_feature_taxonomy.md`
- `docs/12_opentaiko_phase1_research_questions.md`
- `prompts/10_spec_extraction_session.md`

### 4.3 調査観点

- 曲選択からリザルトまでの通常プレイ導線
- `.tja`読み込み
- BPM、OFFSET、SCROLL、分岐、ノーツ種別
- audio timeとgame timeの関係
- 入力正規化と判定処理
- スコア、コンボ、ゲージ
- 描画更新とフレーム依存処理
- 設定、ログ、エラー処理
- Rust版で検証可能に再設計する対象

## 5. Phase1スコープ定義: Phase1スコープ・非スコープ・受け入れ基準

### 5.1 目的

CodexがPhase1対象を誤解しないように、実装対象、対象外、合格条件を固定する。

### 5.2 成果物

- `docs/20_phase1_scope.md`
- `docs/21_phase1_non_scope.md`
- `docs/22_phase1_acceptance_criteria.md`
- `docs/23_phase1_definition_of_done.md`

### 5.3 固定する内容

- 通常プレイの最小完備範囲
- 対応譜面要素の初期範囲
- audio syncとjudgementの合格条件
- headless autoplayで必須の検証
- リザルトまでの完走条件
- Phase2以降へ送る機能

## 6. Rustアーキテクチャ方針: Rust版アーキテクチャ方針

### 6.1 目的

場当たり的な実装を避け、Rust workspace、crate、module、データフロー、境界を固定する。

### 6.2 成果物

- `docs/30_rust_architecture_overview.md`
- `docs/31_module_boundaries.md`
- `docs/32_data_model.md`
- `docs/33_runtime_loop.md`
- `docs/34_error_handling_and_logging.md`

### 6.3 採用する主要境界

- `chart`: 譜面パースと内部表現
- `song`: 曲メタデータと音源参照
- `time`: canonical time、chart time、audio time、offset
- `audio`: 再生制御と再生位置取得
- `input`: 入力イベント正規化
- `judgement`: 判定窓と判定結果
- `playfield`: ノーツ状態、スクロール、描画用状態
- `score`: スコア、コンボ、ゲージ
- `renderer`: 描画抽象
- `headless`: autoplay、非描画検証
- `telemetry`: timing log、実行ログ
- `tools`: analyzer、fixture生成、CI補助

## 7. Timing / Audio / Judgement検証設計: Timing / Audio / Judgement検証設計

### 7.1 目的

音ズレ、判定ズレ、フレーム依存バグをAIが検出できる形にする。

### 7.2 成果物

- `docs/40_timing_model.md`
- `docs/41_audio_sync_model.md`
- `docs/42_judgement_model.md`
- `docs/43_timing_log_schema.md`
- `docs/44_timing_log_analyzer_spec.md`

### 7.3 固定する内容

- canonical timeの定義
- chart time、audio time、game timeの対応
- offset適用順序
- 判定窓
- autoplay入力生成規則
- ノーツ到達予定時刻
- 実判定時刻
- audio position差分
- pass/fail閾値

## 8. テストハーネス・回帰検証設計: テストハーネス・golden fixture・回帰検証設計

### 8.1 目的

Codexが「実装した」と主張するだけでなく、機械的な合否判定を出せるようにする。

### 8.2 成果物

- `docs/50_test_harness_overview.md`
- `docs/51_fixture_design.md`
- `docs/52_golden_update_policy.md`
- `docs/53_ci_commands.md`
- `docs/53_ci_commands.md`

### 8.3 fixture分類

- 単一BPM譜面
- BPM変化譜面
- OFFSETあり譜面
- 空白小節あり譜面
- 複数ノーツ種別譜面
- 密集配置譜面
- 長時間安定性確認譜面
- 入力境界値確認譜面

## 9. Session分離・PR運用設計: Session分離・Git worktree・PR運用設計

### 9.1 目的

自己承認を避け、実装、レビュー、QAを独立Sessionで回せる状態にする。

### 9.2 成果物

- `docs/60_session_topology.md`
- `docs/61_worktree_policy.md`
- `docs/62_loop_engineering_flow.md`
- `docs/63_ticket_lifecycle.md`
- `docs/64_review_and_qa_gates.md`

### 9.3 Session構成

- 管制Session
- 仕様抽出Session
- 設計レビューSession
- テスト基盤Session
- チケット実装Session
- QA/回帰検証Session

## 10. Codexプロンプト整備: Codex用プロンプト群・テンプレート整備

### 10.1 目的

Codexにそのまま投入できる永続指示、Session別プロンプト、テンプレートを完成させる。

### 10.2 成果物

- `AGENTS.md`
- `prompts/30_control_session.md`
- `prompts/10_spec_extraction_session.md`
- `prompts/31_design_review_session.md`
- `prompts/20_test_infra_session.md`
- `prompts/32_ticket_implementation_session.md`
- `prompts/33_qa_regression_session.md`
- `templates/ticket_template.md`
- `templates/plan_review_template.md`
- `templates/pr_review_template.md`
- `templates/qa_report_template.md`
- `templates/failure_report_template.md`

## 11. Codex作業開始パッケージ: Codex作業開始パッケージ作成

### 11.1 目的

CodexへPhase1作業開始を指示できる状態にまとめる。

### 11.2 成果物

- `docs/80_codex_execution_checklist.md`
- `docs/81_human_operator_minimal_steps.md`
- `docs/70_phase1_ticket_backlog.md`
- `docs/73_first_execution_batch.md`
- `prompts/50_initial_control_session_start.md`
- `prompts/10_spec_extraction_session.md`
- `prompts/20_test_infra_session.md`
- `prompts/32_ticket_implementation_session.md`
- `prompts/33_qa_regression_session.md`

## 12. 標準ゲート

全回で次のゲートを適用する。

- 文書に責務が1つだけ定義されている。
- 実装開始前に必要な未決事項が明示されている。
- Codexが読み取れるファイル名、入力、出力、合格条件がある。
- 人間の主観判断に依存する合格条件を置かない。
- 実装Sessionが自分で最終承認できない構造になっている。
- failure loopへ戻すためのログまたはレビュー項目がある。

## 13. 準備計画完了状態

準備計画は、次の4ファイルが揃った状態で完了する。

- `docs/00_project_goal.md`
- `docs/01_preparation_workplan.md`
- `docs/02_document_index.md`
- `docs/03_definition_of_ready.md`

この4ファイルにより、OpenTaiko調査設計のOpenTaiko調査設計へ進む準備が整う。
