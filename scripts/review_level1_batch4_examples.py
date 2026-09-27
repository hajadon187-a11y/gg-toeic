#!/usr/bin/env python3
"""Review the fourth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "near": "新しい支店は駅の近くにある。",
    "human": "会社は顧客サービスにおいて人間味のある対応を重視している。",
    "computer": "コンピューターが注文を自動的に処理した。",
    "activity": "報告書は監査中の活動を要約している。",
    "film": "会社は新入社員向けの研修映画を制作した。",
    "morning": "朝の会議は8時30分に始まる。",
    "account": "支払いをする前に口座残高を確認してください。",
    "major": "会社は新しい機器に大規模な投資を行った。",
    "above": "連絡先については、上記の情報を参照してください。",
    "design": "デザインチームは新製品のパンフレットを作成した。",
    "event": "会社は来月、業界イベントのスポンサーになる。",
    "condition": "その機器は良好な状態です。",
    "carry": "署名済みの書類を法務部まで運んでください。",
    "choose": "チームは金曜までに仕入先を選ぶ。",
    "father": "私の父は国際的な運送会社に勤めている。",
    "decision": "マネージャーの決定は顧客からのフィードバックに基づいていた。",
    "certain": "契約には解約に関する特定の条件が含まれている。",
    "forward": "請求書を経理部へ転送してください。",
    "main": "本社は中心街にある。",
    "die": "プレゼンテーション中に電池が切れる可能性がある。",
    "bear": "会社が送料を負担する。",
    "cut": "会社は運営費を削減する予定だ。",
    "describe": "パンフレットは新しいサービスについて説明している。",
    "himself": "取締役自身が提案を承認した。",
    "available": "交換部品は地域倉庫から入手できます。",
    "especially": "新しいソフトウェアは在庫管理に特に役立つ。",
    "girl": "受付の少女が来訪者用のバッジを渡してくれた。",
    "maybe": "おそらく仕入先はより早い納品日を提示できる。",
    "community": "会社はボランティア活動を通じて地域社会を支援している。",
    "else": "購買部の別の担当者に連絡してください。",
    "particular": "顧客は特定の納品日を希望した。",
    "join": "数名の新入社員が来月営業チームに加わる。",
    "difficult": "チームは厳しい締め切りに直面した。",
    "please": "改訂版の請求書を本日送ってください。",
    "detail": "契約書には合意内容の詳細がすべて記載されている。",
    "difference": "価格差は送料を反映している。",
    "action": "マネージャーは顧客サービスを改善するため行動を起こした。",
    "health": "会社はすべての正社員に健康保険を提供している。",
    "eat": "従業員は休憩室で昼食を取ることができる。",
    "phone": "もう一度鳴る前に電話に出てください。",
    "draw": "アナリストは売上データから結論を導き出した。",
    "date": "仕入先に納品日を確認してください。",
    "practice": "会社は従業員に安全な取り扱い手順を実践するよう促している。",
    "model": "会社は新型のプリンターを導入した。",
    "customer": "顧客が返金を求めた。",
    "front": "荷物を正面受付に置いてください。",
    "explain": "マネージャーは会議で新しい手順を説明する。",
    "door": "オフィスのドアを静かに閉めてください。",
    "outside": "配送トラックは倉庫の外で待機している。",
    "behind": "遅延の背景にあった理由は税関検査だった。",
    "economic": "経済状況が会社の売上に影響を与えた。",
    "approach": "マネージャーは顧客サービスへの新しい取り組み方を提案した。",
    "land": "飛行機は午後6時に着陸する。",
    "charge": "通常配送には料金がかかりません。",
    "finally": "出荷品は今朝ようやく到着した。",
    "claim": "顧客は破損した製品について請求を申し立てた。",
    "enjoy": "従業員は柔軟な勤務時間を楽しんでいる。",
    "death": "その保険契約は契約者の死亡後に給付金を支払う。",
    "nice": "ホテルのスタッフは訪問中の顧客に親切だった。",
    "amount": "請求書には支払総額が記載されている。",
    "improve": "会社は顧客サービスを改善する予定だ。",
    "picture": "パンフレットには新しいオフィスの写真が載っている。",
    "boy": "配達員が書類を受付に届けた。",
    "organization": "その団体は中小企業向けの研修を提供している。",
    "happy": "顧客は迅速な対応に満足した。",
    "couple": "マネージャーは仕入先との会議を2件予定した。",
    "act": "会社は問題を解決するため迅速に行動しなければならない。",
    "opportunity": "その研修は新しいスキルを身につける良い機会だ。",
    "accord": "支払いは契約に従って行われた。",
    "list": "新しい仕入先を承認済みリストに追加してください。",
    "fund": "会社は銀行融資で事業拡大の資金を調達する。",
    "kid": "会社は子どものいる従業員に育児福利厚生を提供している。",
    "industry": "最新の報告書は業界が地域企業に与えた影響を説明している。",
    "measure": "会社は発売後に顧客満足度を測定する。",
    "kill": "中止になれば、そのプロジェクトは失敗に終わる可能性がある。",
    "likely": "出荷品は遅れて到着する可能性が高い。",
    "certainly": "マネージャーは確実に提案を確認する。",
    "national": "会社は全国規模の配送網を運営している。",
    "itself": "システムは更新後に自動的に再起動する。",
    "field": "アスタリスクの付いた欄に記入してください。",
    "air": "出荷品は航空便で送られる。",
    "benefit": "新しい方針はパートタイム従業員の利益になる。",
    "news": "会社はプレスリリースでそのニュースを発表した。",
    "percent": "営業チームは目標の90パーセントを達成した。",
    "focus": "マネージャーは私たちに最も緊急な問題に集中するよう求めた。",
    "instead": "紙のフォームではなくオンラインフォームを使ってください。",
    "data": "アナリストは報告書を作成する前にデータを確認した。",
    "address": "配送先住所を確認してください。",
    "performance": "評価ではチームの業績を査定する。",
    "chance": "新サービスは顧客に時間を節約する機会を与える。",
    "accept": "顧客は改訂された納品日を受け入れることに同意した。",
    "mention": "マネージャーは会議で遅延について言及する。",
    "choice": "顧客は3つの配送方法から選べる。",
    "common": "これは古い機器によくある問題です。",
    "culture": "会社は安全を重視する企業文化を育てている。",
    "demand": "新サービスへの需要は今四半期に増加した。",
    "material": "仕入先は新製品用の原材料を注文した。",
    "limit": "会社は毎月の経費に上限を設定した。",
    "listen": "返答する前に顧客の懸念を聞いてください。",
    "due": "請求書の支払期限は月末です。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][300:400]
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
    print(f"reviewed 500+ Japanese examples batch 4: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
