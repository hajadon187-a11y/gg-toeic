#!/usr/bin/env python3
"""Review the seventh 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "guess": "マネージャーは出荷品がいつ到着するか推測するしかなかった。",
    "fun": "会社は従業員向けの楽しいイベントを企画した。",
    "disease": "診療所は患者の医療記録に病気を記録した。",
    "balance": "支払いをする前に口座残高を確認してください。",
    "damage": "検査員は出荷品の損傷を記録した。",
    "basis": "その決定は顧客からのフィードバックに基づいていた。",
    "author": "著者は会社のイベントで本にサインした。",
    "basic": "研修では基本的な安全手順を扱う。",
    "encourage": "上司は新入社員にオリエンテーションへ参加するよう促した。",
    "hair": "そのサロンはヘアサービス用の新しい機器を注文した。",
    "male": "調査には男女両方の従業員が含まれていた。",
    "exercise": "従業員は出勤前に会社のジムで運動できる。",
    "income": "報告書は所得の変化が地域企業に与えた影響を説明している。",
    "dark": "照明が故障した後、倉庫は暗かった。",
    "imagine": "新しいシステムがどれほど時間を節約できるか想像してみてください。",
    "earn": "会社は前四半期に利益を得た。",
    "daughter": "彼の娘は会社の海外オフィスで働いている。",
    "define": "チームは締め切り前にプロジェクトの範囲を定義する。",
    "conclusion": "報告書はコストを削減すべきだという結論に達している。",
    "clock": "受付エリアの時計は5分進んでいる。",
    "everybody": "部署の全員がメモを受け取った。",
    "debate": "取締役会は提案された予算について議論した。",
    "green": "会社は廃棄物を減らすため環境に配慮した方針を採用した。",
    "maintain": "チームは予定に従って機器を保守する。",
    "credit": "顧客はクレジットカードで支払った。",
    "discover": "監査チームは報告書の誤りを発見した。",
    "dead": "電池が切れていたため、スキャナーは起動しなかった。",
    "afternoon": "会議は明日の午後に予定されている。",
    "extend": "顧客は締め切りを延長するよう依頼した。",
    "direction": "荷物に記載された指示に従ってください。",
    "facility": "会社は新しい生産施設を開設した。",
    "daily": "システムは毎日バックアップを作成する。",
    "clothes": "その店は地元企業に作業服を販売している。",
    "dance": "会社はイベントで来場者が踊れるようバンドを雇った。",
    "completely": "新しいシステムは古いものに完全に置き換わった。",
    "female": "調査には女性と男性の従業員が含まれていた。",
    "dream": "彼女の夢は小さなデザインスタジオを開くことだ。",
    "easily": "新しいソフトウェアは既存のコンピューターに簡単にインストールできる。",
    "agency": "広告代理店がキャンペーンを企画した。",
    "dollar": "価格が1ドル上がった。",
    "garden": "ホテルは会議の参加者向けに庭を整備している。",
    "fix": "技術者は会議前にプリンターを修理する。",
    "ahead": "休暇中のスケジュールを前もって計画してください。",
    "cross": "報告書を提出する前に数値を照合してください。",
    "candidate": "各候補者は履歴書を提出した。",
    "legal": "法務部は契約書を確認した。",
    "conversation": "マネージャーは仕入先と話し合いをした。",
    "magazine": "会社はビジネス誌に広告を掲載した。",
    "immediately": "直ちにマネージャーへ知らせてください。",
    "communication": "明確なコミュニケーションはプロジェクトに不可欠です。",
    "agent": "旅行代理店は営業チームの航空便を手配した。",
    "judge": "裁判官は判決を発表する前に事件を審理した。",
    "herself": "取締役自身が提案を承認した。",
    "generation": "新世代のソフトウェアはより少ないエネルギーを使用する。",
    "estimate": "請負業者は修理費の見積もりを提示した。",
    "favorite": "顧客はお気に入りのデザインを選んだ。",
    "difficulty": "チームは締め切りに間に合わせることの難しさを報告した。",
    "announce": "チームは締め切り前に結果を発表する。",
    "independent": "その支店は独立した事業として運営されている。",
    "majority": "従業員の大半が研修を修了した。",
    "exchange": "会社は出張前に通貨を両替する。",
    "budget": "チームは予算内に収めた。",
    "famous": "そのホテルは会議施設で有名だ。",
    "blood": "診療所は新入社員の血液検査を手配した。",
    "appropriate": "面接には適切な服装をしてください。",
    "block": "交通事故が倉庫への道路をふさいだ。",
    "count": "調査チームは必須オリエンテーションに参加する新入社員を全員数えなければならない。",
    "content": "マネージャーはプレゼンテーションの内容を確認した。",
    "invite": "チームは顧客を製品発表会に招待する。",
    "element": "信頼は良好な提携関係における重要な要素だ。",
    "effective": "新しい研修プログラムは効果的だ。",
    "correct": "請求書の誤りを訂正してください。",
    "admit": "仕入先は間違いを認めた。",
    "beat": "チームは締め切りに間に合わせるため遅くまで働いた。",
    "copy": "契約書のコピーを私に送ってください。",
    "committee": "委員会は新しい安全方針を承認した。",
    "aware": "改訂された納品スケジュールに注意してください。",
    "advice": "コンサルタントは運営費の削減について助言した。",
    "handle": "管理担当者は金曜までにスケジュール変更に対応できます。",
    "glass": "オフィスのドアにはガラスのパネルがある。",
    "administration": "経営部門は新しい方針を承認した。",
    "complex": "設置作業は1人で行うには複雑すぎる。",
    "context": "マネージャーはその決定の背景を説明した。",
    "directly": "仕入先に直接連絡してください。",
    "heavy": "倉庫に重量のある荷物が届いた。",
    "conduct": "チームは締め切り前に調査を実施する。",
    "equipment": "技術者は使用前に機器を点検した。",
    "extra": "仕入先は速達配送に追加料金を請求した。",
    "executive": "幹部は拡張計画を承認した。",
    "chair": "委員長が会議を開始した。",
    "expensive": "修理費は予想より高額だった。",
    "deliver": "チームは締め切り前に注文品を納品する。",
    "connection": "会議中にインターネット接続が切れた。",
    "collect": "チームは締め切り前にデータを集める。",
    "inform": "遅延について顧客に知らせてください。",
    "appeal": "その広告は若い専門職に訴求している。",
    "highly": "新しいソフトウェアは既存システムとの互換性が非常に高い。",
    "flat": "オフィスの屋根は平らだ。",
    "absolutely": "マネージャーは納品日について完全に確信していた。",
    "flow": "報告書は今四半期にキャッシュフローが改善したことを示している。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][600:700]
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
    print(f"reviewed 500+ Japanese examples batch 7: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
