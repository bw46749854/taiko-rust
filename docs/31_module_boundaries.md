# 31_module_boundaries: Module境界定義

作成日: 2026-06-25  
状態: 第4回ドラフト・採用候補  
上流文書: `docs/30_rust_architecture_overview.md`

## 1. 目的

この文書は、Rust版Phase1のcrate/module境界、依存方向、公開API、禁止依存を定義する。Codex実装Sessionは、この境界を越えて責務を混ぜない。

## 2. 境界設計の原則

- domain logicはplatformへ依存しない。
- parser、judgement、score、gauge、runtime stepは単体テスト可能にする。
- adapterはtrait越しにruntimeへ値を渡す。
- `taiko_play` と `headless_autoplay` は同じruntime crateを使う。
- telemetryは観測であり、runtimeの結果を変えない。

## 3. 依存方向

正しい依存方向は次である。

```text
binaries
  -> taiko_cli
       -> taiko_runtime
            -> taiko_timing
            -> taiko_chart
            -> taiko_domain
       -> taiko_audio
       -> taiko_render
       -> taiko_test_support

pure crates:
  taiko_domain <- taiko_chart <- taiko_timing <- taiko_runtime
  taiko_test_support -> taiko_domain / taiko_chart / taiko_timing / taiko_runtime
```

禁止依存は次である。

| from | must not depend on | 理由 |
|---|---|---|
| `taiko_domain` | すべての外部adapter | domain純度維持 |
| `taiko_chart` | `taiko_runtime`, audio/render/input | parseを副作用から分離 |
| `taiko_runtime` | winit, wgpu, cpal, symphonia直接 | headlessと描画ありのruntime共有 |
| `taiko_audio` | `taiko_render` | adapter間結合の排除 |
| `taiko_render` | judgement/score更新処理 | 描画によるゲーム状態変更の禁止 |
| `taiko_cli` input adapter module | judgement/score更新処理 | 入力正規化と判定の分離 |
| `taiko_test_support` | window/audio device | CI/headlessで実行可能にする |

## 4. `taiko_domain`

### 4.1 責務

- 共通newtype
- note kind
- input kind
- judgement rank
- score/gauge/result型
- timing/log event型のdomain側表現
- error enumの基礎型

### 4.2 公開API候補

```rust
pub struct ChartTimeUs(pub i64);
pub struct AudioTimeUs(pub i64);
pub struct GameTimeUs(pub i64);
pub struct DurationUs(pub i64);

pub enum NoteKind {
    Don,
    Ka,
    BigDon,
    BigKa,
    Roll,
    BigRoll,
    Balloon,
}

pub enum InputKind {
    Red { hand: Hand },
    Blue { hand: Hand },
}

pub enum JudgementRank {
    Perfect,
    Good,
    Miss,
}
```

### 4.3 禁止事項

- file pathを直接読む。
- wall clockを読む。
- serde実装以外のI/Oを持つ。

## 5. `taiko_chart`

### 5.1 責務

- `.tja` textをparseする。
- header、command、note lineをdomain modelへ変換する。
- unsupported featureを明示errorへ変換する。
- chart hashとsource locationを保持する。
- parse warningを収集する。

### 5.2 入力と出力

```rust
pub struct ParseRequest {
    pub source_path: PathBuf,
    pub text: String,
    pub selected_course: CourseId,
    pub policy: ParsePolicy,
}

pub struct ParseOutput {
    pub package: SongPackage,
    pub warnings: Vec<ParseWarning>,
}
```

### 5.3 依存可能crate

- `taiko_domain`
- `serde` 系
- `thiserror`
- parser補助crate

### 5.4 禁止事項

- 音声ファイルをdecodeしない。
- runtime stateを作らない。
- unsupported commandを無視して成功扱いにしない。

## 6. `taiko_runtime`

### 6.1 責務

- `RuntimeState` を保持する。
- `RuntimeStepInput` を受け取り、`RuntimeStepOutput` を返す。
- autoplay policyを同じstep経路へ注入する。
- miss確定、hit判定、roll/balloon更新、score/gauge/result更新を順序立てる。
- render snapshotとtelemetry eventを生成する。

### 6.2 公開API候補

```rust
pub struct RuntimeConfig {
    pub judgement: JudgementConfig,
    pub score: ScoreConfig,
    pub gauge: GaugeConfig,
    pub autoplay: AutoplayConfig,
}

pub struct RuntimeStepInput {
    pub game_time: GameTimeUs,
    pub audio_time: AudioTimeUs,
    pub raw_inputs: Vec<InputEvent>,
}

pub struct RuntimeStepOutput {
    pub phase: PlayPhase,
    pub render_snapshot: RenderSnapshot,
    pub telemetry_events: Vec<TelemetryEvent>,
    pub result: Option<ResultSummary>,
}

impl RuntimeState {
    pub fn new(package: SongPackage, config: RuntimeConfig) -> Result<Self, RuntimeError>;
    pub fn step(&mut self, input: RuntimeStepInput) -> Result<RuntimeStepOutput, RuntimeError>;
}
```

### 6.3 禁止事項

- `Instant::now()` を呼ばない。
- audio deviceへ触れない。
- renderer APIへ触れない。
- input deviceへ触れない。
- `println!` で検証用ログを直接出さない。

## 7. `taiko_audio`

