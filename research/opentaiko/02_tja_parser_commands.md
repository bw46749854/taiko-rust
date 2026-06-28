# 02_tja_parser_commands: TJA command調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`

## 1. 結論

Phase1 parserは、OpenTaiko通常プレイで登場するTJA commandを3分類で扱う。

- Must implement gameplay: chart timing、note visibility、branch、score/gauge、audio start、通常play完走に必要なもの。
- Must parse / must not crash: 通常譜面に現れるが、Phase1 gameplay中核の完全再現までは要求しないもの。
- Explicit non-scope with report: 通常プレイ完走の中核外。検出してreportする。

## 2. Must implement gameplay command

| command/header | Rust採用名 | 必須理由 | 実装単位 |
|---|---|---|---|
| `BPM:` | `InitialBpm` | timeline初期値 | metadata parser |
| `#BPMCHANGE` | `BpmChangeEvent` | 曲中BPM変化 | body command parser + scheduler |
| `#MEASURE` | `MeasureEvent` | 変拍子、任意分割 | scheduler |
| `#DELAY` | `DelayEvent` | TJA time cursor補正 | scheduler |
| `OFFSET:` | `ChartOffset` | audio/chart sync | audio sync model |
| `WAVE:` | `AudioPath` | 曲再生 | metadata parser |
| `PATH_WAV:` | `AudioBasePath` | audio参照解決 | metadata parser |
| `COURSE:` | `CourseSection` | 複数難易度選択 | course selector |
| `#SCROLL` | `ScrollEvent` | 速度変化、追い越し | scroll timeline |
| `#NMSCROLL` | `ScrollModeNormal` | scroll mode復帰 | scroll model |
| `#BMSCROLL` | `ScrollModeBm` | BPM非依存表示系 | scroll model |
| `#HBSCROLL` | `ScrollModeHb` | HB表示系 | scroll model |
| `#GOGOSTART` / `#GOGOEND` | `GogoStateEvent` | score倍率、演出状態、fixture検証 | runtime state |
| `#BARLINE`, `#BARLINEON`, `#BARLINEOFF` | `BarlineEvent` | 小節線表示と譜面互換 | visual/timing log |
| `#SECTION` | `BranchSectionReset` | branch条件区間リセット | branch evaluator |
| `#BRANCHSTART` | `BranchStart` | 譜面分岐開始 | branch parser/evaluator |
| `#N` / `#E` / `#M` | `BranchRouteBody` | 普通/玄人/達人route | branch body parser |
| `#LEVELHOLD` | `LevelHold` | branch固定 | branch runtime |
| `#BRANCHEND` | `BranchEnd` | branch終了 | branch runtime |
| `BALLOON:` | `BalloonCountsNormal` | balloon hit数 | roll/balloon model |
| `BALLOONNOR:` | `BalloonCountsNormal` | 普通route balloon | branch roll model |
| `BALLOONEXP:` | `BalloonCountsExpert` | 玄人route balloon | branch roll model |
| `BALLOONMAS:` | `BalloonCountsMaster` | 達人route balloon | branch roll model |
| `SCOREMODE:` | `ScoreMode` | score互換 | score model |
| `SCOREINIT:` | `ScoreInit` | score互換 | score model |
| `SCOREDIFF:` | `ScoreDiff` | score互換 | score model |
| `GAUGEINCR:` | `GaugeIncreaseMode` | gauge互換 | gauge model |
| `.FORCEGAUGE` | `ForceGauge` | gauge variant | gauge model |

## 3. Must parse / must not crash command

| command/header | Phase1処理 | 理由 |
|---|---|---|
| `#SUDDEN` | parseし、visual state/timing logへ出す。描画完全再現はStep3でfixture化する | OpenTaiko通常譜面互換 |
| `#DIRECTION` | parseし、scroll direction stateへ出す | 特殊表示互換 |
| `#JPOSSCROLL` | parseし、判定枠移動eventとして保持する | 追い越し・特殊表示互換 |
| `HEADSCROLL:` | 初期scrollとしてparseする | TJA互換 |
| `HIDDENBRANCH:` | parseし、metadataへ保持する | 選曲UI寄りだがbranch metadataに影響 |
| `GAME:` / `#GAMETYPE` | Taikoを主対象として保持。Konga等はreport対象 | 通常Taiko playの境界明示 |
| `LIFE:` / `.BOOMRULE` | parse/report。Tower等の完全仕様は非中核 | OpenTaiko header互換 |
| `SONGVOL:` | parse/report。音量反映はadapter側 | audio metadata互換 |

## 4. Explicit non-scope with report

| command/header | 処理 | 理由 |
|---|---|---|
| `#NEXTSONG` | explicit non-scope report | 段位/複数曲連結。Phase1通常1曲play外 |
| `EXAM*` | explicit non-scope report | 段位条件 |
| `#BGAON` / `#BGAOFF` | explicit non-scope report | BGA演出 |
| `#LYRIC` | explicit non-scope report | lyrics |
| `#CAM*` | explicit non-scope report | camera演出 |
| `#OBJ*` / `#ADDOBJECT` / `#REMOVEOBJECT` | explicit non-scope report | object演出 |
| `#CHANGETEXTURE` / `#RESETTEXTURE` | explicit non-scope report | skin/object演出 |
| `#SPLITLANE` / `#MERGELANE` | report。実装優先度はStep4 ticket判断へ回す | lane演出寄り |
| `#BORDERCOLOR`, `#SETCONFIG`, `#ENABLEDORON`, `#DISABLEDORON` | report | gameplay中核外 |

## 5. 実装方針

Parserは未知commandでpanicしない。すべてのcommandは次のいずれかになる。

```text
ParsedGameplayEvent
ParsedCompatibilityEvent
ParsedNonScopeReport
ParsedWarning
ParsedError
```

`ParsedError` は、TJA構文が壊れて通常play続行が不可能な場合だけ使う。OpenTaiko譜面に現れるがPhase1中核外のcommandはerrorにしない。
