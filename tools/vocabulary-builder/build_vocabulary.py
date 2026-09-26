#!/usr/bin/env python3
"""
TOEFL Vocabulary Builder: 学術英語語彙DBを構築するパイプライン
1. ダウンロード: オープンライセンスの高頻度語リスト + 既存1,000語をマージ
2. 分類: レベル(1〜4)・トピックを自動付与
3. AI補完: DeepSeek APIで日本語訳・例文・類義語をバッチ生成
4. エクスポート: アプリ用Kotlinソース生成
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ─── 定数 ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
RAW_WORDS_PATH = DATA_DIR / "raw_words.txt"
WORDS_JSON_PATH = DATA_DIR / "words.json"
ENRICHED_JSON_PATH = DATA_DIR / "enriched.json"
KOTLIN_OUTPUT_PATH = OUTPUT_DIR / "VocabularyData.kt"
APP_VOCABULARY_DATA = BASE_DIR.parent.parent / "app" / "src" / "main" / "java" \
    / "com" / "gachiguild" / "gachitoefl" / "data" / "local" / "VocabularyData.kt"
APP_ASSETS_JSON = BASE_DIR.parent.parent / "app" / "src" / "main" / "assets" / "vocabulary.json"

# オープンライセンスの高頻度語リスト（google-10000-english: MITライセンス相当）
GOOGLE_10000_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt"
# バックアップ: 各種公開リストの試行順
FALLBACK_URLS = [
    "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa.txt",
]

# トピック判定キーワード
TOPIC_KEYWORDS = {
    "Environment": ["environment", "climate", "carbon", "pollut", "sustain", "green", "ecolog",
                    "recycl", "emission", "energy", "conserv", "fossil", "renewable", "waste",
                    "nature", "habitat", "species", "biodivers", "global warming", "エコ", "環境",
                    "気候", "二酸化炭素", "汚染", "省エネ", "生物"],
    "Education": ["educat", "school", "student", "universit", "academ", "learn", "study",
                  "teacher", "curricul", "lecture", "lesson", "knowledge", "seminar", "degree",
                  "campus", "college", "教育", "学生", "大学", "学習", "講義", "知識", "学校"],
    "Technology": ["technolog", "digital", "software", "computer", "network", "device", "internet",
                   "online", "robot", "artificial", "machine", "innov", "automation", "cyber",
                   "electronic", "テクノロジー", "技術", "デジタル", "コンピュータ", "ネットワーク",
                   "インターネット", "オンライン", "革新", "自動化"],
    "Health": ["health", "medic", "disease", "patient", "doctor", "hospital", "clinic",
               "treatment", "therapy", "illness", "symptom", "nutrition", "fitness", "mental",
               "vaccin", "drug", "stress", "健康", "医療", "病気", "患者", "治療", "栄養", "ストレス"],
    "Society": ["societ", "social", "community", "family", "population", "urban", "rural",
                "poverty", "inequal", "crime", "justice", "culture", "tradition", "migration",
                "immigrat", "public", "govern", "policy", "citizen", "welfare", "housing",
                "社会", "コミュニティ", "家族", "人口", "都市", "地方", "貧困", "不平等",
                "犯罪", "文化", "伝統", "移民", "公共", "政府", "政策"],
    "Economy": ["econom", "finance", "market", "trade", "business", "money", "income", "bank",
                "invest", "tax", "wealth", "industry", "commerce", "employee", "unemploy",
                "profit", "budget", "consum", "salary", "currency", "経済", "金融", "市場",
                "貿易", "ビジネス", "お金", "収入", "投資", "税", "富", "産業", "雇用", "失業"],
    "Science": ["science", "research", "experiment", "hypothesis", "theory", "laboratory",
                "physics", "chemistry", "biology", "analysis", "evidence", "observe",
                "genetic", "quantum", "科学", "研究", "実験", "仮説", "理論", "分析", "証拠", "遺伝子"],
}

# Level 1 の基礎語
LEVEL1_WORDS = set("""
a about after again all also an and any are as at back be because been before being
between both but by came can come could day did do down each even every few first for
from get go good got great had has have he her here him his how I if in into is it its
just know like little long make made man many may me might more most much must my never
new no not now of off old on one only or other our out over own people place right said
same say see she should since so some still such take than that the their them then there
these they thing this those three through time to two under up us use very was way we well
what when where which while who why will with work world would year you your
""".split())

# Level 2 の代表ルート（アカデミック語彙）
LEVEL2_ROOTS = [
    "analy", "accur", "benefi", "signific", "establish", "demonstrat", "interpret",
    "contribut", "consequent", "furthermore", "nevertheless", "emphasiz", "acquire",
    "assume", "conduct", "evident", "initially", "subsequent", "ultimately", "adapt",
    "alter", "approach", "available", "concept", "derive", "distinct", "element",
    "ensure", "estimate", "evaluation", "exclude", "explicit", "exposure", "external",
    "generate", "identify", "illustrate", "impact", "indicate", "individual",
    "influence", "instance", "issue", "maintain", "majority", "method", "minimal",
    "modify", "monitor", "objective", "obtain", "occur", "option", "outcome",
    "overall", "perceive", "perspective", "potential", "precise", "principle",
    "procedure", "proportion", "pursue", "relevant", "reluctant", "resolve",
    "accommodate", "accompany", "account", "accumulate", "acknowledge", "adequate",
    "adjust", "administer", "advocate", "affect", "allocate", "alternative",
    "anticipate", "apparent", "appeal", "appropriate", "assess", "assign", "assist",
    "attach", "attain", "attribute", "authentic", "aware", "barrier", "capacity",
    "category", "challenge", "character", "circumstance", "cite", "clarify",
    "coherent", "commit", "compatible", "competent", "component", "compromise",
    "confirm", "conform", "consecutive", "consent", "consistent", "constitute",
    "consult", "consume", "contemporary", "convert", "convey", "convince",
    "cooperate", "coordinate", "correspond", "criterion", "crucial", "cultivate",
    "declare", "decline", "decrease", "deduce", "depict", "designate", "devise",
    "diligent", "diminish", "disclose", "distinct", "diverse", "domestic",
    "dominant", "draft", "drastic", "economic", "efficient", "eliminate", "emerge",
    "enable", "enhance", "enormous", "evaluate", "evolve", "expand", "expert",
    "factor", "feasible", "flexible", "fluctuat", "focus", "foundation", "function",
    "fundamental", "grant", "guarantee", "identical", "ignore", "imply", "include",
    "incorporate", "inevitable", "inherent", "initiative", "intense", "interact",
    "justify", "knowledge", "legitimate", "leisure", "liable", "limit", "logic",
    "marginal", "maximize", "notion", "obligation", "obvious", "occupy",
    "opposite", "originate", "particular", "passive", "percentage", "permanent",
    "permit", "persistent", "phase", "phenomenon", "portion", "positive", "precede",
    "predict", "preliminary", "presume", "prevail", "priority", "proclaim",
    "productive", "profound", "prohibit", "promote", "prompt", "prospect", "prosper",
    "protest", "prove", "provoke", "prudent", "qualify", "quantity", "radical",
    "random", "range", "rational", "react", "realistic", "reasonable", "recover",
    "reflect", "regulate", "reinforce", "reject", "relative", "relax", "release",
    "reliable", "rely", "remove", "render", "replace", "represent", "require",
    "resemble", "reserve", "resist", "resource", "respond", "restore", "restrict",
    "retain", "reveal", "revenue", "reverse", "revise", "reward", "rural",
    "satisfy", "schedule", "secure", "seek", "select", "sensitive", "separate",
    "series", "severe", "shift", "similar", "simulate", "slight", "source",
    "specific", "specify", "stable", "standard", "status", "stimulate", "strategy",
    "structure", "sufficient", "suitable", "supplement", "survive", "symbol",
    "temporary", "tendency", "terminate", "transfer", "transform", "transition",
    "transport", "typical", "undertake", "unify", "unique", "utilize", "valid",
    "vary", "vehicle", "venture", "verify", "viable", "voluntary", "vulnerable",
    "welfare", "widespread",
]

# Level 3 の応用語ルート
LEVEL3_ROOTS = [
    "ambiguous", "analogous", "arbitrary", "articulate", "coincide", "collapse",
    "compensate", "conceive", "condense", "confer", "configure", "consolidate",
    "constraint", "contradict", "conventional", "cumulative", "deficiency", "deplete",
    "deteriorate", "differentiate", "discriminate", "displace", "dispose", "disrupt",
    "distort", "dwell", "elaborate", "embody", "empirical", "endeavor", "enhance",
    "envisage", "equilibrium", "exacerbate", "exemplify", "exert", "expenditure",
    "explicit", "feasible", "formulate", "hierarchy", "homogeneous", "hypothesis",
    "implement", "implication", "implicit", "incentive", "incorporate", "indigenous",
    "infer", "infrastructure", "inherent", "innovation", "institution", "intellectual",
    "intervene", "intrinsic", "investigate", "legislation", "mechanism", "migration",
    "minimize", "notwithstanding", "obsolete", "paradigm", "parameter", "perpetuate",
    "plausible", "predominant", "presume", "prevalence", "profound", "prohibition",
    "proportion", "qualitative", "quantitative", "rationale", "reciprocal",
    "redundancy", "reinforce", "resilience", "scrutinize", "simultaneous", "skeptical",
    "sophisticated", "spontaneous", "subsequent", "subsidiary", "subsidy",
    "substitute", "supplementary", "suppress", "surpass", "sustainable", "tangible",
    "theoretical", "transaction", "transcend", "transient", "underlying",
    "unprecedented", "validate",
]

# Level 4 の発展語ルート（専門性の高い希少語）
LEVEL4_ROOTS = [
    "aberrant", "abstruse", "acquiesce", "admonish", "adroit", "amorphous",
    "anachronism", "anomaly", "antithesis", "apathy", "arbiter", "archaic",
    "assiduous", "autonomy", "banal", "benevolent", "bourgeois", "capricious",
    "catalyst", "circumvent", "cogent", "colloquial", "commensurate", "complacent",
    "concomitant", "conjecture", "connoisseur", "consensus", "conspicuous",
    "contentious", "contingent", "corroborate", "credence", "cursory", "debilitate",
    "deleterious", "demarcation", "denigrate", "derivative", "despot", "dichotomy",
    "diffident", "diligence", "discrepancy", "disparate", "disseminate", "dissident",
    "dogmatic", "ebullient", "eclectic", "efficacy", "elucidate", "emancipate",
    "empiricism", "enigmatic", "ephemeral", "epistemology", "equivocal", "erudite",
    "esoteric", "ethical", "euphemism", "exacerbate", "exigency", "expedient",
    "explicate", "expository", "extraneous", "fallacy", "fastidious", "fecund",
    "felicitous", "fidelity", "florid", "foment", "fortuitous", "garrulous",
    "germane", "gregarious", "hegemony", "heuristic", "hierarchy", "iconoclast",
    "idiosyncrasy", "immutable", "impartial", "imperative", "impermeable",
    "impetus", "implicit", "impute", "inadvertent", "incisive", "incontrovertible",
    "incumbent", "indefatigable", "indolent", "ineffable", "inexorable",
    "ingenuous", "inimical", "innocuous", "insidious", "insinuate", "intractable",
    "intransigent", "intrepid", "inundate", "inure", "inveterate", "irascible",
    "laconic", "lament", "laudable", "lenient", "lethargic", "levity", "limpid",
    "magnanimous", "maverick", "meticulous", "mollify", "mordant", "multifaceted",
    "myriad", "nebulous", "nonchalant", "norms", "obfuscate", "obsequious",
    "obstinate", "obviate", "officious", "onerous", "ostensible", "palliate",
    "paradigm", "parsimonious", "paucity", "pedantic", "penchant", "penurious",
    "perfunctory", "pernicious", "perpetuate", "perspicacious", "pertinent",
    "pious", "pivotal", "placate", "platitude", "plethora", "polemic", "pragmatic",
    "precarious", "precipitous", "predecessor", "predilection", "presage",
    "presumptuous", "pristine", "proclivity", "profligate", "prolific",
    "propensity", "propitiate", "prosaic", "protean", "pugnacious", "pulchritude",
    "quagmire", "quandary", "querulous", "quixotic", "quotidian", "raconteur",
    "rancor", "rapacious", "recalcitrant", "recondite", "redolent", "refulgent",
    "repudiate", "rescind", "resilient", "resplendent", "restive", "reticent",
    "reverent", "rhetoric", "sagacious", "salient", "sanctimonious", "sanguine",
    "sardonic", "scintilla", "scrupulous", "secular", "sedulous", "seminal",
    "serendipity", "solicitous", "solvent", "spurious", "staid", "stigma",
    "stipulate", "strident", "subjugate", "sublime", "subterranean", "succinct",
    "supercilious", "superfluous", "supplant", "surmise", "sycophant", "taciturn",
    "tantamount", "temerity", "tenable", "tenuous", "timorous", "torpid",
    "tractable", "trenchant", "ubiquitous", "unctuous", "undulate", "unequivocal",
    "untenable", "vacillate", "vapid", "veracity", "verbose", "vicissitude",
    "vindicate", "virulent", "viscous", "volatile", "voracious", "whimsical",
]


# ─── ユーティリティ ────────────────────────────────────────────────
def log(msg: str) -> None:
    print(f"[vocab-builder] {time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}", flush=True)


def make_progress_reporter(total: int, interval_sec: int = 180, phase: str = ""):
    """指定間隔（デフォルト3分）ごとに進捗を自動報告するクロージャを返す。
    進捗報告を呼び出すには、返された関数に current (処理済み数) を渡す。
    total に達した際にも必ず最終報告が行われる。
    """
    state = {"last_report": time.time(), "last_current": 0, "last_elapsed": 0.0}

    def report(current: int) -> None:
        now = time.time()
        elapsed = now - state["last_report"]
        done = current >= total
        # 3分経過ごと、または完了時に報告
        if elapsed >= interval_sec or done:
            pct = (current / total * 100.0) if total > 0 else 100.0
            # 直前の報告からの処理速度でETA（残り推定時間）を算出
            delta_current = current - state["last_current"]
            delta_time = elapsed
            if delta_current > 0 and not done:
                rate = delta_current / delta_time  # 語/秒
                remaining = total - current
                eta_sec = remaining / rate if rate > 0 else 0.0
                eta_str = f" | 残り約{eta_sec/60:.1f}分"
            else:
                eta_str = " | 完了"
            log(f"進捗: {current}/{total} 語 ({pct:.1f}%) | 経過{elapsed/60:.1f}分{eta_str} | {phase}")
            state["last_report"] = now
            state["last_current"] = current

    return report


def normalize_word(word: str) -> str:
    """小文字化・前後空白除去・英字のみに正規化"""
    w = word.strip().lower()
    # 複数形の簡易レンマ化
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("es") and len(w) > 4:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    return w


def classify_level(word: str) -> int:
    w = word.lower()
    if w in LEVEL1_WORDS:
        return 1
    if any(w.startswith(r) or r in w for r in LEVEL4_ROOTS):
        return 4
    if any(w.startswith(r) or r in w for r in LEVEL3_ROOTS):
        return 3
    if any(w.startswith(r) or r in w for r in LEVEL2_ROOTS):
        return 2
    # フォールバック: 単語の長さでレベルを判断（短い=基本、長い=発展）
    length = len(w)
    if length <= 4:
        return 1
    if length <= 7:
        return 2
    if length <= 10:
        return 3
    return 4


def classify_topic(word: str) -> str:
    w = word.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in w for k in keywords):
            return topic
    return "General"


# ─── ステップ1: ダウンロード ──────────────────────────────────────
def download_words(max_words: int = 9000) -> list[str]:
    DATA_DIR.mkdir(exist_ok=True)
    words: list[str] = []
    seen: set[str] = set()

    # 1) 高頻度リストを試行
    urls = [GOOGLE_10000_URL] + FALLBACK_URLS
    for url in urls:
        try:
            log(f"ダウンロード: {url}")
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    line = line.strip()
                    if line and line.isalpha() and len(line) <= 20:
                        norm = normalize_word(line)
                        if norm and norm not in seen:
                            seen.add(norm)
                            words.append(norm.title())
                log(f"高頻度リストから {len(words)} 語取得")
                break
        except Exception as e:
            log(f"ダウンロード失敗: {e}")

    # 2) 既存アプリのTOEFL語彙 (VocabularyData.kt から抽出)
    try:
        existing = extract_existing_app_words(APP_VOCABULARY_DATA)
        for w in existing:
            norm = normalize_word(w)
            if norm and norm not in seen:
                seen.add(norm)
                words.append(w)
        log(f"既存TOEFL語彙から追加: {len(existing)} 語")
    except Exception as e:
        log(f"既存語彙の読み込みに失敗: {e}")

    # 3) 上限まで追加（9,000語に達しない場合、Level2/3の代表語を手動追加）
    for w in LEVEL2_ROOTS + LEVEL3_ROOTS + LEVEL4_ROOTS:
        if len(words) >= max_words:
            break
        norm = normalize_word(w)
        if norm and norm not in seen:
            seen.add(norm)
            words.append(w)

    RAW_WORDS_PATH.write_text("\n".join(words), encoding="utf-8")
    log(f"合計 {len(words)} 語を {RAW_WORDS_PATH} に保存")
    return words


def extract_existing_app_words(kotlin_path: Path) -> list[str]:
    """既存 VocabularyData.kt から word = "..." を抽出"""
    if not kotlin_path.exists():
        return []
    text = kotlin_path.read_text(encoding="utf-8")
    return re.findall(r'word = "([^"]+)"', text)


# ─── ステップ2: 処理・分類 ────────────────────────────────────────
def process_words(words: list[str], max_words: int) -> list[dict]:
    data: list[dict] = []
    for i, word in enumerate(words[:max_words]):
        item = {
            "id": i + 1,
            "word": word,
            "wordUk": word,          # デフォルトは米英同一スペル
            "phoneticUk": "",
            "meaning": "",
            "meaningEn": "",
            "synonyms": "",
            "example": "",
            "level": classify_level(word),
            "topic": classify_topic(word),
            "source_list": "google-10000" if i < 10000 else "custom",
        }
        data.append(item)
    WORDS_JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"処理後 {len(data)} 語を {WORDS_JSON_PATH} に保存")
    return data


# ─── ステップ3: AI補完 ─────────────────────────────────────────────
def load_enriched() -> dict[str, dict]:
    if ENRICHED_JSON_PATH.exists():
        raw = json.loads(ENRICHED_JSON_PATH.read_text(encoding="utf-8"))
        result = {}
        for item in raw:
            w = (item.get("word") or "").lower()
            if w:
                # AIレスポンス形式に統一（中途保存との互換性確保）
                result[w] = {
                    "word": item.get("word", ""),
                    # 既存データにUK情報が無い場合は米スペル・空発音をデフォルト設定
                    "wordUk": item.get("wordUk", item.get("word", w)),
                    "phoneticUk": item.get("phoneticUk", ""),
                    "meaning_jp": item.get("meaning_jp", item.get("meaning", "")),
                    "meaning_en": item.get("meaning_en", item.get("meaningEn", "")),
                    "synonyms": item.get("synonyms", ""),
                    "collocations": item.get("collocations", ""),
                    "example": item.get("example", ""),
                }
        return result
    return {}


def save_enriched(items: list[dict]) -> None:
    """全データを保存"""
    ENRICHED_JSON_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def save_enriched_map(enriched_map: dict[str, dict]) -> None:
    """各バッチ完了後に部分保存する（途中停止・再開対応）"""
    ENRICHED_JSON_PATH.write_text(
        json.dumps(list(enriched_map.values()), ensure_ascii=False, indent=1),
        encoding="utf-8"
    )
    log(f"途中保存: {len(enriched_map)} 語分を {ENRICHED_JSON_PATH} に保存")


def load_existing_enriched() -> dict[str, dict]:
    """アプリの既存語彙（DatabaseSeeder.kt 100語 + VocabularyData.kt 900語）から
    word -> {meaning, meaningEn, synonyms, example} を抽出する。"""
    existing: dict[str, dict] = {}

    # DatabaseSeeder.kt 内の insertVocabulary エントリ
    seeder_path = BASE_DIR.parent.parent / "app" / "src" / "main" / "java" \
        / "com" / "gachiguild" / "gachitoefl" / "data" / "local" / "DatabaseSeeder.kt"
    if seeder_path.exists():
        text = seeder_path.read_text(encoding="utf-8")
        # VocabularyEntity( ... ) を抽出
        for m in re.finditer(r'insertVocabulary\((VocabularyEntity\([^)]*\))\)', text):
            body = m.group(1)
            word = re.search(r'word = "([^"]*)"', body)
            meaning = re.search(r'meaning = "([^"]*)"', body)
            meaning_en = re.search(r'meaningEn = "([^"]*)"', body)
            synonyms = re.search(r'synonyms = "([^"]*)"', body)
            example = re.search(r'example = "([^"]*)"', body)
            if word:
                existing[word.group(1).lower()] = {
                    "word": word.group(1),
                    # 既存KotlinデータにはUK情報が無いため、米スペルをデフォルト設定
                    "wordUk": word.group(1),
                    "phoneticUk": "",
                    "meaning_jp": meaning.group(1) if meaning else "",
                    "meaning_en": meaning_en.group(1) if meaning_en else "",
                    "synonyms": synonyms.group(1) if synonyms else "",
                    "example": example.group(1) if example else "",
                }

    # VocabularyData.kt 内のエントリ（同様の形式）
    vocab_data_path = BASE_DIR.parent.parent / "app" / "src" / "main" / "java" \
        / "com" / "gachiguild" / "gachitoefl" / "data" / "local" / "VocabularyData.kt"
    if vocab_data_path.exists():
        text = vocab_data_path.read_text(encoding="utf-8")
        for m in re.finditer(r'VocabularyEntity\(([^)]*)\)', text):
            body = m.group(1)
            word = re.search(r'word = "([^"]*)"', body)
            word_uk = re.search(r'wordUk = "([^"]*)"', body)
            phonetic_uk = re.search(r'phoneticUk = "([^"]*)"', body)
            meaning = re.search(r'meaning = "([^"]*)"', body)
            meaning_en = re.search(r'meaningEn = "([^"]*)"', body)
            synonyms = re.search(r'synonyms = "([^"]*)"', body)
            example = re.search(r'example = "([^"]*)"', body)
            if word:
                existing[word.group(1).lower()] = {
                    "word": word.group(1),
                    "wordUk": word_uk.group(1) if word_uk else word.group(1),
                    "phoneticUk": phonetic_uk.group(1) if phonetic_uk else "",
                    "meaning_jp": meaning.group(1) if meaning else "",
                    "meaning_en": meaning_en.group(1) if meaning_en else "",
                    "synonyms": synonyms.group(1) if synonyms else "",
                    "example": example.group(1) if example else "",
                }

    log(f"既存語彙データから {len(existing)} 語を抽出")
    return existing


def extract_json_array(text: str) -> list | None:
    """DeepSeekのレスポンスからJSON配列を堅牢に抽出する。
    マークダウンコードフェンス・末尾カンマ・制御文字などの不整合に対応。"""
    # 1) マークダウンのコードフェンスを除去
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```\s*$", "", text, flags=re.MULTILINE)

    # 2) 最初の '[' を起点に、文字列リテラルを考慮しながら対応する ']' を走査
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
    raw = re.sub(r",\s*([\]}])", r"\1", raw)                 # 末尾カンマ除去
    raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", raw)   # 制御文字除去
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # シングルクォート表記への簡易フォールバック
        fixed = re.sub(r"(['\"])([a-zA-Z_]+)\1\s*:", r'"\2":', raw)
        fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return None


# ─── 発音・表記対応 ───────────────────────────────────────────────
# TOEFL向けの正本は米国英語を優先し、wordUk/phoneticUkには比較用のUK情報を保持する。
# key = 米国英語 (US), value = 英国英語 (UK)
US_TO_UK_MAP = {
    "analyze": "analyse",
    "analyzed": "analysed",
    "analyzes": "analyses",
    "analyzing": "analysing",
    "color": "colour",
    "colors": "colours",
    "colored": "coloured",
    "colorful": "colourful",
    "center": "centre",
    "centers": "centres",
    "organize": "organise",
    "organized": "organised",
    "organizes": "organises",
    "organizing": "organising",
    "recognize": "recognise",
    "recognized": "recognised",
    "recognizes": "recognises",
    "recognizing": "recognising",
    "realize": "realise",
    "realized": "realised",
    "realizes": "realises",
    "realizing": "realising",
    "apartment": "flat",
    "apartments": "flats",
    "vacation": "holiday",
    "vacations": "holidays",
    "elevator": "lift",
    "elevators": "lifts",
    "truck": "lorry",
    "trucks": "lorries",
    "sidewalk": "pavement",
    "sidewalks": "pavements",
    "gasoline": "petrol",
    "cookie": "biscuit",
    "cookies": "biscuits",
    "fall": "autumn",
    "movie": "film",
    "movies": "films",
    "favorite": "favourite",
    "favorites": "favourites",
    "behavior": "behaviour",
    "labor": "labour",
    "neighbor": "neighbour",
    "neighborhood": "neighbourhood",
    "honor": "honour",
    "humor": "humour",
    "theater": "theatre",
    "theaters": "theatres",
    "meter": "metre",
    "meters": "metres",
    "traveling": "travelling",
    "traveled": "travelled",
    "canceled": "cancelled",
    "counselor": "counsellor",
    "defense": "defence",
    "license": "licence",
    "offense": "offence",
    "practiced": "practised",
    "practice": "practise",
    "program": "programme",
    "programs": "programmes",
    "odor": "odour",
    "savory": "savoury",
    "tire": "tyre",
    "tires": "tyres",
}


def uk_spelling(word: str) -> str:
    """米国英語の単語を英国英語のスペルに変換する（マッピングに無い場合は同一文字列）"""
    w = word.strip()
    lowered = w.lower()
    if lowered in US_TO_UK_MAP:
        mapped = US_TO_UK_MAP[lowered]
        # 先頭大文字を維持
        if w[:1].isupper():
            return mapped[:1].upper() + mapped[1:]
        return mapped
    return w


def apply_uk_synonyms(word: str, synonyms: str) -> str:
    """類義語リストにUK表現が含まれるように調整する。
    - 元の類義語に米英どちらの表現も含まれていない場合はUK表現を追加
    - 米国スペルの類義語が含まれる場合、UKスペルを追記
    """
    if not synonyms.strip():
        return synonyms
    uk = uk_spelling(word)
    items = [s.strip() for s in synonyms.split(",") if s.strip()]
    lowered = [s.lower() for s in items]

    # 米英で単語自体が異なる場合（例: apartment→flat）
    if uk.lower() != word.lower():
        # UK表現が既に類義語に含まれているか
        has_uk = any(s.lower() == uk.lower() for s in items)
        if not has_uk:
            # 元の単語（US）のUK対応表現が他にもあるか（例: 'apartment, condo' に 'flat' を追加）
            items.append(uk)
        return ", ".join(items)

    # スペル差のみの場合（例: color→colour, analyze→analyse）
    uk_forms = {uk_spelling(s) for s in items if uk_spelling(s) != s}
    missing_uk = [uk_form for uk_form in uk_forms if uk_form.lower() not in lowered]
    if missing_uk:
        # 元の類義語にUKスペルが含まれていない場合、末尾に "(UK: xxx)" 形式の注記を追加
        return synonyms + f" (UK: {', '.join(sorted(missing_uk))})"
    return synonyms


def apply_uk_example(word: str, example: str) -> str:
    """例文にUK表現が含まれるように調整する。
    - 米英で単語自体が異なる場合（例: apartment→flat）、例文にUK表現がなければ注記を追加
    - スペル差のみの場合（例: color→colour）、例文内にUSスペルがあればUKスペルに置換
    """
    if not example.strip():
        return example
    uk = uk_spelling(word)
    lowered_example = example.lower()

    # 米英で単語自体が異なる場合（例: apartment→flat）
    if uk.lower() != word.lower():
        if uk.lower() in lowered_example:
            return example  # 既にUK表現が含まれている
        # UK表現が例文に無い場合、注記を末尾に追加
        return f"{example} (UK: {uk})"

    # スペル差のみの場合（例: color→colour）: 例文中のUSスペルをUKスペルに置換
    word_us = word.lower()
    word_uk = uk.lower()
    if word_us in lowered_example and word_uk != word_us:
        # 単語境界を考慮した置換
        pattern = re.compile(rf"\b{re.escape(word_us)}\b", re.IGNORECASE)
        return pattern.sub(uk, example)
    return example


def is_complete_entry(e: dict, require_uk: bool = False) -> bool:
    """AI補完が完了しているエントリか（日本語訳・英語定義・例文・コロケーションが揃っている）"""
    jp = e.get("meaning_jp") or e.get("meaning") or ""
    en = e.get("meaning_en") or e.get("meaningEn") or ""
    ex = e.get("example") or ""
    col = e.get("collocations") or ""
    uk = e.get("wordUk") or ""
    ph = e.get("phoneticUk") or ""
    if require_uk:
        return bool(jp.strip() and en.strip() and ex.strip() and col.strip()
                    and uk.strip() and ph.strip())
    return bool(jp.strip() and en.strip() and ex.strip() and col.strip())


def enrich_with_ai(items: list[dict], batch_size: int = 50) -> list[dict]:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "")

    # 既存補完データ+アプリ既存語彙をベース設定（共通処理）
    enriched_map = load_enriched()
    for key, val in load_existing_enriched().items():
        if key not in enriched_map:
            enriched_map[key] = val

    if not api_key or api_key == "sk-xxxx":
        log("APIキー未設定。既存データのみを適用します。")
        result = []
        for it in items:
            e = enriched_map.get(it["word"].lower(), {})
            result.append({**it,
                          "wordUk": e.get("wordUk", it.get("word", "")),
                          "phoneticUk": e.get("phoneticUk", ""),
                          "meaning": e.get("meaning_jp", ""),
                          "meaningEn": e.get("meaning_en", ""),
                          "synonyms": apply_uk_synonyms(it.get("word", ""), e.get("synonyms", "")),
                          "collocations": e.get("collocations", ""),
                          "example": apply_uk_example(it.get("word", ""), e.get("example", ""))})
        save_enriched(result)
        return result

    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=120.0,  # 接続・読み取りタイムアウト（フリーズ防止）
        max_retries=3,
    )
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # 補完データが不完全な単語のみを対象にする（途中保存済みでも再走査で検出できる）
    pending = [it for it in items if not is_complete_entry(enriched_map.get(it["word"].lower(), {}))]
    # 既に意味・例文は揃っているが collocations が未生成の語も対象に含める
    pending += [
        it for it in items
        if it not in pending
        and not (enriched_map.get(it["word"].lower(), {}).get("collocations") or "").strip()
    ]
    # UK情報（wordUk・phoneticUk）が未取得の語も対象に含める（再エンリッチでUK対応）
    pending += [
        it for it in items
        if it not in pending
        and not is_complete_entry(enriched_map.get(it["word"].lower(), {}), require_uk=True)
    ]
    # 重複除去（元の順序を維持）
    seen = set()
    deduped = []
    for it in pending:
        key = it["word"].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(it)
    pending = deduped

    log(f"未補完: {len(pending)} 語 / 合計: {len(items)} 語")
    if not pending:
        log("すべて補完済みです。")
        return items

    # 3分ごとに進捗を自動報告するレポーター
    report_progress = make_progress_reporter(len(pending), interval_sec=180, phase="AI補完")
    batch_start_time = time.time()

    for start in range(0, len(pending), batch_size):
        # 3分ごとの進捗報告（経過時間に基づき自動出力）
        report_progress(start)
        batch = pending[start:start + batch_size]
        words_str = ", ".join(f'"{it["word"]}"' for it in batch)
        level_str = ", ".join(str(it["level"]) for it in batch)
        topic_str = ", ".join(f'"{it["topic"]}"' for it in batch)

        prompt = f"""以下のTOEFL英単語について、各項目をJSON配列で返してください。
