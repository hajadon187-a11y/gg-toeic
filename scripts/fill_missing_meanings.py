#!/usr/bin/env python3
"""Fill the localized meanings missing from the latest TOEIC business entries."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"

LANGUAGE_FIELDS = (
    "meaningZh", "meaningHi", "meaningVi", "meaningKo",
    "meaningId", "meaningTh", "meaningEs",
)


TRANSLATIONS = {
    "attendee": {
        "meaningZh": "参加活动或会议的人",
        "meaningHi": "किसी कार्यक्रम या बैठक में शामिल होने वाला व्यक्ति",
        "meaningVi": "người tham dự một sự kiện hoặc cuộc họp",
        "meaningKo": "행사나 회의에 참석하는 사람",
        "meaningId": "orang yang menghadiri acara atau rapat",
        "meaningTh": "ผู้เข้าร่วมงานหรือการประชุม",
        "meaningEs": "persona que asiste a un evento o una reunión",
    },
    "contributor": {
        "meaningZh": "为工作或想法作出贡献的人",
        "meaningHi": "काम या विचारों में योगदान देने वाला व्यक्ति",
        "meaningVi": "người đóng góp công sức hoặc ý tưởng",
        "meaningKo": "일이나 아이디어에 기여하는 사람",
        "meaningId": "orang yang menyumbangkan karya atau ide",
        "meaningTh": "ผู้มีส่วนร่วมในการเสนอผลงานหรือความคิด",
        "meaningEs": "persona que aporta trabajo o ideas",
    },
    "minutes": {
        "meaningZh": "会议讨论内容的书面记录",
        "meaningHi": "बैठक में हुई चर्चा का लिखित रिकॉर्ड",
        "meaningVi": "biên bản ghi lại những nội dung đã được thảo luận trong cuộc họp",
        "meaningKo": "회의에서 논의된 내용을 기록한 문서",
        "meaningId": "catatan tertulis tentang hal-hal yang dibahas dalam rapat",
        "meaningTh": "บันทึกเป็นลายลักษณ์อักษรเกี่ยวกับสิ่งที่หารือกันในการประชุม",
        "meaningEs": "acta escrita de lo tratado en una reunión",
    },
    "headquarters": {
        "meaningZh": "组织的总部",
        "meaningHi": "किसी संगठन का मुख्यालय",
        "meaningVi": "trụ sở chính của một tổ chức",
        "meaningKo": "조직의 본사",
        "meaningId": "kantor pusat suatu organisasi",
        "meaningTh": "สำนักงานใหญ่ขององค์กร",
        "meaningEs": "sede central de una organización",
    },
    "supervisor": {
        "meaningZh": "负责监督员工的人；主管",
        "meaningHi": "कर्मचारियों की निगरानी करने वाला व्यक्ति",
        "meaningVi": "người giám sát nhân viên",
        "meaningKo": "직원을 감독하는 사람; 관리자",
        "meaningId": "orang yang mengawasi karyawan",
        "meaningTh": "ผู้ควบคุมดูแลพนักงาน",
        "meaningEs": "persona que supervisa a los trabajadores",
    },
    "resignation": {
        "meaningZh": "正式辞职声明",
        "meaningHi": "नौकरी छोड़ने की औपचारिक सूचना",
        "meaningVi": "tuyên bố chính thức về việc nghỉ việc",
        "meaningKo": "퇴직 의사를 공식적으로 밝히는 것",
        "meaningId": "pernyataan resmi bahwa seseorang berhenti dari pekerjaannya",
        "meaningTh": "การแจ้งลาออกอย่างเป็นทางการ",
        "meaningEs": "declaración formal de que alguien deja su empleo",
    },
    "payroll": {
        "meaningZh": "员工及其工资的名单；工资表",
        "meaningHi": "कर्मचारियों और उन्हें दिए जाने वाले वेतन की सूची",
        "meaningVi": "danh sách nhân viên và tiền lương trả cho họ",
        "meaningKo": "직원 목록과 지급되는 급여 내역; 급여 대장",
        "meaningId": "daftar karyawan dan gaji yang dibayarkan kepada mereka",
        "meaningTh": "รายชื่อพนักงานและเงินเดือนที่จ่ายให้",
        "meaningEs": "lista de empleados y salarios que se les pagan; nómina",
    },
    "vacancy": {
        "meaningZh": "空缺的工作或职位",
        "meaningHi": "खाली नौकरी या पद",
        "meaningVi": "vị trí hoặc chỗ làm còn trống",
        "meaningKo": "비어 있는 일자리나 직책",
        "meaningId": "lowongan pekerjaan atau jabatan yang belum terisi",
        "meaningTh": "ตำแหน่งงานที่ว่าง",
        "meaningEs": "puesto de trabajo vacante",
    },
    "workload": {
        "meaningZh": "分配给个人或团队的工作量",
        "meaningHi": "किसी व्यक्ति या टीम को सौंपे गए काम की मात्रा",
        "meaningVi": "khối lượng công việc được giao cho một người hoặc một nhóm",
        "meaningKo": "개인이나 팀에 배정된 업무량",
        "meaningId": "jumlah pekerjaan yang diberikan kepada seseorang atau tim",
        "meaningTh": "ปริมาณงานที่มอบหมายให้บุคคลหรือทีม",
        "meaningEs": "cantidad de trabajo asignada a una persona o un equipo",
    },
    "receipt": {
        "meaningZh": "确认付款的书面凭证；收据",
        "meaningHi": "भुगतान की पुष्टि करने वाला लिखित रिकॉर्ड",
        "meaningVi": "biên lai xác nhận việc thanh toán",
        "meaningKo": "결제를 확인하는 서면 기록; 영수증",
        "meaningId": "bukti tertulis yang mengonfirmasi pembayaran",
        "meaningTh": "หลักฐานเป็นลายลักษณ์อักษรยืนยันการชำระเงิน",
        "meaningEs": "comprobante escrito que confirma un pago",
    },
    "refund": {
        "meaningZh": "退还给顾客的钱；退款",
        "meaningHi": "ग्राहक को लौटाया गया पैसा",
        "meaningVi": "khoản tiền trả lại cho khách hàng",
        "meaningKo": "고객에게 돌려주는 돈; 환불금",
        "meaningId": "uang yang dikembalikan kepada pelanggan",
        "meaningTh": "เงินที่คืนให้ลูกค้า",
        "meaningEs": "dinero que se devuelve a un cliente; reembolso",
    },
    "cash flow": {
        "meaningZh": "企业资金的流入和流出；现金流",
        "meaningHi": "व्यवसाय में आने और बाहर जाने वाले धन का प्रवाह",
        "meaningVi": "dòng tiền vào và ra của một doanh nghiệp",
        "meaningKo": "기업으로 들어오고 나가는 자금의 흐름; 현금 흐름",
        "meaningId": "arus uang yang masuk dan keluar dari bisnis",
        "meaningTh": "การไหลเข้าและออกของเงินในธุรกิจ",
        "meaningEs": "flujo de dinero que entra y sale de una empresa",
    },
    "vendor": {
        "meaningZh": "销售商品或服务的个人或公司；供应商",
        "meaningHi": "वस्तुएँ या सेवाएँ बेचने वाला व्यक्ति या कंपनी",
        "meaningVi": "cá nhân hoặc công ty bán hàng hóa hoặc dịch vụ",
        "meaningKo": "상품이나 서비스를 판매하는 개인 또는 회사; 판매업체",
        "meaningId": "orang atau perusahaan yang menjual barang atau jasa",
        "meaningTh": "บุคคลหรือบริษัทที่ขายสินค้าและบริการ",
        "meaningEs": "persona o empresa que vende bienes o servicios; proveedor",
    },
    "shipment": {
        "meaningZh": "从一个地方运往另一个地方的货物；货运",
        "meaningHi": "एक स्थान से दूसरे स्थान भेजा गया माल",
        "meaningVi": "hàng hóa được gửi từ nơi này đến nơi khác",
        "meaningKo": "한 곳에서 다른 곳으로 보내는 물품; 화물",
        "meaningId": "barang yang dikirim dari satu tempat ke tempat lain",
        "meaningTh": "สินค้าที่ส่งจากที่หนึ่งไปยังอีกที่หนึ่ง",
        "meaningEs": "mercancías enviadas de un lugar a otro",
    },
    "warehouse": {
        "meaningZh": "存放货物的建筑物；仓库",
        "meaningHi": "माल रखने की इमारत; गोदाम",
        "meaningVi": "tòa nhà nơi lưu trữ hàng hóa; nhà kho",
        "meaningKo": "물품을 보관하는 건물; 창고",
        "meaningId": "bangunan tempat barang disimpan; gudang",
        "meaningTh": "อาคารที่ใช้เก็บสินค้า; คลังสินค้า",
        "meaningEs": "edificio donde se almacenan mercancías; almacén",
    },
    "itinerary": {
        "meaningZh": "列出旅行详细安排的计划；行程表",
        "meaningHi": "यात्रा के विवरण वाली योजना; यात्रा कार्यक्रम",
        "meaningVi": "kế hoạch nêu chi tiết chuyến đi; lịch trình",
        "meaningKo": "여행 세부 일정이 적힌 계획; 여행 일정표",
        "meaningId": "rencana yang memuat rincian perjalanan; rencana perjalanan",
        "meaningTh": "แผนการเดินทางที่แสดงรายละเอียดต่าง ๆ",
        "meaningEs": "plan con los detalles de un viaje; itinerario",
    },
    "departure": {
        "meaningZh": "离开某地；出发",
        "meaningHi": "किसी स्थान से निकलने की क्रिया; प्रस्थान",
        "meaningVi": "việc rời khỏi một nơi; khởi hành",
        "meaningKo": "어떤 장소를 떠나는 일; 출발",
        "meaningId": "tindakan meninggalkan suatu tempat; keberangkatan",
        "meaningTh": "การออกจากสถานที่หนึ่ง; การออกเดินทาง",
        "meaningEs": "acción de salir de un lugar; salida",
    },
    "hardware": {
        "meaningZh": "计算机或设备的实体部件；硬件",
        "meaningHi": "कंप्यूटर या उपकरण के भौतिक भाग; हार्डवेयर",
        "meaningVi": "các bộ phận vật lý của máy tính hoặc thiết bị; phần cứng",
        "meaningKo": "컴퓨터나 기기의 물리적 부품; 하드웨어",
        "meaningId": "bagian fisik komputer atau perangkat; perangkat keras",
        "meaningTh": "ชิ้นส่วนทางกายภาพของคอมพิวเตอร์หรืออุปกรณ์; ฮาร์ดแวร์",
        "meaningEs": "componentes físicos de un ordenador o dispositivo; hardware",
    },
    "notify": {
        "meaningZh": "正式告知某人某事；通知",
        "meaningHi": "किसी को किसी बात की औपचारिक सूचना देना",
        "meaningVi": "chính thức thông báo cho ai về điều gì",
        "meaningKo": "누군가에게 어떤 사실을 공식적으로 알리다; 통지하다",
        "meaningId": "memberi tahu seseorang secara resmi tentang sesuatu",
        "meaningTh": "แจ้งให้ใครทราบอย่างเป็นทางการเกี่ยวกับบางเรื่อง",
        "meaningEs": "informar oficialmente a alguien de algo; notificar",
    },
    "postpone": {
        "meaningZh": "将活动推迟到更晚的时间；延期",
        "meaningHi": "किसी कार्यक्रम को बाद के समय तक टालना",
        "meaningVi": "trì hoãn một sự kiện đến thời điểm muộn hơn",
        "meaningKo": "행사를 나중으로 미루다; 연기하다",
        "meaningId": "menunda suatu acara hingga waktu yang lebih kemudian",
        "meaningTh": "เลื่อนงานหรือเหตุการณ์ไปเป็นเวลาภายหลัง",
        "meaningEs": "retrasar un evento hasta un momento posterior; posponer",
    },
    "profitable": {
        "meaningZh": "能够带来经济收益的；有利可图的",
        "meaningHi": "वित्तीय लाभ पैदा करने वाला; लाभदायक",
        "meaningVi": "tạo ra lợi nhuận tài chính; có lợi nhuận",
        "meaningKo": "재정적 이익을 내는; 수익성이 있는",
        "meaningId": "menghasilkan keuntungan finansial; menguntungkan",
        "meaningTh": "ที่สร้างผลกำไรทางการเงิน; ทำกำไร",
        "meaningEs": "que genera beneficios económicos; rentable",
    },
    "onboarding": {
        "meaningZh": "帮助新员工熟悉组织的入职流程",
        "meaningHi": "नए कर्मचारी को संगठन से परिचित कराने की प्रक्रिया",
        "meaningVi": "quy trình giúp nhân viên mới làm quen với tổ chức",
        "meaningKo": "신입 직원이 조직에 적응하도록 돕는 온보딩 과정",
        "meaningId": "proses memperkenalkan karyawan baru kepada organisasi",
        "meaningTh": "กระบวนการแนะนำพนักงานใหม่ให้รู้จักองค์กร",
        "meaningEs": "proceso de incorporación de nuevos empleados a una organización",
    },
    "deliverable": {
        "meaningZh": "必须提交或交付的产品或成果；交付物",
        "meaningHi": "प्रस्तुत या सौंपा जाने वाला उत्पाद या परिणाम",
        "meaningVi": "sản phẩm hoặc kết quả phải được bàn giao",
        "meaningKo": "제출하거나 납품해야 하는 제품 또는 결과물; 납품물",
        "meaningId": "produk atau hasil yang harus diserahkan",
        "meaningTh": "ผลงานหรือผลลัพธ์ที่ต้องส่งมอบ",
        "meaningEs": "producto o resultado que debe entregarse; entregable",
    },
    "turnover": {
        "meaningZh": "员工流动率或营业额",
        "meaningHi": "कर्मचारियों के बदलने की दर या कारोबार की मात्रा",
        "meaningVi": "tỷ lệ luân chuyển nhân viên hoặc doanh thu",
        "meaningKo": "직원 이직률 또는 매출액",
        "meaningId": "tingkat pergantian karyawan atau omzet",
        "meaningTh": "อัตราการหมุนเวียนของพนักงานหรือยอดขาย",
        "meaningEs": "tasa de rotación de empleados o volumen de ventas",
    },
    "outsourcing": {
        "meaningZh": "付费请另一家公司完成工作的做法；外包",
        "meaningHi": "काम कराने के लिए किसी दूसरी कंपनी को भुगतान करने की प्रथा",
        "meaningVi": "việc thuê một công ty khác thực hiện công việc; thuê ngoài",
        "meaningKo": "다른 회사에 업무를 맡기고 비용을 지불하는 방식; 아웃소싱",
        "meaningId": "praktik membayar perusahaan lain untuk melakukan pekerjaan; alih daya",
        "meaningTh": "การจ้างบริษัทอื่นให้ทำงานแทน; การจ้างเหมาภายนอก",
        "meaningEs": "práctica de pagar a otra empresa para que realice un trabajo; externalización",
    },
    "retailer": {
        "meaningZh": "向消费者销售商品的企业；零售商",
        "meaningHi": "उपभोक्ताओं को सामान बेचने वाला व्यवसाय; खुदरा विक्रेता",
        "meaningVi": "doanh nghiệp bán hàng cho người tiêu dùng; nhà bán lẻ",
        "meaningKo": "소비자에게 상품을 판매하는 사업체; 소매업체",
        "meaningId": "bisnis yang menjual barang kepada konsumen; pengecer",
        "meaningTh": "ธุรกิจที่ขายสินค้าให้ผู้บริโภค; ผู้ค้าปลีก",
        "meaningEs": "empresa que vende bienes a los consumidores; minorista",
    },
    "distributor": {
        "meaningZh": "向销售商供应商品的企业；分销商",
        "meaningHi": "विक्रेताओं को सामान उपलब्ध कराने वाला व्यवसाय; वितरक",
        "meaningVi": "doanh nghiệp cung cấp hàng hóa cho người bán; nhà phân phối",
        "meaningKo": "판매자에게 상품을 공급하는 사업체; 유통업체",
        "meaningId": "bisnis yang memasok barang kepada penjual; distributor",
        "meaningTh": "ธุรกิจที่จัดหาสินค้าให้ผู้ขาย; ผู้จัดจำหน่าย",
        "meaningEs": "empresa que suministra bienes a los vendedores; distribuidor",
    },
    "consignment": {
        "meaningZh": "为销售或交付而寄送的货物；寄售货物",
        "meaningHi": "बिक्री या डिलीवरी के लिए भेजा गया माल",
        "meaningVi": "hàng hóa được gửi đi để bán hoặc giao; hàng ký gửi",
        "meaningKo": "판매나 배송을 위해 보내는 물품; 위탁 상품",
        "meaningId": "barang titipan yang dikirim untuk dijual atau diserahkan",
        "meaningTh": "สินค้าที่ส่งไปเพื่อขายหรือจัดส่ง; สินค้าฝากขาย",
        "meaningEs": "mercancías enviadas para su venta o entrega; envío en consignación",
    },
    "customs": {
        "meaningZh": "控制入境货物的政府部门；海关",
        "meaningHi": "देश में प्रवेश करने वाले माल को नियंत्रित करने वाला सरकारी विभाग; सीमा शुल्क विभाग",
        "meaningVi": "cơ quan hải quan kiểm soát hàng hóa nhập vào một quốc gia",
        "meaningKo": "국경을 통과하는 물품을 관리하는 정부 기관; 세관",
        "meaningId": "departemen pemerintah yang mengawasi barang yang masuk ke suatu negara; bea cukai",
        "meaningTh": "หน่วยงานของรัฐที่ควบคุมสินค้าที่นำเข้าประเทศ; ศุลกากร",
        "meaningEs": "departamento gubernamental que controla las mercancías que entran en un país; aduanas",
    },
    "forecasting": {
        "meaningZh": "预测未来结果的过程；预测",
        "meaningHi": "भविष्य के परिणामों का पूर्वानुमान लगाने की प्रक्रिया",
        "meaningVi": "quy trình dự đoán các kết quả trong tương lai; dự báo",
        "meaningKo": "미래 결과를 예측하는 과정; 예측",
        "meaningId": "proses memprediksi hasil di masa depan; peramalan",
        "meaningTh": "กระบวนการคาดการณ์ผลลัพธ์ในอนาคต",
        "meaningEs": "proceso de prever resultados futuros; previsión",
    },
    "quarterly": {
        "meaningZh": "每三个月发生一次的；季度的",
        "meaningHi": "हर तीन महीने होने वाला; त्रैमासिक",
        "meaningVi": "diễn ra mỗi ba tháng; hàng quý",
        "meaningKo": "3개월마다 발생하는; 분기별",
        "meaningId": "yang berlangsung setiap tiga bulan; triwulanan",
        "meaningTh": "ที่เกิดขึ้นทุกสามเดือน; รายไตรมาส",
        "meaningEs": "que ocurre cada tres meses; trimestral",
    },
    "optional": {
        "meaningZh": "可以选择但不是必需的；可选的",
        "meaningHi": "वैकल्पिक और अनिवार्य नहीं",
        "meaningVi": "có thể chọn nhưng không bắt buộc",
        "meaningKo": "선택할 수 있지만 필수는 아닌; 선택 사항인",
        "meaningId": "dapat dipilih tetapi tidak wajib; opsional",
        "meaningTh": "มีให้เลือกแต่ไม่จำเป็นต้องทำ; เป็นทางเลือก",
        "meaningEs": "disponible pero no obligatorio; opcional",
    },
    "delegate": {
        "meaningZh": "将任务或责任交给他人；委派",
        "meaningHi": "किसी अन्य व्यक्ति को कार्य या जिम्मेदारी सौंपना",
        "meaningVi": "giao nhiệm vụ hoặc trách nhiệm cho người khác",
        "meaningKo": "다른 사람에게 업무나 책임을 맡기다; 위임하다",
        "meaningId": "memberikan tugas atau tanggung jawab kepada orang lain",
        "meaningTh": "มอบหมายงานหรือความรับผิดชอบให้ผู้อื่น",
        "meaningEs": "asignar una tarea o responsabilidad a otra persona; delegar",
    },
    "incur": {
        "meaningZh": "招致或承担费用或义务",
        "meaningHi": "किसी खर्च या दायित्व को वहन करना",
        "meaningVi": "phát sinh hoặc phải chịu một khoản chi phí hay nghĩa vụ",
        "meaningKo": "비용이나 의무를 부담하다",
        "meaningId": "menanggung biaya atau kewajiban",
        "meaningTh": "ก่อให้เกิดหรือต้องรับภาระค่าใช้จ่ายหรือข้อผูกพัน",
        "meaningEs": "incurrir en un costo o una obligación",
    },
    "verify": {
        "meaningZh": "检查某事是否真实或准确；核实",
        "meaningHi": "यह जाँचना कि कोई बात सही या सटीक है",
        "meaningVi": "kiểm tra xem điều gì đó có đúng hoặc chính xác hay không",
        "meaningKo": "무언가가 사실이거나 정확한지 확인하다; 검증하다",
        "meaningId": "memeriksa apakah sesuatu benar atau akurat; memverifikasi",
        "meaningTh": "ตรวจสอบว่าสิ่งใดเป็นจริงหรือถูกต้อง",
        "meaningEs": "comprobar que algo es verdadero o exacto; verificar",
    },
}


def main() -> None:
    items = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    changed = 0
    for item in items:
        translations = TRANSLATIONS.get(str(item.get("word", "")).lower())
        if not translations:
            continue
        for field, value in translations.items():
            if str(item.get(field, "")) != value:
                item[field] = value
                changed += 1

    missing = [
        (item["word"], field)
        for item in items
        for field in LANGUAGE_FIELDS
        if not str(item.get(field, "")).strip()
        and item["word"] in TRANSLATIONS
    ]
    assert not missing, missing
    VOCAB_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"filled localized meanings: {changed}")


if __name__ == "__main__":
    main()
