# 42_judgement_model: Judgementモデル

作成日: 2026-06-25
Status: canonical
上流文書: `docs/20_phase1_scope.md`, `docs/22_phase1_acceptance_criteria.md`, `docs/32_data_model.md`, `docs/40_timing_model.md`

## 1. 目的

この文書は、Phase1の判定モデルを固定する。対象はtap note、roll、balloon、miss確定、autoplay、timing logである。

Phase1の目標は、任意の曲を通常プレイできる範囲まで到達することである。ただし、判定精度は人間の目視では収束しない。判定処理は必ずlog化し、analyzerがexpectedと比較できる形にする。

## 2. 判定対象

Phase1で判定対象にするnoteを次に固定する。

| TJA文字 | Phase1種別 | 判定 |
|---|---|---|
| `1` | Don | tap |
| `2` | Ka | tap |
| `3` | DonBig | tap。Phase1では通常tapとして扱い、両手同時必須にしない |
| `4` | KaBig | tap。Phase1では通常tapとして扱い、両手同時必須にしない |
| `5` | RollStart | roll start |
| `6` | BigRollStart | roll start |
| `7` | BalloonStart | balloon start |
| `8` | RollEnd | roll/balloon end |

`0` は空slotである。

次はPhase1非対象またはunsupportedとしてparse時に記録する。

| TJA文字 | 扱い |
|---|---|
| `9` | kusudama扱いはPhase1非対象 |
| `A`, `B` | 2P/hand noteはPhase1非対象 |
| `C` | mineはPhase1非対象 |
| `D` | fuse rollはPhase1非対象 |
| `F` | adlibはPhase1非対象 |
| `G`, `H`, `I` | extension noteはPhase1非対象 |

## 3. JudgeKind

`taiko_domain::judgement` に次を置く。

```rust
pub enum JudgeKind {
    Perfect,
    Good,
    Bad,
    Miss,
    Roll,
    Balloon,
    Ignored,
}
```

OpenTaiko側の表示/集計名にはPerfect/Great/Good/Poor/Missのような区分があるが、Rust版Phase1では判定窓として `Perfect`, `Good`, `Bad`, `Miss` を正規名にする。表示名の差異はUI layerで扱う。

## 4. 判定窓

判定窓はconfigから注入する。

```rust
pub struct JudgementWindows {
    pub perfect_us: i64,
    pub good_us: i64,
    pub bad_us: i64,
}
```

`abs(delta_us)` で分類する。

```text
abs(delta) <= perfect_us => Perfect
abs(delta) <= good_us    => Good
abs(delta) <= bad_us     => Bad
otherwise                => outside window
```

Phase1 default profileを次に固定する。

| profile | perfect | good | bad |
|---|---:|---:|---:|
| `phase1-default` | 25,000us | 75,000us | 108,000us |
| `strict-test` | 10,000us | 20,000us | 30,000us |

OpenTaiko互換値は未確定値として扱う。OpenTaiko調査設計調査で最終抽出するまで、Rust版のacceptanceはfixture profileのexpected一致で判定する。

## 5. InputKind

```rust
pub enum InputKind {
    DonLeft,
    DonRight,
    KaLeft,
    KaRight,
}
```

Phase1ではDon系noteはDon入力、Ka系noteはKa入力でhit可能にする。Big noteは通常入力1回でhit可能にする。両手同時・大音符の加点差はPhase2以降へ送る。

## 6. Nearest note選択

input eventごとに、対象laneの未hit tap noteから次を満たすものを探す。

1. laneが一致する。
2. `abs(input_time - note_time) <= bad_us`。
3. `abs(delta)` が最小。
4. tieは `note_id` が小さい方を選ぶ。

選択したnoteに対してJudgeKindを確定する。選択できないinputは `Ignored` としてlogへ出す。score/gaugeは変えない。

## 7. Miss確定

tap noteは次の条件でMissになる。

```text
game_time_us > note_time_us + bad_us
```

Miss確定はinputがなくてもruntime stepで発生する。miss eventは1noteにつき1回だけ出す。

Miss確定前にhit済みになったnoteはMissにならない。

## 8. 同時押し・近接note

Phase1の同時刻noteは `note_id` 昇順で処理する。

同じlaneで同時刻に複数noteが存在するfixtureはunsupported testとして扱う。実曲で出た場合は、parserは受け入れるがruntimeはnearest ruleでdeterministicに処理する。

