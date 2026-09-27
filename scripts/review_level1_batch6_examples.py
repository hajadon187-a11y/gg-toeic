#!/usr/bin/env python3
"""Review the sixth 100 TOEIC 500+ example translations in Japanese."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


JA = {
    "occur": "システム保守中に遅延が発生する可能性がある。",
    "alone": "コンサルタントは監査に一人で取り組んだ。",
    "drug": "診療所は各薬品を安全なキャビネットに保管している。",
    "direct": "顧客からの問い合わせはサポートチームに回してください。",
    "director": "取締役は改訂版の予算を承認した。",
    "clearly": "指示にはフォームの提出方法が明確に説明されている。",
    "lack": "スタッフ不足が遅延を引き起こした。",
    "depend": "最終的な費用は配送方法によって変わる可能性がある。",
    "department": "マネージャーは彼女を経理部に異動させた。",
    "gain": "会社は新規顧客の獲得を目指している。",
    "argue": "双方は契約条件をめぐって言い争った。",
    "board": "取締役会は拡張計画を承認した。",
    "holiday": "オフィスは祝日のため休業する。",
    "mark": "改訂版の契約書で変更箇所に印を付けてください。",
    "church": "教会は屋根の修理を請負業者に依頼した。",
    "machine": "IT部門はシステム更新後に機械を監視した。",
    "achieve": "チームは締め切り前に売上目標を達成した。",
    "item": "請求書の各項目を確認してください。",
    "cent": "1個あたりの価格が1セント上がった。",
    "floor": "会議室は3階にあります。",
    "anyone": "質問がある方は誰でもヘルプデスクに連絡してください。",
    "method": "新しい方法により処理時間が短縮される。",
    "election": "会社は従業員委員会の選挙を行った。",
    "military": "その会社は軍に機器を供給している。",
    "hotel": "アシスタントは来訪する顧客のためにオフィス近くのホテルを予約した。",
    "club": "ビジネスクラブは交流イベントを開催した。",
    "below": "印刷された氏名の下に署名してください。",
    "movie": "会社は職場の安全に関する短編映画を制作した。",
    "doctor": "医師は会社の診療所で従業員を診察した。",
    "discussion": "その議論は配送費を削減する方法に焦点を当てた。",
    "challenge": "最大の課題は締め切りに間に合わせることだ。",
    "nation": "会社は多くの国に製品を輸出している。",
    "nearly": "プロジェクトはほぼ完了している。",
    "link": "請求書をダウンロードするにはリンクをクリックしてください。",
    "despite": "遅延にもかかわらず、出荷品は今日到着した。",
    "introduce": "チームは会議で製品を紹介する。",
    "advantage": "新しいシステムは競合他社に対する優位性をもたらす。",
    "marry": "私の同僚は来春結婚する。",
    "mile": "倉庫は港から2マイル離れている。",
    "ability": "応募者は問題解決能力を示した。",
    "card": "受付で身分証明書を提示してください。",
    "hospital": "病院は救急部門用の新しい機器を注文した。",
    "interview": "マネージャーは明日、3人の候補者と面接する。",
    "agreement": "両社は合意書に署名した。",
    "capital": "会社は事業拡大のため資本を調達した。",
    "popular": "新サービスは中小企業に人気がある。",
    "beautiful": "そのホテルからは港の美しい景色が見える。",
    "fear": "遅延への恐れから、顧客は注文をキャンセルした。",
    "aim": "そのキャンペーンはブランド認知度の向上を目指している。",
    "husband": "彼女の夫は運送会社に勤めている。",
    "access": "従業員はパスワードでシステムにアクセスする必要がある。",
    "movement": "税関により商品の移動が遅れた。",
    "identify": "チームは締め切り前に問題を特定する。",
    "loss": "会社は第1四半期に損失を計上した。",
    "modern": "会社は最新のセキュリティシステムを導入した。",
    "bus": "シャトルバスは午後6時にオフィスを出発する。",
    "conference": "当社は会議で最新ソフトウェアを展示する。",
    "natural": "その製品は天然素材で作られている。",
    "express": "明日の上司との会議で懸念を伝えたい。",
    "indicate": "希望する納品日を記入してください。",
    "attend": "全従業員は安全説明会に出席しなければならない。",
    "brother": "私の兄は営業部で働いている。",
    "investment": "最新の報告書は投資が地域企業に与えた影響を説明している。",
    "organize": "アシスタントは日付順にファイルを整理する。",
    "beyond": "修理費は当初の見積もりを超えていた。",
    "fish": "そのレストランは地元の仕入先から新鮮な魚を仕入れている。",
    "potential": "その設計にはエネルギー使用量を削減できる可能性がある。",
    "energy": "新しい機器はより少ないエネルギーを使用する。",
    "file": "支払い後に請求書をファイルしてください。",
    "bar": "ホテルのバーは会議の参加者も利用できます。",
    "deep": "倉庫は工業団地の奥深くにある。",
    "except": "夜勤の従業員を除き、全員が出席した。",
    "clean": "使用後は機器を清掃してください。",
    "advance": "会社は注文の前金を支払った。",
    "fill": "金曜までに申請書に記入してください。",
    "generally": "そのサービスは通常、9時から5時まで利用できる。",
    "avoid": "チームはスケジュールを確認して遅延を避ける。",
    "goal": "チームの目標は顧客満足度を高めることだ。",
    "associate": "顧客はそのブランドを品質と結び付けている。",
    "blue": "青いフォルダーには署名済み契約書が入っている。",
    "box": "サンプルを箱の中に入れてください。",
    "huge": "会社は海外から大口注文を受けた。",
    "instance": "これは請求ミスの一例です。",
    "cold": "低温保管室は施錠しておく必要がある。",
    "assume": "納品日が変更されたと思い込まないでください。",
    "baby": "会社は子どもが生まれた従業員に育児休暇を提供している。",
    "doubt": "仕入先が金曜までに納品できるか疑わしい。",
    "competition": "会社は市場で激しい競争に直面している。",
    "argument": "マネージャーは納品スケジュールをめぐる口論を収めた。",
    "adult": "荷物の受け取りには成人の署名が必要です。",
    "fly": "取締役は会議のため大阪へ飛行機で向かう。",
    "document": "製品を返品する前に損傷を記録してください。",
    "application": "金曜までに申請書を提出してください。",
    "hot": "暑い天候により屋外設置が遅れた。",
    "bill": "経理部は電気料金を支払った。",
    "central": "中央オフィスがすべての国際注文を処理する。",
    "career": "研修プログラムは営業職としてのキャリアを支援する。",
    "anyway": "注文は遅れたが、顧客は新しい日程を受け入れた。",
    "dog": "会社はオフィス内への介助犬の同伴を認めている。",
    "dress": "従業員は顧客との会議にふさわしい服装をすべきだ。",
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    level_rows = [item for item in vocabulary if int(item.get("level", 0)) == 1][500:600]
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
    print(f"reviewed 500+ Japanese examples batch 6: {len(level_rows)} terms, {changed} fields")


if __name__ == "__main__":
    main()
