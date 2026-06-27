# 30_rust_architecture_overview: Rust版アーキテクチャ概要

作成日: 2026-06-25  
状態: 第4回ドラフト・採用候補  
上流文書: `docs/20_phase1_scope.md`, `docs/21_phase1_non_scope.md`, `docs/22_phase1_acceptance_criteria.md`, `docs/23_phase1_definition_of_done.md`

## 1. 目的

この文書は、Phase1実装をCodexへ渡す前に、Rust版リズムゲームの上位アーキテクチャを固定する。対象は、1人用通常プレイ、描画あり実行、headless autoplay、timing log analyzerである。

Phase1の主目的は、ゲーム本体だけを作ることではない。実装、検証、回帰、修正をAIが反復できる構造を作ることである。そのため、アーキテクチャは次を最優先にする。

- 通常プレイ処理をdeterministicに再実行できる。
- 描画あり実行とheadless実行が同じdomain/runtimeを通る。
- audio、renderer、input、wall clockを差し替え可能にする。
- timing、judgement、score、gauge、resultをログから検証できる。
- Session分離レビューで責務境界を追跡できる。

## 2. 採用する全体方針

Rust版Phase1は、pure domain coreとplatform adapterを分離する。

```text
+-------------------------------------------------------------+
| binaries                                                    |
|  - taiko_play                                               |
|  - headless_autoplay                                        |
|  - timing_log_analyzer                                      |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
| app / orchestration                                         |
|  CLI, config loading, fixture loading, run lifecycle         |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
| runtime core                                                |
|  RuntimeState, RuntimeStep, PlayPhase, event dispatch        |
+------+--------------+-------------+--------------+----------+
       |              |             |              |
       v              v             v              v
+------+----+   +-----+-----+  +----+------+  +----+----------+
| chart     |   | time      |  | judgement |  | score/gauge   |
| parser    |   | clocks    |  | windows   |  | result        |
+-----------+   +-----------+  +-----------+  +---------------+
       ^              ^             ^              ^
       |              |             |              |
+------v--------------v-------------v--------------v----------+
| telemetry                                                   |
|  timing log JSONL, summary JSON, trace log, analyzer input   |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
| platform adapters                                           |
|  audio(cpal), render(wgpu+winit), input(winit), file I/O     |
+-------------------------------------------------------------+
```

## 3. binary名の固定

第3回の受け入れ基準ではbinary名が暫定だった。第4回で次に固定する。

| binary | 役割 | 必須性 |
|---|---|---|
| `taiko_play` | 描画あり通常プレイ。CLIから `.tja` を起動する | Phase1必須 |
| `headless_autoplay` | 描画なしdeterministic autoplay。timing logとsummaryを出力する | Phase1必須 |
| `timing_log_analyzer` | timing logとexpected/goldenを比較してpass/failを返す | Phase1必須 |
| `fixture_inspect` | fixture、chart、expectedの整合性を検査する補助tool | Phase1推奨 |

第5回以降のコマンド例は `taiko_play`、`headless_autoplay`、`timing_log_analyzer` を正とする。

## 4. Cargo workspace方針

Cargo workspaceを採用する。理由は、複数crateを単一lockfile、共通target、共通CIコマンドで管理し、domainとplatformの依存方向をCargo上でも分離できるためである。

Phase1のworkspace構成は次で固定する。`AGENTS.md` のcanonical crate/binary名を正とし、この文書はそれに従う。

```text
Cargo.toml
crates/
  taiko_domain/
  taiko_chart/
  taiko_timing/
  taiko_runtime/
  taiko_audio/
  taiko_render/
  taiko_test_support/
  taiko_cli/
fixtures/
  synthetic/
  user_selected/
docs/
prompts/
templates/
```

### 4.1 crate責務

