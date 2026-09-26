#!/usr/bin/env python3
"""NGSL・NAWL・AWL を統合して TOEFL 学術語彙データを構築する。"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LIST_DIR = DATA_DIR / "new_lists"
MERGED_PATH = DATA_DIR / "merged_words.json"
ENRICHED_PATH = DATA_DIR / "enriched.json"
APP_ASSETS_PATH = BASE_DIR.parent.parent / "app/src/main/assets/vocabulary.json"
KOTLIN_PATH = BASE_DIR / "output/VocabularyData_merged.kt"
TARGET_COUNT = 3851
AI_BATCH_SIZE = 10
PROGRESS_INTERVAL = 100


def _load_classifiers():
    """既存ビルダーの分類ロジックだけを読み込む（依存パッケージは不要）。"""
    source = (BASE_DIR / "build_vocabulary.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {"TOPIC_KEYWORDS", "LEVEL1_WORDS", "LEVEL2_ROOTS", "LEVEL3_ROOTS", "LEVEL4_ROOTS",
             "classify_level", "classify_topic"}
    nodes = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id in names for target in targets):
                nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    namespace: dict = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(BASE_DIR / "build_vocabulary.py"), "exec"), namespace)
    return namespace["classify_level"], namespace["classify_topic"]


classify_level, classify_topic = _load_classifiers()


def log(message: str) -> None:
    print(f"[merged-vocab] {message}", flush=True)


def normalize(word: str) -> str:
    return re.sub(r"\s+", " ", word.strip().casefold())


def atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def read_lists() -> tuple[list[str], list[str], list[str]]:
    with (LIST_DIR / "ngsl.csv").open(encoding="utf-8", newline="") as stream:
        ngsl = [row["word"].strip() for row in csv.DictReader(stream) if row.get("word", "").strip()]

    # NAWL はヘッダーなしの1語1行ファイル。
    nawl = [line.strip() for line in (LIST_DIR / "nawl.csv").read_text(encoding="utf-8").splitlines() if line.strip()]

    # AWL は「word : meaning」の形式なので左側だけを使う。
    awl = []
    for line in (LIST_DIR / "awl.txt").read_text(encoding="utf-8").splitlines():
        word = line.split(":", 1)[0].strip()
        if word:
            awl.append(word)
    return ngsl, nawl, awl


def merge_words() -> list[dict]:
    ngsl, nawl, awl = read_lists()
    seen: set[str] = set()
    items: list[dict] = []
    source_counts = {"NGSL": 0, "NAWL": 0, "AWL": 0}
    duplicate_counts = {"NGSL": 0, "NAWL": 0, "AWL": 0}

    for source, words in (("NGSL", ngsl), ("NAWL", nawl), ("AWL", awl)):
        for raw_word in words:
            key = normalize(raw_word)
            if not key:
                continue
            if key in seen:
                duplicate_counts[source] += 1
                continue
            seen.add(key)
            word = raw_word.strip()
            items.append({
                "id": len(items) + 1,
                "word": word,
                "wordUk": word,
                "phoneticUk": "",
                "meaning": "",
                "meaningEn": "",
                "synonyms": "",
                "collocations": "",
                "example": "",
                "level": classify_level(word),
                "topic": classify_topic(word),
                "source_list": source,
            })
            source_counts[source] += 1

    log(f"内訳: NGSL {source_counts['NGSL']} / NAWL {source_counts['NAWL']} / AWL {source_counts['AWL']} / 合計 {len(items)}")
    log(f"重複除外: NGSL {duplicate_counts['NGSL']} / NAWL {duplicate_counts['NAWL']} / AWL {duplicate_counts['AWL']}")
    if len(items) != TARGET_COUNT:
        raise ValueError(f"語数検証失敗: expected {TARGET_COUNT}, got {len(items)}")
    if len({normalize(item["word"]) for item in items}) != len(items):
        raise ValueError("重複検証失敗: 正規化後の重複があります")
    atomic_write_json(MERGED_PATH, items)
    log(f"build 完了: {MERGED_PATH}")
    return items


def load_json_array(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except json.JSONDecodeError as exc:
        log(f"JSONを読み込めませんでした（無視します）: {path}: {exc}")
        return []


def has_enrichment_fields(entry: dict) -> bool:
    """AI補完済みとして再利用できる最低限のフィールドを持つか確認する。"""
    meaning = entry.get("meaning") or entry.get("meaning_jp")
    meaning_en = entry.get("meaningEn") or entry.get("meaning_en")
    return all(str(entry.get(field) or "").strip() for field in ("example", "synonyms", "collocations")) \
        and bool(str(meaning or "").strip()) \
        and bool(str(meaning_en or "").strip())


def reusable_entries() -> dict[str, dict]:
    result: dict[str, dict] = {}
    # enriched.json が途中保存の場合、空欄のエントリまで再利用すると再開できない。
    # 意味・定義・例文がそろったエントリだけを追加する。
    for entry in load_json_array(ENRICHED_PATH):
        word = str(entry.get("word", "")).strip()
        if word and normalize(word) not in result and has_enrichment_fields(entry):
            result[normalize(word)] = entry
    # enriched.json にない完全な語はアプリ assets の既存データから再利用する。
    for entry in load_json_array(APP_ASSETS_PATH):
        word = str(entry.get("word", "")).strip()
        if word and normalize(word) not in result and has_enrichment_fields(entry):
            result[normalize(word)] = entry
    log(f"既存データから再利用可能な語: {len(result)} 語")
    return result


def merge_existing(items: list[dict]) -> tuple[list[dict], list[dict]]:
    existing = reusable_entries()
    merged: list[dict] = []
    pending: list[dict] = []
    for item in items:
        old = existing.get(normalize(item["word"]))
        if old is None:
            merged.append(dict(item))
            pending.append(merged[-1])
            continue
        # ID・分類・出典は今回のリストを正とし、補完フィールドは既存値を再利用する。
        current = dict(item)
        aliases = {
            "meaning": ("meaning", "meaning_jp"),
            "meaningEn": ("meaningEn", "meaning_en"),
            "wordUk": ("wordUk",), "phoneticUk": ("phoneticUk",),
            "synonyms": ("synonyms",), "collocations": ("collocations",), "example": ("example",),
        }
        for field, candidates in aliases.items():
            for candidate in candidates:
                if old.get(candidate) is not None:
                    current[field] = old[candidate]
                    break
        merged.append(current)
    log(f"再利用: {len(items) - len(pending)} 語 / AI補完対象: {len(pending)} 語")
    return merged, pending


def extract_json_array(text: str) -> list[dict] | None:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    start = text.find("[")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                try:
                    value = json.loads(re.sub(r",\s*([}\]])", r"\1", text[start:index + 1]))
                    return value if isinstance(value, list) else None
                except json.JSONDecodeError:
                    return None
    return None


def enrich(items: list[dict]) -> list[dict]:
    merged, pending = merge_existing(items)
    if not pending:
        atomic_write_json(ENRICHED_PATH, merged)
        return merged

    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / ".env")
    except ImportError:
        pass
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key in {"sk-xxxx", "sample_api_key", "あとで書き換え"}:
        log("DEEPSEEK_API_KEY が未設定のため、新規語は未補完のまま保存します。")
        atomic_write_json(ENRICHED_PATH, merged)
        return merged

    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=120.0,
        max_retries=0,
    )
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    by_word = {normalize(item["word"]): item for item in merged}
    started = time.time()

    for start in range(0, len(pending), AI_BATCH_SIZE):
        batch = pending[start:start + AI_BATCH_SIZE]
        words = ", ".join(json.dumps(item["word"], ensure_ascii=False) for item in batch)
        prompt = f"""以下の英単語について、単語ごとにJSON配列で返してください。
