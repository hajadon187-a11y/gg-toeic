#!/usr/bin/env python3
"""Run the native-speaker quality audit one language at a time.

`extract_language_slices.py` cuts the shipped assets into `data/slices/{lang}.json`
so that a review never has to hold all 9 languages at once. This tool consumes
those slices and drives the actual native-editor pass:

1. read one slice at a time (`--only` picks a single language)
2. split that slice into small batches that fit a normal request budget
3. ask the model, as a native editor of that one language, only for entries that
   are unnatural, literal, incomplete or wrong; unchanged entries stay out of
   the answer
4. cache every finished batch per (language, id) so an interrupted run resumes
5. write a per-language report and, with `--apply`, merge the corrections back
   into `vocabulary.json` and `vocabulary_phrase_translations.json`

Running one language per invocation is the whole point: the largest slice is
about 500K translated tokens and the run is chunked well below that, so no
single pass is ever near the multi-million-token ceiling that made the
all-languages review impossible.

Usage:
  python3 audit_language_slices.py --only es --dry-run   # 対象件数の確認
  python3 audit_language_slices.py --only es --limit 40  # 疎通確認
  python3 audit_language_slices.py --only es             # 1言語を全件
  python3 audit_language_slices.py --all                 # 8言語を順に全件
  python3 audit_language_slices.py --only es --apply     # 結果をアセットへ反映
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
SLICE_DIR = BASE_DIR / "data" / "slices"
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
DEFAULT_CACHE = Path("/private/tmp/toefl-language-audit-cache.json")
DEFAULT_REPORT = Path("/private/tmp/toefl-language-audit-report.json")

# `audit_phrase_quality.py` / `review_phrase_translations.py` と同じ言語表。
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
LATIN_LANGS = frozenset({"vi", "id", "es"})
WRONG_SCRIPT = re.compile(r"[ぁ-ゟァ-ヿ一-鿿가-힣ऀ-ॿก-๛]")

# 見出し語・単位・略語として訳文に残ってよい英字。
ALLOWED_LATIN = {
    "gpa", "sat", "toefl", "dna", "rna", "ph", "rem", "swot", "usb", "gps",
    "phd", "ceo", "tv", "cd", "dvd", "pdf", "ppt", "ai", "ml", "api", "url",
    "html", "css", "sql", "cpu", "gpu", "ram", "kg", "km", "cm", "mm", "hz",
    "uk", "usa", "us", "nyu", "mit", "it",
}


def log(message: str) -> None:
    print(f"[language-audit] {time.strftime('%H:%M:%S')} | {message}", flush=True)


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
    """訳文がその言語の文字で書かれているか。"""
    if not isinstance(value, str) or not value.strip():
        return False
    if not re.search(LANGUAGES[language][1], value):
        return False
    if language in LATIN_LANGS and WRONG_SCRIPT.search(value):
        return False
    return True


def latin_leaks(value: str) -> list[str]:
    """非ラテン文字言語の訳文に残った英単語を返す。"""
    tokens = {token.lower().strip("'-") for token in re.findall(r"[A-Za-z][A-Za-z'-]+", value)}
    return sorted(token for token in tokens if token and token not in ALLOWED_LATIN)


def collocation_count(value: str) -> int:
    return len([part for part in re.split(r"[,、，;；]", value) if part.strip()])


def valid_translation(raw: object, source: dict[str, Any], language: str) -> bool:
    """モデルの訳文が受け入れ可能か決定論的に検査する。

    文字種・英字残り・項目数を、出荷前監査 `audit_phrase_quality.py` と同じ基準で見る。
    """
    if not isinstance(raw, dict):
        return False
    example = raw.get("example")
    collocations = raw.get("collocations")
    if not has_target_script(example, language) or not has_target_script(collocations, language):
        return False
    if language not in LATIN_LANGS:
        if latin_leaks(str(example)) or latin_leaks(str(collocations)):
            return False
    if collocation_count(str(collocations)) != collocation_count(source["collocationsSource"]):
        return False
    return True


def prompt_for(batch: list[dict[str, Any]], language: str) -> str:
    name = LANGUAGES[language][0]
    payload = "\n".join(
        f'{item["id"]}\tword={item["word"]}\t'
        f'EN meaning={item["meaningEn"]}\tCURRENT meaning={item["meaning"]}\t'
        f'EN example={item["exampleSource"]}\tCURRENT example={item["example"]}\t'
        f'EN collocations={item["collocationsSource"]}\tCURRENT collocations={item["collocations"]}'
        for item in batch
    )
    return f"""You are a meticulous native {name} editor reviewing a TOEFL vocabulary app.
