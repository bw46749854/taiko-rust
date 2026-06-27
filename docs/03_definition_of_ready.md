# 03_definition_of_ready: Phase1実装開始前 Definition of Ready

作成日: 2026-06-25  
状態: 第1回ドラフト・採用候補

## 1. Definition of Readyの目的

Definition of Readyは、CodexにPhase1実装開始を指示する前に満たすべき条件を定義する。目的は、実装Sessionが仕様不足、検証不足、Session責務の混線、曖昧な完了判定を理由に停止または自己承認へ流れることを防ぐことである。

Phase1実装開始は、この文書のReady項目が満たされた状態で行う。

## 2. Ready判定の単位

Ready判定は、次の4層で行う。

1. Project Ready: プロジェクト全体の目的と準備成果物が揃っている。
2. Specification Ready: Phase1仕様、非仕様、受け入れ基準が揃っている。
3. Engineering Ready: Rustアーキテクチャ、検証設計、CIコマンドが揃っている。
4. Operation Ready: Session分離、worktree、チケット、レビュー、QA導線が揃っている。

4層すべてを満たしてからPhase1実装を開始する。

## 3. Project Ready

### 3.1 必須文書

- `docs/00_project_goal.md`
- `docs/01_preparation_workplan.md`
- `docs/02_document_index.md`
- `docs/03_definition_of_ready.md`

### 3.2 合格条件

- Phase1の上位目的が明文化されている。
- AIループエンジニアリング基盤の整備が主目的に含まれている。
- 準備作業が9回に分割されている。
- 文書体系が定義されている。
- Phase1実装開始前のReady条件が定義されている。

## 4. Specification Ready

### 4.1 必須文書

- `docs/10_opentaiko_research_plan.md`
- `docs/11_opentaiko_feature_taxonomy.md`
- `docs/12_opentaiko_phase1_research_questions.md`
- `docs/20_phase1_scope.md`
- `docs/21_phase1_non_scope.md`
- `docs/22_phase1_acceptance_criteria.md`
- `docs/23_phase1_definition_of_done.md`

### 4.2 合格条件

- OpenTaiko調査の対象と非対象が定義されている。
- Phase1対象機能が列挙されている。
- Phase1非対象機能が列挙されている。
- 商用ゲーム表現、第三者アセット、許可不明素材を取り込まない制約が明記されている。
- 通常プレイの開始、進行、終了、リザルトが仕様化されている。
- `.tja`読み込みのPhase1対応範囲が定義されている。
- BPM、OFFSET、ノーツ時刻、スクロール、判定の扱いが仕様化されている。
- 合格条件がログ、コマンド、数値、fixtureで判定可能になっている。

## 5. Engineering Ready

### 5.1 必須文書

- `docs/30_rust_architecture_overview.md`
- `docs/31_module_boundaries.md`
- `docs/32_data_model.md`
- `docs/33_runtime_loop.md`
- `docs/34_error_handling_and_logging.md`
- `docs/40_timing_model.md`
- `docs/41_audio_sync_model.md`
- `docs/42_judgement_model.md`
- `docs/43_timing_log_schema.md`
- `docs/44_timing_log_analyzer_spec.md`
- `docs/50_test_harness_overview.md`
- `docs/51_fixture_design.md`
- `docs/52_golden_update_policy.md`
- `docs/53_ci_commands.md`
- `docs/53_ci_commands.md`

### 5.2 合格条件

- Rust workspace構成が定義されている。
- crateまたはmodule境界が定義されている。
- realtime依存処理とdeterministic処理が分離されている。
- audio、renderer、inputは抽象境界を持つ。
- chart parser、time model、judgement、score、gaugeは単体テスト可能である。
- headless autoplayが描画なしで実行できる設計になっている。
- timing log schemaが定義されている。
- timing log analyzerがpass/failとexit codeを返す仕様になっている。
- golden fixtureとgolden logの更新ルールが定義されている。
- CIまたはローカル必須コマンドが定義されている。

### 5.3 必須コマンド

