# 23_phase1_definition_of_done: Phase1完了定義

作成日: 2026-06-25
Status: canonical
目的: Phase1を「実装済み」ではなく「OpenTaiko通常プレイ対応範囲を検証済み・回帰可能・AIループで収束可能」な状態として完了判定する。

## 1. Definition of Doneの上位定義

Phase1のDoneは、通常プレイ機能と検証基盤の両方が完了した状態である。ゲームが起動するだけではDoneではない。単一の簡単な譜面を再生できた状態でもDoneではない。

Doneは、次の6条件を同時に満たす状態である。

1. 実装範囲が `docs/20_phase1_scope.md` と一致している。
2. 非対象範囲が `docs/21_phase1_non_scope.md` に従って除外されている。
3. `docs/24_phase1_normal_play_compatibility_contract.md` に違反していない。
4. `docs/25_phase1_feature_classification.md` のMust implement gameplay項目が検証済みである。
5. `docs/22_phase1_acceptance_criteria.md` の全項目がPASSしている。
6. 実装Session以外のQA/回帰検証Sessionが最終判定している。

## 2. Done Gate一覧

| Gate | 名称 | 判定者 | 合格条件 |
|---|---|---|---|
| G0 | Compatibility Gate | 管制Session + 設計レビューSession | ticketがCompatibility Contractに従う |
| G1 | Scope Gate | 管制Session | Must implement / parse/report / non-scope分類が明記されている |
| G2 | Research Gate | 仕様抽出Session + 設計レビューSession | OpenTaiko調査根拠が `research/opentaiko/` にある |
| G3 | Design Gate | 設計レビューSession | module境界、timing、branch、score/gaugeに矛盾がない |
| G4 | Implementation Gate | チケット実装Session | 実装と自己テストが完了 |
| G5 | Static Gate | チケット実装Session | fmt/clippy/testが通る |
| G6 | Headless Gate | テスト基盤Sessionまたは実装Session | headless autoplayが通る |
| G7 | Analyzer Gate | QA/回帰検証Session | timing log analyzerがPASS |
| G8 | Synthetic Regression Gate | QA/回帰検証Session | synthetic fixturesのgolden差分が0 |
| G9 | User Song Gate | QA/回帰検証Session | user-selected songs標準10カテゴリがPASS |
| G10 | Final Acceptance Gate | QA/回帰検証Session | Phase1 acceptance reportがPASS |

G7〜G10は実装Sessionが担当しない。自己承認を禁止する。

## 3. チケット単位のDone

各チケットは、次を満たしてDoneにする。

### 3.1 入力文書

チケット着手前に、チケット本文へ次を明記する。

- 対象scope ID
- 対象feature classification ID
- 対象acceptance criteria ID
- OpenTaiko調査成果物への参照
- 参照設計文書
- 変更予定module
- 実行必須コマンド
- 期待されるtiming logまたはresult summary
- compatibility reportへの影響
- 非スコープに触れないことの確認

### 3.2 実装完了

実装完了には次を要求する。

- 変更内容がチケット目的へ限定されている。
- public APIまたはデータモデル変更が設計文書へ反映されている。
- parse error、unsupported compatibility、explicit non-scope、runtime errorを区別している。
- timing logへの影響がある変更ではschema/testを更新している。
- fixtureへ影響する変更ではexpected summaryをレビュー対象にしている。
- branch、scroll、score/gaugeへ影響する変更では専用fixtureを追加または更新している。

### 3.3 検証完了

検証完了には次を要求する。

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all
cargo run --bin taiko_cli -- check all
cargo run --bin headless_autoplay -- <ticket fixture args>
cargo run --bin timing_log_analyzer -- <ticket log args>
```

ticketがuser-selected song validationに影響する場合、次も要求する。

```bash
cargo run --bin taiko_cli -- user-song validate --manifest <manifest path>
```

実行ログをPRまたはhandoff文書へ貼る。コマンド未実行はDoneにしない。

## 4. Feature group単位のDone

### 4.1 Parser Done

- 必須headerを読める。
- 複数COURSEから対象COURSEを抽出できる。
- `#START`〜`#END` の対象courseだけを抽出できる。
- 0〜9のPhase1 gameplay noteを内部eventへ変換できる。
- A/B/C/D/F/G/H/Iをparse/report対象として処理できる。
- BPM/MEASURE/SCROLL/DELAY/OFFSET/GOGO/BARLINE/BRANCHを内部eventへ変換できる。
- parser unit testとfixture testが通る。

### 4.2 Scheduler / Timing Done

- 任意分割note schedulerを実装している。
- 4/8/12/16/24/36分、32/48相当、混合n分を同一schedulerで扱う。
- BPMCHANGE、MEASURE、DELAY、OFFSETの計算が単体テストで検証されている。
- display position計算とjudgement計算が分離されている。
- headless variable tickで結果が一致する。
- timing log analyzerがdeltaを検証できる。

### 4.3 Note / Roll / Balloon Done

