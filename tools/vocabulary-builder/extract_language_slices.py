#!/usr/bin/env python3
"""Split the shipped vocabulary assets into one file per learner language.

The two shipped assets store every language side by side:

    app/src/main/assets/vocabulary.json
        6,384 rows x 19 fields, including meaningZh / meaningHi / ... / meaningEs
    app/src/main/assets/vocabulary_phrase_translations.json
        6,384 entries x (example + collocations) x 9 languages

Reading the whole thing at once therefore costs a full multi-language token
budget (roughly 4.5M tokens), which no single review pass can hold. Every
question this project asks about the assets is asked per language, so this tool
cuts the assets into one slice per language:

    data/slices/{lang}.json

Each slice contains only what that language needs:

  * the English source (word / example / collocations) so a reviewer can compare
  * the single `meaning{XX}` field for that language
  * the single `example` and `collocations` translation for that language

The English source is duplicated into each slice on purpose: it is what the
native reviewer compares against, and it is small next to the translations.
After slicing, the largest slice (es) is about 430K tokens and the smallest
(zh) about 110K tokens, so one language at a time fits comfortably.

The `English` language code is kept separate: `en` is the source, not a learner
language, so it is not sliced here.

This tool never calls an API and never writes to the shipped assets.

Usage:
  python3 extract_language_slices.py                 # 全言語のスライスを作成
  python3 extract_language_slices.py --only es zh    # 一部の言語だけ
  python3 extract_language_slices.py --dry-run       # 書き込まず見積りだけ
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
SLICE_DIR = BASE_DIR / "data" / "slices"

# 出荷している8学習言語。`audit_phrase_quality.py` と揃える。
# `en` は学習対象ではなく比較元なのでスライスしない。
LANGS = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es")

# `vocabulary.json` の意味フィールド名。英語は `meaningEn`。
MEANING_FIELDS = {
    "zh": "meaningZh",
    "hi": "meaningHi",
    "vi": "meaningVi",
    "ko": "meaningKo",
    "id": "meaningId",
    "es": "meaningEs",
    "th": "meaningTh",
    # 日本語の意味は `meaning`（サフィックスなし）。
    "ja": "meaning",
}

# おおよそのトークン数の見積り。ASCII は約3.3文字/トークン、
# 非ラテン文字は多くのトークナイザで約1.6文字/トークン。
LATIN_LANGS = frozenset({"vi", "id", "es"})


def estimate_tokens(chars: int, lang: str) -> int:
    per_token = 3.3 if lang in LATIN_LANGS else 1.6
    return int(chars / per_token)


def build_slice(lang: str, vocabulary: list, translations: dict) -> dict:
    """1言語分のスライスを組み立てる。"""
    field = MEANING_FIELDS[lang]
    items = []
    for item in vocabulary:
        item_id = item["id"]
        entry = translations.get(f"builtin:{item_id}", {})
        example = entry.get("example", {})
        collocations = entry.get("collocations", {})
        items.append(
            {
                "id": item_id,
                "word": item["word"],
                "level": item.get("level"),
                "topic": item.get("topic"),
                "meaningEn": item.get("meaningEn", ""),
                "meaning": item.get(field, ""),
                "exampleSource": example.get("source", ""),
                "example": example.get(lang, ""),
                "collocationsSource": collocations.get("source", ""),
                "collocations": collocations.get(lang, ""),
            }
        )
    return {
        "schemaVersion": 1,
        "language": lang,
        "entryCount": len(items),
        "source": {
            "vocabulary": str(VOCAB_PATH.relative_to(ROOT)),
            "phrases": str(PHRASE_PATH.relative_to(ROOT)),
        },
        "entries": items,
    }


def slice_metrics(payload: dict, lang: str) -> dict:
    """スライスの件数・文字数・推定トークン数を返す。"""
    chars = 0
    translated_chars = 0
    missing = 0
    for item in payload["entries"]:
        chars += sum(len(str(value)) for value in item.values())
        translated_chars += sum(
            len(str(item[field])) for field in ("meaning", "example", "collocations")
        )
        if not str(item["example"]).strip() or not str(item["collocations"]).strip():
            missing += 1
    return {
        "language": lang,
        "entries": payload["entryCount"],
        "chars": chars,
        "charsWithoutEnglishSource": translated_chars,
        "estimatedTokens": estimate_tokens(chars, lang),
        "estimatedTokensWithoutEnglishSource": estimate_tokens(translated_chars, lang),
        "entriesMissingTranslation": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=LANGS, action="append",
                        help="この言語だけを処理する（複数指定可）")
    parser.add_argument("--out-dir", type=Path, default=SLICE_DIR,
                        help=f"スライスの出力先（既定: {SLICE_DIR}）")
    parser.add_argument("--dry-run", action="store_true",
                        help="ファイルを書かずに見積りだけ表示する")
    args = parser.parse_args()

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    translations = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))["translations"]
    languages = args.only or list(LANGS)

    if not args.dry_run:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"vocabulary words: {len(vocabulary)}")
    metrics = []
    for lang in languages:
        payload = build_slice(lang, vocabulary, translations)
        stats = slice_metrics(payload, lang)
        metrics.append(stats)
        target = args.out_dir / f"{lang}.json"
        if not args.dry_run:
            target.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        suffix = "" if args.dry_run else f" -> {target}"
        print(
            f"  {lang}: {stats['entries']} entries, "
            f"{stats['chars']:,} chars, ~{stats['estimatedTokens']:,} tokens "
            f"(without English source ~{stats['estimatedTokensWithoutEnglishSource']:,})"
            f"{suffix}"
        )
        if stats["entriesMissingTranslation"]:
            print(f"      missing translation: {stats['entriesMissingTranslation']}")

    if not args.dry_run:
        summary = args.out_dir / "summary.json"
        summary.write_text(
            json.dumps({"languages": metrics}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"summary written: {summary}")
        print(f"largest slice: ~{max(m['estimatedTokens'] for m in metrics):,} tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
