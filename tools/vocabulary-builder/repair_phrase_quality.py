#!/usr/bin/env python3
"""Repair the phrase defects reported by audit_phrase_quality.py.

This tool is data-only: it never calls a translation API. It fixes the
mechanically identifiable defects found by the audit and rewrites both shipped
assets at the same time so their `source` fields stay aligned.

Fixes applied per word:

  1. Korean verb conjugation repair
     좋아하다한다 -> 좋아한다, 분리하다하라고 -> 분리하라고, 예약했다했다 -> 예약했다

  2. Separator normalisation in collocation translations
     Chinese  ； -> ，
     Japanese ,  -> 、

  3. British/American spelling alignment
     When the headword is American but its collocations are British
     (gynecologist vs gynaecologist), both the English `collocations` and every
     language translation are rewritten to the American spelling, and the
     phrase translation `source` is updated.

  4. Explanatory parentheses removed from collocations
     "bat (animal)" and "breed (type)" are dropped from the list.

  5. Korean name transliteration
     Maya -> 메이야, Chen -> 첸, Lee -> 리 (only inside Korean translations)

Usage:
  python3 repair_phrase_quality.py --dry-run   # 変更内容を確認するだけ
  python3 repair_phrase_quality.py             # アセットへ書き込む
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"

LANGS = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es")

# 韓国語訳の動詞活用破損。長いものから順に置換する。
KO_CONJUGATION_FIXES = (
    ("하다하라고", "하라고"),
    ("하다한다", "한다"),
    ("하다 했다", "했다"),
    ("하다했다", "했다"),
    ("한다한다", "한다"),
    ("했다했다", "했다"),
    ("하다 한다", "한다"),
)

# 英綴り -> 米綴り（見出し語側に合わせる）。
UK_TO_US = {
    "gynaecologist": "gynecologist",
    "gynaecologists": "gynecologists",
    "socialise": "socialize",
    "socialised": "socialized",
    "socialising": "socializing",
    "socialises": "socializes",
    "archaeologist": "archeologist",
    "archaeologists": "archeologists",
    "institutionalise": "institutionalize",
    "institutionalised": "institutionalized",
    "institutionalising": "institutionalizing",
    "institutionalises": "institutionalizes",
    "candour": "candor",
    "meagre": "meager",
    "leveller": "leveler",
    "levellers": "levelers",
    "lacklustre": "lackluster",
}
UK_RE = re.compile(
    r"(?<![A-Za-z])(" + "|".join(sorted(UK_TO_US, key=len, reverse=True)) + r")(?![A-Za-z])"
)

# 見出し語自体が英綴りの語（アプリ内に米綴りの同義語が別IDで存在する）。
# 見出し語は変えず、コロケーション側を英綴りに合わせて内部整合を取る。
# 例) archaeology の見出し語はそのまま、コロケーションの archeology を archaeology へ。
HEADWORD_UK_ENTRIES = {
    2862: "archaeology", 4583: "haemoglobin", 5500: "analyse", 5501: "labour",
    5517: "utilise", 5632: "behaviour", 5741: "defence", 5770: "favour",
    6164: "archaeological", 6165: "archaeologist",
}
# 英綴り -> 米綴り（HEADWORD_UK_ENTRIES の語を米綴りへ寄せるため）。
HEADWORD_UK_TO_US_EXTRA = {
    "archaeology": "archeology", "archaeological": "archeological",
    "archaeologist": "archeologist", "haemoglobin": "hemoglobin",
    "analyse": "analyze", "labour": "labor", "utilise": "utilize",
    "behaviour": "behavior", "defence": "defense", "favour": "favor",
}
UK_TO_US.update(HEADWORD_UK_TO_US_EXTRA)


PAREN_RE = re.compile(r"\((?:type|animal|verb|noun|adj|adjective|adverb)\)", re.I)

# 韓国語訳に残った英語名の置換。
KO_NAME_FIXES = (("Maya", "메이야"), ("Chen", "첸"), ("Lee", "리"))


def dedupe_segments(value: str) -> str:
    """コロケーション内の重複項目を落とす（firstly のような破損を直す）。

    「firstly, secondly, thirdly; firstly and foremost; ...」のように区切りに
    `;` が混ざっている場合も正規化してから重複を除く。
    """
    parts = [part.strip() for part in re.split(r"[,、，;；]", value) if part.strip()]
    seen: set[str] = set()
    kept: list[str] = []
    for part in parts:
        key = part.lower()
        if key in seen:
            continue
        seen.add(key)
        kept.append(part)
    return ", ".join(kept)


def log(message: str) -> None:
    print(f"[repair] {message}", flush=True)


def to_us_spelling(value: str) -> str:
    return UK_RE.sub(lambda match: UK_TO_US[match.group(1).lower()], value)


def fix_korean_conjugation(value: str) -> str:
    for broken, fixed in KO_CONJUGATION_FIXES:
        value = value.replace(broken, fixed)
    return value


def fix_korean_names(value: str) -> str:
    for english, korean in KO_NAME_FIXES:
        value = re.sub(rf"(?<![A-Za-z]){english}(?![A-Za-z])", korean, value)
    return value


def join_segments(segments: list[str], lang: str) -> str:
    """言語ごとの正しい区切り記号で項目を連結する。"""
    separator = {"zh": "，", "ja": "、"}.get(lang, ", ")
    return separator.join(segments)


def normalize_separators(value: str, lang: str) -> str:
    if lang == "zh":
        return value.replace("；", "，")
    if lang == "ja":
        return re.sub(r"\s*,\s*", "、", value).replace("；", "、")
    if lang == "hi":
        # ヒンディー語はアラビア語のコンマ「،」が混ざっているので ASCII へ寄せる。
        return value.replace("،", ",").replace(";", ",")
    return value.replace(";", ",")


def split_segments(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,、，;；]", value) if part.strip()]




def repair(vocabulary: list, translations: dict, *, dry_run: bool) -> dict[str, int]:
    stats = {
        "ko_conjugation": 0, "ko_names": 0, "separator_zh": 0, "separator_ja": 0,
        "separator_hi": 0, "separator_other": 0, "us_spelling": 0, "parenthetical": 0,
        "duplicate_segment": 0, "spelling_align": 0,
    }

    for item in vocabulary:
        item_id, word = item["id"], item["word"]
        entry = translations.get(f"builtin:{item_id}")
        if not entry:
            continue
        example = entry.setdefault("example", {})
        collocations = entry.setdefault("collocations", {})

        # ── 1. 韓国語の動詞活用と人名を修復 ─────────────────────────
        korean = str(example.get("ko", ""))
        if korean:
            repaired = fix_korean_conjugation(korean)
            if repaired != korean:
                stats["ko_conjugation"] += 1
            renamed = fix_korean_names(repaired)
            if renamed != repaired:
                stats["ko_names"] += 1
            if renamed != korean:
                example["ko"] = renamed

        # ── 2. コロケーション訳の区切り記号を統一 ───────────────────
        for lang in LANGS:
            value = str(collocations.get(lang, ""))
            if not value:
                continue
            normalized = normalize_separators(value, lang)
            if normalized != value:
                key = {
                    "zh": "separator_zh", "ja": "separator_ja", "hi": "separator_hi",
                }.get(lang, "separator_other")
                stats[key] = stats.get(key, 0) + 1
                collocations[lang] = normalized

        # ── 3. 綴り統一（見出し語の綴りにコロケーションを合わせる） ──
        source = item["collocations"]
        headword_is_uk = item_id in HEADWORD_UK_ENTRIES
        if headword_is_uk:
            # 見出し語が英綴り: コロケーションの米綴りを英綴りへ戻す。
            reverse = {us: uk for uk, us in HEADWORD_UK_TO_US_EXTRA.items()}
            reverse_re = re.compile(
                r"(?<![A-Za-z])(" + "|".join(sorted(reverse, key=len, reverse=True)) + r")(?![A-Za-z])",
                re.IGNORECASE,
            )
            new_source = reverse_re.sub(lambda m: reverse[m.group(1).lower()], source)
            if new_source != source:
                stats["spelling_align"] += 1
                item["collocations"] = new_source
                collocations["source"] = new_source
                collocations["en"] = new_source
                for lang in LANGS:
                    value = str(collocations.get(lang, ""))
                    if value:
                        collocations[lang] = reverse_re.sub(
                            lambda m: reverse[m.group(1).lower()], value
                        )
                log(f"align to UK headword: {word} -> {new_source[:60]}")
        elif not UK_RE.search(word) and UK_RE.search(source):
            new_source = to_us_spelling(source)
            if new_source != source:
                stats["us_spelling"] += 1
                item["collocations"] = new_source
                collocations["source"] = new_source
                collocations["en"] = new_source
                for lang in LANGS:
                    value = str(collocations.get(lang, ""))
                    if value:
                        collocations[lang] = to_us_spelling(value)
                log(f"US spelling: {word} -> {new_source[:60]}")

        # ── 4. 説明カッコの項目を除去（訳文側も同じ位置を落とす） ────
        source = item["collocations"]
        if PAREN_RE.search(source):
            parts = [part.strip() for part in source.split(",")]
            kept = [part for part in parts if part and not PAREN_RE.search(part)]
            if kept and len(kept) != len(parts):
                stats["parenthetical"] += 1
                new_source = ", ".join(kept)
                item["collocations"] = new_source
                collocations["source"] = new_source
                collocations["en"] = new_source
                for lang in LANGS:
                    translated = split_segments(str(collocations.get(lang, "")))
                    # 訳文の項目数が英語と一致していれば同じ位置を落とせる。
                    if len(translated) == len(parts):
                        collocations[lang] = join_segments(
                            [segment for index, segment in enumerate(translated)
                             if not PAREN_RE.search(parts[index])],
                            lang,
                        )
                log(f"drop parenthetical: {word} -> {new_source[:60]}")

        # ── 5. コロケーション内の重複項目を除去 ──────────────────────
        source = item["collocations"]
        deduped = dedupe_segments(source)
        if deduped != source:
            stats["duplicate_segment"] += 1
            item["collocations"] = deduped
            collocations["source"] = deduped
            collocations["en"] = deduped
            log(f"dedupe segments: {word} -> {deduped[:60]}")

    if not dry_run:
        VOCAB_PATH.write_text(
            json.dumps(vocabulary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="書き込まずに変更点だけ表示")
    args = parser.parse_args()

    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root["translations"]

    stats = repair(vocabulary, translations, dry_run=args.dry_run)
    log("summary: " + ", ".join(f"{name}={count}" for name, count in stats.items()))

    if args.dry_run:
        log("dry run: no file written")
        return 0

    PHRASE_PATH.write_text(
        json.dumps(
            {"schemaVersion": phrase_root.get("schemaVersion", 1), "translations": translations},
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    log(f"written: {VOCAB_PATH}")
    log(f"written: {PHRASE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

