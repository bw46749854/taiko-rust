# Adoption Decision Template

作成日: 2026-06-25

## 1. Decision ID

`AD-YYYYMMDD-XXX`

## 2. 対象機能

対象command、note type、runtime機能を書く。

## 3. OpenTaiko観測結果

参照sourceと観測結果を書く。

## 4. 採用分類

- Must implement gameplay
- Must parse / must not crash
- Explicit non-scope with report

## 5. 採用内容

Rust版Phase1で実装する内容を固定する。

## 6. 非採用内容

Phase1に入れない内容を固定する。

## 7. Report方針

parse warning、compatibility warning、explicit non-scope reportのどれを出すかを書く。

## 8. Review checklist

- OpenTaiko source参照がある。
- Phase1分類が1つに決まっている。
- test / fixture要求がある。
- 未解決事項がticketへ接続されている。