### 7.1 責務

- 音源decodeとplaybackを扱う。
- `AudioBackend` traitを提供する。
- `CpalAudioBackend` と `VirtualAudioBackend` を実装する。
- sample frameから `AudioTimeUs` を生成する。
- audio underrun、device error、decode errorをtelemetryへ出せる形で返す。

### 7.2 trait候補

```rust
pub trait AudioBackend {
    fn prepare(&mut self, request: AudioPrepareRequest) -> Result<AudioPrepared, AudioError>;
    fn start(&mut self, at_game_time: GameTimeUs) -> Result<(), AudioError>;
    fn pause(&mut self) -> Result<(), AudioError>;
    fn stop(&mut self) -> Result<(), AudioError>;
    fn position(&self) -> AudioTimeUs;
    fn state(&self) -> AudioPlaybackState;
}
```

### 7.3 実装境界

- `CpalAudioBackend` はdevice、stream、callback、sample cursorを保持する。
- `VirtualAudioBackend` はheadless用に、注入されたvirtual clockからpositionを返す。
- decodeは `symphonia` を使い、runtimeへはPCM buffer/stream抽象だけを渡す。

## 8. `taiko_render`

### 8.1 責務

- `RenderSnapshot` を描画する。
- window/surface/device/pipeline/textureを管理する。
- renderer状態はgame stateの派生に限定する。

### 8.2 trait候補

```rust
pub trait RenderBackend {
    fn resize(&mut self, width: u32, height: u32) -> Result<(), RenderError>;
    fn render(&mut self, snapshot: &RenderSnapshot) -> Result<RenderStats, RenderError>;
}
```

### 8.3 禁止事項

- note hit状態を変更しない。
- score/gaugeを更新しない。
- chart timeを進めない。
- telemetry logへdomain eventを追加しない。render statsだけ返す。

## 9. `taiko_cli` input adapter module

### 9.1 責務

- platform eventを `InputEvent` へ変換する。
- 1P Red/Blue/handを正規化する。
- key repeat、press/release、focus lossを処理する。
- headless入力とautoplay入力を同じ型で扱えるようにする。

### 9.2 trait候補

```rust
pub trait InputBackend {
    fn drain_events(&mut self, now: GameTimeUs) -> Vec<InputEvent>;
}
```

### 9.3 禁止事項

- 判定候補ノーツを検索しない。
- combo/score/gaugeを変更しない。
- keyboard layout依存の文字判定をdomainへ漏らさない。

## 10. `taiko_runtime` telemetry event model

### 10.1 責務

- timing log JSONLを書き出す。
- summary JSONを書き出す。
- run metadata、chart hash、fixture idを管理する。
- trace logとtiming logを分離する。

### 10.2 出力

| 出力 | 形式 | 用途 |
|---|---|---|
| timing log | JSONL | analyzer入力 |
| summary | JSON | headless/CI結果 |
| trace log | text or JSON | failure調査 |
| result | JSON | Phase1リザルト正本 |

## 11. `taiko_cli`

### 11.1 責務

- CLI引数を読む。
- configを読む。
- chart/audio/fixtureを解決する。
- runtime、audio、renderer、input、telemetryを組み立てる。
- exit codeを返す。

### 11.2 禁止事項

- parserの仕様分岐をここに書かない。
- judgement窓をここで直接計算しない。
- analyzer expectedを勝手に更新しない。

## 12. `taiko_test_support`

### 12.1 責務

- timing log analyzer
- fixture integrity check
- golden/expected差分表示
- CI補助

### 12.2 analyzer API候補

```rust
pub struct AnalyzeRequest {
    pub log_path: PathBuf,
    pub expect_path: PathBuf,
    pub policy: AnalyzePolicy,
}

pub struct AnalyzeReport {
    pub status: AnalyzeStatus,
    pub failures: Vec<AnalyzeFailure>,
    pub metrics: AnalyzeMetrics,
}
```

## 13. review観点

設計レビューSessionは、PRまたはチケットPlanに対して次を確認する。

- 変更対象crateがこの文書の責務に一致している。
- pure crateへplatform依存が入っていない。
- runtime stepが描画あり/headlessで共有されている。
- telemetryがruntime結果を変えていない。
- unsupported featureを黙って無視していない。
- errorが適切な分類とexit codeに接続されている。

---

## Step2 Amendment: crate境界の確定

Step2以降は `taiko_domain` をpure domain crateの正本名にする。旧文書に残る `taiko_core` は採用しない。

| crate | 許可する依存 | 禁止する依存 |
|---|---|---|
| `taiko_domain` | 標準library、deterministic math | audio, renderer, filesystem, wall clock |
| `taiko_chart` | `taiko_domain` | renderer, real audio playback |
| `taiko_runtime` | `taiko_domain`, `taiko_chart`, `taiko_timing` | OpenTaiko source direct dependency |
| `taiko_audio` | `taiko_domain`のaudio metadata | gameplay ruleへの逆依存 |
| `taiko_runtime` | renderer mandatory dependency | deterministic headless must not require renderer |
| `taiko_test_support` | timing log schema | runtime mutable stateへの直接依存 |
| `taiko_cli` | 各crateのpublic API | private module参照 |

`research/opentaiko/` は実装根拠であり、Rust crateから参照する実行時依存ではない。

