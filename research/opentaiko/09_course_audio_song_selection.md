# 09_course_audio_song_selection: course / audio / song selection調査

作成日: 2026-06-25  
状態: Step2正式採用  
参照source: `OpenTaiko/src/Songs/CTja.cs`

## 1. 結論

Phase1は、複数COURSEを含むTJAから任意の難易度を選択して通常playできることを必須にする。audioは `WAVE`, `PATH_WAV`, `OFFSET` を扱い、実音源ファイルはbundleへ含めない。

## 2. Course選択

`COURSE:` は複数難易度譜面の境界を表す。Rust版Phase1では、parserが全course metadataを読み、runtimeに渡すcourseを明示的に選択する。

```text
SelectedChart {
  title,
  subtitle,
  course,
  level,
  side,
  audio_path,
  events,
}
```

## 3. 複数COURSEの合格条件

- 同一TJA内に複数courseが存在しても、指定courseだけを実行できる。
- 指定courseに分岐がある場合、branch routeも実行できる。
- metadataはcourseごとに保持する。
- user-selected song validationでは、manifestにcourse/difficultyを明記する。

## 4. Audio path

採用する解決順序:

1. manifestで指定されたTJA pathを基準にする。
2. `PATH_WAV:` があればaudio base pathとして扱う。
3. `WAVE:` の値をbase pathへ結合する。
4. ファイルが存在しない場合、headlessではsilent audio adapterへfallbackし、compatibility warningを出す。
5. 描画あり通常実行ではaudio missingを明確なerrorにする。

## 5. OFFSET

`OFFSET:` はchart/audio syncの中核である。Phase1では正負OFFSETをサポートし、timing logへ `offset_signed_ms` を必ず出す。

## 6. Non-scope

`#NEXTSONG` による段位/複数曲連結はPhase1非スコープにする。検出時はreportし、通常1曲playへは入れない。
