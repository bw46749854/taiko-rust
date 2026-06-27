# 40_timing_model: Timingモデル

作成日: 2026-06-25  
状態: 第5回ドラフト・採用候補  
上流文書: `docs/30_rust_architecture_overview.md`, `docs/31_module_boundaries.md`, `docs/32_data_model.md`, `docs/33_runtime_loop.md`, `docs/34_error_handling_and_logging.md`

## 1. 目的

この文書は、Rust版Phase1の時刻モデルを固定する。対象は `.tja` から生成される譜面時刻、runtime stepで使用するgame time、audio callbackから得るaudio time、rendererで使うdisplay timeである。

Phase1で最も避けるべき失敗は、実装が進むほど「音ズレの原因が不明になる」ことである。そのため、時刻は次の原則で扱う。

- canonicalな譜面時刻は整数microsecondで表す。
- `.tja`の小数BPM、OFFSET、DELAY、SCROLL計算は1か所で正規化する。
- runtimeは外部clockを直接読まない。
- audio timeとgame timeの差分を全runで記録する。
- judgementはchart time基準で実行し、render frame基準では実行しない。
- headless autoplayはbit-levelで再現可能なtiming logを出す。

## 2. 用語

| 用語 | 型名 | 説明 |
|---|---|---|
| Chart time | `ChartTimeUs` | 譜面上の発声・判定基準時刻。microsecond整数 |
| Game time | `GameTimeUs` | runtimeが現在処理している進行時刻。pauseやseekの制御後の時刻 |
| Audio time | `AudioTimeUs` | audio backendが報告する再生位置。sample frameから導出する |
| Wall time | `WallTimeUs` | OSのmonotonic clock由来の外部時刻。domainには入れない |
| Frame time | `FrameTimeUs` | renderer更新時の表示用時刻。判定には使わない |
| Judgement delta | `DeltaUs` | input時刻 - note時刻。負値は早押し、正値は遅押し |
| Sync delta | `SyncDeltaUs` | game time - audio time。正値はgameがaudioより進んでいる |

## 3. 正規newtype

`taiko_domain::time` に次を置く。

```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct ChartTimeUs(pub i64);

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct GameTimeUs(pub i64);

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct AudioTimeUs(pub i64);

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct DeltaUs(pub i64);
```

`i64`を採用する。`.tja`の負OFFSET、曲開始前ノーツ、pre-roll、debug replayを表せるためである。Phase1で扱う実時間は数分程度だが、型としては長尺譜面に耐える。

## 4. 時刻の責務分離

| 処理 | 入力時刻 | 出力時刻 | 所属crate |
|---|---|---|---|
| `.tja` parse | BPM, MEASURE, OFFSET, DELAY | `ChartTimeUs` | `taiko_chart` |
| runtime step | `GameTimeUs` | due events | `taiko_runtime` |
| input normalize | backend event time | `GameTimeUs` | `taiko_cli` input adapter + `taiko_runtime` |
| judgement | `GameTimeUs`, `ChartTimeUs` | `DeltaUs`, `JudgeKind` | `taiko_runtime` |
| audio progress | sample frame count | `AudioTimeUs` | `taiko_audio` |
| render position | `GameTimeUs`, `ChartTimeUs` | x/y/fade | `taiko_render` |
| telemetry | all above | JSONL | `taiko_runtime telemetry + taiko_test_support writer` |

rendererは見た目の補間を担当する。renderer内でnote hit、miss確定、score、gaugeを変更しない。

audio callbackはsample frameの進行を報告する。audio callback内でruntime stateを変更しない。

input backendは入力を収集する。input callback内で判定を直接実行しない。

## 5. `.tja`からChartTimeへの変換

### 5.1 小節解像度

Phase1では、内部表現をtickではなくmicrosecond event listに正規化する。ただしparser内部では、OpenTaikoが持つ小節解像度384に相当する基準を参考値として扱う。

正規化後のChartは次を持つ。

