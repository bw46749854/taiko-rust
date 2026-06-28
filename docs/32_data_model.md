# 32_data_model: Rust版Data Model定義

作成日: 2026-06-25
Status: canonical
上流文書: `docs/20_phase1_scope.md`, `docs/30_rust_architecture_overview.md`, `docs/31_module_boundaries.md`

## 1. 目的

この文書は、Rust版Phase1で使う主要データモデルを定義する。対象は `.tja` parse後のChart、runtime state、input、judgement、score、gauge、result、telemetryである。

Codex実装Sessionは、ここで定義した型名と責務を実装チケットの出発点にする。詳細なfield名は実装時に調整できるが、責務、ID、time型、状態遷移はこの文書に従う。

## 2. 型設計の原則

- time型はnewtypeで分ける。
- note、input、judgement、score eventは安定IDを持つ。
- runtimeで変更される状態と、chart由来の不変データを分ける。
- parser warningとunsupported errorを分ける。
- JSON出力される型は `serde` 互換にする。
- headlessと描画ありで同じ型を使う。

## 3. time型

Phase1ではmicrosecond整数を基準にする。

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ChartTimeUs(pub i64);

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct AudioTimeUs(pub i64);

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct GameTimeUs(pub i64);

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct DurationUs(pub i64);
```

### 3.1 time型の意味

| 型 | 意味 | 主な生成元 |
|---|---|---|
| `ChartTimeUs` | 譜面上の正規時刻 | parser/timing model/runtime |
| `AudioTimeUs` | audio backendが返す再生位置 | cpal sample cursor / virtual audio |
| `GameTimeUs` | runtime呼び出し側の経過時刻 | winit loop / virtual clock |
| `DurationUs` | 差分、判定窓、遅延 | config/parser |

### 3.2 変換規則

- `ChartTimeUs` と `AudioTimeUs` を暗黙加算しない。
- offset適用は `TimingContext` のmethodだけで行う。
- `f64` から `i64` へ変換する箇所は `round_to_nearest_us()` に集約する。
- renderer座標用のfloat変換は `RenderSnapshot` 生成以降に限定する。

## 4. 曲・譜面モデル

```rust
pub struct SongPackage {
    pub metadata: SongMetadata,
    pub audio: SongAudio,
    pub course: CourseChart,
    pub source: SourceInfo,
}

pub struct SongMetadata {
    pub title: String,
    pub subtitle: Option<String>,
    pub artist: Option<String>,
    pub genre: Option<String>,
    pub preview_start: Option<DurationUs>,
}

pub struct SongAudio {
    pub path: PathBuf,
    pub offset: DurationUs,
    pub volume: Option<f32>,
}

pub struct SourceInfo {
    pub chart_path: PathBuf,
    pub chart_hash: String,
    pub line_count: usize,
}
```

### 4.1 course model

```rust
pub struct CourseChart {
    pub id: CourseId,
    pub level: Option<u8>,
    pub score_config: ScoreConfig,
    pub timing_segments: Vec<TimingSegment>,
    pub notes: Vec<ChartNote>,
    pub barlines: Vec<BarlineEvent>,
    pub gogo_events: Vec<GogoEvent>,
    pub parse_warnings: Vec<ParseWarning>,
}

pub enum CourseId {
    Easy,
    Normal,
    Hard,
    Oni,
    Edit(String),
}
```

`CourseId::Dan` はPhase1非対応である。parserはDan courseを `UnsupportedFeature` として返す。

## 5. `.tja` timing model

```rust
pub struct TimingSegment {
    pub start_chart_time: ChartTimeUs,
    pub start_measure_index: u32,
    pub bpm: Bpm,
    pub measure: MeasureRatio,
    pub scroll: ScrollSpeed,
}

pub struct Bpm(pub f64);

pub struct MeasureRatio {
    pub numerator: u32,
    pub denominator: u32,
}

pub struct ScrollSpeed(pub f64);
```

### 5.1 ticks

OpenTaiko系譜面の小節解像度を踏まえ、Phase1 parser内部では `ticks_per_measure = 384` を採用する。note lineの文字数から小節内位置をtickへ変換し、BPMとMEASUREから `ChartTimeUs` を計算する。

```rust
pub struct ChartPosition {
    pub measure_index: u32,
    pub tick_in_measure: u32,
    pub ticks_per_measure: u32,
}
```

### 5.2 DELAY

`#DELAY` は以後の `ChartTimeUs` を進める譜面イベントとして扱う。note表示座標だけを動かす処理ではない。

## 6. note model

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct NoteId(pub u32);

pub struct ChartNote {
    pub id: NoteId,
    pub kind: NoteKind,
    pub start_time: ChartTimeUs,
    pub end_time: Option<ChartTimeUs>,
    pub source_position: ChartPosition,
    pub lane: NoteLane,
    pub required_hits: Option<u16>,
    pub scroll: ScrollSpeed,
    pub gogo: bool,
}

