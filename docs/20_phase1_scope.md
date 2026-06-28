# 20_phase1_scope: Phase1スコープ定義

作成日: 2026-06-25
Status: canonical
上流文書: `docs/24_phase1_normal_play_compatibility_contract.md`, `docs/25_phase1_feature_classification.md`

## 1. Phase1の固定ゴール

Phase1のゴールは、Rust製の独自リズムゲームで、OpenTaikoが通常プレイで対応している範囲の `.tja` 譜面要素を含む曲を、1P通常プレイとして最後まで進行できる状態にすることである。

Phase1の「任意の曲」は、単純な1曲の起動成功ではない。ユーザーが選定した複数の実曲と、機能別synthetic fixtureを使い、通常プレイで遭遇するOpenTaiko対応譜面要素を検証対象へ含める。

Phase1完了は、次の状態で判定する。

- `.tja` metadata、音源path、COURSE、譜面本体を読み込める。
- 1P通常プレイループを開始、進行、終了できる。
- 任意分割note schedulerで各note tokenを正しい時刻へ配置できる。
- Don/Ka/大音符、連打、風船、BalloonExを処理できる。
- BPMCHANGE、MEASURE、DELAY、OFFSETをtimingへ反映できる。
- GOGO、BARLINE、SCROLL、scroll mode、譜面分岐を通常プレイへ反映できる。
- score、combo、gauge、clear判定、resultを生成できる。
- headless autoplay、timing log、timing log analyzerで自動合否判定できる。
- synthetic fixturesとuser-selected real songsの二層検証でPASSできる。

Phase1では、OpenTaikoを参考仕様の情報源として扱う。OpenTaikoのコード構造、アセット、UI、演出、全モードの再現は行わない。

## 2. 採用するプレイ範囲

| 項目 | Phase1採用範囲 | 完了判定 |
|---|---|---|
| プレイ人数 | 1Pのみ | 1P入力、1Pスコア、1Pゲージ、1Pリザルトが完結する |
| プレイモード | 通常演奏 | 曲開始から曲終了まで通常プレイとして完走する |
| 曲指定 | CLIまたは最小曲リスト | `.tja` pathとCOURSEを指定して起動できる |
| 難易度 | 複数COURSEから指定COURSEを選択 | 複数COURSEを含む `.tja` から対象譜面を抽出できる |
| 譜面要素 | OpenTaiko通常プレイ対応範囲 | `docs/25` のMust implement gameplay項目を満たす |
| 描画 | 固定スキン相当の最小レーン表示 | ノーツ、判定ライン、barline、score、combo、gauge、終了状態が視認できる |
| 音声 | 1つのBGM音源を再生 | WAVE/PATH_WAV解決、再生開始、再生位置取得、終了検知ができる |
| 入力 | Red/Blue系の1P入力 | Don/Ka/Big/Roll/Balloonに必要な入力を正規化できる |
| 判定 | 良/可/不可相当 | 判定窓、early/late、miss確定、hit済み除外を実装する |
| スコア | Phase1標準スコアモデル | SCOREINIT/SCOREDIFF/SCOREMODEを読み、score/combo/gaugeへ反映する |
| リザルト | 最小画面 + JSON | score/combo/judgement count/roll/balloon/gauge/clear/autoplayを出す |
| 自動検証 | headless autoplay + timing log analyzer | synthetic fixtureとuser-selected song検証でPASSを返す |

## 3. `.tja` 読み込みスコープ

### 3.1 必須Header

| Header | Phase1扱い | Rust内部モデル |
|---|---|---|
| `TITLE` | 対応。欠落時はファイル名由来の代替名を生成 | `SongMetadata.title` |
| `SUBTITLE` | 対応。表示とログへ保存 | `SongMetadata.subtitle` |
| `BPM` | 対応。初期BPMとして必須 | `Chart.initial_bpm` |
| `WAVE` | 対応。音源path | `SongAudio.path` |
| `PATH_WAV` | 対応。WAVE解決のbase path | `SongAudio.base_path` |
| `OFFSET` | 対応。正負をchart/audio同期へ反映 | `TimingModel.offset_ms` |
| `COURSE` | 対応。指定COURSE抽出に使用 | `CourseId` |
| `LEVEL` | 対応。表示とリザルトへ保存 | `CourseMetadata.level` |
| `BALLOON` | 対応。風船/BalloonExの必要打数へ使用 | `Chart.balloon_counts_by_route` |
| `SCOREINIT` | 対応。score configへ保存 | `ScoreConfig.score_init` |
| `SCOREDIFF` | 対応。score configへ保存 | `ScoreConfig.score_diff` |
| `SCOREMODE` | 対応。Phase1 score modelへ入力 | `ScoreConfig.score_mode` |
| `DEMOSTART` | parse保存。通常プレイでは使用しない | `SongMetadata.preview_start` |

### 3.2 必須Command

