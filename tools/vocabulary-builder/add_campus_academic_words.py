#!/usr/bin/env python3
"""キャンパスライフ・講義トピックの追加語にフルデータを与えてアプリの語彙JSONへ投入する。

対象語は `data/toefl_campus_academic_selection.json`（`select_campus_academic_words.py`
の出力で、既存語彙と重複しない語のみを含む）。

各語に対して以下を生成する。
  - wordUk / phoneticUk   : 比較用のイギリス英語表記と発音記号
  - meaning               : 日本語訳（TOEFLの大学・学術文脈）
  - meaningEn             : 英語定義
  - synonyms              : 類義語（米国英語優先）
  - collocations          : TOEFL講義・キャンパス会話で使えるコロケーション
  - example               : TOEFL講義・キャンパス会話の例文
  - meaningZh/Hi/Vi/Ko/Id/Es/Th : 多言語の意味

その後、`vocabulary_phrase_translations.json` に example / collocations の
9言語訳（ja/zh/hi/vi/ko/id/es/en）を書き込む。

使い方:
  python3 add_campus_academic_words.py --stage content   # 語彙本体を生成
  python3 add_campus_academic_words.py --stage phrase    # 例文・コロケーション訳を生成
  python3 add_campus_academic_words.py --all             # 両方
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
SELECTION = BASE_DIR / "data" / "toefl_campus_academic_selection.json"
VOCABULARY = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary.json"
PHRASES = REPO_DIR / "app" / "src" / "main" / "assets" / "vocabulary_phrase_translations.json"
CACHE_DIR = Path("/private/tmp/toefl-campus-academic")

SOURCE_LIST = "TOEFL-curated"
CONTENT_BATCH = 18
PHRASE_BATCH = 24
WORKERS = 4

MEANING_LANGUAGES = {
    "meaningZh": "Simplified Chinese",
    "meaningHi": "Hindi",
    "meaningVi": "Vietnamese",
    "meaningKo": "Korean",
    "meaningId": "Indonesian",
    "meaningEs": "Spanish",
    "meaningTh": "Thai",
}
PHRASE_LANGUAGES = {
    "ja": ("Japanese", r"[ぁ-ゟァ-ヿ一-鿿]"),
    "zh": ("Simplified Chinese", r"[一-鿿]"),
    "hi": ("Hindi", r"[ऀ-ॿ]"),
    "vi": ("Vietnamese", r"[A-Za-zÀ-ỹ]"),
    "ko": ("Korean", r"[가-힣]"),
    "id": ("Indonesian", r"[A-Za-zÀ-ỹ]"),
    "th": ("Thai", r"[ก-๛]"),
    "es": ("Spanish", r"[A-Za-zÀ-ỹÁÉÍÓÚÜÑáéíóúüñ]"),
}

# ロックを取らずに同じ語彙を扱うため、Windows系の改行/制御文字を落とすためのパターン
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def log(message: str) -> None:
    print(f"[add-campus] {time.strftime('%H:%M:%S')} | {message}", flush=True)


# ─── プロバイダ ────────────────────────────────────────────────────
class Provider:
    """LUNA（OpenAI互換）を優先し、無ければDeepSeekを使う薄いクライアント。

    本リポジトリのビルドツールは `openai` SDK を使ってきたが、`.env` の
    LUNA_BASE_URL は OpenAI 公式のエンドポイントを指すため、依存を増やさず
    urllib + OpenAI互換JSONで呼び出す。
    """

    def __init__(self) -> None:
        load_dotenv(BASE_DIR / ".env")
        candidates = [
            ("LUNA", os.getenv("LUNA_API_KEY"), os.getenv("LUNA_BASE_URL"), os.getenv("LUNA_MODEL")),
            ("DEEPSEEK", os.getenv("DEEPSEEK_API_KEY"), os.getenv("DEEPSEEK_BASE_URL"), os.getenv("DEEPSEEK_MODEL")),
        ]
        for name, key, base, model in candidates:
            if key and base and model and not key.startswith("sk-xxxx"):
                self.name, self.key = name, key
                self.base = base.rstrip("/")
                self.model = model
                log(f"プロバイダ: {name} ({self.model})")
                return
        raise SystemExit("利用可能なAPIキーが .env にありません（LUNA_API_KEY / DEEPSEEK_API_KEY）")

    def json_call(self, prompt: str, max_tokens: int = 16000, attempts: int = 4) -> Any:
        """JSONのみを返すよう指示したプロンプトを送り、パース済みの値を返す。"""
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            # 新しい推論系モデルは max_tokens ではなく max_completion_tokens を使い、
            # temperature も既定値(1)以外を受け付けないため送信しない。
            "max_completion_tokens": max_tokens,
        }
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
                return parse_json_object(payload["choices"][0]["message"]["content"] or "")
            except urllib.error.HTTPError as error:
                last_error = f"HTTP {error.code}: {error.read()[:200]!r}"
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


# ─── 検証 ──────────────────────────────────────────────────────────
def has_script(value: Any, pattern: str) -> bool:
    return isinstance(value, str) and bool(re.search(pattern, value))


def validate_content(entry: dict[str, Any], target: dict[str, Any]) -> None:
    """生成結果がアプリの監査（空フィールド禁止）を満たすか確認する。"""
    for field in ("meaning", "meaningEn", "synonyms", "collocations", "example"):
        if not str(entry.get(field, "")).strip():
            raise ValueError(f"{target['word']}: {field} が空です")
    if not has_script(entry["meaning"], r"[ぁ-ゟァ-ヿ一-鿿]"):
        raise ValueError(f"{target['word']}: meaning が日本語ではありません: {entry['meaning']}")
    if not re.search(r"[A-Za-z]", entry["meaningEn"]):
        raise ValueError(f"{target['word']}: meaningEn が英語ではありません")
    if "," not in entry["collocations"]:
        raise ValueError(f"{target['word']}: collocations が複数形ではありません")
    if "IELTS" in json.dumps(entry, ensure_ascii=False):
        raise ValueError(f"{target['word']}: IELTS表記が混入しています")


def content_prompt(batch: list[dict[str, Any]]) -> str:
    lines = "\n".join(
        f'{i + 1}. word="{item["word"]}" level={item["level"]} topic={item["topic"]} '
        f'分野={item["domain"]}'
        for i, item in enumerate(batch)
    )
    return f"""You are building a TOEFL vocabulary app. For each English word below, produce
