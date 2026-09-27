#!/usr/bin/env python3
"""Review the second 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "great": "チームが成し遂げた大きな進歩を、その報告書は強調している。",
    "leave": "その従業員は今日早く退社してもよいか尋ねた。",
    "number": "オンライン注文の数は今月増加した。",
    "both": "両方のオフィスは祝日のため休業します。",
    "own": "会社は昨年、自社の地域オフィスを開設した。",
    "part": "財務部は研修に割り当てられた予算の一部を確認した。",
    "point": "マネージャーは会議中に重要な点を指摘した。",
    "little": "プロジェクトを完了するまでチームに残された時間はほとんどない。",
    "help": "顧客が申請書を記入するのを手伝ってください。",
    "ask": "仕入先に最新の納品日を尋ねてください。",
    "meet": "チームは締め切り前に顧客と会う。",
    "another": "アシスタントは会議のために別の会議室を予約した。",
    "become": "会社は持続可能な包装材のリーダーになることを目指している。",
    "interest": "顧客は新サービスに関心を示した。",
    "country": "会社は複数の国に製品を輸出している。",
    "old": "古いシステムは来月交換される。",
    "each": "各応募者は確認メールを受け取った。",
    "late": "遅れて届いた出荷品が生産の遅延を引き起こした。",
    "high": "会社は今四半期の高い売上目標を設定した。",
    "different": "2つの計画には異なる投資水準が必要です。",
    "off": "技術者は保守作業の前に機械の電源を切った。",
    "next": "次回の会議は月曜日に開催される。",
    "end": "契約は会計年度末に終了する。",
    "live": "複数の従業員が新しい支店の近くに住んでいる。",
    "why": "報告書は出荷品が遅れた理由を説明している。",
    "while": "マネージャーが不在の間、アシスタントは電話に応対した。",
    "play": "広告は朝のニュース番組中に流れる。",
    "might": "出荷品は予想より遅れて到着する可能性がある。",
    "must": "すべての来訪者は受付で記帳しなければならない。",
    "home": "改装中、その従業員は在宅勤務をした。",
    "never": "上司は領収書のない経費報告を決して承認しない。",
    "include": "報告書には最新の売上高が含まれる予定だ。",
    "course": "会社は職場の安全に関する短期講座を開いている。",
    "house": "会社は訪問中の技術者を近くのホテルに泊める予定だ。",
    "group": "プロジェクトチームは毎週月曜日に進捗を確認する。",
    "case": "払い戻しが必要になった場合に備え、領収書のコピーを保管してください。",
    "around": "配送ドライバーは正午ごろ到着した。",
    "book": "明日の会議室を予約してください。",
    "family": "会社は従業員とその家族に福利厚生を提供している。",
    "let": "スケジュール変更について顧客に知らせてください。",
    "again": "作業を続ける前に、もう一度指示を確認してください。",
    "kind": "顧客にはどのような書類が必要ですか。",
    "keep": "記録を少なくとも5年間保管してください。",
    "hear": "マネージャーが改訂版のスケジュールを承認したと聞いています。",
    "every": "システムは毎朝セキュリティチェックを行う。",
    "during": "定期保守中、システムはオフラインになっていた。",
    "always": "会社は使用前に必ず機器を確認する。",
    "big": "会社は海外の顧客と大口契約を獲得した。",
    "follow": "チームは締め切り前に指示に従う。",
    "begin": "会議は午前9時に始まる。",
    "important": "報告書は顧客需要の重要な変化をいくつか示している。",
    "under": "プロジェクトは法務部の審査中です。",
    "few": "研修会の残り席はわずかです。",
    "bring": "会議に署名済みの契約書を持参してください。",
    "early": "面接には早めに到着してください。",
    "hand": "これらのファイルを運ぶのを手伝ってもらえますか。",
    "move": "チームは締め切り前に機器を移動する。",
    "money": "会社は機器のアップグレード用に資金を取り分けた。",
    "fact": "報告書は売上が増加したという事実を確認している。",
    "however": "配送は遅れたが、顧客は新しい日程を受け入れた。",
    "area": "倉庫は工業地域にあります。",
    "name": "フォームの上部に氏名を記入してください。",
    "friend": "友人がこの仕入先を私に推薦してくれた。",
    "month": "上司はプロジェクトには1か月で十分だと言った。",
    "large": "会社は新しい顧客から大口注文を受けた。",
    "business": "その事業は新しい契約を獲得した後に拡大した。",
    "information": "フォームで求められている情報を提出してください。",
    "open": "会社は来春、新しい支店を開設する。",
    "order": "金曜午後までに注文を入れてください。",
    "government": "会社は政府の規制を遵守しなければならない。",
    "issue": "マネージャーは会議中にその問題に対処した。",
    "market": "会社は製品を発売する前に市場を調査している。",
    "pay": "チームは締め切り前に請求書を支払う。",
    "build": "会社は来年、新しい配送センターを建設する。",
    "hold": "会社は明日、仕入先との会議を開く。",
    "against": "その保険契約は会社を金銭的損失から守る。",
    "believe": "顧客は改訂版の計画がコストを削減すると考えている。",
    "love": "顧客は新しいサービスをとても気に入ったと言った。",
    "increase": "オンライン注文の増加には追加のスタッフが必要だった。",
    "job": "会社はウェブサイトに求人を掲載した。",
    "plan": "チームは製品発売の計画を最終決定した。",
    "away": "マネージャーは今日の午後、オフィスを離れている。",
    "example": "マネージャーは苦情への対応方法の例を示した。",
    "happen": "システム更新中に予期せぬ遅延が起こることがある。",
    "offer": "仕入先は大量注文に割引を提示した。",
    "close": "チームは締め切り前に口座を閉鎖する。",
    "lead": "取締役は明日、会議の司会を務める。",
    "buy": "購買チームは来月、新しい機器を購入する。",
    "far": "新しい倉庫は市の中心部から遠い。",
    "hour": "技術者は機械の修理に1時間取り組んだ。",
    "face": "会社は遅延によりコストの上昇に直面している。",
    "hope": "新しい方針が顧客満足度を高めることを期待している。",
    "idea": "マネージャーは配送費削減のアイデアを提示した。",
    "cost": "配送費は今四半期に増加した。",
    "less": "新しい手順は旧手順より紙の使用量が少ない。",
    "form": "フォームに記入して金曜までに返送してください。",
    "head": "マネージャーは新しい部署を率いる。",
    "car": "レンタカーは燃料を満タンにして返却しなければならない。",
    "level": "オフィスの騒音レベルは低いままだった。",
    "person": "購買担当者が注文を承認した。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][100:200]
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
    print(f"reviewed 500+ Japanese examples batch 2: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
