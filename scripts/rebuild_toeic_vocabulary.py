#!/usr/bin/env python3
"""Rebuild the vocabulary assets for the TOEIC-oriented app.

The source vocabulary is intentionally kept as a base set. This script removes
only clearly campus-specific entries, demotes academic-only entries, adds a
curated business seed, and regenerates the phrase-translation index so that
every stable key and source string matches vocabulary.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


# These words are useful in academic English but are not useful as a core TOEIC
# business deck. They are removed rather than merely moved to a premium level.
CAMPUS_ONLY_WORDS = {
    "campus",
    "classroom",
    "coursework",
    "curriculum",
    "dissertation",
    "dorm",
    "dormitory",
    "freshman",
    "freshmen",
    "lecture",
    "lecturer",
    "midterm",
    "office-hours",
    "officehour",
    "professor",
    "registrar",
    "semester",
    "sophomore",
    "syllabus",
    "thesis",
    "tutor",
    "tutoring",
    "tuition",
    "undergraduate",
}


# Academic/scientific entries remain available, but are moved to the highest
# internal level so the business deck is the default path through the app.
ACADEMIC_ONLY_WORDS = {
    "archaeology",
    "archaeological",
    "astronomy",
    "biodiversity",
    "biology",
    "botany",
    "chemistry",
    "ecosystem",
    "geology",
    "laboratory",
    "molecule",
    "photosynthesis",
    "species",
    "zoology",
}


# Existing examples were written for campus study. These phrase replacements
# move explicit campus wording into workplace wording. If a phrase is changed,
# its old non-English translation is discarded rather than showing a translation
# for a different source sentence.
CONTEXT_REWRITES = (
    ("office hours", "scheduled meeting"),
    ("advising office", "HR office"),
    ("freshmen", "new employees"),
    ("freshman", "new employee"),
    ("professors", "managers"),
    ("professor", "manager"),
    ("roommates", "colleagues"),
    ("roommate", "colleague"),
    ("classrooms", "training rooms"),
    ("classroom", "training room"),
    ("lectures", "presentations"),
    ("lecture", "presentation"),
    ("semesters", "quarters"),
    ("semester", "quarter"),
    ("campuses", "offices"),
    ("campus", "office"),
    ("dormitories", "apartments"),
    ("dormitory", "apartment"),
    ("dorms", "apartments"),
    ("dorm", "apartment"),
    ("midterms", "performance reviews"),
    ("midterm", "performance review"),
    ("advisers", "supervisors"),
    ("adviser", "supervisor"),
    ("advisors", "supervisors"),
    ("advisor", "supervisor"),
    ("tutoring center", "training center"),
    ("tutoring", "training"),
    ("tutor", "trainer"),
    ("lecturers", "presenters"),
    ("lecturer", "presenter"),
    ("library", "resource center"),
    ("registrars", "administrators"),
    ("registrar", "administrator"),
    ("syllabi", "agendas"),
    ("syllabus", "agenda"),
    ("dissertations", "reports"),
    ("dissertation", "report"),
    ("theses", "reports"),
    ("thesis", "report"),
    ("coursework", "training work"),
    ("curriculum", "training program"),
    ("undergraduates", "trainees"),
    ("undergraduate", "trainee"),
    ("sophomores", "junior employees"),
    ("sophomore", "junior employee"),
    ("tuition", "training fees"),
    ("freshman seminar", "new-employee orientation"),
    ("biology class", "compliance training"),
    ("chemistry class", "safety training"),
    ("biology course", "training program"),
    ("math course", "accounting course"),
    ("course", "training program"),
    ("courses", "training programs"),
)

EXAMPLE_OVERRIDES = {
    "attendee": "Each attendee received a name badge at the conference.",
    "contributor": "Each contributor was recognized in the project report.",
    "headquarters": "The company moved its headquarters to Tokyo.",
    "supervisor": "Ask your supervisor before changing the schedule.",
    "resignation": "The manager accepted the employee's resignation.",
    "payroll": "The payroll team processed the salaries on Friday.",
    "vacancy": "The company posted a vacancy on its website.",
    "workload": "The supervisor adjusted the workload for the team.",
    "receipt": "Please keep the receipt for your expense report.",
    "refund": "The store issued a refund to the customer.",
    "cash flow": "The report shows that cash flow improved this quarter.",
    "vendor": "The purchasing team selected a new vendor.",
    "shipment": "The shipment arrived at the warehouse on time.",
    "warehouse": "The warehouse stores products before delivery.",
    "itinerary": "The assistant confirmed the itinerary before the business trip.",
    "departure": "The departure time was changed because of the delay.",
    "hardware": "The IT team replaced the damaged hardware.",
    "notify": "Please notify the client about the delay.",
    "postpone": "The manager decided to postpone the meeting.",
    "profitable": "The new service became profitable within a year.",
    "onboarding": "The HR team prepared an onboarding plan for new employees.",
    "deliverable": "The team submitted the deliverable before the deadline.",
    "turnover": "The company is working to reduce employee turnover.",
    "outsourcing": "Outsourcing reduced the cost of customer support.",
    "retailer": "The retailer placed a large order before the holiday season.",
    "distributor": "The distributor delivered the products to local stores.",
    "consignment": "The consignment arrived at the port on Monday.",
    "customs": "The shipment was held at customs for two days.",
    "forecasting": "Accurate forecasting helps the company plan its budget.",
    "quarterly": "The company publishes a quarterly financial report.",
    "optional": "The advanced training session is optional for employees.",
    "delegate": "The manager will delegate the task to an experienced employee.",
    "incur": "The company may incur additional shipping costs.",
    "verify": "Please verify the invoice before making payment.",
}

EXAMPLE_JA_OVERRIDES = {
    "attendee": "各出席者は会議で名札を受け取った。",
    "contributor": "各貢献者はプロジェクト報告書で評価された。",
    "minutes": "アシスタントは会議が始まる前に議事録を準備した。",
    "headquarters": "会社は本社を東京へ移転した。",
    "supervisor": "予定を変更する前に上司に確認してください。",
    "resignation": "マネージャーは従業員の退職届を受理した。",
    "payroll": "給与担当チームは金曜日に給与を処理した。",
    "vacancy": "会社はウェブサイトに求人を掲載した。",
    "workload": "上司はチームの仕事量を調整した。",
    "receipt": "経費精算のために領収書を保管してください。",
    "refund": "店は顧客に払い戻しを行った。",
    "cash flow": "報告書によると、今四半期は資金繰りが改善した。",
    "vendor": "購買チームは新しい販売業者を選定した。",
    "shipment": "出荷品は予定どおり倉庫に到着した。",
    "warehouse": "倉庫では配達前の商品を保管している。",
    "itinerary": "アシスタントは出張前に旅程を確認した。",
    "departure": "遅延のため出発時刻が変更された。",
    "hardware": "ITチームは壊れたハードウェアを交換した。",
    "notify": "遅延について顧客に通知してください。",
    "postpone": "マネージャーは会議を延期することにした。",
    "profitable": "その新サービスは1年以内に利益を生むようになった。",
    "onboarding": "人事チームは新入社員向けの入社時研修計画を準備した。",
    "deliverable": "チームは締め切り前に納品物を提出した。",
    "turnover": "会社は従業員の離職率を下げようとしている。",
    "outsourcing": "外注により顧客サポートの費用が減少した。",
    "retailer": "小売業者は休暇シーズン前に大量注文を出した。",
    "distributor": "販売代理店は商品を地域の店舗へ納品した。",
    "consignment": "委託販売品は月曜日に港へ到着した。",
    "customs": "出荷品は税関で2日間止められた。",
    "forecasting": "正確な予測は会社の予算計画に役立つ。",
    "quarterly": "会社は四半期ごとの財務報告書を発行している。",
    "optional": "上級研修は従業員にとって任意である。",
    "delegate": "マネージャーは経験豊富な従業員にその仕事を委任する。",
    "incur": "会社は追加の配送費を負担する可能性がある。",
    "verify": "支払いの前に請求書を確認してください。",
}


# word | Japanese gloss | English definition | topic | level | part of speech
BUSINESS_ROWS = """
agenda|議題、予定表|a list of topics to discuss at a meeting|Meetings|1|noun
appointment|予約、面会の約束|an arranged time to meet someone|Meetings|1|noun
attendee|出席者|a person who attends an event or meeting|Meetings|1|noun
briefing|説明会、概要説明|a short meeting that gives essential information|Meetings|2|noun
conference|会議、学会|a formal meeting for discussion|Meetings|1|noun
contributor|貢献者、寄稿者|a person who contributes work or ideas|Workplace|2|noun
discussion|議論、話し合い|a conversation about a particular subject|Meetings|1|noun
minutes|議事録|a written record of what was discussed at a meeting|Meetings|2|noun
participant|参加者|a person who takes part in an activity|Meetings|1|noun
presentation|プレゼンテーション|a formal talk that explains an idea or plan|Meetings|1|noun
proposal|提案|a plan or suggestion offered for consideration|Meetings|1|noun
seminar|セミナー|a meeting for discussion or training|Meetings|2|noun
workshop|研修会、ワークショップ|a session in which people learn or practice a skill|Workplace|1|noun
appointment|予約、面会の約束|an arranged time to meet someone|Meetings|1|noun
colleague|同僚|a person who works with you|Workplace|1|noun
department|部署、部門|a division of an organization|Workplace|1|noun
employee|従業員|a person who is paid to work for an organization|Workplace|1|noun
employer|雇用主|a person or organization that employs people|Workplace|1|noun
executive|役員、幹部|a senior manager in a business|Workplace|2|noun
headquarters|本社|the main offices of an organization|Workplace|1|noun
manager|管理職、責任者|a person responsible for controlling a business or team|Workplace|1|noun
supervisor|監督者、上司|a person who supervises workers|Workplace|1|noun
branch|支店、支部|a local office or division of an organization|Workplace|1|noun
facility|施設|a building or place designed for a particular purpose|Workplace|1|noun
personnel|人事、人員|the people employed by an organization|Human Resources|2|noun
recruit|新入社員、採用候補者|a person newly hired or selected for an organization|Human Resources|2|noun
applicant|応募者|a person who applies for a job or position|Human Resources|1|noun
candidate|候補者|a person being considered for a job or role|Human Resources|1|noun
promotion|昇進、販売促進|a move to a more important job or an effort to increase sales|Human Resources|1|noun
resignation|辞職、退職届|a formal statement that someone is leaving a job|Human Resources|2|noun
retirement|退職、定年|the act of leaving work permanently|Human Resources|1|noun
payroll|給与、給与支払簿|a list of employees and the money paid to them|Human Resources|2|noun
salary|給料、年俸|fixed regular pay for work|Human Resources|1|noun
wage|賃金|money paid for work, usually by the hour or day|Human Resources|1|noun
bonus|賞与、ボーナス|extra money paid in addition to regular pay|Human Resources|1|noun
benefit|福利厚生、利益|an advantage or payment provided by an employer|Human Resources|1|noun
vacancy|空き、求人|an unfilled job or position|Human Resources|2|noun
orientation|研修、適応指導|training that introduces a person to a new job or organization|Human Resources|1|noun
attendance|出席、勤務状況|the fact of being present at work or an event|Human Resources|1|noun
performance|業績、実績|how well a person or organization does something|Human Resources|1|noun
productivity|生産性|the rate at which work is completed|Workplace|2|noun
responsibility|責任|a duty or task that someone is expected to handle|Workplace|1|noun
workload|仕事量|the amount of work assigned to a person or team|Workplace|1|noun
deadline|締め切り|the latest time by which something must be finished|Workplace|1|noun
schedule|予定、日程|a plan that shows when activities will happen|Workplace|1|noun
shift|勤務時間帯、交代|a period of work assigned to a person|Workplace|1|noun
policy|方針、規定|an official plan or rule used by an organization|Workplace|1|noun
procedure|手順|an established way of doing something|Workplace|1|noun
regulation|規則、規制|an official rule made by an authority|Compliance|2|noun
compliance|法令遵守|the act of obeying a rule or requirement|Compliance|3|noun
contract|契約|a formal written agreement|Legal|1|noun
agreement|合意、契約|a decision or arrangement accepted by everyone|Legal|1|noun
clause|条項|a separate part of a legal document|Legal|3|noun
confidentiality|秘密保持|the protection of private information|Legal|3|noun
copyright|著作権|the legal right to control the use of creative work|Legal|2|noun
invoice|請求書|a document requesting payment for goods or services|Finance|1|noun
receipt|領収書|a written record that confirms payment|Finance|1|noun
payment|支払い|money given for goods or services|Finance|1|noun
refund|払い戻し|money returned to a customer|Finance|1|noun
revenue|収益、売上高|income earned by a business|Finance|2|noun
profit|利益|money left after costs are paid|Finance|1|noun
loss|損失|money lost by a business|Finance|1|noun
expense|費用|money spent to operate a business|Finance|1|noun
budget|予算|a plan for how money will be spent|Finance|1|noun
forecast|予測|a statement about what is likely to happen in the future|Finance|2|noun
estimate|見積もり、推定|an approximate calculation or judgment|Finance|1|noun
audit|監査|an official examination of financial records|Finance|2|noun
account|口座、勘定|a record of money held or owed|Finance|1|noun
balance|残高、均衡|the amount of money in an account|Finance|1|noun
deposit|預金、保証金|money placed in an account or paid in advance|Finance|1|noun
withdrawal|引き出し|the act of taking money out of an account|Finance|2|noun
loan|融資、貸付|money borrowed and expected to be repaid|Finance|1|noun
interest|利息、関心|money charged for borrowing money|Finance|1|noun
investment|投資|money put into something to gain a return|Finance|1|noun
capital|資本|money and assets used by a business|Finance|2|noun
cash flow|資金繰り、キャッシュフロー|the movement of money into and out of a business|Finance|2|noun
stock|在庫、株式|goods kept for sale or shares in a company|Finance|1|noun
shareholder|株主|a person who owns shares in a company|Finance|2|noun
dividend|配当|a payment made to shareholders from company profits|Finance|3|noun
client|顧客、取引先|a person or organization that receives professional services|Sales|1|noun
customer|顧客|a person or organization that buys goods or services|Sales|1|noun
consumer|消費者|a person who buys or uses goods and services|Sales|1|noun
supplier|供給業者|a company that provides goods or materials|Sales|1|noun
vendor|販売業者|a person or company that sells goods or services|Sales|2|noun
product|製品|something made or sold by a business|Sales|1|noun
service|サービス|work done for a customer|Sales|1|noun
order|注文|a request to buy something|Sales|1|noun
purchase|購入|something that is bought|Sales|1|noun
market|市場|the area or group where goods are sold|Marketing|1|noun
demand|需要|the desire or need for a product or service|Marketing|1|noun
campaign|キャンペーン|an organized effort to achieve a business goal|Marketing|1|noun
brand|ブランド|a product name or identity|Marketing|1|noun
advertisement|広告|a public notice that promotes a product or service|Marketing|1|noun
feedback|フィードバック|opinions about a product, service, or performance|Marketing|1|noun
survey|調査、アンケート|a set of questions used to collect information|Marketing|1|noun
competitor|競合他社|a person or company competing with another|Marketing|1|noun
target|目標、対象|the person or result that an activity is intended to reach|Marketing|1|noun
warranty|保証|a promise to repair or replace a product|Sales|2|noun
retail|小売|the sale of goods to the public|Sales|2|noun
wholesale|卸売|the sale of goods in large quantities|Sales|2|noun
shipment|発送品、出荷|goods sent from one place to another|Logistics|1|noun
delivery|配達、納品|the act of taking goods to a customer|Logistics|1|noun
warehouse|倉庫|a building where goods are stored|Logistics|1|noun
inventory|在庫|a complete list of goods held by a business|Logistics|2|noun
freight|貨物、運賃|goods transported in bulk|Logistics|2|noun
carrier|運送業者|a company that transports people or goods|Logistics|2|noun
route|経路、路線|the way between two places|Logistics|1|noun
destination|目的地|the place where someone or something is going|Logistics|1|noun
reservation|予約|an arrangement to keep a seat, room, or service|Travel|1|noun
itinerary|旅程|a plan showing the details of a journey|Travel|2|noun
accommodation|宿泊施設|a place where someone stays|Travel|2|noun
departure|出発|the act of leaving a place|Travel|1|noun
arrival|到着|the act of reaching a place|Travel|1|noun
delay|遅延|a period when something is late|Travel|1|noun
software|ソフトウェア|programs used by a computer|Technology|1|noun
hardware|ハードウェア|the physical parts of a computer or device|Technology|1|noun
database|データベース|an organized collection of information|Technology|2|noun
network|ネットワーク|a system of connected computers or people|Technology|1|noun
security|安全、セキュリティ|protection from danger or unauthorized access|Technology|1|noun
access|アクセス、利用権|the right or ability to use something|Technology|1|noun
update|更新|a change that makes something more current|Technology|1|noun
maintenance|保守、維持管理|work done to keep something in good condition|Technology|2|noun
achieve|達成する|to successfully complete or reach a goal|Workplace|1|verb
analyze|分析する|to examine something carefully|Workplace|1|verb
approve|承認する|to officially accept a plan or request|Workplace|1|verb
assign|割り当てる|to give someone a task or responsibility|Workplace|1|verb
authorize|認可する|to give official permission|Compliance|2|verb
calculate|計算する|to find an amount by using mathematics|Finance|1|verb
confirm|確認する|to show that information or an arrangement is correct|Communication|1|verb
coordinate|調整する|to organize people or activities so they work together|Workplace|2|verb
decrease|減少する、減らす|to become or make something smaller|Finance|1|verb
expand|拡大する|to become larger or make something larger|Business|1|verb
implement|実施する|to put a plan or decision into effect|Workplace|2|verb
improve|改善する|to make something better|Workplace|1|verb
increase|増加する、増やす|to become or make something greater|Finance|1|verb
manage|管理する|to control or organize a business or activity|Workplace|1|verb
monitor|監視する、確認する|to watch and check something over time|Workplace|1|verb
negotiate|交渉する|to discuss an agreement until everyone accepts it|Sales|2|verb
notify|通知する|to officially tell someone about something|Communication|1|verb
obtain|取得する|to get something through effort or planning|Workplace|2|verb
postpone|延期する|to delay an event until a later time|Meetings|1|verb
propose|提案する|to suggest a plan or idea|Meetings|1|verb
reduce|減らす|to make something smaller or lower|Finance|1|verb
resolve|解決する|to solve a problem or disagreement|Customer Service|2|verb
respond|返答する|to answer or react to something|Communication|1|verb
review|見直す、検討する|to examine something carefully|Workplace|1|verb
submit|提出する|to send something for consideration or approval|Workplace|1|verb
transfer|移す、異動させる|to move something or someone from one place to another|Workplace|1|verb
valid|有効な|legally or officially acceptable|Legal|2|adjective
annual|年1回の、年間の|happening once every year|Workplace|1|adjective
available|利用できる、空いている|ready for use or able to be obtained|Workplace|1|adjective
commercial|商業の|related to buying and selling|Business|2|adjective
competitive|競争力のある|able to compete successfully|Marketing|2|adjective
corporate|企業の|related to a company or business|Business|1|adjective
domestic|国内の|related to one country rather than another|Business|2|adjective
global|世界的な|involving the whole world|Business|1|adjective
internal|内部の|related to the inside of an organization|Workplace|1|adjective
international|国際的な|involving more than one country|Business|1|adjective
professional|専門的な、職業上の|related to a job or requiring special skill|Workplace|1|adjective
reliable|信頼できる|consistently good and dependable|Workplace|1|adjective
temporary|一時的な|lasting for a limited period|Workplace|1|adjective
urgent|緊急の|requiring immediate attention|Workplace|1|adjective
efficient|効率的な|working well without wasting time or resources|Workplace|1|adjective
flexible|柔軟な|able to change or adapt easily|Workplace|1|adjective
profitable|利益の出る|producing a financial gain|Finance|2|adjective
onboarding|入社時研修|the process of introducing a new employee to an organization|Human Resources|2|noun
stakeholder|利害関係者|a person or group affected by a business decision|Business|2|noun
procurement|調達|the process of obtaining goods or services for an organization|Logistics|3|noun
merger|合併|the joining of two companies into one|Business|3|noun
acquisition|買収、取得|the act of buying another company or asset|Business|3|noun
portfolio|ポートフォリオ、資産一覧|a collection of investments, products, or work|Finance|2|noun
asset|資産|something valuable owned by a person or organization|Finance|2|noun
liability|負債、責任|a debt or obligation owed by an organization|Finance|3|noun
equity|株主資本、公平性|the value of ownership in a company|Finance|3|noun
benchmark|基準、指標|a standard used for comparison|Business|2|noun
deliverable|納品物|a product or result that must be provided|Workplace|2|noun
turnover|離職率、売上高|the rate at which employees or money are replaced|Human Resources|3|noun
retention|維持、定着|the act of keeping employees or customers|Human Resources|2|noun
reimbursement|払い戻し、経費精算|money paid back for an expense|Finance|2|noun
commission|手数料、歩合|money paid to someone based on sales|Sales|2|noun
prospect|見込み客|a possible customer or business opportunity|Sales|1|noun
lead|見込み客、手がかり|a person or organization that may become a customer|Sales|1|noun
pitch|売り込み、提案|a persuasive presentation of an idea or product|Sales|2|noun
endorsement|推薦、支持|public approval or support for a product or person|Marketing|2|noun
subscription|定期購読、契約|an arrangement to receive a service regularly|Sales|1|noun
outsourcing|外注|the practice of paying another company to do work|Business|2|noun
merchandise|商品|goods offered for sale|Sales|1|noun
retailer|小売業者|a business that sells goods to consumers|Sales|1|noun
distributor|販売代理店、流通業者|a business that supplies goods to sellers|Logistics|2|noun
consignment|委託販売品、積荷|goods sent to another place for sale or delivery|Logistics|3|noun
customs|税関|the government department that controls goods entering a country|Logistics|2|noun
tariff|関税|a tax on goods entering a country|Logistics|3|noun
revenue|収益|income earned by a business|Finance|2|noun
margin|利益幅、余白|the difference between revenue and cost|Finance|2|noun
forecasting|予測|the process of predicting future results|Finance|2|noun
quarterly|四半期ごとの|happening every three months|Finance|1|adjective
monthly|毎月の|happening every month|Workplace|1|adjective
mutual|相互の|shared by two or more people or groups|Business|1|adjective
strategic|戦略的な|related to a plan for achieving a long-term goal|Business|2|adjective
operational|運営上の|related to the everyday work of an organization|Workplace|2|adjective
innovative|革新的な|introducing new ideas or methods|Business|2|adjective
adequate|十分な|good enough for a particular purpose|Workplace|1|adjective
mandatory|義務的な|required by a rule or law|Compliance|2|adjective
optional|任意の|available but not required|Workplace|1|adjective
allocate|割り当てる|to distribute money, time, or resources for a purpose|Finance|2|verb
collaborate|協力する|to work together with another person or group|Workplace|1|verb
compile|まとめる|to collect information into a single document or list|Workplace|2|verb
delegate|委任する|to give a task or responsibility to another person|Workplace|2|verb
diversify|多角化する|to develop a wider range of products or investments|Business|3|verb
facilitate|促進する|to make an action or process easier|Workplace|3|verb
incur|負担する、被る|to experience a cost or obligation|Finance|3|verb
retain|保持する|to continue to have or keep something|Business|2|verb
specify|明記する|to state something clearly and exactly|Communication|2|verb
verify|検証する|to check that something is true or accurate|Compliance|2|verb
"""


def parse_seed_rows() -> list[dict[str, object]]:
    result = []
    seen: set[str] = set()
    for raw in BUSINESS_ROWS.splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        word, meaning, definition, topic, level, part_of_speech = raw.split("|")
        key = word.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "word": word,
                "meaning": meaning,
                "meaningEn": definition,
                "topic": topic,
                "level": int(level),
                "partOfSpeech": part_of_speech,
            }
        )
    return result


def apply_context_rewrites(text: str) -> tuple[str, bool]:
    updated = text
    for old, new in CONTEXT_REWRITES:
        updated = re.sub(rf"\b{re.escape(old)}\b", new, updated, flags=re.IGNORECASE)
    return updated, updated != text


def example_for(seed: dict[str, object]) -> str:
    word = str(seed["word"])
    if word in EXAMPLE_OVERRIDES:
        return EXAMPLE_OVERRIDES[word]
    pos = str(seed["partOfSpeech"])
    topic = str(seed["topic"])
    if pos == "verb":
        return f"The manager will {word} the plan during the afternoon meeting."
    if pos == "adjective":
        return f"The company adopted a {word} approach to its daily operations."
    if topic == "Finance":
        return f"The finance team reviewed the {word} before the monthly report."
    if topic == "Logistics":
        return f"The logistics team checked the {word} before the shipment left."
    if topic == "Sales":
        return f"The sales team discussed the {word} with the client."
    if topic == "Meetings":
        return f"The assistant prepared the {word} before the meeting began."
    if topic == "Technology":
        return f"The IT team checked the {word} before the system update."
    if topic == "Travel":
        return f"The assistant confirmed the {word} before the business trip."
    return f"The team reviewed the {word} during the weekly meeting."


def build_seed_entry(seed: dict[str, object], new_id: int) -> dict[str, object]:
    example = example_for(seed)
    word = str(seed["word"])
    return {
        "id": new_id,
        "word": word,
        "wordUk": word,
        "phoneticUk": "",
        "meaning": seed["meaning"],
        "meaningEn": seed["meaningEn"],
        "synonyms": "",
        "collocations": f"{word} in business, manage the {word}, review the {word}",
        "example": example,
        "level": seed["level"],
        "topic": seed["topic"],
        "source_list": "TOEIC-business-v1",
        "meaningZh": "",
        "meaningHi": "",
        "meaningVi": "",
        "meaningKo": "",
        "meaningId": "",
        "meaningTh": "",
        "meaningEs": "",
    }


def translated_phrase(source: str, *, japanese: str | None = None) -> dict[str, str]:
    result = {"source": source, "en": source}
    if japanese:
        result["ja"] = japanese
    return result


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    old_translations = phrase_root.get("translations", {})

    original_words = {str(item.get("word", "")).casefold() for item in vocabulary}
    kept: list[dict[str, object]] = []
    changed_fields: dict[str, set[str]] = {}

    for item in vocabulary:
        word = str(item.get("word", "")).strip()
        if word.casefold() in CAMPUS_ONLY_WORDS:
            continue

        item = dict(item)
        stable_key = f"builtin:{item['id']}"
        if word.casefold() in ACADEMIC_ONLY_WORDS or item.get("topic") in {"Science", "Education"}:
            if int(item.get("level", 2)) >= 3:
                item["level"] = 5
            item["topic"] = "Academic"

        # The previous cleanup renamed this source label mechanically. Treat it
        # as legacy data instead of claiming that it was actually TOEIC-curated.
        if item.get("source_list") == "TOEIC-curated":
            item["source_list"] = "legacy-base"

        for field in ("example", "collocations"):
            current = str(item.get(field, ""))
            updated, changed = apply_context_rewrites(current)
            if changed:
                item[field] = updated
                changed_fields.setdefault(stable_key, set()).add(field)
        kept.append(item)

    existing_words = {str(item.get("word", "")).casefold() for item in kept}
    next_id = max(int(item["id"]) for item in kept) + 1
    for seed in parse_seed_rows():
        word_key = str(seed["word"]).casefold()
        if word_key in existing_words:
            continue
        entry = build_seed_entry(seed, next_id)
        kept.append(entry)
        existing_words.add(word_key)
        next_id += 1

    kept.sort(key=lambda item: int(item["id"]))

    new_translations: dict[str, object] = {}
    for item in kept:
        stable_key = f"builtin:{item['id']}"
        current_entry = old_translations.get(stable_key, {})
        output_entry: dict[str, object] = {}
        for field in ("collocations", "example"):
            source = str(item.get(field, "")).strip()
            if not source:
                continue
            if field in changed_fields.get(stable_key, set()):
                output_entry[field] = translated_phrase(source)
                continue
            if item.get("source_list") == "TOEIC-business-v1" and field == "example":
                output_entry[field] = translated_phrase(
                    source,
                    japanese=EXAMPLE_JA_OVERRIDES.get(str(item["word"])),
                )
                continue
            old_entry = current_entry.get(field)
            if isinstance(old_entry, dict) and str(old_entry.get("source", "")).strip() == source:
                output_entry[field] = old_entry
            else:
                output_entry[field] = translated_phrase(source)
        if output_entry:
            new_translations[stable_key] = output_entry

    VOCAB_PATH.write_text(
        json.dumps(kept, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    PHRASE_PATH.write_text(
        json.dumps({"schemaVersion": 1, "translations": new_translations}, ensure_ascii=False, indent=1)
        + "\n",
        encoding="utf-8",
    )

    words = [str(item["word"]).casefold() for item in kept]
    ids = [int(item["id"]) for item in kept]
    assert len(words) == len(set(words)), "duplicate vocabulary words"
    assert len(ids) == len(set(ids)), "duplicate vocabulary ids"
    assert set(new_translations).issubset({f"builtin:{item['id']}" for item in kept})
    print(f"vocabulary: {len(vocabulary)} -> {len(kept)}")
    print(f"removed campus-only: {len(vocabulary) - len([x for x in vocabulary if str(x.get('word', '')).casefold() not in CAMPUS_ONLY_WORDS])}")
    print(f"added business seed: {len(kept) - len([x for x in vocabulary if str(x.get('word', '')).casefold() not in CAMPUS_ONLY_WORDS])}")
    print(f"rewritten phrase keys: {len(changed_fields)}")
    print(f"translation keys: {len(new_translations)}")


if __name__ == "__main__":
    main()
