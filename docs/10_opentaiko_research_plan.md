# 10_opentaiko_research_plan: OpenTaiko調査設計

作成日: 2026-06-25  
状態: 第2回ドラフト・採用候補

## 1. 目的

この文書は、OpenTaikoから何を調べ、何をPhase1 Rust実装の参考仕様にし、何を調査のみまたはPhase2以降へ送るかを固定する。

第2回の主目的は、仕様抽出Sessionがすぐに調査を開始できる状態を作ることである。調査対象を広げすぎるとPhase1が収束しないため、OpenTaiko全体を網羅するのではなく、1人用通常プレイ、`.tja` 読み込み、タイミング、判定、スコア、ゲージ、リザルト、headless検証に必要な観点へ限定する。

## 2. 調査の上位方針

OpenTaikoはRust版の直接移植元ではなく、参考仕様の主要情報源である。Rust版では、C#実装の構造をそのまま移すのではなく、Phase1に必要なプレイ仕様、データ仕様、時刻仕様、検証観点を抽出し、Rust向けの独立した設計へ変換する。

調査では以下を守る。

1. 商用ゲームのUI、演出、アセット、挙動の正確な複製を目的にしない。
2. OpenTaikoのソース、README、CHANGELOG、設定、既存コメントから、通常プレイ成立に必要な事実を抽出する。
3. 抽出結果は、Rust版でテスト可能な仕様に変換する。
4. OpenTaikoの複雑な拡張機能は、Phase1対象、Phase2対象、Phase3以降、対象外、調査のみへ分類する。
5. 推測だけで仕様化しない。出典ファイル、該当関数、該当変数、観測した挙動を記録する。
6. 実装Sessionが直接使えるように、調査結果には「Phase1反映」「Phase1非反映」「未解決」を必ず付ける。

## 3. 参照リポジトリの初期観測

2026-06-25時点の初期観測では、OpenTaiko公開リポジトリは以下の特徴を持つ。

- リポジトリ: `0auBSQ/OpenTaiko`
- デフォルトブランチ: `main`
- 主要ディレクトリ: `.github/workflows`, `FDK`, `OpenTaiko`, `special`
- 主要ファイル: `OpenTaiko.sln`, `README.md`, `README-JA.md`, `CHANGELOG.md`, `LICENSE`
- GitHub表示上の主要言語: C#中心、Luaを含む
- README上の目的: TJAPlayer3系の `.tja` chart player
- README上の非目的: 商用ゲームや商用ライセンスの正確なコピー
- README上の注意: 曲、スキン、アセットは別リポジトリまたはHub管理であり、著作権法と各作者ライセンスに従う必要がある

調査Sessionは、上記を出発点にして、最新のリポジトリ状態を再確認してから調査を開始する。

## 4. 調査対象ファイルの初期リスト

仕様抽出Sessionは、最初に以下を読む。

| 優先 | パス | 主目的 |
|---:|---|---|
| P0 | `README.md` | プロジェクト目的、非目的、ライセンス、アセット境界を確認する |
| P0 | `README-JA.md` | 日本語での利用上の注意、目的、非目的を確認する |
| P0 | `LICENSE` | MIT License範囲を確認する |
| P0 | `OpenTaiko/src/Songs/CTja.cs` | `.tja` メタデータ、譜面パース、BPM、OFFSET、SCROLL、分岐、WAV、内部リストを調査する |
| P0 | `OpenTaiko/src/Songs/TJA/CChip.cs` | 譜面イベント、ノーツ、発声時刻、チップ状態、チャンネル番号を調査する |
| P0 | `OpenTaiko/src/Stages/07.Game/CStage演奏画面共通.cs` | 演奏開始、結果格納、共通プレイ状態、スコア計算入口、ゲージ入口を調査する |
| P0 | `OpenTaiko/src/Stages/07.Game/Taiko/CStage演奏ドラム画面.cs` | 太鼓通常プレイ固有の入力、判定、描画更新、autoplay相当処理を調査する |
| P0 | `OpenTaiko/src/Stages/07.Game/Taiko/NotesManager.cs` | ノーツ種別、入力種別、ノーツ移動式、表示分類を調査する |
| P1 | `OpenTaiko/src/Stages/07.Game/*Gauge*` または関連ファイル | ゲージ増減モデルを調査する |
| P1 | `OpenTaiko/src/Stages/07.Game/*Score*` または関連ファイル | スコア、コンボ、リザルトへ渡す値を調査する |
| P1 | `OpenTaiko/src/Config*` または設定関連ファイル | 判定窓、AutoPlay、音声補正、入力設定を調査する |
| P1 | `FDK` 以下の音声、タイマー、入力関連 | 実時間、音声再生位置、入力取得の境界を調査する |
| P2 | `CHANGELOG.md` | 近年の仕様変更、タイミング、判定、譜面互換性に関する変更を調査する |

