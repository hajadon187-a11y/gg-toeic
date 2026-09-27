#!/usr/bin/env python3
"""Review the final 22 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "alcohol": "そのレストランの営業許可は酒類の提供を認めている。",
    "festival": "会社は地域の祭りに協賛した。",
    "confident": "応募者は面接中、自信に満ちた様子だった。",
    "curve": "グラフは月間売上の曲線を示している。",
    "knee": "従業員は箱を運んでいるときに膝をけがした。",
    "depth": "技術者は基礎の深さを測定した。",
    "entrance": "正面玄関をお使いください。",
    "log": "システムはすべての取引を記録する。",
    "giant": "会社は海外から大口注文を受けた。",
    "god": "博物館は古代の神の像を展示した。",
    "extensive": "会社は大規模な市場調査を実施した。",
    "interpret": "マネージャーは会議前にグラフを解釈するよう私たちに求めた。",
    "independence": "新しい支店はより大きな独立性を持って運営されている。",
    "inner": "内側の包装が輸送中の製品を保護する。",
    "harm": "新しい方針は環境への害を防ぐ。",
    "consult": "署名する前に法務部へ相談してください。",
    "intervention": "そのプロジェクトには経営陣の介入が必要だった。",
    "impress": "プレゼンテーションは顧客に好印象を与えた。",
    "exam": "資格試験は金曜に予定されている。",
    "behave": "従業員は顧客との会議でプロらしく振る舞わなければならない。",
    "loud": "廊下の音楽が大きかったため、マネージャーはドアを閉めるよう求めた。",
    "dimension": "荷物の寸法は配送ラベルに記載されている。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][1300:]
    assert {str(item["word"]).casefold() for item in level_rows} == set(JA)
    changed = 0
    for item in level_rows:
        key = f"builtin:{item['id']}"
        example = translations.setdefault(key, {}).setdefault("example", {})
        source = str(item["example"]).strip()
        if example.get("source") != source:
            example["source"] = source
            changed += 1
        if example.get("en") != source:
            example["en"] = source
            changed += 1
        value = JA[str(item["word"]).casefold()]
        if example.get("ja") != value:
            example["ja"] = value
            changed += 1
    VOCAB_PATH.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    PHRASE_PATH.write_text(json.dumps(phrase_root, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"reviewed 500+ Japanese examples batch 14: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
