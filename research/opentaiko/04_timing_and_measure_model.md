# 04_timing_and_measure_model: timing / measure調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`, `OpenTaiko/src/Stages/07.Game/Taiko/NotesManager.cs`

## 1. 結論

Phase1 timing modelは、OpenTaiko由来の概念をRust版に整理して実装する。

- `BPM:` と `#BPMCHANGE` でBPM timelineを作る。
- `#MEASURE` で小節長を変える。
- `#DELAY` でdefinition cursorのtimeを進める。
- `OFFSET:` はchart/audio相対位置へ反映する。
- note配置は「小節内token数による任意分割」で統一する。

## 2. OpenTaikoで確認した構造

`CTja.CBPM` はBPM値、BPM change time、BMSCROLL用time、branch courseを持つ。Phase1ではこれを `BpmPoint` として採用する。

```text
BpmPoint {
  id,
  bpm,
  tja_time_ms,
  bm_scroll_time,
  branch_route,
}
```

## 3. 任意分割note scheduler

採用する配置式:

```text
measure_duration_ms = 240000.0 / bpm * measure_numerator / measure_denominator
note_time_ms = measure_start_ms + measure_duration_ms * token_index / token_count
```

`#DELAY` は `measure_start_ms` ではなくdefinition cursorのtimeへ加算するeventとして扱う。`#BPMCHANGE` は次のtoken配置から有効になる。

## 4. 384解像度との関係

OpenTaikoには `n小節の解像度 = 384` がある。Rust版Phase1では内部表現に有理数tickを使う。

採用値:

```text
BarResolution = 384
Tick = Rational<i64>
```

msは最終計算値として出す。golden比較ではtick/beatを第一基準、msを第二基準にする。

## 5. OFFSET

`OFFSET:` は秒単位の値として読み、msへ変換する。負OFFSETと正OFFSETを区別して保持する。

```text
ChartOffset {
  signed_ms,
  source_value_seconds,
}
```

OpenTaikoはglobal offsetを加味して最終的な絶対値と符号を保持する。Rust版Phase1では、config/global offsetを別fieldに分ける。

## 6. DELAY

`#DELAY` は秒単位指定をmsへ変換し、definition cursorの現在時刻を進める。BMSCROLL用timeにも影響する。

## 7. Timing log要件

Step3で `docs/43_timing_log_schema.md` を更新する際、以下を必須fieldにする。

- `measure_index`
- `measure_numerator`
- `measure_denominator`
- `token_count_in_measure`
- `token_index_in_measure`
- `beat_in_measure`
- `absolute_tick`
- `tja_time_ms`
- `audio_time_ms`
- `bpm_point_id`
- `delay_accumulated_ms`
- `offset_signed_ms`
