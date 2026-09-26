"""Fix the last two example-translation defects found by the gap scan.

`translate_example_gaps.py` reduced the untranslated-word defects from 9,765 rows
to two rows where the English word must be replaced by an idiomatic phrase rather
than a single word:

  - Spanish:    "No queda much comida ..."      -> "No queda mucha comida ..."
  - Vietnamese: "điểm IQ không thể ..."          -> "chỉ số IQ không thể ..."

Both are one-off wording fixes, so they are applied explicitly rather than through
a general replacement table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"

# (語, 言語, 修正前の断片, 修正後の断片)
FIXES = [
    ("much", "es", "queda much comida", "queda mucha comida"),
    ("IQ", "vi", "điểm IQ", "chỉ số IQ"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="残った2件の訳文を修正する")
    parser.add_argument("--check", action="store_true", help="書き込まずに確認")
    args = parser.parse_args()

    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root["translations"]
    by_word = {item["word"]: item for item in vocabulary}

    applied = 0
    for word, language, before, after in FIXES:
        item = by_word.get(word)
        if item is None:
            print(f"skip: {word} が語彙にありません")
            continue
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            print(f"skip: {word} の example 訳がありません")
            continue
        value = str(record.get(language, ""))
        if before not in value:
            print(f"skip: {word} [{language}] に想定の断片がありません: {value[:70]}")
            continue
        record[language] = value.replace(before, after)
        applied += 1
        print(f"{word} [{language}]: {value[:70]} -> {record[language][:70]}")

    print(f"applied: {applied}/{len(FIXES)}")
    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {PHRASES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
