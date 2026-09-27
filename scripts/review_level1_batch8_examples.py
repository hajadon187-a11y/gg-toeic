#!/usr/bin/env python3
"""Review the eighth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "fair": "仕入先は公正な価格を提示した。",
    "additional": "会社は仕入先に追加情報を求めた。",
    "farm": "会社は地元の農場からコーヒーを仕入れている。",
    "collection": "財務チームは請求書の一式を確認した。",
    "hang": "受付エリアに掲示を掛けてください。",
    "band": "会社は歓迎会のためにバンドを雇った。",
    "alternative": "チームは別の配送方法を提案した。",
    "attitude": "その従業員の前向きな姿勢はマネージャーに好印象を与えた。",
    "cheap": "仕入先は安価ですが信頼できる選択肢を提示した。",
    "double": "会社は来年、生産量を倍増する予定だ。",
    "leg": "会議室のテーブルの脚が1本壊れている。",
    "examine": "チームは締め切り前に記録を調べる。",
    "lay": "請負業者は新施設の基礎を築く。",
    "display": "チームは会議で結果を展示する。",
    "intend": "会社は海外への拡大を意図している。",
    "dinner": "顧客は会議の後、私たちを夕食に招待した。",
    "apart": "2つの倉庫は5マイル離れている。",
    "federal": "会社は連邦規則を遵守しなければならない。",
    "crime": "警察は倉庫で起きた犯罪を捜査した。",
    "decline": "売上の減少が経営陣を懸念させた。",
    "decade": "会社はここで10年以上営業している。",
    "launch": "チームは来月その製品を発売する。",
    "consumer": "消費者は新サービスに好意的に反応した。",
    "favor": "お願いがあります。請求書を送ってもらえますか。",
    "dry": "書類は乾燥した場所に保管してください。",
    "institution": "金融機関は融資を承認した。",
    "horse": "その農場は物資の運搬に馬を使っている。",
    "eventually": "プロジェクトは数回の修正を経て最終的に利益を上げた。",
    "heat": "機器は極端な熱から保護しなければならない。",
    "excite": "新製品は発売時に顧客を興奮させた。",
    "importance": "マネージャーはデータセキュリティの重要性を説明した。",
    "distance": "倉庫までの距離は2マイル未満です。",
    "guide": "アシスタントは来訪者を会議室まで案内する。",
    "grant": "財務チームはプロジェクトを承認する前に助成金を確認した。",
    "feed": "システムはデータベースにデータを入力する。",
    "ensure": "すべてのフォームに署名があることを確認してください。",
    "chief": "最高財務責任者が予算を承認した。",
    "cool": "保管室は涼しく保つ必要がある。",
    "expert": "専門家が機器を検査した。",
    "labor": "会社は自動化によって人件費を削減した。",
    "library": "会社は従業員研修資料用のデジタルライブラリーを開設した。",
    "excellent": "そのホテルは会議向けの優れた施設を備えている。",
    "edge": "新しいシステムは競合他社に対する優位性をもたらす。",
    "camp": "会社は新しい技術者向けの研修キャンプを開催した。",
    "audience": "プレゼンテーションは聴衆に好評だった。",
    "lift": "会社は来月、制限を解除する。",
    "email": "請求書をメールで送ってください。",
    "global": "会社には世界規模の顧客基盤がある。",
    "advertise": "チームは発売前にサービスを宣伝する。",
    "extent": "報告書は損害の程度を測定している。",
    "annual": "会社は年次業績を発表した。",
    "fully": "システムは完全に稼働している。",
    "contrast": "対照的に、改訂版の計画はコストを削減する。",
    "artist": "会社はポスターのデザインを芸術家に依頼した。",
    "conflict": "マネージャーは部署間の対立を解決した。",
    "entire": "チーム全体が会議に出席した。",
    "crowd": "開店時、店の外に群衆が集まった。",
    "corner": "新しいカフェはオフィス近くの角にある。",
    "gas": "会社はエネルギー費を削減するためガスに切り替えた。",
    "category": "申請フォームでカテゴリーを選択してください。",
    "defense": "会社はサイバー攻撃への防御を強化した。",
    "cook": "シェフは会議の参加者に昼食を作る。",
    "driver": "運転手は荷物を正しい住所に届けた。",
    "ball": "その機械は摩擦を減らすためボールベアリングを使っている。",
    "cry": "診察が長引くと、その子どもは泣くかもしれない。",
    "introduction": "マネージャーは新しい方針を紹介した。",
    "confirm": "チームは締め切り前に予約を確認する。",
    "emerge": "システム更新後に問題が発生する可能性がある。",
    "concept": "その概念は研修会で説明された。",
    "island": "そのリゾートは島で会議を開催した。",
    "football": "会社はサッカーチームのスポンサーになった。",
    "flight": "アシスタントは取締役の航空便を予約した。",
    "left": "研修会の残り席は2席だけです。",
    "background": "その応募者には経理の経験がある。",
    "improvement": "報告書は売上の大幅な改善を示している。",
    "consequence": "遅延は顧客に深刻な結果をもたらした。",
    "circumstance": "このような状況では、会議は延期される。",
    "busy": "営業部は休暇シーズン中は忙しい。",
    "brain": "研究チームは脳がストレスにどう反応するかを調べた。",
    "funny": "発表者は懇親会で面白い話をした。",
    "contribute": "従業員は計画会議でアイデアを提供できる。",
    "failure": "システム障害が生産を遅らせた。",
    "bottom": "請求書の下部に合計金額が記載されている。",
    "adopt": "会社は新しい方針を採用する。",
    "combine": "2社は事業を統合する予定だ。",
    "hide": "機密ファイルを一般公開から隠してください。",
    "colleague": "同僚が契約書を確認した。",
    "bag": "書類をバッグの中に入れてください。",
    "equal": "2つの支払い金額は同じだった。",
    "expression": "契約書に「支払期限30日」という表現が出てくる。",
    "extremely": "新しい決済システムは非常に信頼性が高い。",
    "commercial": "会社は新サービスのCMを公開した。",
    "lady": "受付の女性が来訪者用バッジを渡してくれた。",
    "duty": "経費を承認するのはマネージャーの職務です。",
    "connect": "プリンターをネットワークに接続してください。",
    "cultural": "会社は海外勤務者向けに文化研修を提供している。",
    "arrange": "アシスタントは来賓の移動手段を手配する。",
    "brief": "取締役はプロジェクトについて簡単な報告をした。",
    "bird": "ホテルは鳥を食事エリアから遠ざけるためネットを設置した。",
    "demonstrate": "応募者は高いコミュニケーション能力を示した。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][700:800]
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
    print(f"reviewed 500+ Japanese examples batch 8: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
