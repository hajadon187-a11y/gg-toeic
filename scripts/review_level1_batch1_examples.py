#!/usr/bin/env python3
"""Review the first 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "the": "改訂版のスケジュールはメールに添付されています。",
    "be": "最終的な数値は明日確認できます。",
    "and": "営業チームとマーケティングチームは一緒に提案書を検討しました。",
    "of": "配送費は見積もりに含まれていました。",
    "to": "改訂版の契約書を顧客に送ってください。",
    "a": "マネージャーはフォローアップ会議を設定しました。",
    "in": "ファイルは共有フォルダーに保存されています。",
    "have": "契約書を確認する時間は十分にあります。",
    "it": "プリンターの用紙が切れているため、注文を処理できません。",
    "you": "会社のウェブサイトからフォームをダウンロードできます。",
    "he": "彼は改訂版のスケジュールについて上司に尋ねました。",
    "for": "会議室は午後の会議用に予約されています。",
    "they": "彼らは仕入先からの返答を待っています。",
    "not": "この場所ではその製品を利用できません。",
    "that": "マネージャーは会議が中止になったことを確認しました。",
    "we": "私たちは明日の会議で提案について話し合います。",
    "on": "報告書は会社のウェブサイトで入手できます。",
    "with": "申請書と一緒に記入済みのフォームを送ってください。",
    "this": "この報告書は調査結果をまとめたものです。",
    "i": "今日の午後、改訂版の請求書を送ります。",
    "do": "締め切りに間に合うよう、最善を尽くしてください。",
    "as": "嵐が近づいたため、オフィスは閉鎖されました。",
    "at": "会議は9時に始まります。",
    "she": "彼女は取締役会で四半期の業績を発表します。",
    "but": "その製品は手頃な価格で、しかも耐久性があります。",
    "from": "その出荷品は地域倉庫から届きました。",
    "by": "金曜午後までにフォームを提出してください。",
    "will": "仕入先は明日の朝、注文品を納品する予定です。",
    "or": "クレジットカードまたは銀行振込で支払えます。",
    "go": "マネージャーは会議の後、支店へ行きます。",
    "so": "道路が通行止めだったため、運転手は別の経路を使いました。",
    "all": "全従業員は金曜までに研修を終えなければなりません。",
    "if": "配送が遅れた場合はお知らせください。",
    "one": "仕入先の1社がより安い価格を提示しました。",
    "would": "顧客は納品日を遅らせることを希望しています。",
    "about": "報告書には新しいプロジェクトに関する情報が含まれています。",
    "can": "新しいシステムは注文をより速く処理できます。",
    "which": "仕入先は2つのモデルを提案しましたが、どちらも当社のニーズを満たしませんでした。",
    "there": "3階には空いているオフィスが2室あります。",
    "know": "チームは締め切りまでに答えを確認できます。",
    "more": "改訂版の手順は、開始時により多くの時間を必要とします。",
    "get": "チームは締め切り前に承認を得るでしょう。",
    "who": "最初に到着した応募者が取締役の面接を受けました。",
    "like": "顧客は改訂版の提案書を確認したいと考えています。",
    "when": "出荷品が到着したら、私に電話してください。",
    "make": "チームは締め切り前に予約を入れます。",
    "what": "報告書は売上減少の原因を説明しています。",
    "up": "更新プログラムをインストールする前にファイルをバックアップしてください。",
    "some": "一部の顧客は納品日を遅らせるよう依頼しました。",
    "other": "工事中は別の入口をお使いください。",
    "out": "会議中にプリンターの用紙が切れました。",
    "good": "上司は私のスケジュールが第1四半期には良いと言いました。",
    "people": "複数の部署の人々が会議に出席し、出席票に署名しました。",
    "no": "標準配送は無料です。",
    "because": "取締役が体調を崩したため、会議は延期されました。",
    "just": "仕入先は配送日をたった今確認したところです。",
    "come": "仕入先はシステム更新後にオフィスへ来る可能性があります。",
    "could": "改訂版の請求書を今日送っていただけますか。",
    "than": "改訂版の手順は以前のものより効率的です。",
    "now": "改訂版のスケジュールは現在確認できます。",
    "then": "数値を確認してからフォームに署名してください。",
    "also": "新しい方針は契約社員にも適用されます。",
    "into": "会社は複数の海外市場へ事業を拡大しました。",
    "only": "その割引は会員だけが利用できます。",
    "look": "チームは締め切り前にその問題を調査します。",
    "give": "チームは締め切り前に顧客へ最新情報を伝えます。",
    "first": "最初の出荷品は予想より早く到着しました。",
    "new": "会社は顧客からの苦情に対応する新しい手順を導入しました。",
    "find": "チームは締め切り前にミスを見つけます。",
    "over": "会社は過去1年間でサービスを拡大しました。",
    "any": "ご質問があればご連絡ください。",
    "after": "チームは立ち上げ後に検証を行いました。",
    "day": "休日の前日は配送チームにとって最も忙しい日です。",
    "where": "地図には新しい支店がどこに開設されるかが示されています。",
    "most": "ほとんどの従業員は柔軟な勤務スケジュールを好みます。",
    "should": "チームは安全手順を確認すべきです。",
    "need": "チームは締め切り前にさらに時間が必要になります。",
    "much": "新しい手順では書類があまり必要ありません。",
    "how": "研修では新しい機器の操作方法を説明します。",
    "back": "署名済みの契約書を金曜までに返送してください。",
    "mean": "上司はこれらの得点の平均は12だと言いました。",
    "even": "その割引は少量の注文にも適用されます。",
    "may": "配送品は予想より遅れて到着する可能性があります。",
    "here": "出かける前に署名済みの書類をここに置いてください。",
    "many": "多くの小売業者が休暇シーズン中にこのサービスを利用します。",
    "last": "最後の出荷品は今朝倉庫を出ました。",
    "child": "会社は子どものいる従業員に育児福利厚生を提供しています。",
    "call": "チームは締め切り前に顧客へ電話します。",
    "before": "注文する前に在庫を確認してください。",
    "company": "報告書には会社に関する情報が含まれています。",
    "through": "会社は地元の小売業者を通じて商品を販売しています。",
    "down": "技術者は保守作業の前にサーバーを停止しました。",
    "life": "定期的な保守によって機器の寿命を延ばせます。",
    "man": "受付の男性が来訪者の予約を確認しました。",
    "change": "会議の時間を変更してもよいですか。",
    "place": "記入済みのフォームを私の机の上に置いてください。",
    "long": "会社はプロジェクトについて長期計画を採用しました。",
    "between": "契約書では2社間の責任を定めています。",
    "feel": "研修を終えると従業員はより自信を持てるようになります。",
    "lot": "店は休暇シーズン前に大量の備品を注文しました。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][:100]
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
    print(f"reviewed 500+ Japanese examples: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
