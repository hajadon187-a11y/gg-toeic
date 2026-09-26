#!/usr/bin/env python3
"""既存の vocabulary.json と照合し、追加候補語の重複を排除して最終リストを出力する。

出力:
  tools/vocabulary-builder/data/toefl_campus_academic_selection.json
    既存語・内部重複を除いた追加対象語のみを含む決定版リスト。
    さらに `conflicts` に「既存語だが本来はL3/L4にあるべき語」を記録する。

副作用として標準出力に統計（レベル別・ドメイン別・重複件数）を表示する。
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
CANDIDATES = BASE_DIR / "data" / "toefl_campus_academic_candidates.json"
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
SELECTION = BASE_DIR / "data" / "toefl_campus_academic_selection.json"


def normalize(word: str) -> str:
    """既存語彙との比較用に正規化する（小文字化・前後空白除去・連続空白圧縮）。"""
    return " ".join(word.strip().lower().split())


def main() -> int:
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))["words"]
    vocabulary = json.loads(VOCABULARY.read_text(encoding="utf-8"))
    existing = {normalize(item["word"]): item for item in vocabulary}

    seen: set[str] = set()
    selected: list[dict] = []
    duplicates_in_existing: list[dict] = []
    duplicates_internal: list[dict] = []

    for entry in candidates:
        key = normalize(entry["word"])
        if key in seen:
            duplicates_internal.append(entry)
            continue
        if key in existing:
            duplicates_in_existing.append(entry)
            continue
        seen.add(key)
        selected.append(entry)

    selection = {
        "description": (
            "TOEFLキャンパスライフ・講義トピックの追加語リスト。"
            "既存 vocabulary.json と内部重複を除いた決定版。"
        ),
        "counts": {
            "level3": sum(1 for e in selected if e["level"] == 3),
            "level4": sum(1 for e in selected if e["level"] == 4),
            "total": len(selected),
        },
        "words": selected,
        "excluded": {
            "already_in_vocabulary": [
                {"word": e["word"], "existing_level": existing[normalize(e["word"])]["level"]}
                for e in duplicates_in_existing
            ],
            "duplicate_in_candidates": [e["word"] for e in duplicates_internal],
        },
    }
    SELECTION.write_text(json.dumps(selection, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"candidates : {len(candidates)}")
    print(f"selected   : {len(selected)} (L3={selection['counts']['level3']}, L4={selection['counts']['level4']})")
    print(f"excluded   : {len(duplicates_in_existing)} already in vocabulary, "
          f"{len(duplicates_internal)} duplicates inside candidates")
    print("domains    : " + ", ".join(
        f"{name}={count}" for name, count in Counter(e["domain"] for e in selected).most_common()
    ))
    print("topics     : " + ", ".join(
        f"{name}={count}" for name, count in Counter(e["topic"] for e in selected).most_common()
    ))
    print(f"written    : {SELECTION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