| crate | 責務 | 性質 |
|---|---|---|
| `taiko_domain` | 共通型、time型、note型、branch型、judgement型、score/gauge/result型、compatibility report型 | pure |
| `taiko_chart` | `.tja` parse、metadata parse、course selection、command classification、Chart生成 | pure |
| `taiko_timing` | BPM/MEASURE/DELAY/OFFSET timeline、任意分割scheduler、rounding policy | pure |
| `taiko_runtime` | RuntimeState、step関数、judgement、branch evaluation、score/gauge update、headless autoplay injection、timing event生成 | pure優先 |
| `taiko_audio` | AudioBackend trait、cpal実装、silent/virtual audio、WAVE/PATH_WAV/OFFSET検証hook | adapter |
| `taiko_render` | RenderBackend trait、wgpu実装、visual-state projection、smoke描画 | adapter |
| `taiko_test_support` | fixture loader、manifest validation、golden comparison、timing log helper、user-song manifest validation helper | pure + I/O |
| `taiko_cli` | 統一CLI、config、run orchestration、subcommand、binary targets | I/O boundary |

### 4.2 binary配置

`taiko_cli` crateは、少なくとも次のbinary targetを提供する。

| binary | 実体 | 役割 |
|---|---|---|
| `taiko_cli` | unified command | fixture validation、headless autoplay、timing analysis、coverage report、gate support |
| `taiko_play` | playable/smoke entrypoint | 最小描画あり通常プレイとautoplay smoke |
| `headless_autoplay` | compatibility shim | `taiko_cli headless autoplay` と同じruntime経路を呼ぶ |
| `timing_log_analyzer` | compatibility shim | `taiko_cli timing analyze` と同じanalyzer経路を呼ぶ |

## 5. dependency方針

### 5.1 採用候補

Phase1では、次の外部crateを採用候補として固定する。実装開始時に `Cargo.lock` で正確なversionを固定する。

| 用途 | crate | 採用理由 |
|---|---|---|
| window/event loop | `winit` | cross-platform window creation/event loopを扱える。game loopではpoll型制御を使う |
| rendering | `wgpu` | cross-platformでsafeなpure Rust graphics APIを使える |
| low-level audio | `cpal` | output stream callback、device/config、stream timestampへアクセスできる |
| audio decode | `symphonia` | pure Rustのdecode/demux framework。WAV/OGG/FLAC/MP3等をfeatureで扱える |
| CLI | `clap` | CLI引数とhelpを構造化する |
| serialization | `serde`, `serde_json` | timing log、summary、expected/goldenをJSONで扱う |
| error | `thiserror`, `anyhow` | library errorとbinary boundary errorを分ける |
| logging | `tracing`, `tracing-subscriber` | structured logとspanを扱う |
| hashing | `blake3` | chart/audio/fixtureの安定hashを作る |
| test | `proptest`, `insta` | parser/property test、snapshot/golden補助 |

### 5.2 audio crateの決定

Phase1のaudio実装は、`rodio` ではなく `cpal + symphonia` を正とする。理由は、Phase1の重要課題が「音を鳴らすこと」だけではなく、audio callback、sample frame、device stream、callback timestampをtiming logへ出して検証することにあるためである。

`rodio` はsmoke用の簡易再生には向くが、Phase1本体のaudio sync検証では採用しない。

### 5.3 renderer crateの決定

描画は `winit + wgpu` を正とする。`winit` はwindow/event loopを担当し、`wgpu` は描画を担当する。Phase1ではスキンシステムを作らず、固定レーン、固定ノーツ形状、固定UI表示を描画する。

## 6. deterministic domain原則

`taiko_domain`、`taiko_chart`、`taiko_timing`、`taiko_runtime`、`taiko_test_support` の中心処理は、次を禁止する。

- `Instant::now()` の直接呼び出し
- audio deviceへの直接アクセス
- window/event loopへの直接アクセス
- thread sleepによる進行制御
- global mutable singleton
- random値の暗黙使用
- floating point比較による合否判定の直書き

runtimeへ渡す時刻、入力、audio位置はすべて外側から注入する。headless autoplayは、同じchart、同じconfig、同じseedless policyで常に同じtiming logを出す。

## 7. canonical time方針

Phase1のcanonical timeは `ChartTimeUs` とする。単位はmicrosecond整数である。

