#!/usr/bin/env python3
"""Review the third 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "experience": "マネージャーは国際営業の豊富な経験がある。",
    "once": "その契約はかつて5年間有効だった。",
    "member": "委員会の各メンバーは議事次第を受け取った。",
    "enough": "倉庫には新しい在庫を置く十分なスペースがある。",
    "bad": "悪天候により配送が遅れた。",
    "city": "市役所は新しい支店の営業許可を承認した。",
    "night": "夜勤は午後10時に始まる。",
    "able": "会社はオンラインで注文を処理できる。",
    "line": "合計金額の下に線を引いてください。",
    "although": "出荷は遅れたが、顧客はそれを受け入れた。",
    "least": "少なくとも3社の仕入先が入札した。",
    "age": "採用の判断に従業員の年齢は関係ない。",
    "low": "会社は新規顧客を引き付けるために低い価格を設定した。",
    "often": "その支店には海外からの注文がよく届く。",
    "possible": "納品日を変更することは可能です。",
    "actually": "実は、上司が私たちの予約を金曜午後に変更しました。",
    "consider": "返答する前に顧客の依頼を検討してください。",
    "parent": "親会社は合併を承認した。",
    "hard": "チームは締め切りに間に合わせるため一生懸命働いた。",
    "party": "会社のパーティーは年次会議の後に開かれる。",
    "local": "地域支店はその地域の顧客にサービスを提供している。",
    "control": "上司に電話している間、研修室のプロジェクターを操作してもらえますか。",
    "already": "経理部はすでに支払いを承認した。",
    "concern": "マネージャーは遅れている出荷について懸念を示した。",
    "lose": "出荷品が返品されると、会社は損失を被る可能性がある。",
    "almost": "プロジェクトはほぼ完了している。",
    "continue": "チームは昼食後もプロジェクトに取り組み続ける。",
    "care": "会社は顧客情報の保護に注意を払っている。",
    "expect": "出荷品は金曜までに到着する見込みです。",
    "effect": "新しい方針は従業員の士気に良い影響を与えた。",
    "ever": "この決済サービスを使ったことがありますか。",
    "anything": "何か必要なことがあれば、カスタマーサービスに連絡してください。",
    "cause": "遅延の主な原因は税関検査だった。",
    "fall": "休暇シーズンの後は売上が通常落ち込む。",
    "deal": "2社は数回の会議を経て取引をまとめた。",
    "allow": "その方針により従業員はリモート勤務ができる。",
    "base": "その研修は今後の仕事の確かな基礎となる。",
    "past": "会社は予算を設定する前に過去の売上データを確認した。",
    "power": "バックアップ発電機は停電中に電力を供給できる。",
    "center": "新しいサービスセンターは来月開業する。",
    "grow": "システム更新後に事業が成長する可能性がある。",
    "nothing": "契約には支払いの遅延を認める規定がない。",
    "mother": "私の母は地元の銀行に勤めている。",
    "matter": "マネージャーはその問題を自分で処理する。",
    "mind": "締め切りは金曜であることを覚えておいてください。",
    "office": "改装のため、オフィスは来週閉鎖される。",
    "force": "嵐のため、オフィスは早く閉めざるを得なかった。",
    "light": "技術者は会議室の照明をつけた。",
    "develop": "会社は新しいモバイルアプリを開発する予定だ。",
    "bit": "報告書には新サービスに関する役立つ情報が少し含まれている。",
    "answer": "上司は私の来四半期についての質問に答えた。",
    "figure": "売上高は目標を上回った。",
    "letter": "予約を確認する手紙を送ってください。",
    "decide": "マネージャーは依頼を承認するかどうか決めなければならない。",
    "language": "契約書の文言は明確で理解しやすい。",
    "class": "研修クラスは9時に始まる。",
    "development": "会社は新製品の開発に投資した。",
    "half": "注文の半分は予定どおり発送された。",
    "minute": "会議は10分後に始まる。",
    "food": "そのレストランは地元の仕入先から新鮮な食品を仕入れている。",
    "break": "次の会議の前に短い休憩を取ってください。",
    "clear": "指示は明確で従いやすい。",
    "future": "会社は将来、事業を拡大する予定だ。",
    "either": "どちらの選択肢でも顧客の要件を満たします。",
    "ago": "出荷品は2日前に到着した。",
    "per": "料金は1個あたりで計算される。",
    "among": "ボーナスは3人のチームメンバーで分けられた。",
    "color": "注文フォームに希望する色を記入してください。",
    "involve": "プロジェクトには複数の部署の従業員が関わる。",
    "period": "保証期間は1年間です。",
    "across": "新しい支店は地域全体の顧客にサービスを提供する。",
    "note": "納品スケジュールの変更に注意してください。",
    "history": "会社は記念パンフレットを作成する前に沿革を確認した。",
    "create": "デザインチームは新サービスのパンフレットを作成する。",
    "drive": "運転手は配送バンを倉庫まで運転する。",
    "along": "2つのオフィスは同じ通り沿いにある。",
    "eye": "在庫水準を注意して見ておいてください。",
    "music": "会社は新しい広告に音楽を使った。",
    "game": "会社は新入社員向けの研修ゲームを開発した。",
    "political": "会社は貿易に影響する可能性のある政治的変化を監視している。",
    "free": "100ドルを超える注文は配送料無料です。",
    "moment": "予定を確認しますので、少々お待ちください。",
    "policy": "会社は新しい法律を遵守するため方針を改訂した。",
    "further": "提案についてさらに詳しい情報を提供してください。",
    "body": "報告書の本文は主な調査結果を要約している。",
    "general": "ゼネラルマネージャーが提案を確認する。",
    "appear": "システム更新後にエラーが現れる可能性がある。",
    "easy": "新しいソフトウェアを使えば経費を簡単に追跡できる。",
    "individual": "各個人が改訂版の方針のコピーを受け取った。",
    "full": "倉庫は発送を待つ製品でいっぱいだ。",
    "black": "プリンターは公式文書に黒いインクを使う。",
    "perhaps": "おそらく仕入先はより早い納品日を提示できる。",
    "add": "チームは締め切り前にその品目を注文に追加する。",
    "pass": "今四半期にコンプライアンス研修に合格したい。",
    "agree": "2社は今日、最終条件に合意する可能性がある。",
    "law": "会社は新しい法律を遵守するため方針を改訂した。",
    "everything": "チェックリストで求められているものをすべて送ってください。",
    "cover": "その保険契約は修理費を補償する。",
    "paper": "アナリストは新製品についてホワイトペーパーを作成した。",
    "position": "営業職には顧客サービスの経験が必要です。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][200:300]
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
    print(f"reviewed 500+ Japanese examples batch 3: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