単語: [{words_str}]
レベル(1=基礎,2=標準,3=応用,4=発展): [{level_str}]
トピック: [{topic_str}]

出力形式（単語ごとに1オブジェクト）:
[
  {{
    "word": "単語",
    "wordUk": "比較用のイギリス英語スペル（米英で同じ場合は同じ単語文字列。例: 'analyze'→'analyse', 'color'→'colour'）",
    "phoneticUk": "イギリス英語の発音記号（IPA形式。例: 'əˈpɑːt.mənt', 'ˈhɒl.ə.deɪ'。不明な場合は空文字）",
    "meaning_jp": "自然な日本語訳（TOEFLの大学・学術文脈で最も一般的な意味）",
    "meaning_en": "英語での簡潔な定義",
    "synonyms": "類義語をカンマ区切りで3-5個。TOEFLで使いやすい米国英語を優先してください",
    "collocations": "自然な英語の連語（コロケーション）をカンマ区切りで3-5個。TOEFLの講義・キャンパス会話・学術ライティングで使える組み合わせ。例: 'analyze data, analyze the results, carefully analyze, analyze in detail'",
    "example": "TOEFLの講義・キャンパス会話・学術ライティングで使える自然な例文。米国英語を優先してください"
  }}
]

必ず有効なJSON配列のみを返してください。"""
        success = False
        for attempt in range(2):
            try:
                log(f"AI補完中（試行{attempt + 1}）: {start + len(batch)} / {len(pending)} 語 | 経過{time.time()-batch_start_time:.0f}秒")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=8000,
                )
                content = resp.choices[0].message.content or ""
                # 堅牢なJSON抽出（コードフェンス・末尾カンマ・制御文字に対応）
                enriched = extract_json_array(content)
                if enriched is None:
                    log(f"JSON抽出失敗: {content[:200]}")
                    continue
                for e in enriched:
                    word_key = (e.get("word") or "").lower()
                    if word_key:
                        e["word"] = word_key
                        # UKスペルが未返却の場合は米スペル（=既存word）をデフォルトで設定
                        if not (e.get("wordUk") or "").strip():
                            e["wordUk"] = e.get("word", word_key)
                        if not (e.get("phoneticUk") or "").strip():
                            e["phoneticUk"] = ""
                        # 既存エントリのフィールドを保持しつつ各フィールドをマージ
                        if word_key in enriched_map:
                            merged = dict(enriched_map[word_key])
                            for field in ("meaning_jp", "meaning_en", "synonyms", "example",
                                          "wordUk", "phoneticUk"):
                                if not (e.get(field) or "").strip():
                                    e[field] = merged.get(field, "")
                        enriched_map[word_key] = e
                # 各バッチ完了後に途中保存（途中停止・再開対応）
                save_enriched_map(enriched_map)
                success = True
                break
            except Exception as e:
                log(f"APIエラー: {e}（バッチ {start}-{start+len(batch)} をスキップ）")
                if attempt == 0:
                    time.sleep(2)
        if not success:
            save_enriched_map(enriched_map)

        # レート制限回避（APIの rate limit 対策）
        time.sleep(1)

    # 最終進捗報告（100% 完了を必ず出力）
    report_progress(len(pending))

    # 元の順序で結合
    result = []
    for it in items:
        e = enriched_map.get(it["word"].lower(), {})
        result.append({
            **it,
            "wordUk": e.get("wordUk", it.get("word", "")),
            "phoneticUk": e.get("phoneticUk", ""),
            "meaning": e.get("meaning_jp", ""),
            "meaningEn": e.get("meaning_en", ""),
            "synonyms": apply_uk_synonyms(it.get("word", ""), e.get("synonyms", "")),
            "collocations": e.get("collocations", ""),
            "example": apply_uk_example(it.get("word", ""), e.get("example", "")),
        })
    save_enriched(result)
    log(f"AI補完完了: {len(result)} 語を {ENRICHED_JSON_PATH} に保存")
    return result


# ─── ステップ4: Kotlinエクスポート ───────────────────────────────
def export_json(items: list[dict]) -> None:
    """assets/vocabulary.json を出力（アプリの大量語彙読み込み用）"""
    APP_ASSETS_JSON.parent.mkdir(parents=True, exist_ok=True)
    APP_ASSETS_JSON.write_text(
        json.dumps(items, ensure_ascii=False, indent=1),
        encoding="utf-8"
    )
    log(f"JSON出力: {APP_ASSETS_JSON}")


def export_kotlin(items: list[dict]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    export_json(items)
    lines = [
        "package com.gachiguild.gachitoefl.data.local",
        "",
        "import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity",
        "",
        "/**",
        " * TOEFL語彙データ（自動生成: tools/vocabulary-builder/build_vocabulary.py）",
        f" * 収録語数: {len(items)}語",
        " * NGSL/NAWL/高頻度語リスト + AI補完（日本語訳・例文・類義語）",
        " */",
        "val VocabularyBatch2: List<VocabularyEntity> = listOf(",
    ]

    for it in items:
        word = escape_kotlin(it["word"])
        word_uk = escape_kotlin(it.get("wordUk", it.get("word", "")))
        phonetic_uk = escape_kotlin(it.get("phoneticUk", ""))
        meaning = escape_kotlin(it.get("meaning", ""))
        meaning_en = escape_kotlin(it.get("meaningEn", ""))
        synonyms = escape_kotlin(it.get("synonyms", ""))
        collocations = escape_kotlin(it.get("collocations", ""))
        example = escape_kotlin(it.get("example", ""))
        level = it.get("level", 2)
        topic = it.get("topic", "General")
        lines.append(
            f'    VocabularyEntity(id = {it["id"]}, word = "{word}", '
            f'wordUk = "{word_uk}", phoneticUk = "{phonetic_uk}", '
            f'meaning = "{meaning}", meaningEn = "{meaning_en}", '
            f'synonyms = "{synonyms}", collocations = "{collocations}", '
            f'example = "{example}", '
            f'level = {level}, topic = "{topic}"),'
        )

    lines.append(")")
    output = "\n".join(lines) + "\n"
    KOTLIN_OUTPUT_PATH.write_text(output, encoding="utf-8")

    # アプリの VocabularyData.kt は空スタブのまま維持する。
    # （アプリは assets/vocabulary.json を VocabularySeeder が読み込む JSON アセット方式のため）
    log(f"Kotlin出力（リファレンス用）: {KOTLIN_OUTPUT_PATH}")
    log(f"アプリ用JSON: {APP_ASSETS_JSON} — VocabularySeeder が assets/vocabulary.json として読み込む")


def escape_kotlin(s: str) -> str:
    return (s.replace("\\", "\\\\")
             .replace('"', '\\"')
             .replace("\n", " ")
             .replace("\r", ""))


# ─── エントリポイント ──────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="TOEFL Vocabulary Builder")
    parser.add_argument("--all", action="store_true", help="全パイプラインを実行")
    parser.add_argument("--download", action="store_true", help="単語リスト取得のみ")
    parser.add_argument("--process", action="store_true", help="分類・処理のみ")
    parser.add_argument("--enrich", action="store_true", help="AI補完のみ")
    parser.add_argument("--export", action="store_true", help="Kotlin出力のみ")
    parser.add_argument("--max-words", type=int, default=9000, help="最大単語数")
    parser.add_argument("--batch-size", type=int, default=50, help="AI補完のバッチサイズ")
    parser.add_argument("--skip-ai", action="store_true", help="AI補完をスキップ（テスト用）")
    args = parser.parse_args()

    load_dotenv()
    max_words = args.max_words

    if args.all or args.download:
        words = download_words(max_words)
        items = process_words(words, max_words)
    elif args.process:
        if not RAW_WORDS_PATH.exists():
            words = download_words(max_words)
        else:
            words = RAW_WORDS_PATH.read_text(encoding="utf-8").splitlines()
        items = process_words(words, max_words)
    else:
        # 既存データからロード
        if WORDS_JSON_PATH.exists():
            items = json.loads(WORDS_JSON_PATH.read_text(encoding="utf-8"))
            # enriched.json があれば補完データをマージ（--export 単体実行でも反映）
            enriched_map = load_enriched()
            if enriched_map:
                merged = []
                for it in items:
                    e = enriched_map.get(it["word"].lower(), {})
                    merged.append({
                        **it,
                        "wordUk": e.get("wordUk", it.get("word", "")),
                        "phoneticUk": e.get("phoneticUk", ""),
                        "meaning": e.get("meaning_jp", ""),
                        "meaningEn": e.get("meaning_en", ""),
                        "synonyms": apply_uk_synonyms(it.get("word", ""), e.get("synonyms", "")),
                        "collocations": e.get("collocations", ""),
                        "example": apply_uk_example(it.get("word", ""), e.get("example", "")),
                    })
                items = merged
                log(f"enriched.json から補完データをマージ（{len(merged)} 語）")
        else:
            log("処理済みデータがありません。--download または --process を先に実行してください。")
            sys.exit(1)

    if (args.all or args.enrich) and not args.skip_ai:
        items = enrich_with_ai(items, args.batch_size)

    if args.all or args.export:
        export_kotlin(items)
        log("完了!")

    if args.download:
        log("ダウンロード完了。--enrich でAI補完、--export でKotlin出力を実行できます。")


if __name__ == "__main__":
    main()
