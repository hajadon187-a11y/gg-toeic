#!/usr/bin/env python3
"""Run a conservative AI-assisted quality pass over all localized meanings.

The existing meanings are treated as the source text for review.  This pass
normalizes Unicode and spacing for every localized field and applies only
high-confidence language-specific corrections.  It deliberately does not
replace an already natural translation with an unverified machine translation.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"

FIELDS = (
    "meaning", "meaningEn", "meaningZh", "meaningHi", "meaningVi",
    "meaningKo", "meaningId", "meaningTh", "meaningEs",
)


# High-confidence corrections found during the full-data audit.
CORRECTIONS = {
    ("meaningVi", "whether"): "liệu có ... hay không",
    ("meaningTh", "liable"): "ต้องรับผิดตามกฎหมาย หรือมีแนวโน้มที่จะ...",
}


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"\s+([,.;:!?，。、；：！？])", r"\1", value)
    return value


def main() -> None:
    items = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    changed = 0
    corrected = 0
    processed = 0

    for item in items:
        word = str(item.get("word", "")).lower()
        for field in FIELDS:
            original = str(item.get(field, ""))
            updated = normalize_text(original)
            correction = CORRECTIONS.get((field, word))
            if correction is not None:
                updated = correction
                corrected += updated != original
            processed += 1
            if updated != original:
                item[field] = updated
                changed += 1

    assert processed == len(items) * len(FIELDS)
    assert all(str(item.get(field, "")).strip() for item in items for field in FIELDS)
    VOCAB_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"reviewed localized fields: {processed}")
    print(f"changed fields: {changed}")
    print(f"high-confidence corrections: {corrected}")


if __name__ == "__main__":
    main()