pub enum NoteKind {
    Don,
    Ka,
    BigDon,
    BigKa,
    Roll,
    BigRoll,
    Balloon,
}

pub enum NoteLane {
    Red,
    Blue,
    AnyRoll,
}
```

### 6.1 note ID

`NoteId` はparse順ではなく、`start_time`, `source_position`, `kind`, `source_line` を基準に安定採番する。golden log比較のため、同じchartから同じIDが生成される必要がある。

### 6.2 roll/balloon

- `Roll`、`BigRoll`、`Balloon` は `end_time` を必須にする。
- 対応する `8` が存在しないroll/balloonはparse errorにする。
- `Balloon` は `required_hits` を必須にする。
- 通常ノーツは `end_time = None` とする。

## 7. input model

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct InputEventId(pub u64);

pub struct InputEvent {
    pub id: InputEventId,
    pub game_time: GameTimeUs,
    pub chart_time: ChartTimeUs,
    pub kind: InputKind,
    pub source: InputSource,
}

pub enum InputKind {
    Red { hand: Hand },
    Blue { hand: Hand },
}

pub enum Hand {
    Left,
    Right,
    Unknown,
}

pub enum InputSource {
    Keyboard,
    Gamepad,
    Autoplay,
    Replay,
}
```

### 7.1 big input

Big Don/Big Kaのbig扱いは、`InputEvent` を直接 `BigRed` / `BigBlue` にしない。judgement側で同一判定窓内の左右同種入力を統合し、`HitStrength::Big` を生成する。

```rust
pub enum HitStrength {
    Normal,
    Big,
}
```

この方針により、keyboard/gamepad/autoplayが同じ判定処理を通る。

## 8. runtime state model

```rust
pub struct RuntimeState {
    pub package: SongPackage,
    pub config: RuntimeConfig,
    pub phase: PlayPhase,
    pub timing: TimingContext,
    pub notes: NoteRuntimeTable,
    pub score: ScoreState,
    pub gauge: GaugeState,
    pub combo: ComboState,
    pub result: Option<ResultSummary>,
}

pub enum PlayPhase {
    Loaded,
    Ready,
    Playing,
    Finishing,
    Result,
    Failed,
}
```

### 8.1 note runtime state

```rust
pub struct NoteRuntimeState {
    pub id: NoteId,
    pub hit_state: NoteHitState,
    pub first_hit_time: Option<ChartTimeUs>,
    pub last_hit_time: Option<ChartTimeUs>,
    pub roll_hits: u16,
    pub balloon_completed: bool,
}

pub enum NoteHitState {
    Waiting,
    Hit,
    Missed,
    ActiveRoll,
    RollEnded,
}
```

Chart由来の `ChartNote` は不変である。hit状態は `NoteRuntimeState` にだけ保持する。

## 9. judgement model

```rust
pub struct JudgementConfig {
    pub perfect_window: DurationUs,
    pub good_window: DurationUs,
    pub miss_window: DurationUs,
    pub big_pair_window: DurationUs,
}

pub struct JudgementAttempt {
    pub input_id: InputEventId,
    pub note_id: Option<NoteId>,
    pub delta: Option<DurationUs>,
    pub lane_match: bool,
    pub strength: HitStrength,
}

pub struct JudgementResult {
    pub input_id: Option<InputEventId>,
    pub note_id: NoteId,
    pub rank: JudgementRank,
    pub delta: DurationUs,
    pub early_late: EarlyLate,
    pub chart_time: ChartTimeUs,
}

pub enum EarlyLate {
    Early,
    Late,
    Exact,
}
```

### 9.1 判定窓

判定窓の初期値はTiming / Audio / Judgement検証設計で固定する。Rustアーキテクチャ方針では、値がconfig/testから注入できる構造を固定する。

## 10. score / combo / gauge model

```rust
pub struct ScoreConfig {
    pub score_init: i32,
    pub score_diff: i32,
    pub perfect_points: i32,
    pub good_points: i32,
    pub roll_points: i32,
    pub balloon_success_points: i32,
    pub gogo_multiplier_permille: u16,
}

pub struct ScoreState {
    pub total_score: i64,
    pub perfect_count: u32,
    pub good_count: u32,
    pub miss_count: u32,
    pub roll_count: u32,
    pub balloon_success_count: u32,
    pub balloon_failure_count: u32,
}

pub struct ComboState {
    pub current: u32,
    pub max: u32,
}

pub struct GaugeConfig {
    pub perfect_gain: f32,
    pub good_gain: f32,
    pub miss_loss: f32,
    pub clear_threshold: f32,
}

pub struct GaugeState {
    pub value: f32,
}
```

