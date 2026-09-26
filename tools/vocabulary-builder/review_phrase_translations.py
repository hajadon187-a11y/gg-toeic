#!/usr/bin/env python3
"""Review and correct all Example/Collocation translations with GPT-5.6 Luna.

The source English and current translations are sent to an OpenAI-compatible
Luna endpoint. Results are cached per language and vocabulary id so an
interrupted run can resume without repeating completed work.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parent.parent
VOCAB = ROOT / "app/src/main/assets/vocabulary.json"
PHRASES = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
DEFAULT_CACHE = Path("/private/tmp/toefl-phrase-review-cache.json")
DEFAULT_REPORT = Path("/private/tmp/toefl-phrase-review-report.json")

LANGUAGES = {
    "ja": ("Japanese", r"[ぁ-ゟァ-ヿ一-鿿]"),
    "zh": ("Simplified Chinese", r"[一-鿿]"),
    "hi": ("Hindi", r"[ऀ-ॿ]"),
    "vi": ("Vietnamese", r"[A-Za-zÀ-ỹÁÉÍÓÚÜÑáéíóúüñ]"),
    "ko": ("Korean", r"[가-힣]"),
    "id": ("Indonesian", r"[A-Za-zÀ-ỹÁÉÍÓÚÜÑáéíóúüñ]"),
    "th": ("Thai", r"[ก-๛]"),
    "es": ("Spanish", r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]"),
}
WRONG_SCRIPT = re.compile(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿก-๛]")


def parse_json(content: str) -> Optional[dict[str, Any]]:
    cleaned = re.sub(r"```(?:json)?", "", content, flags=re.IGNORECASE).replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        parsed = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def has_target_script(value: object, language: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if not re.search(LANGUAGES[language][1], value):
        return False
    if language in {"vi", "id", "es"} and WRONG_SCRIPT.search(value):
        return False
    return True


def collocation_count(value: str) -> int:
    return len([part for part in re.split(r"[,，、]", value) if part.strip()])


def valid_item(raw: object, item: dict[str, Any], language: str) -> bool:
    if not isinstance(raw, dict):
        return False
    example = raw.get("example")
    collocations = raw.get("collocations")
    if not has_target_script(example, language) or not has_target_script(collocations, language):
        return False
    if str(example).strip().casefold() == item["example"].strip().casefold():
        return False
    if str(collocations).strip().casefold() == item["collocations"].strip().casefold():
        return False
    return collocation_count(str(collocations)) == collocation_count(item["collocations"])


def prompt_for(batch: list[dict[str, Any]], language: str) -> str:
    name = LANGUAGES[language][0]
    payload = "\n".join(
        f'{item["id"]}\tword={item["word"]}\t'
        f'EN example={item["example"]}\tCURRENT example={item["current_example"]}\t'
        f'EN collocations={item["collocations"]}\tCURRENT collocations={item["current_collocations"]}'
        for item in batch
    )
    return f"""You are a meticulous native {name} editor reviewing a TOEFL vocabulary app.
For every item, compare the current {name} Example and Collocations with the English source.
Keep a current translation unchanged when it is accurate and natural. Correct it when it is
literal, unnatural, incomplete, ambiguous, or changes the meaning, tense, modality, subject,
number, or logical relationship.

Return ONLY a valid JSON object mapping each numeric id to this exact shape:
{{"numeric_id": {{"example": "final translation", "collocations": "final translations"}}}}
The values must contain only {name}, with no English source, labels, comments, alternatives,
brackets, or quality scores. Preserve the order and number of collocations, separated by commas
or the standard list separator for {name}. Use the standard script of {name}.

