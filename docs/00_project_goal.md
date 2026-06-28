# 00_project_goal: OpenTaiko参考 Rustリズムゲーム Phase1 Codexループ準備ゴール

作成日: 2026-06-25
Status: adopted

## 1. 本プロジェクトの主目的

本プロジェクトの主目的は、Rustでリズムゲームを実装すること単体ではない。主目的は、Codexを中心にしたAIループエンジニアリングの導線を整備し、実装、テスト、バグ検出、修正、精度調整、回帰検証をAIが反復できる状態を作ることである。

Phase1では、OpenTaikoを参考仕様の主要情報源として扱い、1人用の通常プレイが成立するRust製リズムゲームを完成させる。完成判定は人間の主観ではなく、コマンド、ログ、golden fixture、timing log analyzer、QAレポートによって行う。

## 2. 開発対象

開発対象は、OpenTaiko相当の通常プレイ体験を目指す独自Rust実装である。OpenTaikoの既存コードは参考調査対象とし、Rust版のソース構造、データモデル、テスト構造、実行導線は新規に設計する。

OpenTaikoはGitHub上で公開されている既存実装であり、READMEでは TJAPlayer3 の精神的後継である `.tja` chart player と説明されている。現行リポジトリはC#中心で、Luaも含む構成である。Rust版ではC#コードの逐語的な移植ではなく、通常プレイに必要な仕様要素を抽出して、Rust向けに分解して実装する。

## 3. Phase1の目的

Phase1の目的は、任意の許可済み曲データと譜面データを使って、1人用の通常プレイが破綻なく成立することである。

Phase1で成立させる体験は次の通りである。

1. 曲を選択または指定する。
2. 曲メタデータ、音源、譜面を読み込む。
3. プレイ開始時に音源時刻とゲーム内時刻を同期する。
4. 譜面上のノーツが判定ラインへ到達する。
5. プレイヤー入力またはautoplay入力に対して判定を行う。
6. スコア、コンボ、ゲージを更新する。
7. 曲終了後にリザルトを表示または出力する。
8. headless autoplayで同じ譜面を非描画実行できる。
9. timing log analyzerでズレと判定分布を検証できる。

Phase1では、ゲーム本体と同じ重みで検証基盤を扱う。検証できない機能はPhase1完了扱いにしない。

## 4. Phase1の非目的

Phase1では、以下を実装対象から外す。

- 多人数プレイ
- ネットワーク機能
- 高度なスキンシステム
- 商用ゲームのUI、演出、アセット、挙動の正確な複製
- OpenTaiko全モードの網羅
- AI Battle、段位、特殊モード
- Phase2で扱うプレイオプション群
- 大規模な譜面管理UI
- 配布用ランチャー、Hub、外部アセット管理

Phase1は「通常プレイが検証可能に成立する最小完備範囲」として固定する。

## 5. 最重要品質属性

### 5.1 Timing correctness

リズムゲームの中核品質は、chart time、audio time、game time、frame time、input timeの整合性である。Phase1ではcanonical timeを明示し、すべての判定、ノーツ移動、ログ出力をこの時刻モデルへ従属させる。

### 5.2 Determinism

headless autoplay、timing log analyzer、golden fixtureの比較は、同じ入力から同じ結果が得られることを要求する。乱数、フレームレート、OSスケジューリング、音声デバイス差異による揺らぎは、ログ上で分離して扱う。

### 5.3 Testability

描画や音声デバイスへ依存する処理は抽象境界を持つ。譜面パース、時刻計算、判定、スコア、ゲージ、autoplay、timing log生成は単体テストとheadless統合テストで検証できる構造にする。

### 5.4 Session separation

自己承認を避けるため、設計、実装、レビュー、QAは別thread・別Git worktreeで分離する。実装Sessionは自分の変更を最終合格判定しない。

## 6. AIループエンジニアリングの目的

AIループは、次のサイクルを人間の介入なしで回せる状態を目指す。

```text
仕様・設計を読む
→ チケットを読む
→ Planを作る
→ Planレビューを受ける
→ 実装する
→ fmt / clippy / testを実行する
→ headless autoplayを実行する
→ timing log analyzerを実行する
→ QAレビューを受ける
→ NGログを修正入力へ戻す
→ PR化する
```

このサイクルの中心成果物は、コードではなく「失敗から次の修正へ戻るための情報構造」である。したがって、すべてのチケットに実行コマンド、期待ログ、合否閾値、失敗時の報告形式を持たせる。

## 7. Phase1完了の上位判定

Phase1完了は、以下のすべてが満たされた状態とする。

- Rust workspaceが構築されている。
- 曲メタデータ、音源、譜面を読み込める。
- 1人用通常プレイを開始、進行、終了できる。
- ノーツ描画または描画抽象により、判定ライン到達がモデル化されている。
- 入力受付と判定が実装されている。
- スコア、コンボ、ゲージ、リザルトが実装されている。
- headless autoplayでfixture譜面を完走できる。
- timing log schemaに従うログが出力される。
- timing log analyzerが許容閾値に基づきpass/failを返す。
- golden fixtureとの差分検証がCIまたはローカルコマンドで実行できる。
- `cargo fmt --check`、`cargo clippy --all-targets --all-features -- -D warnings`、`cargo test --all` が通る。
- QA/回帰検証Sessionが、実装Sessionとは別worktreeで合否を判定している。

## 8. ライセンスとアセット境界

OpenTaiko本体はMIT Licenseで公開されている。Rust版では、第三者アセット、曲、譜面、スキン、フォント、商用ゲーム由来表現を混入させない。テスト用fixtureは自作または利用許諾が明確なものだけを使用する。

Phase1準備文書には、実装者が誤って既存アセットや商用ゲーム表現を取り込まないための制約を含める。

## 9. 準備計画で固定する決定

準備計画では次を固定する。

- この準備プロジェクトの完了状態
- 9回構成の作業分割
- 文書体系
- 準備完了判定
- レビュー対象となる文書の責務
- Phase1実装開始前に必須となるDefinition of Ready

詳細なPhase1仕様、OpenTaiko機能調査、Rustモジュール設計、timing log schema、Session別プロンプトはOpenTaiko調査設計以降で作成する。