- `.tja` parse中のBPM計算では小数が発生するため、変換境界でrounding policyを1か所に閉じ込める。
- judgement、autoplay、miss確定、result、timing logは整数microsecondで扱う。
- rendererは表示座標計算に必要な箇所だけ `f32` / `f64` へ変換する。
- audio backendはsample frame countから `AudioTimeUs` を生成する。

`ChartTimeUs`、`AudioTimeUs`、`GameTimeUs` は別newtypeにする。型で混同を防ぐ。

## 8. runtime共有方針

描画あり実行とheadless実行は、同じ `RuntimeState::step(input)` を呼ぶ。

| 実行形態 | clock | audio | renderer | input | runtime |
|---|---|---|---|---|---|
| `taiko_play` | wall clock注入 | `CpalAudioBackend` | `WgpuRenderBackend` | `WinitInputBackend` | 共通 |
| `taiko_play --autoplay` | wall clock注入 | `CpalAudioBackend` | `WgpuRenderBackend` | `AutoplayPolicy` | 共通 |
| `headless_autoplay` | virtual clock | `VirtualAudioBackend` | `NullRenderer` | `AutoplayPolicy` | 共通 |
| analyzer test | log replay | なし | なし | log input | analyzer専用 |

この構成により、Phase1の合否はheadlessで高速判定し、描画あり実行では同じruntimeのplatform結合だけを確認する。

## 9. architecture上の禁止事項

実装Sessionは、次を行わない。

- renderer内で判定、score、gaugeを更新する。
- audio callback内でgame stateを直接更新する。
- input callback内で判定を直接実行する。
- `.tja` parserがruntime stateを直接変更する。
- headless専用runtimeを別実装する。
- log出力のためにruntime挙動を変える。
- CIを通すために判定窓、expected、goldenを実装Sessionが単独変更する。

## 10. Phase1完成時の上位コマンド

Step6時点の正規コマンド名は次である。

```bash
cargo fmt --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
cargo run --bin headless_autoplay -- --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --course oni --log target/timing/basic_single_bpm.jsonl --summary target/timing/basic_single_bpm.summary.json
cargo run --bin timing_log_analyzer -- --log target/timing/basic_single_bpm.jsonl --expect out/synthetic_analyzer.json
cargo run --bin taiko_play -- --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja --course oni --autoplay --quit-after-result
```

fixture名、manifest、analyzer profileは `docs/53_ci_commands.md`、`fixtures/synthetic/phase1_synthetic_manifest.toml`、各ticketを正とする。

## 11. 後続文書への接続

- `docs/31_module_boundaries.md`: crate/module依存方向と公開APIを固定する。
- `docs/32_data_model.md`: Rust型、ID、time型、result型を固定する。
- `docs/33_runtime_loop.md`: runtime phase、step順序、event順序を固定する。
- `docs/34_error_handling_and_logging.md`: error分類、exit code、logging、failure report連携を固定する。
- `docs/40_timing_model.md`: canonical timeとoffset適用順序を数式レベルで固定する。

---

## Step2 Amendment: OpenTaiko調査反映後の責務追加

Step2で、Phase1は単純な通常play loopではなく、OpenTaiko通常プレイ互換の中核機能を扱う方針に更新された。Architectureは次を正式責務として持つ。

| crate | Step2で追加された責務 |
|---|---|
| `taiko_chart` | TJA command分類、複数COURSE選択、BALLOON配列、branch body parse、compatibility report |
| `taiko_domain` | 任意分割scheduler、branch/scroll/score/gaugeのpure model |
| `taiko_runtime` | branch transition、GOGO state、BARLINE state、roll/balloon state、score/gauge update |
| `taiko_runtime` | deterministic autoplay、autoroll、balloon required hits充足、branch route検証 |
| `taiko_test_support` | branch coverage、scroll anomaly、score/gauge/clear検証補助 |
| `taiko_cli` | analyzer subcommand、fixture validation subcommand、coverage report subcommand |
| `taiko_audio` | WAVE/PATH_WAV/OFFSET解決、silent adapter、audio start log |

実装ticketは `research/opentaiko/10_phase1_adoption_decisions.md` を必読にする。

