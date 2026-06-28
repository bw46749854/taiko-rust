# 08_score_gauge_clear_model: score / gauge / clear調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`, `OpenTaiko/src/Stages/07.Game/CStage演奏画面共通.cs`

## 1. 結論

Phase1はscore、gauge、clear判定をMust implement gameplayに入れる。通常play完走だけではPhase1合格にしない。score/gauge/clearがtiming logとQA reportで検証できることを合格条件にする。

## 2. OpenTaikoで確認したmetadata

| header | Rust採用名 | 処理 |
|---|---|---|
| `SCOREMODE:` | `ScoreMode` | score formula選択 |
| `SCOREINIT:` | `ScoreInit` | 初期配点。複数値を保持 |
| `SCOREDIFF:` | `ScoreDiff` | combo段階差分 |
| `GAUGEINCR:` | `GaugeIncreaseMode` | gauge増加方式 |
| `.FORCEGAUGE` | `ForceGauge` | gauge type override |

## 3. Score runtime採用事項

OpenTaiko runtimeでは、判定、combo、score mode、GOGO状態、大音符区分を使って加点する。Rust版Phase1でも以下を保持する。

```text
ScoreEventInput {
  judge,
  combo_before_hit,
  score_mode,
  score_init,
  score_diff,
  gogo_active,
  is_big_note,
}
```

## 4. GOGO

GOGOはscore倍率とvisual stateの両方に影響する。Phase1ではscore倍率の反映を必須、演出完全再現は非中核にする。

## 5. Gauge runtime採用事項

OpenTaiko runtimeはjudge resultとnote種別を使ってgaugeを更新し、clear/norma状態を判定する。Rust版Phase1では、まずdeterministicなgauge modelを作り、詳細式はTKT-0011でOpenTaiko追加調査により固定する。

必須log:

- `gauge_before`
- `gauge_after`
- `gauge_delta`
- `gauge_mode`
- `clear_before`
- `clear_after`
- `failed`

## 6. Clear判定

Phase1のclear判定は、曲終了時のgauge stateから算出する。段位、Tower、特殊challengeのclear/failはExplicit non-scope with reportへ分類する。

## 7. Unresolved

OpenTaikoのgauge増減量、force gauge、hard/extreme処理、skin/config依存値はStep2では完全固定しない。TKT-0011の着手条件として追加source調査を必須にする。
