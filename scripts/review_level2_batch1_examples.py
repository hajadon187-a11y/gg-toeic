#!/usr/bin/env python3
"""Review the first 100 TOEIC 600+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "say": "マネージャーは結果が最終確定したと言った。",
    "think": "提案を承認する前によく考えてください。",
    "time": "プロジェクトは予定どおり完了した。",
    "see": "顧客は会議で結果を確認する。",
    "year": "会社は昨年、事業を拡大した。",
    "take": "技術者は機器を修理室へ運んだ。",
    "well": "新しいシステムは古い機器でも問題なく動作する。",
    "very": "新しいソフトウェアはとても使いやすい。",
    "work": "報告書は今四半期に完了した作業を要約している。",
    "use": "チームは締め切り前にそのソフトウェアを使用する。",
    "want": "顧客は納品日を変更したいと考えている。",
    "way": "上司はコストを削減する方法を教えてくれた。",
    "thing": "最も重要なことは締め切りを守ることだ。",
    "right": "顧客には注文をキャンセルする権利がある。",
    "such": "このような遅延は配送スケジュール全体に影響する。",
    "tell": "遅延について顧客に伝えてください。",
    "really": "新しいサービスは顧客にとても人気がある。",
    "show": "チームは締め切り前に顧客へ結果を示す。",
    "too": "当初の見積もりは高すぎた。",
    "still": "注文はまだ処理中です。",
    "problem": "マネージャーは会議中に問題を解決した。",
    "write": "フォームの上部に氏名を記入してください。",
    "same": "2枚の請求書には同じ金額が記載されている。",
    "try": "チームは今日、その問題の解決を試みる。",
    "start": "会議は9時に始まる。",
    "talk": "チームは締め切り前に顧客と話す。",
    "something": "何か問題が起きたら連絡してください。",
    "put": "ファイルを共有フォルダーに入れてください。",
    "school": "会社は新しい技術者向けの研修校を運営している。",
    "world": "会社は世界中で事業を展開している。",
    "week": "報告書の提出期限は来週です。",
    "report": "上司は会議前に報告書を求めた。",
    "woman": "受付の女性が来訪者用バッジを渡してくれた。",
    "seem": "システム更新後、数値が異常に見える可能性がある。",
    "system": "新しいシステムは注文を自動的に処理する。",
    "question": "質問がある場合はカスタマーサービスに連絡してください。",
    "set": "チームは締め切り前にスケジュールを設定する。",
    "small": "会社は中小企業にサービスを提供している。",
    "study": "会社は顧客満足度の調査を委託した。",
    "since": "その店はセール開始以来、忙しい状態が続いている。",
    "run": "サーバーは営業時間中、継続的に稼働する。",
    "turn": "退出する前に機器の電源を切ってください。",
    "state": "マネージャーはプロジェクトの現在の状態を確認した。",
    "provide": "上司は来四半期の研修プログラム一覧を提供する。",
    "read": "フォームに記入する前に指示を読んでください。",
    "without": "注文品は遅延なく発送された。",
    "word": "顧客向けの手紙に「返金」という語が出てくる。",
    "service": "会社は中小企業向けの新サービスを開始した。",
    "second": "2回目の出荷品は今朝到着した。",
    "though": "配送は遅れたが、顧客は受け入れた。",
    "yes": "顧客は改訂版の提案に同意した。",
    "result": "調査結果は次回の会議で発表される。",
    "young": "会社は研修プログラムに若い専門職を採用している。",
    "program": "研修プログラムは来月始まる。",
    "understand": "チームは締め切り前に指示を理解する。",
    "thank": "迅速な対応について顧客にお礼を伝えてください。",
    "today": "経理チームは今日、返金を行う。",
    "student": "会社は夏季に学生アシスタントを雇った。",
    "room": "明日の会議のため会議室を予約してください。",
    "until": "オフィスは午後6時まで営業する。",
    "reason": "マネージャーは遅延の理由を説明した。",
    "spend": "会社は従業員研修により多くの費用をかける予定だ。",
    "learn": "新入社員はオリエンテーション中に手順を学ぶ。",
    "support": "チームは締め切り前に提案を支持する。",
    "whether": "マネージャーは顧客が変更を承認したか尋ねた。",
    "present": "取締役は四半期の業績を発表する。",
    "side": "側面のドアは配送専用です。",
    "quite": "新しいシステムはかなり信頼性が高い。",
    "sure": "上司がスケジュールを承認したと確信していますか。",
    "term": "契約期間は1年間です。",
    "speak": "取締役は明日、会議で話す。",
    "within": "3営業日以内に返答してください。",
    "process": "チームは金曜までに申請を処理する。",
    "public": "会社は公式声明を発表した。",
    "train": "会社は繁忙期前に新しいスタッフを研修する。",
    "rather": "顧客はかなり簡単な解決策を求めた。",
    "view": "ホテルから港の景色が見える。",
    "together": "営業チームとマーケティングチームは協力して働いた。",
    "price": "仕入先は大量注文に低い価格を提示した。",
    "product": "会社は先月、新製品を発売した。",
    "story": "マネージャーは会議で成功事例を紹介した。",
    "stand": "展示台は入口の近くにある。",
    "whole": "チーム全員が会議に出席した。",
    "yet": "仕入先はまだ日付を確認していない。",
    "rate": "銀行は先月、金利を引き下げた。",
    "sort": "ファイルを日付順に並べてください。",
    "water": "施設は節水システムを使用している。",
    "send": "今日、請求書を顧客に送ってください。",
    "soon": "交換部品はまもなく到着する。",
    "watch": "機器を使う前に実演を見てください。",
    "probably": "出荷品はおそらく明日到着する。",
    "suggest": "チームは締め切り前に解決策を提案する。",
    "test": "技術者は新しい機器の試験を実施した。",
    "visit": "顧客は来週、支店を訪問する。",
    "return": "顧客は30日以内なら製品を返品できる。",
    "walk": "来訪者は駅から支店まで歩いて行ける。",
    "value": "会社は長期的な顧客関係を重視している。",
    "record": "チームは締め切り前に結果を記録する。",
    "stay": "宿泊客は会議中ホテルに滞在する。",
    "stop": "カバーを開ける前に機械を止めてください。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 2][:100]
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
    print(f"reviewed 600+ Japanese examples batch 1: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
