#!/usr/bin/env python3
"""Review the twelfth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "liberal": "会社は柔軟な在宅勤務方針を採用している。",
    "lake": "湖を見下ろすホテルはビジネス会議を開催している。",
    "competitive": "会社は競争力のある価格を提示している。",
    "hi": "こんにちは。改訂版の請求書を送ってもらえますか。",
    "habit": "毎朝在庫を確認することは有用な習慣だ。",
    "disk": "技術者はサーバーのディスクを交換した。",
    "core": "顧客サービスは会社の成功の中核だ。",
    "emotional": "その広告は顧客との感情的なつながりを生み出す。",
    "aircraft": "航空機は無事に空港へ到着した。",
    "existence": "報告書は請求ミスの存在を確認している。",
    "bone": "診療所は骨の検査用機器を注文した。",
    "appointment": "顧客は営業担当者との予約を確認した。",
    "emphasize": "マネージャーは安全の重要性を強調した。",
    "effectively": "新しいシステムは注文をより効率的に処理する。",
    "elsewhere": "紛失したファイルは別の場所に保管されている可能性がある。",
    "bother": "会議中に顧客の邪魔をしないでください。",
    "initiative": "会社は廃棄物削減の取り組みを開始した。",
    "diet": "食堂はさまざまな食事上の要望に対応した料理を提供している。",
    "gray": "オフィスには灰色の壁と現代的な家具がある。",
    "complicate": "遅延は配送スケジュールを複雑にする可能性がある。",
    "discipline": "マネージャーは規律と時間厳守を重視している。",
    "disappoint": "遅延は顧客を失望させた。",
    "boss": "上司は改訂版のスケジュールを承認した。",
    "assumption": "その計画は売上が増加するという前提に基づいている。",
    "freeze": "会社は景気低迷中、採用を凍結した。",
    "extreme": "その機器は極端な温度では動作しない。",
    "forth": "その計画は契約書に示されている。",
    "coat": "従業員は倉庫の点検中にコートを着ていた。",
    "democracy": "会社は民主的な意思決定を奨励している。",
    "lucky": "出荷品が嵐の前に到着して幸運だった。",
    "crash": "プレゼンテーション中にコンピューターが故障した。",
    "concentration": "騒音が従業員の集中力に影響した。",
    "implication": "報告書は新しい方針の影響について論じている。",
    "deserve": "その従業員は改善に対する評価に値する。",
    "defend": "会社は自社の商標を守る。",
    "classic": "そのホテルはクラシックなデザインを採用している。",
    "king": "会社は新製品をKingと名付けた。",
    "interaction": "研修は部署間の交流を促す。",
    "collapse": "システム更新後に市場が崩壊する可能性がある。",
    "borrow": "会社は倉庫を拡張するために資金を借りた。",
    "fundamental": "信頼は提携を成功させる基本条件だ。",
    "dish": "そのレストランは人気の郷土料理を出した。",
    "abroad": "会社は海外にオフィスを持っている。",
    "capable": "そのシステムは大量注文を処理できる。",
    "defeat": "チームは主な競合相手を破った。",
    "enhance": "アップグレードによりシステムの安全性が高まる。",
    "emergency": "会社は悪天候に備えた緊急計画を持っている。",
    "distinguish": "ソフトウェアは有効な入力と無効な入力を区別する。",
    "breast": "診療所は乳がん検診を提供している。",
    "cope": "チームは注文の急増に対処した。",
    "approximately": "プロジェクトには約3か月かかる。",
    "accommodation": "アシスタントは訪問する技術者の宿泊先を手配した。",
    "highlight": "報告書は遅延の主な原因を強調している。",
    "climate": "報告書は気候と周辺地域への影響を説明した。",
    "exception": "その方針は例外なく全従業員に適用される。",
    "corporation": "その企業はシンガポールに地域オフィスを開設した。",
    "chip": "技術責任者はコンピューターチップが電気信号を処理する仕組みを説明した。",
    "encounter": "チームは設置中に問題に遭遇した。",
    "brown": "オフィスの椅子は茶色です。",
    "breathe": "従業員は安全訓練中、ゆっくり呼吸するよう指示された。",
    "excuse": "締め切りを逃すことに言い訳はできない。",
    "confuse": "似たラベルが倉庫スタッフを混乱させた。",
    "beauty": "その場所の自然の美しさが訪問者を引き付けた。",
    "install": "技術者は新しいソフトウェアをインストールする。",
    "calculate": "会計担当者は研修費の合計を計算した。",
    "creation": "新しい雇用の創出が地域社会に利益をもたらした。",
    "luck": "運よく、技術者はなくした鍵を見つけた。",
    "illness": "診療所は患者の医療記録に病気を記録した。",
    "journalist": "ジャーナリストはインタビューを公表する前に情報源を確認した。",
    "advertisement": "その広告はビジネス誌に掲載された。",
    "consistent": "会社は一貫した顧客サービスを提供している。",
    "aside": "破損した製品を脇に置いてください。",
    "comfort": "ホテルは出張者に快適な客室を提供している。",
    "gene": "研究チームは病気に関連する遺伝子を調べた。",
    "criteria": "採用基準は申請フォームに記載されている。",
    "integrate": "新入社員はすぐにチームに溶け込む。",
    "criticism": "マネージャーは批判を受け入れ、計画を修正した。",
    "convention": "会社は業界会議で製品を展示した。",
    "bet": "マネージャーは未検証の計画に会社の資金を賭けようとはしなかった。",
    "calm": "マネージャーは緊急時にも冷静だった。",
    "abandon": "会社は古いシステムを廃止した。",
    "examination": "その職には健康診断が必要です。",
    "efficient": "新しい手順は効率的で従いやすい。",
    "delight": "その贈り物は訪問中の顧客を喜ばせた。",
    "lean": "会社は無駄を省く生産方式を採用した。",
    "dramatic": "会社はオンライン売上で著しい成長を遂げた。",
    "differ": "2つのモデルは価格と容量が異なる。",
    "grateful": "継続的なご支援に感謝しています。",
    "bike": "従業員は近隣のオフィス間の移動に自転車を使える。",
    "distribute": "会社は各支店に資料を配布する。",
    "intellectual": "会社は従業員の知的好奇心を奨励している。",
    "derive": "報告書は公式データから数値を導き出している。",
    "crucial": "明確なコミュニケーションはプロジェクトの成功に不可欠だ。",
    "crop": "嵐の後、農場は作物の一部を失った。",
    "interpretation": "契約書の解釈について弁護士が話し合った。",
    "gentleman": "受付の男性が来訪者用バッジを渡してくれた。",
    "drama": "広告のドラマ性が世間の注目を集めた。",
    "landscape": "新施設周辺の景観は美しい。",
    "fault": "技術者は電気システムの故障を発見した。",
    "exhibit": "会社は会議で最新ソフトウェアを展示する。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][1100:1200]
    assert {str(item["word"]).casefold() for item in level_rows} == set(JA)
    changed = 0
    for item in level_rows:
        key = f"builtin:{item['id']}"
        example = translations.setdefault(key, {}).setdefault("example", {})
        source = str(item["example"]).strip()
        if example.get("source") != source:
            example["source"] = source
            changed += 1
        if example.get("en") != source:
            example["en"] = source
            changed += 1
        value = JA[str(item["word"]).casefold()]
        if example.get("ja") != value:
            example["ja"] = value
            changed += 1
    VOCAB_PATH.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    PHRASE_PATH.write_text(json.dumps(phrase_root, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"reviewed 500+ Japanese examples batch 12: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