単語: [{words}]
各オブジェクトのキーは word, wordUk, phoneticUk, meaning_jp, meaning_en, synonyms, collocations, example としてください。
synonyms と collocations はカンマ区切りで3〜5個、example はTOEFLで使える自然な英文にしてください。
必ず有効なJSON配列のみを返してください。"""
        response_data: list[dict] | None = None
        for attempt in range(1, 4):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=8000,
                )
                response_data = extract_json_array(response.choices[0].message.content or "")
                if response_data is not None:
                    break
                log(f"JSON解析失敗: バッチ {start + 1}-{start + len(batch)} / 試行 {attempt}")
            except Exception as exc:
                log(f"APIエラー: {exc} / バッチ {start + 1}-{start + len(batch)} / 試行 {attempt}")
            if attempt < 3:
                time.sleep(2 ** (attempt - 1))

        if response_data:
            for entry in response_data:
                key = normalize(str(entry.get("word", "")))
                if key not in by_word:
                    continue
                item = by_word[key]
                item["wordUk"] = entry.get("wordUk") or item["word"]
                item["phoneticUk"] = entry.get("phoneticUk") or ""
                item["meaning"] = entry.get("meaning_jp") or entry.get("meaning") or ""
                item["meaningEn"] = entry.get("meaning_en") or entry.get("meaningEn") or ""
                item["synonyms"] = entry.get("synonyms") or ""
                item["collocations"] = entry.get("collocations") or ""
                item["example"] = entry.get("example") or ""

        # API 成否にかかわらず、各バッチ単位で安全に保存する。
        atomic_write_json(ENRICHED_PATH, merged)
        done = min(start + len(batch), len(pending))
        if done % PROGRESS_INTERVAL == 0 or done == len(pending):
            elapsed = max(time.time() - started, 0.001)
            rate = done / elapsed
            remaining = (len(pending) - done) / rate if rate else 0
            log(f"進捗: {done}/{len(pending)}語 ({done / len(pending) * 100:.1f}%) | 処理速度 {rate * 60:.1f}語/分 | 残り約{remaining / 60:.1f}分")
        time.sleep(1)
    return merged


def escape_kotlin(value: object) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")


def export(items: list[dict]) -> None:
    if len(items) != TARGET_COUNT:
        raise ValueError(f"export対象の語数が不正です: {len(items)}")
    atomic_write_json(APP_ASSETS_PATH, items)
    lines = [
        "package com.gachiguild.gachitoefl.data.local", "",
        "import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity", "",
        "/** 自動生成: build_merged_vocabulary.py / 収録語数: 3851語 */",
        "val VocabularyMergedData: List<VocabularyEntity> = listOf(",
    ]
    for item in items:
        fields = ", ".join([
            f"id = {item['id']}", f'word = "{escape_kotlin(item["word"])}"',
            f'wordUk = "{escape_kotlin(item.get("wordUk"))}"', f'phoneticUk = "{escape_kotlin(item.get("phoneticUk"))}"',
            f'meaning = "{escape_kotlin(item.get("meaning"))}"', f'meaningEn = "{escape_kotlin(item.get("meaningEn"))}"',
            f'synonyms = "{escape_kotlin(item.get("synonyms"))}"', f'collocations = "{escape_kotlin(item.get("collocations"))}"',
            f'example = "{escape_kotlin(item.get("example"))}"', f"level = {item.get('level', 2)}",
            f'topic = "{escape_kotlin(item.get("topic", "General"))}"',
        ])
        lines.append(f"    VocabularyEntity({fields}),")
    lines.append(")")
    KOTLIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    KOTLIN_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"export 完了: {APP_ASSETS_PATH}")
    log(f"Kotlin リファレンス: {KOTLIN_PATH}")


def load_build_data() -> list[dict]:
    if not MERGED_PATH.exists():
        raise FileNotFoundError(f"{MERGED_PATH} がありません。先に --build を実行してください。")
    items = load_json_array(MERGED_PATH)
    if len(items) != TARGET_COUNT:
        raise ValueError(f"入力データの語数が不正です: {len(items)}")
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="NGSL + NAWL + AWL merged vocabulary builder")
    parser.add_argument("--build", action="store_true", help="リストを統合して語数を検証")
    parser.add_argument("--enrich", action="store_true", help="不足語だけAI補完（10語バッチ）")
    parser.add_argument("--export", action="store_true", help="assets JSON と Kotlin を出力")
    args = parser.parse_args()
    if not (args.build or args.enrich or args.export):
        parser.error("--build、--enrich、--export のいずれかを指定してください")
    try:
        items = merge_words() if args.build else load_build_data()
        if args.enrich:
            items = enrich(items)
        elif args.export and ENRICHED_PATH.exists():
            enriched = load_json_array(ENRICHED_PATH)
            if len(enriched) == TARGET_COUNT:
                items = enriched
        if args.export:
            export(items)
        return 0
    except Exception as exc:
        log(f"失敗: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
