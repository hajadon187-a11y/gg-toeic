#!/usr/bin/env python3
"""Generate vocabulary translations for the eight supported learner languages.

The meanings already present in vocabulary.json are translated into
Simplified Chinese, Hindi, Vietnamese, Korean, Indonesian, Thai, and Spanish. Results are
written back to the single JSON asset used by the app.

DeepSeek is used because this is a data-generation tool, not an app runtime
dependency. MyMemory remains available as a fallback provider. Generated
translations should still be reviewed by a native speaker before commercial
publication.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
DEFAULT_INPUT = REPO_DIR / "app/src/main/assets/vocabulary.json"
SEPARATOR = "X9QSEP9QX"
LANGUAGES = {
    "meaning": "ja",
    "meaningZh": "zh-CN",
    "meaningHi": "hi",
    "meaningVi": "vi",
    "meaningKo": "ko",
    "meaningId": "id",
    "meaningTh": "th",
    "meaningEs": "es",
}
DEFAULT_FIELDS = [field for field in LANGUAGES if field != "meaning"]


def is_valid_translation(field: str, value: str) -> bool:
    """Reject obvious wrong-script output before it reaches the app asset."""
    if not value.strip():
        return False
    if field == "meaning":
        # Japanese may contain kana, kanji, or both.  This field is generated
        # from the English gloss for the new TOEFL vocabulary set.
        return bool(re.search(r"[ぁ-ゟァ-ヿ一-鿿]", value))
    if field == "meaningVi":
        # Vietnamese uses Latin letters. CJK, Hangul, Devanagari, or kana here
        # indicates that the Japanese/source text was returned unchanged.
        has_latin = re.search(r"[A-Za-zÀ-ỹ]", value)
        has_wrong_script = re.search(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿ]", value)
        return bool(has_latin and not has_wrong_script)
    if field == "meaningId":
        # Indonesian also uses Latin letters. CJK, Hangul, Devanagari, or kana
        # indicates that the Japanese/source text was returned unchanged.
        has_latin = re.search(r"[A-Za-zÀ-ỹ]", value)
        has_wrong_script = re.search(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿ]", value)
        return bool(has_latin and not has_wrong_script)
    if field == "meaningTh":
        # Thai uses Thai script. Reject values that are only a source-language
        # echo or contain another supported language's script.
        has_thai = re.search(r"[\u0e00-\u0e7f]", value)
        has_wrong_script = re.search(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿ]", value)
        return bool(has_thai and not has_wrong_script)
    if field == "meaningHi":
        # Hindi uses Devanagari. CJK, Hangul, or kana means the source was echoed.
        has_devanagari = re.search(r"[\u0900-\u097f]", value)
        has_wrong_script = re.search(r"[ぁ-ゟァ-ヿ一-鿿가-힣]", value)
        return bool(has_devanagari and not has_wrong_script)
    if field == "meaningEs":
        # Spanish uses Latin script. Reject source-language CJK, kana, Hangul,
        # or Devanagari echoes.
        has_latin = re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", value)
        has_wrong_script = re.search(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿ]", value)
        return bool(has_latin and not has_wrong_script)
    if field == "meaningKo":
        # Korean uses Hangul. CJK, Devanagari, or kana means the source was echoed.
        has_hangul = re.search(r"[\uac00-\ud7af]", value)
        has_wrong_script = re.search(r"[ぁ-ゟァ-ヿ一-鿿ऀ-ॿ]", value)
        return bool(has_hangul and not has_wrong_script)
    # meaningZh: Simplified Chinese. Reject kana and other non-CJK scripts.
    return not bool(re.search(r"[ぁ-ゟァ-ヿ가-힣ऀ-ॿ]", value))


def request_translation(text: str, target: str, retries: int = 5, delay: float = 1.0) -> str:
    query = urllib.parse.urlencode({"q": text, "langpair": f"ja|{target}"})
    url = f"https://api.mymemory.translated.net/get?{query}"
    last_error: Optional[Exception] = None
    for attempt in range(retries):
        try:
            if delay:
                time.sleep(delay)
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("responseStatus") != 200:
                raise RuntimeError(payload.get("responseDetails") or "translation failed")
            translated = payload.get("responseData", {}).get("translatedText", "")
            if translated:
                return html.unescape(translated).strip()
            raise RuntimeError("empty translation")
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code == 429:
                # Respect the service's rate limit before retrying.
                retry_after = error.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 30)
            else:
                time.sleep(min(2 ** attempt, 16))
        except Exception as error:  # network services can transiently fail
            last_error = error
            time.sleep(min(2 ** attempt, 16))
    raise RuntimeError(f"translation failed for {target}: {last_error}")


def chunks(items: list[tuple[int, str]], max_chars: int = 800) -> list[list[tuple[int, str]]]:
    result: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    length = 0
    for item in items:
        item_length = len(item[1]) + len(SEPARATOR)
        if current and length + item_length > max_chars:
            result.append(current)
            current = []
            length = 0
        current.append(item)
        length += item_length
    if current:
        result.append(current)
    return result


def extract_json_object(content: str) -> Optional[dict]:
    """Extract a JSON object even when the model wraps it in a code fence."""
    cleaned = re.sub(r"```(?:json)?", "", content, flags=re.IGNORECASE).replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        value = json.loads(cleaned[start:end + 1])
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def extract_tab_separated_translations(content: str) -> Optional[dict[int, str]]:
    """Accept the simple id<TAB>translation format sometimes returned by the model."""
    result: dict[int, str] = {}
    for line in content.splitlines():
        match = re.match(r"^\s*(\d+)\s*\t\s*(.+?)\s*$", line)
        if match:
            result[int(match.group(1))] = match.group(2).strip()
    return result or None


def translate_batch_deepseek(
    batch: list[tuple[int, str]], target: str, client: OpenAI, model: str
) -> dict[int, str]:
    language_names = {
        "ja": "Japanese",
        "zh-CN": "Simplified Chinese",
        "hi": "Hindi",
        "vi": "Vietnamese",
        "ko": "Korean",
        "id": "Indonesian",
        "th": "Thai",
        "es": "Spanish",
    }
    source = "\n".join(f"{index}\t{text}" for index, text in batch)
    source_language = "English"
    prompt = f"""Translate the {source_language} vocabulary meanings below into {language_names[target]}.
