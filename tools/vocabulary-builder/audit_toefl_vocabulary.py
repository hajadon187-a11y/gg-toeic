#!/usr/bin/env python3
"""Audit the TOEFL vocabulary asset before it is shipped in the Android app."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VOCABULARY_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
REQUIRED_FIELDS = {
    "id",
    "word",
    "meaning",
    "meaningEn",
    "synonyms",
    "collocations",
    "example",
    "level",
    "topic",
    "source_list",
}
PHRASE_TYPES = ("example", "collocations")
PHRASE_LANGUAGES = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es", "en")


def normalize_word(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def fail(message: str) -> None:
    print(f"ERROR: {message}")


def main() -> int:
    vocabulary = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    phrase_translations = phrase_root.get("translations", {})
    errors: list[str] = []

    ids = [item.get("id") for item in vocabulary]
    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        errors.append(f"duplicate ids: {duplicate_ids[:10]}")

    words: dict[str, int] = {}
    for item in vocabulary:
        missing = sorted(REQUIRED_FIELDS - item.keys())
        if missing:
            errors.append(f"{item.get('id', '?')} missing fields: {', '.join(missing)}")
        word = normalize_word(str(item.get("word", "")))
        if not word:
            errors.append(f"{item.get('id', '?')} has an empty word")
        elif word in words:
            errors.append(f"duplicate word: {item.get('word')} (ids {words[word]} and {item.get('id')})")
        else:
            words[word] = item.get("id", -1)

        level = item.get("level")
        if not isinstance(level, int) or not 1 <= level <= 5:
            errors.append(f"{item.get('word', '?')} has invalid level: {level!r}")
        for field in ("meaning", "meaningEn", "example", "topic", "source_list"):
            if not str(item.get(field, "")).strip():
                errors.append(f"{item.get('word', '?')} has an empty {field}")
        if "IELTS" in json.dumps(item, ensure_ascii=False) or "雅思" in json.dumps(item, ensure_ascii=False):
            errors.append(f"legacy exam name remains in {item.get('word', '?')}")

        phrase_key = f"builtin:{item.get('id')}"
        phrase_entry = phrase_translations.get(phrase_key)
        if not isinstance(phrase_entry, dict):
            errors.append(f"missing phrase translations: {item.get('word')}")
            continue

        # Both phrase types are rendered for every built-in word.  Validate
        # both for every source list, not only TOEFL-curated additions.
        for phrase_type in PHRASE_TYPES:
            translation = phrase_entry.get(phrase_type)
            if not isinstance(translation, dict):
                errors.append(f"missing {phrase_type} translation: {item.get('word')}")
                continue
            expected_source = item.get("example") if phrase_type == "example" else item.get("collocations")
            if translation.get("source") != expected_source:
                errors.append(f"{phrase_type} translation key mismatch: {item.get('word')}")
            missing_languages = [
                language for language in PHRASE_LANGUAGES
                if not str(translation.get(language, "")).strip()
            ]
            if missing_languages:
                errors.append(
                    f"{phrase_type} translation missing languages for {item.get('word')}: "
                    + ", ".join(missing_languages)
                )

    levels = Counter(item.get("level") for item in vocabulary)
    curated = [item for item in vocabulary if item.get("source_list") == "TOEFL-curated"]
    if not curated:
        errors.append("no TOEFL-curated additions found")

    print(f"vocabulary: {len(vocabulary)} words")
    print("levels: " + ", ".join(f"L{level}={levels[level]}" for level in sorted(levels)))
    print(f"TOEFL-curated additions: {len(curated)}")
    print(f"phrase translation records: {len(phrase_translations)}")
    print(f"all-word phrase translation languages checked: {len(vocabulary)} x {len(PHRASE_TYPES)} x {len(PHRASE_LANGUAGES)}")

    for error in errors:
        fail(error)
    if errors:
        print(f"audit failed: {len(errors)} issue(s)")
        return 1
    print("audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
