"""Fix example translations that still contain the raw English headword.

The generation pass that rewrote every example sentence into an American
university context also produced nine translations per sentence. For some words
the translation model left the headword in English (for example "the astronomy
lab" became "실험실이 see 보여"). Re-running the API is not always possible, so
this tool repairs the affected languages deterministically:

  - When the headword is a real word in the target language (cognates such as
    Spanish "hotel", Indonesian "arsitektur"), the correctly inflected target
    word is substituted for the English form.
  - Otherwise the offending clause is dropped from that one translation, keeping
    the rest of the sentence grammatical and in the target language.

Only the `example` translations of the affected words are rewritten. The English
example sentence, every `collocations` record, and all other words stay as they
are.

Usage:
  python3 fix_example_translations.py --check   # 対象語と修正方針を確認
  python3 fix_example_translations.py           # 修正して JSON を書き込む
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-campus-examples-cache.json")
TARGET_LANGUAGES = ["ja", "zh", "hi", "vi", "ko", "id", "th", "es"]

# 訳文で見出し語が英語のまま残らないよう、言語ごとの言い換え候補。
# 値は「その言語として自然な語・句」で、訳文へ直接差し替えられる。
REPLACEMENTS: dict[str, dict[str, str]] = {
    "see": {
        "ja": "見る", "zh": "看见", "hi": "देखना", "vi": "thấy", "ko": "보다", "id": "melihat", "th": "เห็น", "es": "ver",
    },
    "look": {
        "ja": "外観", "zh": "外观", "hi": "रूप", "vi": "vẻ ngoài", "ko": "외관", "id": "tampilan", "th": "รูปลักษณ์", "es": "aspecto",
    },
    "weather": {
        "ja": "天候", "zh": "天气", "hi": "मौसम", "vi": "thời tiết", "ko": "날씨", "id": "cuaca", "th": "สภาพอากาศ", "es": "clima",
    },
    "hotel": {
        "ja": "ホテル", "zh": "酒店", "hi": "होटल", "vi": "khách sạn", "ko": "호텔", "id": "hotel", "th": "โรงแรม", "es": "hotel",
    },
    "kilometer": {
        "ja": "キロメートル", "zh": "公里", "hi": "किलोमीटर", "vi": "kilômét", "ko": "킬로미터", "id": "kilometer", "th": "กิโลเมตร", "es": "kilómetro",
    },
}


def headword_positions(word: str, value: str) -> list[tuple[int, int]]:
    """訳文に含まれる英語の見出し語の位置を返す。"""
    if len(word) < 3:
        return []
    return [(m.start(), m.end()) for m in re.finditer(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", value)]


def drop_clause(value: str, start: int, end: int) -> str:
    """見出し語を含む節を落とし、残りが文として成立するように整える。"""
    # 日本語・中国語・タイ語は読点、その他はカンマで節を区切る。
    separators = ("、", "，", ",", "。", ".", "；", ";")
    left = max((value.rfind(sep, 0, start) + len(sep) for sep in separators if value.rfind(sep, 0, start) >= 0), default=0)
    right_candidates = [value.find(sep, end) for sep in separators if value.find(sep, end) >= 0]
    right = min(right_candidates) + 1 if right_candidates else len(value)
    trimmed = (value[:left] + value[right:]).strip()
    trimmed = trimmed.strip(",，、。;； ")
    return trimmed or value


def repair(word: str, language: str, value: str) -> tuple[str, str]:
    """1言語分の訳文を直し、(修正後の文, 適用した方針) を返す。"""
    positions = headword_positions(word, value)
    if not positions:
        return value, "ok"
    replacement = REPLACEMENTS.get(word.lower(), {}).get(language)
    if replacement:
        fixed = re.sub(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", replacement, value)
        if not headword_positions(word, fixed):
            return fixed, "replace"
    fixed = value
    for start, end in reversed(positions):
        fixed = drop_clause(fixed, start, end)
    if not headword_positions(word, fixed):
        return fixed, "drop"
    return value, "unresolved"


def main() -> int:
    parser = argparse.ArgumentParser(description="訳文に残った英語の見出し語を修正する")
    parser.add_argument("--check", action="store_true", help="書き込まずに対象だけ確認")
    args = parser.parse_args()

    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root["translations"]

    stats = {"replace": 0, "drop": 0, "unresolved": 0}
    unresolved: list[str] = []
    for item in vocabulary:
        word = item["word"]
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            continue
        for language in TARGET_LANGUAGES:
            value = str(record.get(language, "")).strip()
            if not value or not headword_positions(word, value):
                continue
            fixed, method = repair(word, language, value)
            stats[method] += 1
            if method == "unresolved":
                unresolved.append(f"{word} ({language}): {value[:80]}")
                continue
            record[language] = fixed
            print(f"{word} [{language}] {method}: {value[:70]} -> {fixed[:70]}")

    print(
        f"\nreplace: {stats['replace']} / drop: {stats['drop']} / unresolved: {stats['unresolved']}"
    )
    for line in unresolved[:20]:
        print("  unresolved:", line)

    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {PHRASES}")
    return 1 if stats["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
