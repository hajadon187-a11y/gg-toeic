#!/usr/bin/env python3
"""High-precision offline audit for the shipped vocabulary translations.

This audit deliberately prefers precision over recall.  It reports only
deterministic defects as errors; linguistic judgments that can be valid in
context (proper names, English terms used as examples, derived headwords,
synonymous translations, and commas inside a translated phrase) are warnings.

It never calls an external API and never modifies shipped assets.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"

LANGS = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es")
ALL_LANGS = LANGS + ("en",)
MEANING_FIELDS = {
    "ja": "meaning",
    "zh": "meaningZh",
    "hi": "meaningHi",
    "vi": "meaningVi",
    "ko": "meaningKo",
    "id": "meaningId",
    "th": "meaningTh",
    "es": "meaningEs",
}

SCRIPT_PATTERNS = {
    "ja": r"[\u3041-\u309f\u30a0-\u30ff\u4e00-\u9fff]",
    "zh": r"[\u4e00-\u9fff]",
    "hi": r"[\u0900-\u097f]",
    "ko": r"[\uac00-\ud7af]",
    "th": r"[\u0e01-\u0e5b]",
    "vi": r"[A-Za-zÀ-ỹ]",
    "id": r"[A-Za-zÀ-ÿ]",
    "es": r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]",
}

NON_LATIN = frozenset({"ja", "zh", "hi", "ko", "th"})
# A target translation may contain Latin loanwords or acronyms, but an
# incompatible native script is a high-confidence copy/paste or generation
# defect.  Han characters are allowed in Japanese and Japanese kana are kept
# separate because they are not interchangeable in Chinese.
FOREIGN_SCRIPT_PATTERNS = {
    "ja": re.compile(r"[\uac00-\ud7af\u0900-\u097f\u0e01-\u0e5b]"),
    "zh": re.compile(r"[\u3041-\u30ff\uac00-\ud7af\u0900-\u097f\u0e01-\u0e5b]"),
    "hi": re.compile(r"[\u3041-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0e01-\u0e5b]"),
    "ko": re.compile(r"[\u3041-\u30ff\u4e00-\u9fff\u0900-\u097f\u0e01-\u0e5b]"),
    "th": re.compile(r"[\u3041-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0900-\u097f]"),
    "vi": re.compile(r"[\u3041-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0900-\u097f\u0e01-\u0e5b]"),
    "id": re.compile(r"[\u3041-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0900-\u097f\u0e01-\u0e5b]"),
    "es": re.compile(r"[\u3041-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0900-\u097f\u0e01-\u0e5b]"),
}
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")

# These are intentionally warnings, not errors.  A native translation may
# legitimately retain an acronym, a proper name, or the English word being
# taught (for example, antiwar in the word "anti").
ALLOWED_LATIN = {
    "gpa", "sat", "toefl", "dna", "rna", "swot", "usb", "gps", "phd",
    "ceo", "tv", "cd", "dvd", "pdf", "ppt", "ai", "ml", "api", "url",
    "html", "css", "sql", "cpu", "gpu", "ram", "kg", "km", "cm", "mm",
    "hz", "uk", "usa", "us", "nyu", "mit", "it", "anti", "anti-", "antiwar",
    "anticorruption", "anti-corruption", "ohio", "rem",
}

# Only patterns that are unambiguously malformed English are errors.  Broader
# grammar heuristics belong in the warning report because they create false
# positives in fragmentary collocation lists.
SOURCE_DEFECTS = (
    ("scientist_team", re.compile(r"\bscientist\s+team\b", re.I)),
    ("very_indeed", re.compile(r"\bvery\s+indeed\b", re.I)),
    ("duplicated_researcher", re.compile(r"\bresearch\s+researcher\b", re.I)),
    (
        "archaeologist_past_fragment",
        re.compile(r"\b(?:archaeologist|archeologist)\s+(?:discovered|excavated)\b", re.I),
    ),
)

LANGUAGE_SPECIFIC_DEFECTS = {
    "ja": (
        ("duplicated_japanese_ending", re.compile(r"(?:するする|したした|しているしている)")),
        ("duplicated_japanese_word", re.compile(r"(?:社会社会|食品食品|結果結果|旋律の旋律|象徴的なな)")),
    ),
    "zh": (
        ("duplicated_chinese_word", re.compile(r"(?:教授教授|规定规定|记忆记忆|神学神学院)")),
    ),
    "id": (
        ("unlocalized_registrar_phrase", re.compile(r"\bkantor\s+registrar\b", re.I)),
        ("unlocalized_community_college", re.compile(r"\bcommunity\s+college(?:s)?\b", re.I)),
    ),
    "es": (
        ("untranslated_english_phrase", re.compile(
            r"\b(?:upon|unlike|regardless|contrary\s+to|historically|community\s+colleges?|"
            r"student\s+talent|longitudinal\s+study|solar\s+energy|residual\s+heat|one\s+ton|"
            r"food\s+waste|food\s+desperdicio|rejectar|resolve|temptar|prohibitirá)\b",
            re.I,
        )),
        ("known_unaccented_form", re.compile(
            r"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])(?:cafeteria|libreria|presentacion|conversacion|"
            r"reunion|pasantia|pasantias|tutorias|ano|mas|politicas|publicas|presion|"
            r"ingenieria|astronomia|linguistica|geologo|hidrogeno|recesion|inversion|"
            r"interes|codigo|generacion)(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])",
            re.I,
        )),
    ),
}
HEADWORD_SPELLING_VARIANTS = {
    "archeologist": "archaeologist",
    "archaeologist": "archeologist",
}


def norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip().casefold())


def segments(value: object) -> list[str]:
    """Return a conservative list for warnings only.

    Commas inside a translated phrase are not treated as deterministic errors;
    this split is used only to identify possible list-shape warnings.
    """
    return [part.strip() for part in re.split(r"[,、，;；]", str(value)) if part.strip()]


def latin_tokens(value: object) -> list[str]:
    return sorted({token.casefold() for token in LATIN_TOKEN.findall(str(value))})


def has_script(value: object, language: str) -> bool:
    return bool(re.search(SCRIPT_PATTERNS[language], str(value)))


def has_foreign_script(value: object, language: str) -> bool:
    return bool(FOREIGN_SCRIPT_PATTERNS[language].search(str(value)))


def inflected_forms(word: str) -> set[str]:
    """Generate only high-confidence English inflections for warnings."""
    target = word.strip().lower()
    if not target:
        return set()
    forms = {target, target + "s", target + "ed", target + "ing"}
    if target.endswith("e"):
        forms.update({target + "d", target[:-1] + "ing"})
    if target.endswith("y") and len(target) > 1 and target[-2] not in "aeiou":
        forms.update({target[:-1] + "ies", target[:-1] + "ied"})
    return forms


def headword_in_example(word: str, example: str) -> bool:
    return any(
        re.search(rf"(?<![a-z]){re.escape(form)}(?![a-z])", example.casefold())
        for form in inflected_forms(word)
    )


def headword_in_collocation(word: str, collocations: str) -> bool:
    """Match inflections and hyphen/space variants without over-reporting."""
    compact_word = re.sub(r"[^a-z]", "", word.casefold())
    compact_source = re.sub(r"[^a-z]", "", collocations.casefold())
    if compact_word and compact_word in compact_source:
        return True
    variant = HEADWORD_SPELLING_VARIANTS.get(word.casefold())
    if variant and re.sub(r"[^a-z]", "", variant) in compact_source:
        return True
    word_tokens = re.findall(r"[a-z]+", word.casefold())
    source_tokens = set(re.findall(r"[a-z]+", collocations.casefold()))
    if len(word_tokens) > 1 and all(token in source_tokens for token in word_tokens):
        return True
    return any(
        re.search(rf"(?<![a-z]){re.escape(form)}(?![a-z])", collocations.casefold())
        for form in inflected_forms(word)
    )


def add(bucket: dict[str, list[dict[str, Any]]], kind: str, **payload: Any) -> None:
    bucket[kind].append(payload)


def audit(vocabulary: list[dict[str, Any]], translations: dict[str, Any]) -> dict[str, Any]:
    errors: dict[str, list[dict[str, Any]]] = {
        "record": [],
        "field": [],
        "translation": [],
        "source": [],
    }
    warnings: dict[str, list[dict[str, Any]]] = {
        "latin_token": [],
        "headword_missing_from_collocation": [],
        "headword_missing_from_example": [],
        "list_shape": [],
    }

    seen_ids: set[int] = set()
    expected_keys = {f"builtin:{item.get('id')}" for item in vocabulary}
    actual_keys = set(translations)
    for key in sorted(expected_keys - actual_keys):
        add(errors, "record", issue="missing_translation_key", key=key)
    for key in sorted(actual_keys - expected_keys):
        add(errors, "record", issue="unexpected_translation_key", key=key)

    for item in vocabulary:
        item_id = item.get("id")
        key = f"builtin:{item_id}"
        if item_id in seen_ids:
            add(errors, "record", issue="duplicate_vocabulary_id", id=item_id)
        seen_ids.add(item_id)
        entry = translations.get(key)
        if not isinstance(entry, dict):
            add(errors, "record", issue="missing_translation_record", id=item_id)
            continue

        for language, field in MEANING_FIELDS.items():
            value = str(item.get(field, "")).strip()
            if not value:
                add(errors, "field", issue="empty_meaning", id=item_id, lang=language, field=field)
                continue
            if not has_script(value, language):
                add(
                    errors,
                    "field",
                    issue="meaning_missing_target_script",
                    id=item_id,
                    lang=language,
                    field=field,
                    value=value,
                )
            if has_foreign_script(value, language):
                add(
                    errors,
                    "field",
                    issue="foreign_script_in_meaning",
                    id=item_id,
                    lang=language,
                    value=value,
                )
        meaning_en = str(item.get("meaningEn", "")).strip()
        if not meaning_en:
            add(errors, "field", issue="empty_meaning_en", id=item_id)

        for field in ("example", "collocations"):
            source = str(item.get(field, "")).strip()
            obj = entry.get(field)
            if not isinstance(obj, dict):
                add(errors, "field", issue="missing_field_object", id=item_id, field=field)
                continue
            if str(obj.get("source", "")).strip() != source:
                add(
                    errors,
                    "translation",
                    issue="source_field_mismatch",
                    id=item_id,
                    field=field,
                    expected=source,
                    actual=str(obj.get("source", "")).strip(),
                )
            for language in ALL_LANGS:
                value = str(obj.get(language, "")).strip()
                if not value:
                    add(errors, "translation", issue="empty", id=item_id, field=field, lang=language)
                if language == "en" and value != source:
                    add(
                        errors,
                        "translation",
                        issue="english_source_mismatch",
                        id=item_id,
                        field=field,
                        expected=source,
                        actual=value,
                    )
            for language in LANGS:
                value = str(obj.get(language, "")).strip()
                if not value:
                    continue
                if not has_script(value, language):
                    add(
                        errors,
                        "translation",
                        issue="missing_target_script",
                        id=item_id,
                        field=field,
                        lang=language,
                        value=value,
                    )
                if has_foreign_script(value, language):
                    add(
                        errors,
                        "translation",
                        issue="incompatible_foreign_script",
                        id=item_id,
                        field=field,
                        lang=language,
                        value=value,
                    )
                for issue, pattern in LANGUAGE_SPECIFIC_DEFECTS.get(language, ()):
                    if pattern.search(value):
                        add(
                            errors,
                            "translation",
                            issue=issue,
                            id=item_id,
                            field=field,
                            lang=language,
                            value=value,
                        )
                if language == "vi" and not re.search(r"[ăâđêôơưĂÂĐÊÔƠƯà-ỹÀ-Ỹ]", value):
                    add(
                        errors,
                        "translation",
                        issue="missing_vietnamese_diacritic",
                        id=item_id,
                        field=field,
                        lang=language,
                        value=value,
                    )
                if language == "vi" and field == "example":
                    letters = re.findall(r"[A-Za-zÀ-ỹĐđ]", value)
                    diacritics = re.findall(r"[ăâđêôơưĂÂĐÊÔƠƯà-ỹÀ-Ỹ]", value)
                    # A normal Vietnamese sentence contains tone or vowel
                    # marks throughout.  A long sentence with only a tiny
                    # number of marked letters is a high-confidence
                    # transliteration artifact, while short technical terms
                    # remain outside this threshold.
                    if len(letters) >= 50 and diacritics and len(diacritics) / len(letters) < 0.10:
                        add(
                            errors,
                            "translation",
                            issue="low_vietnamese_diacritic_ratio",
                            id=item_id,
                            field=field,
                            lang=language,
                            value=value,
                        )
                if norm(value) == norm(source):
                    add(
                        errors,
                        "translation",
                        issue="exact_english_copy",
                        id=item_id,
                        field=field,
                        lang=language,
                        value=value,
                    )
                if language in NON_LATIN:
                    leaked = [token for token in latin_tokens(value) if token not in ALLOWED_LATIN]
                    if leaked:
                        add(
                            warnings,
                            "latin_token",
                            id=item_id,
                            field=field,
                            lang=language,
                            tokens=leaked,
                            value=value,
                        )

            if field == "collocations":
                for name, pattern in SOURCE_DEFECTS:
                    if pattern.search(source):
                        add(errors, "source", issue=name, id=item_id, word=item.get("word"), source=source)
                source_segments = segments(source)
                word = str(item.get("word", "")).strip().casefold()
                if word and source_segments and not headword_in_collocation(word, source):
                    add(
                        warnings,
                        "headword_missing_from_collocation",
                        id=item_id,
                        word=item.get("word"),
                        source=source,
                    )
                for language in LANGS:
                    value = str(obj.get(language, "")).strip()
                    # A target may naturally use a comma for alternatives or
                    # an explanatory phrase.  Only a target with fewer pieces
                    # is a high-confidence missing-translation candidate.
                    if value and len(segments(value)) < len(source_segments):
                        add(
                            warnings,
                            "list_shape",
                            id=item_id,
                            word=item.get("word"),
                            lang=language,
                            source_count=len(source_segments),
                            target_count=len(segments(value)),
                        )
            elif not headword_in_example(str(item.get("word", "")), source):
                add(
                    warnings,
                    "headword_missing_from_example",
                    id=item_id,
                    word=item.get("word"),
                    example=source,
                )

    return {
        "wordCount": len(vocabulary),
        "translationRecordCount": len(translations),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="JSONレポートの出力先")
    parser.add_argument("--fail-on", choices=("error", "none"), default="error")
    args = parser.parse_args()

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    report = audit(vocabulary, phrase_root.get("translations", {}))
    error_count = sum(len(values) for values in report["errors"].values())
    warning_count = sum(len(values) for values in report["warnings"].values())

    print(f"vocabulary words: {report['wordCount']}")
    print(f"translation records: {report['translationRecordCount']}")
    print(f"deterministic errors: {error_count}")
    for kind, values in report["errors"].items():
        if values:
            print(f"  error/{kind}: {len(values)}")
            for value in values[:5]:
                print(f"    - {value}")
    print(f"review warnings: {warning_count}")
    for kind, values in report["warnings"].items():
        if values:
            print(f"  warning/{kind}: {len(values)}")
            for value in values[:3]:
                print(f"    - {value}")

    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.json}")
    if error_count and args.fail_on == "error":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
