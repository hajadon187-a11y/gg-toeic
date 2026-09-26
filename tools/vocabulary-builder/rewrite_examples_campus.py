#!/usr/bin/env python3
"""Rewrite every vocabulary example sentence into an American university context.

The Android app ships sentences that were written for general, economic, or
environmental topics. This build-time tool regenerates all of them so that the
context is "an American college lecture, textbook, or a conversation between a
professor and a student", and regenerates the translations of those sentences to
match.

Targets:
  - app/src/main/assets/vocabulary.json                     -> `example`
  - app/src/main/assets/vocabulary_phrase_translations.json -> `builtin:{id}.example`
    (the `source` field is rewritten at the same time so the shipped audit keeps
     passing)

`collocations` and every other field stay untouched. Results are cached per word
under /private/tmp so an interrupted run resumes instead of repeating work.

Usage:
  python3 rewrite_examples_campus.py --dry-run           # 対象件数だけ確認
  python3 rewrite_examples_campus.py --limit 48          # 疎通確認（先頭48語）
  python3 rewrite_examples_campus.py                     # 全6,384語を書き換え
  python3 rewrite_examples_campus.py --ids 1,2,3         # 語彙IDを指定
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent.parent
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
CACHE = Path("/private/tmp/toefl-campus-examples-cache.json")

BATCH_SIZE = 24
WORKERS = 16
EXAMPLE_MAX_WORDS = 32
CACHE_SCHEMA = 1

# Languages shipped for example translations. `en` repeats the example itself so
# the JSON keeps the same ten keys the app and the audit already expect.
PHRASE_LANGUAGES: dict[str, tuple[str, str]] = {
    "ja": ("Japanese", r"[ぁ-ゟァ-ヿ一-鿿]"),
    "zh": ("Simplified Chinese", r"[一-鿿]"),
    "hi": ("Hindi", r"[ऀ-ॿ]"),
    "vi": ("Vietnamese", r"[A-Za-zÀ-ỹ]"),
    "ko": ("Korean", r"[가-힣]"),
    "id": ("Indonesian", r"[A-Za-zÀ-ỹ]"),
    "th": ("Thai", r"[ก-๛]"),
    "es": ("Spanish", r"[A-Za-zÀ-ỹÁÉÍÓÚÜÑáéíóúüñ]"),
}
TRANSLATION_FIELDS = ["ja", "zh", "hi", "vi", "ko", "id", "th", "es", "en"]

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_LATIN_LETTER = re.compile(r"[A-Za-z]")
_DEAD_PHRASES = re.compile(
    r"\b(?:in conclusion|in summary|overall|as we have seen|this essay|"
    r"this paper will|in this paper|in this essay|let us now|we will discuss)\b",
    re.IGNORECASE,
)

LEVEL_CONTEXT = {
    1: (
        "CEFR A2-B1 everyday campus English: a short chat between a student and a "
        "roommate, classmate, or adviser. 8-16 words, one clause, concrete vocabulary"
    ),
    2: (
        "CEFR B1-B2 campus-life English: registration, the library, the dorm, the "
        "cafeteria, an internship, or a first-year survey course. 10-20 words"
    ),
    3: (
        "CEFR B2-C1 undergraduate lecture or textbook English: the professor explains "
        "a concept in a 100-level or 200-level class. 12-24 words"
    ),
    4: (
        "CEFR C1-C2 advanced lecture, research-seminar, or academic-writing English: "
        "the professor presents evidence, method, or theory. 14-28 words"
    ),
}


def log(message: str) -> None:
    print(f"[rewrite-examples] {time.strftime('%H:%M:%S')} | {message}", flush=True)


# ─── プロバイダ ────────────────────────────────────────────────────
class Provider:
    """DeepSeek（OpenAI互換）を urllib で呼び出す薄いクライアント。"""

    def __init__(self) -> None:
        load_dotenv(BASE_DIR / ".env")
        candidates = [
            (
                "LUNA",
                os.getenv("LUNA_API_KEY"),
                os.getenv("LUNA_BASE_URL"),
                os.getenv("LUNA_MODEL"),
            ),
            (
                "DEEPSEEK",
                os.getenv("DEEPSEEK_API_KEY"),
                os.getenv("DEEPSEEK_BASE_URL"),
                os.getenv("DEEPSEEK_MODEL"),
            ),
        ]
        for name, key, base, model in candidates:
            if key and base and model and not key.startswith("sk-xxxx"):
                self.name, self.key = name, key
                self.base = base.rstrip("/")
                self.model = model
                log(f"プロバイダ: {name} ({self.model})")
                return
        raise SystemExit(
            "利用可能なAPIキーが .env にありません（LUNA_API_KEY / DEEPSEEK_API_KEY）"
        )

    def json_call(self, prompt: str, max_tokens: int = 8000, attempts: int = 4) -> Any:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        if self.name == "DEEPSEEK":
            # deepseek-chat は temperature と max_tokens をそのまま受け付ける
            body["temperature"] = 0.7
            body["max_tokens"] = max_tokens
        else:
            # 推論系モデルは max_tokens ではなく max_completion_tokens を使い、
            # temperature も既定値以外を受け付けないため送信しない
            body["max_completion_tokens"] = max_tokens
        last_error = ""
        for attempt in range(attempts):
            try:
                request = urllib.request.Request(
                    f"{self.base}/chat/completions",
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"},
                )
                with urllib.request.urlopen(request, timeout=300) as response:
                    payload = json.load(response)
                content = payload["choices"][0]["message"]["content"] or ""
                return parse_json_object(content)
            except urllib.error.HTTPError as error:
                detail = error.read()[:200]
                last_error = f"HTTP {error.code}: {detail!r}"
                if error.code in (400, 401, 402, 403):
                    raise RuntimeError(f"API呼び出しに失敗しました: {last_error}") from error
            except Exception as error:  # noqa: BLE001 - リトライのため全例外を捕捉
                last_error = f"{type(error).__name__}: {error}"
            time.sleep(2 + attempt * 3)
        raise RuntimeError(f"API呼び出しに失敗しました: {last_error}")


def parse_json_object(content: str) -> Any:
    """LLMの応答からJSONを寛容に抽出する（コードフェンス・前後ノイズに対応）。"""
    cleaned = _CONTROL_CHARS.sub("", content)
    cleaned = re.sub(r"```(?:json)?", "", cleaned, flags=re.IGNORECASE).replace("```", "").strip()
    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = cleaned.find(opener), cleaned.rfind(closer)
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"JSONを抽出できませんでした: {content[:200]}")


# ─── プロンプト ────────────────────────────────────────────────────
def batch_prompt(batch: list[dict[str, Any]]) -> str:
    lines = "\n".join(
        f'{item["id"]}\tword="{item["word"]}"\tlevel={item["level"]}'
        f'\ttopic={item.get("topic", "")}\tcurrent_sentence="{item.get("example", "")}"'
        for item in batch
    )
    level_notes = "\n".join(f"- L{level}: {note}" for level, note in sorted(LEVEL_CONTEXT.items()))
    return f"""You are a lexicographer writing example sentences for an American TOEFL vocabulary app.