- Don/Ka/大Don/大Kaを判定できる。
- 通常連打、大連打の区間と打数を扱える。
- 風船のrequired hits、成功、失敗を扱える。
- BalloonEx/くすだま相当を扱える。
- BALLOON headerと分岐別BALLOON配列を扱える。
- resultへroll/balloon/BalloonEx結果を出せる。

### 4.4 Branch Done

- SECTION、BRANCHSTART、N/E/M、LEVELHOLD、BRANCHENDをparseできる。
- N/E/M route別note streamを保持できる。
- 精度、良/可/不可、連打、風船、scoreに基づくroute選択ができる。
- headless autoplayでroute coverage用入力profileを実行できる。
- branch routeがtiming logとresult summaryへ出る。

### 4.5 Scroll / Visual Timing Done

- 正、負、0、高速SCROLLを表示位置計算へ反映できる。
- 追い越し表示でpanicしない。
- NMSCROLL、BMSCROLL、HBSCROLLを扱える。
- SUDDEN、DIRECTION、JPOSSCROLLはparse/reportできる。
- 表示ギミックがjudgement結果を変えない。

### 4.6 Audio Done

- WAVE/PATH_WAVからBGM音源を読み込める。
- 再生、停止、再生位置取得ができる。
- headless仮想audio clockと描画あり実audio clockを切り替えられる。
- OFFSET正負をchart/audio deltaへ反映できる。
- audio deltaをtiming logへ出せる。

### 4.7 Input / Judgement Done

- Red/Blue左右入力を正規化できる。
- Big入力を扱える。
- input eventに時刻、source、kindが入る。
- Perfect/Good/Miss相当を返せる。
- early/late deltaをlogへ出せる。
- hit済みノーツを再判定しない。
- miss確定がframe rateへ依存しない。

### 4.8 Score / Combo / Gauge Done

- SCOREINIT/SCOREDIFF/SCOREMODEをscore configへ反映できる。
- 通常ノーツ、大音符、roll、balloon、BalloonExのscoreを計算できる。
- GOGO stateをscore/logへ反映できる。
- combo増加、切断、max combo保存が正しい。
- gauge増減、clamp、clear判定が正しい。
- golden summaryと一致する。

### 4.9 Rendering / Runtime Done

- 描画あり実行で起動、曲開始、譜面進行、曲終了、リザルト遷移ができる。
- ノーツ、barline、score、combo、gaugeが表示される。
- runtime panicがなく、errorはユーザー向けmessageとlogに出る。
- 描画処理がjudgement結果を変えない。

### 4.10 Headless / Analyzer Done

- headless autoplayが全synthetic fixtureを実行する。
- headless autoplayがuser-selected song manifestを実行する。
- timing logがJSONL schemaに合う。
- analyzerがPASS/FAIL/BLOCKEDを返す。
- analyzerのexit codeがCIで使える。
- golden summary比較ができる。
- 差分発生時にfield単位のfailureを出す。

## 5. Phase1全体Done

### 5.1 Code成果物

- Rust workspace
- parser module
- scheduler/timing module
- branch module
- scroll/visual timing module
- audio abstraction
- input module
- judgement module
- score/gauge module
- runtime/playfield module
- renderer integration
- headless autoplay binary
- timing log analyzer binary
- taiko_cli binary
- fixture directory
- CI command scripts

### 5.2 Documentation成果物

- Compatibility Contract
- feature classification
- OpenTaiko調査成果物
- Phase1 scope
- Phase1 non-scope
- Phase1 acceptance criteria
- Rust architecture overview
- timing model
- audio sync model
- judgement model
- branch model
- score/gauge model
- timing log schema
- analyzer spec
- test harness design
- fixture design
- user-selected song validation design
- golden log policy
- session/worktree policy
- AGENTS.md
- ticket template
- PR review checklist

### 5.3 Evidence成果物

- `reports/phase1_acceptance_report.md`
- `reports/compatibility/*.md`
- `reports/user_selected/*.md`
- `target/timing/*.jsonl`
- `target/timing/*.summary.json`
- `reports/regression/*.md`
- command logs
- failed-run logsが0件、または全件が修正済みticketへ紐づく

## 6. Failure handling

FAILを検出したときは、次の形式で修正ループへ戻す。

```markdown
# Failure Handoff

- failure id:
- detected by:
- command:
- fixture or song id:
- expected:
- actual:
- delta:
- related scope id:
- related classification id:
- related acceptance id:
- suspected module:
- required next session:
- proposed ticket title:
```

FAILを「既知の問題」として残したままPhase1 Doneにしない。

## 7. Golden更新ルール

Golden更新は、実装の都合で行わない。Golden更新は次の条件を満たす。

- Compatibility Contractに違反していない。
- 仕様文書が更新されている。
- OpenTaiko調査根拠またはPhase1設計根拠がある。
- expected値の変更理由がある。
- 旧実装のバグ修正に伴う変更であることが説明されている。
- QA/回帰検証Sessionが差分を確認している。
- 管制Sessionが対象チケットを発行している。

Golden更新だけのPRは、実装修正PRと分離する。
