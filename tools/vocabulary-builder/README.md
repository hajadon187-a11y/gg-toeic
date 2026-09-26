# TOEFL Vocabulary Builder

TOEFL向けの学術語彙データを生成するための作業領域です。

## 方針

- アプリが読む正本は `app/src/main/assets/vocabulary.json` の1つだけです。
- 語彙の追加・削除・レベル変更は、生成前にJSON監査を通します。
- 単語の出典とライセンス条件を記録します。
- TOEFLのスコアを単語1語から保証する表現は使わず、学習レベルの目安として管理します。

## 現在の主要スクリプト

- `build_vocabulary.py`: 語彙の収集・分類・補完・JSON出力
- `build_merged_vocabulary.py`: NGSL / NAWL / AWL の統合
- `download_new_lists.py`: 公開語彙リストの取得
- `generate_translations.py`: 多言語訳の生成
- `generate_all_phrase_translations.py`: コロケーション訳の生成
- `add_collocations.py`: コロケーションの補完
- `audit_toefl_vocabulary.py`: 出荷前の語彙アセット監査
- `select_campus_academic_words.py`: キャンパスライフ／講義トピックの追加候補を既存語彙と突き合わせて重複排除

## 例文・コロケーションの品質監査（外部API不要）

`audit_phrase_quality_precise.py` を出荷前のゲートとして使用します。単語・意味・例文・
コロケーション・多言語訳の関係を全6,384語について決定論的に検査し、確定エラーと
確認候補を分離します。翻訳APIは呼ばず、出荷済みJSONだけで完結します。

旧`audit_phrase_quality.py`は検出漏れを減らすための広い候補抽出用で、固有名詞、
語例、補足読点、派生語、同義訳を誤検出するため、合否判定や自動修正の根拠には使いません。

| 検証軸 | 内容 |
|---|---|
| レコード整合性 | 6,384語と翻訳レコードのID・sourceが一致するか |
| 意味訳 | 8言語の意味訳が存在し、対象言語の文字種で書かれているか |
| Example | 8言語の訳が存在し、対象言語の文字種・ベトナム語表記を満たすか |
| Collocation | 明白な英語原文の破損、空欄、未翻訳コピーがないか |
| 誤検出抑制 | 固有名詞、英語の語例、補足読点、派生語、同義訳は警告に留める |

```bash
python3 audit_phrase_quality_precise.py                 # 確定エラーがあれば終了コード1
python3 audit_phrase_quality_precise.py --json out.json # JSONレポートも出力
```

`repair_phrase_quality.py`は、区切り記号や重複項目を一括変換するため、自然な訳文中の
読点や正当な反復まで壊す可能性があります。自動修正には使わず、修正は
`repair_vocabulary_quality_issues.py`の明示的な修正表を通して行います。

| 修正 | 内容 | 実績 |
|---|---|---|
| 韓国語の動詞活用 | 좋아하다한다 → 좋아한다、분리하다하라고 → 분리하라고 | 39 |
| 韓国語の人名 | Maya → 메이야 など | 24 |
| 中国語の区切り | ； → ， | 78 |
| 日本語の区切り | , → 、 | 531 |
| ヒンディー語の区切り | ، / ; → , | 24 |
| 米英綴りの整合 | gynaecologist → gynecologist（見出し語に合わせる） | 8 |
| 説明カッコの除去 | bat (animal) / breed (type) を項目ごと削除し訳文も同期 | 2 |
| 重複項目の除去 | firstly, firstly … の重複 | 1 |

```bash
python3 audit_phrase_quality_precise.py     # 修正前後の確定エラーを確認
python3 repair_vocabulary_quality_issues.py # 明示済みの高信頼修正だけを反映
python3 audit_toefl_vocabulary.py           # 既存の出荷前監査（回帰確認）
```


## 例文の大学文脈化（全6,384語）

例文を「アメリカの大学の講義・教科書・教授と学生の会話」に合わせて作り直し、
その訳文（9言語）も同時に作り直す一連のツールです。

| スクリプト | 役割 |
|---|---|
| `rewrite_examples_campus.py` | 全語の例文を大学文脈へ書き換え、例文の9言語訳を生成（`--revalidate` で検査に落ちた語だけ生成し直す） |
| `restore_example_cache.py` | 出荷済み JSON から作業キャッシュを復元（API を呼ばずに再検査したいとき） |
| `apply_example_rewrites.py` | 生成結果を `vocabulary.json` と `vocabulary_phrase_translations.json` へ反映 |
| `translate_example_gaps.py` | 訳文に英語のまま残った見出し語を検出し、訳語へ置き換え |
| `fix_nonlatin_examples.py` | 日本語・韓国語・中国語・タイ語・ヒンディー語の訳文に残った英語句を訳出 |
| `apply_example_gap_fixes.py` | 収集済みの訳語辞書を API なしで反映 |
| `clean_example_artifacts.py` | 機械置換で生じた表記の乱れ（重複語・余分な空白）を整える |
| `fix_final_example_translations.py` | 最後まで残った個別の訳文を修正 |

