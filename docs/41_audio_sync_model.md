# 41_audio_sync_model: Audio同期モデル

作成日: 2026-06-25
Status: canonical
上流文書: `docs/30_rust_architecture_overview.md`, `docs/33_runtime_loop.md`, `docs/40_timing_model.md`

## 1. 目的

この文書は、Phase1のaudio再生と譜面進行の同期モデルを固定する。目的は、音が鳴る実装を作ることではなく、音ズレを測定し、Codexの実装ループが自動で原因を切り分けられる構造を作ることである。

Phase1では、次を採用する。

- audio backendは `AudioBackend` traitで抽象化する。
- headlessでは `VirtualAudioBackend` を使う。
- 通常プレイでは `CpalAudioBackend` を使う。
- decoderはruntimeから分離する。
- audio timeはsample frame countから導出する。
- sync deltaをtiming logへ周期出力する。

## 2. AudioBackend trait

`taiko_audio` に次のtraitを置く。

```rust
pub trait AudioBackend {
    fn prepare(&mut self, request: AudioPrepareRequest) -> Result<AudioHandle, AudioError>;
    fn start(&mut self, handle: AudioHandle, start_at_game_time: GameTimeUs) -> Result<(), AudioError>;
    fn stop(&mut self) -> Result<(), AudioError>;
    fn snapshot(&self) -> AudioClockSnapshot;
}
```

`runtime` はtraitを直接持たない。`app` が `snapshot()` を取り、`RuntimeStepInput.audio_time_us` と telemetry へ渡す。

## 3. AudioClockSnapshot

```rust
pub struct AudioClockSnapshot {
    pub backend: AudioBackendKind,
    pub stream_state: AudioStreamState,
    pub sample_rate_hz: u32,
    pub channels: u16,
    pub frames_rendered: u64,
    pub frames_submitted: u64,
    pub audio_time_us: Option<AudioTimeUs>,
    pub callback_count: u64,
    pub underrun_count: u64,
    pub last_callback_wall_time_us: Option<WallTimeUs>,
    pub device_latency_us: Option<i64>,
}
```

`audio_time_us` は `frames_rendered` と `sample_rate_hz` から計算する。device timestampが取れる環境でも、それを正規時刻にはしない。device timestampはtelemetry上の補助情報として扱う。

## 4. Decoder責務

decoderは音声ファイルをPCM bufferへ変換する。runtime step中にdecodeしない。

```rust
pub struct DecodedAudio {
    pub sample_rate_hz: u32,
    pub channels: u16,
    pub samples_f32_interleaved: Vec<f32>,
    pub duration_us: AudioTimeUs,
    pub source_hash: String,
}
```

Phase1では、`.wav` を必須対応、`.ogg` を推奨対応、`.mp3` を後続候補にする。fixtureは `.wav` を正とする。音声codec差でtiming fixtureが不安定になることを避ける。

## 5. 再生開始モデル

通常プレイでは、game startとaudio startの対応を明示する。

```text
game_start_time_us = 0
audio_start_chart_time_us = chart_audio_offset_us
```

再生開始時、telemetryへ `audio_start` eventを1回出す。

必須field:

- `game_time_us`
- `audio_time_us`
- `chart_audio_offset_us`
- `sample_rate_hz`
- `buffer_size_frames`
- `backend`
- `audio_source_hash`

## 6. Sync delta

sync deltaの定義を次に固定する。

```text
sync_delta_us = game_time_us - expected_game_time_from_audio_us
```

`expected_game_time_from_audio_us` は次で求める。

```text
expected_game_time_from_audio_us = audio_time_us - chart_audio_offset_us
```

正値はgameがaudioより進んでいる。負値はgameがaudioより遅れている。

この符号を全ログ・summary・analyzerで統一する。

## 7. Audio telemetry event

通常プレイと `taiko_play --autoplay` では、少なくとも250msごとに `audio_sync_sample` を出す。

```json
{
  "type": "audio_sync_sample",
  "run_id": "...",
  "seq": 128,
  "game_time_us": 12345000,
  "audio_time_us": 12343000,
  "sync_delta_us": 2000,
  "sample_rate_hz": 48000,
  "frames_rendered": 592464,
  "callback_count": 724,
  "underrun_count": 0,
  "device_latency_us": 5300
}
```

