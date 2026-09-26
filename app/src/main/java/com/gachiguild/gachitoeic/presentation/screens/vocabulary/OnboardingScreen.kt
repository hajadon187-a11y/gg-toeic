package com.gachiguild.gachitoeic.presentation.screens.vocabulary

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.OpenInNew
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gachiguild.gachitoeic.data.ai.AiAppProvider
import com.gachiguild.gachitoeic.data.ai.InstalledAiApp
import com.gachiguild.gachitoeic.ui.AppStrings

private data class OnboardingCopy(
    val welcomeTitle: String,
    val welcomeBody: String,
    val next: String,
    val back: String,
    val finish: String,
    val aiSkip: String,
    val targetTitle: String,
    val targetBody: String,
    val dailyTitle: String,
    val dailyBody: String,
    val aiTitle: String,
    val aiBody: String,
    val aiFreeInstall: String,
    val aiSelect: String,
    val aiSelected: String,
    val aiRefresh: String,
    val startLearning: String,
    val aiPracticeTitle: String,
    val aiPractice: String,
    val noAiBody: String,
    val aiConnectionIntro: String,
    val learnWord: String,
    val practiceWithAi: String,
    val aiBenefit: String,
    val dailyUnit: String,
    val aiStartedBody: String,
    val chatGptDescription: String,
    val geminiDescription: String
)

