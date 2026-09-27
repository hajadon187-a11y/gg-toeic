#!/usr/bin/env python3
"""Review the ninth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "contribution": "会社は地域の慈善団体に寄付をした。",
    "appreciate": "迅速なご返答に感謝します。",
    "chapter": "ハンドブックには職場の安全に関する章がある。",
    "apparently": "どうやら仕入先は昨日注文品を発送したようだ。",
    "burn": "技術者はモーターが焼き切れる可能性があると警告した。",
    "initial": "当初の見積もりは最終費用より低かった。",
    "critical": "技術者はシステムに重大なエラーを発見した。",
    "gather": "チームは顧客からフィードバックを集める。",
    "earth": "その製品は地球上で採取された素材から作られている。",
    "essential": "明確なコミュニケーションはプロジェクトに不可欠だ。",
    "desire": "顧客はより早い配送を望んでいると伝えた。",
    "currently": "経理部は現在フォームを確認している。",
    "employ": "会社は来年、技術者をさらに雇用する予定だ。",
    "beach": "ビーチ近くのホテルはビジネス会議を開催している。",
    "attract": "そのキャンペーンは新規顧客を引き付けることを目指している。",
    "engage": "会社はソーシャルメディアを通じて顧客と交流している。",
    "flower": "ホテルは受付用の花を注文した。",
    "crisis": "会社は金融危機に備えた計画を作成した。",
    "boat": "会社は島へ物資を届けるため船を使っている。",
    "aid": "会社は困っている従業員に経済的援助を提供している。",
    "fan": "機器の試験中に冷却ファンが止まった。",
    "kitchen": "そのレストランは厨房を改装した。",
    "fresh": "そのレストランは地元の仕入先から新鮮な食品を仕入れている。",
    "delay": "嵐のため仕入先は出荷を遅らせる。",
    "engineer": "技術者は使用前に機器を点検した。",
    "insurance": "会社は従業員に健康保険を提供している。",
    "divide": "マネージャーはチームメンバーに仕事を分担した。",
    "length": "契約期間は1年間です。",
    "investigation": "調査では不正の証拠は見つからなかった。",
    "expand": "会社は海外で事業を拡大する。",
    "commit": "会社は二酸化炭素排出量の削減に取り組んだ。",
    "jump": "燃料価格は来月急騰する可能性がある。",
    "host": "会社は来年春に会議を主催する。",
    "district": "支店は金融街にある。",
    "broad": "会社は幅広い製品を提供している。",
    "lunch": "顧客は私たちを昼食に招待した。",
    "actual": "実際の費用は見積もりより高かった。",
    "battle": "会社は契約獲得競争に勝った。",
    "cash": "その店は現金とクレジットカードを受け付けている。",
    "hardly": "新しいシステムにはほとんどエラーがない。",
    "award": "会社は顧客サービスで賞を受賞した。",
    "coach": "コーチはチームビルディングの研修を指導した。",
    "consideration": "その提案は検討中です。",
    "code": "アクセスコードを入力してください。",
    "accident": "事故により倉庫付近の交通が遅れた。",
    "impossible": "スタッフを増やさなければ締め切りに間に合わせるのは不可能だ。",
    "enable": "新しいソフトウェアにより従業員はリモート勤務ができる。",
    "afraid": "顧客は出荷品が紛失するのではないかと恐れていた。",
    "active": "その口座はまだ有効です。",
    "conclude": "チームは締め切り前に会議を終える。",
    "cancer": "診療所は従業員にがん検診を提供している。",
    "convince": "営業担当者は顧客を説得して契約を更新してもらった。",
    "environmental": "会社は工場向けの環境基準を採用した。",
    "healthy": "食堂は野菜と焼き鳥を使った健康的な昼食を提供している。",
    "blow": "電力サージでヒューズが飛ぶ可能性がある。",
    "location": "納品場所を確認してください。",
    "invest": "会社は新技術に投資する予定だ。",
    "actor": "その俳優は会社のCMに出演した。",
    "glad": "注文品が無事に届いたと聞いてうれしく思います。",
    "finance": "財務部は四半期の業績を確認した。",
    "hate": "従業員は不必要な書類作業を嫌がる。",
    "egg": "ホテルは地元の仕入先から卵を注文した。",
    "concert": "会社は地域向けのコンサートに協賛した。",
    "comfortable": "ホテルは会議の参加者に快適な椅子を用意した。",
    "carefully": "契約書を注意深く確認してください。",
    "camera": "防犯カメラが配送の様子を記録した。",
    "cycle": "会社は月次の請求サイクルを採用している。",
    "coffee": "オフィスは従業員に無料のコーヒーを提供している。",
    "freedom": "その方針により、従業員は勤務時間を自由に選べる。",
    "construction": "新しい支店の建設は来月始まる。",
    "dear": "パテル様、お問い合わせありがとうございます。",
    "historical": "博物館は地元企業の歴史的文書を展示した。",
    "branch": "新しい支店は来月開業する。",
    "bind": "契約は両当事者を合意した条件に拘束する。",
    "belong": "これらの書類は財務ファイルに入れてください。",
    "fashion": "その店は最新のファッショントレンドを取り入れている。",
    "danger": "警告標識は機械の近くに危険があることを示している。",
    "bomb": "警備チームは荷物に爆弾がないか確認した。",
    "army": "その会社は軍に機器を供給している。",
    "dangerous": "その化学物質は誤って扱うと危険です。",
    "decrease": "システム更新後、費用は減少する可能性がある。",
    "hurt": "遅延が売上に悪影響を与えた。",
    "council": "市議会は再開発計画を承認した。",
    "editor": "編集者は社内誌の記事を確認した。",
    "generate": "太陽光パネルは施設用の電力を発電する。",
    "gift": "会社は来訪者一人ひとりに小さな贈り物を渡した。",
    "delivery": "配送品は予想より早く到着した。",
    "deny": "仕入先は損害への責任を否定した。",
    "guest": "ホテルの宿泊客はレイトチェックアウトを希望した。",
    "anybody": "質問がある方は誰でもヘルプデスクに連絡できます。",
    "bedroom": "ホテルは訪問する幹部のために寝室を予約した。",
    "climb": "会社が新サービスを開始すると売上が伸びた。",
    "basically": "遅延は基本的に署名の不足が原因だった。",
    "mainly": "そのサービスは主に中小企業に利用されている。",
    "manner": "マネージャーは苦情に専門的な態度で対応した。",
    "gun": "警備員は銃を見たと報告した。",
    "familiar": "マネージャーは新しい手順に詳しい。",
    "ignore": "機器の警告を無視しないでください。",
    "destroy": "火災で倉庫内の複数のファイルが焼失した。",
    "affair": "会社の財務業務は経理部が処理している。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][800:900]
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
    print(f"reviewed 500+ Japanese examples batch 9: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
