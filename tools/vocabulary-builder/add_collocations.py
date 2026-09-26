#!/usr/bin/env python3
"""
TOEFL Vocabulary Collocations Adder: 既存語彙にコロケーションを追加するスクリプト
- 既存の data/enriched.json を読み込み、collocations が未生成の語のみを対象にAI生成
- 50語ずつバッチでDeepSeek APIに送信し、途中保存（再開可能）
- 完了後に --export で assets/vocabulary.json を更新
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ENRICHED_JSON_PATH = DATA_DIR / "enriched.json"
WORDS_JSON_PATH = DATA_DIR / "words.json"
APP_ASSETS_JSON = BASE_DIR.parent.parent / "app" / "src" / "main" / "assets" / "vocabulary.json"


def log(msg: str) -> None:
    print(f"[add-collocations] {msg}", flush=True)


def load_data() -> list[dict]:
    """enriched.json または words.json からデータを読み込む"""
    if ENRICHED_JSON_PATH.exists():
        data = json.loads(ENRICHED_JSON_PATH.read_text(encoding="utf-8"))
        log(f"enriched.json から {len(data)} 語を読み込み")
        return data
    if WORDS_JSON_PATH.exists():
        data = json.loads(WORDS_JSON_PATH.read_text(encoding="utf-8"))
        log(f"words.json から {len(data)} 語を読み込み")
        return data
    log("データが見つかりません。先に build_vocabulary.py を実行してください。")
    sys.exit(1)


def extract_json_array(text: str) -> list | None:
    """DeepSeekのレスポンスからJSON配列を堅牢に抽出する"""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```\s*$", "", text, flags=re.MULTILINE)

    start = text.find("[")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return parse_json_lenient(text[start:i + 1])
    return None


def parse_json_lenient(raw: str) -> list | None:
    """末尾カンマ・制御文字などの軽微なJSON不整合を修正してパースする"""
    raw = re.sub(r",\s*([\]}])", r"\1", raw)
    raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = re.sub(r"(['\"])([a-zA-Z_]+)\1\s*:", r'"\2":', raw)
        fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return None


def save_progress(data: list[dict]) -> None:
    ENRICHED_JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding="utf-8"
    )
    log(f"途中保存: {ENRICHED_JSON_PATH}")


def export_assets(data: list[dict]) -> None:
    APP_ASSETS_JSON.parent.mkdir(parents=True, exist_ok=True)
    APP_ASSETS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding="utf-8"
    )
    log(f"assets/vocabulary.json に出力: {APP_ASSETS_JSON}")


def add_collocations(data: list[dict], batch_size: int = 50) -> list[dict]:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "sk-xxxx":
        log("DEEPSEEK_API_KEY が設定されていません。.env を確認してください。")
        sys.exit(1)

    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # collocations が未生成の語のみを対象
    pending = [it for it in data if not (it.get("collocations") or "").strip()]
    total = len(pending)
    done = len(data) - total
    log(f"既にコロケーション生成済み: {done} 語 / 未生成: {total} 語")

    if total == 0:
        log("すべての語にコロケーションが付与済みです。")
        return data

    # データをインデックスで追跡（ID順を維持）
    index_by_word = {str(it.get("word", "")).lower(): i for i, it in enumerate(data)}
    used_indices = set()

    for start in range(0, total, batch_size):
        batch = pending[start:start + batch_size]
        words_str = ", ".join(f'"{it["word"]}"' for it in batch)
        level_str = ", ".join(str(it.get("level", 2)) for it in batch)
        topic_str = ", ".join(f'"{it.get("topic", "General")}"' for it in batch)
        meaning_str = ", ".join(f'"{it.get("meaning", "")[:50]}"' for it in batch)

        prompt = f"""以下のTOEFL英単語について、「コロケーション（自然な連語）」のみをJSON配列で返してください。
単語: [{words_str}]
レベル(1=基礎,2=標準,3=応用,4=発展): [{level_str}]
トピック: [{topic_str}]
日本語訳: [{meaning_str}]

出力形式（単語ごとに1オブジェクト）:
[
  {{
    "word": "単語",
    "collocations": "自然な英語の連語（コロケーション）をカンマ区切りで3-5個。TOEFLの講義・キャンパス会話・学術ライティングで使える頻出の組み合わせ。例: 'analyze data, analyze the results, carefully analyze, analyze in detail'"
  }}
]

必ず有効なJSON配列のみを返してください。その他のフィールドは含めないでください。"""
        success = False
        for attempt in range(2):
            try:
                log(f"AI生成中（試行{attempt + 1}）: {start + len(batch)} / {total} 語")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=4000,
                )
                content = resp.choices[0].message.content or ""
                enriched_list = extract_json_array(content)
                if enriched_list is None:
                    log(f"JSON抽出失敗: {content[:200]}")
                    continue

                for e in enriched_list:
                    w = str(e.get("word") or "").lower()
                    col = str(e.get("collocations") or "").strip()
                    idx = index_by_word.get(w)
                    if idx is not None and col and idx not in used_indices:
                        data[idx]["collocations"] = col
                        used_indices.add(idx)

                save_progress(data)
                success = True
                break
            except Exception as e:
                log(f"APIエラー: {e}（バッチ {start}-{start+len(batch)} をスキップ）")
                if attempt == 0:
                    time.sleep(2)
        if not success:
            save_progress(data)

        # レート制限回避
        time.sleep(1)

    completed = sum(1 for it in data if (it.get("collocations") or "").strip())
    log(f"完了: {completed} / {len(data)} 語にコロケーションを付与")
    save_progress(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="TOEFL Vocabulary Collocations Adder")
    parser.add_argument("--batch-size", type=int, default=50, help="AI生成のバッチサイズ")
    parser.add_argument("--export", action="store_true", help="完了後に assets/vocabulary.json を更新")
    args = parser.parse_args()

    data = load_data()
    data = add_collocations(data, args.batch_size)

    if args.export:
        export_assets(data)
        log("完了! assets/vocabulary.json を更新しました。")
    else:
        log("完了! --export を付けると assets/vocabulary.json を更新できます。")


if __name__ == "__main__":
    main()
