"""Rebuild the generation cache from the shipped JSON assets.

The cache under /private/tmp is a resume aid only: vocabulary.json and
vocabulary_phrase_translations.json already hold every generated example and its
translations. This script restores the cache from those files so a later run can
revalidate or regenerate individual words without calling the API again.
"""

import json
from pathlib import Path

REPO = Path("/Users/masafumihayakawa/GG_TOEFL")
VOCABULARY = REPO / "app/src/main/assets/vocabulary.json"
PHRASES = REPO / "app/src/main/assets/vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-campus-examples-cache.json")
FIELDS = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es", "en")


def main() -> None:
    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    phrases = json.loads(PHRASES.read_text("utf-8"))["translations"]

    entries: dict[str, dict[str, str]] = {}
    for item in vocabulary:
        example_entry = phrases.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(example_entry, dict):
            continue
        if example_entry.get("source") != item["example"]:
            continue
        entries[str(item["id"])] = {
            "example": item["example"],
            **{field: str(example_entry.get(field, "")).strip() for field in FIELDS},
        }

    CACHE.write_text(
        json.dumps({"schemaVersion": 1, "entries": entries}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"restored {len(entries)} cache entries to {CACHE}")


if __name__ == "__main__":
    main()
