# 24_phase1_normal_play_compatibility_contract: Phase1通常プレイ互換契約

作成日: 2026-06-25  
状態: Step1新規・採用候補  
入力: `research/opentaiko/10_phase1_adoption_decisions.md`

## 1. 目的

この文書は、Phase1でいう「任意の曲を通常プレイできる」の意味を固定するCompatibility Contractである。

Phase1は、単一の簡単な曲を再生できる状態を目標にしない。OpenTaikoが通常プレイで対応している譜面要素を含む曲を、1P通常プレイとして完走し、結果を生成し、AIがheadless autoplayとtiming log analyzerで検証できる状態を目標にする。

## 2. 正式定義

Phase1の「任意の曲を一曲プレイできる」とは、次をすべて満たすことである。

1. ユーザーがローカルに配置した `.tja` と音源を読み込める。
2. `.tja` 内の複数COURSEから指定COURSEを選択できる。
3. OpenTaiko通常プレイ対応範囲の譜面要素をparseできる。
4. Must implement gameplay項目を通常プレイへ反映できる。
5. Must parse / must not crash項目でpanicしない。
6. Explicit non-scope with report項目を明示reportへ出す。
7. 曲開始から曲終了までruntime panicなしに進行できる。
8. score、combo、gauge、clear、resultを生成できる。
9. headless autoplayで再現可能に実行できる。
10. timing log analyzerで合否を判定できる。

## 3. Phase1で必須となる通常プレイ要素

### 3.1 note / scheduler

- 任意分割note scheduler
- 4分、8分、12分、16分、24分、36分
- 32分、48分相当の高密度配置
- 異なるn分音符の混合
- Don / Ka
- 大Don / 大Ka
- 通常連打
- 大連打
- 風船連打
- BalloonEx / くすだま相当

### 3.2 timing

- BPMCHANGE
- MEASURE
- DELAY
- OFFSET正負
- WAVE
- PATH_WAV
- 音声開始時刻
- chart/audio delta logging

### 3.3 display / scroll

- GOGO START/END
- BARLINE ON/OFF
- 小節線表示状態
- SCROLL正値
- SCROLL負値
- SCROLL 0
- 高速SCROLL
- 追い越し
- NMSCROLL
- BMSCROLL
- HBSCROLL

### 3.4 branching

- SECTION
- BRANCHSTART
- N/E/M route
- LEVELHOLD
- BRANCHEND
- 精度分岐
- 良/可/不可条件
- 連打条件
- 風船条件
- score条件
- 分岐別BALLOON配列

### 3.5 score / gauge

- SCOREINIT
- SCOREDIFF
- SCOREMODE
- 通常ノーツ配点
- roll配点
- balloon配点
- GOGO state
- combo
- gauge
- clear判定
- result summary

## 4. 互換深度の分類

Phase1は、OpenTaiko通常プレイ要素を次の3分類で扱う。

| 分類 | 契約 |
|---|---|
| Must implement gameplay | 通常プレイ・headless・analyzerの全経路で実装する |
| Must parse / must not crash | parse/reportし、panicを禁止する。通常プレイ完全再現はStep2で採用判断する |
| Explicit non-scope with report | 実装対象に入れない。検出時にreportし、Phase1完了判定から除外する |

分類の正本は `docs/25_phase1_feature_classification.md` とする。

## 5. 検証契約

Phase1の合格判定は、synthetic fixtureとuser-selected songの二層で行う。

### 5.1 Synthetic fixture

Synthetic fixtureは仕様網羅のために使う。Step3で25〜35譜面へ分割する。

最低限、次を網羅する。

- 基本note
- 任意分割
- 混合n分
- BPM/MEASURE/DELAY/OFFSET
- roll/balloon/BalloonEx
- GOGO/BARLINE
- branch
- scroll
- course/audio
- compatibility report
- integrated mixed gimmick
- long stability

### 5.2 User-selected songs

User-selected songsは実戦互換のために使う。標準10カテゴリで検証する。

1. 基本譜面
2. 高密度譜面
3. 変拍子・BPM譜面
4. 連打譜面
5. 分岐譜面A
6. 分岐譜面B
7. scroll譜面
8. HB/BM/特殊表示譜面
9. 総合混合譜面
10. 長尺・負荷譜面

曲・音源・譜面データはbundleへ含めない。ユーザーのローカル環境に配置し、manifestで参照する。

## 6. 合格判定

Phase1 PASSには次が必要である。

- Must implement gameplay項目のsynthetic coverageが100%。
- user-selected song 10カテゴリが全て検証済み。
- headless autoplayが全対象で曲終了まで進行。
- timing log analyzerがPASS。
- compatibility reportに未処理panicが0件。
- non-scope項目が実装scopeに混入していない。
- QA/回帰検証Sessionが最終reportを作成。

## 7. Step2へ送る未確定項目

Step1ではCompatibility Contractを固定する。次の細部はStep2のOpenTaiko実装調査で確定する。

- 複素SCROLLの数値表現
- SUDDEN/DIRECTION/JPOSSCROLLの最小再現深度
- score modeごとの細部
- 分岐条件の正確な計算式
- BalloonExの成功条件と配点
- BMSCROLL/HBSCROLLの座標式
