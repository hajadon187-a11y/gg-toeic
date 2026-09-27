#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review 700+ examples 901-1050 in English and Japanese."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VOCAB_PATH=ROOT/"app/src/main/assets/vocabulary.json"
PHRASE_PATH=ROOT/"app/src/main/assets/vocabulary_phrase_translations.json"

EN={
"valve":"The technician replaced the faulty valve in the heating system.",
"vegetation":"The construction plan protects vegetation around the new facility.",
"vein":"The nurse located a vein before taking the blood sample.",
"verbal":"The manager gave verbal approval before sending the order.",
"vertical":"The warehouse uses vertical storage to save floor space.",
"virtue":"Patience is an important virtue when handling customer complaints.",
"vitamin":"The nutrition label lists the amount of vitamin C in each serving.",
"vocabulary":"The training course introduces vocabulary used in office communication.",
"vowel":"The language app helps learners practice each vowel sound.",
"weave":"The manufacturer uses a machine to weave the protective fabric.",
"wheat":"The bakery buys wheat from local farms.",
"whichever":"Please choose whichever delivery option best meets the customer's needs.",
"whoever":"Whoever opens the store must complete the morning safety check.",
"widespread":"The software update caused widespread problems across the network.",
"wisdom":"The new manager relied on the former director's wisdom during the transition.",
"workshop":"The company held a workshop on effective presentation skills.",
"yeast":"The bakery stores yeast in a cool, dry room.",
"analyse":"The analyst will analyse the survey results before Friday.",
"labour":"The contractor estimated the labour required for the renovation.",
"equate":"The report does not equate higher sales with higher customer satisfaction.",
"reside":"The company's legal department resides at the main office.",
"immigrate":"The program helps qualified workers immigrate with their families.",
"maximise":"The new schedule will maximise the use of the training rooms.",
"academy":"The company established an academy for future supervisors.",
"amend":"The parties agreed to amend the delivery clause in the contract.",
"enforce":"The supervisor must enforce the company's safety rules.",
"licence":"The driver showed a valid licence at the security gate.",
"transit":"The shipment is currently in transit to the regional warehouse.",
"discriminate":"The hiring policy prohibits managers from discriminating against applicants.",
"ignorant":"The customer was ignorant of the new return policy.",
"instruct":"The trainer will instruct employees on how to use the new system.",
"intelligent":"The intelligent software identifies unusual payment activity.",
"ministry":"The company submitted the proposal to the Ministry of Transport.",
"utilise":"The hotel will utilise its rooftop for evening events.",
"dispose":"Please dispose of confidential documents in the locked bin.",
"equip":"The company will equip the new office with energy-efficient lighting.",
"prohibit":"The policy prohibits employees from sharing passwords.",
"sole":"The supplier is the sole distributor of the product in this region.",
"eventual":"The eventual decision will depend on the safety inspection.",
"inevitable":"Some disruption is inevitable during the building renovation.",
"inspect":"A technician will inspect the elevator before it reopens.",
"minimise":"The revised process will minimise waiting time for customers.",
"terminate":"The company may terminate the agreement if payment is not received.",
"virtual":"The team held a virtual meeting with the overseas branch.",
"accommodate":"The conference room can accommodate up to forty participants.",
"attain":"The sales team worked hard to attain its quarterly target.",
"behalf":"The assistant signed the document on behalf of the director.",
"coincide":"The product launch will coincide with the store's anniversary.",
"compatible":"The new software is compatible with older operating systems.",
"passive":"The training encourages staff to take an active rather than passive role.",
"refine":"The design team will refine the proposal after receiving feedback.",
"restrain":"The company must restrain costs while demand remains uncertain.",
"rigid":"The rigid schedule left little time for equipment testing.",
"violate":"Employees who violate the privacy policy may lose system access.",
"ongoing":"The manager provided an update on the ongoing construction project.",
"persist":"The warning will persist until the software is updated.",
"reluctance":"The supplier showed reluctance to accept the revised payment terms.",
"so-called":"The so-called discount was not included in the final invoice.",
"underlying":"The audit revealed the underlying cause of the inventory error.",
"specialized":"The hospital ordered specialized equipment for the new clinic.",
"ambassador":"The ambassador attended the opening of the company's cultural center.",
"wicked":"The ethics report condemned the wicked misuse of customer data.",
"compression":"File compression reduced the size of the training videos.",
"superintendent":"The building superintendent arranged repairs to the elevators.",
"internationally":"The company operates internationally through regional partners.",
"humidity":"High humidity can damage paper products in the warehouse.",
"strengthening":"The company is strengthening its cybersecurity procedures.",
"alternatively":"Alternatively, customers may collect their orders at the branch.",
"complimentary":"The hotel offers complimentary breakfast to conference guests.",
"embassy":"The travel office contacted the embassy about the visa application.",
"distinguished":"The distinguished researcher gave a keynote speech at the conference.",
"inappropriate":"The supervisor removed an inappropriate comment from the report.",
"internship":"The engineering student completed an internship at the manufacturing plant.",
"unauthorized":"The security system detected an unauthorized login attempt.",
"collaborative":"The project uses a collaborative approach involving three departments.",
"acknowledged":"The supplier acknowledged receipt of the purchase order.",
"investigator":"The investigator interviewed employees about the missing inventory.",
"geographical":"The report compares geographical differences in delivery times.",
"periodically":"The company periodically reviews its emergency procedures.",
"accomplished":"The accomplished architect designed the new headquarters.",
"manufactured":"The parts are manufactured at the company's local plant.",
"metropolitan":"The metropolitan branch serves customers throughout the capital region.",
"resume":"The company will resume deliveries after the storm passes.",
"exceptional":"The hotel received an award for exceptional customer service.",
"threatening":"The message contained threatening language and was reported to security.",
"preservation":"The museum invested in the preservation of its historic documents.",
"isolated":"The technician isolated the faulty circuit before beginning repairs.",
"salvation":"The emergency fund provided salvation for the small business after the flood.",
"copyrighted":"The training video contains copyrighted photographs.",
"geographic":"The map shows the geographic distribution of the company's branches.",
"anticipated":"The company hired additional staff in anticipation of higher demand.",
"appreciated":"The customer's detailed feedback was greatly appreciated.",
"transparent":"The manager gave a transparent explanation of the price increase.",
"literacy":"The nonprofit offers digital literacy classes to older workers.",
"sophisticated":"The factory uses sophisticated equipment to monitor production.",
"contracting":"The company is contracting local firms for the renovation work.",
"accordingly":"The delivery date changed, and the invoice was adjusted accordingly.",
"unavailable":"The meeting room is unavailable until three o'clock.",
"transmitted":"The encrypted data was transmitted to the central server.",
"promotional":"The retailer prepared promotional materials for the summer sale.",
"coordinator":"The event coordinator confirmed the speakers' travel arrangements.",
"represented":"The attorney represented the company during the contract dispute.",
"implemented":"The hospital implemented a new visitor-registration system.",
"distributed":"The trainer distributed updated safety manuals to all employees.",
"wilderness":"The resort offers guided tours of the nearby wilderness.",
"journalism":"The company sponsored a journalism award for local reporters.",
"millennium":"The museum opened an exhibit about technology in the new millennium.",
"compressed":"The compressed file was small enough to send by email.",
"impatient":"The customer became impatient after waiting for an update.",
"excursion":"The conference package includes an afternoon excursion for guests.",
"analytical":"The analyst used an analytical method to compare the proposals.",
"monitoring":"Continuous monitoring helps the factory detect equipment problems early.",
"rendering":"The design software produced a realistic rendering of the new lobby.",
"commonwealth":"The company exports its products to several Commonwealth countries.",
"customise":"Customers can customise the color and size of the product online.",
"processing":"The bank is processing the application now.",
"relevance":"The reviewer questioned the relevance of the data to the proposal.",
"spirituality":"The wellness center offers a quiet room for spirituality and reflection.",
"miniature":"The architect presented a miniature model of the proposed hotel.",
"peninsula":"The company built a resort on a coastal peninsula.",
"sculpture":"The hotel placed a sculpture in the center of the lobby.",
"substantially":"The renovation substantially improved the efficiency of the building.",
"nonprofit":"The nonprofit provides job training for unemployed adults.",
"fragrance":"The store tested a new fragrance before adding it to the product line.",
"columnist":"The newspaper columnist wrote about the company's environmental policy.",
"petroleum":"The refinery processes petroleum for regional fuel suppliers.",
"validation":"The system requires email validation before an account can be used.",
"vocational":"The college offers vocational training in hospitality management.",
"suffering":"The clinic supports workers suffering from repetitive strain injuries.",
"broadband":"The branch upgraded its broadband connection for video meetings.",
"citizenship":"The application form asks for the applicant's citizenship.",
"confidential":"The attorney stored the confidential agreement in a locked cabinet.",
"geology":"The construction company consulted a specialist in geology before drilling.",
"signature":"The contract is not valid without the client's signature.",
"vulnerable":"The update protects vulnerable devices from security attacks.",
"exclusive":"The hotel offered an exclusive rate to members of the business club.",
"demolish":"The developer plans to demolish the old warehouse next year.",
"mainstream":"The product moved into the mainstream after a successful campaign.",
"testimony":"The witness gave testimony about the accident at the site.",
"authentic":"The restaurant serves authentic regional dishes.",
"inclusive":"The company is committed to creating an inclusive workplace.",
"astronomy":"The museum offers an astronomy program for visiting students.",
"delicate":"The courier marked the package as delicate and fragile.",
"workforce":"The company plans to expand its workforce next year.",
"sociology":"The survey team used sociology to study workplace relationships.",
"assurance":"The manager gave the client assurance that the issue would be resolved.",
"humanity":"The relief program supports the basic needs of people affected by the disaster.",
"visibility":"Heavy fog reduced visibility near the airport.",
"overturn":"The appeals panel may overturn the original decision.",
"obstacle":"Limited parking is an obstacle for customers visiting the branch.",
}

