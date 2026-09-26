#!/usr/bin/env python3
"""Generate native-reviewed Japanese phrase translations for TOEFL Level 1.

This is a build-time data task only. The Android app never calls the provider;
the generated JSON is bundled as a local dictionary. A cache is written after
each completed batch so an interrupted run can resume without repeating work.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
INPUT = REPO_DIR / "app/src/main/assets/vocabulary.json"
OUTPUT = REPO_DIR / "app/src/main/assets/vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-level1-phrase-ja-cache.json")
BATCH_SIZE = 16


def has_japanese(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    return bool(re.search(r"[ぁ-ゟァ-ヿ一-鿿]", value))


def parse_json(content: str) -> dict[str, Any] | None:
    cleaned = re.sub(r"```(?:json)?", "", content, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        value = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def valid_result(value: Any, batch: list[dict[str, Any]]) -> bool:
    if not isinstance(value, dict):
        return False
    for item in batch:
        result = value.get(str(item["id"]), value.get(item["id"]))
        if not isinstance(result, dict):
            return False
        if not has_japanese(result.get("collocations")):
            return False
        if not has_japanese(result.get("example")):
            return False
    return True


def translate_batch(
    batch: list[dict[str, Any]], client: OpenAI, model: str
) -> dict[str, dict[str, str]]:
    payload = "\n".join(
        f'{item["id"]}\tCollocations: {item["collocations"]}\tExample: {item["example"]}'
        for item in batch
    )
    prompt = f"""あなたはTOEFL教材を作る日本語ネイティブの編集者です。
次の英語の Collocations と Sample Sentence を、自然で意味の正確な日本語に翻訳してください。
単語帳に収録するため、直訳調ではなく、学習者が実際に使える自然な表現にしてください。

必ず次のJSON形式だけを返してください。説明、Markdown、キーの欠落は禁止です。
{{"id": {{"collocations": "日本語の連語リスト", "example": "自然な日本語の例文"}}}}

ルール:
- collocations は入力の順番と項目数を保ち、「、」で区切る。
- example は英文の意味と主語・時制・因果関係を保つ自然な一文にする。
- 日本語以外の説明、英語の併記、括弧内の編集コメントは追加しない。
- “the number of” のように文脈で訳が変わる表現は、単語帳として最も自然な訳にする。

入力:
{payload}
"""

    for attempt in range(4):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=6000,
            response_format={"type": "json_object"},
        )
        parsed = parse_json(response.choices[0].message.content or "")
        if valid_result(parsed, batch):
            result: dict[str, dict[str, str]] = {}
            for item in batch:
                raw = parsed.get(str(item["id"]), parsed.get(item["id"]))
                result[str(item["id"])] = {
                    "collocations": raw["collocations"].strip(),
                    "example": raw["example"].strip(),
                }
            return result
        if len(batch) > 1:
            middle = len(batch) // 2
            left = translate_batch(batch[:middle], client, model)
            right = translate_batch(batch[middle:], client, model)
            return {**left, **right}
        time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(f"Invalid Japanese translation response for ids {[i['id'] for i in batch]}")


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "sk-xxxx":
        raise SystemExit("DEEPSEEK_API_KEY is not configured")

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=180.0,
        max_retries=3,
    )
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    vocabulary = load_json(INPUT, [])
    level1 = [item for item in vocabulary if item.get("level") == 1]

    dictionary = load_json(OUTPUT, {"schemaVersion": 1, "translations": {}})
    translations: dict[str, dict[str, Any]] = dictionary.setdefault("translations", {})
    cache: dict[str, dict[str, str]] = load_json(CACHE, {})

    pending: list[dict[str, Any]] = []
    for item in level1:
        key = f'builtin:{item["id"]}'
        current = translations.get(key, {})
        collocation_entry = current.get("collocations", {})
        example_entry = current.get("example", {})
        if (
            collocation_entry.get("source") == item.get("collocations")
            and has_japanese(collocation_entry.get("ja"))
            and example_entry.get("source") == item.get("example")
            and has_japanese(example_entry.get("ja"))
        ):
            continue
        cached = cache.get(str(item["id"]))
        if cached and has_japanese(cached.get("collocations")) and has_japanese(cached.get("example")):
            continue
        pending.append(item)

    print(f"Level 1: {len(level1)} entries, {len(pending)} pending", flush=True)
    batches = [pending[i : i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(translate_batch, batch, client, model) for batch in batches]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            result = future.result()
            cache.update(result)
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"completed {index}/{len(futures)} batches", flush=True)

    for item in level1:
        key = f'builtin:{item["id"]}'
        result = cache.get(str(item["id"]))
        if not result:
            continue
        translations[key] = {
            "collocations": {
                "source": item["collocations"],
                "ja": result["collocations"],
            },
            "example": {
                "source": item["example"],
                "ja": result["example"],
            },
        }

    OUTPUT.write_text(
        json.dumps({"schemaVersion": 1, "translations": translations}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(translations)} dictionary entries to {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
