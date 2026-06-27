# 06_branching_model: 譜面分岐調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`, `OpenTaiko/src/Stages/07.Game/CStage演奏画面共通.cs`

## 1. 結論

Phase1は譜面分岐をMust implement gameplayに入れる。普通/玄人/達人の3route、`SECTION`, `BRANCHSTART`, `N/E/M`, `LEVELHOLD`, `BRANCHEND` をすべてparser/runtime対象にする。

## 2. Branch command

| command | Phase1 event | 処理 |
|---|---|---|
| `#SECTION` | `BranchSectionReset` | branch判定用score/countをresetする |
| `#BRANCHSTART` | `BranchStart` | 条件type、閾値、range、big条件、judge timeを保持する |
| `#N` | `BranchRoute(Normal)` | 普通譜面bodyへ切替 |
| `#E` | `BranchRoute(Expert)` | 玄人譜面bodyへ切替 |
| `#M` | `BranchRoute(Master)` | 達人譜面bodyへ切替 |
| `#LEVELHOLD` | `LevelHold` | route固定を有効化する |
| `#BRANCHEND` | `BranchEnd` | 共通譜面へ復帰する |

## 3. Branch condition type

OpenTaiko parserで確認したconditionをRust版へ採用する。

| TJA condition | Rust enum | Phase1処理 |
|---|---|---|
| `p` | `Accuracy` | Must implement gameplay |
| `pp` | `PercentPerfect` | Must implement gameplay |
| `jb` | `JudgeBad` | Must implement gameplay |
| `r` | `Roll` | Must implement gameplay |
| `rb` | `BalloonHits` | Must implement gameplay |
| `s` | `Score` | Must implement gameplay |
| `jp` | `JudgePerfect` | Must implement gameplay |
| `jg` | `JudgeGood` | Must implement gameplay |
| `d` | `JudgePerfectBigOnly` | parseし、big-only条件として扱う |
| unknown | `UnknownCondition` | parse warning。current branch維持 |

## 4. Big-only / regular-only区分

OpenTaikoは条件文字の大文字・小文字を見てBigOnly等を判定する。Rust版Phase1では次のenumへ変換する。

```text
BranchCondBigMode = Both | RegularOnly | BigOnly
```

## 5. Branch runtime

採用するbranch評価手順:

1. `#SECTION` でsection score/countをresetする。
2. `#BRANCHSTART` のjudge pointに到達する。
3. branch conditionを評価する。
4. Normal / Expert / Master routeを決める。
5. `#LEVELHOLD` が有効な間はrouteを固定する。
6. `#BRANCHEND` で共通譜面へ復帰する。

## 6. Timing log要件

- `branch_section_id`
- `branch_condition_type`
- `branch_threshold_expert`
- `branch_threshold_master`
- `branch_selected_route`
- `branch_previous_route`
- `branch_levelhold_active`
- `branch_metric_snapshot`

## 7. Unresolved

OpenTaikoのbranch judge chip time算出は詳細追跡が必要。Step2では概念仕様を固定し、TKT-0008/TKT-0009で式単位調査を実施する。