初期リストに存在しないファイルが見つかった場合、仕様抽出Sessionは調査ログに追加する。追加したファイルは、必ず「なぜ必要か」を1行で記録する。

## 5. 調査する機能範囲

### 5.1 Phase1へ直接反映する調査範囲

Phase1へ直接反映する範囲は以下で固定する。

| 分類 | 調査対象 | Phase1への変換 |
|---|---|---|
| `.tja` メタデータ | TITLE, SUBTITLE, BPM, WAVE, OFFSET, COURSE, LEVEL, BALLOON, SCOREINIT, SCOREDIFFなど | Rust内部の `SongMetadata`, `CourseMetadata`, `Chart` へ変換する |
| 譜面ノーツ | 0〜9, A〜I等のノーツ文字、休符、ロール、風船、終端 | Phase1対応ノーツ種別を定義する |
| BPM/MEASURE | BPM変化、小節長、譜面上時刻への変換 | canonical time計算へ反映する |
| OFFSET | 音源開始時刻と譜面開始時刻の差 | audio sync modelへ反映する |
| SCROLL | ノーツ移動速度 | 表示位置計算とheadless到達時刻検証へ反映する |
| 入力 | red/blue系入力、左右入力、大音符の扱い | `input` と `judgement` の境界へ反映する |
| 判定 | Perfect/Great/Miss等の判定、判定窓、miss処理 | `judgement` moduleへ反映する |
| スコア | score init/diff、コンボ、加点 | `score` moduleへ反映する |
| ゲージ | クリア判定、増減、リザルト | `gauge` moduleへ反映する |
| リザルト | 良/可/不可、コンボ、スコア、クリア | `result` modelへ反映する |
| autoplay | 自動入力生成の考え方 | headless autoplayへ反映する |
| ログ | エラー、クラッシュ、タイミング検証の入口 | timing log / failure reportへ反映する |

### 5.2 Phase1で調査のみ行う範囲

以下はPhase1の実装対象にしない。ただし、通常プレイ仕様の境界を誤らないため調査のみ行う。

- 譜面分岐
- 段位、Tower、AI Battle、特殊モード
- 2P以上の多人数プレイ
- 複雑なスキン、演出、Lua拡張
- 動画、歌詞、背景演出、カメラ移動
- OpenTaiko独自拡張のうち、通常プレイ最小成立に不要なもの
- Hub、配布、外部曲・スキン管理

### 5.3 調査対象外

以下は調査対象外とする。

- 商用ゲームの挙動、画面、演出、アセットの再現調査
- 著作権・商標上の権利確認がない曲、スキン、画像、音源の収集
- プレイ体験の雰囲気再現を目的にしたスクリーンショット収集
- OpenTaikoの全機能網羅

## 6. 調査の実行手順

仕様抽出Sessionは以下の順で作業する。

### 6.1 リポジトリスナップショット確認

1. `git rev-parse HEAD` で対象commitを記録する。
2. `git status --short` で作業ツリーが汚れていないことを記録する。
3. `README.md`, `README-JA.md`, `LICENSE` を読む。
4. 調査ログに、参照したcommit、日付、主要ディレクトリを記録する。

### 6.2 ソース入口調査

1. `OpenTaiko/src/Songs/CTja.cs` を読む。
2. `.tja` メタデータ、譜面行、命令、BPM、OFFSET、SCROLL、分岐の処理入口を列挙する。
3. `OpenTaiko/src/Songs/TJA/CChip.cs` を読む。
4. `CChip` が保持するノーツ時刻、BPM、SCROLL、チャンネル番号、表示状態、判定状態を列挙する。
5. `NotesManager.cs` を読む。
6. ノーツ文字、ノーツ種別、入力種別、ノーツ位置計算式を抽出する。

### 6.3 通常プレイ導線調査

1. 曲選択後に `CTja` がどのように演奏画面へ渡るかを追跡する。
2. 演奏画面Activate時の初期化を追跡する。
3. 音源再生開始、ゲーム内時刻、チップ処理、入力処理、判定、スコア、ゲージ、リザルト保存の順序を記録する。
4. 60fps依存、OSタイマー依存、音声デバイス依存の箇所を記録する。

