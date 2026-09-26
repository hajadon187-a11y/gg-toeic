#!/usr/bin/env python3
"""Repair high-confidence vocabulary quality defects found by the full audit.

This is intentionally data-only: it does not call a translation API.  The
changes are limited to malformed examples, missing/misaligned phrase records,
duplicate or fragmentary collocations, and clearly untranslated text.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"
LANGUAGES = ("ja", "zh", "hi", "vi", "ko", "id", "th", "es")


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root["translations"]
    by_id = {item["id"]: item for item in vocabulary}

    def set_example(item_id: int, source: str, values: dict[str, str]) -> None:
        item = by_id[item_id]
        item["example"] = source
        entry = translations.setdefault(f"builtin:{item_id}", {})
        example = entry.setdefault("example", {})
        example["source"] = source
        for language in LANGUAGES:
            if language in values:
                example[language] = values[language]
        example["en"] = source

    def set_collocations(
        item_id: int, source: str, values: dict[str, str], *, update_vocab: bool = True
    ) -> None:
        if update_vocab:
            by_id[item_id]["collocations"] = source
        entry = translations.setdefault(f"builtin:{item_id}", {})
        collocations = entry.setdefault("collocations", {})
        collocations["source"] = source
        for language in LANGUAGES:
            collocations[language] = values[language]
        collocations["en"] = source

    def set_meaning(item_id: int, language: str, value: str) -> None:
        by_id[item_id][{"ja": "meaning", "zh": "meaningZh", "hi": "meaningHi", "vi": "meaningVi", "ko": "meaningKo", "id": "meaningId", "th": "meaningTh", "es": "meaningEs"}[language]] = value

    # These examples either used only a derived form of the headword or had a
    # clearly broken translation.  The revised English sentences contain the
    # actual headword and preserve the intended meaning.
    set_example(
        1537,
        "The anthropology professor traced the movement of farming communities to the west across North America.",
        {
            "ja": "人類学の教授は、北米を横断して西へ移動した農耕共同体の動きをたどった。",
            "zh": "人类学教授追溯了农耕社区向西穿越北美的迁移。",
            "hi": "मानवविज्ञान के प्रोफेसर ने उत्तरी अमेरिका में कृषक समुदायों के पश्चिम की ओर बढ़ने का पता लगाया।",
            "vi": "Giáo sư nhân học đã lần theo sự di chuyển về phía tây của các cộng đồng nông nghiệp qua Bắc Mỹ.",
            "ko": "인류학 교수는 북아메리카를 가로질러 서쪽으로 이동한 농경 공동체의 움직임을 추적했다.",
            "id": "Profesor antropologi menelusuri perpindahan komunitas pertanian ke arah barat melintasi Amerika Utara.",
            "th": "ศาสตราจารย์มานุษยวิทยาติดตามการเคลื่อนตัวไปทางตะวันตกของชุมชนเกษตรกรรมทั่วอเมริกาเหนือ",
            "es": "El profesor de antropología rastreó el movimiento hacia el oeste de las comunidades agrícolas por Norteamérica.",
        },
    )
    set_example(
        4920,
        "The professor's claim began to stir debate during our first-year history seminar.",
        {
            "ja": "教授の主張は、1年生向けの歴史セミナーで議論を巻き起こし始めた。",
            "zh": "教授的观点开始在我们的大一历史研讨课上引发争论。",
            "hi": "प्रोफेसर के दावे ने हमारी प्रथम-वर्ष इतिहास संगोष्ठी में बहस छेड़ दी।",
            "vi": "Nhận định của giáo sư bắt đầu làm dấy lên cuộc tranh luận trong hội thảo lịch sử năm nhất của chúng tôi.",
            "ko": "교수의 주장은 우리 신입생 역사 세미나에서 논쟁을 일으키기 시작했다.",
            "id": "Klaim profesor itu mulai memicu perdebatan dalam seminar sejarah tahun pertama kami.",
            "th": "ข้อกล่าวอ้างของศาสตราจารย์เริ่มจุดชนวนการถกเถียงในสัมมนาประวัติศาสตร์สำหรับนักศึกษาปีหนึ่งของเรา",
            "es": "La afirmación del profesor empezó a suscitar debate durante nuestro seminario de historia de primer año.",
        },
    )
    set_example(
        4980,
        "The professor explained how the prefix anti- appears in words such as antiwar and anti-corruption.",
        {
            "ja": "教授は、anti-という接頭辞がantiwarやanti-corruptionなどの語に現れる仕組みを説明した。",
            "zh": "教授解释了前缀 anti- 如何出现在 antiwar 和 anti-corruption 等词中。",
            "hi": "प्रोफेसर ने समझाया कि anti- उपसर्ग antiwar और anti-corruption जैसे शब्दों में कैसे आता है।",
            "vi": "Giáo sư giải thích tiền tố anti- xuất hiện như thế nào trong các từ như antiwar và anti-corruption.",
            "ko": "교수는 anti-라는 접두사가 antiwar와 anti-corruption 같은 단어에 어떻게 나타나는지 설명했다.",
            "id": "Profesor menjelaskan bagaimana prefiks anti- muncul dalam kata-kata seperti antiwar dan antikorupsi.",
            "th": "ศาสตราจารย์อธิบายว่าคำนำหน้า anti- ปรากฏในคำอย่าง antiwar และ anti-corruption ได้อย่างไร",
            "es": "El profesor explicó cómo aparece el prefijo anti- en palabras como antiwar y anticorrupción.",
        },
    )
    set_example(
        5401,
        "The psychology survey will span two semesters and include students from four academic departments.",
        {
            "ja": "その心理学調査は2学期にわたり、4つの学部の学生を対象にする予定だ。",
            "zh": "这项心理学调查将历时两个学期，并包括来自四个学系的学生。",
            "hi": "यह मनोविज्ञान सर्वेक्षण दो सेमेस्टर तक चलेगा और इसमें चार शैक्षणिक विभागों के छात्र शामिल होंगे।",
            "vi": "Khảo sát tâm lý học sẽ kéo dài hai học kỳ và gồm sinh viên từ bốn khoa.",
            "ko": "그 심리학 조사는 두 학기 동안 진행되며 네 개 학과의 학생들이 참여할 예정이다.",
            "id": "Survei psikologi itu akan berlangsung selama dua semester dan melibatkan mahasiswa dari empat departemen akademik.",
            "th": "การสำรวจทางจิตวิทยานี้จะกินเวลาสองภาคการศึกษาและจะมีนักศึกษาจากสี่ภาควิชาร่วมด้วย",
            "es": "La encuesta de psicología abarcará dos semestres e incluirá a estudiantes de cuatro departamentos académicos.",
        },
    )

    # Correct the US spelling in the vocabulary record so its phrase key is
    # identical to the phrase dictionary source.
    set_collocations(
        2792,
        "highly civilized society, civilized behavior, civilized world, civilized values",
        {
            "ja": "高度に文明化された社会、礼儀正しい振る舞い、文明世界、文明社会の価値観",
            "zh": "高度文明的社会，文明行为，文明世界，文明价值观",
            "hi": "अत्यंत सभ्य समाज, सभ्य व्यवहार, सभ्य दुनिया, सभ्य मूल्य",
            "vi": "xã hội hết sức văn minh, hành vi văn minh, thế giới văn minh, các giá trị văn minh",
            "ko": "고도로 문명화된 사회, 문명화된 행동, 문명 세계, 문명화된 가치관",
            "id": "masyarakat yang sangat beradab, perilaku beradab, dunia beradab, nilai-nilai beradab",
            "th": "สังคมที่มีอารยธรรมอย่างสูง, พฤติกรรมที่มีอารยธรรม, โลกที่มีอารยธรรม, ค่านิยมที่มีอารยธรรม",
            "es": "sociedad altamente civilizada, comportamiento civilizado, mundo civilizado, valores civilizados",
        },
    )

    # Restore the three missing all-language collocation records and repair the
    # two especially unnatural English collocations in the source data.
    set_collocations(
        2791,
        "civilised society, highly civilised, civilised behaviour, civilised world, civilised nation",
        {
            "ja": "文明的な社会、高度に文明化された、文明的な振る舞い、文明世界、文明的な国",
            "zh": "文明社会，高度文明的，文明行为，文明世界，文明国家",
            "hi": "सभ्य समाज, अत्यंत सभ्य, सभ्य व्यवहार, सभ्य दुनिया, सभ्य राष्ट्र",
            "vi": "xã hội văn minh, hết sức văn minh, hành vi văn minh, thế giới văn minh, quốc gia văn minh",
            "ko": "문명화된 사회, 고도로 문명화된, 문명화된 행동, 문명 세계, 문명화된 국가",
            "id": "masyarakat beradab, sangat beradab, perilaku beradab, dunia beradab, negara beradab",
            "th": "สังคมที่มีอารยะ, มีอารยธรรมอย่างสูง, พฤติกรรมที่มีอารยะ, โลกที่มีอารยธรรม, ประเทศที่มีอารยะ",
            "es": "sociedad civilizada, muy civilizado, comportamiento civilizado, mundo civilizado, nación civilizada",
        },
    )
    set_collocations(
        2886,
        "field archaeologist, marine archaeologist, professional archaeologist, team of archaeologists, archaeologist discovers artifacts",
        {
            "ja": "フィールド考古学者、海洋考古学者、専門の考古学者、考古学者のチーム、考古学者が遺物を発見する",
            "zh": "田野考古学家，海洋考古学家，专业考古学家，考古学家团队，考古学家发现文物",
            "hi": "क्षेत्रीय पुरातत्वविद्, समुद्री पुरातत्वविद्, पेशेवर पुरातत्वविद्, पुरातत्वविदों की टीम, पुरातत्वविद् कलाकृतियाँ खोजता है",
            "vi": "nhà khảo cổ thực địa, nhà khảo cổ biển, nhà khảo cổ chuyên nghiệp, nhóm các nhà khảo cổ, nhà khảo cổ phát hiện hiện vật",
            "ko": "현장 고고학자, 해양 고고학자, 전문 고고학자, 고고학자 팀, 고고학자가 유물을 발견하다",
            "id": "arkeolog lapangan, arkeolog kelautan, arkeolog profesional, tim arkeolog, arkeolog menemukan artefak",
            "th": "นักโบราณคดีภาคสนาม, นักโบราณคดีทางทะเล, นักโบราณคดีมืออาชีพ, ทีมนักโบราณคดี, นักโบราณคดีค้นพบโบราณวัตถุ",
            "es": "arqueólogo de campo, arqueólogo marino, arqueólogo profesional, equipo de arqueólogos, el arqueólogo descubre artefactos",
        },
    )
    set_collocations(
        3094,
        "school counsellor, marriage counsellor, grief counsellor, counsellor training",
        {
            "ja": "スクールカウンセラー、結婚カウンセラー、グリーフカウンセラー、カウンセラー研修",
            "zh": "学校辅导员，婚姻咨询师，哀伤咨询师，咨询师培训",
            "hi": "स्कूल काउंसलर, विवाह काउंसलर, शोक काउंसलर, काउंसलर प्रशिक्षण",
            "vi": "cố vấn học đường, chuyên viên tư vấn hôn nhân, chuyên viên tư vấn tang chế, đào tạo tư vấn viên",
            "ko": "학교 상담사, 결혼 상담사, 애도 상담사, 상담사 교육",
            "id": "konselor sekolah, konselor pernikahan, konselor duka, pelatihan konselor",
            "th": "ผู้ให้คำปรึกษาในโรงเรียน, ผู้ให้คำปรึกษาด้านการแต่งงาน, ผู้ให้คำปรึกษาด้านความโศกเศร้า, การฝึกอบรมผู้ให้คำปรึกษา",
            "es": "orientador escolar, consejero matrimonial, consejero de duelo, formación de consejeros",
        },
    )

    # Remove duplicated discourse-marker entries and incomplete fragments.
    collocation_repairs = {
        893: (
            "anyway, let's move on, it doesn't matter, in conclusion, regardless, back to the point",
            ["とにかく、次に進もう、問題ではない、結論として、いずれにせよ、本題に戻ると", "无论如何，继续吧，没关系，总之，无论怎样，回到正题", "खैर, आगे बढ़ते हैं, इससे कोई फर्क नहीं पड़ता, निष्कर्षतः, चाहे जो हो, मुद्दे पर लौटते हैं", "dù sao, hãy tiếp tục, điều đó không quan trọng, tóm lại, bất kể thế nào, quay lại vấn đề chính", "어쨌든, 다음으로 넘어가자, 상관없다, 결론적으로, 어쨌든, 본론으로 돌아가자", "bagaimanapun juga, mari kita lanjutkan, tidak masalah, sebagai kesimpulan, terlepas dari itu, kembali ke pokok pembicaraan", "อย่างไรก็ตาม, มาพูดถึงเรื่องต่อไปกัน, ไม่สำคัญหรอก, สรุปแล้ว, ไม่ว่าอย่างไรก็ตาม, กลับมาที่ประเด็น", "de todos modos, sigamos adelante, no importa, en conclusión, en cualquier caso, volviendo al tema"]
        ),
        1269: (
            "unfortunately, however, unfortunately due to, unfortunately not, unfortunately there is",
            ["残念ながら、しかしながら、残念ながら～が原因で、残念ながら～ない、残念ながら～がある", "不幸的是，然而，遗憾的是由于，很遗憾没有，遗憾的是有", "दुर्भाग्य से, हालांकि, दुर्भाग्य से ... के कारण, दुर्भाग्य से नहीं, दुर्भाग्य से ... है", "thật không may, tuy nhiên, thật không may do, thật không may không, thật không may là có", "불행히도, 그러나, 불행히도 ~ 때문에, 불행히도 아니다, 불행히도 ~이 있다", "sayangnya, namun, sayangnya karena, sayangnya tidak, sayangnya ada", "น่าเสียดาย, อย่างไรก็ตาม, น่าเสียดายเนื่องจาก, น่าเสียดายที่ไม่, น่าเสียดายที่มี", "desafortunadamente, sin embargo, desafortunadamente debido a, desafortunadamente no, desafortunadamente hay"]
        ),
        1403: (
            "moreover, and moreover, moreover the study shows, moreover there is evidence, moreover it is important to note",
            ["さらに、さらに、さらに研究は示している、さらに証拠がある、さらに重要なのは", "此外，而且，此外研究表明，此外有证据，此外需要注意的是", "इसके अलावा, और इसके अलावा, इसके अलावा अध्ययन दिखाता है, इसके अलावा प्रमाण है, इसके अलावा यह ध्यान देना महत्वपूर्ण है", "hơn nữa, hơn nữa, hơn nữa nghiên cứu cho thấy, hơn nữa có bằng chứng, hơn nữa cần lưu ý rằng", "게다가, 더욱이, 더욱이 연구는 보여 준다, 더욱이 증거가 있다, 더욱이 주목할 점은", "terlebih lagi, dan terlebih lagi, terlebih lagi penelitian menunjukkan, terlebih lagi terdapat bukti, terlebih lagi penting untuk dicatat", "ยิ่งไปกว่านั้น, และยิ่งไปกว่านั้น, ยิ่งไปกว่านั้นการศึกษาชี้ให้เห็น, ยิ่งไปกว่านั้นมีหลักฐาน, ยิ่งไปกว่านั้นสิ่งสำคัญที่ควรสังเกตคือ", "además, y además, además el estudio muestra, además hay pruebas, además es importante señalar"]
        ),
        1753: (
            "meanwhile, back home, in the meantime, meanwhile elsewhere, meanwhile at the same time",
            ["一方で、故郷では、その間に、別の場所では、一方で同時に", "与此同时，在国内，在此期间，在其他地方，与此同时", "इस बीच, अपने देश में, इस दौरान, अन्यत्र, इसी बीच उसी समय", "trong khi đó, ở quê nhà, trong lúc đó, ở nơi khác, trong khi đó đồng thời", "한편, 본국에서는, 그동안, 다른 곳에서는, 한편 동시에", "sementara itu, di tanah air, pada saat yang sama, di tempat lain, sementara itu bersamaan", "ในขณะเดียวกัน, ที่บ้านเกิด, ในระหว่างนี้, ที่อื่น, ในขณะเดียวกัน", "mientras tanto, de vuelta a casa, entretanto, en otros lugares, mientras tanto al mismo tiempo"]
        ),
        1754: (
            "furthermore, furthermore it is important to note, furthermore the study shows, furthermore this suggests, furthermore there is evidence",
            ["さらに、さらに重要なのは、さらに研究は示している、さらにこれは示唆する、さらに証拠がある", "此外，此外需要注意的是，此外研究表明，此外这表明，此外有证据", "इसके अलावा, इसके अलावा यह ध्यान देना महत्वपूर्ण है, इसके अलावा अध्ययन दिखाता है, इसके अलावा यह संकेत देता है, इसके अलावा प्रमाण मौजूद है", "hơn nữa, hơn nữa cần lưu ý rằng, hơn nữa nghiên cứu cho thấy, hơn nữa điều này gợi ý rằng, hơn nữa có bằng chứng", "게다가, 게다가 주목할 점은, 게다가 연구는 보여 준다, 게다가 이는 시사한다, 게다가 증거가 있다", "selain itu, selain itu penting untuk dicatat, selain itu penelitian menunjukkan, selain itu hal ini menunjukkan, selain itu terdapat bukti", "นอกจากนี้, นอกจากนี้สิ่งสำคัญที่ควรสังเกตคือ, นอกจากนี้การศึกษาชี้ให้เห็น, นอกจากนี้สิ่งนี้บ่งชี้ว่า, นอกจากนี้มีหลักฐาน", "además, además es importante señalar, además el estudio muestra, además esto sugiere, además hay pruebas"]
        ),
        1946: (
            "secondly, secondly it is important to note, secondly we should consider, secondly the study shows, secondly there is evidence",
            ["第二に、第二に重要なのは、第二に考慮すべきなのは、第二に研究は示している、第二に証拠がある", "其次，其次需要注意的是，其次我们应该考虑，其次研究表明，其次有证据", "दूसरी बात, दूसरी बात यह ध्यान देना महत्वपूर्ण है, दूसरी बात हमें विचार करना चाहिए, दूसरी बात अध्ययन दिखाता है, दूसरी बात प्रमाण है", "thứ hai, thứ hai cần lưu ý rằng, thứ hai chúng ta nên xem xét, thứ hai nghiên cứu cho thấy, thứ hai có bằng chứng", "둘째로, 둘째로 주목할 점은, 둘째로 우리는 고려해야 한다, 둘째로 연구는 보여 준다, 둘째로 증거가 있다", "kedua, kedua penting untuk dicatat, kedua kita harus mempertimbangkan, kedua penelitian menunjukkan, kedua terdapat bukti", "ประการที่สอง, ประการที่สองสิ่งสำคัญที่ควรสังเกตคือ, ประการที่สองเราควรพิจารณา, ประการที่สองการศึกษาชี้ให้เห็น, ประการที่สองมีหลักฐาน", "en segundo lugar, en segundo lugar es importante señalar, en segundo lugar debemos considerar, en segundo lugar el estudio muestra, en segundo lugar hay pruebas"]
        ),
        2018: (
            "respectively, in that order, A and B respectively, correspond respectively, listed respectively",
            ["それぞれ、順に、AとBはそれぞれ、順に対応する、それぞれ列挙された", "分别，按该顺序，A和B分别，分别对应，分别列出", "क्रमशः, उसी क्रम में, A और B क्रमशः, क्रमशः संबंधित होना, क्रमशः सूचीबद्ध", "tương ứng, theo thứ tự đó, A và B lần lượt, tương ứng với, được liệt kê lần lượt", "각각, 그 순서대로, A와 B는 각각, 각각 대응하다, 각각 나열되다", "masing-masing, dalam urutan itu, A dan B masing-masing, masing-masing sesuai, dicantumkan masing-masing", "ตามลำดับ, ตามลำดับนั้น, A และ B ตามลำดับ, สอดคล้องกันตามลำดับ, เรียงตามลำดับ", "respectivamente, en ese orden, A y B respectivamente, corresponder respectivamente, enumerados respectivamente"]
        ),
        2549: (
            "consequently, and consequently, consequently the pressure drops, consequently the results change, consequently the study supports the hypothesis",
            ["その結果、そしてその結果、その結果圧力が下がる、その結果結果が変わる、その結果研究は仮説を支持する", "因此，并因此，因此压力下降，因此结果改变，因此研究支持该假设", "नतीजतन, और नतीजतन, नतीजतन दबाव घटता है, नतीजतन परिणाम बदलते हैं, नतीजतन अध्ययन परिकल्पना का समर्थन करता है", "do đó, và do đó, do đó áp suất giảm, do đó kết quả thay đổi, do đó nghiên cứu ủng hộ giả thuyết", "결과적으로, 그리고 그 결과, 결과적으로 압력이 떨어지다, 결과적으로 결과가 바뀌다, 결과적으로 연구는 가설을 지지하다", "akibatnya, dan akibatnya, akibatnya tekanan turun, akibatnya hasil berubah, akibatnya penelitian mendukung hipotesis", "ดังนั้น, และด้วยเหตุนี้, ดังนั้นความดันจึงลดลง, ดังนั้นผลลัพธ์จึงเปลี่ยนแปลง, ดังนั้นการศึกษาจึงสนับสนุนสมมติฐาน", "en consecuencia, y en consecuencia, en consecuencia la presión baja, en consecuencia cambian los resultados, en consecuencia el estudio respalda la hipótesis"]
        ),
        5149: (
            "interestingly enough, interestingly, interestingly the study found, interestingly this suggests, interestingly however",
            ["実に興味深いことに、興味深いことに、興味深いことに研究は明らかにした、興味深いことにこれは示唆する、興味深いことにしかし", "说来也有意思，有趣的是，有趣的是研究发现，有趣的是这表明，有趣的是然而", "दिलचस्प बात यह है कि, दिलचस्प रूप से, दिलचस्प बात यह है कि अध्ययन ने पाया, दिलचस्प बात यह है कि इससे संकेत मिलता है, हालांकि दिलचस्प रूप से", "thú vị thay, thú vị là, thú vị là nghiên cứu phát hiện, thú vị là điều này gợi ý, tuy nhiên thú vị là", "참 흥미롭게도, 흥미롭게도, 흥미롭게도 연구 결과, 흥미롭게도 이는 시사한다, 그러나 흥미롭게도", "menariknya, menariknya, menariknya penelitian menemukan, menariknya hal ini menunjukkan, namun menariknya", "น่าสนใจทีเดียว, น่าสนใจ, น่าสนใจที่การศึกษาพบ, น่าสนใจที่สิ่งนี้ชี้ให้เห็น, อย่างไรก็ตามก็น่าสนใจ", "curiosamente, resulta interesante que, curiosamente el estudio descubrió, curiosamente esto sugiere, sin embargo resulta interesante"]
        ),
    }
    for item_id, (source, values) in collocation_repairs.items():
        set_collocations(item_id, source, dict(zip(LANGUAGES, values)))

    # Repair the remaining high-confidence English collocation defects found
    # by the all-word audit.  These are source-data fixes, so every language
    # is updated together and remains aligned with the English list.
    additional_collocation_repairs = {
        697: (
            "indeed true, indeed important, indeed necessary, yes indeed, indeed so",
            {
                "ja": "本当に正しい、実に重要な、確かに必要な、まさにその通り、確かにそうだ",
                "zh": "确实正确，确实重要，确实必要，是的确实如此，确实如此",
                "hi": "वास्तव में सही, वास्तव में महत्वपूर्ण, वास्तव में आवश्यक, हाँ बिल्कुल, वास्तव में ऐसा ही",
                "vi": "thực sự đúng, thực sự quan trọng, thực sự cần thiết, đúng vậy, quả đúng như vậy",
                "ko": "정말 옳은, 정말 중요한, 정말 필요한, 정말 그렇지, 확실히 그렇다",
                "id": "memang benar, memang penting, memang perlu, ya memang, memang demikian",
                "th": "ถูกต้องจริง ๆ, สำคัญจริง ๆ, จำเป็นจริง ๆ, ใช่แล้ว, เป็นเช่นนั้นจริง ๆ",
                "es": "efectivamente cierto, realmente importante, realmente necesario, sí que lo es, efectivamente así",
            },
        ),
        1409: (
            "research scientist, political scientist, data scientist, team of scientists, leading scientist",
            {
                "ja": "研究科学者、政治学者、データサイエンティスト、科学者チーム、著名な科学者",
                "zh": "研究科学家，政治学家，数据科学家，科学家团队，顶尖科学家",
                "hi": "शोध वैज्ञानिक, राजनीतिक वैज्ञानिक, डेटा वैज्ञानिक, वैज्ञानिकों की टीम, अग्रणी वैज्ञानिक",
                "vi": "nhà khoa học chuyên nghiên cứu, nhà khoa học chính trị, nhà khoa học dữ liệu, nhóm các nhà khoa học, nhà khoa học hàng đầu",
                "ko": "연구 과학자, 정치학자, 데이터 과학자, 과학자 팀, 저명한 과학자",
                "id": "ilmuwan peneliti, ilmuwan politik, ilmuwan data, tim ilmuwan, ilmuwan terkemuka",
                "th": "นักวิทยาศาสตร์วิจัย, นักรัฐศาสตร์, นักวิทยาศาสตร์ข้อมูล, ทีมนักวิทยาศาสตร์, นักวิทยาศาสตร์ชั้นนำ",
                "es": "investigador científico, científico político, científico de datos, equipo de científicos, científico destacado",
            },
        ),
        1645: (
            "research assistant, lead researcher, independent researcher, researcher finds evidence, team of researchers",
            {
                "ja": "研究助手、主任研究者、独立研究者、研究者が証拠を見つける、研究者チーム",
                "zh": "研究助理，首席研究员，独立研究员，研究员发现证据，研究人员团队",
                "hi": "शोध सहायक, प्रमुख शोधकर्ता, स्वतंत्र शोधकर्ता, शोधकर्ता प्रमाण पाता है, शोधकर्ताओं की टीम",
                "vi": "trợ lý nghiên cứu, trưởng nhóm nghiên cứu, nhà nghiên cứu độc lập, nhà nghiên cứu tìm thấy bằng chứng, nhóm các nhà nghiên cứu",
                "ko": "연구 조교, 수석 연구원, 독립 연구원, 연구원이 증거를 찾다, 연구원 팀",
                "id": "asisten peneliti, peneliti utama, peneliti independen, peneliti menemukan bukti, tim peneliti",
                "th": "ผู้ช่วยวิจัย, หัวหน้านักวิจัย, นักวิจัยอิสระ, นักวิจัยพบหลักฐาน, ทีมนักวิจัย",
                "es": "asistente de investigación, investigador principal, investigador independiente, el investigador encuentra pruebas, equipo de investigadores",
            },
        ),
        1946: (
            "secondly, it is important to note, secondly we should consider, secondly the study shows, secondly there is evidence",
            {
                "ja": "第二に、第二に重要なのは、第二に考慮すべきなのは、第二に研究は示している、第二に証拠がある",
                "zh": "其次，其次需要注意的是，其次我们应该考虑，其次研究表明，其次有证据",
                "hi": "दूसरी बात, दूसरी बात यह ध्यान देना महत्वपूर्ण है, दूसरी बात हमें विचार करना चाहिए, दूसरी बात अध्ययन दिखाता है, दूसरी बात प्रमाण है",
                "vi": "thứ hai, thứ hai cần lưu ý rằng, thứ hai chúng ta nên xem xét, thứ hai nghiên cứu cho thấy, thứ hai có bằng chứng",
                "ko": "둘째로, 둘째로 주목할 점은, 둘째로 우리는 고려해야 한다, 둘째로 연구는 보여 준다, 둘째로 증거가 있다",
                "id": "kedua, kedua penting untuk dicatat, kedua kita harus mempertimbangkan, kedua penelitian menunjukkan, kedua terdapat bukti",
                "th": "ประการที่สอง, ประการที่สองสิ่งสำคัญที่ควรสังเกตคือ, ประการที่สองเราควรพิจารณา, ประการที่สองการศึกษาชี้ให้เห็น, ประการที่สองมีหลักฐาน",
                "es": "en segundo lugar, en segundo lugar es importante señalar, en segundo lugar debemos considerar, en segundo lugar el estudio muestra, en segundo lugar hay pruebas",
            },
        ),
        6165: (
            "field archaeologist, archaeological excavation, team of archaeologists, archaeologist discovers artifacts",
            {
                "ja": "現地考古学者、考古学的発掘、考古学者のチーム、考古学者が遺物を発見する",
                "zh": "田野考古学家，考古发掘，考古学家团队，考古学家发现文物",
                "hi": "क्षेत्रीय पुरातत्त्ववेत्ता, पुरातात्त्विक खुदाई, पुरातत्त्ववेत्ताओं की टीम, पुरातत्त्ववेत्ता कलाकृतियाँ खोजता है",
                "vi": "nhà khảo cổ thực địa, cuộc khai quật khảo cổ, nhóm các nhà khảo cổ, nhà khảo cổ phát hiện hiện vật",
                "ko": "현장 고고학자, 고고학적 발굴, 고고학자 팀, 고고학자가 유물을 발견하다",
                "id": "arkeolog lapangan, penggalian arkeologis, tim arkeolog, arkeolog menemukan artefak",
                "th": "นักโบราณคดีภาคสนาม, การขุดค้นทางโบราณคดี, ทีมนักโบราณคดี, นักโบราณคดีค้นพบโบราณวัตถุ",
                "es": "arqueólogo de campo, excavación arqueológica, equipo de arqueólogos, el arqueólogo descubre artefactos",
            },
        ),
    }
    for item_id, (source, values) in additional_collocation_repairs.items():
        set_collocations(item_id, source, values)
    translations["builtin:4535"]["collocations"]["id"] = "hidup berdampingan dengan damai, hidup berdampingan dengan, hidup berdampingan secara harmonis, belajar hidup berdampingan, hidup berdampingan satu sama lain"
    set_collocations(
        95,
        "mean that, what do you mean by, arithmetic mean, mean value, it doesn't mean",
        {
            "ja": "〜という意味である、〜で何を意味する、算術平均、平均値、〜という意味ではない",
            "zh": "意味着，所说的……是指什么，算术平均数，均值，这并不意味着",
            "hi": "इसका मतलब है कि, से क्या मतलब है, अंकगणितीय माध्य, माध्य मान, इसका मतलब यह नहीं है",
            "vi": "có nghĩa là, bạn có ý gì khi nói, trung bình cộng, giá trị trung bình, điều đó không có nghĩa là",
            "ko": "~을 의미하다, 무엇을 뜻하는지, 산술 평균, 평균값, 그것이 의미하는 것은 아니다",
            "id": "berarti bahwa, apa yang dimaksud dengan, rata-rata aritmetika, nilai rata-rata, itu tidak berarti",
            "th": "หมายความว่า, หมายถึงอะไรเมื่อพูดว่า, ค่าเฉลี่ยเลขคณิต, ค่าเฉลี่ย, ไม่ได้หมายความว่า",
            "es": "significar que, qué quieres decir con, media aritmética, valor medio, no significa",
        },
    )
    set_collocations(
        5123,
        "most importantly, importantly for, equally importantly, importantly, it is important",
        {
            "ja": "最も重要なことに、〜にとって重要なことに、同じく重要なことに、重要なことに、重要なのは〜だ",
            "zh": "最重要的是，对……而言重要的是，同样重要的是，重要的是，重要的是……",
            "hi": "सबसे महत्वपूर्ण बात, के लिए महत्वपूर्ण, समान रूप से महत्वपूर्ण, महत्वपूर्ण बात, यह महत्वपूर्ण है कि",
            "vi": "quan trọng nhất là, quan trọng đối với, quan trọng không kém, đáng chú ý là, điều quan trọng là",
            "ko": "가장 중요하게는, ~에게 중요한 점은, 마찬가지로 중요한 것은, 중요하게도, 중요한 것은 ~이다",
            "id": "yang paling penting, penting bagi, sama pentingnya, yang penting, yang penting adalah",
            "th": "ที่สำคัญที่สุด, ที่สำคัญสำหรับ, ที่สำคัญพอ ๆ กัน, ที่สำคัญ, สิ่งสำคัญคือ",
            "es": "lo más importante, importante para, igualmente importante, es importante destacar que, lo importante es",
        },
    )
    set_collocations(
        6129,
        "the theory of behaviorism, principles of behaviorism, behaviorism in psychology, behaviorist approach, behaviorism research",
        {
            "ja": "行動主義の理論、行動主義の原則、心理学における行動主義、行動主義的アプローチ、行動主義研究",
            "zh": "行为主义理论，行为主义原则，心理学中的行为主义，行为主义方法，行为主义研究",
            "hi": "व्यवहारवाद का सिद्धांत, व्यवहारवाद के सिद्धांत, मनोविज्ञान में व्यवहारवाद, व्यवहारवादी दृष्टिकोण, व्यवहारवाद पर शोध",
            "vi": "lý thuyết về chủ nghĩa hành vi, các nguyên lý của chủ nghĩa hành vi, chủ nghĩa hành vi trong tâm lý học, phương pháp tiếp cận hành vi, nghiên cứu về chủ nghĩa hành vi",
            "ko": "행동주의 이론, 행동주의 원리, 심리학에서의 행동주의, 행동주의적 접근법, 행동주의 연구",
            "id": "teori behaviorisme, prinsip behaviorisme, behaviorisme dalam psikologi, pendekatan behavioris, penelitian behaviorisme",
            "th": "ทฤษฎีพฤติกรรมนิยม, หลักการพฤติกรรมนิยม, พฤติกรรมนิยมในจิตวิทยา, แนวทางแบบพฤติกรรมนิยม, งานวิจัยด้านพฤติกรรมนิยม",
            "es": "teoría del conductismo, principios del conductismo, conductismo en psicología, enfoque conductista, investigación sobre el conductismo",
        },
    )
    translations["builtin:6092"]["collocations"]["ja"] = "洗濯室、洗濯をする、洗濯設備、洗濯用洗剤"
    translations["builtin:6092"]["collocations"]["zh"] = "洗衣房，洗衣服，洗衣设施，洗衣用洗涤剂"
    natural_collocation_overrides = {
        1403: {
            "ja": "さらに、また、さらに研究は〜を示している、さらに〜という証拠がある、さらに重要なのは〜だ",
            "hi": "इसके अलावा, और इसके अलावा, इसके अलावा अध्ययन से पता चलता है, इसके अलावा प्रमाण मौजूद है, इसके अलावा यह ध्यान देना महत्वपूर्ण है",
            "ko": "게다가, 더욱이, 더욱이 연구 결과는 ~을 보여 준다, 더욱이 ~라는 증거가 있다, 더욱이 주목할 점은 ~이다",
        },
        1754: {
            "ja": "さらに、さらに重要なのは〜だ、さらに研究は〜を示している、さらにこれは〜を示唆する、さらに〜という証拠がある",
            "hi": "इसके अलावा, इसके अलावा यह ध्यान देना महत्वपूर्ण है, इसके अलावा अध्ययन से पता चलता है, इसके अलावा यह संकेत देता है, इसके अलावा प्रमाण मौजूद है",
            "ko": "게다가, 게다가 주목할 점은 ~이다, 게다가 연구 결과는 ~을 보여 준다, 게다가 이는 ~을 시사한다, 게다가 ~라는 증거가 있다",
        },
        1946: {
            "ja": "第二に、第二に重要なのは〜だ、第二に〜を考慮すべきだ、第二に研究は〜を示している、第二に〜という証拠がある",
            "hi": "दूसरी बात, दूसरी बात यह ध्यान देना महत्वपूर्ण है, दूसरी बात हमें विचार करना चाहिए, दूसरी बात अध्ययन से पता चलता है, दूसरी बात प्रमाण मौजूद है",
            "ko": "둘째로, 둘째로 주목할 점은 ~이다, 둘째로 우리는 ~을 고려해야 한다, 둘째로 연구 결과는 ~을 보여 준다, 둘째로 ~라는 증거가 있다",
        },
    }
    for item_id, values in natural_collocation_overrides.items():
        for language, value in values.items():
            translations[f"builtin:{item_id}"]["collocations"][language] = value
    translations["builtin:592"]["collocations"]["ko"] = "증거를 제공하다, 강력한 증거, 증거는 시사한다, 증거는 ~을 보여 준다, 명백한 증거"

    # Clearly untranslated or malformed strings in the most visible language
    # batches.  These are full-sentence replacements, not word substitutions,
    # so tense and word order remain coherent.
    example_repairs = {
        326: {"ko": "내 룸메이트는 저녁 수업 후 농구를 시청하는 것을 좋아한다."},
        748: {"ko": "내 실험 파트너는 그 식물이 햇빛을 필요로 한다는 것을 입증하는 데 도움을 주었다."},
        1180: {"id": "Kantor registrar memasukkan nama saya ke dalam daftar tunggu biologi."},
        1820: {"id": "Kantor registrar menerbitkan kartu mahasiswa sementara saat kartu pengganti saya disiapkan."},
        2441: {"ko": "공학 교수는 명확한 목표가 학생들이 어려운 설계 프로젝트를 끝까지 해내도록 어떻게 동기를 부여하는지 보여 주었다."},
        2584: {"ko": "교수는 생물학 강의에서 호르몬이 혈당을 어떻게 조절하는지 설명했다."},
        2782: {"ko": "역사 강의에서 학생들은 혁명 후 지도자들이 사회 질서를 어떻게 재건하는지 배웠다."},
        2846: {"id": "Profesor biologi menjelaskan bahwa setiap asam amino berkontribusi pada struktur protein."},
        3617: {"ko": "세미나는 새로운 통계 도구가 복잡한 사회 자료를 어떻게 더 정교하게 분석할 수 있게 하는지 검토한다."},
        3764: {"ko": "경제학 교수는 시장 금리가 하락할 때 대출자들이 학자금 대출을 재융자하는 방식을 설명했다."},
        4707: {"ko": "경제학 수업에서 우리는 물가가 오를 때 소비자들이 어떻게 반응하는지 배웠다."},
        5202: {"ko": "경제학 교수는 기업이 수입과 생산 비용을 비교해 이윤을 극대화하는 방식을 보여 준다."},
        5356: {"ko": "그 엔지니어는 손상된 실험실 컴퓨터에서 삭제된 파일을 복구하는 방법을 보여 주었다."},
        5364: {"ko": "천문학에서 지구는 24시간마다 한 번씩 회전하는 것처럼 보이며, 낮과 밤의 일일 주기를 만든다."},
        5410: {"id": "Buku teks ekonomi menjelaskan bagaimana upah dapat tetap stabil ketika permintaan tenaga kerja hampir tidak berubah."},
        5503: {"ko": "강의에서는 아파트 임대료가 오르는데도 많은 학생이 캠퍼스 근처에 거주하는 이유를 살펴보았다."},
        5526: {"ko": "환경 과학 수업에서는 캠퍼스 식당에서 나오는 쓰레기를 최소화하는 방법을 배웠다."},
        3716: {"ko": "연구 세미나는 설문 문구의 겉보기에 사소한 차이가 보고된 태도에 큰 변화를 일으킨다는 것을 보여 주었다."},
        2256: {"ko": "이 통계치는 교수가 강의 시간을 바꾼 후 출석률이 향상되었음을 보여 준다."},
        2551: {"vi": "Các phát hiện lịch sử đã được kiểm chứng khi một kho lưu trữ khác công bố cùng những hồ sơ bầu cử."},
        6344: {"vi": "Bài giảng tâm lý học phát triển so sánh các giai đoạn phát triển trong quá trình học ngôn ngữ của trẻ."},
        1290: {"vi": "Cố vấn học tập nói rằng tôi cần có hồ sơ tiêm chủng cập nhật trước khi đăng ký phòng thí nghiệm sinh học."},
        4707: {
            "ko": "경제학 수업에서 우리는 물가가 오를 때 소비자들이 어떻게 반응하는지 배웠다.",
            "vi": "Trong khóa học kinh tế, chúng tôi học cách người tiêu dùng phản ứng khi giá tăng.",
        },
        6088: {"vi": "Giáo sư phân tích tuyển tập này như một tập hợp tác phẩm được tuyển chọn, qua đó cho thấy các lựa chọn biên tập giúp học giả xây dựng một quy điển lịch sử như thế nào."},
        16: {"es": "Estudiamos juntos en la biblioteca antes de nuestro examen de biología."},
        19: {"vi": "Đây là chỗ ngồi của tôi trong buổi hội thảo dành cho sinh viên năm nhất.", "id": "Ini adalah tempat duduk saya dalam seminar mahasiswa baru.", "es": "Este es mi asiento en el seminario para estudiantes de primer año."},
        36: {"vi": "Bạn có muốn gặp tôi trong giờ tư vấn để thảo luận về điểm giữa kỳ không?", "id": "Apakah kamu mau bertemu saat jam konsultasi untuk membahas nilai ujian tengah semester?", "es": "¿Te gustaría reunirte durante el horario de consulta para hablar de tu nota del examen parcial?"},
        52: {"id": "Tagihan energi teman sekamar saya naik setelah kami menggunakan pemanas.", "es": "La factura de energía de mi compañero de cuarto aumentó después de que usamos la calefacción."},
        53: {"vi": "Một số sinh viên ăn sáng ở nhà ăn trước buổi học buổi sáng."},
        111: {"vi": "Bạn cùng lớp của tôi nói rằng cuộc sống đại học trở nên dễ dàng hơn sau tháng đầu tiên.", "id": "Teman sekelas saya mengatakan bahwa kehidupan perguruan tinggi terasa lebih mudah setelah bulan pertama."},
        115: {"vi": "Giáo sư giao một bài đọc dài cho ngày mai.", "id": "Profesor saya memberi tugas bacaan panjang untuk besok.", "es": "Mi profesor asignó una lectura larga para mañana."},
        145: {"vi": "Mỗi sinh viên nhận một chiếc chìa khóa từ cố vấn ký túc xá.", "id": "Setiap mahasiswa menerima kunci dari penasihat asrama.", "es": "Cada estudiante recibió una llave del asesor de la residencia."},
        240: {"vi": "Chương trình sinh học yêu cầu sinh viên học một môn thí nghiệm trong năm nhất.", "id": "Program biologi ini mengharuskan mahasiswa mengambil mata kuliah laboratorium pada tahun pertama.", "es": "El programa de biología exige cursar una materia de laboratorio durante el primer año."},
        246: {"vi": "Hôm nay tôi có một buổi học trong tòa nhà khoa học.", "id": "Hari ini saya mengikuti kuliah di gedung sains.", "es": "Hoy tengo una clase en el edificio de ciencias."},
        341: {"vi": "Hãy nhớ rằng thư viện đóng cửa sớm vào thứ Sáu."},
        412: {"vi": "Trước khi chọn một lớp khó, đến giờ tư vấn là điều hợp lý.", "id": "Datang ke jam konsultasi sebelum memilih kelas yang sulit itu masuk akal."},
        439: {"vi": "Một người trong lớp sinh học của tôi đã chia sẻ ghi chú sau khi tôi vắng buổi giảng.", "id": "Seseorang di kelas biologi saya membagikan catatan setelah saya melewatkan kuliah."},
        444: {"vi": "Đôi khi bạn cùng phòng của tôi học trong thư viện sau bữa tối.", "id": "Kadang-kadang teman sekamar saya belajar di perpustakaan setelah makan malam."},
        464: {"vi": "Có lẽ tôi nên đến phòng đăng ký trước khi thay đổi thời khóa biểu học kỳ mùa thu.", "id": "Mungkin saya harus mengunjungi kantor registrasi sebelum mengubah jadwal musim gugur saya.", "es": "Quizás debería visitar la oficina de registro antes de cambiar mi horario de otoño."},
        675: {"vi": "Hãy chọn bất cứ điều gì phù hợp với ngân sách của bạn tại hiệu sách trong trường.", "id": "Pilihlah apa pun yang sesuai dengan anggaranmu di toko buku kampus.", "es": "Elige lo que sea adecuado para tu presupuesto en la librería del campus."},
        725: {"vi": "Thành công ở trường đại học thường bắt đầu từ việc đi học và đặt câu hỏi.", "id": "Keberhasilan di perguruan tinggi sering dimulai dengan menghadiri kelas dan mengajukan pertanyaan.", "es": "El éxito en la universidad suele comenzar asistiendo a clase y haciendo preguntas."},
        735: {"vi": "Mục đích của buổi định hướng tân sinh viên là giúp sinh viên tìm các nguồn hỗ trợ trong trường.", "id": "Tujuan orientasi mahasiswa baru adalah membantu mahasiswa menemukan sumber daya kampus.", "es": "El propósito de la orientación para estudiantes nuevos es ayudarles a encontrar recursos del campus."},
        765: {"vi": "Xin lỗi, tôi không thể đến giờ tư vấn vì phòng thí nghiệm của tôi kết thúc lúc năm giờ.", "id": "Maaf, saya tidak bisa datang ke jam konsultasi karena kegiatan di laboratorium saya berakhir pukul lima.", "es": "Lo siento, no puedo ir al horario de consulta porque mi laboratorio termina a las cinco."},
        768: {"vi": "Gần như mọi sinh viên đều nộp báo cáo thí nghiệm sinh học đúng hạn."},
        782: {"vi": "Giáo sư điều dưỡng giải thích vì sao mọi bệnh viện cần đủ kinh phí để chăm sóc bệnh nhân an toàn.", "id": "Profesor keperawatan menjelaskan mengapa setiap rumah sakit membutuhkan dana yang cukup untuk merawat pasien dengan aman.", "es": "El profesor de enfermería explicó por qué todo hospital necesita financiación suficiente para atender a los pacientes de forma segura."},
        790: {"vi": "Bạn cùng lớp nói thư viện trường phổ biến vì nó mở cửa đến nửa đêm."},
        817: {"vi": "Giáo sư khoa học môi trường giải thích vì sao các vùng đất ngập nước tự nhiên làm giảm lũ quanh khuôn viên trường.", "id": "Profesor ilmu lingkungan menjelaskan mengapa lahan basah alami mengurangi banjir di sekitar kampus."},
        822: {"vi": "Đầu tư vào nhà ở trong khuôn viên giúp thị trấn đại học của chúng ta phát triển.", "id": "Investasi pada perumahan kampus membantu kota perguruan tinggi kami berkembang."},
        854: {"vi": "Nhiệm vụ ở thư viện yêu cầu sinh viên so sánh hai nguồn học thuật trước khi viết báo cáo.", "id": "Tugas di perpustakaan mengharuskan mahasiswa membandingkan dua sumber akademik sebelum menulis laporan."},
        855: {"vi": "Sinh viên năm nhất cảm thấy bối rối trong tuần đầu tiên ở trường là điều bình thường."},
        1148: {"vi": "Sau khi kỳ thực tập kết thúc, chúng tôi đi taxi từ ký túc xá đến sân bay.", "id": "Setelah magang selesai, kami naik taksi dari asrama ke bandara."},
        1181: {"vi": "Giáo sư tâm lý học dùng thực tế ảo để minh họa nỗi sợ ảnh hưởng đến trí nhớ như thế nào.", "id": "Profesor psikologi menggunakan realitas virtual untuk menunjukkan bagaimana rasa takut memengaruhi ingatan."},
        1191: {"vi": "Giáo trình kế toán định nghĩa thu nhập ròng là doanh thu sau khi trừ chi phí.", "id": "Buku teks akuntansi mendefinisikan pendapatan bersih sebagai pendapatan setelah biaya dikurangkan."},
        1263: {"vi": "Điểm mạnh lớn nhất của cô ấy trong kỳ thực tập là giải thích các ý tưởng kỹ thuật cho nhân viên mới.", "id": "Kekuatan terbesarnya selama magang adalah menjelaskan gagasan teknis kepada karyawan baru.", "es": "La mayor fortaleza de su pasantía fue explicar ideas técnicas a los empleados nuevos."},
        1277: {"vi": "Có vẻ như thư viện sẽ đóng cửa sớm trong kỳ nghỉ đông.", "id": "Tampaknya perpustakaan akan tutup lebih awal selama liburan musim dingin.", "es": "Al parecer, la biblioteca cerrará temprano durante las vacaciones de invierno."},
        1638: {"vi": "Góc yên tĩnh này trong thư viện phù hợp để ôn lại ghi chú trước kỳ thi giữa kỳ.", "id": "Sudut perpustakaan yang tenang ini cocok untuk meninjau catatan sebelum ujian tengah semester.", "es": "Este rincón tranquilo de la biblioteca es adecuado para repasar los apuntes antes del examen parcial."},
        1645: {"vi": "Một nhà nghiên cứu sinh học đã giải thích dự án thực tập của cô ấy trong buổi hội thảo năm nhất.", "id": "Seorang peneliti biologi menjelaskan proyek magangnya dalam seminar tahun pertama kami."},
        1910: {"vi": "Giáo sư kỹ thuật minh họa cách một vi mạch máy tính xử lý các tín hiệu điện.", "id": "Profesor teknik mendemonstrasikan cara sebuah chip komputer memproses sinyal listrik."},
        2320: {"vi": "Nhà kinh tế học gọi việc phục hồi nhanh chóng là suy nghĩ viển vông nếu không có những thay đổi lớn trên thị trường lao động.", "id": "Ekonom itu menyebut pemulihan cepat sebagai angan-angan tanpa perubahan besar dalam pasar tenaga kerja."},
        3210: {"vi": "Giáo sư mô tả lý thuyết phân tâm học là cách giải thích có ảnh hưởng nhưng gây tranh luận về động cơ vô thức.", "id": "Profesor menggambarkan teori psikoanalitik sebagai penjelasan yang berpengaruh tetapi kontroversial tentang motivasi tak sadar."},
        3288: {"vi": "Trong hội thảo thiết kế, giáo sư lập luận rằng tư duy bên có thể thách thức các giả định ẩn trong quy trình kỹ thuật.", "id": "Dalam seminar desain, profesor berpendapat bahwa berpikir lateral dapat menantang asumsi yang tertanam dalam rutinitas teknik.", "es": "En el seminario de diseño, el profesor sostuvo que el pensamiento lateral puede cuestionar los supuestos arraigados en las rutinas de ingeniería."},
        3920: {"vi": "Hội thảo về lý thuyết điều tiết của trường luật xem xét cách các cơ quan biện minh cho thẩm quyền đối với nghiên cứu khoa học.", "id": "Seminar teori regulasi di fakultas hukum mengkaji cara lembaga membenarkan kewenangan atas penelitian ilmiah.", "es": "El seminario sobre teoría regulatoria de la facultad de Derecho examinó cómo los organismos justifican su autoridad sobre la investigación científica."},
        4726: {"vi": "Việc thường xuyên đến giờ tư vấn giúp tôi hiểu các bài giảng kinh tế học."},
        4812: {"vi": "Trong giờ tư vấn, tôi không thể giả vờ rằng mình hiểu công thức thống kê.", "id": "Saat jam konsultasi, saya tidak bisa berpura-pura memahami rumus statistik itu.", "es": "Durante el horario de consulta, no podía fingir que entendía la fórmula estadística."},
        5084: {"vi": "Trong giờ tư vấn, sinh viên có thể tự do hỏi giáo sư về những khái niệm khó."},
        5206: {"vi": "Giáo sư cho thấy mạng xã hội có thể ảnh hưởng đến lựa chọn bỏ phiếu như thế nào trong một buổi giảng chính trị học.", "id": "Profesor menunjukkan bagaimana media sosial dapat memengaruhi pilihan pemilih dalam kuliah ilmu politik.", "es": "El profesor mostró cómo las redes sociales pueden influir en las decisiones de voto durante una clase de ciencias políticas."},
        5716: {"vi": "Sách giáo khoa địa chất sử dụng mô hình máy tính để dự đoán sông băng có thể định hình lại thung lũng ra sao.", "id": "Buku teks geologi menggunakan pemodelan komputer untuk memprediksi bagaimana gletser dapat membentuk kembali lembah."},
        5964: {"vi": "Khu nội trú đại học cung cấp tư vấn và các bữa ăn chung cho sinh viên năm nhất.", "id": "Asrama kampus universitas itu menawarkan bimbingan dan makan bersama bagi mahasiswa baru.", "es": "La residencia universitaria ofrece orientación y comidas compartidas para los estudiantes de primer año."},
        6237: {"vi": "Phòng đọc của thư viện trường mở cửa đến nửa đêm trong kỳ thi cuối kỳ.", "id": "Ruang baca perpustakaan universitas buka sampai tengah malam selama ujian akhir.", "es": "La sala de lectura de la biblioteca universitaria abre hasta medianoche durante los exámenes finales."},
        84: {"vi": "Sau giờ học, tôi sẽ gặp bạn cùng phòng ở thư viện."},
        88: {"vi": "Hầu hết sinh viên năm nhất tham dự buổi họp chào mừng."},
        275: {"vi": "Trong bài giảng hiện tại, giáo sư trình bày cách sông băng tạo hình các thung lũng.", "id": "Kuliah ini membahas cara gletser membentuk lembah.", "es": "La clase actual explica cómo los glaciares forman los valles."},
        354: {"vi": "Vấn đề thực sự là phòng ký túc xá của chúng tôi không có bàn."},
        381: {"vi": "Lớp xã hội học của tôi học trong thư viện vào mỗi thứ Ba."},
        564: {"vi": "Giáo sư không đề cập rằng giờ tư vấn bị hủy trong đề cương môn học."},
        726: {"vi": "Sách thư viện đến hạn vào ngày mai, nên tôi cần trả lại vào hôm nay.", "id": "Buku perpustakaan harus dikembalikan besok, jadi saya perlu mengembalikannya hari ini.", "es": "El libro de la biblioteca vence mañana, así que debo devolverlo hoy."},
        790: {"vi": "Bạn cùng lớp nói thư viện trường được nhiều người yêu thích vì nó mở cửa đến nửa đêm.", "id": "Teman sekelas saya berkata bahwa perpustakaan kampus populer karena buka sampai tengah malam."},
        817: {"es": "El profesor de ciencias ambientales explicó por qué los humedales naturales reducen las inundaciones alrededor del campus."},
        838: {"id": "Banyak mahasiswa tahun pertama mengalami stres selama ujian tengah semester pertama mereka."},
        1119: {"vi": "Nhóm học của chúng tôi họp tại phòng sinh hoạt ký túc xá vào mỗi thứ Ba.", "id": "Kelompok belajar kami bertemu di ruang bersama asrama setiap Selasa.", "es": "Nuestro grupo de estudio se reúne en la sala común de la residencia todos los martes."},
        1586: {"id": "Penasihat Anda mengatakan bahwa Anda bisa berhasil jika menghadiri jam konsultasi dan merevisi esai."},
        1645: {"es": "Una bióloga explicó su proyecto de prácticas durante nuestro seminario de primer año."},
        1910: {"es": "El profesor de ingeniería demostró cómo un chip de computadora procesa las señales eléctricas."},
        2320: {"es": "El economista calificó de ilusoria una recuperación rápida sin cambios importantes en el mercado laboral."},
        4043: {"vi": "Giáo sư nghiên cứu đô thị mô tả Đại lộ College là một đại lộ lớn nối trường đại học với các khu dân cư xung quanh."},
        4726: {"vi": "Việc thường xuyên đến giờ tư vấn giúp tôi hiểu các bài giảng kinh tế học."},
        5909: {"es": "El programa revisado incluye una nueva fecha para el examen parcial del curso de biología de primer año."},
    }
    for item_id, values in example_repairs.items():
        entry = translations[f"builtin:{item_id}"]["example"]
        for language, value in values.items():
            entry[language] = value

    # Remove high-confidence generation artifacts found by the offline native
    # candidate scan.  These are grammar errors, not stylistic preferences.
    native_example_repairs = {
        "ja": {
            42: "今学期はより多くの学生がキャンパス菜園に参加した。",
            88: "ほとんどの新入生は歓迎会に出席する。",
            101: "私の最後の試験は金曜日なので、その後で教務課に行ける。",
            123: "多くの学生は午前の授業の後にカフェテリアで昼食を食べる。",
            1820: "交換カードが用意される間、教務課は仮の学生証を発行した。",
            2701: "人類学の教授は、超能力の主張がフィールド調査の証拠に取って代わることはできないと述べた。",
            2725: "公衆衛生の講義では、無保険の学生が深刻な症状の治療を遅らせる理由を説明した。",
            3934: "研究セミナーでは、新たに翻訳された碑文について歴史家が提案してきた無数の解釈を検討した。",
            4788: "看護学のアドバイザーは、妊娠中の学生が妥当な学業上の配慮を申請できると説明した。",
            6198: "私たちの一学期間にわたる生物学プロジェクトでは、大学の温室近くで毎週昆虫を観察する必要がある。",
        },
        "ko": {
            90: "나는 오후 강의 전에 조용한 자리가 필요하다.",
            290: "주거 사무실을 통해 식사 계획을 변경하는 것이 가능하다.",
            206: "지도교수님은 내 등록 양식에 과목명을 적었다.",
            274: "경제학 교수는 빈곤선이 가구 소득을 비교하는 데 도움이 된다고 말했다.",
            326: "내 룸메이트는 저녁 수업 후 농구를 시청하는 것을 좋아한다.",
            748: "내 실험 파트너는 그 식물이 햇빛을 필요로 한다는 것을 입증하는 데 도움을 주었다.",
            914: "생물학 개론 조사에서 남학생들이 환경 과학을 선택할 가능성이 약간 더 높은 것으로 나타났다.",
            1043: "심리학 수업에서는 수면이 학생들의 기억력을 향상시키는지 시험하는 임상시험을 논의했다.",
            1345: "내 룸메이트는 도서관이 자정 전에 문을 닫는 것이 이상하다고 생각했다.",
            1638: "도서관의 이 조용한 구석은 중간고사 전에 필기를 복습하기에 적합하다.",
            1932: "그 증거는 교수가 심리학 입문 교과서를 개정하기에 충분하다고 한다.",
            2039: "교수님은 수업이 오늘 그 장을 끝낼 가능성은 희박하다고 말했다.",
            2441: "공학 교수는 명확한 목표가 학생들이 어려운 설계 프로젝트를 끝까지 해내도록 어떻게 동기를 부여하는지 보여 주었다.",
            2584: "교수는 생물학 강의에서 호르몬이 혈당을 어떻게 조절하는지 설명했다.",
            2782: "역사 강의에서 학생들은 혁명 후 지도자들이 사회 질서를 어떻게 재건하는지 배웠다.",
            3449: "종교 세미나에서 교수는 윤회를 개인 정체성에 관한 이론으로 분석했다.",
            3617: "세미나는 새로운 통계 도구가 복잡한 사회 자료를 어떻게 더 정교하게 분석할 수 있게 하는지 검토한다.",
            3764: "경제학 교수는 시장 금리가 하락할 때 대출자들이 학자금 대출을 재융자하는 방식을 설명했다.",
            4178: "신경과학 교수는 손상된 신경 경로를 회복시키지 않고 증상만 줄이는 약물과 재활치료를 구별했다.",
            4707: "경제학 수업에서 우리는 물가가 오를 때 소비자들이 어떻게 반응하는지 배웠다.",
            5190: "물리학 교수는 자기장이 금속 원판을 건드리지 않고 움직일 수 있는 원리를 시연했다.",
            5202: "경제학 교수는 기업이 수입과 생산 비용을 비교해 이윤을 극대화하는 방식을 보여 준다.",
            5221: "화학 교수는 그 반응이 열을 방출한다는 증거가 미미하다고 판단했다.",
            5322: "화학 교수는 모든 학생이 실험실 안전 수칙을 따라야 하는 이유를 설명했다.",
            5356: "그 엔지니어는 손상된 실험실 컴퓨터에서 삭제된 파일을 복구하는 방법을 보여 주었다.",
            5364: "천문학에서 지구는 24시간마다 한 번씩 회전하는 것처럼 보이며, 낮과 밤의 일일 주기를 만든다.",
            5413: "교수는 기기를 올바르게 보정하고 나면 절차가 간단하다고 말했다.",
            5503: "강의에서는 아파트 임대료가 오르는데도 많은 학생이 캠퍼스 근처에 거주하는 이유를 살펴보았다.",
            5526: "환경 과학 수업에서는 캠퍼스 식당에서 나오는 쓰레기를 최소화하는 방법을 배웠다.",
            5544: "소위 성적 장학금은 학교에서 광범위한 시험 준비를 제공받은 지원자에게 유리했다.",
            6092: "기숙사 상담원은 세탁실이 기숙사의 자정 정숙 시간 전에 문을 닫는다고 말했다.",
            6093: "시설 관리자는 캠퍼스 공공요금이 기숙사비와 식비와 별도로 부과된다고 설명했다.",
        },
        "zh": {
            4495: "教授认为，在历史解释中，证据应该胜过传统。",
        },
        "hi": {
            1578: "छात्र संघ की बैठक में छात्र कक्षा का एक प्रतिनिधि चुनेंगे।",
            5544: "तथाकथित योग्यता छात्रवृत्ति ने उन आवेदकों को लाभ पहुंचाया जिनके स्कूलों ने व्यापक परीक्षा तैयारी दी थी।",
        },
        "vi": {
            274: "Giáo sư kinh tế học nói rằng ngưỡng nghèo giúp so sánh thu nhập gia đình.",
            3449: "Trong hội thảo tôn giáo, giáo sư phân tích luân hồi như một lý thuyết về bản sắc cá nhân.",
            378: "Bạn cùng phòng nói rằng màu xanh trong phòng ký túc xá khiến bạn ấy thấy yên bình.",
            541: "Sau buổi giảng tối, nhân viên an ninh khuôn viên trường đã giúp tôi tìm ký túc xá.",
            579: "Khi bước vào giảng đường, sinh viên xuất trình thẻ đại học cho trợ giảng.",
            1057: "Tiêu đề của giáo trình lịch sử cho biết rõ chủ đề chính của sách.",
        },
        "id": {
            274: "Profesor ekonomi mengatakan bahwa garis kemiskinan membantu membandingkan pendapatan keluarga.",
        },
        "th": {
            378: "รูมเมตของฉันบอกว่าสีน้ำเงินในห้องหอพักทำให้รู้สึกสงบ",
            535: "อาจารย์ที่ปรึกษาของเราบอกว่ารถบัสในมหาวิทยาลัยน่าจะมาถึงช้า",
            1180: "สำนักงานทะเบียนใส่ชื่อฉันไว้ในรายชื่อผู้รอเรียนวิชาชีววิทยา",
            1261: "เจ้าหน้าที่สำนักงานนายทะเบียนช่วยฉันทำบัตรนักศึกษาที่หายใหม่",
            1263: "จุดแข็งที่ยิ่งใหญ่ที่สุดของเธอในการฝึกงานคือการอธิบายแนวคิดทางเทคนิคให้พนักงานใหม่เข้าใจ",
            1647: "การคัดเลือกแหล่งข้อมูลปฐมภูมิช่วยกำหนดการบรรยายของศาสตราจารย์ประวัติศาสตร์เรื่องสงครามกลางเมือง",
            2036: "ภาควิชาจะดำเนินการสำรวจพฤติกรรมการเรียนของนักศึกษาปีหนึ่งในภาคเรียนนี้",
            2253: "นักสังคมวิทยาในวิชาปีหนึ่งของเราศึกษาว่านโยบายมหาวิทยาลัยส่งผลต่อนักศึกษาจากชุมชนต่าง ๆ อย่างไร",
            2283: "การปรับปรุงห้องสมุดเพิ่มห้องอ่านหนังสือเงียบ ๆ โดยไม่ลดพื้นที่สำหรับคอลเลกชันสิ่งพิมพ์",
            2404: "ความไม่เป็นที่นิยมของตำราทำให้ภาควิชาเลือกฉบับอื่นในภาคการศึกษาหน้า",
            2409: "ศาสตราจารย์ด้านธรณีวิทยาอภิปรายถึงความไม่เหมาะสมของหินชนิดนี้สำหรับฐานรากอาคารในเขตแผ่นดินไหว",
            2469: "ในเศรษฐศาสตร์ ความไม่แน่นอนของอัตราดอกเบี้ยทำให้การวางแผนค่าเล่าเรียนระยะยาวซับซ้อนขึ้น",
            2478: "ความแน่นอนของเวลาทำการประจำสัปดาห์ช่วยให้นักศึกษาวางแผนพบอาจารย์ที่ปรึกษาได้",
            2570: "การปรับปรุงของการออกแบบสะพานช่วยลดแรงเค้นโดยไม่เพิ่มน้ำหนัก",
            2675: "ในจิตวิทยา การไตร่ตรองเกี่ยวกับทางเลือกในอดีตอาจเผยให้เห็นรูปแบบการตัดสินใจ",
            3275: "ศาสตราจารย์รัฐศาสตร์อธิบายว่าสถาบันที่อ่อนแออาจทำให้รัฐไม่สามารถปกครองได้อย่างไร",
            3312: "นักประวัติศาสตร์โต้แย้งว่านโยบายภาษาทำให้การทำให้เป็นชายขอบของนักศึกษาชนพื้นเมืองในมหาวิทยาลัยของรัฐรุนแรงขึ้น",
            3330: "นักประวัติศาสตร์ศิลป์เสนอว่าโพรเทรตเรอเนซองส์แบบฉบับผสมผสานใบหน้าในอุดมคติเข้ากับสัญลักษณ์ของสถานะทางสังคม",
            3483: "ในสัมมนาวิศวกรรม ศาสตราจารย์วิเคราะห์ว่าความช่างคิดช่วยให้นักศึกษาออกแบบสะพานที่ใช้งานได้ด้วยวัสดุจำกัดอย่างไร",
            3541: "โครงการฟื้นฟูของคลินิกในมหาวิทยาลัยใช้การวัดซ้ำเพื่อประเมินว่าผู้ป่วยโรคหลอดเลือดสมองฟื้นการควบคุมการเคลื่อนไหวได้อย่างไร",
            3558: "ศาสตราจารย์ด้านระบาดวิทยาเชื่อมโยงการสัมผัสเชื้อราในมหาวิทยาลัยเป็นเวลานานกับอาการทางระบบหายใจของผู้อยู่อาศัย",
            3613: "ศาสตราจารย์เคมีแสดงให้เห็นว่าสารประกอบที่ละลายได้จะละลายได้ง่ายในของเหลวที่เลือก",
            4302: "ก่อนเข้าร่วมการศึกษาที่มีมนุษย์เป็นผู้เข้าร่วม ผู้เข้าร่วมได้ลงนามในหนังสือสละสิทธิ์ที่ยอมรับความไม่สบายใจทางอารมณ์ที่อาจเกิดขึ้น",
            4553: "ในการบรรยายฟิสิกส์ แรงผลักทางไฟฟ้าสถิตผลักทรงกลมที่มีประจุทั้งสองออกจากกัน",
            4560: "ศาสตราจารย์เตือนว่าการลอกเลียนผลงานในรายงานวิจัยอาจทำให้นักศึกษาถูกพักการเรียนจากมหาวิทยาลัย",
            4670: "การฟื้นตัวทางการเงินของมหาวิทยาลัยทำให้เปิดสอนหลายวิชาได้อีกครั้งในภาคการศึกษาหน้า",
            4741: "ห้องปฏิบัติการชีววิทยาต้องการการวัดระดับออกซิเจนในแต่ละตัวอย่างอย่างระมัดระวัง",
            4755: "จุดอ่อนประการหนึ่งของแบบสำรวจคือไม่รวมนักศึกษาที่อาศัยอยู่นอกมหาวิทยาลัย",
            4767: "ศาสตราจารย์กล่าวชื่นชมมายาสำหรับการวิเคราะห์ข้อมูลการเลือกตั้งอย่างรอบคอบ",
            4850: "ใช้ราวจับที่ขั้นบันไดสุดท้ายเพราะบันไดหอพักสูงชัน",
            5332: "นักศึกษาได้ทำแบบสอบถามเกี่ยวกับพฤติกรรมการนอนเพื่อโครงการวิจัยจิตวิทยา",
            5349: "การทดแทนเครื่องซักผ้าที่เสียในหอพักช่วยลดข้อร้องเรียนของนักศึกษา",
            5531: "ระหว่างเวลาพบอาจารย์ที่ปรึกษา อาจารย์ที่ปรึกษาได้ยื่นคำร้องในนามของนักศึกษาต่างชาติคนหนึ่ง",
            5544: "ทุนการศึกษาที่เรียกว่าเป็นทุนความสามารถกลับเอื้อประโยชน์แก่ผู้สมัครจากโรงเรียนที่มีการเตรียมสอบอย่างเข้มข้น",
            5554: "การเสริมสร้างบริการอาชีพของมหาวิทยาลัยช่วยให้นักศึกษาหางานฝึกงานภาคฤดูร้อนได้",
            5862: "การโยกย้ายของภาควิชาต้องใช้วิธีการอย่างรอบคอบเพื่อรักษาตัวอย่างในห้องปฏิบัติการระหว่างการย้าย",
            5891: "การทำแผนที่ยีนสมัยใหม่ผสานแบบจำลองทางสถิติกับข้อมูลการหาลำดับเพื่อระบุตำแหน่งของความแปรผันที่เกี่ยวข้องกับโรคทางพันธุกรรม",
            5910: "การนำออกหนังสือเก่าทำให้ห้องสมุดมีพื้นที่มากขึ้นสำหรับเอกสารประกอบวิชาปัจจุบัน",
            6373: "ในธรณีวิทยา การละลายของแผ่นน้ำแข็งอาจเปลี่ยนการหมุนเวียนของมหาสมุทรและเร่งการเปลี่ยนแปลงสภาพภูมิอากาศระดับภูมิภาค",
        },
    }
    for language, repairs in native_example_repairs.items():
        for item_id, value in repairs.items():
            translations[f"builtin:{item_id}"]["example"][language] = value

    # Remove unmistakable cross-script fragments left inside otherwise native
    # translations.  These are not stylistic rewrites; each fragment is a
    # copied word from another language or a malformed mixed-script token.
    mixed_script_repairs = {
        "hi": {
            536: "मेरे सलाहकार को निश्चित रूप से पता है कि विषय बदलने के फॉर्म कब जमा करने हैं।",
            5377: "सलाहकार ने मेरे पहले सेमेस्टर के लिए उचित पाठ्यभार सुझाया।",
            5891: "आधुनिक जीन मानचित्रण सांख्यिकीय मॉडलों को अनुक्रमण डेटा से मिलाकर वंशानुगत रोगों से जुड़े आनुवंशिक रूपांतरों का स्थान निर्धारित करता है।",
            6154: "हमारी भूविज्ञान की कक्षा में प्रोफेसर ने दिखाया कि भूकंप भ्रंश के साथ ऊर्जा छोड़कर भू-दृश्य को कैसे बदल सकता है।",
        },
        "ko": {
            1149: "오리엔테이션 기간에 자원봉사자들은 캠퍼스 푸드 팬트리에서 신입생들에게 음식을 나누어 주는 일을 도왔다.",
            1619: "경제학 교재는 가격 상승이 항상 소비자 수요를 줄인다는 개념에 의문을 제기한다.",
            2479: "경제학 교수는 보상에는 노동에 대한 대가로 지급되는 임금과 복리후생이 포함된다고 설명했다.",
            3682: "우리 언어학 세미나에서는 자료를 언어 변화에 관한 더 포괄적인 이론의 틀 안에서 해석할 때에만 서로 경쟁하는 분석들이 일관성을 갖는다.",
            4973: "경제학 개론 강의에서 교수는 산업 혁명 기간 농업이 노동 시장을 어떻게 변화시켰는지 설명한다.",
            5334: "교수는 링컨의 인용문이 민주주의에 관한 교과서의 주장을 어떻게 뒷받침하는지 설명했다.",
        },
        "th": {
            1349: "นักศึกษาคนหนึ่งลื่นบนพื้นโรงอาหารที่เปียก แต่เหตุการณ์นั้นไม่ทำให้เกิดการบาดเจ็บร้ายแรง",
            2908: "การล่มสลายโดยสิ้นเชิง, การล่มสลายของการเจรจา, การสื่อสารขัดข้อง, ภาวะจิตใจพังทลาย, การขัดข้องของระบบ",
            5376: "ศาสตราจารย์ประวัติศาสตร์ศิลป์กล่าวว่าภาพจิตรกรรมฝาผนังที่เป็นประเด็นถกเถียงนั้นกลายเป็นกระแสฮือฮาในมหาวิทยาลัย",
            5830: "ในช่วงเวลาพบอาจารย์ ศาสตราจารย์ลีทุ่มเทช่วยนักศึกษาเข้าใจบทที่ยากในตำราจิตวิทยาของพวกเขา",
        },
        "ja": {
            1536: "典型的な新入生の時間割には、講義と各授業前の定期的な読書が含まれる。",
            1755: "〜を非難する、虚偽の告発をする、公に非難する、政府を非難する、人を〜で非難する",
            2191: "指導教員は、化学での私の目覚ましい上達は定期的な学習によるものだと言った。",
            2401: "婚姻上の不貞、不貞の疑い、感情的な不倫、不貞の告発、婚姻における不貞",
            4686: "生物学の教授は難しい内容を理解しやすく説明するので、私は尊敬している。",
            5245: "キャンパスのフードパントリーの崇高な目的は、定期的な食事を買えない学生を助けることだ。",
        },
        "zh": {
            1536: "典型的大一新生课表包括讲座，以及每节课前的定期阅读。",
        },
    }
    for language, repairs in mixed_script_repairs.items():
        for item_id, value in repairs.items():
            translations[f"builtin:{item_id}"]["example" if item_id not in {1755, 2401, 2908} else "collocations"][language] = value

    set_meaning(6199, "th", "อาจารย์พิเศษ, อาจารย์นอกเวลา")
    set_meaning(6214, "th", "การยกเว้นค่าธรรมเนียม, การได้รับยกเว้นค่าธรรมเนียม")
    set_meaning(6316, "th", "การท่องจำแบบกลไก")

    # Keep one target phrase per English collocation.  The former versions
    # accidentally translated "firstly and foremost" and "it is important"
    # as extra comma-separated items.
    first_collocation_translations = {
        "ja": "第一に、第二に、第三に、何よりもまず、重要なのは",
        "zh": "首先，其次，第三，首先也是最重要的，重要的是",
        "hi": "सबसे पहले, दूसरे, तीसरे, सबसे पहले और सबसे महत्वपूर्ण, यह महत्वपूर्ण है",
        "vi": "thứ nhất, thứ hai, thứ ba, trước hết và quan trọng nhất, điều quan trọng là",
        "ko": "첫째, 둘째, 셋째, 무엇보다도 먼저, 중요한 점은",
        "id": "pertama, kedua, ketiga, pertama dan yang terpenting, penting untuk",
        "th": "ประการแรก, ประการที่สอง, ประการที่สาม, ประการแรกและสำคัญที่สุด, สิ่งสำคัญคือ",
        "es": "en primer lugar, en segundo lugar, en tercer lugar, en primer lugar y ante todo, es importante",
    }
    for language, value in first_collocation_translations.items():
        translations["builtin:4870"]["collocations"][language] = value

    # Exact adjacent-word duplication is an unambiguous generation artifact
    # in these target-language phrase fields.  Do not collapse near-duplicates
    # such as Thai compounds or Japanese ものの.
    for item_id in by_id:
        for field in ("example", "collocations"):
            for language in ("th", "vi", "id"):
                value = translations[f"builtin:{item_id}"][field].get(language, "")
                if language == "th":
                    value = re.sub(r"([ก-๛]+)\s+\1", r"\1", value)
                else:
                    value = re.sub(r"\b([A-Za-zÀ-ỹĐđ]{2,})\s+\1\b", r"\1", value, flags=re.I)
                translations[f"builtin:{item_id}"][field][language] = value
            value = translations[f"builtin:{item_id}"][field].get("ja", "")
            translations[f"builtin:{item_id}"][field]["ja"] = re.sub(r"(?<!も)のの", "の", value)

    # The remaining Vietnamese examples were generated as unaccented ASCII
    # transliterations. Replace every such row with a complete native-script
    # translation prepared from its English source sentence.
    vietnamese_repairs_path = BASE_DIR / "vietnamese_example_repairs.json"
    vietnamese_repairs = json.loads(vietnamese_repairs_path.read_text(encoding="utf-8"))
    for item_id, value in vietnamese_repairs.items():
        translations[f"builtin:{int(item_id)}"]["example"]["vi"] = value

    # Restore mandatory Spanish accent marks that were systematically dropped
    # by an earlier generation pass.  Ambiguous words such as "trabajo" and
    # "practica" are deliberately excluded; this table only contains forms
    # whose unaccented spelling is clearly wrong in the affected sentences.
    spanish_accents = {
        "biologia": "biología", "psicologia": "psicología", "sociologia": "sociología",
        "geologia": "geología", "quimica": "química", "economia": "economía",
        "politica": "política", "investigacion": "investigación", "educacion": "educación",
        "informacion": "información", "comunicacion": "comunicación", "inscripcion": "inscripción",
        "academico": "académico", "academica": "académica", "proximo": "próximo",
        "proxima": "próxima", "despues": "después", "manana": "mañana", "tambien": "también",
        "asi": "así", "dificil": "difícil", "util": "útil", "periodo": "período",
        "analisis": "análisis", "tecnologia": "tecnología", "teoria": "teoría",
        "decision": "decisión", "opcion": "opción", "leccion": "lección", "sesion": "sesión",
        "metodo": "método", "numero": "número", "electrica": "eléctrica", "facil": "fácil",
        "pasantia": "pasantía", "todavia": "todavía", "ultimo": "último", "ultima": "última",
        "energia": "energía", "companero": "compañero", "calefaccion": "calefacción",
        "asesoria": "asesoría", "proposito": "propósito", "orientacion": "orientación",
        "estadistica": "estadística", "matricula": "matrícula", "titulo": "título",
        "explico": "explicó", "analizo": "analizó", "mostro": "mostró", "examino": "examinó",
        "presento": "presentó", "comparo": "comparó", "incluyo": "incluyó", "ayudo": "ayudó",
        "cafeteria": "cafetería", "libreria": "librería", "presentacion": "presentación",
        "conversacion": "conversación", "reunion": "reunión", "sugerira": "sugerirá",
        "encontro": "encontró", "tutorias": "tutorías", "pasantia": "pasantía",
        "pasantias": "pasantías", "ano": "año", "mas": "más", "despues": "después",
        "ultimo": "último", "ultima": "última", "dificil": "difícil", "periodo": "período",
        "companera": "compañera", "companeras": "compañeras", "companeros": "compañeros",
        "pequeno": "pequeño", "pequena": "pequeña", "pequenas": "pequeñas",
        "politicas": "políticas", "publicas": "públicas", "politica": "política",
        "politico": "político", "politicos": "políticos", "relacion": "relación",
        "relaciono": "relacionó", "razon": "razón", "informatica": "informática",
        "diseno": "diseño", "ingenieria": "ingeniería", "geologo": "geólogo",
        "astronomia": "astronomía", "hidrogeno": "hidrógeno", "molecula": "molécula",
        "moleculas": "moléculas", "atomos": "átomos", "oxigeno": "oxígeno",
        "presion": "presión", "disminucion": "disminución", "descomposicion": "descomposición",
        "recesion": "recesión", "inversion": "inversión", "interes": "interés",
        "prestamos": "préstamos", "concentracion": "concentración", "solucion": "solución",
        "interpretacion": "interpretación", "participacion": "participación", "comision": "comisión",
        "redistribucion": "redistribución", "jurisdiccion": "jurisdicción", "satelite": "satélite",
        "comunicacion": "comunicación", "tecnologia": "tecnología", "teorico": "teórico",
        "teorica": "teórica", "publicas": "públicas", "suenos": "sueños", "sueno": "sueño",
        "medula": "médula", "facilmente": "fácilmente", "liquido": "líquido",
        "disolucion": "disolución", "celula": "célula", "trafico": "tráfico",
        "evaluo": "evaluó", "discutio": "discutió", "distinguio": "distinguió",
        "dibujo": "dibujó", "relaciono": "relacionó", "concentro": "concentró",
        "linguistica": "lingüística", "podria": "podría", "ningun": "ningún",
        "algun": "algún", "comprension": "comprensión", "migracion": "migración",
        "practicas": "prácticas", "advirtio": "advirtió", "explicacion": "explicación",
        "automoviles": "automóviles", "historicos": "históricos", "catedra": "cátedra",
        "decada": "década", "linea": "línea", "grafico": "gráfico", "reaccion": "reacción",
        "transformacion": "transformación", "proporcion": "proporción", "participacion": "participación",
        "version": "versión", "limite": "límite", "edicion": "edición",
        "publicos": "públicos",
        "codigo": "código", "generacion": "generación", "region": "región",
        "estacion": "estación", "nacion": "nación", "accion": "acción", "seccion": "sección",
        "adquisicion": "adquisición", "aplicacion": "aplicación", "situacion": "situación",
        "organizacion": "organización", "institucion": "institución", "produccion": "producción",
        "reproduccion": "reproducción", "tradicion": "tradición", "construccion": "construcción",
        "destruccion": "destrucción", "proliferacion": "proliferación", "fundacion": "fundación",
        "evolucion": "evolución", "revolucion": "revolución", "conservacion": "conservación",
        "observacion": "observación", "representacion": "representación", "distribucion": "distribución",
        "tecnologica": "tecnológica", "sociologica": "sociológica", "economica": "económica",
        "cientifica": "científica", "historica": "histórica", "geografica": "geográfica",
        "biologica": "biológica", "fisica": "física", "medica": "médica", "critica": "crítica",
    }
    for item in vocabulary:
        record = translations[f"builtin:{item['id']}"]
        for field in ("example", "collocations"):
            entry = record[field]
            value = entry.get("es", "")
            for source, target in spanish_accents.items():
                value = re.sub(
                    rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){source}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])",
                    lambda match, target=target: target.capitalize()
                    if match.group(0)[0].isupper()
                    else target,
                    value,
                    flags=re.IGNORECASE,
                )
            entry["es"] = value

    # Restore the interrogative accent in the common explanatory construction
    # "explicar cómo ...".  This is deliberately limited to verb contexts so
    # that valid uses such as "trabajo como tutor" remain unchanged.
    for item in vocabulary:
        entry = translations[f"builtin:{item['id']}"]["example"]
        value = entry.get("es", "")
        value = re.sub(
            r"\b(explica|explicó|explicar|explicaba|mostró|muestra|describió|describir|analizó|analiza|demostró|demuestra|enseñó|enseña|examinó|examina|sostuvo|sostiene|comparó|compara|identificó|identifica|presentó|presenta|determinó|determina) como\b",
            r"\1 cómo",
            value,
            flags=re.IGNORECASE,
        )
        value = re.sub(r"\b(explica|explicó|explicar|mostró|muestra|analizó|analiza|demostró|demuestra|examinó|examina) por que\b", r"\1 por qué", value, flags=re.IGNORECASE)
        value = re.sub(r"\bpor que\b", "por qué", value, flags=re.IGNORECASE)
        value = re.sub(r"\bfecha limite\b", "fecha límite", value, flags=re.IGNORECASE)
        value = re.sub(r"\b(la biblioteca|mi compañero de cuarto|el compañero de cuarto) esta\b", r"\1 está", value, flags=re.IGNORECASE)
        value = re.sub(r"\bpublico (?=(un|una|el|la))", "publicó ", value, flags=re.IGNORECASE)
        value = re.sub(r"\bcommunity colleges\b", "colegios comunitarios", value, flags=re.IGNORECASE)
        value = re.sub(r"\bcommunity college\b", "colegio comunitario", value, flags=re.IGNORECASE)
        entry["es"] = value

    # Context-dependent Spanish accents and unmistakable untranslated or
    # malformed words.  These cannot be handled safely by a blanket spelling
    # substitution because forms such as "como", "esta" and "uso" can also
    # be valid without an accent in another grammatical role.
    spanish_example_repairs = {
        95: "Mi profesor dijo que la media de estas calificaciones es doce.",
        1246: "La cafetería redujo el desperdicio de alimentos al donar las comidas no utilizadas a un refugio.",
        1221: "La clase de ingeniería va a resolver el problema del diseño del puente con un modelo computacional.",
        1276: "Su secreto para sacar una A era repasar los apuntes antes de cada examen.",
        1375: "Después de inscribirme, la suma de las tarifas de la biblioteca apareció en mi cuenta estudiantil.",
        1539: "Un asesor residente me ayudó a informar sobre un calentador roto en mi residencia.",
        1703: "El profesor puede rechazar los informes de laboratorio que carezcan del grupo de control requerido.",
        1737: "A diferencia de la cafetería de la residencia, el café del campus sirve sándwiches frescos al mediodía.",
        1777: "Mi asesor me ayudó a resolver un problema de inscripción antes de que comenzara el semestre.",
        1790: "El departamento de ingeniería busca talento estudiantil para su programa de prácticas de verano.",
        1805: "El libro de economía explica por qué las diferencias salariales regionales pueden persistir entre las zonas urbanas y rurales.",
        1918: "Nuestro curso de estudios urbanos examina cómo las ciudades ofrecen empleos mientras presionan el transporte público.",
        2030: "El consejo estudiantil incluyó el costo de los libros de texto en la agenda de la reunión del lunes.",
        2055: "El asesor dijo que un horario uniforme haría más fácil la inscripción de los estudiantes de primer año.",
        2541: "El profesor describió a los estudiantes resilientes que se recuperan rápidamente después de recibir bajas calificaciones en el examen parcial.",
        2610: "Independientemente de las condiciones meteorológicas, la clase de geología recogerá muestras cerca del río.",
        2737: "La clase de etnobotánica examinó cómo las plantas medicinales apoyan la atención médica en comunidades remotas.",
        3008: "Contrariamente a lo que afirmó la clase, algunas plantas del desierto siguen activas durante las noches frescas.",
        3300: "El profesor de políticas públicas examinó informes ministeriales antes de evaluar el programa estatal de vivienda.",
        3311: "El estudio longitudinal siguió a los mismos estudiantes de primer año durante cuatro años para medir cambios en el estrés.",
        3316: "El profesor de economía presenta el liberalismo como una teoría que favorece la propiedad privada y la intervención gubernamental limitada.",
        3439: "Desde una perspectiva sociológica, el profesor sostiene que la vivienda del campus puede reproducir las divisiones sociales mediante un acceso desigual a los recursos.",
        3555: "El profesor sostuvo que el calor residual puede distorsionar las mediciones en un experimento climático sensible.",
        3578: "En geología, el profesor mostró cómo se acumula el sedimento donde el río pierde velocidad cerca de su desembocadura.",
        3615: "El profesor comparó cada disolvente midiendo su polaridad y su tasa de evaporación en el laboratorio.",
        3655: "En la clase de ciencia de materiales, el profesor explicó por qué los polímeros mutables reaccionan de manera distinta a los cambios de temperatura.",
        3816: "En la clase del profesor, los combustibles fósiles siguieron siendo la fuente de energía predominante durante la industrialización inicial.",
        3847: "A pesar del tamaño reducido de la muestra, el profesor de lingüística sostuvo que el experimento aportaba evidencia para la teoría propuesta.",
        3856: "El profesor de biología presentó a Darwin como un naturalista cuyas observaciones de campo cuestionaron las teorías establecidas sobre el cambio de las especies.",
        3912: "El profesor de filosofía explicó el universalismo como la creencia de que la preocupación moral debe extenderse a todas las personas.",
        3947: "El historiador del arte situó el Renacimiento de Florencia dentro de sistemas cambiantes de mecenazgo que transformaron la identidad cívica.",
        4101: "El seminario de relaciones internacionales examinó cómo el unilateralismo puede debilitar la cooperación basada en tratados.",
        4262: "Durante un seminario de astronomía, el profesor sostuvo que un agujero negro gigantesco podría distorsionar el espacio-tiempo de toda una galaxia.",
        4336: "La clase de paleontología relacionó las extinciones del Pleistoceno con cambios rápidos en el clima.",
        4584: "El profesor de ingeniería explicó por qué una fuga de refrigerante puede aumentar el impacto climático de un edificio.",
        4719: "Intento resistir la tentación de revisar el teléfono mientras estudio en la biblioteca.",
        4724: "Omitir el mantenimiento obligatorio puede arruinar el equipo del laboratorio de ingeniería.",
        4814: "El laboratorio de química tiene reglas de seguridad estrictas sobre el uso de gafas y zapatos cerrados.",
        4838: "El profesor de geología usó una exploración del fondo marino para explicar el movimiento de las placas.",
        4903: "El libro de biología explica por qué una rata puede transmitir ciertas enfermedades.",
        4954: "El profesor de astronomía explica cómo la energía solar impulsa la circulación atmosférica en algunos planetas.",
        5113: "Históricamente, las universidades estadounidenses admitían a menos mujeres, pero los patrones de matriculación cambiaron durante el siglo veinte.",
        5247: "El libro de antropología describe regalar como una norma que fortalece las relaciones dentro de muchas comunidades.",
        5324: "La psicología estudia cómo la memoria, la emoción y la experiencia social influyen en la conducta humana.",
        5369: "En este escenario económico, subir las tasas de interés reduce los préstamos, pero aumenta el desempleo.",
        5375: "Nuestro seminario de primer año se reúne semanalmente para analizar cómo las redes sociales moldean las opiniones políticas.",
        5449: "El profesor de ingeniería explicó que una tonelada de fuerza puede deformar una viga de acero.",
        5551: "El superintendente de la universidad presentó pruebas a favor de ampliar el financiamiento público de los colegios comunitarios.",
        5639: "Los estudiantes universitarios de primera generación pueden ser vulnerables a las confusas normas de ayuda financiera durante su primer semestre.",
        5666: "Nuestro libro de sociología explica por qué los campus suburbanos suelen depender de estudiantes que viajan desde casa.",
        5791: "La clase de ingeniería comparó motores diésel con motores eléctricos durante una demostración de laboratorio.",
        6014: "El asesor marcó mi problema de vivienda como urgente porque el contrato del dormitorio vence mañana.",
        6033: "El profesor de economía explicó por qué el ingreso familiar mediano puede revelar la desigualdad con más claridad que el promedio.",
        6119: "El profesor de psicología examinó si el temperamento durante la infancia predecía la cooperación en la adolescencia.",
        6146: "El profesor de astronomía usó una supernova para demostrar cómo las estrellas masivas crean elementos más pesados que el hierro.",
        1933: "La oficina del registrador publicó una actualización sobre la fecha límite para retirar una materia.",
        5187: "La universidad ofreció al profesor que se jubilaba un pago único en vez de pagos mensuales de pensión.",
        579: "Al entrar al aula, los estudiantes mostraron sus identificaciones universitarias al ayudante de cátedra.",
        964: "Mi hermana estudia en un colegio comunitario cercano y visita el campus los fines de semana.",
        1110: "El asesor explicó cómo transferir créditos de un colegio comunitario a la universidad.",
        1130: "Durante la última década, los cursos en línea han cambiado la manera en que los colegios comunitarios atienden a los estudiantes que trabajan.",
        1682: "El departamento de ingeniería inició un proyecto conjunto con un colegio comunitario cercano.",
        2054: "El gobernador visitó nuestro campus para hablar sobre fondos para los colegios comunitarios.",
        5187: "La universidad ofreció al profesor que se jubilaba un pago único en vez de pagos mensuales de pensión.",
        5437: "El alto salario de las prácticas puede tentar a los estudiantes a ignorar si el puesto ofrece capacitación útil.",
        5503: "La clase examinó por qué muchos estudiantes residen cerca del campus pese al aumento de los alquileres.",
        5521: "El programa del curso prohibirá que los estudiantes usen software generativo durante el examen parcial para hacer en casa.",
    }
    for item_id, value in spanish_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["es"] = value

    vietnamese_mixed_example_repairs = {
        1563: "Chính sách bảo vệ dữ liệu của thư viện yêu cầu sinh viên sử dụng mật khẩu an toàn.",
        1601: "Cố vấn nói rằng các kỹ năng mềm có thể giúp tôi giao tiếp với đồng nghiệp trong kỳ thực tập.",
        1647: "Việc lựa chọn các nguồn tư liệu gốc đã định hình bài giảng lịch sử của giáo sư về Nội chiến.",
        1649: "Cố vấn hỏi liệu sức khỏe tâm thần của sinh viên có đang ảnh hưởng đến việc đi học hay không.",
        1693: "Giọng điệu của giáo trình kinh tế trở nên phê phán hơn ở các chương sau.",
        1737: "Khác với nhà ăn ký túc xá, quán cà phê trong trường phục vụ bánh sandwich tươi vào buổi trưa.",
        1754: "Hơn nữa, thư viện tổ chức các buổi hướng dẫn nghiên cứu miễn phí trong tuần thi giữa kỳ.",
        1761: "Giáo sư sinh học nói rằng y học hiện đại đã cải thiện khả năng sống sót sau nhiều bệnh truyền nhiễm.",
        1790: "Khoa kỹ thuật đang tìm kiếm sinh viên tài năng cho chương trình thực tập mùa hè.",
        1796: "Hội thảo năm nhất của chúng tôi thử nghiệm một chương trình cố vấn thí điểm cho sinh viên mới.",
        1862: "Giáo trình tâm lý học mô tả một cơ chế đối phó giúp sinh viên kiểm soát căng thẳng trong kỳ thi giữa kỳ.",
        1887: "Lớp khoa học chính trị phân tích các bài phát biểu của tổng thống trong cuộc bầu cử vừa qua.",
        1902: "Khoảng một phần tư sinh viên năm nhất sống trong khu nhà ở của trường vào học kỳ đầu tiên.",
        1950: "Tuyết dày khiến khuôn viên trường đóng cửa và hủy buổi thực hành chiều của chúng tôi.",
        2073: "Trong khóa lịch sử năm nhất, giáo sư mô tả thời đại công nghiệp đã biến đổi các thành phố Mỹ như thế nào.",
        2085: "Cố vấn giúp tôi chuyển tín chỉ trung học vào trường đại học.",
        2111: "Khoa sinh học đã có tăng trưởng ổn định trong hoạt động nghiên cứu bậc đại học.",
        2179: "Kỳ thực tập bắt buộc gây áp lực cho lịch trình của sinh viên trong tuần thi giữa kỳ.",
        2185: "Các quy tắc lỏng lẻo trong bếp ký túc xá có thể gây ra vấn đề an toàn.",
        2189: "Phòng thí nghiệm địa chất dùng bể nước để mô phỏng áp suất dưới lòng đất.",
        2293: "Giáo sư kỹ thuật giải thích điện trở giới hạn dòng điện trong mạch như thế nào.",
        2319: "Giáo trình khoa học chính trị mô tả cách một phong trào dân tộc chủ nghĩa có thể giành được sự ủng hộ trong khủng hoảng kinh tế.",
        2321: "Sau vụ cháy rừng, khu học tập từng xanh tươi trở nên không thể nhận ra đối với những sinh viên quay lại.",
        2382: "Cố vấn nghề nghiệp nói rằng kỳ thực tập có ý nghĩa có thể nâng cao giá trị bản thân của sinh viên hơn chỉ đạt điểm cao.",
        2395: "Trong bài giảng kinh tế, giáo sư liên hệ khả năng sinh lời dài hạn với việc phân bổ nguồn lực hiệu quả thay vì tăng doanh số nhanh.",
        2404: "Sự không phổ biến của giáo trình khiến khoa quyết định chọn một ấn bản khác vào học kỳ tới.",
        2457: "Trong bài giảng lịch sử, giáo sư cho rằng việc biết chữ rộng rãi từng là điều không thể tưởng tượng đối với nhiều nhà cai trị.",
        2538: "Các câu trả lời khảo sát không theo thứ tự khiến giáo sư khó so sánh ý kiến của sinh viên.",
        2543: "Nhà sử học đặt câu hỏi liệu ưu thế quân sự có tự nó giải thích được sự bành trướng nhanh chóng của đế chế hay không.",
        2559: "Phạm vi của dự án ngôn ngữ học bao gồm các giọng vùng miền và ảnh hưởng của chúng đến giao tiếp trong lớp.",
        2573: "Môn tâm lý học trình bày khả năng phục hồi như một kỹ năng sinh viên có thể củng cố sau những thất bại học tập.",
        2610: "Bất kể thời tiết, lớp địa chất sẽ thu thập mẫu gần con sông.",
        2625: "Trong sinh học, mô biểu bì tạo thành một lớp bảo vệ quanh nhiều cơ quan.",
        2637: "Trong bài giảng về chính sách môi trường, giáo sư áp dụng nguyên tắc người gây ô nhiễm phải trả tiền vào một trường hợp làm sạch sông.",
        2731: "Giáo sư điều dưỡng giải thích rằng can thiệp này cần thiết về mặt y tế vì tình trạng của bệnh nhân đang xấu đi.",
        2737: "Bài giảng về dân tộc thực vật học xem xét cách các loài cây dược liệu hỗ trợ chăm sóc sức khỏe ở các cộng đồng xa xôi.",
        2739: "Mẫu nghiên cứu gồm những sinh viên năm nhất tình nguyện tham gia thông qua khoa tâm lý học của trường.",
        2743: "Nhà thống kê trong hội thảo nghiên cứu giải thích tại sao mẫu khảo sát quá nhỏ.",
        2756: "Trong xã hội học, sự tham gia tự nguyện có nghĩa là sinh viên tự chọn tham gia nghiên cứu mà không chịu áp lực từ nhà nghiên cứu.",
        2768: "Trong bài giảng kinh tế học, chủ nghĩa xã hội được phân tích như một hệ thống phân bổ nguồn lực tập thể.",
        2774: "Giáo trình kinh tế phân tích một vụ thâu tóm thù địch đối với một ngân hàng khu vực.",
        2918: "Giải tích giúp sinh viên kỹ thuật mô tả cách các lực thay đổi tác động lên vật thể đang chuyển động.",
        3008: "Trái với nhận định trong bài giảng, một số cây sa mạc vẫn hoạt động vào những đêm mát.",
        3014: "Vỏ xoắn ốc không thể nhầm lẫn của hóa thạch giúp lớp địa chất xác định loài sinh vật biển cổ đại của nó.",
        3066: "Trong bài giảng xã hội học, giáo sư giải thích tinh thần thể thao là sự tôn trọng đối thủ và tinh thần chơi đẹp.",
    }
    for item_id, value in vietnamese_mixed_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["vi"] = value

    indonesian_mixed_example_repairs = {
        378: "Teman sekamar saya berkata bahwa warna biru di kamar asrama kami terasa menenangkan.",
        415: "Peraturan asrama menyatakan bahwa jam tenang dimulai pukul sepuluh.",
        425: "Makalah sejarah saya harus dikumpulkan besok, jadi saya perlu memakai printer perpustakaan.",
        442: "Acara mahasiswa di gedung serikat mahasiswa dimulai setelah makan siang.",
        471: "Silakan bawa kartu mahasiswa Anda ke kantor registrar.",
        517: "Kualitas makanan di kafetaria kami meningkat semester ini.",
        562: "Masyarakat kita bergantung pada universitas untuk mempersiapkan mahasiswa menjadi warga yang bertanggung jawab.",
        579: "Saat memasuki ruang kuliah, para mahasiswa menunjukkan kartu identitas universitas kepada asisten pengajar.",
        673: "Pekerja di kafetaria kampus membantu saya menemukan makanan tanpa kacang tanah.",
        674: "Pers kampus melaporkan pemilihan pemerintahan mahasiswa.",
        750: "Teman sekamar saya bekerja di kafe kampus selama musim panas.",
        806: "Hilangnya beasiswa memaksa mahasiswa tahun kedua itu bekerja lebih lama.",
        872: "Seorang mahasiswa baru yang sukses memeriksa silabus sebelum memilih kelas semester depan.",
        939: "Ingatan seorang mahasiswa tentang sekolah menengah dapat membentuk harapannya terhadap kehidupan perguruan tinggi.",
        983: "Seseorang meninggalkan kalkulator di ruang belajar, jadi saya membawanya ke meja perpustakaan.",
        1186: "Kehadiran seorang tutor membantu mahasiswa tahun pertama memahami tugas statistik.",
        1195: "Penasihat memberi saya jawaban singkat tentang perubahan jurusan saya.",
        1209: "Mahasiswa itu menolak mengubah topik penelitiannya sebelum membahasnya dengan penasihat akademik.",
        1246: "Kafetaria mengurangi limbah makanan dengan menyumbangkan makanan yang tidak terpakai ke tempat penampungan.",
        1539: "Seorang penasihat asrama membantu saya melaporkan pemanas yang rusak di asrama.",
        1737: "Berbeda dengan kantin asrama, kafe kampus menyajikan sandwich segar saat makan siang.",
        1754: "Selain itu, perpustakaan mengadakan lokakarya penelitian gratis selama pekan ujian tengah semester.",
        1790: "Departemen teknik sedang mencari mahasiswa berbakat untuk program magang musim panas.",
        1862: "Buku teks psikologi itu menjelaskan mekanisme koping yang membantu mahasiswa mengendalikan stres selama ujian tengah semester.",
        1887: "Kelas ilmu politik menganalisis pidato presiden dalam pemilihan umum terakhir.",
        1902: "Sekitar seperempat mahasiswa tahun pertama tinggal di asrama kampus pada semester pertama mereka.",
        1950: "Salju lebat membuat kampus ditutup dan membatalkan praktikum sore kami.",
        2073: "Dalam mata kuliah sejarah tahun pertama, profesor menjelaskan bagaimana era industri mengubah kota-kota Amerika.",
        2085: "Penasihat membantu saya memindahkan kredit sekolah menengah ke universitas.",
        2111: "Departemen biologi mengalami pertumbuhan yang stabil dalam kegiatan penelitian sarjana.",
        2179: "Magang wajib itu membebani jadwal mahasiswa selama pekan ujian tengah semester.",
        2185: "Peraturan yang longgar di dapur asrama dapat menimbulkan masalah keselamatan.",
        2189: "Laboratorium geologi menggunakan tangki air untuk mensimulasikan tekanan bawah tanah.",
        2293: "Profesor teknik menjelaskan bagaimana hambatan listrik membatasi arus dalam rangkaian.",
        2319: "Buku teks ilmu politik menggambarkan bagaimana gerakan nasionalis dapat memperoleh dukungan selama krisis ekonomi.",
        2321: "Setelah kebakaran hutan, kawasan belajar yang dahulu hijau menjadi tidak dikenali oleh mahasiswa yang kembali.",
        2382: "Penasihat karier mengatakan bahwa magang yang bermakna dapat meningkatkan harga diri mahasiswa lebih daripada sekadar nilai tinggi.",
        2395: "Dalam kuliah ekonomi, profesor mengaitkan profitabilitas jangka panjang dengan alokasi sumber daya yang efisien, bukan dengan peningkatan penjualan yang cepat.",
        2404: "Ketidakpopuleran buku teks itu membuat departemen memilih edisi lain untuk semester berikutnya.",
        2457: "Dalam kuliah sejarah, profesor berpendapat bahwa literasi luas dahulu dianggap tak terpikirkan oleh banyak penguasa.",
        2538: "Jawaban survei yang tidak berurutan menyulitkan profesor membandingkan pendapat mahasiswa.",
        2543: "Sejarawan itu mempertanyakan apakah keunggulan militer saja dapat menjelaskan perluasan kekaisaran yang cepat.",
        2559: "Ruang lingkup proyek linguistik itu mencakup dialek regional dan pengaruhnya terhadap komunikasi di kelas.",
        2573: "Mata kuliah psikologi itu memperkenalkan ketahanan sebagai keterampilan yang dapat diperkuat mahasiswa setelah mengalami kegagalan akademik.",
        2610: "Terlepas dari cuaca, kelas geologi akan mengumpulkan sampel di dekat sungai.",
        2625: "Dalam biologi, jaringan epitel membentuk lapisan pelindung di sekitar banyak organ.",
        2637: "Dalam kuliah kebijakan lingkungan, profesor menerapkan prinsip pencemar membayar pada kasus pembersihan sungai.",
        2731: "Profesor keperawatan menjelaskan bahwa intervensi ini diperlukan secara medis karena kondisi pasien memburuk.",
        2737: "Kuliah etnobotani membahas bagaimana tanaman obat mendukung layanan kesehatan di komunitas terpencil.",
        2739: "Sampel penelitian itu terdiri atas mahasiswa tahun pertama yang secara sukarela mengikuti penelitian melalui departemen psikologi universitas.",
        2743: "Ahli statistik dalam seminar penelitian menjelaskan mengapa sampel survei itu terlalu kecil.",
        2756: "Dalam sosiologi, partisipasi sukarela berarti mahasiswa memilih mengikuti penelitian tanpa tekanan dari peneliti.",
        2768: "Dalam kuliah ekonomi, sosialisme dianalisis sebagai sistem alokasi sumber daya kolektif.",
        2774: "Buku teks ekonomi itu menganalisis pengambilalihan bermusuhan terhadap sebuah bank regional.",
        3008: "Bertentangan dengan pernyataan dalam kuliah, beberapa tanaman gurun tetap aktif pada malam yang sejuk.",
        3014: "Cangkang spiral fosil yang tidak mungkin keliru membantu kelas geologi mengidentifikasi spesies laut purba tersebut.",
        3066: "Dalam kuliah sosiologi, profesor menjelaskan bahwa sportivitas adalah rasa hormat kepada lawan dan semangat bermain secara adil.",
    }
    for item_id, value in indonesian_mixed_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["id"] = value

    # Repair the remaining high-confidence mixed-language examples found by
    # the offline source/target comparison.  These are sentence-level fixes:
    # technical terms and deliberate English-word explanations are retained
    # only where the source sentence is explicitly teaching the English form.
    additional_vietnamese_example_repairs = {
        325: "Giáo sư sẽ sớm tải đề cương đã chỉnh sửa lên trang web của môn học.",
        788: "Bạn cùng phòng gợi ý một giải pháp để mang sách của tôi đến thư viện.",
        941: "Giáo sư âm nhạc phân tích cách một bài hát phản ánh thời kỳ lịch sử của nó.",
        138: "Tôi cần một thứ gì đó cho bài thuyết trình của mình từ hiệu sách trong khuôn viên trường.",
        1320: "Giáo trình địa chất mô tả một nơi nào đó dưới khuôn viên trường, nơi các lớp đá cổ vẫn lộ ra.",
        1378: "Giáo trình lịch sử mô tả cách một binh sĩ viết thư về nhà trong thời Nội chiến.",
        316: "Hãy sắp xếp các câu trả lời khảo sát theo năm học trước cuộc họp của chúng ta.",
        1221: "Lớp kỹ thuật sẽ giải bài toán thiết kế cầu bằng mô hình máy tính.",
        1679: "Kết quả khảo sát sinh viên năm nhất hơi khác với dự đoán của giáo sư.",
        1884: "Giáo sư tâm lý học thảo luận về cách âm nhạc có thể ảnh hưởng đến tâm hồn con người.",
        2050: "Môn đại cương năm nhất cung cấp cho sinh viên nền tảng vững chắc về chính phủ Hoa Kỳ.",
        2162: "Sinh viên hét lên khi chuông báo cháy ở ký túc xá làm gián đoạn bài thi của cô ấy.",
        2336: "Giáo sư tâm lý học nhận xét rằng sinh viên năm nhất có thể trở nên phụ thuộc vào sự chấp nhận của bạn đồng trang lứa khi thích nghi với môi trường đại học xa lạ.",
        2399: "Trong tâm lý học phát triển, các nghiên cứu về cặp song sinh cùng trứng thường phù hợp với những phát hiện từ các nghiên cứu nhận con nuôi, cho thấy ảnh hưởng di truyền chung.",
        2448: "Trong bài giảng xã hội học, giáo sư giải thích rằng lệnh giới nghiêm trong khuôn viên trường có thể hạn chế tự do của sinh viên, đồng thời cải thiện an toàn vào ban đêm.",
        2497: "Góc nhìn xã hội học giải thích vì sao sinh viên đại học thường kết bạn với bạn cùng lớp có hoàn cảnh tương đồng.",
        2686: "Giáo sư tâm lý học giải thích rằng tình trạng thiếu ngủ khiến một số tình nguyện viên mất phương hướng trong một thí nghiệm định hướng không gian.",
        2724: "Giáo trình tâm lý học mô tả quá trình xã hội hóa là quá trình trẻ em học các quy tắc văn hóa.",
        2805: "Sinh viên giao lưu trong phòng sinh hoạt ký túc xá sau giờ học và kết bạn với những người đến từ các bang khác nhau.",
        2022: "Giáo trình địa chất giải thích đất hình thành như thế nào khi đá phong hóa theo thời gian.",
        3272: "Giáo sư khoa học chính trị đã sử dụng bằng chứng so sánh từ nguồn quỹ ứng phó thảm họa để chứng minh chủ nghĩa liên bang phân bổ thẩm quyền giữa các cấp chính quyền như thế nào.",
        3822: "Giáo sư kỹ thuật lập luận rằng các hệ thống điều khiển lỗi thời có thể ngừng hoạt động dưới tác động nhiệt kéo dài.",
        5400: "Văn phòng đăng ký sẽ công bố lịch thi cuối kỳ vào một thời điểm nào đó trước kỳ nghỉ xuân.",
        5651: "Trong tâm lý học phát triển, lời trấn an bằng lời nói của người chăm sóc có thể làm giảm lo âu của trẻ khi thực hiện một nhiệm vụ xa lạ.",
        6260: "Giáo sư thiên văn giải thích tại sao điểm chí đánh dấu bước chuyển mùa trên quỹ đạo Trái Đất.",
        6323: "Giáo sư đưa ra bằng chứng cho thấy một nhóm nội bộ có thể phân bổ tài nguyên khan hiếm cho các thành viên của mình rộng rãi hơn người bên ngoài.",
        3179: "Giáo sư y tế công cộng nghiên cứu cách các điều kiện kinh tế - xã hội ảnh hưởng đến việc sinh viên đại học tiếp cận dịch vụ chăm sóc y tế.",
        3190: "Chương trình học bổng hỗ trợ những sinh viên có hoàn cảnh kinh tế - xã hội khó khăn, không đủ tiền mua tài liệu môn học bắt buộc.",
        3215: "Giáo sư chứng minh rằng không thuật toán học máy nào miễn nhiễm với sai sót khi các nhà nghiên cứu kiểm tra nó bằng dữ liệu lịch sử thiên lệch.",
        3220: "Giáo sư giáo dục giải thích trẻ em được xã hội hóa như thế nào qua nề nếp lớp học và kỳ vọng của bạn bè.",
        3306: "Nghiên cứu xã hội - văn hóa cho thấy ngôn ngữ và truyền thống gia đình hình thành quan niệm của sinh viên về thành công học tập.",
        3439: "Về mặt xã hội học, giáo sư cho rằng nhà ở trong khuôn viên có thể tái tạo sự phân chia xã hội thông qua việc tiếp cận tài nguyên không bình đẳng.",
        3614: "Trong bài giảng, giáo sư hóa học xác định glucose là chất tan khi nước hòa tan nó.",
        3615: "Giáo sư so sánh từng dung môi bằng cách đo độ phân cực và tốc độ bay hơi trong phòng thí nghiệm.",
        3617: "Hội thảo nghiên cứu xem xét cách các công cụ thống kê mới làm tinh vi hơn việc phân tích dữ liệu xã hội phức tạp.",
        3858: "Hội thảo nghiên cứu so sánh tính xã hội của con người với sự hợp tác giữa các loài linh trưởng sống trong những nhóm phức tạp.",
        4185: "Giáo sư tâm lý học đưa ra bằng chứng cho thấy những câu chuyện cá nhân sinh động có thể khơi dậy sự đồng cảm ngay cả ở những sinh viên hoài nghi về thông điệp đó.",
        4555: "Trong hội thảo về tu từ chính trị, giáo sư lập luận rằng lời hứa cường điệu của ứng cử viên về việc xóa bỏ nghèo đói che khuất những giới hạn của chính sách được đề xuất.",
        4954: "Giáo sư thiên văn giải thích năng lượng mặt trời thúc đẩy sự luân chuyển khí quyển trên một số hành tinh như thế nào.",
        5018: "Giáo sư giải thích phòng thí nghiệm địa chất trong khuôn viên trường giúp sinh viên phân tích các mẫu đá thu thập từ những cánh đồng gần đó như thế nào.",
        5398: "Giáo sư nhận xét rằng nói to trong thư viện đại học không được xem là hành vi được xã hội chấp nhận.",
        5522: "Giáo sư nói rằng nguồn bằng chứng duy nhất là một bản đồ bị hư hỏng trong kho lưu trữ của trường đại học.",
        5650: "Môn xã hội học của tôi sử dụng các cuộc khảo sát trong khuôn viên để xem sinh viên năm nhất thích nghi với đời sống đại học ra sao.",
        5777: "Trợ lý phòng thí nghiệm chỉ cho tôi ổ cắm nào có thể cấp điện an toàn cho kính hiển vi.",
        6007: "Học bổng được trao chỉ dựa trên thành tích học tập do văn phòng đăng ký ghi nhận.",
        6120: "Giáo sư tâm lý học xã hội lập luận rằng người hướng ngoại có thể thể hiện tính hòa đồng vì tương tác xã hội mang lại sự củng cố, chứ không chỉ vì mong muốn bẩm sinh được ở bên người khác.",
        1246: "Nhà ăn giảm lãng phí thực phẩm bằng cách tặng các suất ăn chưa dùng cho một nơi trú ẩn.",
        3311: "Nghiên cứu theo chiều dọc này theo dõi cùng một nhóm sinh viên năm nhất trong bốn năm để đo mức thay đổi về căng thẳng.",
        3474: "Giáo sư điều dưỡng mời một điều dưỡng viên gia đình thảo luận về nghề chăm sóc bệnh nhân.",
        3484: "Giáo sư trình bày bằng chứng sơ bộ cho thấy chương trình phụ đạo mới cải thiện điểm thi của sinh viên năm nhất.",
        3492: "Trong hội thảo tâm lý học, giáo sư cảnh báo rằng chủ nghĩa giản lược có thể bỏ qua các nguyên nhân xã hội của bệnh tâm thần.",
        3863: "Sinh viên tương lai nên so sánh tỷ lệ tốt nghiệp trước khi chọn một trường đại học.",
        4043: "Giáo sư nghiên cứu đô thị mô tả Đại lộ College là một đại lộ lớn nối trường đại học với các khu dân cư xung quanh.",
        4178: "Giáo sư thần kinh học phân biệt phương pháp điều trị phục hồi chức năng với thuốc chỉ làm giảm triệu chứng mà không phục hồi các đường dẫn truyền thần kinh bị tổn thương.",
        2270: "Giáo trình khoa học môi trường giải thích việc đốt nhiên liệu không tái tạo làm tăng khí CO₂ trong khí quyển như thế nào.",
        2669: "Giáo sư giải thích cách các nhà máy nhiệt điện than thải khí lưu huỳnh đioxit vào khí quyển.",
        4416: "Trong bài giảng về độc chất học, giáo sư giải thích rằng việc tiếp xúc quá nhiều với khí cacbon monoxit có thể làm cơ thể bị nhiễm độc trước khi xuất hiện triệu chứng rõ ràng.",
        6042: "Kỳ thực tập đã cung cấp cho Lena một phương pháp đã được kiểm chứng để sắp xếp ghi chú nghiên cứu.",
        5113: "Trong lịch sử, các trường đại học Mỹ tuyển ít phụ nữ hơn, nhưng mô hình ghi danh đã thay đổi trong thế kỷ hai mươi.",
        5186: "Giáo sư kỹ thuật chỉ ra cách một vòng phản hồi có thể khuếch đại sai số nhỏ.",
        5209: "Một giảng viên cố vấn đã giúp sinh viên năm hai lập kế hoạch thực tế cho kỳ thực tập kỹ thuật.",
        5304: "Trong bài giảng ngôn ngữ học, giáo sư giải thích rằng tiền tố “pre-” trong “preview” mang nghĩa “before” (trước).",
        5309: "Giáo sư tâm lý học thảo luận cách định kiến ngầm có thể ảnh hưởng đến việc đánh giá bài viết của sinh viên.",
        5318: "Trong bài giảng kinh tế, giáo sư giải thích thuế lũy tiến có thể làm giảm bất bình đẳng thu nhập như thế nào.",
        5322: "Giáo sư hóa học giải thích tại sao mọi sinh viên phải tuân theo quy trình an toàn của phòng thí nghiệm.",
        5324: "Tâm lý học nghiên cứu trí nhớ, cảm xúc và trải nghiệm xã hội ảnh hưởng đến hành vi con người như thế nào.",
        5412: "Giáo sư kỹ thuật nhận thấy cải tiến thiết kế có ý nghĩa thống kê sau khi kiểm soát chi phí vật liệu.",
        5444: "Trong phòng thí nghiệm hệ thống năng lượng, độ dày lớp cách nhiệt quyết định tốc độ một mô hình tòa nhà mất nhiệt.",
        5509: "Trong lớp luật so sánh, giáo sư giải thích rằng giấy phép trong tiếng Anh-Anh được viết là “licence”, còn trong tiếng Anh-Mỹ là “license”.",
        5545: "Bài giảng kỹ thuật môi trường xác định rằng nguyên nhân sâu xa của ngập lụt trong khuôn viên là thiết kế thoát nước kém.",
        5555: "Ngoài ra, sinh viên có thể hoàn thành khảo sát trong giờ hành chính của giáo sư.",
        6182: "Giáo sư xã hội học giải thích rằng một câu hỏi tu từ có thể thách thức người nghe mà không yêu cầu câu trả lời.",
        6277: "Giáo sư địa chất phân biệt phong hóa hóa học với phong hóa vật lý bằng mẫu khoáng vật và dữ liệu thực địa.",
        6319: "Giáo sư tâm lý học mô tả quá trình tự hiện thực hóa bản thân là việc phát huy tiềm năng sau khi các nhu cầu cơ bản được đáp ứng.",
        6380: "Bài tiểu luận hội thảo của cô ấy sử dụng hồ sơ điều tra dân số để nghiên cứu nạn phân biệt đối xử về nhà ở tại một thành phố vùng Trung Tây.",
    }
    for item_id, value in additional_vietnamese_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["vi"] = value

    additional_indonesian_example_repairs = {
        527: "Beasiswa saya akan membiayai kelas musim panas saya di sebuah perguruan tinggi komunitas.",
        964: "Saudara perempuan saya belajar di perguruan tinggi komunitas terdekat dan mengunjungi kampus pada akhir pekan.",
        1110: "Penasihat menjelaskan cara mentransfer kredit dari perguruan tinggi komunitas ke universitas.",
        1130: "Selama satu dekade terakhir, kursus daring telah mengubah cara perguruan tinggi komunitas melayani mahasiswa yang bekerja.",
        1200: "Profesor itu mengatakan bahwa biaya kuliah merupakan faktor utama yang mendorong mahasiswa memilih perguruan tinggi komunitas.",
        1463: "Departemen teknik akan beralih ke panduan digital pada semester depan untuk mengurangi biaya pencetakan.",
        845: "Di kantor administrasi akademik, Maya harus mengisi informasi kontak darurat sebelum mendaftar kelas.",
        1563: "Kebijakan perlindungan data perpustakaan mewajibkan mahasiswa menggunakan kata sandi yang aman.",
        1601: "Penasihat saya mengatakan bahwa keterampilan lunak dapat membantu saya berkomunikasi dengan rekan kerja selama magang.",
        1647: "Pemilihan sumber primer membentuk kuliah profesor sejarah kami tentang Perang Saudara.",
        1649: "Penasihat bertanya apakah kesehatan mental mahasiswa itu memengaruhi kehadirannya.",
        3474: "Profesor keperawatan mengundang seorang praktisi perawat keluarga untuk membahas karier dalam perawatan pasien.",
        1693: "Nada buku teks ekonomi itu menjadi lebih kritis dalam bab-bab berikutnya.",
        1761: "Profesor biologi mengatakan bahwa pengobatan modern telah meningkatkan kelangsungan hidup setelah banyak penyakit menular.",
        1682: "Departemen teknik memulai proyek bersama dengan perguruan tinggi komunitas di dekat kampus.",
        2054: "Gubernur mengunjungi kampus kami untuk membahas pendanaan bagi perguruan tinggi komunitas.",
        2793: "Buku teks pendidikan mengaitkan buta huruf pada orang dewasa dengan terbatasnya akses ke program perguruan tinggi komunitas.",
        2797: "Dalam mata kuliah sosiologi kami, profesor menjelaskan bahwa terbatasnya akses terhadap penitipan anak dapat meningkatkan angka putus kuliah di kalangan mahasiswa perguruan tinggi komunitas.",
        2918: "Kalkulus memberi mahasiswa teknik cara untuk menjelaskan bagaimana gaya yang berubah memengaruhi benda bergerak.",
        3219: "Dalam seminar sosiologi kami, demograf membandingkan data survei longitudinal dengan catatan sensus untuk menjelaskan pola pendaftaran yang berubah di universitas-universitas regional.",
        3311: "Studi longitudinal itu mengikuti mahasiswa baru yang sama selama empat tahun untuk mengukur perubahan stres.",
        3515: "Seminar penelitian membela analisis kuantitatif sebagai metode untuk memperkirakan efek kausal dari data longitudinal.",
        3868: "Buku teks ilmu politik menganalisis cara badan legislatif negara bagian menyeimbangkan tuntutan yang bersaing atas pendanaan perguruan tinggi negeri.",
        4459: "Yayasan filantropis universitas itu mendanai penelitian tentang kerawanan pangan di kalangan mahasiswa perguruan tinggi komunitas.",
        4456: "Tidak gentar oleh eksperimen yang gagal, mahasiswa teknik itu merevisi desainnya dan mempresentasikan hasil yang meyakinkan di seminar penelitian.",
        4457: "Profesor kajian film itu berpendapat bahwa latar pedesaan membentuk suasana tenang dalam film dokumenter tersebut.",
        4553: "Dalam kuliah fisika, tolakan elektrostatik mendorong kedua bola bermuatan menjauh.",
        4560: "Profesor memperingatkan bahwa plagiarisme dalam makalah penelitian dapat menyebabkan mahasiswa diskors dari universitas.",
        4670: "Pemulihan keuangan universitas memungkinkan pembukaan kembali beberapa mata kuliah semester depan.",
        4687: "Mahasiswa musik itu berlatih di ruang latihan sebelum konser malam.",
        4834: "Selama minggu pendaftaran, saya memberi tahu penasihat akademik bahwa nenek saya akan mengunjungi kampus saat akhir pekan keluarga.",
        4906: "Anda dapat menggunakan mata kuliah di perguruan tinggi komunitas sebagai pengganti mata kuliah pilihan yang diwajibkan.",
        4926: "Kuliah sejarah dunia membahas bagaimana Kesultanan Utsmaniyah memengaruhi perdagangan di tiga benua.",
        4967: "Keinginan kafetaria untuk menyajikan resep baru menghasilkan malam kuliner internasional yang populer.",
        5113: "Secara historis, perguruan tinggi Amerika menerima lebih sedikit perempuan, tetapi pola pendaftaran berubah selama abad kedua puluh.",
        5186: "Profesor teknik menunjukkan bagaimana putaran umpan balik dapat memperbesar kesalahan kecil.",
        5209: "Seorang dosen pembimbing membantu mahasiswa tahun kedua itu menyusun rencana realistis untuk magang tekniknya.",
        5245: "Tujuan mulia dari pantri makanan kampus adalah membantu mahasiswa yang tidak mampu membeli makanan secara teratur.",
        5247: "Buku teks antropologi menggambarkan pemberian hadiah sebagai norma yang memperkuat hubungan dalam banyak komunitas.",
        5309: "Profesor psikologi membahas bagaimana prasangka implisit dapat memengaruhi penilaian tulisan mahasiswa.",
        5318: "Dalam kuliah ekonomi, profesor menjelaskan bagaimana perpajakan progresif dapat mengurangi ketimpangan pendapatan.",
        5322: "Profesor kimia menjelaskan mengapa setiap mahasiswa harus mengikuti protokol keselamatan laboratorium.",
        5324: "Psikologi mengkaji bagaimana ingatan, emosi, dan pengalaman sosial memengaruhi perilaku manusia.",
        5412: "Profesor teknik menemukan bahwa perbaikan desain itu signifikan secara statistik setelah mengendalikan biaya material.",
        5444: "Di laboratorium sistem energi, ketebalan isolasi menentukan seberapa cepat model bangunan kehilangan panas.",
        5457: "Terjemahan dalam buku teks sejarah kami mempertahankan makna asli perjanjian tersebut.",
        5460: "Kuliah fakultas kedokteran mengkaji bagaimana obat imunosupresif meningkatkan tingkat keberhasilan transplantasi.",
        5545: "Kuliah teknik lingkungan mengidentifikasi bahwa penyebab mendasar banjir kampus adalah desain drainase yang buruk.",
        5551: "Pengawas universitas memaparkan bukti untuk memperluas pendanaan publik bagi perguruan tinggi komunitas.",
        5554: "Penguatan layanan karier universitas membantu mahasiswa menemukan magang musim panas.",
        5555: "Sebagai alternatif, mahasiswa dapat menyelesaikan survei selama jam kerja dosen.",
        5750: "Publisitas museum itu menarik mahasiswa, tetapi data kehadiran menunjukkan sedikit perubahan dalam jumlah pendaftar.",
        5780: "Langganan perpustakaan kami memberi akses ke ribuan jurnal akademik.",
        5862: "Relokasi departemen itu memerlukan metode yang cermat untuk menjaga sampel laboratorium selama pemindahan.",
        5880: "Kemenangan tim teknik itu terjadi ketika desain jembatan mereka lulus uji keselamatan profesor.",
        5891: "Pemetaan gen modern menggabungkan model statistik dengan data sekuensing untuk menemukan varian yang terkait dengan kelainan bawaan.",
        5901: "Profesor menjelaskan peninjauan yudisial sebagai kewenangan tertinggi Mahkamah Agung atas sengketa konstitusional.",
        5902: "Bimbingan psikologi kami membantu mahasiswa memahami memori melalui eksperimen sederhana di kelas.",
        5909: "Silabus yang direvisi mencantumkan tanggal ujian tengah semester baru untuk mata kuliah biologi mahasiswa baru.",
        5910: "Penghapusan buku-buku usang memberi perpustakaan lebih banyak ruang untuk bahan kuliah terbaru.",
        5948: "Penghuni asrama melaporkan pemanas yang rusak kepada kantor perumahan sebelum ujian tengah semester.",
        5952: "Perekrutan asisten laboratorium di departemen biologi dimulai setelah mahasiswa menyelesaikan kimia pengantar.",
        6045: "Profesor itu berpendapat bahwa warisan perguruan tinggi komunitas tersebut mencakup pembukaan pendidikan tinggi bagi orang dewasa yang bekerja.",
        5277: "Dalam kuliah sosiologi, profesor menjelaskan bahwa perguruan tinggi komunitas merupakan jalur praktis menuju gelar sarjana bagi banyak mahasiswa.",
        6182: "Profesor sosiologi menjelaskan bahwa pertanyaan retoris dapat menantang audiens tanpa meminta jawaban.",
        6194: "Karena praktikum biologi dibatalkan, pengajar menjadwalkan sesi pengganti sebelum ujian tengah semester.",
        6219: "Mesin fotokopi departemen teknik macet sebelum profesor dapat menyalin petunjuk laboratorium.",
        6223: "Ruang santai departemen memberi mahasiswa tempat yang tenang untuk membandingkan catatan setelah kuliah.",
        6277: "Profesor geologi membedakan pelapukan kimia dari pelapukan fisik menggunakan sampel mineral dan data lapangan.",
        2281: "Perusahaan teknologi itu setuju untuk mensponsori hackathon ilmu komputer kami.",
        2759: "Sejarawan itu menemukan minat publik yang berkelanjutan terhadap arsip tersebut sepanjang semester.",
        2951: "Profesor sosiologi menjelaskan bagaimana penutupan kampus perguruan tinggi komunitas memengaruhi keluarga di sekitarnya.",
        3531: "Negara bagian membantu mensubsidi uang kuliah perguruan tinggi komunitas bagi mahasiswa dari keluarga berpenghasilan rendah.",
        4109: "Dalam seminar kebijakan pendidikan, profesor berpendapat bahwa kuliah gratis di perguruan tinggi komunitas dapat menjadi penyetara dengan mempersempit kesenjangan sosial ekonomi dalam pencapaian gelar.",
        4316: "Repositori digital universitas menyimpan data dari penelitian iklim selama puluhan tahun.",
        4791: "Di kios kafetaria, pilih menu untuk membayar makan siang dengan saldo kampus.",
        5623: "Sebelum janji temu pagi saya di kantor administrasi akademik, alarm kebakaran di asrama mengganggu tidur saya.",
        3863: "Calon mahasiswa sebaiknya membandingkan tingkat kelulusan sebelum memilih universitas.",
        6042: "Magang itu memberi Lena metode yang telah teruji untuk mengatur catatan penelitiannya.",
        6319: "Profesor psikologi menggambarkan aktualisasi diri sebagai perwujudan potensi diri setelah kebutuhan dasar terpenuhi.",
        6380: "Makalah seminarnya menggunakan catatan sensus untuk meneliti diskriminasi perumahan di sebuah kota di Midwest.",
    }
    for item_id, value in additional_indonesian_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["id"] = value

    # "Kantor registrar" is understandable in Indonesian but is an
    # untranslated institutional label repeated throughout the generated
    # examples.  Use the natural local description in sentence contexts.
    for entry in translations.values():
        example = entry.get("example", {})
        if isinstance(example, dict) and "id" in example:
            example["id"] = re.sub(
                r"\bkantor registrar\b",
                "kantor administrasi akademik",
                str(example["id"]),
                flags=re.IGNORECASE,
            )
    translations["builtin:6060"]["collocations"]["id"] = (
        "biro administrasi akademik universitas, kantor administrasi akademik, "
        "menghubungi bagian administrasi akademik, arsip administrasi akademik, administrator akademik"
    )

    japanese_example_repairs = {
        147: "化学の授業に遅刻したので、私はドアの近くに静かに座った。",
        192: "学生センターは無料の個別指導プログラムを運営している。",
        345: "春休みの間は寮に滞在する予定だ。",
        381: "私の社会科の授業は毎週火曜日に図書館で行われる。",
        503: "ルームメートは春休みに実家へ帰省する予定だ。",
        537: "1年生向けの授業では、複数の国の国家的な教育政策を比較した。",
        776: "交渉が失敗すれば、何人かの大学院生労働者がストライキをするかもしれない。",
        890: "化学の教授は、混合物を2つの透明な液体に分離するよう私たちに求めた。",
        1088: "学務課は、履修単位数に比例して各学生の授業料を比較する。",
        1210: "キャンパスシャトルは寮と図書館の間で学生を輸送するのに役立つ。",
        1246: "学食は、余った食事を避難所に寄付することで食品廃棄物を減らした。",
        1561: "経済学の教授は、授業料の上昇が新入生の登録者数の減少を予測するかもしれないと言っている。",
        1703: "教授は、必要な対照群を欠く実験レポートを却下することがある。",
        1777: "アドバイザーは、学期が始まる前に登録の問題を解決するのを手伝ってくれた。",
        1786: "インターンシップのアドバイザーは、学生たちにキャンパスの締切前に応募するよう促した。",
        1935: "歴史学の教授は学生たちに、大学の文書館にある手紙を保存するよう求めた。",
        1962: "ルームメートは春休みに大学のフードパントリーで奉仕する予定だ。",
        2087: "その工学会社は私たちの卒業設計授業からインターンを2人採用する予定だ。",
        2148: "教授は明日の招待講演を大学図書館のウェブサイトで配信する。",
        2281: "そのテクノロジー企業は私たちのコンピューターサイエンス・ハッカソンを後援することに同意した。",
        2334: "工学の教授は、新入生の履修登録を効率化するために登録フォームを設計し直した。",
        2566: "歴史の講義で、教授は大学学長がなぜ辞任することを選んだのか説明した。",
        2584: "教授は生物学の講義で、ホルモンが血糖値を調節する仕組みを説明した。",
        2591: "教授は、修復された壁画を、変化する地域のアイデンティティーについての象徴的な表現だと述べた。",
        3335: "言語学の教授は、著者資格をめぐる対立の後、2つの研究チームの間を調停する。",
        3594: "音楽史家は、その旋律構造がアフリカ系アメリカ人のゴスペルの伝統を反映していると論じた。",
        3625: "教授は、標準化試験が主流の規範と異なる教育背景を持つ志願者を周縁化する可能性を示した。",
        4526: "教授は、ドキュメンタリーが構造的原因を無視して貧困を美化することがあると警告した。",
        4719: "図書館で勉強している間、スマートフォンを確認したい気持ちに抵抗するようにしている。",
        5346: "アドバイザーは、毎週の小テストが生物学入門で学んだ語彙を強化すると言った。",
        5356: "その技術者は、壊れた研究室のコンピューターから削除されたファイルを復元する方法を見せてくれた。",
        5437: "インターンシップの高い給料は、その職が有益な訓練を提供するかどうかを学生が無視するよう誘惑するかもしれない。",
        5503: "講義では、アパートの家賃が上昇しているにもかかわらず、多くの学生が大学の近くに居住する理由を検討した。",
        5521: "シラバスでは、持ち帰り形式の中間試験中に学生が生成ソフトウェアを使うことを禁じている。",
        5366: "その学生は布を使って実験台からインクをこすり落とした。",
        5881: "キャンパスの医師は、学生が溶連菌性咽頭炎の検査で陽性になった後、抗生物質を処方した。",
    }
    for item_id, value in japanese_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["ja"] = value

    chinese_example_repairs = {
        238: "这位年轻教授给我上地质学入门课。",
        415: "宿舍规定静音时间从晚上十点开始。",
        537: "大一课程比较了几个国家的教育政策。",
        6315: "心理学教授教了一个帮助记忆形成阶段的助记法。",
    }
    for item_id, value in chinese_example_repairs.items():
        translations[f"builtin:{item_id}"]["example"]["zh"] = value

    translations["builtin:2549"]["collocations"]["ja"] = "その結果、そしてその結果、その結果圧力が下がる、その結果が変わる、その結果研究は仮説を支持する"
    translations["builtin:3949"]["collocations"]["zh"] = "就读神学院，神学培训机构，神学院培训，进入神学院，神学院教育"

    # Clear untranslated English fragments in non-Latin collocation strings.
    for item_id, values in {
        6092: {"ja": "洗濯室、洗濯をする、洗濯設備、洗濯用洗剤", "zh": "洗衣房，洗衣服，洗衣设施，洗衣用洗涤剂"},
        6292: {"ja": "石碑、記念建築、国定記念物、記念碑", "zh": "石碑，纪念性建筑，国家纪念物，纪念碑"},
    }.items():
        for language, value in values.items():
            translations[f"builtin:{item_id}"]["collocations"][language] = value

    # Keep the repository's one-space JSON indentation to avoid a formatting-only diff.
    VOCAB_PATH.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    PHRASE_PATH.write_text(json.dumps(phrase_root, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"repaired vocabulary entries: {len(example_repairs) + 7}")
    print("repaired phrase collocation records: 13")


if __name__ == "__main__":
    main()