Phase1実装チケットの完了報告には、少なくとも次のコマンド結果を含める。

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all
cargo run --bin headless_autoplay -- --fixture fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja
cargo run --bin timing_log_analyzer -- --input target/timing/basic_single_bpm.jsonl --golden out/synthetic_analyzer.json
```

正確な引数とfixture名は `docs/53_ci_commands.md` と各ticketを正とする。

## 6. Operation Ready

### 6.1 必須文書

- `docs/60_session_topology.md`
- `docs/61_worktree_policy.md`
- `docs/62_loop_engineering_flow.md`
- `docs/63_ticket_lifecycle.md`
- `docs/64_review_and_qa_gates.md`
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

### 6.2 合格条件

- 管制Sessionの責務が定義されている。
- 仕様抽出Sessionの責務が定義されている。
- 設計レビューSessionの責務が定義されている。
- テスト基盤Sessionの責務が定義されている。
- チケット実装Sessionの責務が定義されている。
- QA/回帰検証Sessionの責務が定義されている。
- 各Sessionは別threadで起動する。
- 実装SessionとレビューSessionは別worktreeで作業する。
- 実装SessionとQA/回帰検証Sessionは別worktreeで作業する。
- 実装者が自分のPRを合格判定しない。
- NG時はfailure reportを作成し、修正チケットまたは修正Planへ戻す。

## 7. チケットReady

各実装チケットは、次の項目を持つ。

- チケットID
- タイトル
- 対象Phase
- 対象module
- 関連文書
- 背景
- 実装範囲
- 非実装範囲
- 受け入れ基準
- 必須コマンド
- headless autoplay対象fixture
- timing log analyzer対象fixture
- 期待されるログまたは統計
- 失敗時に添付するログ
- Planレビュー担当Session
- QA担当Session

この項目が欠けたチケットは実装開始しない。

## 8. PR Ready

PR作成前に、実装Sessionは次を提出する。

- 実装Plan
- Planレビュー結果
- 変更ファイル一覧
- 実行したコマンドと結果
- headless autoplay結果
- timing log analyzer結果
- 未解決事項
- QAへ渡す観点

PR本文は `templates/pr_review_template.md` に従う。

## 9. QA Ready

QA/回帰検証Sessionは、次を受け取ってから検証を開始する。

- PRまたはbranch名
- 対象チケット
- 関連文書
- 実装Sessionの完了報告
- 実行すべき検証コマンド
- 期待されるpass/fail条件

QAは別worktreeで検証し、`templates/qa_report_template.md` に従って結果を返す。

## 10. Failure Loop Ready

失敗時は、次の情報をfailure reportに記録する。

- 失敗したコマンド
- exit code
- stderr要約
- timing log analyzerのfail項目
- goldenとの差分
- 再現手順
- 推定原因
- 修正対象module
- 次の修正Planへの入力

失敗ログがないNG判定は採用しない。NGは必ず再現可能な入力へ変換する。

## 11. Ready判定表

| 層 | 必須状態 | 判定者 |
|---|---|---|
| Project Ready | 第1回成果物が揃っている | 管制Session |
| Specification Ready | Phase1仕様とOpenTaiko調査設計が揃っている | 設計レビューSession |
| Engineering Ready | Rust設計、timing設計、test harness設計が揃っている | 設計レビューSession + テスト基盤Session |
| Operation Ready | Session分離、worktree、PR、QA、failure loopが揃っている | 管制Session + QA/回帰検証Session |
| Ticket Ready | 初回バックログがReady項目を満たしている | 管制Session |

## 12. Phase1実装開始の最終ゲート

Phase1実装開始は、次の状態で行う。

- 第1回から第9回までの成果物が存在する。
- `AGENTS.md` が存在する。
- 各Session起動プロンプトが存在する。
- 初回バックログが存在する。
- 最初のチケットがTicket Readyを満たしている。
- worktree作成手順が存在する。
- headless autoplayとtiming log analyzerのskeletonチケットが存在する。
- QA/回帰検証Sessionが合否判定できる。

このゲートを通過した後、CodexへPhase1の実装開始を指示する。
