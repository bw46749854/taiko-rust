# 26_phase1_user_selected_song_validation: ユーザー選定曲検証方針

作成日: 2026-06-25
状態: canonical
入力: `research/opentaiko/10_phase1_adoption_decisions.md`

## 1. 目的

この文書は、Phase1の実戦互換検証に使うuser-selected song validationの方針を定義する。

Synthetic fixturesは仕様網羅を検証する。User-selected songsは、OpenTaiko通常プレイ対応譜面を実曲で完走できることを検証する。

## 2. 基本方針

- 曲、音源、譜面データはrepository、PRへ含めない。
- 開発期間モードでは `operations/dev_asset_bundle.example.toml` に従うGoogle Drive zipを `.external_assets/opentaiko/` に展開する。
- 本番モードではユーザーが用意したOpenTaiko互換ディレクトリを `OPENTAIKO_CONTENT_ROOT` または `--content-root` で指定する。
- manifestで曲path、COURSE、検証カテゴリ、期待する主要featureを指定する。
- validation reportにはparse結果、headless結果、timing analyzer結果、compatibility reportを記録する。
- 標準検証数は10曲とする。

## 3. 標準10カテゴリ

| No | カテゴリ | 主に検証する要素 |
|---:|---|---|
| 1 | 基本譜面 | Don/Ka/大音符/小節線/通常BPM |
| 2 | 高密度譜面 | 16/24/36分と混合n分 |
| 3 | 変拍子・BPM譜面 | BPMCHANGE、MEASURE、DELAY、OFFSET |
| 4 | 連打譜面 | 通常連打、大連打、風船、BalloonEx |
| 5 | 分岐譜面A | 精度条件 p/pp 系 |
| 6 | 分岐譜面B | 連打/score/LEVELHOLD/SECTION 系 |
| 7 | scroll譜面 | 低速、高速、負SCROLL、0 SCROLL、追い越し |
| 8 | HB/BM/特殊表示譜面 | HBSCROLL、BMSCROLL、SUDDEN、DIRECTION、JPOSSCROLL |
| 9 | 総合混合譜面 | BPM変化、scroll、連打、分岐の同時出現 |
| 10 | 長尺・負荷譜面 | 長時間、ノーツ数多め、複数ギミック |

## 4. 標準候補曲

以下は検証カテゴリを説明するための標準候補である。曲データは同梱しない。

| No | 曲名 | 難易度 | 主に検証する要素 |
|---:|---|---|---|
| 1 | ドンカマ2000 | おに ★×10 | BPM変化、HS/SCROLL、追い越し、24分、48分相当、極端な低速/高速、大音符 |
| 2 | Sync Your World | おに ★×9 | 8分、12分、16分、24分、混合n分、GOGO、小節線ギミック、縁主体 |
| 3 | Irregular Clock | おに ★×9 | BPM変化、HS、6分追い越し、12分、24分、大音符、連打 |
| 4 | SHOGYO MUJO | おに ★×9 | 譜面分岐、N/E/M、分岐別連打、分岐別score、風船、連打秒数差 |
| 5 | メタルホーク BGM1 | おに ★×10 | 譜面分岐、精度分岐、12分、24分、達人維持、玄人/普通route |
| 6 | 幽玄ノ乱 | おに ★×10 | BPM300、8分、16分、長複合、高密度、長尺gauge、通常連打 |
| 7 | Destr0yer | おに ★×7 | 低BPM、黄色連打、風船、大連打、HS付き連打、no-big-note edge |
| 8 | 美しく忙しきドナウ | おに ★×8 | 3拍子、BPM変化、見た目BPM、12分、連打 |
| 9 | Calamity Fortune | おに ★×10 | 16分長複合、24分、短連打、風船、休符区間、密度変化 |
| 10 | Destr0yer 裏譜面 | おに ★×10 | 追加HS、32/48相当、局所難、表裏差分、裏譜面route |

## 5. Manifestに必要な情報

coverage designでschema化する。compatibility contract時点では、必要fieldを次で固定する。

```yaml
songs:
  - id: user-song-001
    category: basic_chart
    title: ""
    tja_path: ""
    audio_root: ""
    course: Oni
    expected_features:
      - don
      - ka
      - big_note
      - barline
    validation:
      parse: required
      headless_autoplay: required
      timing_analyzer: required
      visual_smoke: optional
```

## 6. Validation reportに必要な情報

```markdown
# User-selected Song Validation Report

- date:
- commit:
- manifest:
- qa session:

## Results

| id | category | title | course | parse | headless | analyzer | compatibility | status |
|---|---|---|---|---|---|---|---|---|

## Coverage

| feature | covered by | status |
|---|---|---|

## Failures

| id | song | failure | related feature | next ticket |
|---|---|---|---|---|
```

## 7. 合格条件

- 10カテゴリすべてがmanifestに存在する。
- 各曲の `.tja` と音源pathが解決できる。
- parseでpanicしない。
- Must implement gameplay対象featureが実行される。
- headless autoplayで曲終了まで進行する。
- timing log analyzerがPASSを返す。
- compatibility warningはreportへ出る。
- Explicit non-scope項目を検出した曲はPhase1合格曲へ数えない。

## 8. coverage designへ送る作業

coverage designで次を作成する。

- `fixtures/user_selected/README.md`
- `fixtures/user_selected/manifests/user_song_manifest.schema.md`
- `fixtures/user_selected/manifests/user_song_manifest.example.md`
- `fixtures/user_selected/reports/user_song_validation_report.schema.md`
- `docs/coverage/phase1_user_song_category_matrix.md`

## 9. OPS-0004 content-root binding

User-selected validation must resolve every `.tja`, audio file, and optional skin/system file relative to the canonical content root. The content root is supplied by `OPENTAIKO_CONTENT_ROOT` or `--content-root`. In CI development mode this root is `.external_assets/opentaiko/` after `scripts/fetch_dev_asset_bundle.py` verifies the Drive zip sha256. Missing development assets are reported as `block`; committed user-selected assets are rejected.