```rust
pub struct Chart {
    pub metadata: ChartMetadata,
    pub course: Course,
    pub timing_map: TimingMap,
    pub notes: Vec<Note>,
    pub barlines: Vec<Barline>,
    pub unsupported: Vec<UnsupportedFeature>,
}
```

### 5.2 BPM区間

`TimingMap` はBPM変更、MEASURE、DELAY、OFFSETを反映した結果を持つ。runtimeは `.tja` 命令を再解釈しない。

```rust
pub struct TimingSegment {
    pub start_measure_index: u32,
    pub start_position_in_measure: Rational32,
    pub start_chart_time_us: ChartTimeUs,
    pub bpm: Bpm,
    pub measure_numerator: u32,
    pub measure_denominator: u32,
    pub scroll: ScrollSpeed,
}
```

BPMは `f64` でparseし、ChartTime確定時にmicrosecondへ丸める。丸め規則は `round_half_away_from_zero` を正とする。丸め規則は `taiko_chart::time_math` の1か所に閉じ込める。

### 5.3 NOTE時刻算出

1小節中のnote列は、カンマまでの文字数で等分する。

```text
note_time = measure_start_time
          + measure_duration_us * note_index / note_slots
```

`note_slots` は、その小節でカンマ前に存在するnote文字列のslot数である。`0` は空slotとして扱う。`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8` はPhase1対象である。Phase1では `A`, `B`, `C`, `D`, `F`, `G`, `H`, `I` をunsupportedまたはnon-scopeとして記録する。

### 5.4 OFFSET

Phase1では `OFFSET` を譜面時刻からaudio開始への補正として扱う。正規定義は次とする。

```text
audible_note_time = chart_note_time + chart_global_offset
```

ただしruntime上の判定基準は `ChartTimeUs` で保持し、audio sync計算時にoffset補正済みの対応関係を使う。parser、runtime、audioがそれぞれ独自にoffsetを足し引きしない。

`OFFSET`の符号仕様はOpenTaiko調査で最終確認する。Phase1実装では、fixtureに正OFFSET/負OFFSETを両方入れ、expected event listで固定する。

### 5.5 DELAY

`#DELAY` は以降のnote発声時刻を後ろへずらす命令として扱う。Phase1ではDELAY中にruntime pauseを入れない。parserがChartTimeを確定し、runtimeは確定済みevent listを処理する。

### 5.6 SCROLL

`#SCROLL` は表示位置計算へ影響する。Phase1のjudgement時刻へは影響させない。timing logにはnoteのscroll値を出すが、analyzerはjudgement timingとは別に表示検証として扱う。

## 6. RuntimeStepの時刻入力

runtimeは毎tick次の入力を受け取る。

```rust
pub struct RuntimeStepInput {
    pub game_time_us: GameTimeUs,
    pub audio_time_us: Option<AudioTimeUs>,
    pub frame_index: u64,
    pub input_events: Vec<InputEvent>,
}
```

`game_time_us` は必須である。`audio_time_us` は描画あり/実audio時に記録する。headless virtualでは `audio_time_us = Some(game_time_us.into_audio_time())` とし、drift 0を期待値にする。

## 7. due event処理順序

同じstep内で処理する順序を固定する。

1. clock snapshotを受け取る。
2. input eventをgame timeへ正規化する。
3. 未処理noteのmiss deadlineを処理する。
4. input eventごとにnearest hittable noteを検索する。
5. judgement eventを生成する。
6. roll/balloon進行を更新する。
7. score/gauge/resultを更新する。
8. telemetry eventを出力する。
9. render snapshotを生成する。

同時刻のnoteは、`note_id` の昇順で処理する。`note_id` はparserが安定生成する。

## 8. monotonicity要件

runtimeに渡す `game_time_us` は単調非減少でなければならない。

- 同一時刻stepは許可する。
- 逆行は通常プレイではerrorにする。
- training/seekはPhase1非対象である。
- headless replayで逆行が必要になった場合は、runtime再生成で対応する。

analyzerは `runtime_step` eventの `game_time_us` が単調非減少であることを検査する。