For every item, judge each CURRENT {name} field against its English source:
the meaning gloss, the example sentence, and the collocation list.

Report an item only when at least one field is wrong. A field is wrong when it is
unnatural or non-idiomatic for a native speaker, a literal translation, incomplete,
ambiguous, or when it changes the meaning, tense, modality, subject, number, or
logical relationship of the English source. A field that is already accurate and
natural must be left out of the answer entirely.

Return ONLY a valid JSON object keyed by the numeric id, and include only the ids
you are correcting. Each value has this exact shape:
{{"numeric_id": {{"meaning": "corrected {name} meaning", "example": "corrected {name} example", "collocations": "corrected {name} collocations"}}}}
Every value must contain only {name}, with no English source, labels, comments,
alternatives, brackets, or quality scores. Preserve the order and number of
collocations, separated by commas or the standard list separator for {name}.
Use the standard script of {name}. Omit a key when that field is already correct.

Items:
{payload}
"""


def audit_batch(
    batch: list[dict[str, Any]], language: str, client: OpenAI, model: str
) -> dict[int, dict[str, str]]:
    """1バッチを監査する。返すのは修正が必要だった項目だけ。"""
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
                if raw is None:
                    continue  # 問題なし = 回答に含めない、が仕様
                if not isinstance(raw, dict):
                    continue
                corrected: dict[str, str] = {}
                for field in ("meaning", "example", "collocations"):
                    value = raw.get(field)
                    if isinstance(value, str) and value.strip():
                        corrected[field] = value.strip()
                source = {
                    "collocationsSource": item["collocationsSource"],
                }
                merged = {
                    "example": corrected.get("example", item["example"]),
                    "collocations": corrected.get("collocations", item["collocations"]),
                }
                if corrected and valid_translation(merged, source, language):
                    result[item["id"]] = corrected
            return result
        if len(batch) > 1:
            middle = len(batch) // 2
            return {
                **audit_batch(batch[:middle], language, client, model),
                **audit_batch(batch[middle:], language, client, model),
            }
        time.sleep(1.0 + attempt)
    # 1件でも解析できない応答が続く入力がある。その項目は「修正なし」として扱い、
    # 言語全体の監査を止めない（`review_phrase_translations.py` と同じ方針）。
    return {}


def load_slice(language: str, slice_dir: Path) -> dict[str, Any]:
    path = slice_dir / f"{language}.json"
    if not path.exists():
        raise SystemExit(
            f"スライスがありません: {path}\n"
            f"先に `python3 extract_language_slices.py --only {language}` を実行してください。"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def batch_items(entries: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    return [entries[i : i + batch_size] for i in range(0, len(entries), batch_size)]


def apply_corrections(
    language: str, cache: dict[str, dict[str, str]], vocabulary: list, dictionary: dict
) -> int:
    """キャッシュ済みの修正を出荷アセットへ反映する。変更したフィールド数を返す。"""
    translations = dictionary["translations"]
    meaning_field = "meaning" if language == "ja" else f"meaning{language.capitalize()}"
    changed = 0
    for item in vocabulary:
        value = cache.get(f"{language}:{item['id']}")
        if not value:
            continue
        if "meaning" in value and value["meaning"] != item.get(meaning_field, ""):
            item[meaning_field] = value["meaning"]
            changed += 1
        entry = translations.get(f"builtin:{item['id']}")
        if not entry:
            continue
        for field in ("example", "collocations"):
            if field in value and value[field] != entry[field].get(language, ""):
                entry[field][language] = value[field]
                changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=list(LANGUAGES), action="append",
                        help="この言語だけを監査する（複数指定可）")
    parser.add_argument("--all", action="store_true", help="8言語を順に監査する")
    parser.add_argument("--slice-dir", type=Path, default=SLICE_DIR)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--batch-size", type=int, default=12)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--limit", type=int, help="1言語あたり先頭N件だけ（疎通確認用）")
    parser.add_argument("--dry-run", action="store_true",
                        help="APIを呼ばず対象件数とバッチ数だけ表示する")
    parser.add_argument("--apply", action="store_true",
                        help="キャッシュ済みの修正を出荷アセットへ書き戻す")
    args = parser.parse_args()

    if not args.only and not args.all:
        raise SystemExit("--only <lang> か --all を指定してください。")

    # 既定では1言語ずつ。--all のときだけ全言語を順に処理する。
    languages = args.only or list(LANGUAGES)

    cache: dict[str, dict[str, str]] = (
        json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    )
    log(f"キャッシュ: {args.cache}（{len(cache)} 件）")

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    dictionary = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))

    client: Optional[OpenAI] = None
    model = ""
    if not args.dry_run and not args.apply:
        load_dotenv(BASE_DIR / ".env")
        api_key = os.getenv("LUNA_API_KEY", "").strip()
        base_url = os.getenv("LUNA_BASE_URL", "").strip()
        model = os.getenv("LUNA_MODEL", "").strip()
        if not api_key or not base_url or not model:
            raise SystemExit("LUNA_API_KEY / LUNA_BASE_URL / LUNA_MODEL を .env に設定してください。")
        client = OpenAI(api_key=api_key, base_url=base_url)
        log(f"プロバイダ: LUNA ({model})")

    report: dict[str, dict[str, Any]] = {}
    for language in languages:
        payload = load_slice(language, args.slice_dir)
        entries = payload["entries"]
        if args.limit:
            entries = entries[: args.limit]
        pending = [entry for entry in entries if not cache.get(f"{language}:{entry['id']}")]
        batches = batch_items(pending, args.batch_size)
        log(
            f"{language}: {len(entries)} entries, {len(pending)} pending, "
            f"{len(batches)} batches (batch-size={args.batch_size})"
        )
        report[language] = {
            "entries": len(entries),
            "pending": len(pending),
            "batches": len(batches),
            "corrected": sum(
                1 for entry in entries if cache.get(f"{language}:{entry['id']}")
            ),
        }

        if args.dry_run or not batches or client is None:
            continue

        before = report[language]["corrected"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(audit_batch, batch, language, client, model): batch
                for batch in batches
            }
            for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
                result = future.result()
                for item_id, value in result.items():
                    cache[f"{language}:{item_id}"] = value
                # 修正なしと確定した項目も記録し、再実行時に再送しない。
                for item in futures[future]:
                    cache.setdefault(f"{language}:{item['id']}", {})
                if index % 10 == 0 or index == len(futures):
                    args.cache.write_text(
                        json.dumps(cache, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    log(f"{language}: completed {index}/{len(futures)} batches")
                if args.delay:
                    time.sleep(args.delay)
        report[language]["corrected"] = sum(
            1 for entry in entries if cache.get(f"{language}:{entry['id']}")
        )
        log(f"{language}: {report[language]['corrected'] - before} entries corrected")

    if args.apply:
        total = 0
        for language in languages:
            changed = apply_corrections(language, cache, vocabulary, dictionary)
            total += changed
            log(f"{language}: applied {changed} field(s)")
        VOCAB_PATH.write_text(
            json.dumps(vocabulary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        PHRASE_PATH.write_text(
            json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        log(f"アセットへ反映しました（{total} フィールド）")

    args.report.write_text(
        json.dumps(
            {"mode": "apply" if args.apply else "audit", "languages": report},
            ensure_ascii=False, indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    log(f"レポート: {args.report}")
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
