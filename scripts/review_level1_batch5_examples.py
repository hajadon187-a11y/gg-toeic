#!/usr/bin/env python3
"""Review the fifth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "foot": "新しいオフィスは丘のふもとにある。",
    "effort": "チームは締め切りに間に合わせるため大いに努力した。",
    "attention": "安全に関する指示に注意を払ってください。",
    "check": "チームは締め切り前に在庫を確認する。",
    "complete": "金曜までにフォームを記入してください。",
    "lie": "書類はマネージャーの机の上に置かれている。",
    "pick": "受付から書類を受け取ってください。",
    "personal": "私物はロッカーに保管してください。",
    "ground": "建設作業員は新しい倉庫の地面を整えた。",
    "animal": "会社は地元の動物保護施設に寄付した。",
    "arrive": "出荷品はシステム更新後に到着する可能性がある。",
    "patient": "問題が解決する間、顧客は辛抱強く待った。",
    "current": "契約書の最新版を使用してください。",
    "century": "その会社は1世紀以上にわたって営業している。",
    "exist": "現在のシステムには複数の問題が存在する可能性がある。",
    "fight": "会社は市場シェアを維持するため奮闘している。",
    "leader": "チームリーダーは改訂版のスケジュールを承認した。",
    "fine": "会社は規則違反の罰金を支払った。",
    "former": "元マネージャーは現在、競合会社で働いている。",
    "contact": "遅延について仕入先に連絡してください。",
    "particularly": "新サービスは中小企業に特に人気がある。",
    "prepare": "チームは締め切り前に報告書を準備する。",
    "discuss": "チームは締め切り前に提案について話し合う。",
    "piece": "新しい支店に機器を1台送ってください。",
    "finish": "チームは締め切り前にプロジェクトを終える。",
    "apply": "金曜までにその職に応募してください。",
    "fire": "点検中に火災報知器が鳴った。",
    "compare": "決定する前に2つの見積書を比較してください。",
    "court": "会社は裁判になる前にその訴訟を解決した。",
    "police": "警察はオフィスへの侵入事件を捜査した。",
    "poor": "計画不足が配送の遅延を引き起こした。",
    "laugh": "発表者が冗談を言ったとき、チームは笑った。",
    "arm": "その椅子には調節可能な肘掛けがある。",
    "heart": "提案の核心はコスト削減の計画です。",
    "employee": "従業員は期限内に経費報告書を提出した。",
    "manage": "マネージャーは最初から最後までプロジェクトを管理する。",
    "bank": "銀行は会社の融資を承認した。",
    "firm": "法律事務所は契約書を確認した。",
    "cell": "技術者は機器の電池を交換した。",
    "article": "マネージャーは社内報の記事を書いた。",
    "fast": "仕入先は迅速な配送を提供している。",
    "attack": "マネージャーは社内ネットワークへの攻撃について話し合った。",
    "foreign": "会社には複数の海外顧客がいる。",
    "feature": "新しいソフトウェアには便利な検索機能がある。",
    "factor": "送料は決定における大きな要因だった。",
    "affect": "遅延は顧客満足度に影響する可能性がある。",
    "drop": "仕入先は配送料を下げることに同意した。",
    "official": "会社は公式声明を発表した。",
    "financial": "銀行は中小企業に財務アドバイスを提供している。",
    "miss": "締め切りを逃さないでください。",
    "art": "オフィスには地元の芸術家の作品が展示されている。",
    "campaign": "会社は新サービスを宣伝するキャンペーンを開始した。",
    "pause": "発表者は質問に答えるため一時中断した。",
    "everyone": "部署の全員が会議に出席した。",
    "forget": "領収書を添付するのを忘れないでください。",
    "page": "契約書の最後のページに署名してください。",
    "drink": "来訪者に飲み物を勧めてください。",
    "opinion": "マネージャーは提案について私の意見を求めた。",
    "park": "来訪者はオフィスの裏に駐車できます。",
    "key": "プロジェクト成功の鍵は明確なコミュニケーションです。",
    "inside": "請求書が入っているか、荷物の中を確認してください。",
    "manager": "マネージャーは発注書を承認した。",
    "international": "会社には国際的な顧客基盤がある。",
    "contain": "このハンドブックのページには会社の休日の日付が記載されている。",
    "notice": "顧客は請求書の間違いに気づいた。",
    "nature": "その苦情の性質上、早急な対応が必要だ。",
    "myself": "私自身が署名する前に契約書を確認した。",
    "exactly": "請求書の合計はちょうど500ドルです。",
    "plant": "その工場は自動車産業向けの部品を生産している。",
    "paint": "会社は来週末にオフィスの壁を塗装する。",
    "necessary": "マネージャーは必要な修理を承認した。",
    "growth": "会社は今年、力強い成長を遂げた。",
    "evening": "夜勤が顧客サポートを担当する。",
    "influence": "顧客のフィードバックが製品設計に影響を与えた。",
    "catch": "遅延後、チームは注文に追いつかなければならない。",
    "attempt": "チームは仕入先への連絡を試みた。",
    "medium": "社内連絡にはメールが好ましい手段です。",
    "average": "平均配送時間は3日です。",
    "management": "経営陣は予算を承認した。",
    "character": "パスワードの文字数制限は20文字です。",
    "bed": "ホテルは出張中の従業員のためにベッドを予約した。",
    "hit": "嵐が地域を直撃し、配送が遅れた。",
    "establish": "会社は新しい支店を設立する予定だ。",
    "indeed": "結果は実際、予想を上回った。",
    "final": "契約書の最終版が準備できた。",
    "economy": "最新の報告書は経済が地域企業に与えた影響を説明している。",
    "fit": "新しい機器は保管室に収まる。",
    "guy": "受付の男性が来訪者用バッジを渡してくれた。",
    "function": "そのソフトウェアには経費を追跡する機能がある。",
    "image": "会社はウェブサイトの画像を更新した。",
    "behavior": "マネージャーは従業員の不適切な行動に対処した。",
    "addition": "さらに、会社は無料配送を提供している。",
    "determine": "監査によって数値が正確かどうかが判断される。",
    "population": "その都市の人口は過去10年間で増加した。",
    "fail": "更新しないとシステムが故障する可能性がある。",
    "environment": "報告書は環境と周辺地域への影響を説明した。",
    "contract": "両社は条件を確認した後、契約書に署名した。",
    "player": "メディアプレーヤーは研修動画を再生できる。",
    "comment": "マネージャーは報告書にコメントを追加した。",
    "enter": "チームは締め切り前にデータを入力する。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][400:500]
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
    print(f"reviewed 500+ Japanese examples batch 5: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