Rewrite the example sentence of every word below so that its context is an American
university: a lecture given by a professor, a course textbook, or a conversation between
a professor and a student on a US campus.

Level guidance (keep each sentence at the difficulty of its own level):
{level_notes}

Hard rules:
- Write American English only (spelling and campus terms such as "semester", "freshman",
  "the registrar's office", "office hours", "midterm", "syllabus").
- The sentence must contain the target word exactly as written, unchanged, and must
  clearly show that word's meaning.
- Use only printable ASCII characters: no curly quotes, no em dashes, no accents.
- One or two sentences, no semicolon chains, no list of three or more items.
- Vary the subject and the discipline across the batch (astronomy, geology, psychology,
  biology, history, economics, linguistics, art history, engineering, and so on) instead
  of repeating one frame.
- Never reuse the current sentence and never just add "in class" to it.
- Never start with a discourse marker such as "In conclusion", "In summary", or
  "Overall". No citations and no quotation marks around the whole sentence.
- Function words (articles, prepositions, pronouns, auxiliary verbs, conjunctions) cannot
  carry an academic topic on their own: for those words write a natural sentence whose
  setting is still a US campus.

Translations:
- Translate each finished sentence into all nine languages below. Every translation must
  read naturally to an educated native speaker of that language, must keep the subject,
  tense, and logic of the English sentence, and must be written only in that language.
- Names of people and places may be transliterated or kept in Latin script.

Languages:
- ja: Japanese (plain style, no explanatory parentheses)
- zh: Simplified Chinese
- hi: Hindi
- vi: Vietnamese
- ko: Korean
- id: Indonesian
- th: Thai
- es: Spanish
- en: repeat the final English sentence exactly

