#!/usr/bin/env python3
"""Add native-style localizations for examples of the added business terms."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "app/src/main/assets/vocabulary.json"
PHRASE_PATH = ROOT / "app/src/main/assets/vocabulary_phrase_translations.json"


# These translations are intentionally short, natural sentences that preserve
# the English meaning and the workplace/TOEIC context.
EXAMPLE_TRANSLATIONS = {
    "attendee": {
        "ja": "各出席者は会議で名札を受け取った。",
        "zh": "每位与会者都在会议上领取了姓名牌。",
        "hi": "प्रत्येक प्रतिभागी को सम्मेलन में एक नाम-पट्टिका मिली।",
        "vi": "Mỗi người tham dự đều nhận được bảng tên tại hội nghị.",
        "ko": "각 참석자는 컨퍼런스에서 이름표를 받았다.",
        "id": "Setiap peserta menerima tanda nama di konferensi.",
        "th": "ผู้เข้าร่วมแต่ละคนได้รับป้ายชื่อในงานประชุม",
        "es": "Cada asistente recibió una credencial con su nombre en la conferencia.",
    },
    "contributor": {
        "ja": "各貢献者はプロジェクト報告書で評価された。",
        "zh": "每位贡献者都在项目报告中获得了认可。",
        "hi": "परियोजना रिपोर्ट में प्रत्येक योगदानकर्ता की सराहना की गई।",
        "vi": "Mỗi người đóng góp đều được ghi nhận trong báo cáo dự án.",
        "ko": "각 기여자는 프로젝트 보고서에서 공로를 인정받았다.",
        "id": "Setiap kontributor mendapat pengakuan dalam laporan proyek.",
        "th": "ผู้มีส่วนร่วมแต่ละคนได้รับการยกย่องในรายงานโครงการ",
        "es": "Cada colaborador fue reconocido en el informe del proyecto.",
    },
    "minutes": {
        "ja": "アシスタントは昼食前に会議の議事録を回覧した。",
        "zh": "助理在午餐前传阅了会议纪要。",
        "hi": "सहायक ने दोपहर के भोजन से पहले बैठक का कार्यवृत्त प्रसारित किया।",
        "vi": "Trợ lý đã gửi biên bản cuộc họp cho mọi người trước giờ ăn trưa.",
        "ko": "비서는 점심 전에 회의록을 회람했다.",
        "id": "Asisten mengedarkan notulen rapat sebelum makan siang.",
        "th": "ผู้ช่วยเวียนรายงานการประชุมก่อนรับประทานอาหารกลางวัน",
        "es": "El asistente distribuyó el acta de la reunión antes del almuerzo.",
    },
    "headquarters": {
        "ja": "会社は本社を東京に移転した。",
        "zh": "公司将总部迁至东京。",
        "hi": "कंपनी ने अपना मुख्यालय टोक्यो में स्थानांतरित कर दिया।",
        "vi": "Công ty đã chuyển trụ sở chính đến Tokyo.",
        "ko": "회사는 본사를 도쿄로 이전했다.",
        "id": "Perusahaan memindahkan kantor pusatnya ke Tokyo.",
        "th": "บริษัทได้ย้ายสำนักงานใหญ่ไปยังโตเกียว",
        "es": "La empresa trasladó su sede central a Tokio.",
    },
    "supervisor": {
        "ja": "配送スケジュールを変更する前に、上司に確認してください。",
        "zh": "更改配送时间表前，请先询问主管。",
        "hi": "डिलीवरी शेड्यूल बदलने से पहले अपने पर्यवेक्षक से पूछ लें।",
        "vi": "Hãy hỏi người giám sát trước khi thay đổi lịch giao hàng.",
        "ko": "배송 일정을 변경하기 전에 상사에게 문의하세요.",
        "id": "Tanyakan kepada supervisor Anda sebelum mengubah jadwal pengiriman.",
        "th": "โปรดสอบถามหัวหน้างานก่อนเปลี่ยนกำหนดการจัดส่ง",
        "es": "Consulte a su supervisor antes de cambiar el calendario de entregas.",
    },
    "resignation": {
        "ja": "マネージャーは従業員の退職届を受理した。",
        "zh": "经理接受了员工的辞职申请。",
        "hi": "प्रबंधक ने कर्मचारी का इस्तीफा स्वीकार कर लिया।",
        "vi": "Người quản lý đã chấp nhận đơn từ chức của nhân viên.",
        "ko": "관리자는 직원의 사직서를 수리했다.",
        "id": "Manajer menerima pengunduran diri karyawan tersebut.",
        "th": "ผู้จัดการยอมรับใบลาออกของพนักงาน",
        "es": "El gerente aceptó la renuncia del empleado.",
    },
    "payroll": {
        "ja": "給与担当チームは金曜日に給与を処理した。",
        "zh": "薪资团队于周五处理了工资发放。",
        "hi": "पेरोल टीम ने शुक्रवार को कर्मचारियों के वेतन का भुगतान संसाधित किया।",
        "vi": "Bộ phận tiền lương đã xử lý việc trả lương vào thứ Sáu.",
        "ko": "급여 담당 팀은 금요일에 급여를 처리했다.",
        "id": "Tim penggajian memproses pembayaran gaji pada hari Jumat.",
        "th": "ทีมเงินเดือนดำเนินการจ่ายเงินเดือนเมื่อวันศุกร์",
        "es": "El equipo de nóminas procesó los salarios el viernes.",
    },
    "vacancy": {
        "ja": "会社はウェブサイトに求人を掲載した。",
        "zh": "公司在网站上发布了一个职位空缺。",
        "hi": "कंपनी ने अपनी वेबसाइट पर नौकरी की रिक्ति प्रकाशित की।",
        "vi": "Công ty đã đăng một vị trí tuyển dụng trên trang web của mình.",
        "ko": "회사는 웹사이트에 채용 공고를 게시했다.",
        "id": "Perusahaan memasang lowongan kerja di situs webnya.",
        "th": "บริษัทประกาศตำแหน่งงานว่างบนเว็บไซต์",
        "es": "La empresa publicó una vacante en su sitio web.",
    },
    "workload": {
        "ja": "上司はチームの仕事量を調整した。",
        "zh": "主管调整了团队的工作量。",
        "hi": "पर्यवेक्षक ने टीम के काम का बोझ समायोजित किया।",
        "vi": "Người giám sát đã điều chỉnh khối lượng công việc của nhóm.",
        "ko": "상사는 팀의 업무량을 조정했다.",
        "id": "Supervisor menyesuaikan beban kerja tim.",
        "th": "หัวหน้างานปรับปริมาณงานของทีม",
        "es": "El supervisor ajustó la carga de trabajo del equipo.",
    },
    "receipt": {
        "ja": "経費精算のため、領収書を保管してください。",
        "zh": "请保留收据，以便报销费用。",
        "hi": "खर्चे की रिपोर्ट के लिए कृपया रसीद संभालकर रखें।",
        "vi": "Vui lòng giữ lại biên lai để làm báo cáo chi phí.",
        "ko": "경비 보고를 위해 영수증을 보관해 주세요.",
        "id": "Harap simpan tanda terima untuk laporan pengeluaran Anda.",
        "th": "โปรดเก็บใบเสร็จไว้สำหรับรายงานค่าใช้จ่าย",
        "es": "Conserve el recibo para su informe de gastos.",
    },
    "refund": {
        "ja": "顧客が商品を返品した後、店は払い戻しを行った。",
        "zh": "顾客退回商品后，商店进行了退款。",
        "hi": "ग्राहक द्वारा उत्पाद लौटाने के बाद स्टोर ने धनवापसी की।",
        "vi": "Cửa hàng đã hoàn tiền sau khi khách hàng trả lại sản phẩm.",
        "ko": "고객이 제품을 반품한 후 매장에서 환불했다.",
        "id": "Toko memberikan pengembalian dana setelah pelanggan mengembalikan produk.",
        "th": "ร้านคืนเงินหลังจากลูกค้าส่งคืนสินค้า",
        "es": "La tienda emitió un reembolso después de que el cliente devolviera el producto.",
    },
    "cash flow": {
        "ja": "報告書によると、今四半期はキャッシュフローが改善した。",
        "zh": "报告显示，公司本季度的现金流有所改善。",
        "hi": "रिपोर्ट से पता चलता है कि इस तिमाही में नकदी प्रवाह में सुधार हुआ।",
        "vi": "Báo cáo cho thấy dòng tiền đã cải thiện trong quý này.",
        "ko": "보고서에 따르면 이번 분기에 현금 흐름이 개선되었다.",
        "id": "Laporan menunjukkan bahwa arus kas membaik pada kuartal ini.",
        "th": "รายงานแสดงให้เห็นว่ากระแสเงินสดดีขึ้นในไตรมาสนี้",
        "es": "El informe muestra que el flujo de caja mejoró este trimestre.",
    },
    "vendor": {
        "ja": "購買チームは新しい仕入先を選定した。",
        "zh": "采购团队选定了一家新的供应商。",
        "hi": "खरीद टीम ने एक नया विक्रेता चुना।",
        "vi": "Bộ phận mua hàng đã chọn một nhà cung cấp mới.",
        "ko": "구매팀은 새로운 판매업체를 선정했다.",
        "id": "Tim pembelian memilih vendor baru.",
        "th": "ทีมจัดซื้อเลือกผู้ขายรายใหม่",
        "es": "El equipo de compras seleccionó un nuevo proveedor.",
    },
    "shipment": {
        "ja": "出荷品は予定どおり倉庫に到着した。",
        "zh": "货物按时抵达仓库。",
        "hi": "शिपमेंट समय पर गोदाम में पहुंच गया।",
        "vi": "Lô hàng đã đến kho đúng giờ.",
        "ko": "화물이 예정대로 창고에 도착했다.",
        "id": "Kiriman tiba di gudang tepat waktu.",
        "th": "สินค้าขนส่งมาถึงคลังสินค้าตรงเวลา",
        "es": "El envío llegó al almacén a tiempo.",
    },
    "warehouse": {
        "ja": "倉庫では配達前の商品を保管している。",
        "zh": "仓库在配送前存放商品。",
        "hi": "गोदाम डिलीवरी से पहले सामान रखता है।",
        "vi": "Kho lưu trữ hàng hóa trước khi giao.",
        "ko": "창고에서는 배송 전에 제품을 보관한다.",
        "id": "Gudang menyimpan produk sebelum dikirim.",
        "th": "คลังสินค้าเก็บผลิตภัณฑ์ไว้ก่อนจัดส่ง",
        "es": "El almacén guarda los productos antes de su entrega.",
    },
    "itinerary": {
        "ja": "アシスタントは出張前に旅程を確認した。",
        "zh": "助理在出差前确认了行程。",
        "hi": "सहायक ने व्यावसायिक यात्रा से पहले यात्रा कार्यक्रम की पुष्टि की।",
        "vi": "Trợ lý đã xác nhận lịch trình trước chuyến công tác.",
        "ko": "비서는 출장 전에 일정을 확인했다.",
        "id": "Asisten mengonfirmasi rencana perjalanan sebelum perjalanan bisnis.",
        "th": "ผู้ช่วยยืนยันกำหนดการเดินทางก่อนเดินทางไปทำงาน",
        "es": "El asistente confirmó el itinerario antes del viaje de negocios.",
    },
    "departure": {
        "ja": "遅延のため、出発時刻が変更された。",
        "zh": "由于延误，出发时间发生了改变。",
        "hi": "देरी के कारण प्रस्थान का समय बदल दिया गया।",
        "vi": "Thời gian khởi hành đã được thay đổi do bị trì hoãn.",
        "ko": "지연으로 인해 출발 시간이 변경되었다.",
        "id": "Waktu keberangkatan diubah karena keterlambatan.",
        "th": "เวลาออกเดินทางถูกเปลี่ยนเนื่องจากความล่าช้า",
        "es": "La hora de salida cambió debido al retraso.",
    },
    "hardware": {
        "ja": "ITチームは破損したハードウェアを交換した。",
        "zh": "IT团队更换了损坏的硬件。",
        "hi": "आईटी टीम ने खराब हार्डवेयर को बदल दिया।",
        "vi": "Đội ngũ CNTT đã thay thế phần cứng bị hỏng.",
        "ko": "IT 팀은 손상된 하드웨어를 교체했다.",
        "id": "Tim TI mengganti perangkat keras yang rusak.",
        "th": "ทีมไอทีเปลี่ยนฮาร์ดแวร์ที่เสียหาย",
        "es": "El equipo de TI sustituyó el hardware dañado.",
    },
    "notify": {
        "ja": "遅延について顧客に通知してください。",
        "zh": "请通知客户有关延误的情况。",
        "hi": "कृपया ग्राहक को देरी के बारे में सूचित करें।",
        "vi": "Vui lòng thông báo cho khách hàng về việc chậm trễ.",
        "ko": "고객에게 지연 사실을 알려 주세요.",
        "id": "Harap beri tahu klien tentang keterlambatan tersebut.",
        "th": "โปรดแจ้งลูกค้าเกี่ยวกับความล่าช้า",
        "es": "Notifique al cliente sobre el retraso.",
    },
    "postpone": {
        "ja": "マネージャーは会議を延期することにした。",
        "zh": "经理决定推迟会议。",
        "hi": "प्रबंधक ने बैठक स्थगित करने का निर्णय लिया।",
        "vi": "Người quản lý quyết định hoãn cuộc họp.",
        "ko": "관리자는 회의를 연기하기로 했다.",
        "id": "Manajer memutuskan untuk menunda rapat.",
        "th": "ผู้จัดการตัดสินใจเลื่อนการประชุม",
        "es": "El gerente decidió posponer la reunión.",
    },
    "profitable": {
        "ja": "その新サービスは1年以内に黒字化した。",
        "zh": "这项新服务在一年内实现了盈利。",
        "hi": "नई सेवा एक वर्ष के भीतर लाभदायक बन गई।",
        "vi": "Dịch vụ mới đã có lãi trong vòng một năm.",
        "ko": "새로운 서비스는 1년 안에 수익을 내기 시작했다.",
        "id": "Layanan baru itu menjadi menguntungkan dalam waktu satu tahun.",
        "th": "บริการใหม่ทำกำไรได้ภายในหนึ่งปี",
        "es": "El nuevo servicio empezó a ser rentable en un año.",
    },
    "onboarding": {
        "ja": "人事チームは新入社員向けのオンボーディング計画を準備した。",
        "zh": "人力资源团队为新员工制定了入职培训计划。",
        "hi": "मानव संसाधन टीम ने नए कर्मचारियों के लिए ऑनबोर्डिंग योजना तैयार की।",
        "vi": "Bộ phận nhân sự đã chuẩn bị kế hoạch hội nhập cho nhân viên mới.",
        "ko": "인사팀은 신입 직원을 위한 온보딩 계획을 마련했다.",
        "id": "Tim SDM menyiapkan rencana orientasi bagi karyawan baru.",
        "th": "ทีม HR จัดทำแผนปฐมนิเทศสำหรับพนักงานใหม่",
        "es": "El equipo de RR. HH. preparó un plan de incorporación para los nuevos empleados.",
    },
    "deliverable": {
        "ja": "チームは締め切り前に成果物を提出した。",
        "zh": "团队在截止日期前提交了交付成果。",
        "hi": "टीम ने समय सीमा से पहले निर्धारित कार्य-परिणाम जमा कर दिया।",
        "vi": "Nhóm đã nộp sản phẩm bàn giao trước thời hạn.",
        "ko": "팀은 마감일 전에 결과물을 제출했다.",
        "id": "Tim menyerahkan hasil kerja yang harus diserahkan sebelum tenggat waktu.",
        "th": "ทีมส่งมอบผลงานก่อนกำหนด",
        "es": "El equipo entregó el resultado previsto antes de la fecha límite.",
    },
    "turnover": {
        "ja": "会社は従業員の離職率を下げようとしている。",
        "zh": "公司正在努力降低员工流失率。",
        "hi": "कंपनी कर्मचारियों के नौकरी छोड़ने की दर कम करने के लिए काम कर रही है।",
        "vi": "Công ty đang nỗ lực giảm tỷ lệ nhân viên nghỉ việc.",
        "ko": "회사는 직원 이직률을 낮추기 위해 노력하고 있다.",
        "id": "Perusahaan berupaya mengurangi pergantian karyawan.",
        "th": "บริษัทกำลังพยายามลดอัตราการลาออกของพนักงาน",
        "es": "La empresa trabaja para reducir la rotación de empleados.",
    },
    "outsourcing": {
        "ja": "外注により顧客サポートの費用が減少した。",
        "zh": "外包降低了客户支持成本。",
        "hi": "आउटसोर्सिंग से ग्राहक सहायता की लागत कम हुई।",
        "vi": "Việc thuê ngoài đã làm giảm chi phí hỗ trợ khách hàng.",
        "ko": "아웃소싱으로 고객 지원 비용이 줄었다.",
        "id": "Alih daya mengurangi biaya dukungan pelanggan.",
        "th": "การจ้างงานภายนอกช่วยลดต้นทุนการสนับสนุนลูกค้า",
        "es": "La externalización redujo el coste de la atención al cliente.",
    },
    "retailer": {
        "ja": "小売業者は休暇シーズン前に大量注文を出した。",
        "zh": "零售商在假日季前下了一笔大订单。",
        "hi": "खुदरा विक्रेता ने छुट्टियों के मौसम से पहले एक बड़ा ऑर्डर दिया।",
        "vi": "Nhà bán lẻ đã đặt một đơn hàng lớn trước mùa lễ.",
        "ko": "소매업체는 연휴 시즌 전에 대량 주문을 넣었다.",
        "id": "Pengecer memesan dalam jumlah besar sebelum musim liburan.",
        "th": "ผู้ค้าปลีกสั่งซื้อสินค้าจำนวนมากก่อนช่วงเทศกาลวันหยุด",
        "es": "El minorista hizo un pedido importante antes de la temporada navideña.",
    },
    "distributor": {
        "ja": "販売代理店は商品を地域の店舗へ納品した。",
        "zh": "分销商将产品配送到当地商店。",
        "hi": "वितरक ने स्थानीय दुकानों तक उत्पाद पहुंचाए।",
        "vi": "Nhà phân phối đã giao sản phẩm cho các cửa hàng địa phương.",
        "ko": "유통업체는 지역 매장에 제품을 배송했다.",
        "id": "Distributor mengirimkan produk ke toko-toko setempat.",
        "th": "ผู้จัดจำหน่ายส่งสินค้าไปยังร้านค้าในท้องถิ่น",
        "es": "El distribuidor entregó los productos a las tiendas locales.",
    },
    "consignment": {
        "ja": "委託販売品は月曜日に港へ到着した。",
        "zh": "寄售货物周一抵达港口。",
        "hi": "बिक्री के लिए भेजा गया माल सोमवार को बंदरगाह पहुंचा।",
        "vi": "Lô hàng ký gửi đã đến cảng vào thứ Hai.",
        "ko": "위탁 판매 물품은 월요일에 항구에 도착했다.",
        "id": "Barang konsinyasi tiba di pelabuhan pada hari Senin.",
        "th": "สินค้าฝากขายมาถึงท่าเรือเมื่อวันจันทร์",
        "es": "La mercancía en consignación llegó al puerto el lunes.",
    },
    "customs": {
        "ja": "出荷品は税関で2日間止められた。",
        "zh": "货物在海关被扣留了两天。",
        "hi": "शिपमेंट को सीमा शुल्क विभाग में दो दिनों तक रोका गया।",
        "vi": "Lô hàng bị giữ tại hải quan trong hai ngày.",
        "ko": "화물이 세관에서 이틀 동안 보류되었다.",
        "id": "Kiriman tersebut tertahan di bea cukai selama dua hari.",
        "th": "สินค้าถูกกักไว้ที่ศุลกากรเป็นเวลาสองวัน",
        "es": "El envío quedó retenido en la aduana durante dos días.",
    },
    "forecasting": {
        "ja": "正確な予測は会社の予算計画に役立つ。",
        "zh": "准确的预测有助于公司制定预算。",
        "hi": "सटीक पूर्वानुमान से कंपनी को अपना बजट बनाने में मदद मिलती है।",
        "vi": "Dự báo chính xác giúp công ty lập ngân sách.",
        "ko": "정확한 예측은 회사가 예산을 계획하는 데 도움이 된다.",
        "id": "Peramalan yang akurat membantu perusahaan merencanakan anggarannya.",
        "th": "การคาดการณ์ที่แม่นยำช่วยให้บริษัทวางแผนงบประมาณได้",
        "es": "Una previsión precisa ayuda a la empresa a planificar su presupuesto.",
    },
    "quarterly": {
        "ja": "会社は四半期ごとの財務報告書を発行している。",
        "zh": "公司每季度发布财务报告。",
        "hi": "कंपनी हर तिमाही वित्तीय रिपोर्ट प्रकाशित करती है।",
        "vi": "Công ty công bố báo cáo tài chính hàng quý.",
        "ko": "회사는 분기별 재무 보고서를 발행한다.",
        "id": "Perusahaan menerbitkan laporan keuangan setiap kuartal.",
        "th": "บริษัทเผยแพร่รายงานทางการเงินรายไตรมาส",
        "es": "La empresa publica un informe financiero trimestral.",
    },
    "optional": {
        "ja": "上級研修は従業員にとって任意である。",
        "zh": "高级培训课程对员工来说是可选的。",
        "hi": "उन्नत प्रशिक्षण सत्र कर्मचारियों के लिए वैकल्पिक है।",
        "vi": "Buổi đào tạo nâng cao là tùy chọn đối với nhân viên.",
        "ko": "고급 교육 세션은 직원에게 선택 사항이다.",
        "id": "Sesi pelatihan lanjutan bersifat opsional bagi karyawan.",
        "th": "การฝึกอบรมขั้นสูงเป็นทางเลือกสำหรับพนักงาน",
        "es": "La sesión de formación avanzada es opcional para los empleados.",
    },
    "delegate": {
        "ja": "マネージャーは経験豊富な従業員にその仕事を委任する。",
        "zh": "经理会把这项任务委派给一名经验丰富的员工。",
        "hi": "प्रबंधक यह कार्य एक अनुभवी कर्मचारी को सौंप देगा।",
        "vi": "Người quản lý sẽ giao nhiệm vụ này cho một nhân viên giàu kinh nghiệm.",
        "ko": "관리자는 경험 많은 직원에게 그 업무를 위임할 것이다.",
        "id": "Manajer akan mendelegasikan tugas tersebut kepada karyawan yang berpengalaman.",
        "th": "ผู้จัดการจะมอบหมายงานนี้ให้พนักงานที่มีประสบการณ์",
        "es": "El gerente delegará la tarea a un empleado con experiencia.",
    },
    "incur": {
        "ja": "会社は追加の配送費を負担する可能性がある。",
        "zh": "公司可能会产生额外的运输费用。",
        "hi": "कंपनी पर अतिरिक्त शिपिंग लागत आ सकती है।",
        "vi": "Công ty có thể phải chịu thêm chi phí vận chuyển.",
        "ko": "회사는 추가 배송 비용을 부담할 수 있다.",
        "id": "Perusahaan mungkin menanggung biaya pengiriman tambahan.",
        "th": "บริษัทอาจต้องรับภาระค่าขนส่งเพิ่มเติม",
        "es": "La empresa puede incurrir en gastos de envío adicionales.",
    },
    "verify": {
        "ja": "支払いの前に請求書を確認してください。",
        "zh": "付款前请核实发票。",
        "hi": "भुगतान करने से पहले कृपया चालान की जाँच करें।",
        "vi": "Vui lòng kiểm tra hóa đơn trước khi thanh toán.",
        "ko": "결제하기 전에 청구서를 확인해 주세요.",
        "id": "Harap verifikasi faktur sebelum melakukan pembayaran.",
        "th": "โปรดตรวจสอบใบแจ้งหนี้ก่อนชำระเงิน",
        "es": "Verifique la factura antes de efectuar el pago.",
    },
}


def main() -> None:
    vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    phrase_root = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    translations = phrase_root.setdefault("translations", {})
    by_word = {str(item.get("word", "")).casefold(): item for item in vocabulary}
    changed = 0
    for word, localized in EXAMPLE_TRANSLATIONS.items():
        item = by_word.get(word.casefold())
        if item is None:
            raise KeyError(f"missing added business term: {word}")
        key = f"builtin:{item['id']}"
        example = translations.setdefault(key, {}).setdefault("example", {})
        source = str(item.get("example", "")).strip()
        if example.get("source") != source:
            example["source"] = source
            changed += 1
        if example.get("en") != source:
            example["en"] = source
            changed += 1
        for language, value in localized.items():
            if example.get(language) != value:
                example[language] = value
                changed += 1

    assert set(EXAMPLE_TRANSLATIONS) == {
        str(item.get("word", "")).casefold()
        for item in vocabulary
        if item.get("source_list") == "TOEIC-business-v1"
    }
    VOCAB_PATH.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    PHRASE_PATH.write_text(json.dumps(phrase_root, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"reviewed added business examples: {changed}")


if __name__ == "__main__":
    main()