headlessでは、各noteまたは固定tickで `audio_sync_sample` を出してよい。ただし `sync_delta_us = 0` を期待値にする。

## 8. Buffering方針

Phase1のaudio bufferは低遅延最適化より測定可能性を優先する。

- requested buffer sizeはconfigに出す。
- actual buffer sizeはlogに出す。
- underrun countを記録する。
- callback intervalのmin/median/p95/maxをsummaryに出す。
- runtimeの合否はaudio callbackの偶発的jitterに依存させない。

## 9. 音ズレ原因の分類

analyzer summaryはaudio関連failureを次に分類する。

| 分類 | 条件 | 想定原因 |
|---|---|---|
| `audio_clock_missing` | `audio_time_us` が必要区間で欠落 | backend未実装、stream未開始 |
| `audio_underrun` | underrun count > 0 | buffer不足、decode遅延 |
| `sync_drift_linear` | sync deltaが時間と相関して増減 | sample rate誤差、frame count計算誤り |
| `sync_offset_constant` | sync delta平均が大きいが傾きは小さい | OFFSET符号、start alignment誤り |
| `sync_jitter_high` | p95/maxが高い | callback jitter、thread scheduling |
| `audio_duration_mismatch` | decoded durationがfixture expectedと不一致 | decoder、sample rate変換誤り |

Codexはfailure分類に応じて修正対象crateを限定する。

## 10. Audio sync gate

### 10.1 Headless gate

headlessではvirtual audioを使うため、次を必須にする。

| 指標 | 合格条件 |
|---|---:|
| sync delta min | `0us` |
| sync delta median | `0us` |
| sync delta max | `0us` |
| audio underrun | `0` |
| audio missing sample | `0` |

### 10.2 Real audio smoke gate

real audio smokeはCI必須ではない。開発環境またはQA/回帰検証Sessionで実施する。

```bash
cargo run -p taiko_play --   --chart fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja   --autoplay   --emit-timing-log target/timing/basic_120bpm.audio.jsonl   --duration-limit 60s

cargo run -p timing_log_analyzer --   --log target/timing/basic_120bpm.audio.jsonl   --profile local-audio-smoke
```

合格条件:

| 指標 | 合格条件 |
|---|---:|
| median abs sync delta | `<= 2ms` |
| p95 abs sync delta | `<= 5ms` |
| max abs sync delta | `<= 12ms` |
| underrun count | `0` |
| callback interval p95 | actual buffer intervalの2.5倍以内 |

## 11. Audioとjudgementの関係

judgementはaudio callbackでは実行しない。input eventはgame timeへ正規化し、runtime stepで判定する。

audio timeは次にだけ使う。

- telemetry
- sync delta
- local audio smoke
- future calibration設計

Phase1では自動calibrationを実装しない。calibrationはPhase2以降で扱う。

## 12. 実装順序

1. `VirtualAudioBackend` を実装する。
2. `AudioClockSnapshot` をlogへ出す。
3. `.wav` decodeのfixture testを作る。
4. `CpalAudioBackend` を最小実装する。
5. `audio_start` と `audio_sync_sample` eventを出す。
6. analyzerのaudio profileを追加する。
7. real audio smoke手順をREADME/CI補助scriptへ接続する。

## 13. 禁止事項

- audio callbackからruntimeを直接呼ぶ。
- audio callback内でJSONを書く。
- sample countではなくwall clockだけでaudio timeを決める。
- real audio smokeの失敗をfixture expected変更で回避する。
- `OFFSET`をparser、runtime、audioの複数箇所で重複適用する。
- headless用のaudio sync処理を通常プレイと別仕様にする。

---

## WAVE/PATH_WAV/OFFSET policy

Phase1 audio modelは `WAVE`, `PATH_WAV`, `OFFSET` を扱う。headless実行では実音源が存在しない場合にsilent adapterで継続し、compatibility warningを出す。描画あり通常実行ではaudio missingを明確なerrorにする。

Timing logは `chart_time_ms`, `audio_time_ms`, `offset_signed_ms`, `audio_adapter_kind` を出力する。

