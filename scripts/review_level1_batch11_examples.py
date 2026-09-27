#!/usr/bin/env python3
"""Review the eleventh 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "debt": "会社は融資を早期返済して負債を減らした。",
    "honor": "会社は契約を尊重した。",
    "blame": "マネージャーは遅延について仕入先を責めなかった。",
    "explanation": "マネージャーは遅延について説明した。",
    "arise": "システム保守中に問題が発生する可能性がある。",
    "dad": "私の父は地元の銀行に勤めている。",
    "declare": "従業員は利益相反の可能性を申告しなければならない。",
    "careful": "顧客データを入力するときは注意してください。",
    "fruit": "ホテルは地元の仕入先から新鮮な果物を購入している。",
    "analyze": "チームは締め切り前にデータを分析する。",
    "mail": "オフィスを出る前に郵便物を確認してください。",
    "anywhere": "どこからでもファイルにアクセスできます。",
    "fat": "その製品は旧版より脂肪分が少ない。",
    "entry": "入場料には会議への参加費が含まれている。",
    "fellow": "同僚がその仕入先を推薦してくれた。",
    "chemical": "工場は化学物質を安全に保管している。",
    "capture": "防犯カメラがその出来事を記録した。",
    "discount": "仕入先は大量注文に割引を提示した。",
    "chairman": "取締役会議長が提案を承認した。",
    "ear": "顧客は電話を耳に当てた。",
    "disappear": "更新後にエラーが消えた。",
    "constant": "絶え間ない騒音のため仕事が難しかった。",
    "hill": "新しい支店は街を見下ろす丘の上にある。",
    "considerable": "そのプロジェクトにはかなりの投資が必要だ。",
    "instruction": "フォームの指示に従ってください。",
    "intelligence": "アナリストは市場情報を集めた。",
    "ideal": "その場所は配送センターに最適だ。",
    "folk": "その祭りでは地域の民族音楽が披露された。",
    "guard": "警備員は夜間に入口を守っている。",
    "cat": "オフィスの猫は受付デスクの近くでよく眠っている。",
    "kiss": "そのカップルは式の後にキスをした。",
    "joint": "両社は合弁事業を発表した。",
    "compete": "その会社は市場でより大きな企業と競争している。",
    "faith": "マネージャーは新しい計画を信頼している。",
    "complaint": "マネージャーは顧客の苦情に対応した。",
    "bore": "ドリルで金属に穴を開けた。",
    "justice": "裁判所は被害者のために正義を求めた。",
    "formal": "会社は正式な通知を送った。",
    "employer": "雇用主は健康保険を提供している。",
    "latter": "2つの提案のうち、後者の方が実用的だ。",
    "ban": "会社は建物内での喫煙を禁止した。",
    "index": "物価指数は今四半期に上昇した。",
    "frequently": "システムは頻繁に更新される。",
    "circle": "フォームで正しい答えを丸で囲んでください。",
    "helpful": "サポートチームは役立つ助言をくれた。",
    "command": "その機器は音声コマンドに反応する。",
    "attractive": "会社は魅力的な福利厚生パッケージを提供している。",
    "impression": "そのプレゼンテーションは顧客に強い印象を与えた。",
    "joke": "発表者は懇親会で冗談を言った。",
    "column": "スプレッドシートには送料の列がある。",
    "electronic": "会社は電子請求書を使用している。",
    "impose": "政府は輸入品に税を課した。",
    "criminal": "警察は倉庫付近の犯罪行為を捜査した。",
    "besides": "コスト削減に加えて、新システムは時間も節約する。",
    "ancient": "博物館は地域の古代の道具を展示した。",
    "coast": "工場は海岸に位置している。",
    "ill": "従業員は今朝、病欠の連絡をした。",
    "kick": "機械は始動時に突然振動した。",
    "closely": "監査担当者は財務記録を詳しく確認した。",
    "legislation": "新しい法律は輸入手続きに影響する。",
    "county": "会社はその郡で複数の店舗を運営している。",
    "assistant": "アシスタントは会議資料を準備した。",
    "implement": "チームは締め切り前に計画を実行する。",
    "chart": "グラフは月間売上の変化を示している。",
    "attach": "領収書を経費報告書に添付してください。",
    "hell": "マネージャーは最初の週は大変だったと言った。",
    "everywhere": "会社の製品は至る所で販売されている。",
    "advise": "コンサルタントは締め切り前に顧客へ助言する。",
    "household": "調査では世帯支出を測定した。",
    "east": "その支店は国内東部の顧客にサービスを提供している。",
    "hat": "作業員は建設区域でヘルメットを着用した。",
    "furthermore": "さらに、新しいシステムは書類作業を減らす。",
    "accuse": "顧客は製品を破損したとして仕入先を責めた。",
    "absence": "マネージャー不在の間、アシスタントが会議を進行した。",
    "construct": "会社は新しい配送センターを建設する。",
    "intention": "会社には方針を変更する意図はない。",
    "dozen": "仕入先は顧客向けにサンプルを12個詰めた。",
    "gap": "研修は従業員の技術スキルの不足を補った。",
    "estate": "会社は商業用不動産に投資した。",
    "equally": "両方の仕入先は契約に同じように適していた。",
    "expose": "監査で複数の会計上の誤りが明らかになった。",
    "alive": "最近の減速にもかかわらず、市場はまだ活気がある。",
    "critic": "評論家は会社の新しい展示を称賛した。",
    "enormous": "会社は新しい機器に莫大な投資をした。",
    "emotion": "その広告は顧客との感情的なつながりを生み出す。",
    "enemy": "警備システムは潜在的な敵から会社を守る。",
    "appoint": "取締役会は新しい取締役を任命する。",
    "communicate": "プロジェクト中、チームは明確に意思疎通しなければならない。",
    "injury": "従業員は上司にけがを報告した。",
    "exhibition": "博物館は地元芸術の展覧会を開催した。",
    "immediate": "その問題には直ちに対応する必要がある。",
    "incident": "マネージャーはその出来事を警備担当に報告した。",
    "childhood": "従業員の幼少期の経験がキャリア選択に影響した。",
    "draft": "法務チームは新しい合意書の草案を作成した。",
    "accompany": "アシスタントは顧客に同行して会議へ行く。",
    "angry": "顧客は納品の遅れに腹を立てていた。",
    "knock": "マネージャーのオフィスに入る前にノックしてください。",
    "illustrate": "グラフはオンライン売上の増加を示している。",
    "imply": "結果は新しい方針が有効であることを示唆している。",
    "breakfast": "ホテルは会議の参加者に朝食を提供している。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][1000:1100]
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
    print(f"reviewed 500+ Japanese examples batch 11: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