```bash
cd tools/vocabulary-builder

python3 rewrite_examples_campus.py --dry-run   # 対象件数の確認
python3 rewrite_examples_campus.py             # 全語の例文と訳を生成
python3 rewrite_examples_campus.py --revalidate # 検査に落ちた語だけ作り直す

python3 apply_example_rewrites.py              # 生成結果をアセットへ反映
python3 translate_example_gaps.py              # 訳文の英語残りを検出・解消
python3 fix_nonlatin_examples.py               # 非ラテン文字言語の英語残りを解消
python3 clean_example_artifacts.py             # 表記の乱れを整える
python3 audit_toefl_vocabulary.py              # 出荷前監査
```

作業中の生成結果は `/private/tmp/toefl-campus-examples-cache.json` などに保存されるため、
中断しても再開できます。

## 言語別スライスとネイティブ監査（1言語ずつ）

9言語を同時に判定しようとすると、`vocabulary.json`（6.1MB）と
`vocabulary_phrase_translations.json`（19MB）で約450万トークンになり、1回の判定には大きすぎます。
そこで資産を**言語ごとに切り出し、1言語ずつ監査**します。

`extract_language_slices.py` は出荷資産を `data/slices/{lang}.json` へ分割します
（APIは呼びません。出荷資産も書き換えません）。

| スライスの中身 | 用途 |
|---|---|
| `word` / `exampleSource` / `collocationsSource` / `meaningEn` | ネイティブ判定の比較元（英語） |
| `meaning`（その言語の意味1フィールドのみ） | 判定対象 |
| `example` / `collocations`（その言語の訳のみ） | 判定対象 |

```bash
python3 extract_language_slices.py                 # 全8言語のスライスを作成
python3 extract_language_slices.py --only es zh    # 一部の言語だけ
python3 extract_language_slices.py --dry-run       # 書き込まず見積りだけ
```

| 言語 | 訳文の文字数 | 推定トークン（英語比較元を除く） |
|---|---:|---:|
| zh | 243,989 | 約 15万 |
| ja | 327,819 | 約 20万 |
| ko | 382,336 | 約 24万 |
| vi | 440,508 | 約 13万 |
| id | 453,323 | 約 14万 |
| es | 503,050 | 約 15万 |
| th | 812,586 | 約 51万 |
| hi | 842,110 | 約 53万 |

`audit_language_slices.py`はLUNA外部APIを呼び出すAPI用ツールです。外部APIを使わない運用では
実行しません。スライス生成とバッチ数確認だけはAPIなしで利用できますが、ネイティブ自然さの
自動判定をこのスクリプト単体で行うことはできません。

```bash
python3 audit_language_slices.py --only es --dry-run   # 対象件数の確認
python3 audit_language_slices.py --only es --limit 40  # 疎通確認
python3 audit_language_slices.py --only es             # 1言語を全件
python3 audit_language_slices.py --all                 # 8言語を順に全件
python3 audit_language_slices.py --only es --apply     # 結果を出荷資産へ反映
```

- 進捗は `(言語, ID)` 単位で `/private/tmp/toefl-language-audit-cache.json` に保存され、
  中断しても続きから再開できます。修正なしと確定した語も記録するため再送しません。
- モデルの訳文は文字種・英字残り・コロケーション項目数を機械検査し、通ったものだけ採用します。
  ただし、このAPI用スクリプトは外部APIを使わない運用の監査ゲートではありません。

## キャンパスライフ・講義トピックの追加語（TOEFL L3 / L4）

`data/toefl_campus_academic_candidates.json` に追加候補語を管理し、
`select_campus_academic_words.py` で既存 `app/src/main/assets/vocabulary.json` と照合して重複を除外する。

```
python3 tools/vocabulary-builder/select_campus_academic_words.py
```

- 入力: `data/toefl_campus_academic_candidates.json`（`word` / `level` / `topic` / `domain`）
- 出力: `data/toefl_campus_academic_selection.json`（決定版リスト＋除外理由）
- `topic` はビルダー既存の `Education` / `Science` / `Society` / `Environment` / `Technology` から選ぶ
- `domain` は選定作業用の分類（履修登録・図書館・寮・天文学・地質学・考古学・心理学 など）で、
  アプリのデータには出力しない
- 除外された語は `excluded.already_in_vocabulary` に既存レベル付きで記録されるため、
  「既存語だが本来はL3/L4にあるべき語」の見直しにも使える

追加する場合は、`candidates.json` の `words` に追記 → 上記スクリプトを再実行 →
`selection.json` の語に対して `build_vocabulary.py` と同じ形式で
`meaning` / `meaningEn` / `synonyms` / `collocations` / `example` と多言語訳を補完する。

レベル設計と監査ルールは、TOEFL用の基準を確定後にここへ追加します。