JA={
"valve":"技術者は暖房システムの故障したバルブを交換した。","vegetation":"建設計画は新施設周辺の植物を保護している。","vein":"看護師は採血前に静脈を確認した。","verbal":"マネージャーは注文を送る前に口頭で承認した。","vertical":"倉庫は床面積を節約するため垂直保管を使っている。","virtue":"顧客の苦情に対応する際、忍耐は重要な美徳だ。","vitamin":"栄養表示には1食分のビタミンC量が記載されている。","vocabulary":"研修ではオフィスコミュニケーションで使う語彙を扱う。","vowel":"語学アプリは各母音の音を練習できる。","weave":"メーカーは機械で防護布を織っている。","wheat":"パン工場は小麦を地元の農家から購入している。","whichever":"顧客の要望に最も合う配送方法を選んでください。","whoever":"店を開ける人は朝の安全点検を完了しなければならない。","widespread":"ソフトウェア更新でネットワーク全体に広範な問題が発生した。","wisdom":"新しいマネージャーは移行期間中、前任者の知恵を頼りにした。","workshop":"会社は効果的なプレゼンテーション技能の研修会を開いた。","yeast":"パン工場は酵母を涼しく乾燥した部屋に保管している。","analyse":"アナリストは金曜日までに調査結果を分析する。","labour":"請負業者は改装に必要な労働力を見積もった。","equate":"報告書は売上増加を顧客満足度の向上と同一視していない。","reside":"会社の法務部門は本社に置かれている。","immigrate":"この制度は資格のある労働者が家族と移住するのを支援する。","maximise":"新しい日程で研修室を最大限に活用できる。","academy":"会社は将来の監督者向けの研修校を設立した。","amend":"両当事者は契約の納品条項を修正することで合意した。","enforce":"監督者は会社の安全規則を徹底しなければならない。","licence":"運転手は警備ゲートで有効な免許証を提示した。","transit":"出荷品は現在、地域倉庫へ輸送中だ。","discriminate":"採用方針は管理職が応募者を差別することを禁じている。","ignorant":"顧客は新しい返品方針を知らなかった。","instruct":"講師は新システムの使い方を従業員に指導する。","intelligent":"その知的なソフトウェアは異常な支払活動を特定する。","ministry":"会社は運輸省に提案書を提出した。","utilise":"ホテルは屋上を夜のイベントに活用する。","dispose":"機密書類は施錠できる箱に廃棄してください。","equip":"会社は新オフィスに省エネ照明を備え付ける。","prohibit":"方針は従業員がパスワードを共有することを禁じている。","sole":"その仕入先はこの地域での唯一の販売代理店だ。","eventual":"最終的な決定は安全検査の結果次第だ。","inevitable":"建物の改装中にある程度の混乱は避けられない。","inspect":"技術者はエレベーターの再開前に点検する。","minimise":"改訂工程は顧客の待ち時間を最小限にする。","terminate":"支払いが届かなければ会社は契約を打ち切ることがある。","virtual":"チームは海外支店とオンライン会議を開いた。","accommodate":"会議室には最大40人を収容できる。","attain":"営業チームは四半期目標の達成に懸命に取り組んだ。","behalf":"アシスタントは取締役に代わって書類に署名した。","coincide":"製品発売は店舗の記念日と重なる。","compatible":"新しいソフトウェアは古いOSと互換性がある。","passive":"研修では受け身ではなく積極的な役割を奨励する。","refine":"デザイン部は意見を受けて提案をさらに洗練する。","restrain":"需要が不確かな間、会社は費用を抑えなければならない。","rigid":"厳格な日程では機器試験の時間がほとんどなかった。","violate":"プライバシー方針に違反した従業員はシステム利用権を失うことがある。","ongoing":"マネージャーは進行中の建設計画について最新情報を伝えた。","persist":"ソフトウェアが更新されるまで警告は表示され続ける。","reluctance":"仕入先は改訂された支払条件を受け入れるのをためらった。","so-called":"いわゆる割引は最終請求書に反映されていなかった。","underlying":"監査で在庫誤差の根本原因が明らかになった。","specialized":"病院は新診療所向けに専門機器を注文した。","ambassador":"大使は会社の文化センター開館式に出席した。","wicked":"倫理報告書は顧客データの悪質な悪用を非難した。","compression":"ファイル圧縮で研修動画のサイズが小さくなった。","superintendent":"ビル管理者はエレベーターの修理を手配した。","internationally":"会社は地域パートナーを通じて国際的に事業を展開している。","humidity":"高い湿度は倉庫内の紙製品を傷めることがある。","strengthening":"会社はサイバーセキュリティ手順を強化している。","alternatively":"別の方法として、顧客は支店で注文品を受け取れる。","complimentary":"ホテルは会議参加者に無料の朝食を提供する。","embassy":"旅行窓口はビザ申請について大使館に問い合わせた。","distinguished":"著名な研究者が会議で基調講演を行った。","inappropriate":"監督者は報告書から不適切なコメントを削除した。","internship":"工学部の学生は製造工場でインターンシップを終えた。","unauthorized":"警備システムは不正なログイン試行を検知した。","collaborative":"このプロジェクトは3部署が関わる協働型で進めている。","acknowledged":"仕入先は発注書を受け取ったことを確認した。","investigator":"調査員は紛失在庫について従業員に聞き取りをした。","geographical":"報告書は配送時間の地理的な違いを比較している。","periodically":"会社は緊急手順を定期的に見直している。","accomplished":"その熟練した建築家が新本社を設計した。","manufactured":"部品は会社の国内工場で製造されている。","metropolitan":"首都圏の支店は都市全体の顧客に対応する。","resume":"嵐が過ぎれば会社は配送を再開する。","exceptional":"ホテルは卓越した顧客サービスで賞を受けた。","threatening":"そのメッセージには脅迫的な表現があり、警備に報告された。","preservation":"博物館は歴史的文書の保存に投資した。","isolated":"技術者は修理前に故障回路を切り離した。","salvation":"緊急基金は洪水後の小企業に救いをもたらした。","copyrighted":"研修動画には著作権で保護された写真が含まれる。","geographic":"地図は会社支店の地理的分布を示している。","anticipated":"会社は需要増加を見越して追加の従業員を雇った。","appreciated":"顧客からの詳しい意見は大いに歓迎された。","transparent":"マネージャーは値上げについて透明性のある説明をした。","literacy":"非営利団体は高齢労働者にデジタル literacy 講座を提供する。","sophisticated":"工場は生産を監視する高度な機器を使っている。","contracting":"会社は改装工事を地元企業に委託している。","accordingly":"納期が変わったため、請求書もそれに応じて修正された。","unavailable":"会議室は3時まで利用できない。","transmitted":"暗号化されたデータが中央サーバーに送信された。","promotional":"小売業者は夏のセール用の販促資料を作成した。","coordinator":"イベントコーディネーターは講演者の移動手配を確認した。","represented":"弁護士は契約紛争で会社を代理した。","implemented":"病院は新しい来訪者登録システムを導入した。","distributed":"講師は全従業員に改訂版の安全マニュアルを配布した。","wilderness":"リゾートは近隣の自然地域へのガイド付きツアーを提供する。","journalism":"会社は地元記者向けのジャーナリズム賞を後援した。","millennium":"博物館は新千年紀の技術に関する展示を開いた。","compressed":"圧縮ファイルはメールで送れるほど小さくなった。","impatient":"顧客は更新を待ち続けて焦り始めた。","excursion":"会議パッケージには参加者向けの午後の小旅行が含まれる。","analytical":"アナリストは提案を比較するため分析的な方法を使った。","monitoring":"継続的な監視で工場は機器の問題を早期に発見できる。","rendering":"設計ソフトは新ロビーの写実的な画像を作成した。","commonwealth":"会社は複数の英連邦諸国に製品を輸出している。","customise":"顧客はオンラインで製品の色とサイズをカスタマイズできる。","processing":"銀行は現在、申請を処理している。","relevance":"審査担当者はデータが提案に関連するか疑問を呈した。","spirituality":"ウェルネスセンターは心静かに内省できる部屋を設けている。","miniature":"建築家は提案ホテルの縮尺模型を提示した。","peninsula":"会社は海岸の半島にリゾートを建設した。","sculpture":"ホテルはロビー中央に彫刻を置いた。","substantially":"改装で建物の効率が大幅に改善した。","nonprofit":"非営利団体は失業中の成人に職業訓練を提供する。","fragrance":"店は新しい香りを商品ラインに加える前に試験した。","columnist":"新聞のコラムニストは会社の環境方針について書いた。","petroleum":"製油所は地域の燃料供給業者向けに石油を精製する。","validation":"システムを使うにはアカウント登録前にメール認証が必要だ。","vocational":"大学はホテル経営の職業訓練を提供している。","suffering":"診療所は反復動作によるけがに苦しむ従業員を支援する。","broadband":"支店はビデオ会議用にブロードバンド回線を更新した。","citizenship":"申請書には申請者の国籍を記入する欄がある。","confidential":"弁護士は機密契約書を施錠した戸棚に保管した。","geology":"建設会社は掘削前に地質学の専門家へ相談した。","signature":"顧客の署名がなければ契約は有効ではない。","vulnerable":"更新プログラムは脆弱な端末をセキュリティ攻撃から守る。","exclusive":"ホテルはビジネスクラブ会員に限定料金を提供した。","demolish":"開発業者は来年、古い倉庫を取り壊す予定だ。","mainstream":"その製品は成功したキャンペーン後に主流になった。","testimony":"証人は現場の事故について証言した。","authentic":"そのレストランは本格的な郷土料理を提供している。","inclusive":"会社は誰もが働きやすい職場づくりに取り組んでいる。","astronomy":"博物館は訪問学生向けに天文学の講座を開く。","delicate":"宅配業者は荷物に壊れ物の表示を付けた。","workforce":"会社は来年、従業員数を増やす計画だ。","sociology":"調査チームは職場の人間関係を研究するため社会学を用いた。","assurance":"マネージャーは問題を解決すると顧客に保証した。","humanity":"救援計画は災害被災者の基本的なニーズを支援する。","visibility":"濃霧で空港周辺の視界が悪くなった。","overturn":"不服審査委員会は元の決定を覆す可能性がある。","obstacle":"駐車場の少なさは支店を訪れる顧客の障害になっている。",
}

JA["literacy"]="非営利団体は高齢労働者にデジタル活用講座を提供する。"

def main() -> None:
    vocabulary=json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root=json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations=phrase_root.setdefault("translations",{})
    rows=[x for x in vocabulary if int(x.get("level",0))==3][900:1050]
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
    print(f"reviewed 700+ English/Japanese examples batch 3a: {len(rows)} terms, {changed} fields")

if __name__=="__main__": main()
