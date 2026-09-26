"""Translate the English words that leaked into example-sentence translations.

The first generation pass rewrote every example sentence into an American
university context and produced eight translations per sentence. In some
translations the model left an English word untranslated, for example

    see     es: "Puedes see el laboratorio de astronomia...?"
    weather zh: "环境科学教材解释了极端 weather 如何影响校园建设项目。"
    think   es: "I think que la biblioteca cierra temprano los viernes."

Re-running the sentence generator for all of them is expensive and was already
blocked by API credit limits, so this tool fixes the leak directly:

1. Collect every English word that appears in a non-English translation of the
   example sentence (the headword itself, and any other English word the model
   left behind).
2. Ask the translation provider once per (language, words) batch for the target
   language equivalents, with part of speech taken from the sentence context.
3. Substitute the returned words, then write the assets back.

`collocations`, every English `example`, and all other words stay untouched.

Usage:
  python3 translate_example_gaps.py --collect            # 対象語の棚卸し
  python3 translate_example_gaps.py --limit 40           # 疎通確認
  python3 translate_example_gaps.py --workers 8          # 全件
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
CACHE = Path("/private/tmp/toefl-example-gap-words.json")

TARGET_LANGUAGES = {
    "ja": ("Japanese", r"[ぁ-ゟァ-ヿ一-鿿]"),
    "zh": ("Simplified Chinese", r"[一-鿿]"),
    "hi": ("Hindi", r"[ऀ-ॿ]"),
    "vi": ("Vietnamese", r"[A-Za-zÀ-ỹ]"),
    "ko": ("Korean", r"[가-힣]"),
    "id": ("Indonesian", r"[A-Za-zÀ-ỹ]"),
    "th": ("Thai", r"[ก-๛]"),
    "es": ("Spanish", r"[A-Za-zÀ-ỹÁÉÍÓÚÜÑáéíóúüñ]"),
}
# 訳文に残ってよい語（固有名詞・記号・単位など）
ALLOWED_TOKENS = {
    "gpa", "sat", "toefl", "usa", "us", "uk", "nyu", "mit", "ba", "ma", "phd",
    "i", "a", "an", "the", "tv", "dna", "rna", "ph", "ceo", "id",
}
_TOKEN = re.compile(r"[A-Za-z][A-Za-z'\-]*")
BATCH_SIZE = 20
WORKERS = 8


def log(message: str) -> None:
    print(f"[translate-gaps] {time.strftime('%H:%M:%S')} | {message}", flush=True)


class Provider:
    """LUNA（OpenAI互換）を優先し、無ければ DeepSeek を使う薄いクライアント。"""

    def __init__(self) -> None:
        load_dotenv(BASE_DIR / ".env")
        candidates = [
            ("LUNA", os.getenv("LUNA_API_KEY"), os.getenv("LUNA_BASE_URL"), os.getenv("LUNA_MODEL")),
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
        raise SystemExit("利用可能なAPIキーが .env にありません（LUNA_API_KEY / DEEPSEEK_API_KEY）")

    def json_call(self, prompt: str, max_tokens: int = 16000, attempts: int = 4) -> Any:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        if self.name == "DEEPSEEK":
            body["temperature"] = 0.2
            body["max_tokens"] = max_tokens
        else:
            body["max_completion_tokens"] = max_tokens
        last_error = ""
        for attempt in range(attempts):
            try:
                request = urllib.request.Request(
                    f"{self.base}/chat/completions",
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"},
                )
                with urllib.request.urlopen(request, timeout=180) as response:
                    payload = json.load(response)
                return parse_json_object(payload["choices"][0]["message"]["content"] or "")
            except urllib.error.HTTPError as error:
                detail = error.read()[:200]
                last_error = f"HTTP {error.code}: {detail!r}"
                if error.code in (401, 402, 403):
                    raise RuntimeError(f"API呼び出しに失敗しました: {last_error}") from error
            except Exception as error:  # noqa: BLE001
                last_error = f"{type(error).__name__}: {error}"
            time.sleep(2 + attempt * 3)
        raise RuntimeError(f"API呼び出しに失敗しました: {last_error}")


def parse_json_object(content: str) -> Any:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", content)
    cleaned = re.sub(r"```(?:json)?", "", cleaned, flags=re.IGNORECASE).replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"JSONを抽出できませんでした: {content[:200]}")
    return json.loads(cleaned[start : end + 1])


def english_tokens(value: str) -> list[str]:
    """訳文に残った英単語を出現順に返す。"""
    found: list[str] = []
    for match in _TOKEN.finditer(value):
        token = match.group(0)
        if token.lower() in ALLOWED_TOKENS or len(token) < 2:
            continue
        if token not in found:
            found.append(token)
    return found


MULTIWORD_HINTS: dict[str, dict[str, str]] = {
    # 複合語は「一部だけ訳す」と誤訳になるため、語全体の訳語を固定する。
    "long-term memory": {
        "ja": "長期記憶", "zh": "长期记忆", "hi": "दीर्घकालिक स्मृति", "vi": "trí nhớ dài hạn",
        "ko": "장기 기억", "id": "memori jangka panjang", "th": "ความจำระยะยาว",
        "es": "memoria a largo plazo",
    },
    "long-term potentiation": {
        "ja": "長期増強", "zh": "长时程增强", "hi": "दीर्घकालिक दृढ़ीकरण", "vi": "tăng cường dài hạn",
        "ko": "장기 강화", "id": "potensiasi jangka panjang", "th": "การเสริมกำลังระยะยาว",
        "es": "potenciación a largo plazo",
    },
    "working memory": {
        "ja": "ワーキングメモリ", "zh": "工作记忆", "hi": "कार्यशील स्मृति", "vi": "trí nhớ làm việc",
        "ko": "작업 기억", "id": "memori kerja", "th": "ความจำใช้งาน", "es": "memoria de trabajo",
    },
    "rem sleep": {
        "ja": "レム睡眠", "zh": "快速眼动睡眠", "hi": "रेम नींद", "vi": "giấc ngủ REM",
        "ko": "렘 수면", "id": "tidur REM", "th": "การนอนหลับ REM", "es": "sueño REM",
    },
    "reward system": {
        "ja": "報酬系", "zh": "奖赏系统", "hi": "पुरस्कार प्रणाली", "vi": "hệ thống khen thưởng",
        "ko": "보상 시스템", "id": "sistem penghargaan", "th": "ระบบให้รางวัล",
        "es": "sistema de recompensa",
    },
    "search engine": {
        "ja": "検索エンジン", "zh": "搜索引擎", "hi": "सर्च इंजन", "vi": "công cụ tìm kiếm",
        "ko": "검색 엔진", "id": "mesin pencari", "th": "เสิร์ชเอนจิน", "es": "motor de búsqueda",
    },
    "secondary source": {
        "ja": "二次資料", "zh": "二手资料", "hi": "द्वितीयक स्रोत", "vi": "nguồn thứ cấp",
        "ko": "2차 자료", "id": "sumber sekunder", "th": "แหล่งข้อมูลทุติยภูมิ",
        "es": "fuente secundaria",
    },
    "self-fulfilling prophecy": {
        "ja": "自己成就予言", "zh": "自我实现的预言", "hi": "स्वयं-पूर्ण भविष्यवाणी",
        "vi": "lời tiên đoán tự ứng nghiệm", "ko": "자기실현적 예언",
        "id": "ramalan yang terwujud sendiri", "th": "คำทำนายที่กลายเป็นจริง",
        "es": "profecía autocumplida",
    },
    "syllabus week": {
        "ja": "シラバス週間", "zh": "课程说明周", "hi": "पाठ्यक्रम परिचय सप्ताह",
        "vi": "tuần giới thiệu môn học", "ko": "오리엔테이션 주간",
        "id": "pekan silabus", "th": "สัปดาห์แนะนำรายวิชา", "es": "semana de presentación",
    },
    "magnitude scale": {
        "ja": "マグニチュード階級", "zh": "震级标度", "hi": "परिमाण पैमाना",
        "vi": "thang độ lớn", "ko": "규모 척도", "id": "skala magnitudo",
        "th": "มาตราระดับขนาด", "es": "escala de magnitud",
    },
    "seminar paper": {
        "ja": "ゼミ論文", "zh": "研讨课论文", "hi": "सेमिनार पत्र", "vi": "bài tiểu luận seminar",
        "ko": "세미나 논문", "id": "makalah seminar", "th": "รายงานสัมมนา",
        "es": "trabajo de seminario",
    },
    "stages of development": {
        "ja": "発達段階", "zh": "发展阶段", "hi": "विकास के चरण", "vi": "các giai đoạn phát triển",
        "ko": "발달 단계", "id": "tahap perkembangan", "th": "ขั้นตอนการพัฒนา",
        "es": "etapas del desarrollo",
    },
}


def translation_is_usable(token: str, value: str, pattern: str) -> bool:
    """返ってきた訳語が1語で、対象言語の文字で書かれているかを確認する。"""
    if not value:
        return False
    if not re.search(pattern, value):
        return False
    # 括弧や読点で複数候補を返す場合は採用しない（訳文に混ぜられないため）。
    if any(mark in value for mark in ("(", ")", "（", "）", "/", "、")):
        return False
    # 説明文の混入（語数が多すぎる）を防ぐ。複合語はやや長くなるため余裕を持たせる。
    limit = 6 if len(token.split()) > 1 else 3
    if len(value.split()) > limit:
        return False
    # 複合語の一部しか訳出していない場合（"long-term memory" -> "memoria"）は誤訳なので弾く。
    if len(token.split()) > 1:
        words = token.split()
        heads = [word for word in words if word.lower() not in ("of", "the", "in", "to", "and", "a", "an")]
        if len(value.split()) < max(1, len(heads) - 1):
            return False
    return True


def leaked_headwords(
    word: str, value: str, language: str | None = None
) -> list[str]:
    """訳文に英語のまま残っている見出し語（活用形を含む）を返す。

    語彙データの不具合は「例文の見出し語が訳されずに英語のまま残る」形で出るため、
    対象をこの1種類に絞る。3文字未満の語も原文表記のまま検出する。

    スペイン語・インドネシア語・ベトナム語では見出し語がそのまま正しい訳語になる
    ことがある（"hotel" → "hotel"）。そこで単語の意味を英辞郎的に判定するのでは
    なく、訳文の中に *英語として* 不自然な形で残っているかを見る:
      - 見出し語がそのまま同形で、かつ訳文の他の部分がすでに対象言語で書かれている
        場合は、同形の正しい訳語とみなして除外する。
      - 一方 "Puedes see el laboratorio" の "see" のように、活用形や別語が英語で
        残っている場合は除外しない。
    そのため、見出し語そのものの同形一致は「その言語で同じ綴りの語が実在する語」に
    限って除外するためのホワイトリストで判定する。
    """
    target = word.strip()
    if not target:
        return []
    # 訳文が対象言語として正しい同形語を含むだけの場合（スペイン語の "las tradiciones
    # musicales"、インドネシア語の "sistem imun" など）は不具合ではない。
    # そのため「見出し語と同形の語」および「その規則変化形」は、対象言語の語として
    # 成立し得るものとみなす。英語の語がそのまま浮いている場合（"Puedes see el ..."）
    # はここで除外されないので、引き続き検出される。
    cognate_forms = {target}
    for suffix in ("s", "es", "ed", "ing", "ies", "a", "o", "al", "ic", "ive"):
        cognate_forms.add(target + suffix)
    # 英語の動詞・助動詞など、対象言語に存在しない基本語は同形でも除外しない。
    leaked: list[str] = []
    candidates = [target] + [target + suffix for suffix in ("s", "es", "ed", "ing", "ies")]
    for candidate in candidates:
        for match in re.finditer(rf"(?<![A-Za-z]){re.escape(candidate)}(?![A-Za-z])", value):
            token = match.group(0)
            if token.lower() in INTERNATIONAL_TOKENS:
                continue
            if token.lower() in ENGLISH_ONLY_TOKENS:
                if token not in leaked:
                    leaked.append(token)
                continue
            if candidate.lower() in cognate_forms:
                continue
            if token not in leaked:
                leaked.append(token)
    return leaked


# スペイン語・インドネシア語・ベトナム語にも同形で存在しない、英語固有の基本語。
# 訳文にこれらがそのまま残っていれば、必ず未訳の不具合。
ENGLISH_ONLY_TOKENS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can", "could",
    "did", "do", "does", "for", "from", "get", "got", "had", "has", "have", "he",
    "her", "him", "his", "how", "i", "if", "in", "is", "it", "its", "like", "make",
    "may", "me", "might", "more", "most", "much", "my", "none", "not", "of", "on",
    "or", "our", "out", "see", "she", "should", "so", "some", "than", "that", "the",
    "their", "them", "then", "there", "these", "they", "think", "this", "those",
    "through", "to", "up", "us", "was", "we", "were", "what", "when", "which",
    "while", "who", "why", "will", "with", "would", "you", "your",
}

# 対象言語でもそのまま通用する固有名詞・略語。訳文に残っていても不具合ではない。
INTERNATIONAL_TOKENS = {"iq", "gpa", "sat", "toefl", "dna", "rna", "ph", "id", "tv", "ceo"}


# スペイン語・インドネシア語・ベトナム語で、見出し語と同じ綴りが正しい訳語になる語。
# これ以外の語で見出し語がそのまま残っていれば、未訳の不具合として扱う。
COGNATE_WHITELIST = {
    "abdominal", "alcohol", "analog", "animal", "area", "atlas", "audio", "banana",
    "bank", "bar", "bus", "club", "chocolate", "civil", "color", "comparable",
    "compatible", "conceptual", "concurrent", "congruent", "continental", "cultural",
    "curricular", "digital", "diesel", "distant", "divides", "electoral", "electron",
    "error", "evident", "ex", "experimental", "final", "festival", "fetal", "gas",
    "general", "golf", "gram", "horizontal", "hospital", "hotel", "humor", "idea",
    "informal", "interior", "ion", "jazz", "labor", "lateral", "legal", "liberal",
    "literal", "local", "lunar", "manual", "marginal", "marina", "mass", "material",
    "median", "medicinal", "mental", "metal", "mineral", "modal", "modern", "modular",
    "molecular", "moral", "motor", "municipal", "musical", "mutable", "natural",
    "neutral", "noble", "norm", "normal", "nuclear", "occipital", "opera", "oral",
    "orbital", "organ", "original", "panel", "paranoia", "patina", "perceptible",
    "perceptual", "personal", "pi", "plausible", "plural", "polar", "pop", "popular",
    "present", "principal", "radio", "radar", "real", "regional", "regular",
    "resident", "residual", "resilient", "resist", "ritual", "rival", "scenario",
    "secret", "sector", "semester", "sexual", "simple", "singular", "ski", "social",
    "soluble", "sponsor", "strict", "suburban", "superior", "talent", "taxi",
    "territorial", "total", "transistor", "trauma", "tropical", "tsunami", "tumor",
    "uniform", "universal", "urgent", "usual", "variable", "vector", "verbal",
    "vertebral", "vertical", "viable", "virtual", "virus", "visible", "visual",
    "vital", "vitamin", "vocal", "vulnerable",
    # インドネシア語で同形の語
    "agenda", "atom", "era", "hotel", "kilo", "meter", "militia", "museum", "panel",
    "planet", "protein", "proton", "reactor", "sensor", "ton", "unit",
}



# ─── 訳語の取得 ────────────────────────────────────────────────────
def translation_prompt(language: str, items: list[dict[str, str]]) -> str:
    language_name = TARGET_LANGUAGES[language][0]
    lines = "\n".join(
        f'{i + 1}. "{item["token"]}"  Context sentence: {item["sentence"]}'
        for i, item in enumerate(items)
    )
    return f"""You are a bilingual lexicographer writing example sentences for a TOEFL vocabulary app.

