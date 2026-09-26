#!/usr/bin/env python3
"""Generate the complete offline phrase dictionary for all vocabulary languages.

This is a build-time task. The Android app only reads the resulting JSON asset
and never contacts the translation provider. Results are cached per language
and word id so the task can be safely resumed after interruption.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
INPUT = REPO_DIR / "app/src/main/assets/vocabulary.json"
OUTPUT = REPO_DIR / "app/src/main/assets/vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-all-phrase-translations-cache.json")
BATCH_SIZE = 48
WORKERS = 6

LANGUAGES = {
    "ja": "Japanese",
    "zh": "Simplified Chinese",
    "hi": "Hindi",
    "vi": "Vietnamese",
    "ko": "Korean",
    "id": "Indonesian",
    "th": "Thai",
    "es": "Spanish",
}

_cache_lock = threading.Lock()


def has_script(value: Any, language: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if language == "ja":
        return bool(re.search(r"[ぁ-ゟァ-ヿ一-鿿]", value))
    if language == "zh":
        return bool(re.search(r"[一-鿿]", value))
    if language == "hi":
        return bool(re.search(r"[ऀ-ॿ]", value))
    if language == "ko":
        return bool(re.search(r"[가-힣]", value))
    if language == "th":
        return bool(re.search(r"[ก-๛]", value))
    if language in {"vi", "id", "es"}:
        has_latin = bool(re.search(r"[A-Za-zÀ-ỹÁÉÍÓÚÜÑáéíóúüñ]", value))
        wrong_script = bool(re.search(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿก-๛]", value))
        return has_latin and not wrong_script
    return False


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


def valid_result(value: Any, batch: list[dict[str, Any]], language: str) -> bool:
    if not isinstance(value, dict):
        return False
    for item in batch:
        result = value.get(str(item["id"]), value.get(item["id"]))
        if not isinstance(result, dict):
            return False
        for field in ("collocations", "example"):
            translated = result.get(field)
            if not has_script(translated, language):
                return False
            if isinstance(translated, str) and translated.strip().casefold() == str(item.get(field, "")).strip().casefold():
                return False
    return True


def prompt_for(batch: list[dict[str, Any]], language: str) -> str:
    language_name = LANGUAGES[language]
    payload = "\n".join(
        f'{item["id"]}\tCollocations: {item["collocations"]}\tExample: {item["example"]}'
        for item in batch
    )
    return f"""You are a meticulous native {language_name} editor creating a high-quality TOEFL vocabulary app.
Translate every English Collocations list and Sample Sentence below into natural, accurate {language_name}.
Do not translate word-for-word when that would sound unnatural. Preserve the meaning, tense, subject,
modality, and logical relationship of each sentence.

Return ONLY a valid JSON object in this exact shape:
{{"numeric_id": {{"collocations": "translation", "example": "translation"}}}}
Do not omit an id. Do not add explanations, comments, Markdown, English labels, or quality scores.

Rules:
- Keep the collocation order and item count; separate translated collocations with a natural comma/list separator.
- Use only the target language in each value (ordinary names, numbers, and punctuation are allowed).
- Use the standard script of {language_name}, suitable for educated native speakers and TOEFL learners.
- For Japanese use natural modern Japanese; for Chinese use Simplified Chinese; for Hindi use Devanagari;
  for Vietnamese and Indonesian use natural Latin-script wording; for Korean use Hangul; for Thai use Thai script;
  for Spanish use natural international Spanish.

Input:
{payload}
"""


def translate_batch(
    batch: list[dict[str, Any]], language: str, client: OpenAI, model: str
) -> dict[str, dict[str, str]]:
    for attempt in range(4):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_for(batch, language)}],
            temperature=0.1,
            max_tokens=12000,
            response_format={"type": "json_object"},
        )
        parsed = parse_json(response.choices[0].message.content or "")
        if valid_result(parsed, batch, language):
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
            left = translate_batch(batch[:middle], language, client, model)
            right = translate_batch(batch[middle:], language, client, model)
            return {**left, **right}
        time.sleep(2.0 * (attempt + 1))

    raise RuntimeError(
        f"Invalid {language} response for ids {[item['id'] for item in batch]}"
    )


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def has_local_entry(
    current: dict[str, Any], item: dict[str, Any], language: str
) -> bool:
    for field in ("collocations", "example"):
        entry = current.get(field, {})
        if entry.get("source") != item.get(field, ""):
            return False
        if language == "en":
            expected = item.get(field, "")
        else:
            expected = entry.get(language, "")
        if not expected:
            return False
    return True


def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    vocabulary = load_json(INPUT, [])
    dictionary = load_json(OUTPUT, {"schemaVersion": 1, "translations": {}})
    translations: dict[str, dict[str, Any]] = dictionary.setdefault("translations", {})
    cache: dict[str, dict[str, dict[str, str]]] = load_json(CACHE, {})
    client: OpenAI | None = None

    def get_client() -> OpenAI:
        nonlocal client
        if client is None:
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if not api_key or api_key == "sk-xxxx":
                raise SystemExit("DEEPSEEK_API_KEY is not configured")
            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                timeout=180.0,
                max_retries=3,
            )
        return client

    def merge_language_cache(language: str) -> None:
        language_cache = cache.get(language, {})
        for item in vocabulary:
            result = language_cache.get(str(item["id"]))
            if not result:
                continue
            key = f'builtin:{item["id"]}'
            entry = translations.setdefault(key, {})
            collocations = entry.setdefault("collocations", {"source": item["collocations"]})
            example = entry.setdefault("example", {"source": item["example"]})
            # 語彙を差し替えた場合に古い翻訳が残らないよう、既存値を上書きする
            # （setdefault だと旧語の翻訳が生き残り、新語と不一致になる）。
            collocations[language] = result["collocations"]
            example[language] = result["example"]

    # 翻訳対象言語（英語以外）を先に処理する。英語 source/en の正規化は最後のループで
    # まとめて行うため、ここで "en" を先に処理して source を更新してしまうと、古い
    # 例文・コロケーションに対する翻訳が「source が一致している」と誤判定される。
    for language in LANGUAGES.keys():
        pending: list[dict[str, Any]] = []
        language_cache = cache.setdefault(language, {})
        for item in vocabulary:
            key = f'builtin:{item["id"]}'
            current = translations.get(key, {})
            if has_local_entry(current, item, language):
                continue
            cached = language_cache.get(str(item["id"]))
            if cached and has_script(cached.get("collocations"), language) and has_script(cached.get("example"), language):
                continue
            pending.append(item)

        batches = [pending[i : i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
        print(f"{language}: {len(pending)} pending in {len(batches)} batches", flush=True)
        if pending:
            api_client = get_client()
        else:
            api_client = None
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = [
                executor.submit(translate_batch, batch, language, api_client, model)
                for batch in batches
            ]
            for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                result = future.result()
                with _cache_lock:
                    language_cache.update(result)
                    CACHE.write_text(
                        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                if index % 10 == 0 or index == len(futures):
                    print(f"{language}: completed {index}/{len(futures)} batches", flush=True)

        merge_language_cache(language)
        OUTPUT.write_text(
            json.dumps({"schemaVersion": 1, "translations": translations}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    for item in vocabulary:
        key = f'builtin:{item["id"]}'
        entry = translations.setdefault(key, {})
        for field in ("collocations", "example"):
            phrase_entry = entry.setdefault(field, {"source": item[field]})
            phrase_entry["source"] = item[field]
            phrase_entry["en"] = item[field]

    OUTPUT.write_text(
        json.dumps({"schemaVersion": 1, "translations": translations}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(translations)} entries to {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
