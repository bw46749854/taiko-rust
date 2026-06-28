# 21_phase1_non_scope: Phase1非スコープ定義

作成日: 2026-06-25
Status: canonical
目的: CodexがPhase1中に不要機能へ広がることを防ぎ、OpenTaiko通常プレイ対応範囲と検証基盤へ収束させる。

## 1. 非スコープ定義の原則

Phase1の非スコープは、通常プレイ完走に必要なOpenTaiko対応譜面要素を除外するための文書ではない。分岐譜面、BMSCROLL/HBSCROLL、BalloonEx、score/gauge、GOGO、BARLINEはPhase1対象である。

非スコープは次のいずれかに該当する項目に限定する。

1. 通常プレイではないモード
2. 多人数・対戦・オンライン・管理機能
3. スキン、BGA、lyrics、camera、object等の演出系
4. Phase2へ送るプレイオプション
5. 商用再現、権利不明アセット、既存C#コードの逐語移植

非スコープを検出したときは、明示的なcompatibility reportを出す。panic、無音正常終了、黙殺は不可とする。

## 2. モード・人数・ゲーム種別の非スコープ

| 項目 | 非スコープ内容 | Phase1での扱い |
|---|---|---|
| 多人数プレイ | 2P以上、対戦、同時プレイ | 1P以外はreportし、実装対象にしない |
| Dan/段位 | 段位認定、複数曲連結、exam条件 | Explicit non-scope with report |
| AI Battle | AI対戦、battle section、AI performance | Explicit non-scope with report |
| Tower | LIFE/Tower専用ゲージ | Explicit non-scope with report |
| Konga | Taiko以外のgame type | Explicit non-scope with report |
| Training | 小節移動、練習UI、bookmark | Phase3+ |
| Online/Heya | 部屋、通信、スコア送信 | Phase3+ |

## 3. 譜面仕様に関する非スコープ

次は非スコープではない。Phase1対象である。

- 譜面分岐
- `#SECTION`, `#BRANCHSTART`, `#N`, `#E`, `#M`, `#LEVELHOLD`, `#BRANCHEND`
- BPMCHANGE, MEASURE, DELAY, OFFSET
- GOGO START/END
- BARLINE ON/OFF
- SCROLL正負/0/高速
- NMSCROLL/BMSCROLL/HBSCROLL
- 大音符、大連打、風船、BalloonEx
- SCOREINIT/SCOREDIFF/SCOREMODE、score/gauge/clear

Phase1の譜面仕様上の非スコープは、通常プレイ完走に不要な演出・モード・特殊ゲーム種別に限る。

| 項目 | 非スコープ内容 | Phase1での扱い |
|---|---|---|
| BGA/動画制御 | BGVIDEO、動画再生、映像同期 | report。通常プレイ継続可 |
| Lyrics | 歌詞表示、歌詞同期 | report。通常プレイ継続可 |
| Camera/Object | カメラ、オブジェクト、Lua演出 | report。通常プレイ継続可 |
| Skin command | OpenTaiko skin座標・演出完全指定 | report。通常プレイ継続可 |
| Dan専用命令 | 段位用exam、複数曲連結 | reportし、通常プレイ対象から除外 |
| Tower専用命令 | LIFE/Tower専用条件 | reportし、通常プレイ対象から除外 |

## 4. Must parse / must not crash項目

以下は非スコープではない。完全gameplay実装対象ではないが、OpenTaiko譜面に出る可能性があるため、parseし、reportし、panicしない。

- Mine / Bomb
- ADLIB
- BalloonFuze
- Kadon / swap note
- A/B 2P joint note
- Konga系H/I
- 複素SCROLL
- SUDDEN
- DIRECTION
- JPOSSCROLL

これらの扱いは `docs/25_phase1_feature_classification.md` に従う。

## 5. UI/UXの非スコープ

| 項目 | 非スコープ内容 | Phase1での扱い |
|---|---|---|
| 高度な曲選択画面 | ジャンル、ソート、検索、ランダム、フォルダ演出 | CLI指定と最小リストのみ |
| スキンシステム | 外部スキン読込、解像度別配置、テーマ切替 | 固定レイアウトのみ |
| アニメーション演出 | キャラ、踊り子、背景演出、歓声、花火 | 非対象 |
| 動画再生 | AVI/BGA/BGVIDEO/PREVIEW動画 | 非対象 |
| 背景画像完全表示 | PREIMAGE/BACKGROUNDの完全再現 | metadata/reportまで |
| リッチリザルト | 称号、演出、保存演出、段位表示 | JSONと最小画面に限定 |
| キーコンフィグUI | ゲーム内割当編集 | config fileまたは固定mappingのみ |

## 6. オプション・設定の非スコープ

Phase2はプレイオプションを組み合わせて変更できる状態を扱う。Phase1では、通常プレイの固定条件を正しく実行する。

| 項目 | 非スコープ内容 | Phase1での扱い |
|---|---|---|
| プレイヤーSpeed option | ユーザー指定速度変更 | `.tja` の `#SCROLL` はPhase1対象 |
| Reverse | 逆走、レーン反転 | Phase2 |
| Random | ノーツ種別ランダム化 | Phase2 |
| Hidden/Doron/Stealth | プレイオプションとしての非表示 | Phase2 |
| Autoのゲーム内切替 | プレイ中のAuto切替 | headless autoplayのみPhase1 |
| Judge補正UI | 手動offset調整UI | config注入のみ |
| Skin選択 | テーマ切替 | 固定assetのみ |
| Song speed | 再生速度変更 | Phase2+ |
| 特殊ゲージ | Hard/Tight等 | Phase2+ |

## 7. OpenTaiko互換性の非スコープ

Rust版Phase1はOpenTaiko互換クローンを作る作業ではない。次を非対象とする。

- OpenTaikoのディレクトリ構造の再現
- OpenTaikoのC#クラス名、関数名、内部状態名の逐語的移植
- OpenTaikoの描画順、演出、スキン座標の完全再現
- OpenTaikoの全モード網羅
- OpenTaikoのアセットや商用由来アセットの同梱
- 商用ゲームのUI、演出、挙動の正確な複製

## 8. 音声・デバイスの非スコープ

| 項目 | 非スコープ内容 | Phase1での扱い |
|---|---|---|
| 複数音声backend完全対応 | ASIO/WASAPI/DirectSound等の全対応 | 採用backendを固定し、抽象境界を作る |
| デバイス別最適化 | 個別遅延profileの自動測定 | timing logへ差分を出す |
| 効果音ミキサー完全再現 | Don/Ka SE、歓声、環境音の完全mix | BGM再生をP0。hit soundは最小 |
| ラウドネス解析 | 音量自動正規化 | 非対象 |

## 9. 権利・配布の非スコープ

- 商用曲、商用譜面、商用画像、商用音源の同梱
- 権利不明のTJA、音源、画像、フォントの同梱
- OpenTaiko外部アセットの無断再配布
- 商用ゲームに酷似するUI/演出の正確な再現

User-selected songsはローカルmanifestで参照する。bundle、repository、PRには曲データを含めない。
