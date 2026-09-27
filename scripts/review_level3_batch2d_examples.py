#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review 700+ examples 751-900 in English and Japanese."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VOCAB_PATH=ROOT/"app/src/main/assets/vocabulary.json"
PHRASE_PATH=ROOT/"app/src/main/assets/vocabulary_phrase_translations.json"

EN={
"psychology":"The training course introduces basic psychology for customer service staff.",
"publish":"The company will publish its annual report next month.",
"pulse":"The nurse checked the patient's pulse at the clinic.",
"punch":"The employee used a punch to mark the metal sheet.",
"punish":"The policy does not punish employees for reporting safety concerns.",
"punishment":"The manager explained the consequences without using punishment as a threat.",
"purely":"The decision was based purely on the results of the quality test.",
"puzzle":"The missing invoice created a puzzle for the accounting team.",
"questionnaire":"Customers completed a short questionnaire after the service call.",
"quiz":"The online training includes a quiz at the end of each unit.",
"quotation":"The supplier sent a quotation for the replacement equipment.",
"rack":"The warehouse worker placed the boxes on the correct rack.",
"radar":"The airport uses radar to monitor incoming aircraft.",
"radiation":"Technicians wear protective clothing when working near radiation.",
"radius":"The delivery service operates within a ten-kilometer radius of the depot.",
"rainfall":"Heavy rainfall delayed construction at the new distribution center.",
"randomly":"The auditor randomly selected invoices for review.",
"rational":"The committee reached a rational decision after reviewing the evidence.",
"ray":"A ray of sunlight entered the office through the skylight.",
"realistic":"The project manager set a realistic completion date.",
"realm":"The new software expands the company into the realm of online payments.",
"recipe":"The chef followed the recipe when preparing lunch for the guests.",
"reinforce":"The supervisor used examples to reinforce the safety instructions.",
"rejection":"The applicant received a rejection letter after the final interview.",
"reliability":"The test measured the reliability of the new delivery system.",
"replacement":"The supplier shipped a replacement for the damaged part.",
"reproduce":"The technician could not reproduce the error on another computer.",
"reproduction":"The museum displayed a reproduction of the original document.",
"republic":"The company opened an office in the island republic.",
"resemble":"The new logo resembles the design used by the parent company.",
"reservoir":"The city checks the reservoir before approving water use.",
"resistant":"The manufacturer developed packaging resistant to moisture.",
"retrieve":"The assistant retrieved the archived contract from the database.",
"revolutionary":"The company introduced a revolutionary battery design.",
"rewrite":"The editor asked the team to rewrite the unclear instructions.",
"rhythm":"The production line operates at a steady rhythm throughout the shift.",
"ridiculous":"The customer considered the proposed surcharge ridiculous.",
"ritual":"The team has a short morning ritual before opening the store.",
"rope":"The rescue crew used a rope to move equipment safely.",
"rotate":"Employees rotate responsibility for answering the help line.",
"rotation":"The department uses a weekly rotation for reception duty.",
"rub":"The cleaner used a cloth to rub the mark from the table.",
"ruler":"The designer used a ruler to measure the label.",
"scatter":"The storm scattered the delivery documents across the loading area.",
"scenario":"The emergency plan covers a scenario in which the power fails.",
"scholarship":"The company offers a scholarship to students studying engineering.",
"scroll":"Scroll down to review the complete list of payment options.",
"selective":"The retailer is selective about the suppliers it works with.",
"semi":"The factory will operate on a semi-automated schedule.",
"seminar":"The human-resources team organized a seminar on workplace conduct.",
"sensation":"The customer reported a strange sensation after using the product.",
"sensible":"The committee approved a sensible plan for reducing costs.",
"sensitivity":"The device can detect small changes in temperature with high sensitivity.",
"separately":"Please pack the fragile items separately.",
"separation":"The office installed a screen for the separation of work areas.",
"sexuality":"The training emphasizes respect for employees regardless of sexuality.",
"shallow":"The technician found that the cable trench was too shallow.",
"shortly":"The director will arrive shortly after the meeting begins.",
"shuttle":"The hotel provides a shuttle between the airport and the conference venue.",
"similarity":"The analyst noted a similarity between this year's sales and last year's results.",
"simplify":"The new form will simplify the registration process.",
"sin":"The ethics course explains why fraud is considered a serious sin.",
"singular":"The editor changed the verb to agree with the singular subject.",
"sketch":"The architect prepared a sketch of the proposed entrance.",
"skip":"Please do not skip the safety check before starting the machine.",
"slab":"The contractor lifted a concrete slab into place.",
"slash":"The revised budget will slash unnecessary travel expenses.",
"slavery":"The museum exhibition explains the history of slavery in the region.",
"slot":"The applicant booked a slot for a video interview.",
"snake":"The grounds crew found a snake near the outdoor storage area.",
"sneeze":"The employee left the meeting after beginning to sneeze repeatedly.",
"sniff":"The dog was trained to sniff out prohibited substances at the airport.",
"socially":"The program helps new employees connect socially with their colleagues.",
"sodium":"The nutrition label shows the amount of sodium in each meal.",
"sometime":"The consultant will visit the branch sometime next week.",
"span":"The warranty has a span of three years.",
"specialty":"Network security is the consultant's specialty.",
"sperm":"The clinic stores sperm samples in a carefully monitored facility.",
"sphere":"The company is expanding its influence in the sphere of renewable energy.",
"sponsorship":"The sports club received sponsorship from a local bank.",
"spray":"The cleaner used a disinfectant spray on the counter.",
"stack":"The assistant placed a stack of forms beside the printer.",
"stadium":"The company reserved a stadium suite for its largest clients.",
"standardize":"The company will standardize its invoice format across all branches.",
"static":"The technician heard static during the conference call.",
"statistical":"The report includes a statistical analysis of customer feedback.",
"statistically":"Statistically, the redesigned process produces fewer errors.",
"straightforward":"The online application is straightforward to complete.",
"strand":"A strand of fiber was found in the product sample.",
"strictly":"The laboratory strictly controls access to its records.",
"stripe":"The designer added a blue stripe to the company vehicle.",
"sub":"The manager ordered a sub for lunch during the training session.",
"substitution":"The airline arranged a substitution when the original pilot became ill.",
"subtract":"Subtract the deposit from the final invoice amount.",
"sufficiently":"The instructions are sufficiently clear for new users.",
"suicide":"The employee assistance program provides confidential support for suicide prevention.",
"super":"The new battery delivers super performance in cold weather.",
"superior":"The test showed that the new material was superior to the old one.",
"surgeon":"The surgeon discussed the procedure with the patient.",
"surgical":"The hospital ordered new surgical equipment.",
"swap":"The two departments agreed to swap meeting rooms.",
"swell":"The wooden door may swell during the rainy season.",
"sword":"The museum displayed a ceremonial sword in the lobby.",
"syllable":"The language trainer marked the stressed syllable in each word.",
"syndrome":"The physician explained the symptoms of the syndrome to the patient.",
"synthesis":"The report is a synthesis of findings from three research teams.",
"synthetic":"The manufacturer uses synthetic fibers in the protective clothing.",
"systematic":"The auditor conducted a systematic review of the purchasing records.",
"tech":"The tech team installed the update on every office computer.",
"technically":"The device is technically ready, but staff still need training.",
"tempt":"The discount may tempt customers to place larger orders.",
"tense":"The negotiations became tense after the deadline was missed.",
"terminal":"The shipment was transferred to a different terminal at the port.",
"terribly":"The old printer works terribly when the paper is damp.",
"textbook":"The trainer used a textbook to introduce basic accounting principles.",
"thermal":"The building has thermal insulation in its outer walls.",
"thickness":"The engineer measured the thickness of the protective coating.",
"thread":"The technician found a loose thread in the safety harness.",
"threshold":"The company set a threshold for approving large purchases.",
"thumb":"The employee injured a thumb while unpacking the shipment.",
"tolerance":"The machine has a low tolerance for measurement errors.",
"ton":"The factory received a ton of recycled paper.",
"toxic":"The chemical is toxic and must be kept in a locked cabinet.",
"tract":"The developer purchased a tract of land for the new facility.",
"traditionally":"The company has traditionally closed its offices in August.",
"trait":"Reliability is an important trait for a customer-service representative.",
"transcription":"The assistant prepared a transcription of the recorded interview.",
"transformation":"The digital transformation changed how customers place orders.",
"translation":"The agency provided a translation of the contract.",
"transmission":"The technician checked the transmission in the delivery van.",
"transmit":"The device can transmit data securely to the central server.",
"transplant":"The hospital arranged a transplant consultation for the patient.",
"tremendous":"The new system has brought tremendous improvements in processing speed.",
"triangle":"The engineer marked a triangle on the inspection diagram.",
"tribe":"The museum exhibit describes the traditions of a local tribe.",
"tricky":"The contract contains a tricky clause about renewal fees.",
"tropical":"The resort imports tropical fruit for its breakfast buffet.",
"tumor":"The physician referred the patient for further tests after finding a tumor.",
"ultimate":"The ultimate goal of the project is to improve customer satisfaction.",
"underneath":"The inspector found a loose cable underneath the machine.",
"unify":"The new platform will unify customer records from every branch.",
"unity":"The director's speech promoted unity among the regional offices.",
"unstable":"The unstable shelf was removed from the storage room.",
"upward":"The latest report shows an upward trend in online sales.",
"urine":"The clinic collected a urine sample for testing.",
"usage":"The software tracks energy usage in each building.",
"utility":"The new building will share utility services with the neighboring facility.",
"utilize":"The company will utilize unused office space for training.",
"vague":"The supplier gave a vague explanation for the delivery delay.",
"validity":"The auditor checked the validity of the expense receipts.",
}