Words (tab separated: id, word, level, topic, current_sentence):
{lines}

Return ONLY a valid JSON object with this exact shape, using the numeric id as the key:
{{"<id>": {{"example": "final English sentence", "ja": "...", "zh": "...", "hi": "...",
 "vi": "...", "ko": "...", "id": "...", "th": "...", "es": "...", "en": "..."}}}}

Do not omit any id. Do not add explanations, comments, markdown fences, or extra keys.
"""


def repair_prompt(batch: list[dict[str, Any]], problems: str) -> str:
    base = batch_prompt(batch)
    return (
        "Your previous answer had these problems:\n"
        f"{problems}\n"
        "Answer again, fixing every problem, and keep the required JSON shape.\n\n" + base
    )


# ─── 検証 ──────────────────────────────────────────────────────────
def has_script(value: Any, pattern: str) -> bool:
    return isinstance(value, str) and bool(re.search(pattern, value))


def word_is_present(word: str, sentence: str) -> bool:
    """例文に原形または一般的な変化形が含まれているかを確認する。"""
    target = word.strip().lower()
    if not target:
        return False
    if re.search(rf"\b{re.escape(target)}\b", sentence):
        return True
    stems = {target}
    for suffix, replacements in (
        ("ies", ["y", "ie"]),
        ("es", ["e", ""]),
        ("s", [""]),
        ("ied", ["y"]),
        ("ed", ["e", ""]),
        ("ing", ["e", ""]),
        ("er", ["e", ""]),
        ("est", ["e", ""]),
        ("ly", [""]),
        ("ment", [""]),
        ("ness", [""]),
        ("tion", ["te", "t"]),
        ("sion", ["se", "d"]),
    ):
        if target.endswith(suffix) and len(target) - len(suffix) >= 3:
            for replacement in replacements:
                stems.add(target[: -len(suffix)] + replacement)
    # 語尾変化で語幹が変わる語（describe/description など）は前方一致で許容する。
    stems.add(target[: max(4, len(target) - 3)])
    for stem in stems:
        if len(stem) < 3:
            continue
        if re.search(rf"\b{re.escape(stem)}\w{{0,6}}\b", sentence):
            return True
    return False


def untranslated_word(word: str, value: str) -> bool:
    """訳文に英語のままの見出し語が残っていないかを確認する。

    固有名詞や学術記号は許容し、日本語話者に不自然なカタカナ語の混入だけを弾く。
    大文字・小文字は区別し、日本語・韓国語・中国語・タイ語でも同じ判定を使う。
    """
    target = word.strip()
    if len(target) < 3:
        return False
    return bool(re.search(rf"(?<![A-Za-z]){re.escape(target)}(?![A-Za-z])", value))


def validate(
    item: dict[str, Any], entry: dict[str, Any], allow_current: bool = False
) -> tuple[dict[str, str] | None, str]:
    """生成結果を検査し、問題があれば理由を返す。

    `allow_current` が真のときは既存と同一の例文を許容する。キャッシュから復元した
    既存データを再検査するときに使う。
    """
    word = item["word"]
    example = str(entry.get("example", "")).strip()
    if not example:
        return None, f"{word}: example が空です"
    if not _LATIN_LETTER.search(example):
        return None, f"{word}: example が英語ではありません"
    if not example.isascii():
        return None, f"{word}: example に非ASCII文字が含まれています: {example[:60]}"
    word_count = len(example.split())
    if word_count < 6 or word_count > EXAMPLE_MAX_WORDS:
        return None, f"{word}: example の語数が不適切です ({word_count} words)"
    if not word_is_present(word, example.lower()):
        return None, f"{word}: example に単語が含まれていません: {example[:80]}"
    if not allow_current and example.casefold() == str(item.get("example", "")).strip().casefold():
        return None, f"{word}: example が既存文と同じです"
    if _DEAD_PHRASES.search(example):
        return None, f"{word}: example に使えない定型表現があります: {example[:60]}"

    result: dict[str, str] = {"example": example}
    for language, (name, pattern) in PHRASE_LANGUAGES.items():
        value = str(entry.get(language, "")).strip()
        if not value:
            return None, f"{word}: {language} 訳が空です"
        if not has_script(value, pattern):
            return None, f"{word}: {language} 訳が {name} ではありません: {value[:60]}"
        if language != "en" and value.casefold() == example.casefold():
            return None, f"{word}: {language} 訳が英語のまま返されました"
        if language != "en" and untranslated_word(word, value):
            return None, f"{word}: {language} 訳に見出し語が英語のまま残っています: {value[:60]}"
        result[language] = value
    result["en"] = example
    return result, ""


# ─── 生成 ──────────────────────────────────────────────────────────
def fetch_entry(provider: Provider, item: dict[str, Any]) -> dict[str, str]:
    """1語分の例文と9言語訳を取得する（検証に落ちたら理由を添えて再試行）。"""
    problems: list[str] = []
    for attempt in range(4):
        prompt = batch_prompt([item]) if not problems else repair_prompt([item], "\n".join(problems))
        try:
            payload = provider.json_call(prompt)
        except Exception as error:  # noqa: BLE001 - API 失敗もリトライ対象
            problems = [f"API error: {type(error).__name__}: {error}"]
            time.sleep(2 + attempt * 3)
            continue
        if not isinstance(payload, dict):
            problems = ["JSONオブジェクトではありません"]
            continue
        entry = payload.get(str(item["id"])) or payload.get(item["id"])
        if not isinstance(entry, dict) and len(payload) == 1:
            only = next(iter(payload.values()))
            entry = only if isinstance(only, dict) else None
        if not isinstance(entry, dict):
            problems = ["id に対応するオブジェクトがありません"]
            continue
        cleaned = {k: (v if isinstance(v, str) else str(v)) for k, v in entry.items()}
        result, problem = validate(item, cleaned)
        if result:
            return result
        problems = [problem]
    raise RuntimeError(f"{item['word']}: 生成に失敗しました ({problems[:1]})")


def fetch_batch(provider: Provider, batch: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """1バッチ分をまとめて生成し、検証を通らない語だけ個別に作り直す。"""
    payload = provider.json_call(batch_prompt(batch))
    if not isinstance(payload, dict):
        raise ValueError("JSONオブジェクトではありません")

    results: dict[str, dict[str, str]] = {}
    retry: list[dict[str, Any]] = []
    for item in batch:
        entry = payload.get(str(item["id"])) or payload.get(item["id"])
        if not isinstance(entry, dict):
            retry.append(item)
            continue
        cleaned = {k: (v if isinstance(v, str) else str(v)) for k, v in entry.items()}
        result, _problem = validate(item, cleaned)
        if result:
            results[str(item["id"])] = result
        else:
            retry.append(item)

    for item in retry:
        results[str(item["id"])] = fetch_entry(provider, item)
    return results


def load_cache() -> dict[str, dict[str, str]]:
    if not CACHE.exists():
        return {}
    try:
        raw = json.loads(CACHE.read_text("utf-8"))
    except json.JSONDecodeError:
        log("キャッシュが壊れているため無視します")
        return {}
    entries = raw.get("entries", raw) if isinstance(raw, dict) else {}
    return {str(k): v for k, v in entries.items() if isinstance(v, dict) and v.get("example")}


def save_cache(cache: dict[str, dict[str, str]]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schemaVersion": CACHE_SCHEMA, "entries": cache}
    temporary = CACHE.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    temporary.replace(CACHE)


# ─── 語彙・訳の更新 ────────────────────────────────────────────────
def write_assets(
    vocabulary: list[dict[str, Any]],
    cache: dict[str, dict[str, str]],
) -> tuple[int, int]:
    translations = json.loads(PHRASES.read_text("utf-8"))
    dictionary: dict[str, Any] = translations.setdefault("translations", {})

    vocabulary_updated = 0
    phrase_updated = 0
    for item in vocabulary:
        result = cache.get(str(item["id"]))
        if not result:
            continue
        example = result["example"]
        if item.get("example") != example:
            item["example"] = example
            vocabulary_updated += 1
        key = f"builtin:{item['id']}"
        entry = dictionary.get(key)
        if not isinstance(entry, dict):
            entry = {}
            dictionary[key] = entry
        collocations = entry.get("collocations")
        if not isinstance(collocations, dict) or not str(collocations.get("ja", "")).strip():
            log(f"  警告: {item['word']} の collocations 訳が欠けています")
        example_entry: dict[str, str] = {"source": example}
        for field in TRANSLATION_FIELDS:
            example_entry[field] = result[field]
        entry["example"] = example_entry
        phrase_updated += 1

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations, ensure_ascii=False, indent=1), encoding="utf-8")
    return vocabulary_updated, phrase_updated


def main() -> int:
    parser = argparse.ArgumentParser(description="例文をアメリカの大学文脈へ書き換える")
    parser.add_argument("--limit", type=int, default=0, help="デバッグ用: 先頭N語だけ処理")
    parser.add_argument("--ids", default="", help="カンマ区切りの語彙IDのみ処理")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="1回のAPI呼び出しの語数")
    parser.add_argument("--workers", type=int, default=WORKERS, help="並列数")
    parser.add_argument("--dry-run", action="store_true", help="対象件数の確認のみ")
    parser.add_argument("--no-write", action="store_true", help="生成のみでJSONは更新しない")
    parser.add_argument(
        "--revalidate",
        action="store_true",
        help="キャッシュ済みの語を再検査し、通らない語だけ生成し直す",
    )
    args = parser.parse_args()

    vocabulary: list[dict[str, Any]] = json.loads(VOCABULARY.read_text("utf-8"))
    cache = load_cache()

    invalid: dict[str, str] = {}
    for item in vocabulary:
        entry = cache.get(str(item["id"]))
        if not entry:
            continue
        # 復元した既存データを対象にするため、既存と同一の例文は許容して検査する。
        _result, problem = validate(item, entry, allow_current=True)
        if problem:
            invalid[str(item["id"])] = problem

    if args.revalidate and not args.dry_run:
        # 検査に通らない語だけをキャッシュから外して作り直す。
        for item_id, problem in invalid.items():
            log(f"  再生成: {problem}")
            cache.pop(item_id, None)
        save_cache(cache)
    if args.revalidate:
        log(f"再検査で {len(invalid)} 語が対象になりました")

    targets = [
        item
        for item in vocabulary
        if not (args.revalidate and str(item["id"]) not in invalid) and str(item["id"]) not in cache
    ]
    if args.ids:
        wanted = {value.strip() for value in args.ids.split(",") if value.strip()}
        targets = [item for item in vocabulary if str(item["id"]) in wanted]
    elif args.limit:
        targets = targets[: args.limit]

    log(f"語彙 {len(vocabulary)} 語 / キャッシュ {len(cache)} 語 / 今回の対象 {len(targets)} 語")
    if args.dry_run:
        # 確認のみ。ここでキャッシュを書き換えると、以降の実行で作り直しが必要になる。
        for problem in list(invalid.values())[:40]:
            log(f"  要再生成: {problem}")
        if len(invalid) > 40:
            log(f"  ...ほか {len(invalid) - 40} 語")
        return 0
    if not targets:
        log("未処理の語はありません。JSON更新へ進みます")

    provider = Provider()
    # word でソートして同じ語尾の語を同一バッチへ集め、実行順に依存しない結果にする。
    ordered = sorted(targets, key=lambda item: item["word"].lower())
    batches = [ordered[i : i + args.batch_size] for i in range(0, len(ordered), args.batch_size)]
    log(f"バッチ数: {len(batches)} (batch_size={args.batch_size}, workers={args.workers})")

    lock = threading.Lock()
    failures: list[str] = []
    completed = 0

    def run(batch: list[dict[str, Any]]) -> None:
        nonlocal completed
        try:
            produced = fetch_batch(provider, batch)
        except Exception as error:  # noqa: BLE001 - 1バッチの失敗で全体を止めない
            log(f"  バッチ失敗（{batch[0]['word']}〜{batch[-1]['word']}）: {type(error).__name__}: {error}")
            produced = {}
            for item in batch:
                try:
                    produced[str(item["id"])] = fetch_entry(provider, item)
                except Exception as inner:  # noqa: BLE001
                    with lock:
                        failures.append(f"{item['word']}: {type(inner).__name__}: {inner}")
                    log(f"  失敗: {item['word']}: {type(inner).__name__}: {inner}")
        with lock:
            cache.update(produced)
            completed += len(produced)
            save_cache(cache)
        log(f"  バッチ完了: {len(produced)}/{len(batch)} 語（累計 {len(cache)}）")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        list(executor.map(run, batches))

    log(f"生成完了: 累計 {len(cache)} 語 / 今回 {completed} 語 / 失敗 {len(failures)} 件")

    if args.no_write:
        log("--no-write のためJSONは更新していません")
        return 1 if failures else 0

    vocabulary_updated, phrase_updated = write_assets(vocabulary, cache)
    log(f"vocabulary.json の example を {vocabulary_updated} 件更新")
    log(f"phrase translations の example を {phrase_updated} 件更新")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
