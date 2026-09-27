#!/usr/bin/env python3
"""Translate TOEIC examples and collocations with a Luna OpenAI-compatible API.

The script deliberately reads credentials from .env without printing their values.
It writes one validated batch at a time so an interrupted run can be resumed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
DOTENV_PATH = ROOT / ".env"
LANGUAGES = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es")
LANGUAGE_NAMES = {
    "ja": "Japanese",
    "zh": "Simplified Chinese",
    "hi": "Hindi",
    "vi": "Vietnamese",
    "ko": "Korean",
    "id": "Indonesian",
    "th": "Thai",
    "es": "Spanish",
}


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        raise SystemExit(f"Missing dotenv file: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def api_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def parse_json_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    if not isinstance(content, str):
        raise ValueError("The API response content is not JSON text")
    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("The API response JSON is not an object")
    return parsed


def call_luna(
    *,
    url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int,
    retries: int = 4,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a meticulous native-language editor for TOEIC business English. "
                    "Return only valid JSON. Do not add commentary or markdown."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
            outer = json.loads(response_body)
            if isinstance(outer, dict) and "choices" in outer:
                content = outer["choices"][0]["message"]["content"]
                return parse_json_content(content)
            return parse_json_content(outer)
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")[:500]
            last_error = RuntimeError(f"HTTP {exc.code}: {response_body}")
        except (URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            last_error = exc
        if attempt + 1 < retries:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Luna API request failed after {retries} attempts: {last_error}")


def make_prompt(items: list[dict[str, Any]], fields: tuple[str, ...], languages: tuple[str, ...]) -> str:
    field_rules = []
    if "example" in fields:
        field_rules.append(
            'For "example", write one natural, concise sentence for each language. '
            "Keep the same business meaning and TOEIC context; do not translate word-for-word."
        )
    if "collocations" in fields:
        field_rules.append(
            'For "collocations", translate each comma-separated phrase in order and return '
            "a comma-separated string with the same number of items. Use natural equivalents, not explanations."
        )
    language_spec = ", ".join(f'"{lang}" ({LANGUAGE_NAMES[lang]})' for lang in languages)
    compact_items = []
    for item in items:
        source: dict[str, str] = {"id": str(item["id"]), "word": item["word"]}
        if "example" in fields:
            source["example"] = item["example"]
        if "collocations" in fields:
            source["collocations"] = item["collocations"]
        compact_items.append(source)
    return (
        "Translate the following TOEIC vocabulary content. Target languages: "
        f"{language_spec}.\n"
        + " ".join(field_rules)
        + "\nDo not change IDs. Return exactly this JSON shape: "
        '{"items":[{"id":1,"example":{"ja":"..."},"collocations":{"ja":"..."}}]} '
        "with every requested field and every requested language present. "
        "No English output is needed because the source English is already supplied.\n"
        + json.dumps({"items": compact_items}, ensure_ascii=False)
    )


def validate_result(
    result: dict[str, Any],
    expected_ids: set[int],
    fields: tuple[str, ...],
    languages: tuple[str, ...],
) -> dict[int, dict[str, dict[str, str]]]:
    raw_items = result.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("The API result has no items array")
    normalized: dict[int, dict[str, dict[str, str]]] = {}
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("An API item is not an object")
        try:
            item_id = int(raw["id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("An API item has an invalid id") from exc
        if item_id not in expected_ids or item_id in normalized:
            raise ValueError(f"Unexpected or duplicate id in API result: {item_id}")
        translated: dict[str, dict[str, str]] = {}
        for field in fields:
            values = raw.get(field)
            if not isinstance(values, dict):
                raise ValueError(f"Item {item_id} has no {field} object")
            translated[field] = {}
            for lang in languages:
                value = values.get(lang)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"Item {item_id} has an empty {field}.{lang}")
                translated[field][lang] = value.strip()
        normalized[item_id] = translated
    if set(normalized) != expected_ids:
        missing = sorted(expected_ids - set(normalized))
        raise ValueError(f"The API omitted ids: {missing}")
    return normalized


def atomic_write_json(path: Path, data: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("examples", "collocations", "both"), default="both")
    parser.add_argument("--languages", default=",".join(LANGUAGES))
    parser.add_argument("--start", type=int, default=0, help="0-based vocabulary index")
    parser.add_argument("--limit", type=int, default=0, help="0 means through the end")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--workers", type=int, default=1, help="parallel API requests")
    parser.add_argument("--write", action="store_true", help="write translations; otherwise dry-run")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    env = load_dotenv(DOTENV_PATH)
    api_key = env.get("LUNA_API_KEY", "").strip()
    base_url = env.get("LUNA_BASE_URL", "").strip()
    model = env.get("LUNA_MODEL", "").strip()
    if not api_key or not base_url or not model:
        raise SystemExit("LUNA_API_KEY, LUNA_BASE_URL, and LUNA_MODEL must all be set in .env")
    languages = tuple(lang.strip() for lang in args.languages.split(",") if lang.strip())
    invalid = sorted(set(languages) - set(LANGUAGES))
    if invalid:
        raise SystemExit(f"Unsupported languages: {', '.join(invalid)}")
    if args.start < 0 or args.limit < 0 or args.batch_size < 1 or args.workers < 1:
        raise SystemExit("start, limit, batch-size, and workers must be non-negative, with batch-size and workers >= 1")
    fields = ("example",) if args.mode == "examples" else ("collocations",) if args.mode == "collocations" else ("example", "collocations")

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_data = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_data["translations"]
    end = len(vocabulary) if args.limit == 0 else min(len(vocabulary), args.start + args.limit)
    selected = vocabulary[args.start:end]
    if not selected:
        raise SystemExit("No vocabulary items selected")
    print(f"Selected {len(selected)} items: indexes {args.start}..{end - 1}; fields={','.join(fields)}; languages={','.join(languages)}")

    url = api_url(base_url)
    def translate_batch(batch: list[dict[str, Any]]) -> dict[int, dict[str, dict[str, str]]]:
        prompt_items = [
            {
                "id": item["id"],
                "word": item["word"],
                "example": item["example"],
                "collocations": item["collocations"],
            }
            for item in batch
        ]
        expected_ids = {item["id"] for item in batch}
        validation_error: Exception | None = None
        for attempt in range(3):
            result = call_luna(
                url=url,
                api_key=api_key,
                model=model,
                prompt=make_prompt(prompt_items, fields, languages),
                timeout=args.timeout,
            )
            try:
                return validate_result(result, expected_ids, fields, languages)
            except ValueError as exc:
                validation_error = exc
                if attempt < 2:
                    time.sleep(2 ** attempt)
        if len(batch) > 1:
            midpoint = len(batch) // 2
            left = translate_batch(batch[:midpoint])
            right = translate_batch(batch[midpoint:])
            return {**left, **right}
        raise RuntimeError(f"Luna returned invalid translations after 3 attempts: {validation_error}")

    batches = [
        selected[offset : offset + args.batch_size]
        for offset in range(0, len(selected), args.batch_size)
    ]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for group_start in range(0, len(batches), args.workers):
            group = batches[group_start : group_start + args.workers]
            futures = [executor.submit(translate_batch, batch) for batch in group]
            for group_offset, (batch, future) in enumerate(zip(group, futures)):
                normalized = future.result()
                batch_number = group_start + group_offset + 1
                print(f"Validated batch {batch_number}: ids {batch[0]['id']}..{batch[-1]['id']}")
                if args.write:
                    for item in batch:
                        entry = translations[f"builtin:{item['id']}"]
                        for field in fields:
                            entry.setdefault(field, {})
                            entry[field].update(normalized[item["id"]][field])
                    atomic_write_json(PHRASE_PATH, phrase_data)
                    print(f"Saved batch {batch_number}")
                elif group_start == 0 and group_offset == 0:
                    print(json.dumps({"items": [normalized[batch[0]["id"]]]}, ensure_ascii=False, indent=2))
    print("Completed successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("Interrupted; no partial API response was written.")