private fun onboardingCopy(strings: AppStrings): OnboardingCopy {
    val copy = when (strings.languageCode) {
    "ja" -> OnboardingCopy("TOEIC単語を、AIとの会話で使える英語へ", "目標Bandに合わせて単語を学び、ChatGPTまたはGeminiと英語で会話練習をします。", "次へ", "戻る", "学習を始める", "スキップ", "目標Bandを選びましょう", "", "1日の学習量を決めましょう", "無理なく続けられる量から始められます。あとで変更できます。", "AI会話を準備しましょう", "ChatGPTまたはGeminiのどちらか1つをインストールすれば、覚えた単語を使って会話練習できます。", "無料でインストール", "このAIを使う", "選択中", "インストールを確認", "AIなしで続ける", "最初の単語カードを、AIと一緒に練習してみましょう！", "AI会話を試す", "AIアプリはあとから設定できます。単語学習だけでも利用できます。", "AIとの連携は簡単です。", "手順に沿ってAIを起動し、AI Liveモードをオンにします。", "その後、このアプリに戻り、覚えたい単語をテーマにAIと話しましょう。", "自分の母語で説明を受けたり、例文を英語で読んで、発音を直してもらうこともできます。", "語 / 日", "AIアプリで会話を始めました。", "音声会話の練習", "Live会話の練習")
    "zh" -> OnboardingCopy("将 TOEIC 词汇变成能在 AI 对话中使用的英语", "根据目标分数学习词汇，并与 ChatGPT 或 Gemini 用英语练习对话。", "下一步", "返回", "开始学习", "跳过", "选择目标分数", "", "设置每日学习量", "从适合长期坚持的数量开始。之后可以更改。", "准备 AI 对话练习", "安装 ChatGPT 或 Gemini 其中任意一个，就可以用学过的词汇进行对话练习。", "免费安装", "使用此 AI", "已选择", "检查安装状态", "不使用 AI，继续", "和 AI 一起练习第一张单词卡吧！", "试试 AI 对话", "之后可以设置 AI。即使不使用 AI，也可以学习词汇。", "连接 AI 应用很简单。", "按照步骤打开 AI 应用，并启用 AI Live 模式。", "然后返回此应用，围绕想记住的单词与 AI 对话。", "你还可以用自己的母语听解释，用英语朗读例句，并请 AI 帮你纠正发音。", "词 / 天", "已在 AI 应用中开始对话。", "语音对话练习", "Live 模式对话练习")
    "hi" -> OnboardingCopy("AI से बातचीत के ज़रिए TOEIC शब्दावली को उपयोगी अंग्रेज़ी में बदलें", "अपना लक्ष्य स्तर चुनें, शब्दावली सीखें और ChatGPT या Gemini के साथ अंग्रेज़ी में बोलने का अभ्यास करें।", "आगे", "वापस", "सीखना शुरू करें", "छोड़ें", "अपना लक्ष्य स्तर चुनें", "", "प्रतिदिन की पढ़ाई की मात्रा चुनें", "ऐसी मात्रा से शुरू करें जिसे लगातार जारी रख सकें। इसे बाद में बदला जा सकता है।", "AI के साथ बातचीत का अभ्यास शुरू करें", "ChatGPT या Gemini में से किसी एक को इंस्टॉल करके सीखे हुए शब्दों से बातचीत का अभ्यास करें।", "मुफ़्त में इंस्टॉल करें", "इस AI का उपयोग करें", "चयनित", "इंस्टॉलेशन जाँचें", "AI के बिना जारी रखें", "AI के साथ अपना पहला शब्द कार्ड आज़माएँ!", "AI बातचीत आज़माएँ", "AI बाद में सेट किया जा सकता है। AI के बिना भी शब्दावली का अभ्यास कर सकते हैं।", "AI ऐप से जुड़ना आसान है।", "निर्देशों का पालन करके AI ऐप खोलें और AI Live मोड चालू करें।", "फिर इस ऐप पर वापस आकर, जिस शब्द को याद करना चाहते हैं उसके बारे में AI से बात करें।", "आप अपनी मातृभाषा में व्याख्या सुन सकते हैं, उदाहरण वाक्य अंग्रेज़ी में पढ़ सकते हैं और AI से अपना उच्चारण ठीक करवा सकते हैं।", "शब्द / दिन", "AI ऐप में बातचीत शुरू हो गई है।", "वॉइस बातचीत का अभ्यास", "Live बातचीत का अभ्यास")
    "vi" -> OnboardingCopy("Biến từ vựng TOEIC thành vốn tiếng Anh có thể dùng khi trò chuyện với AI", "Chọn cấp độ mục tiêu, học từ vựng và luyện nói tiếng Anh với ChatGPT hoặc Gemini.", "Tiếp theo", "Quay lại", "Bắt đầu học", "Bỏ qua", "Chọn cấp độ mục tiêu", "", "Chọn lượng học mỗi ngày", "Hãy bắt đầu với lượng học có thể duy trì đều đặn. Bạn có thể thay đổi sau.", "Thiết lập luyện hội thoại với AI", "Cài đặt ChatGPT hoặc Gemini để luyện hội thoại bằng những từ bạn đã học.", "Cài đặt miễn phí", "Dùng AI này", "Đã chọn", "Kiểm tra cài đặt", "Tiếp tục không dùng AI", "Hãy cùng AI luyện tập thẻ từ đầu tiên!", "Thử hội thoại với AI", "Bạn có thể thiết lập AI sau. Bạn vẫn có thể học từ vựng mà không cần AI.", "Việc kết nối với ứng dụng AI rất đơn giản.", "Làm theo hướng dẫn để mở ứng dụng AI và bật chế độ AI Live.", "Sau đó, quay lại ứng dụng này và trò chuyện với AI về từ bạn muốn ghi nhớ.", "Bạn cũng có thể nghe giải thích bằng tiếng mẹ đẻ, đọc câu ví dụ bằng tiếng Anh và nhờ AI sửa phát âm.", "từ / ngày", "Cuộc hội thoại đã bắt đầu trong ứng dụng AI.", "Luyện hội thoại bằng giọng nói", "Luyện hội thoại trong chế độ Live")
    "ko" -> OnboardingCopy("TOEIC 어휘를 AI와 대화할 때 쓸 수 있는 영어로 바꿔 보세요", "목표 레벨을 선택하고 어휘를 학습한 뒤 ChatGPT 또는 Gemini와 영어 말하기를 연습합니다.", "다음", "뒤로", "학습 시작", "건너뛰기", "목표 레벨을 선택하세요", "", "하루 학습량을 선택하세요", "꾸준히 유지할 수 있는 양으로 시작하세요. 나중에 변경할 수 있습니다.", "AI 대화 연습 설정", "ChatGPT 또는 Gemini 중 하나를 설치하면 학습한 단어로 대화 연습을 할 수 있습니다.", "무료 설치", "이 AI 사용하기", "선택됨", "설치 확인", "AI 없이 계속", "AI와 함께 첫 번째 단어 카드를 연습해 보세요!", "AI 대화 해보기", "AI는 나중에 설정할 수 있습니다. AI 없이도 어휘를 학습할 수 있습니다.", "AI 앱 연결은 간단합니다.", "안내에 따라 AI 앱을 실행하고 AI Live 모드를 켜세요.", "그런 다음 이 앱으로 돌아와 외우고 싶은 단어를 주제로 AI와 대화하세요.", "모국어로 설명을 듣고, 예문을 영어로 읽으며 AI에게 발음을 교정받을 수도 있습니다.", "단어 / 일", "AI 앱에서 대화를 시작했습니다.", "음성 대화 연습", "Live 모드 대화 연습")
    "id" -> OnboardingCopy("Ubah kosakata TOEIC menjadi bahasa Inggris yang bisa Anda gunakan saat berbicara dengan AI", "Pilih level target, pelajari kosakata, dan berlatih berbicara dalam bahasa Inggris dengan ChatGPT atau Gemini.", "Berikutnya", "Kembali", "Mulai belajar", "Lewati", "Pilih level target", "", "Pilih jumlah kata yang dipelajari setiap hari", "Mulailah dengan jumlah yang sanggup Anda pelajari secara rutin. Anda dapat mengubahnya nanti.", "Siapkan latihan percakapan dengan AI", "Instal salah satu aplikasi, ChatGPT atau Gemini, untuk berlatih menggunakan kata-kata yang Anda pelajari dalam percakapan.", "Instal gratis", "Gunakan AI ini", "Dipilih", "Periksa instalasi", "Lanjutkan tanpa AI", "Latih kartu kata pertama bersama AI!", "Coba percakapan AI", "AI dapat disiapkan nanti. Anda tetap dapat belajar kosakata tanpa AI.", "Menghubungkan aplikasi AI itu mudah.", "Ikuti langkah-langkah untuk membuka aplikasi AI dan mengaktifkan mode AI Live.", "Setelah itu, kembali ke aplikasi ini dan berbicaralah dengan AI tentang kata yang ingin Anda hafalkan.", "Anda juga dapat menerima penjelasan dalam bahasa ibu, membaca contoh kalimat dalam bahasa Inggris, dan meminta AI memperbaiki pelafalan Anda.", "kata / hari", "Percakapan telah dimulai di aplikasi AI.", "Latihan percakapan melalui suara", "Latihan percakapan dalam mode Live")
    "th" -> OnboardingCopy("เปลี่ยนคำศัพท์ TOEIC ให้เป็นภาษาอังกฤษที่ใช้ได้จริงผ่านการสนทนากับ AI", "เลือกระดับเป้าหมาย เรียนคำศัพท์ และฝึกพูดภาษาอังกฤษกับ ChatGPT หรือ Gemini", "ถัดไป", "ย้อนกลับ", "เริ่มเรียน", "ข้าม", "เลือกระดับเป้าหมาย", "", "เลือกปริมาณการเรียนต่อวัน", "เริ่มจากปริมาณที่ทำต่อเนื่องได้ คุณสามารถเปลี่ยนได้ภายหลัง", "เตรียมการฝึกสนทนากับ AI", "ติดตั้ง ChatGPT หรือ Gemini อย่างใดอย่างหนึ่งเพื่อฝึกสนทนาโดยใช้คำศัพท์ที่เรียนมา", "ติดตั้งฟรี", "ใช้ AI นี้", "เลือกแล้ว", "ตรวจสอบการติดตั้ง", "ดำเนินการต่อโดยไม่ใช้ AI", "ลองฝึกการ์ดคำศัพท์ใบแรกกับ AI!", "ลองสนทนากับ AI", "คุณสามารถตั้งค่า AI ได้ภายหลัง และยังเรียนคำศัพท์ได้โดยไม่ใช้ AI", "การเชื่อมต่อกับแอป AI เป็นเรื่องง่าย", "ทำตามขั้นตอนเพื่อเปิดแอป AI และเปิดโหมด AI Live", "จากนั้นกลับมาที่แอปนี้ แล้วพูดคุยกับ AI เกี่ยวกับคำศัพท์ที่ต้องการจำ", "คุณยังสามารถรับคำอธิบายเป็นภาษาแม่ อ่านประโยคตัวอย่างเป็นภาษาอังกฤษ และให้ AI ช่วยแก้การออกเสียงได้", "คำ / วัน", "เริ่มการสนทนาในแอป AI แล้ว", "ฝึกสนทนาด้วยเสียง", "ฝึกสนทนาในโหมด Live")
    "es" -> OnboardingCopy("Convierte el vocabulario de TOEIC en inglés que puedas usar al conversar con la IA", "Elige tu nivel objetivo, aprende vocabulario y practica inglés con ChatGPT o Gemini.", "Siguiente", "Atrás", "Empezar a estudiar", "Omitir", "Elige tu nivel objetivo", "", "Elige tu cantidad diaria de estudio", "Empieza con una cantidad que puedas mantener. Puedes cambiarla después.", "Configura la práctica de conversación con IA", "Instala una de estas aplicaciones, ChatGPT o Gemini, para practicar conversaciones usando las palabras que aprendes.", "Instalar gratis", "Usar esta IA", "Seleccionada", "Comprobar instalación", "Continuar sin IA", "¡Practica tu primera tarjeta de vocabulario con IA!", "Probar conversación con IA", "Puedes configurar la IA más tarde. También puedes estudiar vocabulario sin IA.", "Conectar una aplicación de IA es sencillo.", "Sigue los pasos para abrir la aplicación de IA y activar el modo AI Live.", "Después, vuelve a esta aplicación y habla con la IA sobre la palabra que quieres recordar.", "También puedes recibir explicaciones en tu lengua materna, leer la frase de ejemplo en inglés y pedir a la IA que corrija tu pronunciación.", "palabras / día", "La conversación ha comenzado en la aplicación de IA.", "Práctica de conversación por voz", "Práctica de conversación en modo Live")
    else -> OnboardingCopy("Turn TOEIC vocabulary into English you can use in AI conversations", "Choose your target level, learn vocabulary, and practice speaking English with ChatGPT or Gemini.", "Next", "Back", "Start learning", "Skip", "Choose your target level", "", "Choose your daily study amount", "Start with an amount you can maintain. You can change it later.", "Set up AI conversation practice", "Install either ChatGPT or Gemini to practice conversations using the words you learn.", "Install for free", "Use this AI", "Selected", "Check installation", "Continue without AI", "Practice your first flashcard with AI!", "Try AI conversation", "You can set up AI later. You can also study vocabulary without AI.", "Connecting an AI app is easy.", "Follow the steps to open the AI app and turn on AI Live mode.", "Then return to this app and talk with AI about the word you want to remember.", "You can also get explanations in your native language, read the example sentence in English, and ask AI to correct your pronunciation.", "words / day", "The conversation has started in the AI app.", "Voice conversation practice", "Practice live conversations")
    }
    val (from, to) = when (strings.languageCode) {
        "ja" -> "Band" to "レベル"
        "hi" -> "बैंड" to "स्तर"
        "vi" -> "band" to "cấp độ"
        "ko" -> "Band" to "레벨"
        "id" -> "band" to "level"
        "th" -> "Band" to "ระดับ"
        "es" -> "banda" to "nivel"
        else -> "band" to "level"
    }
    return copy.copy(
        welcomeBody = copy.welcomeBody.replace(from, to),
        targetTitle = copy.targetTitle.replace(from, to)
    )
}