Each item below is an English word that was left untranslated inside a
{language_name} sentence, together with that sentence for context. Give the one
{language_name} word that a native speaker would use for it in exactly that context.

Words:
{lines}

Return ONLY a valid JSON object mapping the English word (exactly as written, lowercase)
to its single {language_name} equivalent:
{{"word": "translation"}}

Rules:
- Translate the word as it is actually used in the context sentence. Read the sentence
  first: for example, "delta" in a geology lecture about a river mouth means the
  landform, while in a statistics lecture it means a difference in value.
- Output exactly one word in {language_name} script. No parentheses, no explanations,
  no alternatives, no romanisation, no English.
- Names of people and places are the only exception; keep those as they are.
- Never return the English word itself.
"""


def translation_is_usable(token: str, value: str, pattern: str) -> bool:
    """返ってきた訳語が1語で、対象言語の文字で書かれているかを確認する。"""
    if not value or value.lower() == token.lower():
        return False
    if not re.search(pattern, value):
        return False
    # 括弧や読点で複数候補を返す場合は最初の1語だけを採用する。
    if any(mark in value for mark in ("(", ")", "（", "）", "/", "、")):
        return False
    # 説明文の混入（語数が多すぎる）を防ぐ。
    if len(value.split()) > 3:
        return False
    if token.lower() in value.lower():
        return False
    return True


def translate_tokens(provider: Provider, language: str, items: list[dict[str, str]]) -> dict[str, str]:
    """1言語ぶんの訳語をまとめて取得する。"""
    pattern = TARGET_LANGUAGES[language][1]
    result: dict[str, str] = {}
    for chunk_start in range(0, len(items), BATCH_SIZE):
        chunk = items[chunk_start : chunk_start + BATCH_SIZE]
        payload = provider.json_call(translation_prompt(language, chunk))
        if not isinstance(payload, dict):
            raise ValueError("JSONオブジェクトではありません")
        lowered = {str(k).lower(): str(v).strip() for k, v in payload.items()}
        for item in chunk:
            # 複合語は固定の訳語を優先し、部分訳による誤訳を防ぐ。
            curated = MULTIWORD_HINTS.get(item["token"].lower(), {}).get(language)
            if curated:
                result[item["token"].lower()] = curated
                continue
            value = lowered.get(item["token"].lower(), "")
            if translation_is_usable(item["token"], value, pattern):
                result[item["token"].lower()] = value
    return result



# ─── 収集と適用 ────────────────────────────────────────────────────
def collect_gaps(
    vocabulary: list[dict[str, Any]], translations: dict[str, Any]
) -> dict[str, dict[str, dict[str, str]]]:
    """言語ごとに「英語のまま残った見出し語」と代表的な文脈を集める。

    戻り値は {language: {lowercase_token: {"token": 原文表記, "sentence": 文脈}}}。
    """
    gaps: dict[str, dict[str, dict[str, str]]] = {}
    for item in vocabulary:
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            continue
        for language in TARGET_LANGUAGES:
            value = str(record.get(language, "")).strip()
            if not value:
                continue
            for token in leaked_headwords(item["word"], value, language):
                gaps.setdefault(language, {}).setdefault(
                    token.lower(), {"token": token, "sentence": value}
                )
    return gaps


def apply_replacements(
    vocabulary: list[dict[str, Any]],
    translations: dict[str, Any],
    lexicon: dict[str, dict[str, str]],
) -> tuple[int, int]:
    """収集した訳語で、訳文に残った見出し語を置き換える。"""
    replaced = 0
    remaining = 0
    for item in vocabulary:
        record = translations.get(f"builtin:{item['id']}", {}).get("example")
        if not isinstance(record, dict):
            continue
        for language in TARGET_LANGUAGES:
            value = str(record.get(language, "")).strip()
            if not value:
                continue
            leaked = leaked_headwords(item["word"], value, language)
            if not leaked:
                continue
            updated = value
            for token in leaked:
                replacement = lexicon.get(language, {}).get(token.lower())
                if not replacement:
                    continue
                updated = re.sub(
                    rf"(?<![A-Za-z]){re.escape(token)}(?![A-Za-z])", replacement, updated
                )
                replaced += 1
            if leaked_headwords(item["word"], updated, language):
                remaining += 1
            record[language] = updated
    return replaced, remaining


def load_cache() -> dict[str, dict[str, str]]:
    if not CACHE.exists():
        return {}
    try:
        raw = json.loads(CACHE.read_text("utf-8"))
    except json.JSONDecodeError:
        return {}
    return {
        str(k): {str(k2): str(v2) for k2, v2 in v.items()}
        for k, v in raw.items()
        if isinstance(v, dict)
    }


def save_cache(lexicon: dict[str, dict[str, str]]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    temporary = CACHE.with_suffix(".tmp")
    temporary.write_text(json.dumps(lexicon, ensure_ascii=False, indent=1), encoding="utf-8")
    temporary.replace(CACHE)


# ─── 実行 ──────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description="例文訳に残った英単語を訳語へ置き換える")
    parser.add_argument("--collect", action="store_true", help="対象語の棚卸しだけ行う")
    parser.add_argument("--limit", type=int, default=0, help="デバッグ用: 言語ごとの語数を制限")
    parser.add_argument("--workers", type=int, default=WORKERS, help="並列数")
    parser.add_argument("--check", action="store_true", help="JSONを書き換えず差分だけ確認")
    args = parser.parse_args()

    vocabulary = json.loads(VOCABULARY.read_text("utf-8"))
    translations_root = json.loads(PHRASES.read_text("utf-8"))
    translations = translations_root["translations"]

    gaps = collect_gaps(vocabulary, translations)
    for language in sorted(gaps):
        print(f"{language}: {len(gaps[language])} distinct English words")
    print(f"total: {sum(len(v) for v in gaps.values())}")
    if args.collect:
        return 0

    items_by_language: dict[str, list[dict[str, str]]] = {}
    for language, bucket in gaps.items():
        tokens = sorted(bucket)
        if args.limit:
            tokens = tokens[: args.limit]
        items_by_language[language] = [
            {"token": bucket[token]["token"], "sentence": bucket[token]["sentence"]}
            for token in tokens
        ]

    provider = Provider()
    lexicon = load_cache()
    lock = threading.Lock()
    failures: list[str] = []

    def run(language: str) -> None:
        try:
            produced = translate_tokens(provider, language, items_by_language[language])
        except Exception as error:  # noqa: BLE001 - 1言語の失敗で全体を止めない
            with lock:
                failures.append(f"{language}: {type(error).__name__}: {error}")
            log(f"  {language} 失敗: {type(error).__name__}: {error}")
            return
        with lock:
            lexicon.setdefault(language, {}).update(produced)
            save_cache(lexicon)
        log(f"  {language}: {len(produced)}/{len(items_by_language[language])} 語を取得")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        list(executor.map(run, sorted(items_by_language)))

    replaced, untouched = apply_replacements(vocabulary, translations, lexicon)
    print(f"replacements applied: {replaced} / sentences still containing English: {untouched}")
    if args.check:
        return 0

    VOCABULARY.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1), encoding="utf-8")
    translations_root["schemaVersion"] = 1
    PHRASES.write_text(json.dumps(translations_root, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {PHRASES}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

    temporary = CACHE.with_suffix(".tmp")
    temporary.write_text(json.dumps(lexicon, ensure_ascii=False, indent=1), encoding="utf-8")
    temporary.replace(CACHE)