dictionary-quality data used in TOEFL Integrated listening lectures and campus conversations.

Words:
{lines}

Return ONLY a valid JSON object of this exact shape (use the word itself as the key):
{{"<word>": {{
  "wordUk": "British spelling (same as the word when US and UK spelling match)",
  "phoneticUk": "UK IPA transcription with slashes, e.g. /ˈdɔːmətri/; empty string if unknown",
  "meaning": "自然な日本語訳。TOEFLの大学・学術・キャンパス文脈で最も一般的な意味。1〜3語句を読点で区切る",
  "meaningEn": "concise English definition, student-dictionary style",
  "synonyms": "3-5 comma-separated synonyms, preferring US English used in TOEFL",
  "collocations": "3-5 comma-separated collocations that really occur in TOEFL lectures, campus conversations and academic writing",
  "example": "ONE natural sentence (12-25 words) set in a TOEFL lecture, lab, library, dormitory or campus conversation",
  "meaningZh": "Simplified Chinese meaning",
  "meaningHi": "Hindi meaning in Devanagari script",
  "meaningVi": "Vietnamese meaning",
  "meaningKo": "Korean meaning in Hangul",
  "meaningId": "Indonesian meaning",
  "meaningEs": "Spanish meaning",
  "meaningTh": "Thai meaning in Thai script"
}}}}

Rules:
- Cover every word in the input. Do not add or omit entries.
- The example sentence must make the meaning obvious from context and sound like a real TOEFL recording.
- Use natural commas inside collocations so the app can split them.
- Never use the exam name "IELTS"; this is a TOEFL-only product.
- Output JSON only. No Markdown, no comments."""


def generate_content(provider: Provider, targets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    cache_path = CACHE_DIR / "content.json"
    cache: dict[str, dict[str, Any]] = json.loads(cache_path.read_text("utf-8")) if cache_path.exists() else {}

    pending = [t for t in targets if t["word"] not in cache]
    log(f"コンテンツ生成: {len(pending)} / {len(targets)} 語が未生成")
    batches = [pending[i : i + CONTENT_BATCH] for i in range(0, len(pending), CONTENT_BATCH)]

    lock = threading.Lock()

    def run(batch: list[dict[str, Any]]) -> None:
        result = provider.json_call(content_prompt(batch))
        if not isinstance(result, dict):
            raise ValueError("JSONオブジェクトではありません")
        produced = 0
        for target in batch:
            entry = result.get(target["word"]) or result.get(target["word"].lower())
            if not isinstance(entry, dict):
                log(f"  欠落: {target['word']}")
                continue
            entry = {k: (v if isinstance(v, str) else str(v)) for k, v in entry.items()}
            try:
                validate_content(entry, target)
            except ValueError as error:
                log(f"  不正: {error}")
                continue
            with lock:
                cache[target["word"]] = entry
            produced += 1
        with lock:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"  バッチ完了: {produced}/{len(batch)} 語（累計 {len(cache)}）")

    run_batches_in_parallel(batches, run, "コンテンツ生成")

    missing = [t["word"] for t in targets if t["word"] not in cache]
    if missing:
        log(f"未生成が {len(missing)} 語残っています: {missing[:10]}")
    return cache


def run_batches_in_parallel(batches: list, worker, label: str) -> None:
    """バッチを並列実行し、途中で失敗しても必ず最後まで試行する。"""
    if not batches:
        return
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(worker, batch): i for i, batch in enumerate(batches)}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as error:  # noqa: BLE001 - 1バッチの失敗で全体を止めない
                failures += 1
                log(f"  {label} バッチ失敗: {type(error).__name__}: {error}")
    if failures:
        log(f"{label}: {failures}/{len(batches)} バッチが失敗（再実行で再試行されます）")


# ─── 例文・コロケーションの多言語訳 ─────────────────────────────────
def phrase_prompt(batch: list[dict[str, Any]], language: str) -> str:
    language_name = PHRASE_LANGUAGES[language][0]
    payload = "\n".join(
        f'{item["id"]}\tCollocations: {item["collocations"]}\tExample: {item["example"]}' for item in batch
    )
    return f"""You are a meticulous native {language_name} editor creating a high-quality TOEFL vocabulary app.
