# 03_note_type_mapping: note type調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Stages/07.Game/Taiko/NotesManager.cs`

## 1. 結論

Phase1は、OpenTaikoのTaiko通常プレイで登場するTJA note文字をparse対象にする。通常play完走に必要なnoteはMust implement gameplayへ入れる。Konga専用、補助、危険物系はparse/reportを基本にする。

## 2. TJA note文字対応

| char | OpenTaiko種別 | Phase1分類 | Rust採用名 | 処理 |
|---|---|---|---|---|
| `0` | Empty | Must implement gameplay | `Empty` | 休符/空token |
| `1` | Don | Must implement gameplay | `Don` | 赤小音符 |
| `2` | Ka | Must implement gameplay | `Ka` | 青小音符 |
| `3` | DonBig | Must implement gameplay | `DonBig` | 赤大音符。score/gauge/judge対象 |
| `4` | KaBig | Must implement gameplay | `KaBig` | 青大音符。score/gauge/judge対象 |
| `5` | Roll | Must implement gameplay | `RollStart` | 通常連打開始 |
| `6` | RollBig | Must implement gameplay | `BigRollStart` | 大連打開始 |
| `7` | Balloon | Must implement gameplay | `BalloonStart` | 風船開始。BALLOON配列と結合 |
| `8` | EndRoll | Must implement gameplay | `RollEnd` | 連打/風船終了 |
| `9` | BalloonEx | Must implement gameplay | `BalloonExStart` | くすだま/芋相当。Phase1対象 |
| `A` | DonHand | Must parse / must not crash | `DonHand` | 2P/特殊大音符系。1P通常ではreport |
| `B` | KaHand | Must parse / must not crash | `KaHand` | 2P/特殊大音符系。1P通常ではreport |
| `C` | Bomb | Must parse / must not crash | `Bomb` | OpenTaiko noteとして認識。Phase1通常playではreport |
| `D` | BalloonFuze | Must parse / must not crash | `BalloonFuze` | ProjectOutfox系。parse/report |
| `F` | Adlib | Must parse / must not crash | `Adlib` | hidden/adlib系。通常score中核外 |
| `G` | Kadon | Must parse / must not crash | `Kadon` | swap/double hit系。Phase1ではreport |
| `H` | RollClap | Must parse / must not crash | `RollClap` | Konga寄り。Taikoではreport |
| `I` | RollPa | Must parse / must not crash | `RollPa` | Konga寄り。Taikoではreport |

## 3. 大音符

`3` と `4` はPhase1のMust implement gameplayに入れる。OpenTaikoのscore処理では大音符がscore bonus対象になる。Rust版Phase1でも、headless autoplay、score/gauge、timing logに大音符区分を出す。

## 4. Roll系

`5`, `6`, `7`, `9`, `8` はPhase1中核に入れる。

採用するevent model:

```text
RollLikeEvent {
  id,
  kind: Roll | BigRoll | Balloon | BalloonEx,
  start_time,
  end_time,
  required_hits: Option<u32>,
  branch_route,
  source_balloon_index,
}
```

## 5. 任意分割schedulerとの関係

note文字は、小節内のtoken indexからbeat/tick/msへ配置する。4/8/12/16/24/36分を個別caseにしない。小節内token数と `MEASURE` から、すべてのtoken位置を決める。

## 6. Phase1で保持するlog属性

- `note_char`
- `note_kind`
- `is_big`
- `is_roll_like`
- `roll_id`
- `balloon_required_hits`
- `branch_route`
- `source_measure_index`
- `token_index_in_measure`
- `token_count_in_measure`
