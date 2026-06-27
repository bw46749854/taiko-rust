# 33_runtime_loop: Runtime Loop定義

作成日: 2026-06-25  
状態: 第4回ドラフト・採用候補  
上流文書: `docs/30_rust_architecture_overview.md`, `docs/31_module_boundaries.md`, `docs/32_data_model.md`

## 1. 目的

この文書は、Phase1通常プレイのruntime loop、event順序、描画あり実行、headless autoplay、audio同期の接続を定義する。

最重要方針は、`taiko_play` と `headless_autoplay` が同じ `RuntimeState::step()` を使うことである。違いは、clock、audio backend、renderer、input sourceだけに限定する。

## 2. runtime phases

```rust
pub enum PlayPhase {
    Loaded,
    Ready,
    Playing,
    Finishing,
    Result,
    Failed,
}
```

| Phase | 意味 | 遷移条件 |
|---|---|---|
| `Loaded` | chart/audio/configを読み込んだ | runtime初期化完了 |
| `Ready` | 開始可能 | autostartまたはstart command |
| `Playing` | chart進行中 | audio start完了 |
| `Finishing` | 最終ノーツ後の終了猶予 | chart endまたはaudio end候補到達 |
| `Result` | リザルト確定 | result summary生成 |
| `Failed` | 継続不能error | fatal error |

Phase1ではゲーム内pause、training、branch、retry UIを実装しない。

## 3. step input / output

```rust
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
```

`RuntimeState::step()` は、入力された時刻とinput eventだけで結果を決める。runtime内部でwall clockを読まない。

## 4. chart time更新

`TimingContext` は `audio_time`、`game_time`、`offset`、実行モードから `current_chart_time` を作る。

### 4.1 描画あり通常実行

描画あり通常実行では、audio再生開始後の基準はaudio timeである。

```text
current_chart_time = audio_time + configured_offset + runtime_start_alignment
```

`game_time` はframe delta、input timestamp、telemetry、audio未開始期間の進行管理に使う。

### 4.2 headless autoplay

headlessではvirtual audio clockを使う。

```text
virtual_audio_time = virtual_game_time - virtual_audio_start_game_time
current_chart_time = virtual_audio_time + configured_offset
```

この構成により、headlessでもaudio基準のruntime経路を通る。

## 5. step処理順序

`RuntimeState::step()` は次の順序で実行する。

1. `RuntimeStepInput` の時刻単調性を検証する。
2. `TimingContext` を更新し、`current_chart_time` を決める。
3. autoplay有効時は、対象ノーツから `InputEvent` を生成して `raw_inputs` へ統合する。
4. input eventを `chart_time`, `id` 順にsortする。
5. 通常ノーツhit判定を処理する。
6. roll/balloon区間内入力を処理する。
7. `current_chart_time - miss_window` を超えた未hit通常ノーツをMissにする。
8. 終了済みroll/balloonを確定する。
9. score/combo/gauge/result候補を更新する。
10. telemetry eventを生成する。
11. render snapshotを生成する。
12. phase遷移を評価する。

## 6. hit判定順序

通常ノーツの判定は、入力ごとに最も近い未hit対象ノーツを選ぶ。

### 6.1 候補条件

- note kindとinput laneが一致する。
- noteは `Waiting` である。
- `abs(input.chart_time - note.start_time) <= miss_window` である。
- 同一入力を複数ノーツへ使わない。

### 6.2 rank決定

```text
abs_delta <= perfect_window => Perfect
abs_delta <= good_window    => Good
otherwise                   => Miss attempt, noteは未hitのまま
```

Miss attemptはtiming logへ残す。noteそのもののMiss確定は、note start time + miss windowを過ぎた時点で行う。

### 6.3 big判定

Big Don/Big Kaは、同一noteに対し、左右同種入力が `big_pair_window` 内に揃った時に `HitStrength::Big` とする。片手入力だけでもhit可能にするが、Phase1標準スコアではbig bonusの有無をeventへ記録する。

## 7. roll / balloon処理

### 7.1 roll

- `start_time <= input.chart_time <= end_time` の入力をroll hitとして数える。
- laneはRed/Blueどちらも許可する。
- roll hitはcomboを増やさない。
- roll hitは固定点を加算する。
- roll区間終了で `RollEnded` にする。

### 7.2 balloon

- `start_time <= input.chart_time <= end_time` の入力をballoon hitとして数える。
- `required_hits` 以上になった時点で成功扱いにする。
- 成功後の追加入力はscore対象にしない。
- end_time到達時点で未達の場合はballoon failureにする。

## 8. score / gauge更新順序

score、combo、gaugeはjudgement resultから更新する。rendererやinput backendは直接更新しない。

```text
JudgementResult
  -> ScoreEvent
  -> ComboEvent
  -> GaugeEvent
  -> TelemetryEvent
```

通常ノーツ:

- `Perfect` と `Good` はcomboを増やす。
- `Miss` はcomboを0へ戻す。
- gaugeはrank別に更新する。

Roll/Balloon:

