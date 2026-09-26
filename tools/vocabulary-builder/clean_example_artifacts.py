"""Clean up mechanical-substitution artifacts left in the example translations.

Replacing leaked English words one at a time can leave a target-language sentence
with a duplicate or misplaced word, because the model had already translated part
of the phrase:

  - Japanese:  "朝の授業まで walk する" -> "朝の授業まで 歩く する"   (verb + する)
  - Spanish:   "I think que ..."        -> "I creo que ..."          (leftover "I")

This tool scans for the known artifact patterns and repairs them.

Usage:
  python3 clean_example_artifacts.py --check
  python3 clean_example_artifacts.py
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"

# 日本語: 「歩く する」「見る する」のような動詞＋する の重複を整える。
JA_VERB_SURU = re.compile(r"([\u4e00-\u9fff\u3040-\u309f]{1,4}く)\s+する")
# 日本語: 助詞と動詞の間に半角スペースが残っている場合を詰める。
JA_SPACE_AROUND_VERB = re.compile(r"([\u3040-\u309f])\s+([\u4e00-\u9fff\u3040-\u309f]{1,4}く)\s")
# 日本語・韓国語: 置換で入った語の前後に残った半角スペースを詰める。
# 日本語は語間に空白を置かず、韓国語の助詞は直前の語に続けて書く。
JA_STRAY_SPACE = re.compile(r"(?<=[\u3040-\u30ff\u4e00-\u9fff])\s+(?=[\u3040-\u30ff\u4e00-\u9fff])")
JA_STRAY_SPACE_AFTER = re.compile(r"(?<=[\u3040-\u30ff\u4e00-\u9fff])\s+(?=[、。])")
KO_STRAY_SPACE = re.compile(r"\s+(?=[\uac00-\ud7af]*[은는이가을를의에])")
# スペイン語: 文頭・文中に残った英語の主語 "I" を除去する。
ES_LEFTOVER_I = re.compile(r"(?<![A-Za-z])I\s+(?=[a-záéíóúñ])")
# ベトナム語・インドネシア語: 残った英語の冠詞・主語を除去する。
LATIN_LEFTOVER = re.compile(r"(?<![A-Za-z])(?:I|you|we|they)\s+(?=[a-zà-ỹ])")


def clean(language: str, value: str) -> str:
    fixed = value
    if language == "ja":
        fixed = JA_VERB_SURU.sub(r"\1", fixed)
        fixed = JA_SPACE_AROUND_VERB.sub(r"\1\2", fixed)
        fixed = JA_STRAY_SPACE.sub("", fixed)
        fixed = JA_STRAY_SPACE_AFTER.sub("", fixed)
        fixed = re.sub(r"\s+([、。])", r"\1", fixed)
    elif language == "ko":
        fixed = KO_STRAY_SPACE.sub("", fixed)
    elif language == "es":
        fixed = ES_LEFTOVER_I.sub("", fixed)
    elif language in ("vi", "id"):
        fixed = LATIN_LEFTOVER.sub("", fixed)
    return re.sub(r"\s{2,}", " ", fixed).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="機械置換の痕跡を整える")
    parser.add_argument("--check", action="store_true", help="書き込まずに確認")
    args = parser.parse_args()

    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root["translations"]

    changed = 0
    for item in vocabulary:
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            continue
        for language in ("ja", "es", "vi", "id"):
            value = str(record.get(language, ""))
            if not value:
                continue
            fixed = clean(language, value)
            if fixed != value:
                record[language] = fixed
                changed += 1
                print(f"{item['word']} [{language}]: {value[:70]} -> {fixed[:70]}")

    print(f"changed: {changed}")
    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {PHRASES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