JA={
"psychology":"研修では顧客サービス担当者向けに基本的な心理学を扱う。","publish":"会社は来月、年次報告書を発行する。","pulse":"看護師は診療所で患者の脈拍を確認した。","punch":"従業員は金属板に穴を開けるためポンチを使った。","punish":"その方針は安全上の懸念を報告した従業員を罰しない。","punishment":"マネージャーは罰を脅しに使わず結果を説明した。","purely":"決定は品質検査の結果だけに基づいていた。","puzzle":"請求書が見つからず経理チームは困った。","questionnaire":"顧客はサービス対応後、短いアンケートに回答した。","quiz":"オンライン研修には各単元の最後に小テストがある。","quotation":"仕入先は交換機器の見積書を送った。","rack":"倉庫作業員は箱を正しい棚に置いた。","radar":"空港は到着する航空機を監視するためレーダーを使っている。","radiation":"技術者は放射線の近くで作業する際、防護服を着る。","radius":"配送サービスは配送拠点から半径10キロ以内で営業している。","rainfall":"大雨で新しい配送センターの建設が遅れた。","randomly":"監査人は確認する請求書を無作為に選んだ。","rational":"委員会は証拠を検討した後、合理的な決定を下した。","ray":"天窓からオフィスに一筋の光が差し込んだ。","realistic":"プロジェクトマネージャーは現実的な完成日を設定した。","realm":"新しいソフトウェアで会社はオンライン決済の分野に進出する。","recipe":"料理人は来客の昼食を作る際、レシピに従った。","reinforce":"監督者は例を使って安全指示を強調した。","rejection":"応募者は最終面接後、不採用通知を受け取った。","reliability":"試験では新しい配送システムの信頼性を測定した。","replacement":"仕入先は破損部品の交換品を発送した。","reproduce":"技術者は別のコンピューターでそのエラーを再現できなかった。","reproduction":"博物館は原本の複製を展示した。","republic":"会社はその島国に事務所を開いた。","resemble":"新しいロゴは親会社が使うデザインに似ている。","reservoir":"市は水の使用を承認する前に貯水池を確認する。","resistant":"メーカーは湿気に強い包装を開発した。","retrieve":"アシスタントはデータベースから保存済みの契約書を取り出した。","revolutionary":"会社は画期的な電池設計を導入した。","rewrite":"編集者は不明確な指示を書き直すようチームに求めた。","rhythm":"生産ラインは勤務中、一定のリズムで稼働する。","ridiculous":"顧客は提案された追加料金をばかげていると考えた。","ritual":"チームには開店前に短い朝の習慣がある。","rope":"救助隊は機器を安全に移動させるためロープを使った。","rotate":"従業員はヘルプラインへの対応を交代で担当する。","rotation":"部署は受付業務を週替わりで担当する。","rub":"清掃員は布でテーブルの跡をこすり取った。","ruler":"デザイナーは定規でラベルを測った。","scatter":"嵐で配送書類が荷積み区域に散らばった。","scenario":"緊急計画には停電した場合の想定が含まれる。","scholarship":"会社は工学を学ぶ学生に奨学金を提供している。","scroll":"下にスクロールして支払方法の全リストを確認してください。","selective":"その小売業者は取引する仕入先を慎重に選んでいる。","semi":"工場は半自動の工程で稼働する。","seminar":"人事部は職場での行動に関するセミナーを開催した。","sensation":"顧客は製品使用後に奇妙な感覚があったと報告した。","sensible":"委員会はコスト削減のための妥当な計画を承認した。","sensitivity":"その装置は高い感度で温度の小さな変化を検知できる。","separately":"壊れやすい品物は別々に梱包してください。","separation":"オフィスは作業区域を分けるためスクリーンを設置した。","sexuality":"研修では性にかかわらず従業員を尊重することを強調する。","shallow":"技術者はケーブル溝が浅すぎることに気づいた。","shortly":"取締役は会議開始後すぐに到着する。","shuttle":"ホテルは空港と会議会場の間にシャトルバスを運行している。","similarity":"アナリストは今年と昨年の売上に類似点を見つけた。","simplify":"新しいフォームで登録手続きが簡単になる。","sin":"倫理講座では詐欺が重大な罪とされる理由を説明する。","singular":"編集者は単数の主語に合わせて動詞を変えた。","sketch":"建築家は提案された入口のスケッチを作成した。","skip":"機械を始動する前に安全点検を省略しないでください。","slab":"請負業者はコンクリートの板を所定の位置に持ち上げた。","slash":"改訂予算は不要な出張費を大幅に削減する。","slavery":"博物館の展示は地域の奴隷制度の歴史を説明している。","slot":"応募者はビデオ面接の時間枠を予約した。","snake":"作業員は屋外保管区域の近くでヘビを見つけた。","sneeze":"従業員はくしゃみを繰り返し始めたため会議を退席した。","sniff":"その犬は空港で禁止物質を嗅ぎ分ける訓練を受けた。","socially":"この制度は新入社員が同僚と交流するのを助ける。","sodium":"栄養表示には各食事のナトリウム量が示されている。","sometime":"コンサルタントは来週のどこかで支店を訪れる。","span":"保証期間は3年間に及ぶ。","specialty":"ネットワークセキュリティはそのコンサルタントの専門分野だ。","sperm":"診療所は精子試料を厳重に管理された施設で保管している。","sphere":"会社は再生可能エネルギー分野で影響力を広げている。","sponsorship":"スポーツクラブは地元銀行から協賛金を受けた。","spray":"清掃員はカウンターに消毒スプレーを吹きかけた。","stack":"アシスタントはプリンターの横に用紙の束を置いた。","stadium":"会社は最大の顧客向けにスタジアムの特別席を予約した。","standardize":"会社は全支店で請求書の形式を統一する。","static":"技術者は電話会議中に雑音を聞いた。","statistical":"報告書には顧客の意見の統計分析が含まれる。","statistically":"統計的には、改訂工程の方がミスが少ない。","straightforward":"オンライン申請は簡単に入力できる。","strand":"製品サンプルから繊維が1本見つかった。","strictly":"研究所は記録へのアクセスを厳格に管理している。","stripe":"デザイナーは社用車に青い полосを加えた。","sub":"マネージャーは研修中の昼食にサンドイッチを注文した。","substitution":"元の操縦士が病気になったため、航空会社は代役を手配した。","subtract":"最終請求額から前金を差し引いてください。","sufficiently":"その指示は新規利用者にも十分明確だ。","suicide":"従業員支援制度は自殺予防のため秘密厳守で相談に応じる。","super":"新しい電池は寒い天候でも非常に高い性能を発揮する。","superior":"試験で新素材が旧素材より優れていることが分かった。","surgeon":"外科医は患者に処置について説明した。","surgical":"病院は新しい外科用機器を注文した。","swap":"2つの部署は会議室を交換することで合意した。","swell":"木製のドアは雨季に膨張することがある。","sword":"博物館はロビーに儀式用の剣を展示した。","syllable":"語学講師は各単語の強勢音節に印を付けた。","syndrome":"医師は患者にその症候群の症状を説明した。","synthesis":"報告書は3つの研究チームの調査結果をまとめたものだ。","synthetic":"メーカーは防護服に合成繊維を使っている。","systematic":"監査人は購買記録を体系的に調べた。","tech":"技術チームは全オフィスコンピューターに更新をインストールした。","technically":"装置は技術的には準備できているが、職員にはまだ研修が必要だ。","tempt":"割引で顧客はより大きな注文をしたくなるかもしれない。","tense":"締め切りに間に合わず交渉は緊迫した。","terminal":"出荷品は港で別のターミナルに移された。","terribly":"古いプリンターは用紙が湿っているとひどく調子が悪い。","textbook":"講師は基本的な会計原則を説明するため教科書を使った。","thermal":"建物は外壁に断熱材を使用している。","thickness":"技術者は保護コーティングの厚さを測定した。","thread":"技術者は安全ハーネスに緩んだ糸を見つけた。","threshold":"会社は高額購入を承認する基準額を設定した。","thumb":"従業員は出荷品を開梱中に親指を負傷した。","tolerance":"その機械は測定誤差の許容範囲が小さい。","ton":"工場は再生紙を1トン受け取った。","toxic":"その化学物質は有毒なので施錠した棚に保管しなければならない。","tract":"開発業者は新施設用に広い土地を購入した。","traditionally":"会社は伝統的に8月に事務所を閉めている。","trait":"信頼性は顧客サービス担当者に重要な特性だ。","transcription":"アシスタントは録音面接の書き起こしを作成した。","transformation":"デジタル変革で顧客の注文方法が変わった。","translation":"その代理店は契約書の翻訳を提供した。","transmission":"技術者は配送バンのトランスミッションを点検した。","transmit":"その装置は中央サーバーへ安全にデータを送信できる。","transplant":"病院は患者の移植相談を手配した。","tremendous":"新システムで処理速度が大幅に向上した。","triangle":"技術者は検査図に三角形を描いた。","tribe":"博物館の展示は地元部族の伝統を紹介している。","tricky":"契約には更新料に関する難しい条項が含まれている。","tropical":"リゾートは朝食ビュッフェ用に熱帯の果物を輸入している。","tumor":"医師は腫瘍を見つけた後、追加検査を紹介した。","ultimate":"このプロジェクトの最終目標は顧客満足度を高めることだ。","underneath":"検査員は機械の下に緩んだケーブルを見つけた。","unify":"新しいプラットフォームは全支店の顧客記録を統合する。","unity":"取締役のスピーチは地域拠点間の結束を促した。","unstable":"不安定な棚は保管室から撤去された。","upward":"最新報告書はオンライン売上の上昇傾向を示している。","urine":"診療所は検査のため尿試料を採取した。","usage":"ソフトウェアは各建物のエネルギー使用量を追跡する。","utility":"新しい建物は隣接施設と公共設備を共有する。","utilize":"会社は未使用のオフィス空間を研修に活用する。","vague":"仕入先は配送遅延について曖昧な説明をした。","validity":"監査人は経費領収書の有効性を確認した。",
}

JA["stripe"]="デザイナーは社用車に青い縞模様を加えた。"

def main() -> None:
    vocabulary=json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root=json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations=phrase_root.setdefault("translations",{})
    rows=[x for x in vocabulary if int(x.get("level",0))==3][750:900]
    expected={str(x["word"]).casefold() for x in rows}
    assert set(EN)==expected and set(JA)==expected
    changed=0
    for item in rows:
        word=str(item["word"]).casefold(); source=EN[word]
        item["example"]=source
        ex=translations.setdefault(f"builtin:{item['id']}",{}).setdefault("example",{})
        for field,value in (("source",source),("en",source),("ja",JA[word])):
            if ex.get(field)!=value: ex[field]=value; changed+=1
    VOCAB_PATH.write_text(json.dumps(vocabulary,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
    PHRASE_PATH.write_text(json.dumps(phrase_root,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
    print(f"reviewed 700+ English/Japanese examples batch 2d: {len(rows)} terms, {changed} fields")

if __name__=="__main__": main()