Translate every English Collocations list and Example Sentence below into natural, accurate {language_name}.

Return ONLY a valid JSON object in this exact shape:
{{"numeric_id": {{"collocations": "translation", "example": "translation"}}}}
Do not omit an id. Do not add explanations, comments, Markdown, English labels, or quality scores.

Rules:
- Keep the collocation order and item count; separate translated collocations with a natural comma separator.
- Use only {language_name} in each value (names, numbers and punctuation are allowed).
- Preserve the meaning, tense, subject, modality and logical relationship of each sentence.
- Use the standard script of {language_name} suitable for educated native speakers and TOEFL learners.

Input:
{payload}
"""


def validate_phrase(result: dict[str, Any], item: dict[str, Any], language: str) -> dict[str, str]:
    pattern = PHRASE_LANGUAGES[language][1]
    out: dict[str, str] = {}
    for field in ("collocations", "example"):
        value = result.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{item['word']}: {field} が空です")
        value = value.strip()
        if not re.search(pattern, value):
            raise ValueError(f"{item['word']}: {field} が {language} ではありません: {value[:60]}")
        if value.casefold() == str(item.get(field, "")).strip().casefold():
            raise ValueError(f"{item['word']}: {field} が英語のまま返されました")
        out[field] = value
    return out


def generate_phrases(
    provider: Provider, items: list[dict[str, Any]], existing: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """語彙エントリの example / collocations を9言語へ翻訳して translations マップを返す。"""
    cache_path = CACHE_DIR / "phrases.json"
    # cache構造: {language: {word: {collocations, example}}}
    cache: dict[str, dict[str, dict[str, str]]] = (
        json.loads(cache_path.read_text("utf-8")) if cache_path.exists() else {}
    )
    lock = threading.Lock()
    translations: dict[str, dict[str, Any]] = existing.setdefault("translations", {})

    for language in PHRASE_LANGUAGES:
        language_cache = cache.setdefault(language, {})
        pending = [item for item in items if item["word"] not in language_cache]
        log(f"{language}: {len(pending)} / {len(items)} 語が未訳")
        batches = [pending[i : i + PHRASE_BATCH] for i in range(0, len(pending), PHRASE_BATCH)]

        def run(batch: list[dict[str, Any]], lang: str = language) -> None:
            parsed = provider.json_call(phrase_prompt(batch, lang))
            if not isinstance(parsed, dict):
                raise ValueError("JSONオブジェクトではありません")
            accepted = 0
            for item in batch:
                raw = parsed.get(str(item["id"]), parsed.get(item["id"]))
                if not isinstance(raw, dict):
                    continue
                try:
                    language_cache[item["word"]] = validate_phrase(raw, item, lang)
                except ValueError as error:
                    log(f"  不正: {error}")
                    continue
                accepted += 1
            with lock:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            log(f"  {lang} バッチ完了: {accepted}/{len(batch)} 語")

        run_batches_in_parallel(batches, run, f"{language} 翻訳")

    # キャッシュ内容を translations へ反映する
    for language, language_cache in cache.items():
        for item in items:
            values = language_cache.get(item["word"])
            if not values:
                continue
            entry = translations.setdefault(f"builtin:{item['id']}", {})
            for field in ("collocations", "example"):
                translation = entry.setdefault(field, {"source": item[field]})
                translation["source"] = item[field]
                translation[language] = values[field]

    # 英語(en)は source と同一なので、常に source から埋める
    for item in items:
        entry = translations.setdefault(f"builtin:{item['id']}", {})
        for field in ("collocations", "example"):
            translation = entry.setdefault(field, {"source": item[field]})
            translation["source"] = item[field]
            translation["en"] = item[field]

    return translations


def report_phrase_coverage(items: list[dict[str, Any]], translations: dict[str, Any]) -> int:
    """不足している言語訳を数える（0ならすべて揃っている）。"""
    missing = 0
    for item in items:
        entry = translations.get(f"builtin:{item['id']}", {})
        for field in ("collocations", "example"):
            translation = entry.get(field, {})
            if translation.get("source") != item[field]:
                missing += 1
                continue
            for language in list(PHRASE_LANGUAGES) + ["en"]:
                if not str(translation.get(language, "")).strip():
                    missing += 1
    return missing


# ─── マージ ────────────────────────────────────────────────────────
# アプリの語彙エントリのキー順。既存データと揃えるため、UI上の並びに合わせて固定する。
ENTRY_KEY_ORDER = [
    "id", "word", "wordUk", "phoneticUk", "meaning", "meaningEn", "synonyms",
    "collocations", "example", "level", "topic", "source_list",
    "meaningZh", "meaningHi", "meaningVi", "meaningKo", "meaningId", "meaningEs", "meaningTh",
]


def build_entry(target: dict[str, Any], content: dict[str, Any], next_id: int) -> dict[str, Any]:
    entry = {
        "id": next_id,
        "word": target["word"],
        "wordUk": content.get("wordUk") or target["word"],
        "phoneticUk": content.get("phoneticUk", ""),
        "meaning": content["meaning"].strip(),
        "meaningEn": content["meaningEn"].strip(),
        "synonyms": content["synonyms"].strip(),
        "collocations": content["collocations"].strip(),
        "example": content["example"].strip(),
        "level": target["level"],
        "topic": target["topic"],
        "source_list": SOURCE_LIST,
    }
    for field in MEANING_LANGUAGES:
        value = str(content.get(field, "")).strip()
        if not value:
            raise ValueError(f"{target['word']}: {field} が空です")
        entry[field] = value
    return {key: entry[key] for key in ENTRY_KEY_ORDER if key in entry}


def merge_into_vocabulary(targets: list[dict[str, Any]], content: dict[str, Any]) -> list[dict[str, Any]]:
    vocabulary: list[dict[str, Any]] = json.loads(VOCABULARY.read_text("utf-8"))
    known = {item["word"].strip().lower() for item in vocabulary}
    next_id = max(item["id"] for item in vocabulary) + 1

    added: list[dict[str, Any]] = []
    for target in targets:
        if target["word"].lower() in known:
            continue
        data = content.get(target["word"])
        if not data:
            continue
        entry = build_entry(target, data, next_id)
        next_id += 1
        vocabulary.append(entry)
        known.add(entry["word"].lower())
        added.append(entry)

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    return added


def load_selection() -> list[dict[str, Any]]:
    selection = json.loads(SELECTION.read_text("utf-8"))
    return selection["words"]


def main() -> int:
    parser = argparse.ArgumentParser(description="キャンパスライフ・講義トピックの追加語を投入する")
    parser.add_argument("--stage", choices=["content", "phrase", "merge"], help="実行する段階")
    parser.add_argument("--all", action="store_true", help="content → merge → phrase を通しで実行")
    parser.add_argument("--limit", type=int, default=0, help="デバッグ用: 先頭N語だけ処理")
    args = parser.parse_args()

    if not args.all and not args.stage:
        parser.error("--stage か --all を指定してください")

    targets = load_selection()
    if args.limit:
        targets = targets[: args.limit]
    log(f"対象語: {len(targets)} 語（L3={sum(1 for t in targets if t['level'] == 3)}, "
        f"L4={sum(1 for t in targets if t['level'] == 4)}）")

    provider: Provider | None = None

    def get_provider() -> Provider:
        nonlocal provider
        if provider is None:
            provider = Provider()
        return provider

    if args.all or args.stage == "content":
        content = generate_content(get_provider(), targets)
        added = merge_into_vocabulary(targets, content)
        log(f"語彙に {len(added)} 語を追加しました")

    if args.all or args.stage == "phrase":
        vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
        items = [item for item in vocabulary if item["source_list"] == SOURCE_LIST]
        log(f"例文・コロケーション訳の対象: {len(items)} 語（TOEFL-curated全体）")
        phrases = json.loads(PHRASES.read_text("utf-8"))
        translations = generate_phrases(get_provider(), items, phrases)
        phrases["schemaVersion"] = 1
        phrases["translations"] = translations
        PHRASES.write_text(json.dumps(phrases, ensure_ascii=False, indent=1), encoding="utf-8")
        missing = report_phrase_coverage(items, translations)
        log(f"不足している訳: {missing} 件")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