異なるlaneの同時刻noteはそれぞれ独立に処理する。

## 9. Roll判定

Rollはtap判定と別扱いにする。

- RollStartからRollEndまでを `RollSpan` として構築する。
- RollSpan中のDon/Ka入力は `JudgeKind::Roll` としてcountする。
- Roll入力はcomboを増やさない。
- Roll入力はscoreへroll点を加算する。
- RollEnd到達時にspanを閉じる。
- RollEndが存在しない場合はparser errorにする。

Phase1ではrollの細かい加点差、連打アニメ、分岐条件反映を非対象にする。

## 10. Balloon判定

BalloonはRollSpanの特殊形として扱う。

```rust
pub struct BalloonSpec {
    pub required_hits: u32,
}
```

- BalloonStartからRollEndまでをspanにする。
- span中の入力ごとにhit countを増やす。
- `required_hits` 到達時に `balloon_cleared` eventを出す。
- `required_hits` 未満でRollEnd到達時に `balloon_failed` eventを出す。
- Phase1ではballoon clear bonusを固定値にする。

Balloon required hitsは `.tja` のBALLOON定義から読む。定義不足はparser warningではなくerrorにする。

## 11. Autoplay判定

`AutoplayPolicy` はtap noteのnote_timeぴったりに入力を生成する。

```text
autoplay_input_time_us = note_time_us
autoplay_delta_us = 0
```

Roll/Balloonでは、span開始から一定間隔で入力を生成する。

```text
autoplay_roll_interval_us = 60_000
```

この値はPhase1固定値とする。実装Sessionはこの値を変更しない。変更が必要になった場合は仕様Sessionで文書更新してから行う。

## 12. Score/Gaugeへの接続

judgementはscore/gaugeへ直接点数値を埋め込まない。`JudgementEvent` を発行し、score/gauge moduleが購読する。

```rust
pub struct JudgementEvent {
    pub note_id: Option<NoteId>,
    pub input_id: Option<InputId>,
    pub judge: JudgeKind,
    pub delta_us: Option<DeltaUs>,
    pub note_time_us: Option<ChartTimeUs>,
    pub input_time_us: Option<GameTimeUs>,
    pub lane: Lane,
}
```

この分離により、analyzerはscore/gauge更新前の純粋な判定結果を検査できる。

## 13. Boundary fixture

判定境界fixtureは必須にする。

`strict-test` profileで、各noteに対して次のinputを生成する。

```text
-perfect_us
-perfect_us - 1
+perfect_us
+perfect_us + 1
-good_us
-good_us - 1
+good_us
+good_us + 1
-bad_us
-bad_us - 1
+bad_us
+bad_us + 1
```

expectedは次の通りである。

- `abs(delta) == perfect_us` はPerfect。
- `abs(delta) == perfect_us + 1` はGood。
- `abs(delta) == good_us` はGood。
- `abs(delta) == good_us + 1` はBad。
- `abs(delta) == bad_us` はBad。
- `abs(delta) == bad_us + 1` はIgnoredまたはMiss対象。

## 14. Analyzerで検査すること

- 全tap noteがhitまたはmissのいずれかで1回だけ解決する。
- hit済みnoteにmissが出ない。
- 1inputが複数noteをhitしない。
- `delta_us = input_time_us - note_time_us` がlog上で一致する。
- JudgeKindが判定窓profileと一致する。
- autoplay tap deltaがすべて0usである。
- lane mismatch inputがIgnoredになる。
- roll/balloon inputがtap comboを増やさない。

## 15. 禁止事項

- 判定窓をコード内に分散して直書きする。
- renderer座標からhit/missを推定する。
- input callback内で判定を確定する。
- Miss確定をrender visibilityに依存させる。
- autoplayをheadless専用runtimeとして実装する。
- expectedに合わせるためにtiming logを書き換える。

---

## Branch, score, and gauge integration

Judgement modelは単独では完結しない。Phase1ではjudge resultを次へ伝播する。

- combo update
- branch metric update
- score update
- gauge update
- clear/fail state update
- timing log output

Branch conditionに使う `Accuracy`, `PercentPerfect`, `JudgeBad`, `Roll`, `BalloonHits`, `Score`, `JudgePerfect`, `JudgeGood` は、runtime stateとして保持する。

