# 34_error_handling_and_logging: Error Handling / Logging定義

作成日: 2026-06-25  
状態: 第4回ドラフト・採用候補  
上流文書: `docs/30_rust_architecture_overview.md`, `docs/31_module_boundaries.md`, `docs/32_data_model.md`, `docs/33_runtime_loop.md`

## 1. 目的

この文書は、Rust版Phase1のerror分類、exit code、logging、timing log、failure report連携を定義する。

AIループでは、失敗を曖昧な文章で扱わない。すべての失敗は、再現可能な入力、error種別、exit code、log path、差分、次の修正対象moduleへ変換する。

## 2. error handling原則

- user向けerrorとdeveloper向けtraceを分ける。
- unsupported featureはparse成功扱いにしない。
- recoverable errorとfatal errorを分ける。
- binary boundaryではexit codeへ変換する。
- library crateではpanicを使わず `Result` を返す。
- invariant violationだけは明示的にfatalへ変換する。
- errorには `run_id`、`chart_path`、`chart_hash`、`source_location` を可能な限り含める。

## 3. error taxonomy

```rust
pub enum TaikoError {
    Parse(ParseError),
    Unsupported(UnsupportedFeatureError),
    Asset(AssetError),
    Audio(AudioError),
    Render(RenderError),
    Input(InputError),
    Runtime(RuntimeError),
    Telemetry(TelemetryError),
    Analyzer(AnalyzerError),
    Io(IoError),
    Config(ConfigError),
}
```

### 3.1 ParseError

| variant | 意味 | 例 | exit |
|---|---|---|---:|
| `MissingRequiredHeader` | 必須header欠落 | `BPM`, `WAVE`なし | 10 |
| `InvalidHeaderValue` | header値不正 | `BPM:abc` | 10 |
| `InvalidCommandValue` | command値不正 | `#MEASURE x/y` | 10 |
| `InvalidNoteLine` | note行不正 | 未知文字、空解析不能 | 10 |
| `RollEndMissing` | roll/balloon終端欠落 | `5` に対応する `8` なし | 10 |
| `BalloonCountMissing` | balloon required hits欠落 | `7` あり `BALLOON` 不足 | 10 |

### 3.2 UnsupportedFeatureError

| variant | Phase1での扱い | exit |
|---|---|---:|
| `BranchChart` | 未対応譜面error | 11 |
| `DanCourse` | 未対応譜面error | 11 |
| `KongaGameType` | 未対応譜面error | 11 |
| `HbScrollOrBmScroll` | 未対応譜面error | 11 |
| `JposScroll` | 未対応譜面error | 11 |
| `SuddenOrHidden` | 未対応譜面error | 11 |
| `UnsupportedNoteChar` | 未対応譜面error | 11 |
| `OpenTaikoExtension` | runtimeに影響する拡張はerror。metadataだけはwarning | 11 |

Unsupportedは正常終了ではない。Codex実装Sessionはunsupportedを黙ってwarning化しない。

### 3.3 AssetError

| variant | 意味 | exit |
|---|---|---:|
| `AudioFileNotFound` | `WAVE` の音源が見つからない | 12 |
| `AudioDecodeFailed` | decode不能 | 12 |
| `FixtureNotFound` | fixture path不正 | 12 |
| `PermissionDenied` | file access不能 | 12 |

### 3.4 AudioError

| variant | 意味 | exit |
|---|---|---:|
| `NoOutputDevice` | default output deviceなし | 20 |
| `UnsupportedOutputConfig` | sample rate/format未対応 | 20 |
| `StreamBuildFailed` | cpal stream作成失敗 | 20 |
| `StreamPlayFailed` | stream開始失敗 | 20 |
| `CallbackUnderrun` | audio callback供給不足 | 21 |
| `PositionNonMonotonic` | audio position逆行 | 21 |

headlessでは `VirtualAudioBackend` を使うため、device系errorは発生しない。

### 3.5 RenderError

| variant | 意味 | exit |
|---|---|---:|
| `SurfaceLost` | 再作成対象 | 30 |
| `SurfaceOutdated` | resize/reconfigure対象 | 30 |
| `DeviceLost` | fatal | 31 |
| `ShaderCompileFailed` | fatal | 31 |
| `FrameAcquireFailed` | recoverableまたはfatal | 30/31 |

recoverable render errorはtraceへ出し、runtime stateは維持する。

### 3.6 RuntimeError