Return ONLY a valid JSON object mapping each numeric id to one natural, concise translation.
The value must contain ONLY the target-language translation. Do not echo the Japanese source,
do not put Japanese before the translation in parentheses, and do not add explanations.
Preserve the meaning and usage notes, and do not omit any id.

For Vietnamese specifically, use Vietnamese Latin script only; never output Japanese, Chinese,
Korean, or Hindi characters in a value.

For Indonesian specifically, use Indonesian Latin script only; never output Japanese, Chinese,
Korean, or Hindi characters in a value.

For Thai specifically, use natural, concise Thai suitable for a vocabulary-learning app;
use Thai script in every value; never output Japanese, Chinese, Korean, Hindi, or
Vietnamese text in a value. For example, translate “satellite” as “ดาวเทียม”,
never as Chinese characters.

For Spanish specifically, use natural, concise Spanish suitable for a vocabulary-learning app;
never output Japanese, Chinese, Korean, Hindi, Thai, or Vietnamese text in a value.

For Japanese specifically, use a natural, concise Japanese gloss suitable for TOEFL
vocabulary-learning app; do not output English-only text or the source definition verbatim.

{source}
"""
    translation_field = next(
        field for field, language in LANGUAGES.items() if language == target
    )
    result = None
    content = ""
    complete = False
    for attempt in range(3):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        result = extract_json_object(content)
        if result is None:
            result = extract_tab_separated_translations(content)
        complete = result is not None and all(
            isinstance(result.get(str(index), result.get(index)), str)
            and is_valid_translation(
                translation_field,
                result.get(str(index), result.get(index)),
            )
            for index, _ in batch
        )
        if complete:
            break
        if len(batch) > 1:
            break
        time.sleep(1.0 + attempt)
    if not complete and len(batch) > 1:
        # Retry malformed or truncated responses with smaller batches.
        middle = len(batch) // 2
        left = translate_batch_deepseek(batch[:middle], target, client, model)
        right = translate_batch_deepseek(batch[middle:], target, client, model)
        return {**left, **right}
    if not complete:
        raise RuntimeError(f"DeepSeek returned invalid JSON: {content[:200]}")
    translated: dict[int, str] = {}
    for index, _ in batch:
        value = result.get(str(index), result.get(index))
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"DeepSeek omitted translation for id {index}")
        translated[index] = value.strip()
    return translated


def translate_batch(
    batch: list[tuple[int, str]],
    target: str,
    delay: float,
    provider: str,
    client: Optional[OpenAI] = None,
    model: str = "deepseek-chat",
) -> dict[int, str]:
    if provider == "deepseek":
        if client is None:
            raise RuntimeError("DeepSeek client is not configured")
        if delay:
            time.sleep(delay)
        return translate_batch_deepseek(batch, target, client, model)

    source = SEPARATOR.join(text for _, text in batch)
    translated = request_translation(source, target, delay=delay)
    parts = [part.strip() for part in translated.split(SEPARATOR)]
    if len(parts) != len(batch):
        # A provider may alter the separator. Retry each item so one malformed
        # batch does not corrupt the alignment of all subsequent translations.
        return {index: request_translation(text, target, delay=delay) for index, text in batch}
    return {index: value for (index, _), value in zip(batch, parts)}


def load_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(path: Path, cache: dict[str, str]) -> None:
    path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--cache", type=Path, default=Path("/private/tmp/toefl-translation-deepseek-cache.json"))
    parser.add_argument("--provider", choices=["deepseek", "mymemory"], default="deepseek")
    parser.add_argument(
        "--only",
        choices=list(LANGUAGES),
        action="append",
        help="translate only the specified field; may be repeated",
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--delay", type=float, default=0.5, help="seconds between requests per worker")
    args = parser.parse_args()

    if args.provider == "deepseek":
        load_dotenv(BASE_DIR / ".env")
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key or api_key == "sk-xxxx":
            raise SystemExit("DEEPSEEK_API_KEY is not configured in tools/vocabulary-builder/.env")
        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            timeout=120.0,
            max_retries=3,
        )
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    else:
        client = None
        model = ""

    data = json.loads(args.input.read_text(encoding="utf-8"))
    cache = load_cache(args.cache)
    fields = {field: LANGUAGES[field] for field in (args.only or DEFAULT_FIELDS)}
    for field, target in fields.items():
        pending = [
            (
                index,
                item.get("meaningEn", "") or item.get("meaning", ""),
            )
            for index, item in enumerate(data)
            if item.get("meaning", "") and not is_valid_translation(
                field, cache.get(f"{field}:{index}", "")
            )
        ]
        # Smaller DeepSeek batches reduce source-echo and malformed JSON responses.
        batches = chunks(pending, max_chars=500 if args.provider == "deepseek" else 800)
        print(f"{field}: {len(pending)} items in {len(batches)} batches", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(
                translate_batch, batch, target, args.delay, args.provider, client, model
            ) for batch in batches]
            completed_batches = 0
            for future in concurrent.futures.as_completed(futures):
                for index, value in future.result().items():
                    cache[f"{field}:{index}"] = value
                completed_batches += 1
                if completed_batches % 10 == 0:
                    save_cache(args.cache, cache)
        for index, item in enumerate(data):
            candidate = cache.get(f"{field}:{index}", item.get(field, ""))
            item[field] = candidate if is_valid_translation(field, candidate) else ""
        save_cache(args.cache, cache)

    serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    args.input.write_text(serialized, encoding="utf-8")
    print(f"Wrote {len(data)} vocabulary entries to {args.input}", flush=True)


if __name__ == "__main__":
    main()
