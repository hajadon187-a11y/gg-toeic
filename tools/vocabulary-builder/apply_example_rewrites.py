"""Write the cached example sentences and translations back into the app assets.

This is a build-time data task. It only touches `example` in
app/src/main/assets/vocabulary.json and `example` (including `source`) in
app/src/main/assets/vocabulary_phrase_translations.json. `collocations` and every
other field stay as they are.

Usage:
  python3 apply_example_rewrites.py            # 変更点を表示して書き込む
  python3 apply_example_rewrites.py --check    # 書き込まずに差分件数だけ確認
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-campus-examples-cache.json")
TRANSLATION_FIELDS = ["ja", "zh", "hi", "vi", "ko", "id", "th", "es", "en"]


def main() -> int:
    parser = argparse.ArgumentParser(description="キャッシュ済みの例文をアプリのJSONへ反映する")
    parser.add_argument("--check", action="store_true", help="書き込まずに件数だけ確認")
    args = parser.parse_args()

    cache = json.loads(CACHE.read_text("utf-8"))["entries"]
    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root.setdefault("translations", {})

    updated = 0
    for item in vocabulary:
        entry = cache.get(str(item["id"]))
        if not entry:
            continue
        example = entry["example"]
        if item.get("example") == example and translations.get(f"builtin:{item['id']}", {}).get(
            "example", {}
        ).get("source") == example:
            continue
        item["example"] = example
        record = {"source": example}
        for field in TRANSLATION_FIELDS:
            record[field] = entry[field]
        key = f"builtin:{item['id']}"
        slot = translations.setdefault(key, {})
        slot["example"] = record
        updated += 1

    print(f"update targets: {updated} / {len(cache)} cached words")
    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {VOCABULARY}")
    print(f"wrote {PHRASES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