- roll hitはscoreへ加算する。
- roll hitはcomboを増やさない。
- balloon成功/失敗はresult countへ反映する。

## 9. phase終了条件

Phase1では、曲終了の判定候補を次の順序で扱う。

1. chart上の最後のnote/roll end/barline/gogo event時刻。
2. audio backendの再生終了。
3. 明示 `#END` に由来するchart end marker。

`Finishing` へ入った後、次を満たした時点で `Result` へ遷移する。

- 未処理noteがない。
- active roll/balloonがない。
- audioがended、またはchart endから設定済み猶予時間を超えた。

終了猶予時間の初期値は第5回で固定する。第4回ではconfig化だけを要求する。

## 10. 描画ありloop

`taiko_play` は、window event loop、audio backend、input backend、rendererを組み合わせる。

```text
Application resumed
  -> create window
  -> create renderer
  -> parse chart
  -> prepare audio
  -> create RuntimeState
  -> phase Ready

Each frame / redraw
  -> collect input events
  -> sample game_time
  -> sample audio_time
  -> runtime.step(...)
  -> write telemetry
  -> render(snapshot)
  -> request next redraw while phase != Result
```

描画ありloopでは、render失敗、surface lost、audio device lostをerror handlingへ送る。runtime stateをrenderer再生成のために巻き戻さない。

## 11. headless autoplay loop

`headless_autoplay` は、window、real audio、keyboardを使わない。

```text
parse chart
create RuntimeState with autoplay enabled
create VirtualAudioBackend
for virtual_time in deterministic ticks:
    audio_time = virtual_audio.position(virtual_time)
    output = runtime.step(RuntimeStepInput {
        game_time: virtual_time,
        audio_time,
        raw_inputs: []
    })
    write telemetry
    stop when output.phase == Result or Failed
write summary
```

### 11.1 headless tick

headless tickは固定intervalで進める。初期値は `1 ms` とする。第5回で、密集譜面と境界判定を確認して確定する。

Autoplay inputの時刻はtick時刻ではなく、対象ノーツの `ChartTimeUs` そのものにする。これにより、headless tick粒度でPerfectがずれない。

## 12. autoplay policy

```rust
pub struct AutoplayPolicy {
    pub enabled: bool,
    pub hit_rank: AutoplayHitRank,
    pub roll_rate_hz: u16,
}

pub enum AutoplayHitRank {
    Perfect,
}
```

Phase1のautoplayはPerfect固定にする。Good/Missを作る疑似AIはPhase1非対象である。

### 12.1 通常ノーツ

- note kindに応じてRed/Blue入力をnote時刻に生成する。
- Big noteは左右同種入力を同時刻またはbig_pair_window内で生成する。

### 12.2 roll/balloon

- rollは `roll_rate_hz` に従って入力を生成する。
- balloonはrequired hitsを満たす入力数を区間内に生成する。
- 生成不能な短区間balloonはanalyzer fail対象にする。

## 13. telemetry出力順序

1 step内のevent順序は次で固定する。

1. frame/sample event
2. input event
3. judgement event
4. score/gauge event
5. miss event
6. phase transition event
7. error event

`seq` はこの順序で単調増加させる。

## 14. error処理との接続

runtime loopはerrorを握りつぶさない。

| error | runtimeの動作 |
|---|---|
| parse error | runtime作成前に終了 |
| unsupported feature | runtime作成前に終了 |
| audio prepare error |描画あり実行は終了。headlessはvirtual audio指定時のみ継続 |
| render error | recoverable surface errorはrenderer再作成。fatalは終了 |
| runtime invariant violation | `Failed` へ遷移し、error telemetryを出す |
| analyzer mismatch | analyzer binaryがnon-zero exit |

## 15. test観点

runtime loopの単体テストは次を必須にする。

- 単一DonでPerfectになる。
- 早押し/遅押しでGoodになる。
- miss window超過でMissになる。
- Roll区間内入力だけがcountされる。
- Balloon required hits達成で成功する。
- 同じheadless runから同じtiming logが出る。
- render snapshot生成がruntime stateを変更しない。
- audio timeが単調でないstepはerrorになる。

## 16. 第5回への未確定値

第4回では構造だけを固定し、次の数値は第5回で確定する。

- perfect/good/miss window
- big_pair_window
- ending grace duration
- autoplay roll_rate_hz
- audio drift pass/fail threshold
- frame jitter pass/fail threshold
- expected/golden更新ルール

---

## Step2 Amendment: runtime loop追加要件

Runtime loopは次の順序を採用する。

1. selected courseのevent streamを読み込む。
2. audio offsetとchart timeを初期化する。
3. BPM/measure/scroll/branch/gogo/barline stateを更新する。
4. note/roll/balloonのvisible/judgement stateを更新する。
5. inputまたはheadless autoplay hitを処理する。
6. judge、combo、score、gauge、branch metricを更新する。
7. branch judge pointでrouteを選択する。
8. timing logへstate snapshotを出す。
9. chart endでclear/fail/resultを確定する。

Branch、score、gauge、scrollはPhase1中核であり、後回しにしない。

