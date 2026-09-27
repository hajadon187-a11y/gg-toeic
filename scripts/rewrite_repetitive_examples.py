#!/usr/bin/env python3
"""Rewrite repetitive vocabulary examples and their local translations.

The model receives each word's definition and collocations so that it can
choose a meaning-appropriate workplace or professional context. A prefix is
used to select one mechanically generated family at a time; the cache keeps
large rewrites resumable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translate_toeic_with_luna import (  # noqa: E402
    LANGUAGES,
    LANGUAGE_NAMES,
    api_url,
    call_luna,
    load_dotenv,
    parse_json_content,
)


ALL_LANGUAGES = ("en",) + LANGUAGES


def make_prompt(items: list[dict[str, Any]], prefix: str) -> str:
    language_spec = ", ".join(
        f'"{lang}" ({"English" if lang == "en" else LANGUAGE_NAMES[lang]})'
        for lang in ALL_LANGUAGES
    )
    compact = [
        {
            "id": item["id"],
            "word": item["word"],
            "meaningEn": item.get("meaningEn", ""),
            "collocations": item.get("collocations", ""),
            "topic": item.get("topic", "General"),
        }
        for item in items
    ]
    return (
        "Rewrite the example sentence for each TOEIC vocabulary item below. "
        f"Return one sentence in each of these languages: {language_spec}.\n"
        "English requirements: write one concise, natural sentence of about 8-22 words; "
        "use the exact vocabulary word as a standalone word; make the situation useful "
        "for business English, such as meetings, HR, finance, sales, logistics, customer "
        "service, compliance, IT, manufacturing, travel, or workplace training. For a "
        "technical, scientific, geographic, or abstract word, use a realistic professional, "
        "product, public-service, or health context. Match the supplied definition and part "
        "of speech. Vary the subjects, verbs, sentence patterns, and settings across items. "
        f"Do not use the old template or begin the new sentence with {prefix!r}; do not write "
        "a definition.\n"
        "Translation requirements: translate the English sentence's meaning naturally for "
        "native readers; do not translate word-for-word, omit the target word's meaning, "
        "or add explanations. Use normal professional terminology in each language.\n"
        "Return only this JSON shape, with no markdown or commentary. Use item_id "
        "for the numeric identifier because id is reserved for Indonesian: "
        '{"items":[{"item_id":1,"en":"...","ja":"...","zh":"...","hi":"...",'
        '"vi":"...","ko":"...","id":"...","th":"...","es":"..."}]}\n'
        + json.dumps({"items": compact}, ensure_ascii=False)
    )


def validate_result(
    result: dict[str, Any],
    batch: list[dict[str, Any]],
    prefix: str,
) -> dict[int, dict[str, str]]:
    raw_items = result.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("response has no items array")
    expected = {int(item["id"]): item for item in batch}
    normalized: dict[int, dict[str, str]] = {}
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("response item is not an object")
        try:
            item_id = int(raw["item_id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("response item has invalid id") from exc
        if item_id not in expected or item_id in normalized:
            raise ValueError(f"unexpected or duplicate id: {item_id}")
        values: dict[str, str] = {}
        for lang in ALL_LANGUAGES:
            value = raw.get(lang)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"item {item_id} has empty {lang}")
            values[lang] = value.strip()
        word = str(expected[item_id]["word"]).strip()
        if not re.search(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", values["en"], re.I):
            raise ValueError(f"item {item_id} English sentence does not contain {word!r}")
        if values["en"].lower().startswith(prefix.lower()):
            raise ValueError(f"item {item_id} still uses the repetitive template")
        normalized[item_id] = values
    if set(normalized) != set(expected):
        missing = sorted(set(expected) - set(normalized))
        raise ValueError(f"response omitted ids: {missing}")
    return normalized


def translate_batch(
    batch: list[dict[str, Any]],
    *,
    url: str,
    api_key: str,
    model: str,
    timeout: int,
    prefix: str,
) -> dict[int, dict[str, str]]:
    result = call_luna(
        url=url,
        api_key=api_key,
        model=model,
        prompt=make_prompt(batch, prefix),
        timeout=timeout,
    )
    return validate_result(result, batch, prefix)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prefix",
        default="The report includes information about ",
        help="Only rewrite examples beginning with this exact prefix.",
    )
    parser.add_argument("--batch-size", type=int, default=6)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--cache", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1 or args.workers < 1:
        raise SystemExit("batch-size and workers must be positive")
    if args.cache is None:
        safe_prefix = re.sub(r"[^a-z0-9]+", "_", args.prefix.casefold()).strip("_")
        args.cache = Path(f"/private/tmp/{safe_prefix}_rewrites.json")

    env = load_dotenv(ROOT / ".env")
    api_key = env.get("LUNA_API_KEY", "").strip()
    base_url = env.get("LUNA_BASE_URL", "").strip()
    model = env.get("LUNA_MODEL", "").strip()
    if not api_key or not base_url or not model:
        raise SystemExit("LUNA_API_KEY, LUNA_BASE_URL, and LUNA_MODEL must be set")

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    targets = [
        item for item in vocabulary
        if str(item.get("example", "")).startswith(args.prefix)
    ]
    if not targets:
        raise SystemExit("No repetitive examples found")
    print(f"Selected {len(targets)} repetitive examples with prefix {args.prefix!r}")

    cached: dict[int, dict[str, str]] = {}
    if args.cache.is_file():
        raw_cache = json.loads(args.cache.read_text(encoding="utf-8"))
        cached = {int(key): value for key, value in raw_cache.items()}
    pending = [item for item in targets if int(item["id"]) not in cached]
    print(f"Using {len(cached)} cached items; requesting {len(pending)} items")

    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    if batches:
        url = api_url(base_url)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(
                    translate_batch,
                    batch,
                    url=url,
                    api_key=api_key,
                    model=model,
                    timeout=args.timeout,
                    prefix=args.prefix,
                ): batch
                for batch in batches
            }
            for index, future in enumerate(as_completed(futures), start=1):
                batch = futures[future]
                try:
                    cached.update(future.result())
                except Exception as exc:
                    ids = ",".join(str(item["id"]) for item in batch)
                    raise SystemExit(f"batch failed for ids {ids}: {exc}") from exc
                args.cache.parent.mkdir(parents=True, exist_ok=True)
                args.cache.write_text(json.dumps(cached, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"Completed batch {index}/{len(batches)} ({len(cached)}/{len(targets)})")

    expected_ids = {int(item["id"]) for item in targets}
    if set(cached) != expected_ids:
        raise SystemExit(f"Cache is incomplete: {len(cached)}/{len(expected_ids)}")
    for item in targets:
        values = cached[int(item["id"])]
        item["example"] = values["en"]
        entry = phrase_root.setdefault("translations", {}).setdefault(f"builtin:{item['id']}", {}).setdefault("example", {})
        entry.clear()
        entry["source"] = values["en"]
        entry.update({lang: values[lang] for lang in LANGUAGES})
        entry["en"] = values["en"]

    if args.write:
        VOCAB_PATH.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        PHRASE_PATH.write_text(json.dumps(phrase_root, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(targets)} examples and their multilingual translations")
    else:
        print("Dry run: use --write to update the assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