| Command | Phase1扱い | 実装責務 |
|---|---|---|
| `#START` | 対応 | 対象COURSEの譜面開始 |
| `#END` | 対応 | 譜面終端と曲終了候補 |
| `#MEASURE` | 対応 | 小節長をschedulerへ反映 |
| `#BPMCHANGE` | 対応 | BPM timelineへ反映 |
| `#DELAY` | 対応 | chart time上の待機として反映 |
| `#SCROLL` | 対応 | 表示位置計算へ反映。判定時刻は変えない |
| `#NMSCROLL` | 対応 | normal scroll modeへ切替 |
| `#BMSCROLL` | 対応 | beat-based scroll modeへ切替 |
| `#HBSCROLL` | 対応 | hybrid/beat-based scroll modeへ切替 |
| `#GOGOSTART` | 対応 | gogo state開始 |
| `#GOGOEND` | 対応 | gogo state終了 |
| `#BARLINEON` | 対応 | 小節線表示状態へ切替 |
| `#BARLINEOFF` | 対応 | 小節線非表示状態へ切替 |
| `#SECTION` | 対応 | 分岐評価区間起点 |
| `#BRANCHSTART` | 対応 | 分岐条件定義 |
| `#N` | 対応 | 普通route譜面 |
| `#E` | 対応 | 玄人route譜面 |
| `#M` | 対応 | 達人route譜面 |
| `#LEVELHOLD` | 対応 | route維持 |
| `#BRANCHEND` | 対応 | 分岐区間終端 |
| `#SUDDEN` | parse/report | 表示互換commandとしてpanicしない |
| `#DIRECTION` | parse/report | 表示互換commandとしてpanicしない |
| `#JPOSSCROLL` | parse/report | 判定ライン移動系としてpanicしない |

## 4. note schedulerスコープ

Phase1では、4分、8分、12分、16分、24分、36分を個別caseとして実装しない。1小節内のnote token数を任意分割として扱い、次の入力から各tokenの発声時刻を計算する。

- 現在BPM
- 現在MEASURE
- 小節内token数
- token index
- DELAY
- OFFSET

この方式で、4/8/12/16/24/36分、32/48相当、混合n分、変拍子、高密度長複合を同じschedulerで扱う。

## 5. ノーツ文字スコープ

| 文字 | 意味 | Phase1扱い |
|---|---|---|
| `0` | Empty | 対応 |
| `1` | Don | 対応 |
| `2` | Ka | 対応 |
| `3` | Big Don | 対応 |
| `4` | Big Ka | 対応 |
| `5` | Roll start | 対応 |
| `6` | Big roll start | 対応 |
| `7` | Balloon | 対応 |
| `8` | Roll/Balloon end | 対応 |
| `9` | BalloonEx / くすだま相当 | 対応 |
| `A` | 2P joint big Don | parse/report |
| `B` | 2P joint big Ka | parse/report |
| `C` | Bomb/Mine | parse/report |
| `D` | BalloonFuze | parse/report |
| `F` | ADLIB | parse/report |
| `G` | Kadon/swap | parse/report |
| `H` | RollClap/RollPa系 | parse/report |
| `I` | RollPa系 | parse/report |

## 6. 分岐譜面スコープ

Phase1では譜面分岐を通常プレイ対象に含める。

必須対応:

- `#SECTION`
- `#BRANCHSTART`
- `#N`
- `#E`
- `#M`
- `#LEVELHOLD`
- `#BRANCHEND`
- 精度条件
- 良/可/不可比率
- 連打条件
- 風船条件
- score条件
- route別BALLOON配列
- route別note stream

headless autoplayでは、route coverage用の入力profileを複数持つ。最終acceptanceでは、N/E/Mの各routeを少なくともsynthetic fixtureで検証する。

## 7. SCROLL / 表示互換スコープ

必須対応:

- 正SCROLL
- 負SCROLL
- 0 SCROLL
- 高速SCROLL
- 追い越し表示
- NMSCROLL
- BMSCROLL
- HBSCROLL

parse/report対象:

- 複素SCROLL
- SUDDEN
- DIRECTION
- JPOSSCROLL

判定は表示座標ではなくchart timeで行う。表示ギミックによりノーツ位置が逆転しても、判定時刻はschedulerの結果を正とする。

## 8. Score / Combo / Gauge / Clearスコープ

Phase1では、通常プレイ完走と回帰検証に必要なscore/gaugeを実装する。

- SCOREINIT/SCOREDIFF/SCOREMODEを読み込む。
- 通常ノーツ、大音符、roll、balloon、BalloonExを加点対象にする。
- GOGO stateをscore eventへ反映する。
- combo、max comboを保持する。
- gaugeを0.0〜100.0でclampする。
- clear threshold以上でclearを返す。
- result JSONにscore/gauge/clearを出す。

OpenTaikoの全score世代の完全互換はOpenTaiko research調査で採用判断を固定する。Phase1では、通常プレイ完走と検証の安定性を満たすscore modelを必須とする。

## 9. Audio / runtimeスコープ

- WAVE/PATH_WAVからBGMを読み込む。
- OFFSET正負をchart/audio比較へ反映する。
- 描画あり実行ではaudio backendから再生位置を取得する。
- headlessでは仮想audio clockを使用する。
- timing logへaudio_started、audio_time_ms、chart_audio_delta_msを出す。

## 10. 検証スコープ

Phase1の検証は二層にする。

1. synthetic fixtures: 25〜35譜面
2. user-selected real songs: 標準10曲カテゴリ

Synthetic fixturesは仕様網羅を確認する。User-selected songsは実戦互換を確認する。曲・音源・譜面データはbundleへ含めない。ユーザーがローカルへ配置し、manifestで参照する。

## 11. compatibility contract以降の未確定項目

次はOpenTaiko researchでOpenTaiko実装を調査して確定する。

- 複素SCROLLの具体的な内部表現
- SUDDEN/DIRECTION/JPOSSCROLLのPhase1最小再現深度
- OpenTaiko score世代とPhase1 score modelの対応
- 分岐条件の正確な閾値計算
- BalloonExの細部
- BMSCROLL/HBSCROLLの座標式