## 9. clock実装

### 9.1 Headless clock

`HeadlessClock` は固定tickで進む。

```text
headless_tick_us = 1000
```

1ms tickを標準にする。判定境界テストではtick列ではなく、input eventのtimestampを直接与えるため、tick粗さによる境界誤差を許さない。

### 9.2 Real-time clock

`RealTimeClock` は `Instant` をapp層で読む。domain/runtimeへ `Instant` を渡さない。

```text
game_time_us = monotonic_elapsed_us - paused_duration_us + start_offset_us
```

Phase1ではpauseを非対象にするため、`paused_duration_us = 0` で実装する。

### 9.3 Audio clock

`AudioClock` は、audio stream開始時のsample frameを0とし、callbackで消費したframe数から時刻を計算する。

```text
audio_time_us = frames_rendered * 1_000_000 / sample_rate
```

device timestampを利用できる場合はtelemetryへ併記する。canonical audio timeはframe count由来とする。

## 10. drift補正方針

Phase1では、runtime時刻をaudioへ追従させる可変補正を実装しない。補正ロジックはズレの原因を隠すため、Phase1では検証対象外にする。

Phase1の通常実行では次を行う。

- game clockを単調に進める。
- audio timeを観測する。
- `sync_delta_us = game_time_us - audio_time_us` を記録する。
- analyzer/local smokeでdriftを検出する。
- driftが閾値超過したら不合格にする。

## 11. Timing gate

### 11.1 CI gate

CIで必須にするgateはheadlessのみである。

| Gate | 合格条件 |
|---|---|
| deterministic replay | 同一fixtureを2回実行し、JSONLのsemantic hashが一致する |
| note schedule | expected note timeとの差が全noteで0us |
| judgement boundary | 境界fixtureのJudgeKindがexpectedと一致する |
| autoplay delta | autoplay hitのdeltaが全tap noteで0us |
| monotonic clock | runtime step, note events, judgement eventsが順序制約を満たす |

### 11.2 Local audio gate

開発環境で実施するgateを次に固定する。

| 指標 | 合格条件 |
|---|---:|
| sync delta median abs | `<= 2_000us` |
| sync delta p95 abs | `<= 5_000us` |
| sync delta max abs | `<= 12_000us` |
| audio underrun count | `0` |
| missing audio timestamp ratio | `<= 1%` |

local audio gateはCI必須にしない。ハードウェア依存であるためである。実装Sessionはlocal audio gateに失敗した場合、timing logとsummaryを添えてQA/回帰検証Sessionへ渡す。

## 12. 禁止事項

- 判定をrender frame到達時に実行する。
- audio callback内でscore/gaugeを更新する。
- driftを隠すためにruntime時刻を無言で補正する。
- fixture expectedを実装Sessionが単独更新する。
- `f32` のnote timeを正とする。
- JSONL出力順をthread raceに依存させる。
- headlessと描画ありで別runtimeを使う。

## 13. Codex実装指示用メモ

Codexには次の順序で実装させる。

1. `taiko_domain::time` newtypeを作る。
2. `.tja`の最小note scheduleを `ChartTimeUs` で出す。
3. headless clockを作る。
4. runtime stepの時刻注入を作る。
5. timing logへ `runtime_step`, `note_scheduled`, `judgement` を出す。
6. analyzerでmonotonicityとexpected一致を検査する。
7. audio clockを追加し、`audio_sample` eventを出す。

---

## Step2 Amendment: 任意分割schedulerの正式採用

4分、8分、12分、16分、24分、36分は個別実装しない。小節内のnote token数を任意分割として扱う。

```text
measure_duration_ms = 240000.0 / bpm * measure_numerator / measure_denominator
note_time_ms = measure_start_ms + measure_duration_ms * token_index / token_count
```

`#MEASURE`, `#BPMCHANGE`, `#DELAY`, `OFFSET` はschedulerの中核入力である。tick/beatは有理数で保持し、msはlogとadapter境界で使う。

