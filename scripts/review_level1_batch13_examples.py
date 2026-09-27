#!/usr/bin/env python3
"""Review the thirteenth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "hunt": "会社はより大きな倉庫を探している。",
    "achievement": "チームの成果は年次会議で称えられた。",
    "dominate": "その会社は地域市場を支配している。",
    "acquisition": "会社は地域の競合会社の買収を発表した。",
    "laughter": "発表者が冗談を言うと部屋に笑い声が広がった。",
    "deeply": "新しい方針は会社の長期計画に大きな影響を与えた。",
    "electricity": "施設は太陽光パネルで電力を発電している。",
    "assistance": "助けが必要な場合はカスタマーサポートに連絡してください。",
    "layer": "ソフトウェアはシステムにセキュリティ層を追加する。",
    "dispute": "両社は契約上の紛争を解決した。",
    "agenda": "議長は予算案を議事次第に追加した。",
    "emphasis": "マネージャーは職場の安全を重視した。",
    "edition": "マニュアルの最新版には更新された手順が含まれている。",
    "entertainment": "ホテルは会議の参加者に娯楽を提供している。",
    "honest": "仕入先は遅延について正直に説明した。",
    "gay": "会社は同性愛者の従業員を支援し、包括的な職場づくりを進めている。",
    "framework": "その合意は将来の協力の枠組みを提供する。",
    "inch": "ディスプレイの幅は12インチです。",
    "equivalent": "交換部品は元の部品と同等です。",
    "enterprise": "その企業は国際市場へ事業を拡大した。",
    "elderly": "会社は高齢の顧客に交通手段を提供している。",
    "governor": "知事は新施設への資金提供を発表した。",
    "arrival": "大雨のため飛行機の到着が遅れた。",
    "contemporary": "オフィスは現代的なデザインだ。",
    "gate": "配送ゲートでお待ちください。",
    "ease": "新しいシステムは使いやすさを向上させる。",
    "beer": "そのレストランは夕食の客に地元のビールを提供している。",
    "assure": "注文が時間どおり届くと顧客に保証してください。",
    "episode": "会社は研修ポッドキャストのエピソードを制作した。",
    "crack": "検査員は倉庫の壁にひびを見つけた。",
    "era": "会社はデジタルサービスの新時代に入った。",
    "coverage": "保険の補償には配送中の損害が含まれる。",
    "cable": "技術者は破損したケーブルを交換した。",
    "input": "マネージャーは営業チームからの意見を歓迎した。",
    "isolate": "技術者は故障した部品を切り離した。",
    "eliminate": "新しい手順は不要な書類作業をなくす。",
    "exclude": "表示価格には税金が含まれていない。",
    "cloud": "データはクラウドに安全に保管されている。",
    "inspire": "リーダーは従業員に顧客サービスの改善を促した。",
    "grand": "ホテルには会議用の壮大なホールがある。",
    "hence": "出荷が遅れたため、顧客に連絡した。",
    "crew": "建設作業員は設置作業を完了した。",
    "false": "報告書には誤った情報が含まれている。",
    "assist": "アシスタントは顧客の申請を手伝う。",
    "formula": "その計算式は送料の合計を算出する。",
    "alter": "仕入先は納品スケジュールを変更した。",
    "anymore": "この場所ではそのサービスはもう利用できない。",
    "hero": "消防士は地域の英雄として表彰された。",
    "convert": "会社は倉庫をオフィスに改装した。",
    "beside": "新しい支店は駅の隣にある。",
    "disaster": "会社は災害復旧計画を持っている。",
    "heavily": "その地域は輸入燃料に大きく依存している。",
    "devote": "会社は従業員研修に資源を充てている。",
    "justify": "マネージャーは追加費用の理由を説明した。",
    "fascinate": "新技術は来訪者を魅了した。",
    "external": "会社は外部監査人を雇った。",
    "depression": "経済不況により高級品への需要が減少した。",
    "guilty": "裁判所は被告を有罪とした。",
    "distinction": "契約書は2つのサービスを明確に区別している。",
    "incorporate": "改訂版の計画は顧客の意見を取り入れている。",
    "evaluate": "チームは決定する前に提案を評価する。",
    "anger": "顧客の怒りは長い遅延が原因だった。",
    "currency": "為替変動が会社の利益に影響した。",
    "database": "データベースは顧客の連絡先情報を保存している。",
    "initially": "当初、そのシステムは使いにくかった。",
    "height": "荷積み場の高さは2メートルです。",
    "apparent": "新入社員に助けが必要なことは明らかだった。",
    "expansion": "会社は東南アジアへの拡張を発表した。",
    "constantly": "システムは安全性向上のため常に更新されている。",
    "badly": "輸送中に機器がひどく損傷した。",
    "everyday": "その店は日常的に使うオフィス用品を販売している。",
    "boundary": "敷地の境界は柵で示されている。",
    "essay": "編集者は掲載前に筆者へ論文を短くするよう依頼した。",
    "disorder": "診療所は新しい手順でその疾患を治療した。",
    "furniture": "オフィスは古い家具を取り替えた。",
    "apartment": "会社は長期赴任する従業員のためにアパートを手配した。",
    "demonstration": "会社は新しいソフトウェアの実演を行った。",
    "analyst": "アナリストは四半期の数値を確認した。",
    "cake": "ホテルは顧客の記念日にケーキを注文した。",
    "foundation": "建設を続ける前に建物の基礎を点検した。",
    "designer": "デザイナーは製品の新しいパッケージを作成した。",
    "innovation": "その新しい技術革新はエネルギー消費を削減した。",
    "album": "会社は年次イベントの写真アルバムを公開した。",
    "loose": "技術者は緩んだケーブルを締めた。",
    "extension": "顧客は締め切りの延長を依頼した。",
    "gradually": "システムは徐々に効率的になった。",
    "evil": "その広告では悪がブランドのヒーローの敵として描かれている。",
    "grass": "整備担当者は毎週金曜に芝生を刈る。",
    "invitation": "顧客は製品発表会への招待状を送った。",
    "frighten": "突然の警報が来訪者を怖がらせた。",
    "bid": "改装工事で、請負業者は他社より低い入札額を提示した。",
    "breed": "その農場は地域のイベント用に馬を繁殖させている。",
    "extraordinary": "会社は今年、並外れた成長を遂げた。",
    "brilliant": "技術者は設計上の問題に対する素晴らしい解決策を提案した。",
    "adviser": "財務アドバイザーは投資計画を確認した。",
    "awful": "顧客はサービスがひどかったと言った。",
    "adjust": "技術者は試験前に機器を調整した。",
    "creative": "デザイナーは創造的な解決策を考案した。",
    "agricultural": "会社は農産物を輸出している。",
    "competitor": "競合会社は先月、価格を引き下げた。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][1200:1300]
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
    print(f"reviewed 500+ Japanese examples batch 13: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
