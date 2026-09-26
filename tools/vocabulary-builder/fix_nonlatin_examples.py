"""Translate English phrases that leaked into non-Latin example translations.

`translate_example_gaps.py` removes English words that duplicate the entry's
headword. A separate and more visible defect is a whole English noun phrase or
subject pronoun left inside Japanese, Korean, Thai, Chinese, or Hindi sentences:

    hi: "मैं अपने प्रोफेसर के office hours के लिए तैयार रहना चाहता हूं"
    ko: "We는 생물학 시험 전에 도서관에서 함께 공부한다."

This tool finds those Latin-script tokens in the five non-Latin target languages
and replaces them with the target-language equivalent, so no English remains.

Usage:
  python3 fix_nonlatin_examples.py --collect
  python3 fix_nonlatin_examples.py --workers 8
"""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import re
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-nonlatin-lexicon.json")
BATCH_SIZE = 30

SCRIPT_PATTERNS = {
    "ja": r"[\u3040-\u30ff\u4e00-\u9fff]",
    "zh": r"[\u4e00-\u9fff]",
    "hi": r"[\u0900-\u097f]",
    "ko": r"[\uac00-\ud7af]",
    "th": r"[\u0e00-\u0e7f]",
}
LATIN_RUN = re.compile(r"[A-Za-z][A-Za-z'\-]*(?:\s+[A-Za-z][A-Za-z'\-]*)*")
# 人名・地名・略語・成績として残ってよい語。
KEEP = {
    "iq", "gpa", "sat", "toefl", "dna", "rna", "ph", "id", "tv", "ceo", "rem",
    "ohio", "maya", "mary", "john", "lee", "chen", "smith", "jones", "boston",
    "chicago", "california", "texas", "nyu", "mit", "harvard", "yale", "stanford",
    "oxford", "cambridge", "amazon", "google", "microsoft",
}


def load_module():
    spec = importlib.util.spec_from_file_location(
        "translate_example_gaps", BASE_DIR / "translate_example_gaps.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def latin_runs(value: str) -> list[str]:
    """訳文に残ったラテン文字の語句のうち、訳すべきものを返す。"""
    runs: list[str] = []
    for match in LATIN_RUN.finditer(value):
        phrase = match.group(0).strip()
        if phrase.lower() in KEEP or len(phrase) < 2:
            continue
        # "3D" のような数字付きの技術用語はそのまま許容する。
        if re.fullmatch(r"\d+[A-Za-z]+", phrase):
            continue
        if phrase not in runs:
            runs.append(phrase)
    return runs


def collect(vocabulary: list[dict], translations: dict) -> dict[str, dict[str, str]]:
    """言語ごとに「英語のまま残った語句 -> 代表的な文脈」を集める。"""
    gaps: dict[str, dict[str, str]] = {}
    for item in vocabulary:
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            continue
        for language in SCRIPT_PATTERNS:
            value = str(record.get(language, "")).strip()
            if not value:
                continue
            for phrase in latin_runs(value):
                gaps.setdefault(language, {}).setdefault(phrase.lower(), value)
    return gaps



def main() -> int:
    parser = argparse.ArgumentParser(description="非ラテン文字の訳文に残った英語を訳す")
    parser.add_argument("--collect", action="store_true", help="棚卸しのみ")
    parser.add_argument("--workers", type=int, default=8, help="並列数")
    parser.add_argument("--check", action="store_true", help="書き込まずに確認")
    args = parser.parse_args()

    module = load_module()
    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root["translations"]

    gaps = collect(vocabulary, translations)
    for language in sorted(gaps):
        print(f"{language}: {len(gaps[language])} distinct English phrases")
    print("total:", sum(len(v) for v in gaps.values()))
    if args.collect:
        return 0

    lexicon: dict[str, dict[str, str]] = {}
    if CACHE.exists():
        lexicon = json.loads(CACHE.read_text("utf-8"))

    provider = module.Provider()
    lock = threading.Lock()

    def run(language: str) -> None:
        pending = [p for p in sorted(gaps[language]) if p not in lexicon.get(language, {})]
        if not pending:
            print(f"  {language}: cached")
            return
        items = [{"token": p, "sentence": gaps[language][p]} for p in pending]
        produced: dict[str, str] = {}
        for start in range(0, len(items), BATCH_SIZE):
            chunk = items[start : start + BATCH_SIZE]
            try:
                produced.update(module.translate_tokens(provider, language, chunk))
            except Exception as error:  # noqa: BLE001 - 1バッチの失敗で全体を止めない
                print(f"  {language} バッチ失敗: {type(error).__name__}: {error}")
        with lock:
            lexicon.setdefault(language, {}).update(produced)
            CACHE.write_text(json.dumps(lexicon, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {language}: {len(produced)}/{len(pending)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        list(executor.map(run, sorted(gaps)))


    replaced = 0
    for item in vocabulary:
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            continue
        for language in SCRIPT_PATTERNS:
            value = str(record.get(language, "")).strip()
            if not value:
                continue
            updated = value
            for phrase in latin_runs(value):
                replacement = lexicon.get(language, {}).get(phrase.lower())
                if not replacement:
                    continue
                updated = re.sub(
                    rf"(?<![A-Za-z]){re.escape(phrase)}(?![A-Za-z])", replacement, updated
                )
                replaced += 1
            record[language] = updated

    remaining = 0
    for item in vocabulary:
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if isinstance(record, dict):
            for language in SCRIPT_PATTERNS:
                if latin_runs(str(record.get(language, ""))):
                    remaining += 1
    print(f"replacements: {replaced} / rows still containing English: {remaining}")

    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {PHRASES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