| variant | 意味 | exit |
|---|---|---:|
| `TimeWentBackwards` | step input時刻が逆行 | 40 |
| `InvalidPhaseTransition` | phase遷移不正 | 40 |
| `NoteStateInvariant` | note状態不整合 | 40 |
| `DuplicateInputUse` | 同一inputを複数hitへ使用 | 40 |
| `ResultAlreadyFinalized` | result確定後の変更 | 40 |

RuntimeErrorは実装バグとして扱い、failure reportへ必ず記録する。

### 3.7 AnalyzerError

| variant | 意味 | exit |
|---|---|---:|
| `LogMissingRequiredEvent` | 必須event欠落 | 50 |
| `SchemaInvalid` | JSONL/schema不正 | 50 |
| `MetricOutOfRange` | drift/jitter等が閾値超過 | 51 |
| `GoldenMismatch` | expected/goldenとの差分 | 51 |
| `NonDeterministicRun` | 同一fixtureでlog差分 | 52 |

## 4. exit code定義

| code | 意味 |
|---:|---|
| 0 | success |
| 1 | unknown fatal |
| 2 | CLI/config usage error |
| 10 | parse error |
| 11 | unsupported Phase1 feature |
| 12 | asset/file error |
| 20 | audio initialization error |
| 21 | audio runtime sync error |
| 30 | render recoverable limit exceeded |
| 31 | render fatal error |
| 40 | runtime invariant error |
| 50 | analyzer schema/log error |
| 51 | analyzer metric/golden failure |
| 52 | analyzer nondeterminism failure |
| 60 | telemetry write error |

CIはexit code 0だけをPASS扱いにする。

## 5. logging出力の分類

| 出力 | 用途 | format | 生成者 |
|---|---|---|---|
| user stderr | 人間向け短文error | text | binary |
| trace log | debug/failure調査 | text or JSON | tracing |
| timing log | analyzer入力 | JSONL | taiko_runtime telemetry + taiko_test_support writer |
| summary | CI/QA結果 | JSON | headless/app/tools |
| result | game result正本 | JSON | runtime/app |

## 6. trace log方針

`tracing` を採用し、次のspanを持つ。

- `run`
- `parse_chart`
- `prepare_audio`
- `runtime_step`
- `render_frame`
- `write_telemetry`
- `analyze_log`

### 6.1 log level

| level | 用途 |
|---|---|
| `ERROR` | 実行継続不能、exit code非0 |
| `WARN` | fallback、parse warning、recoverable render error |
| `INFO` | run開始/終了、chart概要、summary path |
| `DEBUG` | step統計、candidate note数、adapter状態 |
| `TRACE` | 入力1件ごとの詳細、frame詳細 |

CI標準は `INFO`。failure report再現時は `DEBUG` または `TRACE` を使う。

## 7. timing log方針

Timing logはAI検証の正本である。trace logとは別ファイルにする。

### 7.1 必須メタデータ

`run_started` eventは次を持つ。

```json
{
  "event": "run_started",
  "run_id": "...",
  "fixture_id": "phase1/basic_single_bpm",
  "chart_path": "fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja",
  "chart_hash": "...",
  "audio_hash": "...",
  "binary": "headless_autoplay",
  "autoplay": true,
  "config_hash": "..."
}
```

### 7.2 必須event

- `run_started`
- `chart_loaded`
- `audio_started`
- `frame` または `tick`
- `input`
- `judgement`
- `score_changed`
- `gauge_changed`
- `run_finished`

error時は `error` eventを必ず出す。

### 7.3 analyzer対象metric

第5回で閾値を確定するが、field名は次を採用する。

| metric | 意味 |
|---|---|
| `audio_chart_drift_us` | `audio_time + offset` と `chart_time` の差 |
| `input_delta_us` | inputとnoteの差 |
| `judge_delta_us` | 判定差 |
| `frame_delta_us` | frame間隔 |
| `late_frame_count` | 許容を超えたframe数 |
| `non_monotonic_time_count` | 時刻逆行数 |
| `missed_expected_note_count` | autoplayでhitすべきnoteのmiss数 |

## 8. summary JSON

`headless_autoplay` はsummary JSONを出力する。

