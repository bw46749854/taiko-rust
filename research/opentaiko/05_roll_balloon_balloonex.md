# 05_roll_balloon_balloonex: 連打・風船・BalloonEx調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`, `OpenTaiko/src/Stages/07.Game/Taiko/NotesManager.cs`, `OpenTaiko/src/Stages/07.Game/CStage演奏画面共通.cs`

## 1. 結論

Phase1では、通常連打、大連打、風船、BalloonExをMust implement gameplayに入れる。`BALLOON`, `BALLOONNOR`, `BALLOONEXP`, `BALLOONMAS` はparser必須であり、branch routeごとにballoon hit countを解決する。

## 2. 対象note

| note char | 種別 | Phase1処理 |
|---|---|---|
| `5` | 通常連打 | start eventを作り、`8` とpairにする |
| `6` | 大連打 | start eventを作り、`8` とpairにする |
| `7` | 風船 | required hitsをBALLOON配列から取る |
| `9` | BalloonEx / くすだま相当 | required hitsをBALLOON配列から取る。visual差分はlog/report対象 |
| `8` | roll end | 直前未終了roll-likeを閉じる |

## 3. BALLOON配列

採用するresolution順序:

1. branch routeがNormal: `BALLOONNOR` があれば使用。なければ `BALLOON`。
2. branch routeがExpert: `BALLOONEXP` があれば使用。なければ `BALLOON`。
3. branch routeがMaster: `BALLOONMAS` があれば使用。なければ `BALLOON`。
4. 配列不足はparse warning。実行時panicにしない。

## 4. Runtime処理

OpenTaiko runtimeではroll/balloonを現在処理中roll chipとして扱い、roll endやtime経過で処理する。Rust版Phase1ではheadless determinismを優先し、roll-like intervalを明示的なdomain eventとして作る。

```text
RollState {
  id,
  kind,
  start_ms,
  end_ms,
  hits,
  required_hits,
  completed,
  branch_route,
}
```

## 5. Headless autoplay要件

- 通常連打/大連打は、設定されたauto roll rateでhitを生成する。
- 風船/BalloonExは、required hitsを満たすhitを生成する。
- 分岐条件にroll/balloon hit数を使うため、roll hit countをbranch scoreへ反映する。

## 6. Unresolved

BalloonExのOpenTaiko完全演出、multi-player reduction、Kusudama固有visualはStep2では式固定しない。Phase1では通常play完走、required hits、branch/score/gauge/log反映を必須にする。