### 10.1 scoreの固定範囲

Phase1ではOpenTaikoの全スコア世代を再現しない。`SCOREINIT` と `SCOREDIFF` は読み込み、Phase1標準スコアモデルの入力にする。点数式の最終値はTiming / Audio / Judgement検証設計/テストハーネス・回帰検証設計のfixtureで固定する。

## 11. render snapshot model

rendererへ渡すのは、runtime stateそのものではなく `RenderSnapshot` である。

```rust
pub struct RenderSnapshot {
    pub chart_time: ChartTimeUs,
    pub phase: PlayPhase,
    pub notes: Vec<RenderNote>,
    pub judgement_effects: Vec<RenderJudgementEffect>,
    pub score: ScoreView,
    pub gauge: GaugeView,
    pub result: Option<ResultSummary>,
}

pub struct RenderNote {
    pub note_id: NoteId,
    pub kind: NoteKind,
    pub x: f32,
    pub y: f32,
    pub visible: bool,
    pub active: bool,
}
```

RenderSnapshot生成はruntime側で行う。rendererは描画だけを行う。

## 12. telemetry model

```rust
#[serde(tag = "event", rename_all = "snake_case")]
pub enum TelemetryEvent {
    RunStarted(RunStartedEvent),
    ChartLoaded(ChartLoadedEvent),
    AudioStarted(AudioStartedEvent),
    Frame(FrameEvent),
    Input(InputTelemetryEvent),
    Judgement(JudgementTelemetryEvent),
    ScoreChanged(ScoreChangedEvent),
    GaugeChanged(GaugeChangedEvent),
    NoteMissed(NoteMissedEvent),
    RunFinished(RunFinishedEvent),
    Error(ErrorTelemetryEvent),
}
```

### 12.1 必須共通field

すべてのtiming log eventは次を持つ。

```rust
pub struct TelemetryCommon {
    pub run_id: String,
    pub seq: u64,
    pub game_time: GameTimeUs,
    pub chart_time: ChartTimeUs,
    pub audio_time: Option<AudioTimeUs>,
}
```

### 12.2 JSON表現

- JSONL 1行1event。
- `seq` は単調増加。
- `run_id` は1実行で固定。
- `chart_hash` と `fixture_id` は `run_started` に入れる。
- analyzerは未知fieldを無視してよいが、必須field欠落はfailにする。

## 13. result model

```rust
pub struct ResultSummary {
    pub song_title: String,
    pub course: CourseId,
    pub level: Option<u8>,
    pub score: i64,
    pub max_combo: u32,
    pub perfect_count: u32,
    pub good_count: u32,
    pub miss_count: u32,
    pub roll_count: u32,
    pub balloon_success_count: u32,
    pub balloon_failure_count: u32,
    pub gauge_final: f32,
    pub clear_status: ClearStatus,
    pub autoplay: bool,
    pub timing_log_path: Option<PathBuf>,
    pub analyzer_summary_path: Option<PathBuf>,
}

pub enum ClearStatus {
    Clear,
    Failed,
}
```

ResultSummaryは画面表示より優先されるPhase1の正本である。

## 14. error modelとの接続

データモデルは、parse不能とunsupportedを分ける。

```rust
pub enum ParseFailureKind {
    Syntax,
    MissingRequiredHeader,
    InvalidValue,
    UnsupportedFeature,
    InconsistentRollRange,
}
```

- 構文不正は `Syntax`。
- Phase1非対応command/noteは `UnsupportedFeature`。
- header欠落は `MissingRequiredHeader`。
- roll終端欠落は `InconsistentRollRange`。

## 15. 実装チケット化の単位

Data model実装は次のチケットへ分割する。

| ticket候補 | 対象 |
|---|---|
| `DM-001` | time newtypeと変換utility |
| `DM-002` | song/chart/note model |
| `DM-003` | input/judgement model |
| `DM-004` | score/gauge/result model |
| `DM-005` | telemetry event model |
| `DM-006` | error model基礎 |

各チケットは単体テストを持つ。serde対象型はsnapshot testを持つ。

---

## OpenTaiko compatibility data model

Phase1 domain modelに次を追加する。

```text
ChartMetadata
CourseMetadata
BpmPoint
MeasureEvent
DelayEvent
ScrollEvent
ScrollModeEvent
BranchStartEvent
BranchRouteBody
BranchEndEvent
GogoStateEvent
BarlineEvent
NoteEvent
RollLikeEvent
BalloonCounts
ScoreConfig
GaugeConfig
CompatibilityReport
```

`NoteEvent` は `token_count_in_measure` と `token_index_in_measure` を保持する。n分音符は個別enumではなく、任意分割schedulerの結果として表現する。

`CompatibilityReport` は、Must parse / must not crash と Explicit non-scope with report の両方を記録する。

