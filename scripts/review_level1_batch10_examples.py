#!/usr/bin/env python3
"""Review the tenth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "civil": "両者は契約について穏便に話し合った。",
    "locate": "会社は新しいオフィスを中心街に置く予定だ。",
    "citizen": "市はすべての市民にサービスを提供した。",
    "gold": "その賞は金で作られていた。",
    "domestic": "会社は国内販売に力を入れている。",
    "load": "そのトラックは重い荷物を運べる。",
    "belief": "新しい計画へのマネージャーの信頼がチームを励ました。",
    "arrangement": "アシスタントは旅行の手配を確認した。",
    "acquire": "会社は小規模な競合会社を買収する予定だ。",
    "corporate": "会社には明確な企業アイデンティティがある。",
    "fairly": "新しいソフトウェアはかなり使いやすい。",
    "capacity": "倉庫には500箱分の収容能力がある。",
    "border": "出荷品は遅れることなく国境を越えた。",
    "assessment": "マネージャーはチームの進捗を評価した。",
    "ad": "会社はビジネス誌に広告を掲載した。",
    "fee": "そのサービスには月額料金がかからない。",
    "hall": "会議ホールには300人収容できる。",
    "escape": "火災報知器のおかげで従業員は安全に避難できた。",
    "component": "技術者は故障した部品を交換した。",
    "afford": "会社は発売を遅らせる余裕がない。",
    "lawyer": "弁護士は契約書を確認した。",
    "cup": "来訪者は受付エリアでコーヒーを1杯飲んだ。",
    "description": "製品説明はウェブサイトに掲載されている。",
    "confidence": "研修によって新入社員は自信を持てるようになった。",
    "industrial": "倉庫は工業地域にある。",
    "complain": "顧客は遅延について苦情を申し立てた。",
    "error": "報告書には誤りがある。",
    "arrest": "警察は倉庫付近で容疑者を逮捕した。",
    "assess": "監査で会社のリスクを評価する。",
    "asset": "倉庫は会社にとって貴重な資産だ。",
    "finger": "その機器はアクセス時に従業員の指を読み取る。",
    "explore": "会社は新しい市場を開拓している。",
    "leadership": "強いリーダーシップが危機の中で会社を支えた。",
    "commitment": "会社の安全への取り組みは明確だ。",
    "bright": "会社には明るい未来がある。",
    "frame": "技術者は展示物の枠を修理した。",
    "bond": "会社は資本を調達するため債券を発行した。",
    "hire": "会社はより多くのスタッフを雇用する予定だ。",
    "hole": "荷物の穴から製品が露出していた。",
    "internal": "会社は内部監査を実施した。",
    "chain": "小売チェーンは新しい店舗を開いた。",
    "literature": "マネージャーは機器を承認する前に技術文献を確認した。",
    "division": "営業部門は四半期目標を上回った。",
    "amaze": "新製品は発売時に顧客を驚かせた。",
    "device": "IT部門はシステム更新後に機器を監視した。",
    "birth": "会社は子どもの出生後に休暇を提供している。",
    "forest": "会社は持続可能な森林から採取した紙を使用している。",
    "label": "各箱に配送先のラベルを貼ってください。",
    "factory": "その工場は自動車産業向けの部品を生産している。",
    "expense": "金曜までに出張経費を提出してください。",
    "channel": "会社は複数の販売チャネルを利用している。",
    "investigate": "チームは締め切り前に苦情を調査する。",
    "friendly": "スタッフは親切で協力的だった。",
    "concentrate": "最も緊急な作業に集中してください。",
    "export": "会社は製品をアジアへ輸出している。",
    "entirely": "その決定は顧客のフィードバックだけに基づいていた。",
    "bridge": "橋が閉鎖され、配送が遅れた。",
    "consist": "チームは3つの部門で構成されている。",
    "graduate": "その卒業生は初級職に応募した。",
    "brand": "会社は強いブランドを築いた。",
    "insist": "顧客は全額返金を強く求めた。",
    "combination": "品質と価格の組み合わせが顧客を引き付けた。",
    "abuse": "会社には職場での虐待を禁じる方針がある。",
    "ice": "ホテルは会議の参加者に氷を提供している。",
    "definitely": "仕入先は確実に納品日を確認する。",
    "grade": "その製品は高い品質評価を受けた。",
    "largely": "増加の大部分は需要の高まりによるものだった。",
    "appearance": "製品の外観が顧客の選択に影響した。",
    "guarantee": "会社は製品の品質を保証している。",
    "judgment": "マネージャーは苦情への対応で適切な判断をした。",
    "approve": "チームは締め切り前に申請を承認する。",
    "loan": "銀行は事業拡大のための融資を承認した。",
    "definition": "契約書にはその用語の明確な定義がある。",
    "elect": "従業員は新しい委員長を選出する。",
    "atmosphere": "オフィスは落ち着いた雰囲気だ。",
    "farmer": "その農家は地元のレストランに野菜を供給している。",
    "comparison": "2つの計画を比較した結果、改訂案が支持された。",
    "characteristic": "耐久性はその製品の重要な特徴だ。",
    "license": "運転手は有効な免許証を持っていなければならない。",
    "identity": "システムは利用者の身元を確認する。",
    "desk": "書類を私の机の上に置いてください。",
    "empty": "在庫品を発送した後、倉庫は空になった。",
    "commission": "営業担当者は販売ごとに歩合を受け取る。",
    "association": "業界団体は新しい安全指針を発表した。",
    "instrument": "技術者は電圧を測定する機器を使った。",
    "investor": "投資家は会社の拡張計画を支援した。",
    "lovely": "ホテルから港のすばらしい景色が見える。",
    "lock": "使用後は保管室に鍵をかけてください。",
    "fuel": "トラックは配送前に燃料を補給する必要がある。",
    "expectation": "そのサービスは顧客の期待を上回った。",
    "employment": "会社は研修修了者に正社員の雇用を提供している。",
    "celebrate": "チームはプロジェクト完了後に祝う予定だ。",
    "breath": "技術者は機械を再起動する前に深呼吸した。",
    "increasingly": "そのサービスは中小企業にますます人気がある。",
    "import": "会社は複数の国からコーヒーを輸入している。",
    "bottle": "空のボトルをリサイクルしてください。",
    "engine": "技術者は飛行前にエンジンを点検した。",
    "cast": "監督はCMに地元の俳優を起用した。",
    "conservative": "会社は投資に慎重な方針を取った。",
    "journey": "成功する事業を築くことは長い道のりだ。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][900:1000]
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
    print(f"reviewed 500+ Japanese examples batch 10: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
