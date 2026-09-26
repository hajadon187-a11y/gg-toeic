#!/usr/bin/env python3
"""Offline quality audit for the vocabulary phrase assets.

Checks the four relationships the shipped app depends on, across every one of
the 6,384 built-in words:

  1. word <-> example        the headword (or an inflected form) appears in the
                             example sentence
  2. example -> translations each of the eight learner-language translations is
                             present, written in the right script, and free of
                             untranslated English
  3. collocations            every segment is a real collocation of the headword
                             (no duplicates, no explanatory parentheses, no
                             British/American spelling split)
  4. collocations -> trans.  the translation has the same number of segments as
                             the English source, uses one consistent separator,
                             and does not leave English behind

This tool never calls an external API: every check is deterministic and can be
re-run on the shipped JSON alone.

Usage:
  python3 audit_phrase_quality.py                 # 全件監査
  python3 audit_phrase_quality.py --json out.json # JSONレポートも出力
  python3 audit_phrase_quality.py --fail-on none  # 常に終了コード0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"

# 8 learner languages shipped for every phrase, plus the English echo.
LANGS = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es")

# 訳文がその言語の文字で書かれていることを確認するための最小要件。
SCRIPT_PATTERNS = {
    "ja": r"[\u3041-\u309f\u30a0-\u30ff\u4e00-\u9fff]",
    "zh": r"[\u4e00-\u9fff]",
    "hi": r"[\u0900-\u097f]",
    "ko": r"[\uac00-\ud7af]",
    "th": r"[\u0e01-\u0e5b]",
}

# 訳文に残ってよい英字（略語・単位・固有名詞）。
ALLOWED_LATIN = {
    "gpa", "sat", "toefl", "dna", "rna", "ph", "rem", "swot", "usb", "gps",
    "phd", "ceo", "tv", "cd", "dvd", "pdf", "ppt", "ai", "ml", "api", "url",
    "html", "css", "sql", "cpu", "gpu", "ram", "kg", "km", "cm", "mm", "hz",
    "uk", "usa", "us", "nyu", "mit", "it",
}
TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]+")

# 英字を残してはいけない言語。vi/id/es はラテン文字を使うため対象外。
# 訳文中の「英語のまま残った語」を検出するのは非ラテン文字言語だけで意味を持つ。
NON_LATIN_LANGS = ("ja", "zh", "hi", "ko", "th")


# 英語の綴りが米英で割れている語。見出し語側は米綴りに統一している。
UK_TO_US = {
    "gynaecologist": "gynecologist", "socialise": "socialize",
    "socialised": "socialized", "socialising": "socializing",
    "archaeologist": "archeologist", "archaeology": "archeology",
    "archaeological": "archeological", "institutionalise": "institutionalize",
    "institutionalised": "institutionalized", "institutionalising": "institutionalizing",
    "candour": "candor", "meagre": "meager", "leveller": "leveler",
    "lacklustre": "lackluster", "behaviour": "behavior", "colour": "color",
    "favour": "favor", "honour": "honor", "labour": "labor",
    "neighbour": "neighbor", "organise": "organize", "realise": "realize",
    "recognise": "recognize", "analyse": "analyze", "centre": "center",
    "theatre": "theater", "programme": "program", "catalogue": "catalog",
    "defence": "defense", "haemoglobin": "hemoglobin", "utilise": "utilize",
    "utilised": "utilized",
}
UK_RE = re.compile(
    r"(?<![a-z])(" + "|".join(sorted(UK_TO_US, key=len, reverse=True)) + r")(?![a-z])",
    re.IGNORECASE,
)

# 見出し語自体が英綴りの語。アプリ内に米綴りの同義語が別IDで存在し、
# 見出し語とコロケーションの綴りは内部で一致しているため不整合ではない。
UK_HEADWORD_IDS = frozenset({
    2862, 4583, 5500, 5501, 5517, 5632, 5741, 5770, 6164, 6165,
})

# コロケーションに現れてはいけない説明カッコ: "bat (animal)" のような補足。
PAREN_RE = re.compile(r"\s*\([^)]*\)")

# 韓国語訳の動詞活用が二重になっている破損パターン。
# 語幹の活用語尾がさらに活用語尾と連結してしまっている（例: 좋아하다한다）。
# 左が誤り、右が正しい形。長いパターンから順に適用する。
KO_CONJUGATION_FIXES = (
    ("하다하라고", "하라고"),
    ("하다한다", "한다"),
    ("하다 했다", "했다"),
    ("하다했다", "했다"),
    ("한다한다", "한다"),
    ("했다했다", "했다"),
    ("하다 한다", "한다"),
)



def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def inflected_forms(word: str) -> set[str]:
    """見出し語の一般的な屈折形を返す（例文の照合に使う）。

    見出し語そのものに加えて、三人称単数・過去形・進行形・複数形・比較級など
    アプリの例文に出てくる形を生成する。派生語（tion / ment など）は作らない。
    """
    target = word.strip().lower()
    if not target:
        return set()
    forms = {target}
    last = target[-1]

    # 複数形・三人称単数 -s / -es / -ies
    if target.endswith("y") and len(target) > 1 and target[-2] not in "aeiou":
        forms.add(target[:-1] + "ies")
    if target.endswith(("s", "x", "z", "ch", "sh")):
        forms.add(target + "es")
    forms.add(target + "s")

    # 過去形・過去分詞 -ed
    forms.add(target + "ed")
    if last == "e":
        forms.add(target + "d")
    if target.endswith("y") and len(target) > 1 and target[-2] not in "aeiou":
        forms.add(target[:-1] + "ied")

    # 進行形 -ing
    forms.add(target + "ing")
    if last == "e":
        forms.add(target[:-1] + "ing")

    # 比較級・最上級・副詞 -er / -est / -ly
    forms.add(target + "er")
    forms.add(target + "est")
    if last == "y" and len(target) > 1 and target[-2] not in "aeiou":
        forms.add(target[:-1] + "ier")
        forms.add(target[:-1] + "iest")
    forms.add(target + "ly")
    if last == "e":
        forms.add(target + "r")
        forms.add(target + "st")
        forms.add(target[:-1] + "ly")

    # 子音重複形 (stop -> stopped / stopping)
    if len(target) > 2 and target[-1] not in "aeiouwxy" and target[-2] in "aeiou" and target[-3] not in "aeiou":
        forms.add(target + target[-1] + "ed")
        forms.add(target + target[-1] + "ing")

    return {form for form in forms if form}


def headword_present(word: str, haystack: str) -> bool:
    """見出し語（または屈折形）がテキストに含まれるか。"""
    lowered = haystack.lower()
    for form in inflected_forms(word):
        if re.search(rf"(?<![a-z]){re.escape(form)}(?![a-z])", lowered):
            return True
    return False


def segments(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,、，;；]", value) if part.strip()]


def latin_leaks(value: str) -> list[str]:
    tokens = {token.lower().strip("'-") for token in TOKEN.findall(value)}
    return sorted(token for token in tokens if token and token not in ALLOWED_LATIN)



def build_findings(vocabulary: list, translations: dict) -> dict:
    findings: dict[str, list[dict[str, object]]] = {
        "word_example": [], "example_translation": [],
        "collocations": [], "collocation_translation": [],
    }
    for item in vocabulary:
        item_id, word = item["id"], item["word"]
        entry = translations.get(f"builtin:{item_id}", {})
        example = entry.get("example", {})
        collocations = entry.get("collocations", {})
        source = item["collocations"]

        # ── 1. word <-> example ────────────────────────────────────────
        if not headword_present(word, item["example"]):
            findings["word_example"].append(
                {"id": item_id, "word": word, "example": item["example"]}
            )

        # ── 2. example -> translations ────────────────────────────────
        for lang in LANGS:
            value = str(example.get(lang, ""))
            if not value.strip():
                findings["example_translation"].append(
                    {"id": item_id, "word": word, "lang": lang, "issue": "empty"}
                )
                continue
            pattern = SCRIPT_PATTERNS.get(lang)
            if pattern and not re.search(pattern, value):
                findings["example_translation"].append(
                    {"id": item_id, "word": word, "lang": lang,
                     "issue": "wrong_script", "value": value}
                )
            if lang in NON_LATIN_LANGS:
                leaks = latin_leaks(value)
                if leaks:
                    findings["example_translation"].append(
                        {"id": item_id, "word": word, "lang": lang,
                         "issue": "latin_leak", "tokens": leaks, "value": value}
                    )
        korean = str(example.get("ko", ""))
        for broken, _ in KO_CONJUGATION_FIXES:
            if broken in korean:
                findings["example_translation"].append(
                    {"id": item_id, "word": word, "lang": "ko",
                     "issue": "broken_conjugation", "token": broken, "value": korean}
                )
                break


        # ── 3. collocations ───────────────────────────────────────────
        parts = segments(source)
        lowered = [part.lower() for part in parts]

        # 見出し語が米綴りなのに、同じ語のコロケーションが英綴りになっている場合だけ
        # 不整合として報告する（無関係な centre / labour は対象外）。
        word_uk = UK_RE.search(word)
        uk_mismatch = False
        if word_uk and item_id not in UK_HEADWORD_IDS:
            us_form = UK_TO_US[word_uk.group(0).lower()]
            same_word_uk = re.compile(
                rf"(?<![a-z]){re.escape(word_uk.group(0))}(?![a-z])", re.IGNORECASE
            )
            if same_word_uk.search(source) and not re.search(
                rf"(?<![a-z]){re.escape(us_form)}(?![a-z])", source, re.IGNORECASE
            ):
                uk_mismatch = True
                findings["collocations"].append(
                    {"id": item_id, "word": word, "issue": "uk_spelling",
                     "source": source, "tokens": [word_uk.group(0).lower()],
                     "expected": us_form}
                )

        if not uk_mismatch and not headword_present(word, source):
            findings["collocations"].append(
                {"id": item_id, "word": word, "issue": "headword_missing", "source": source}
            )
        if len(lowered) != len(set(lowered)):
            findings["collocations"].append(
                {"id": item_id, "word": word, "issue": "duplicate_segment", "source": source}
            )
        paren = PAREN_RE.search(source)
        if paren:
            findings["collocations"].append(
                {"id": item_id, "word": word, "issue": "parenthetical",
                 "source": source, "match": paren.group(0).strip()}
            )

        # ── 4. collocations -> translations ───────────────────────────
        expected = len(parts)
        for lang in LANGS:
            value = str(collocations.get(lang, ""))
            if not value.strip():
                findings["collocation_translation"].append(
                    {"id": item_id, "word": word, "lang": lang, "issue": "empty"}
                )
                continue
            pattern = SCRIPT_PATTERNS.get(lang)
            if pattern and not re.search(pattern, value):
                findings["collocation_translation"].append(
                    {"id": item_id, "word": word, "lang": lang,
                     "issue": "wrong_script", "value": value}
                )
            if lang in NON_LATIN_LANGS:
                leaks = latin_leaks(value)
                if leaks:
                    findings["collocation_translation"].append(
                        {"id": item_id, "word": word, "lang": lang,
                         "issue": "latin_leak", "tokens": leaks, "value": value}
                    )
            actual = len(segments(value))
            if actual != expected:
                findings["collocation_translation"].append(
                    {"id": item_id, "word": word, "lang": lang,
                     "issue": "segment_count", "expected": expected, "actual": actual,
                     "source": source, "value": value}
                )
        # 区切り記号の不統一（中国語は「，」、日本語は「、」に統一する）
        zh_value = str(collocations.get("zh", ""))
        if "；" in zh_value:
            findings["collocation_translation"].append(
                {"id": item_id, "word": word, "lang": "zh",
                 "issue": "separator_semicolon", "value": zh_value}
            )
        ja_value = str(collocations.get("ja", ""))
        if "," in ja_value:
            findings["collocation_translation"].append(
                {"id": item_id, "word": word, "lang": "ja",
                 "issue": "separator_ascii_comma", "value": ja_value}
            )
    return findings



LABELS = {
    "word_example": "word x example",
    "example_translation": "example translations",
    "collocations": "collocations (English)",
    "collocation_translation": "collocation translations",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="結果をJSONで書き出す先")
    parser.add_argument(
        "--fail-on", choices=["any", "none"], default="any",
        help="any: 問題があれば終了コード1 / none: 常に0",
    )
    args = parser.parse_args()

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    translations = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))["translations"]
    findings = build_findings(vocabulary, translations)

    print(f"vocabulary words: {len(vocabulary)}")
    for key, label in LABELS.items():
        by_issue = Counter(finding.get("issue", "mismatch") for finding in findings[key])
        detail = ", ".join(f"{name}={count}" for name, count in sorted(by_issue.items()))
        suffix = f" [{detail}]" if detail else ""
        print(f"  {label}: {len(findings[key])} issue(s){suffix}")
        for finding in findings[key][:5]:
            print(f"      - {finding}")

    total = sum(len(value) for value in findings.values())
    if args.json:
        args.json.write_text(
            json.dumps(
                {"wordCount": len(vocabulary), "totalIssues": total, "findings": findings},
                ensure_ascii=False, indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"report written: {args.json}")

    if total and args.fail_on == "any":
        print(f"audit failed: {total} issue(s)")
        return 1
    print("audit passed" if not total else f"audit finished with {total} issue(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