Items:
{payload}
"""


def review_batch(batch: list[dict[str, Any]], language: str, client: OpenAI, model: str) -> dict[int, dict[str, str]]:
    for attempt in range(3):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_for(batch, language)}],
            max_completion_tokens=12000,
            response_format={"type": "json_object"},
        )
        parsed = parse_json(response.choices[0].message.content or "")
        if parsed is not None:
            result: dict[int, dict[str, str]] = {}
            for item in batch:
                raw = parsed.get(str(item["id"]), parsed.get(item["id"]))
                if not valid_item(raw, item, language):
                    result = {}
                    break
                result[item["id"]] = {
                    "example": str(raw["example"]).strip(),
                    "collocations": str(raw["collocations"]).strip(),
                }
            if len(result) == len(batch):
                return result
        if len(batch) > 1:
            middle = len(batch) // 2
            return {
                **review_batch(batch[:middle], language, client, model),
                **review_batch(batch[middle:], language, client, model),
            }
        time.sleep(1.0 + attempt)
    # A small number of entries can make a model return an unusable response
    # repeatedly (for example, conjunction-heavy collocation fragments). Keep
    # the existing target-language text for that item and continue the full
    # review rather than aborting the entire language.
    if len(batch) == 1:
        item = batch[0]
        return {
            item["id"]: {
                "example": item["current_example"],
                "collocations": item["current_collocations"],
            }
        }
    raise RuntimeError(f"Invalid Luna response for {language}: {[x['id'] for x in batch]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--only", choices=list(LANGUAGES), action="append")
    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("LUNA_API_KEY", "")
    base_url = os.getenv("LUNA_BASE_URL", "").strip()
    if not api_key:
        raise SystemExit("LUNA_API_KEY is not configured in tools/vocabulary-builder/.env")
    if not base_url:
        raise SystemExit("LUNA_BASE_URL is not configured in tools/vocabulary-builder/.env")
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=180.0, max_retries=3)
    model = os.getenv("LUNA_MODEL", "gpt-5.6-luna")

    vocabulary = json.loads(VOCAB.read_text(encoding="utf-8"))
    dictionary = json.loads(PHRASES.read_text(encoding="utf-8"))
    translations = dictionary["translations"]
    cache: dict[str, dict[str, str]] = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    before = {key: json.loads(json.dumps(value, ensure_ascii=False)) for key, value in translations.items()}
    languages = args.only or list(LANGUAGES)

    for language in languages:
        pending: list[dict[str, Any]] = []
        for item in vocabulary:
            key = f'builtin:{item["id"]}'
            entry = translations[key]
            current = {
                "id": item["id"], "word": item["word"],
                "example": entry["example"]["source"],
                "collocations": entry["collocations"]["source"],
                "current_example": entry["example"].get(language, ""),
                "current_collocations": entry["collocations"].get(language, ""),
            }
            cached = cache.get(f"{language}:{item['id']}")
            if cached and valid_item(cached, current, language):
                continue
            pending.append(current)
        batches = [pending[i : i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
        print(f"{language}: {len(pending)} items in {len(batches)} batches", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(review_batch, batch, language, client, model) for batch in batches]
            for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
                cache.update({f"{language}:{item_id}": value for item_id, value in future.result().items()})
                if index % 10 == 0 or index == len(futures):
                    args.cache.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    print(f"{language}: completed {index}/{len(futures)}", flush=True)
                if args.delay:
                    time.sleep(args.delay)
        for item in vocabulary:
            value = cache.get(f'{language}:{item["id"]}')
            if not value:
                continue
            entry = translations[f'builtin:{item["id"]}']
            current = {
                "id": item["id"], "word": item["word"],
                "example": entry["example"]["source"],
                "collocations": entry["collocations"]["source"],
                "current_example": entry["example"].get(language, ""),
                "current_collocations": entry["collocations"].get(language, ""),
            }
            if valid_item(value, current, language):
                entry["example"][language] = value["example"]
                entry["collocations"][language] = value["collocations"]
        PHRASES.write_text(json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report: dict[str, dict[str, int]] = {}
    for language in LANGUAGES:
        changed = 0
        for key, old in before.items():
            new = translations.get(key, {})
            for field in ("example", "collocations"):
                if old.get(field, {}).get(language) != new.get(field, {}).get(language):
                    changed += 1
        report[language] = {"entries": len(vocabulary), "changed_fields": changed}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