@Composable
fun OnboardingScreen(
    strings: AppStrings,
    installedApps: List<InstalledAiApp>,
    initialTargetLevel: String,
    initialDailyTarget: Int,
    initialPreferredProviderPackage: String?,
    onRefreshInstalledApps: () -> Unit,
    onOpenStore: (AiAppProvider) -> Unit,
    onProviderSelected: (InstalledAiApp?) -> Unit,
    onAiPractice: (InstalledAiApp) -> Boolean,
    onStartLearning: () -> Unit,
    onOpenPrivacyPolicy: () -> Unit,
    onComplete: (targetLevel: String, dailyTarget: Int, provider: InstalledAiApp?) -> Unit,
    onPageChanged: (Int) -> Unit = {}
) {
    val copy = onboardingCopy(strings)
    var page by rememberSaveable { mutableIntStateOf(0) }
    var targetLevel by rememberSaveable { mutableStateOf(initialTargetLevel) }
    var dailyTarget by rememberSaveable { mutableIntStateOf(initialDailyTarget.coerceIn(5, 30)) }
    var selectedPackage by rememberSaveable { mutableStateOf(initialPreferredProviderPackage) }
    var aiStarted by rememberSaveable { mutableStateOf(false) }

    LaunchedEffect(page) {
        onPageChanged(page)
    }

    val selectedApp = installedApps.firstOrNull { it.packageName == selectedPackage }
    val complete = { onComplete(targetLevel, dailyTarget, selectedApp) }

    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 28.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                repeat(3) { index ->
                    Box(
                        modifier = Modifier
                            .padding(horizontal = 4.dp)
                            .size(if (index == page) 10.dp else 7.dp)
                            .background(
                                if (index == page) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant,
                                MaterialTheme.shapes.small
                            )
                    )
                }
            }

            when (page) {
                0 -> {
                    // アプリの使い方ツアーの直後に、AIの設定を案内する。
                    OnboardingTitle(copy.aiTitle, copy.aiBody)
                    if (installedApps.isEmpty()) Text(copy.noAiBody, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    AiProviderOnboardingCard(AiAppProvider.CHATGPT, installedApps.firstOrNull { it.provider == AiAppProvider.CHATGPT }, selectedPackage == AiAppProvider.CHATGPT.packageName, copy, { onOpenStore(AiAppProvider.CHATGPT) }) { app ->
                        if (selectedPackage == app.packageName) {
                            selectedPackage = null
                            onProviderSelected(null)
                        } else {
                            selectedPackage = app.packageName
                            onProviderSelected(app)
                        }
                    }
                    AiProviderOnboardingCard(AiAppProvider.GEMINI, installedApps.firstOrNull { it.provider == AiAppProvider.GEMINI }, selectedPackage == AiAppProvider.GEMINI.packageName, copy, { onOpenStore(AiAppProvider.GEMINI) }) { app ->
                        if (selectedPackage == app.packageName) {
                            selectedPackage = null
                            onProviderSelected(null)
                        } else {
                            selectedPackage = app.packageName
                            onProviderSelected(app)
                        }
                    }
                    OutlinedButton(onClick = onRefreshInstalledApps, modifier = Modifier.fillMaxWidth()) { Text(copy.aiRefresh) }
                    TextButton(
                        onClick = onOpenPrivacyPolicy,
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    ) {
                        Text("Privacy Policy")
                    }
                    PrimaryOnboardingButton(if (selectedApp == null) "Start Learning" else copy.next) {
                        if (selectedApp == null) onStartLearning() else page = 1
                    }
                    OnboardingSkipButton(copy.aiSkip, onClick = onStartLearning)
                }
                1 -> {
                    OnboardingTitle(copy.welcomeTitle, copy.welcomeBody)
                    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                        Column(modifier = Modifier.padding(20.dp)) {
                            Text(copy.aiConnectionIntro)
                            Spacer(modifier = Modifier.size(10.dp))
                            Text(copy.learnWord)
                            Spacer(modifier = Modifier.size(10.dp))
                            Text(copy.practiceWithAi)
                            Spacer(modifier = Modifier.size(10.dp))
                            Text(copy.aiBenefit)
                        }
                    }
                    OnboardingNavigation({ page = 0 }, copy.back, { page = 2 }, copy.next)
                    OnboardingSkipButton(copy.aiSkip, onClick = complete)
                }
                else -> {
                    val guidance = aiLiveGuidanceCopy(strings)
                    val images = aiLiveGuidanceImages(selectedApp?.provider ?: AiAppProvider.CHATGPT)
                    OnboardingTitle(copy.aiPracticeTitle, guidance.intro)
                    AiLiveGuidanceImage(strings, guidance.liveLabel, images.first)
                    Text(guidance.liveDescription, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    AiLiveGuidanceImage(strings, guidance.appsLabel, images.second)
                    Text(guidance.appsDescription, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    if (selectedApp != null) {
                        Button(onClick = { aiStarted = onAiPractice(selectedApp) }, modifier = Modifier.fillMaxWidth()) {
                            Icon(Icons.Filled.OpenInNew, contentDescription = null)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(copy.aiPractice)
                        }
                        if (aiStarted) Text(copy.aiStartedBody, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    } else Text(copy.noAiBody, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Button(onClick = complete, modifier = Modifier.fillMaxWidth()) { Text(copy.finish) }
                    TextButton(onClick = { page = 1 }, modifier = Modifier.align(Alignment.CenterHorizontally)) { Text(copy.back) }
                }
            }
        }
    }
}

@Composable
private fun AiProviderOnboardingCard(
    provider: AiAppProvider,
    installedApp: InstalledAiApp?,
    selected: Boolean,
    copy: OnboardingCopy,
    onInstall: () -> Unit,
    onSelect: (InstalledAiApp) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Row(modifier = Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(modifier = Modifier.weight(1f)) {
                Text(provider.fallbackLabel, fontWeight = FontWeight.Bold)
                Text(if (provider == AiAppProvider.CHATGPT) copy.chatGptDescription else copy.geminiDescription, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            if (installedApp == null) {
                OutlinedButton(onClick = onInstall) { Text(copy.aiFreeInstall) }
            } else {
                Button(onClick = { onSelect(installedApp) }) { Text(if (selected) copy.aiSelected else copy.aiSelect) }
            }
        }
    }
}

@Composable
private fun OnboardingTitle(title: String, body: String) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(title, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        if (body.isNotBlank()) Text(body, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun PrimaryOnboardingButton(label: String, onClick: () -> Unit) {
    Button(onClick = onClick, modifier = Modifier.fillMaxWidth()) { Text(label) }
}

@Composable
private fun OnboardingSkipButton(label: String, onClick: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Center
    ) {
        TextButton(onClick = onClick) { Text(label) }
    }
}

@Composable
private fun OnboardingNavigation(back: () -> Unit, backLabel: String, next: () -> Unit, nextLabel: String) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedButton(onClick = back, modifier = Modifier.weight(1f)) { Text(backLabel) }
        Button(onClick = next, modifier = Modifier.weight(1f)) { Text(nextLabel) }
    }
}