### 6.4 検証可能仕様への変換

1. 調査結果を「OpenTaikoの観測事実」と「Rust版Phase1仕様案」に分離する。
2. Rust版では、音声・描画・入力を抽象化し、headless autoplayで再現できる形にする。
3. タイミング品質に関係する項目は、`expected_time_ms`, `actual_time_ms`, `delta_ms`, `audio_time_ms`, `frame_index` のようなログ項目へ変換する。
4. 未解決事項は、Phase1スコープ定義前に必ず質問として残す。

## 7. 調査ログ形式

各調査メモは以下の形式に従う。

```markdown
# Research Note: <対象>

作成日: YYYY-MM-DD
対象commit: <sha>
調査者Session: 仕様抽出Session

## 1. 調査対象

- ファイル:
- 関数/クラス:
- 行または検索語:

## 2. 観測事実

- 事実1
- 事実2

## 3. Phase1への反映

- 反映する仕様:
- Rust module候補:
- 必要なテスト:

## 4. Phase1では反映しない内容

- 内容:
- 理由:
- 送り先: Phase2 / Phase3以降 / 対象外 / 調査のみ

## 5. 未解決事項

- QID:
- 質問:
- 次に読むファイル:
```

## 8. Phase1反映の判断基準

調査項目は以下の基準で分類する。

| 判定 | 基準 |
|---|---|
| Phase1 | 1人用通常プレイの開始、進行、終了、リザルト、headless検証に必須である |
| Phase2 | 通常プレイは成立するが、プレイオプションや追加設定として後から組み合わせる機能である |
| Phase3以降 | モード、演出、拡張、管理機能として大きな追加実装を要する |
| 対象外 | 商用ゲームの正確な複製、第三者アセット依存、Phase1目的外である |
| 調査のみ | 境界理解には必要だが、Phase1実装に入れない |

判断に迷う項目は一時的に「調査のみ」に置く。第3回のPhase1スコープ定義で最終判定する。

## 9. 必須の調査成果物

仕様抽出Sessionは、最低限以下を作成する。

| 出力 | 内容 |
|---|---|
| `research/opentaiko/00_snapshot.md` | commit、主要ディレクトリ、README上の目的・非目的、ライセンス境界 |
| `research/opentaiko/10_tja_parser.md` | `.tja` metadata、命令、ノーツ行、対応/非対応候補 |
| `research/opentaiko/20_timing.md` | BPM、OFFSET、MEASURE、SCROLL、時刻変換、音声時刻 |
| `research/opentaiko/30_notes_and_input.md` | ノーツ種別、入力種別、レーン、big note、roll |
| `research/opentaiko/40_judgement.md` | 判定窓、判定結果、miss処理、autoplay入力 |
| `research/opentaiko/50_score_gauge_result.md` | スコア、コンボ、ゲージ、リザルト |
| `research/opentaiko/60_render_runtime.md` | 描画更新、ノーツ位置、フレーム依存箇所 |
| `research/opentaiko/70_phase_classification.md` | Phase1/2/3/対象外/調査のみの分類表 |
| `research/opentaiko/80_unresolved_questions.md` | 第3回までに解く未解決事項 |

## 10. 調査完了条件

第2回成果物に基づくOpenTaiko調査は、次を満たした状態で完了とする。

- P0対象ファイルをすべて読んでいる。
- `.tja` 読み込み、timing、input、judgement、score、gauge、resultに対する観測事実がある。
- 各観測事実に出典ファイルと該当箇所がある。
- Phase1へ反映する項目と反映しない項目が分かれている。
- 未解決事項がQID付きで管理されている。
- 第3回 `docs/20_phase1_scope.md` を作れるだけの入力が揃っている。

## 11. 仕様抽出Sessionへの禁止事項

仕様抽出Sessionは以下を行わない。

- Rust実装を開始しない。
- チケット実装を開始しない。
- OpenTaikoのコードをそのままRustへ翻訳しない。
- アセット、曲、スキン、画像、音源を収集しない。
- 商用ゲームの再現に向けた調査をしない。
- 出典のない推測をPhase1仕様として確定しない。

## 12. 次回への受け渡し

この調査設計の次工程は、第3回「Phase1スコープ・非スコープ・受け入れ基準の定義」である。第3回では、この文書と `docs/11_opentaiko_feature_taxonomy.md`、`docs/12_opentaiko_phase1_research_questions.md` を入力として、Phase1で実装する対象を確定する。