```json
{
  "status": "PASS",
  "run_id": "...",
  "fixture_id": "phase1/basic_single_bpm",
  "result": {
    "score": 123456,
    "max_combo": 100,
    "perfect_count": 100,
    "good_count": 0,
    "miss_count": 0,
    "gauge_final": 100.0,
    "clear_status": "clear"
  },
  "timing": {
    "max_audio_chart_drift_us": 0,
    "max_input_delta_us": 0,
    "non_monotonic_time_count": 0
  },
  "paths": {
    "timing_log": "target/timing/basic_single_bpm.jsonl"
  }
}
```

Statusは `PASS`, `FAIL`, `BLOCKED` の3値にする。`BLOCKED` はCI失敗である。

## 9. user-facing error message

人間向けstderrは短く、次の形式にする。

```text
ERROR[11 unsupported_phase1_feature]: #BRANCHSTART is not supported in Phase1
chart: fixtures/synthetic/phase1_core/fx_core_001_basic_notes.tja
line: 42
hint: remove branch commands or use a Phase1-compatible fixture
log: target/logs/run_....log
```

user-facing errorは長大なbacktraceを出さない。backtraceはtrace logへ出す。

## 10. failure report連携

QA/回帰検証Sessionまたは実装SessionがNGを出すとき、failure reportに次を添付する。

- 実行コマンド
- exit code
- stderr全文または要約
- timing log path
- summary path
- analyzer report path
- 失敗eventの `seq`
- chart hash
- config hash
- 再現手順
- 推定module
- 次の修正Planへの入力

## 11. panic方針

library crateでpanicを使わない。panicを許可する箇所は次だけである。

- unit test内のassert
- binary起動直後の開発時未実装箇所。ただしPhase1受け入れ前に撤去する
- unreachable invariantをdebug assertionとして置く箇所。ただしreleaseでは `RuntimeError` へ変換する

`unwrap()` と `expect()` は、test以外では原則禁止する。binary `main()` ではerrorをexit codeへ変換する。

## 12. unsupported warningの境界

Phase1でruntimeに影響しないmetadataだけはwarningにできる。

| 入力 | 扱い |
|---|---|
| 未使用の `DEMOSTART` | parseしてmetadata保存、warning不要 |
| 未使用の画像metadata | metadata warning |
| runtimeに影響する未対応command | unsupported error |
| 未対応note char | unsupported error |
| 分岐/特殊scroll | unsupported error |

## 13. analyzer失敗の分類

analyzerは失敗を次に分類する。

| category | 意味 | 修正先候補 |
|---|---|---|
| `schema` | log形式不正 | telemetry/tools |
| `timing` | drift/jitter/非単調 | time/audio/runtime |
| `judgement` | rank/delta不一致 | judgement/runtime |
| `score` | score/combo/gauge不一致 | score/gauge |
| `result` | result summary不一致 | runtime/result |
| `determinism` | 同一run差分 | runtime/autoplay/time |

## 14. CIで保存するartifact

CIまたはローカルQAは、失敗時に次を保存する。

```text
target/timing/*.jsonl
target/timing/*.summary.json
target/analyzer/*.report.json
target/logs/*.log
target/screenshots/*.png   # 描画ありsmokeで生成できる場合
```

ログ保存に失敗した場合は `TelemetryError` として扱う。

## 15. 実装チケット化の単位

| ticket候補 | 対象 |
|---|---|
| `ERR-001` | error enumとexit code mapping |
| `ERR-002` | tracing初期化とtrace log出力 |
| `ERR-003` | timing log writer |
| `ERR-004` | summary writer |
| `ERR-005` | analyzer report model |
| `ERR-006` | failure reportテンプレート連携 |

## 16. review観点

設計レビューSessionは、error/logging実装について次を確認する。

- unsupported featureが明示errorになっている。
- exit codeが表に従っている。
- timing logとtrace logが混ざっていない。
- analyzerがfail理由を分類している。
- failure reportに再現情報が残る。
- `unwrap()` / `expect()` がtest以外に残っていない。

---

## Step2 Amendment: compatibility report方針

Parser/runtimeは未知またはPhase1非中核機能をpanicにしない。次の区分でreportする。

| report kind | 用途 |
|---|---|
| `parse_warning` | 値不足、配列不足、fallback採用 |
| `compatibility_warning` | OpenTaiko譜面に現れるが完全再現しない機能 |
| `explicit_non_scope` | 段位、BGA、lyrics、camera/objectなどPhase1対象外 |
| `fatal_parse_error` | chart構造が壊れて選択courseを構築できない |

`fatal_parse_error` 以外はuser-selected song validation reportへ出力する。

