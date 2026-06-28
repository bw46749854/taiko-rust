# 07_scroll_and_visual_timing: scroll / visual timing調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`, `OpenTaiko/src/Stages/07.Game/Taiko/NotesManager.cs`, `OpenTaiko/src/Stages/07.Game/CStage演奏画面共通.cs`

## 1. 結論

Phase1はSCROLL系と追い越し系をMust implement gameplayに入れる。描画完全再現よりも、通常play完走、headless検証、timing log検査を優先する。

## 2. 対象event

| command | Phase1分類 | 処理 |
|---|---|---|
| `#SCROLL` | Must implement gameplay | 正、負、0、高速、複素を保持する |
| `#NMSCROLL` | Must implement gameplay | Normal modeへ切替 |
| `#BMSCROLL` | Must implement gameplay | BMScroll modeへ切替 |
| `#HBSCROLL` | Must implement gameplay | HBScroll modeへ切替 |
| `#SUDDEN` | Must parse / must not crash | sudden show/move offsetを保持し、logへ出す |
| `#DIRECTION` | Must parse / must not crash | scroll directionを保持する |
| `#JPOSSCROLL` | Must parse / must not crash | 判定枠移動eventとして保持する |

## 3. Scroll value

`#SCROLL` は複素数風指定を含む。Rust版Phase1は次の型にする。

```text
ScrollValue {
  x: f64,
  y: f64,
  source_text: String,
}
```

0 SCROLL、負SCROLL、高速SCROLLはすべて合法値にする。panic、clamp、無視は採用しない。

## 4. Scroll mode

`NotesManager` はNormalでms差分とBPMから距離を計算し、BM/HBではbeat基準を使う。Rust版Phase1では以下を採用する。

```text
ScrollMode = Normal | BmScroll | HbScroll
```

`Normal` はtime/BPM基準、`BmScroll` と `HbScroll` はbeat基準で表示距離を計算する。

## 5. 追い越し検証

追い越しは、note表示位置の順序がnote時刻順と異なる状態としてlogから検出する。

Timing analyzerは以下を検査する。

- event time順の安定性
- visual position順の逆転発生
- negative scroll区間
- zero scroll停止区間
- extreme scroll区間
- complex scroll y成分

## 6. Renderer要件

Step2ではrenderer完全仕様は固定しない。Rust版Phase1 runtimeは、`NoteVisualState` を出力できる構造にする。

```text
NoteVisualState {
  note_id,
  time_ms,
  lane_x,
  lane_y,
  scroll_mode,
  scroll_x,
  scroll_y,
  direction,
  sudden_state,
  jpos_offset,
}
```
