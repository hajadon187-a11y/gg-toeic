"""Apply the cached example-translation lexicon to the shipped assets.

`translate_example_gaps.py` builds the lexicon (language -> English word ->
translation) but also re-runs the API phase every time it starts. Once the
lexicon is complete, this tool writes it into the assets without any API call:

  - For every example translation, English words that leaked from the source
    sentence are replaced with the target-language equivalents.
  - The English `example` sentence, every `collocations` record, and all other
    words stay as they are.

Usage:
  python3 apply_example_gap_fixes.py --check   # 置換件数だけ確認
  python3 apply_example_gap_fixes.py           # assets を更新
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-example-gap-words.json")


def load_module():
    spec = importlib.util.spec_from_file_location(
        "translate_example_gaps", BASE_DIR / "translate_example_gaps.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="例文訳の英単語残りをキャッシュから修正する")
    parser.add_argument("--check", action="store_true", help="書き込まずに件数だけ確認")
    args = parser.parse_args()

    module = load_module()
    lexicon = json.loads(CACHE.read_text("utf-8"))
    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root["translations"]

    replaced, remaining = module.apply_replacements(vocabulary, translations, lexicon)
    print(f"replacements applied: {replaced} / sentences still containing English: {remaining}")

    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {PHRASES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
