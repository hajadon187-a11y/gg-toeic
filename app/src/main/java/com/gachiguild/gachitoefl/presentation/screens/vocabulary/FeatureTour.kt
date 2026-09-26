package com.gachiguild.gachitoefl.presentation.screens.vocabulary

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import com.gachiguild.gachitoefl.R
import com.gachiguild.gachitoefl.ui.AppStrings
import java.util.Locale

/**
 * ステップ文言に依存せずステップを識別する ID。
 * タイトルは多言語対応のため、画面側の特例処理はこの ID で判定する。
 */
enum class FeatureTourStepId {
    LONG_PRESS_MENU
}

/**
 * チュートリアルの1ステップ。
 *
 * [practiceWord] が設定されているステップでは、実際に操作してもらう単語を画面に掲示し、
 * 長押しなどの操作を検知するとガイドにチェックを表示する。
 */
data class FeatureTourStep(
    val targetKey: String,
    val title: String,
    val description: String,
    val practiceWord: String? = null,
    val stepId: FeatureTourStepId? = null
) {
    /** 実操作を促すステップか。 */
    val hasPractice: Boolean get() = practiceWord != null

    /** 実操作の検知に使うキー。実操作なしのステップでは null。 */
    val practiceKey: String? get() = practiceWord?.let { "$targetKey:$it" }
}

/** Stores coordinates for composables that can be explained by a tour. */
class FeatureTourState {
    private val bounds = mutableStateMapOf<String, Rect>()
    private val performedActions = mutableStateMapOf<String, Int>()

    fun register(key: String, rect: Rect) {
        bounds[key] = rect
    }

    fun boundsFor(key: String): Rect? = bounds[key]

    /**
     * チュートリアル中にユーザーが実操作（長押しなど）を行ったことを記録する。
     * 記録すると [actionCountFor] が変化し、ガイドのチェック表示が更新される。
     */
    fun registerAction(key: String) {
        performedActions[key] = (performedActions[key] ?: 0) + 1
    }

    /** [key] の実操作回数。未実施なら 0。 */
    fun actionCountFor(key: String): Int = performedActions[key] ?: 0

    fun clearActions() {
        performedActions.clear()
    }
}

fun Modifier.featureTourTarget(state: FeatureTourState, key: String): Modifier =
    onGloballyPositioned { coordinates ->
        state.register(key, coordinates.boundsInRoot())
    }

data class FeatureTourCopy(
    val mainTitle: String,
    val mainIntro: String,
    val settingsTour: String,
    val skip: String,
    val back: String,
    val next: String,
    val finish: String,
    val step: String,
    val settingsTitle: String,
    val settingsIntro: String,
    val openSettingsGuide: String
)

fun featureTourCopy(strings: AppStrings): FeatureTourCopy = when (strings.languageCode) {
    "ja" -> FeatureTourCopy("アプリの使い方", "主要なボタンと画面の役割を確認しましょう。", "設定画面の説明", "スキップ", "戻る", "次へ", "完了", "ステップ", "設定画面の使い方", "表示・データ移行の設定を確認しましょう。", "設定画面の使い方を見る")
    "zh" -> FeatureTourCopy("应用使用指南", "了解主要按钮和区域的作用。", "设置指南", "跳过", "返回", "下一步", "完成", "步骤", "设置页面使用指南", "了解显示和数据迁移设置。", "查看设置指南")
    "hi" -> FeatureTourCopy("ऐप का उपयोग कैसे करें", "मुख्य बटन और सेक्शन क्या करते हैं, यह जानें।", "सेटिंग्स गाइड", "छोड़ें", "वापस", "आगे", "पूरा करें", "चरण", "सेटिंग्स का उपयोग कैसे करें", "प्रदर्शन और डेटा स्थानांतरण सेटिंग देखें।", "सेटिंग्स गाइड देखें")
    "vi" -> FeatureTourCopy("Cách sử dụng ứng dụng", "Tìm hiểu chức năng của các nút và khu vực chính.", "Hướng dẫn Cài đặt", "Bỏ qua", "Quay lại", "Tiếp theo", "Hoàn tất", "Bước", "Cách sử dụng mục Cài đặt", "Xem lại các thiết lập hiển thị và di chuyển dữ liệu.", "Xem hướng dẫn Cài đặt")
    "ko" -> FeatureTourCopy("앱 사용 방법", "주요 버튼과 영역의 기능을 확인하세요.", "설정 안내", "건너뛰기", "뒤로", "다음", "완료", "단계", "설정 화면 사용 방법", "표시 및 데이터 이전 설정을 확인하세요.", "설정 안내 보기")
    "id" -> FeatureTourCopy("Cara menggunakan aplikasi", "Pelajari fungsi tombol dan bagian utama.", "Panduan Pengaturan", "Lewati", "Kembali", "Berikutnya", "Selesai", "Langkah", "Cara menggunakan menu Pengaturan", "Pelajari pengaturan tampilan dan pemindahan data.", "Lihat panduan Pengaturan")
    "th" -> FeatureTourCopy("วิธีใช้แอป", "ดูหน้าที่ของปุ่มและส่วนหลักต่าง ๆ", "คู่มือการตั้งค่า", "ข้าม", "ย้อนกลับ", "ถัดไป", "เสร็จสิ้น", "ขั้นตอน", "วิธีใช้หน้าการตั้งค่า", "ตรวจสอบการตั้งค่าการแสดงผลและการย้ายข้อมูล", "ดูคู่มือการตั้งค่า")
    "es" -> FeatureTourCopy("Cómo usar la aplicación", "Conoce la función de los botones y las secciones principales.", "Guía de Ajustes", "Omitir", "Atrás", "Siguiente", "Terminar", "Paso", "Cómo usar Ajustes", "Consulta los ajustes de pantalla y migración de datos.", "Ver la guía de Ajustes")
    else -> FeatureTourCopy("How to use the app", "Learn what the main buttons and sections do.", "Settings guide", "Skip", "Back", "Next", "Finish", "Step", "How to use Settings", "Review display and data migration settings.", "See the Settings guide")
}

data class FlashcardButtonHelpCopy(
    val previousDescription: String,
    val forgotDescription: String,
    val rememberedDescription: String,
    val previousLabel: String
)

fun flashcardButtonHelpCopy(strings: AppStrings): FlashcardButtonHelpCopy =
    FlashcardButtonHelpCopy(
        previousDescription = strings.frogPrevButtonHelp,
        forgotDescription = strings.frogStarButtonHelp,
        rememberedDescription = strings.frogButtonHelp,
        previousLabel = strings.vocabPrev
    )

private val featureTourTargetLevels = listOf("BASIC", "STANDARD", "ADVANCED")

private fun featureTourToeflScore(level: String): String = when (level) {
    "BASIC" -> "60+"
    "STANDARD" -> "80+"
    else -> "100+"
}

private fun featureTourLevelWordCountLabel(strings: AppStrings, count: Int): String {
    val formattedCount = String.format(Locale.US, "%,d", count)
    return if (strings.isJapanese) {
        "${formattedCount}語"
    } else {
        formattedCount
    }
}

private fun toeflText(value: String): String = value
    .replace("Band", "Level")
    .replace("band", "level")

private fun FeatureTourStep.toToefl(): FeatureTourStep = copy(
    title = toeflText(title),
    description = toeflText(description)
)

/**
 * 実操作を促すステップのガイド文言。
 *
 * 「どの単語をどう操作するか」だけを短く伝える。購入の案内は含めず、
 * 初回起動で離脱しないようにする。
 */
private data class FeatureTourPracticeCopy(
    val instruction: String,
    val done: String,
    val autoAdvance: String,
    val holdHint: String,
    val searching: String
)

private fun featureTourPracticeCopy(strings: AppStrings): FeatureTourPracticeCopy = when (strings.languageCode) {
    "ja" -> FeatureTourPracticeCopy(
        instruction = "実際に試してみましょう",
        done = "長押しできました！",
        autoAdvance = "「検索する」まで進めると次の説明に移ります。",
        holdHint = "カードの枠で囲まれた単語を、指で1秒ほど長く押してください。",
        searching = "検索しています…"
    )
    "zh" -> FeatureTourPracticeCopy(
        instruction = "实际试一试吧",
        done = "长按成功！",
        autoAdvance = "继续点击“搜索”即可进入下一步说明。",
        holdHint = "用手指长按卡片中带边框的单词约1秒。",
        searching = "正在搜索…"
    )
    "hi" -> FeatureTourPracticeCopy(
        instruction = "अब खुद आज़माएँ",
        done = "लंबा दबाना हो गया!",
        autoAdvance = "“खोजें” तक पहुँचने पर अगला चरण दिखेगा।",
        holdHint = "कार्ड में बॉर्डर वाले शब्द को लगभग 1 सेकंड तक दबाए रखें।",
        searching = "खोजा जा रहा है…"
    )
    "vi" -> FeatureTourPracticeCopy(
        instruction = "Hãy thử ngay",
        done = "Đã nhấn giữ thành công!",
        autoAdvance = "Nhấn “Tìm kiếm” để chuyển sang bước tiếp theo.",
        holdHint = "Giữ ngón tay khoảng 1 giây lên từ được đóng khung trên thẻ.",
        searching = "Đang tìm kiếm…"
    )
    "ko" -> FeatureTourPracticeCopy(
        instruction = "직접 해 보세요",
        done = "길게 누르기 성공!",
        autoAdvance = "“검색”까지 진행하면 다음 설명으로 넘어갑니다.",
        holdHint = "카드에서 테두리로 표시된 단어를 약 1초 동안 길게 누르세요.",
        searching = "검색 중…"
    )
    "id" -> FeatureTourPracticeCopy(
        instruction = "Coba sendiri",
        done = "Berhasil menekan lama!",
        autoAdvance = "Lanjutkan ke “Cari” untuk berpindah ke penjelasan berikutnya.",
        holdHint = "Tahan jari sekitar 1 detik pada kata yang dibingkai di kartu.",
        searching = "Mencari…"
    )
    "th" -> FeatureTourPracticeCopy(
        instruction = "ลองทำดูจริง ๆ",
        done = "แตะค้างสำเร็จ!",
        autoAdvance = "ไปจนถึง “ค้นหา” แล้วจะเข้าสู่คำอธิบายถัดไป",
        holdHint = "กดนิ้วค้างไว้ประมาณ 1 วินาทีบนคำที่มีกรอบในการ์ด",
        searching = "กำลังค้นหา…"
    )
    "es" -> FeatureTourPracticeCopy(
        instruction = "Pruébalo tú mismo",
        done = "¡Pulsación larga correcta!",
        autoAdvance = "Al llegar a “Buscar” pasarás a la siguiente explicación.",
        holdHint = "Mantén el dedo aproximadamente 1 segundo sobre la palabra enmarcada de la tarjeta.",
        searching = "Buscando…"
    )
    else -> FeatureTourPracticeCopy(
        instruction = "Try it yourself",
        done = "Long press detected!",
        autoAdvance = "Tap “Search” to move on to the next explanation.",
        holdHint = "Hold your finger on the framed word on the card for about one second.",
        searching = "Searching…"
    )
}

private fun dailyTargetSelectionLabel(strings: AppStrings): String = when (strings.languageCode) {
    "ja" -> "1日の学習量を選択"
    "zh" -> "选择每日学习量"
    "hi" -> "दैनिक पढ़ाई की मात्रा चुनें"
    "vi" -> "Chọn lượng học mỗi ngày"
    "ko" -> "하루 학습량 선택"
    "id" -> "Pilih jumlah belajar harian"
    "th" -> "เลือกปริมาณการเรียนต่อวัน"
    "es" -> "Elige tu cantidad diaria de estudio"
    else -> "Choose your daily study amount"
}

private fun dailyTargetLabel(strings: AppStrings, amount: Int): String = when {
    strings.isJapanese -> "$amount 語/日"
    strings.languageCode == "zh" -> "$amount 词/天"
    strings.languageCode == "hi" -> "$amount शब्द / दिन"
    strings.languageCode == "vi" -> "$amount từ / ngày"
    strings.languageCode == "ko" -> "${amount}단어/일"
    strings.languageCode == "id" -> "$amount kata/hari"
    strings.languageCode == "th" -> "$amount คำ/วัน"
    strings.languageCode == "es" -> "$amount palabras/día"
    else -> "$amount words/day"
}

@Composable
private fun FeatureTourTargetBandSelector(
    strings: AppStrings,
    selectedBand: String,
    levelWordCounts: Map<String, Int>,
    premiumUnlocked: Boolean,
    onBandSelected: (String) -> Unit,
    onPremiumLevelClick: () -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Level",
                style = androidx.compose.material3.MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = if (strings.isJapanese) "TOEFL iBTスコアの目安" else "TOEFL iBT score guide",
                style = androidx.compose.material3.MaterialTheme.typography.labelSmall
            )
        }
        featureTourTargetLevels.chunked(2).forEach { rowBands ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                rowBands.forEach { band ->
                    val isPremiumLocked = band == "ADVANCED" && !premiumUnlocked
                    val wordCount = levelWordCounts[band]
                    FilterChip(
                        selected = selectedBand == band && !isPremiumLocked,
                        onClick = {
                            if (isPremiumLocked) onPremiumLevelClick() else onBandSelected(band)
                        },
                        label = {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    (if (isPremiumLocked) "🔒 " else "") +
                                        featureTourToeflScore(band) +
                                        if (wordCount != null && wordCount > 0) {
                                            " (${featureTourLevelWordCountLabel(strings, wordCount)})"
                                        } else {
                                            ""
                                        }
                                )
                            }
                        },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

@Composable
private fun FeatureTourDailyTargetSelector(
    strings: AppStrings,
    selectedTarget: Int,
    options: List<Int>,
    onTargetSelected: (Int) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(
            text = dailyTargetSelectionLabel(strings),
            style = androidx.compose.material3.MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Bold
        )
        options.chunked(2).forEach { rowOptions ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                rowOptions.forEach { amount ->
                    FilterChip(
                        selected = selectedTarget == amount,
                        onClick = { onTargetSelected(amount) },
                        label = { Text(dailyTargetLabel(strings, amount)) },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

fun mainFeatureTourSteps(strings: AppStrings): List<FeatureTourStep> = (when (strings.languageCode) {
    "ja" -> listOf(
        FeatureTourStep("frog_header", "カエルアイコン", "タップすると、単語カードや画面の状態を起動時の状態に戻します。"),
        FeatureTourStep("accent_button", "発音アクセント", "アメリカ英語とイギリス英語の発音を切り替えます。"),
        FeatureTourStep("sound_button", "音声ボタン", "単語の発音とカード操作音をオン／オフにします。"),
        FeatureTourStep("settings_button", "設定", "表示言語、バックアップ、レストアを管理します。"),
        FeatureTourStep("progress_section", "学習進捗", "未マスター、総単語数、お気に入り、マスター済みの単語数を確認できます。"),
        FeatureTourStep("progress_search", "学習進捗の検索", "虫眼鏡をタップすると、単語名や意味から単語を検索できます。見つけた単語は単語カードで確認できます。"),
        FeatureTourStep("level_filter", "レベル（TOEFL）", "単語をTOEFLの学習レベル別に絞り込めます。下のスコアを目安に選択でき、100+はプレミアム機能です。"),
        FeatureTourStep("streak_area", "ストリーク", "ここをタップすると、連続学習日数の詳細や、ストリークを続けるためのヒントを確認できます。途切れたストリークの救済もできます。"),
        FeatureTourStep("daily_goal", "今日の学習と1日の目標", "今日の学習状況を確認できます。下の選択肢から1日の学習量を設定できます。"),
        FeatureTourStep("flashcard_tab", "単語カード", "カードをタップすると意味・例文・コロケーションが表示されます。"),
        FeatureTourStep("flashcard_area", "長押しメニュー", "説明が表示されているときに単語を長押しすると、検索・発音・コピーができます。下のガイドの単語を実際に長押しして、「検索する」を押してみましょう。短くタップすると説明を閉じます。", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "カードの操作", "◀で前の単語に戻り、「お気に入り」「マスター」で学習結果を記録します。"),
        FeatureTourStep("flashcard_area", "左右スワイプ", "右にスワイプ：「マスター」ボタンと同じ処理をします。\n左にスワイプ：⭐️「お気に入り」ボタンと同じ処理をします。"),
        FeatureTourStep("favorites_tab", "お気に入りタブ", "お気に入りに登録した単語を確認できます。"),
        FeatureTourStep("heatmap_area", "履歴タブ", "履歴タブでは、学習ヒートマップとこれまでの学習履歴を確認できます。"),
        FeatureTourStep("ai_tab", "AI会話", "ChatGPTまたはGeminiを起動して、発音・会話練習を始めます。")
    )
    "zh" -> listOf(
        FeatureTourStep("frog_header", "青蛙图标", "点击可将单词卡和画面状态恢复到初始状态。"),
        FeatureTourStep("accent_button", "发音口音", "在英式英语和美式英语的发音之间切换。"),
        FeatureTourStep("sound_button", "声音按钮", "开启或关闭单词发音和卡片操作音。"),
        FeatureTourStep("settings_button", "设置", "管理显示语言、备份和恢复。"),
        FeatureTourStep("progress_section", "学习进度", "查看未掌握、单词总数、收藏和已掌握的单词数量。"),
        FeatureTourStep("progress_search", "搜索学习进度", "点击放大镜，可以按单词或释义搜索词汇。找到的单词可以在单词卡中查看。"),
        FeatureTourStep("level_filter", "级别（TOEFL）", "可以按 TOEFL 学习级别筛选单词，可根据下方分数进行选择。100+ 是高级版功能。"),
        FeatureTourStep("streak_area", "连续学习", "点击这里可查看连续学习详情和保持连续学习的提示。连续学习中断后也可以进行挽救。"),
        FeatureTourStep("daily_goal", "今日学习和每日目标", "查看今日学习情况，并从下方选项设置每日学习量。"),
        FeatureTourStep("flashcard_tab", "单词卡", "点击卡片可显示释义、例句和搭配。"),
        FeatureTourStep("flashcard_area", "长按菜单", "显示释义时长按单词，可以搜索、朗读或复制。请实际长按下方指南中的单词，然后点击“搜索”。短按可关闭释义。", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "卡片操作", "使用◀返回上一个单词，并用“收藏”和“记住了”记录学习结果。"),
        FeatureTourStep("flashcard_area", "左右滑动", "向右滑动：与“记住了”按钮执行相同操作。\n向左滑动：与⭐️“收藏”按钮执行相同操作。"),
        FeatureTourStep("favorites_tab", "收藏夹选项卡", "查看你收藏的单词。"),
        FeatureTourStep("heatmap_area", "历史记录选项卡", "在历史记录选项卡中查看学习热力图和学习历史。"),
        FeatureTourStep("ai_tab", "AI 对话", "启动 ChatGPT 或 Gemini，开始发音和对话练习。")
    )
    "hi" -> listOf(
        FeatureTourStep("frog_header", "मेंढक आइकन", "इसे टैप करके शब्द कार्ड और स्क्रीन की स्थिति को शुरुआती स्थिति में लौटाएँ।"),
        FeatureTourStep("accent_button", "उच्चारण ऐक्सेंट", "ब्रिटिश और अमेरिकी अंग्रेज़ी के उच्चारण के बीच बदलें।"),
        FeatureTourStep("sound_button", "ध्वनि बटन", "शब्दों का उच्चारण और कार्ड बटन की ध्वनि चालू या बंद करें।"),
        FeatureTourStep("settings_button", "सेटिंग्स", "ऐप की भाषा, बैकअप और पुनर्स्थापना प्रबंधित करें।"),
        FeatureTourStep("progress_section", "पढ़ाई की प्रगति", "अभी तक पूरी तरह न सीखे गए, कुल, पसंदीदा और पूरी तरह सीखे गए शब्दों की संख्या देखें।"),
        FeatureTourStep("progress_search", "पढ़ाई की प्रगति खोजें", "आवर्धक लेंस पर टैप करके शब्द या अर्थ से शब्द खोजें। मिले हुए शब्द को शब्द कार्ड में देखें।"),
        FeatureTourStep("level_filter", "स्तर (TOEFL)", "शब्दों को TOEFL सीखने के स्तर के अनुसार फ़िल्टर करें। नीचे दिए गए स्कोर के आधार पर चुनें। 100+ प्रीमियम सुविधा है।"),
        FeatureTourStep("streak_area", "स्ट्रीक", "यहाँ टैप करके लगातार पढ़ाई की जानकारी और स्ट्रीक बनाए रखने के सुझाव देखें। स्ट्रीक टूटने पर उसे बचाने का विकल्प भी उपलब्ध है।"),
        FeatureTourStep("daily_goal", "आज की पढ़ाई और दैनिक लक्ष्य", "आज की पढ़ाई देखें और नीचे दिए गए विकल्पों से दैनिक पढ़ाई की मात्रा चुनें।"),
        FeatureTourStep("flashcard_tab", "शब्द कार्ड", "अर्थ, उदाहरण और संयोजन देखने के लिए कार्ड टैप करें।"),
        FeatureTourStep("flashcard_area", "लॉन्ग-प्रेस मेनू", "अर्थ दिखने पर किसी शब्द को लंबे समय तक दबाकर खोजें, उसका उच्चारण सुनें या उसे कॉपी करें। नीचे दिए गाइड के शब्द को असल में लंबा दबाएँ और फिर “खोजें” दबाएँ। छोटा टैप अर्थ को बंद करता है।", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "कार्ड की क्रियाएँ", "◀ से पिछले शब्द पर लौटें; सीखने का परिणाम दर्ज करने के लिए “पसंदीदा” और “याद रहा” का उपयोग करें।"),
        FeatureTourStep("flashcard_area", "बाएँ-दाएँ स्वाइप", "दाईं ओर स्वाइप: नीचे दिए गए ‘याद रहा’ बटन जैसा कार्य।\nबाईं ओर स्वाइप: ⭐️ ‘पसंदीदा’ बटन जैसा कार्य।"),
        FeatureTourStep("favorites_tab", "पसंदीदा टैब", "पसंदीदा में जोड़े गए शब्द देखें।"),
        FeatureTourStep("heatmap_area", "इतिहास टैब", "इतिहास टैब में पढ़ाई का हीटमैप और अपना अध्ययन इतिहास देखें।"),
        FeatureTourStep("ai_tab", "AI बातचीत", "उच्चारण और बातचीत का अभ्यास शुरू करने के लिए ChatGPT या Gemini खोलें।")
    )
    "vi" -> listOf(
        FeatureTourStep("frog_header", "Biểu tượng con ếch", "Chạm để đưa thẻ từ và trạng thái màn hình về trạng thái ban đầu."),
        FeatureTourStep("accent_button", "Giọng phát âm", "Chuyển đổi phát âm giữa tiếng Anh Anh và tiếng Anh Mỹ."),
        FeatureTourStep("sound_button", "Nút âm thanh", "Bật hoặc tắt phát âm từ và âm thanh của các nút trên thẻ."),
        FeatureTourStep("settings_button", "Cài đặt", "Quản lý ngôn ngữ hiển thị, sao lưu và khôi phục."),
        FeatureTourStep("progress_section", "Tiến độ học", "Xem số từ chưa thành thạo, tổng số từ, số từ yêu thích và số từ đã thành thạo."),
        FeatureTourStep("progress_search", "Tìm kiếm trong tiến độ học", "Chạm vào kính lúp để tìm từ theo từ vựng hoặc nghĩa. Từ tìm được có thể xem trong thẻ từ."),
        FeatureTourStep("level_filter", "Cấp độ (TOEFL)", "Lọc từ vựng theo cấp độ học TOEFL. Chọn theo các mức điểm bên dưới. 100+ là tính năng Premium."),
        FeatureTourStep("streak_area", "Chuỗi ngày học", "Chạm vào đây để xem chi tiết chuỗi ngày học và mẹo duy trì chuỗi. Bạn cũng có thể khôi phục chuỗi khi bị gián đoạn."),
        FeatureTourStep("daily_goal", "Việc học hôm nay và mục tiêu hằng ngày", "Xem tiến độ hôm nay và chọn lượng học mỗi ngày ở các lựa chọn bên dưới."),
        FeatureTourStep("flashcard_tab", "Thẻ từ", "Chạm vào thẻ để xem nghĩa, câu ví dụ và các kết hợp từ."),
        FeatureTourStep("flashcard_area", "Menu nhấn giữ", "Khi phần giải thích hiện ra, nhấn giữ một từ để tìm kiếm, nghe phát âm hoặc sao chép. Hãy thực sự nhấn giữ từ trong hướng dẫn bên dưới, rồi nhấn “Tìm kiếm”. Chạm nhanh để đóng phần giải thích.", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "Thao tác với thẻ", "Dùng ◀ để quay lại từ trước; dùng Yêu thích và Nhớ để ghi lại kết quả học."),
        FeatureTourStep("flashcard_area", "Vuốt sang trái hoặc phải", "Vuốt sang phải: giống nút “Nhớ” ở chân thẻ.\nVuốt sang trái: giống nút ⭐️ “Yêu thích”."),
        FeatureTourStep("favorites_tab", "Tab yêu thích", "Xem các từ bạn đã đánh dấu yêu thích."),
        FeatureTourStep("heatmap_area", "Tab lịch sử", "Trong tab lịch sử, hãy xem bản đồ nhiệt học tập và lịch sử học tập."),
        FeatureTourStep("ai_tab", "Hội thoại AI", "Mở ChatGPT hoặc Gemini để luyện phát âm và hội thoại.")
    )
    "ko" -> listOf(
        FeatureTourStep("frog_header", "개구리 아이콘", "탭하면 단어 카드와 화면 상태를 시작 상태로 되돌립니다."),
        FeatureTourStep("accent_button", "발음 악센트", "영국식 영어와 미국식 영어의 발음을 전환합니다."),
        FeatureTourStep("sound_button", "소리 버튼", "단어 발음과 카드 조작음을 켜거나 끕니다."),
        FeatureTourStep("settings_button", "설정", "표시 언어, 백업 및 복원을 관리합니다."),
        FeatureTourStep("progress_section", "학습 진행률", "아직 마스터하지 않은 단어, 전체 단어 수, 즐겨찾기와 마스터한 단어 수를 확인하세요."),
        FeatureTourStep("progress_search", "학습 진행률 검색", "돋보기를 탭하면 단어나 뜻으로 단어를 검색할 수 있습니다. 찾은 단어는 단어 카드에서 확인할 수 있습니다."),
        FeatureTourStep("level_filter", "레벨 (TOEFL)", "TOEFL 학습 레벨별로 단어를 필터링할 수 있습니다. 아래 점수를 기준으로 선택하며 100+는 프리미엄 기능입니다."),
        FeatureTourStep("streak_area", "연속 학습", "여기를 탭해 연속 학습 상세 정보와 연속 학습을 유지하는 팁을 확인하세요. 연속 학습이 끊겼을 때 복구할 수도 있습니다."),
        FeatureTourStep("daily_goal", "오늘 학습과 일일 목표", "오늘의 학습 상황을 확인하고 아래 선택지에서 하루 학습량을 설정하세요."),
        FeatureTourStep("flashcard_tab", "단어 카드", "카드를 탭하면 뜻, 예문, 연어가 표시됩니다."),
        FeatureTourStep("flashcard_area", "길게 누르기 메뉴", "뜻이 표시될 때 단어를 길게 누르면 검색하거나 발음을 듣고 복사할 수 있습니다. 아래 안내의 단어를 실제로 길게 누른 뒤 “검색”을 눌러 보세요. 짧게 탭하면 뜻이 닫힙니다.", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "카드 조작", "◀로 이전 단어로 돌아가고, 즐겨찾기·기억함으로 학습 결과를 기록합니다."),
        FeatureTourStep("flashcard_area", "좌우 스와이프", "오른쪽으로 스와이프: 하단의 ‘기억함’ 버튼과 같은 동작.\n왼쪽으로 스와이프: ⭐️ ‘즐겨찾기’ 버튼과 같은 동작."),
        FeatureTourStep("favorites_tab", "즐겨찾기 탭", "즐겨찾기에 추가한 단어를 확인합니다."),
        FeatureTourStep("heatmap_area", "기록 탭", "기록 탭에서 학습 히트맵과 학습 기록을 확인합니다."),
        FeatureTourStep("ai_tab", "AI 대화", "ChatGPT 또는 Gemini를 열어 발음과 대화를 연습합니다.")
    )
    "id" -> listOf(
        FeatureTourStep("frog_header", "Ikon katak", "Ketuk untuk mengembalikan kartu dan keadaan layar ke tampilan awal."),
        FeatureTourStep("accent_button", "Aksen pengucapan", "Beralih antara pengucapan bahasa Inggris Britania dan Amerika."),
        FeatureTourStep("sound_button", "Tombol suara", "Nyalakan atau matikan pengucapan kata dan suara tombol kartu."),
        FeatureTourStep("settings_button", "Pengaturan", "Kelola bahasa tampilan, pencadangan, dan pemulihan."),
        FeatureTourStep("progress_section", "Kemajuan belajar", "Lihat jumlah kata yang belum dikuasai, total kata, favorit, dan telah dikuasai."),
        FeatureTourStep("progress_search", "Pencarian kemajuan belajar", "Ketuk kaca pembesar untuk mencari kata berdasarkan kata atau artinya. Kata yang ditemukan dapat dilihat di kartu kata."),
        FeatureTourStep("level_filter", "Level (TOEFL)", "Saring kata berdasarkan level belajar TOEFL. Pilih berdasarkan skor di bawah ini. 100+ adalah fitur Premium."),
        FeatureTourStep("streak_area", "Streak belajar", "Ketuk di sini untuk melihat detail dan tips mempertahankan streak belajar. Anda juga dapat memulihkan streak yang terputus."),
        FeatureTourStep("daily_goal", "Belajar hari ini dan target harian", "Lihat kemajuan hari ini dan pilih jumlah kata yang dipelajari setiap hari dari opsi di bawah."),
        FeatureTourStep("flashcard_tab", "Kartu kata", "Ketuk kartu untuk melihat arti, contoh kalimat, dan kolokasi."),
        FeatureTourStep("flashcard_area", "Menu tekan lama", "Saat arti ditampilkan, tekan lama sebuah kata untuk mencari, mendengarkan pengucapannya, atau menyalinnya. Tekan lama kata pada panduan di bawah, lalu tekan “Cari”. Ketuk singkat untuk menutup arti.", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "Tindakan kartu", "Gunakan ◀ untuk kembali ke kata sebelumnya, lalu gunakan Favorit dan Ingat untuk mencatat hasil belajar."),
        FeatureTourStep("flashcard_area", "Geser ke kiri atau kanan", "Geser ke kanan: sama seperti tombol “Ingat” di bagian bawah kartu.\nGeser ke kiri: sama seperti tombol ⭐️ “Favorit”."),
        FeatureTourStep("favorites_tab", "Tab favorit", "Lihat kata yang Anda tandai sebagai favorit."),
        FeatureTourStep("heatmap_area", "Tab riwayat", "Di tab riwayat, lihat peta panas belajar dan riwayat belajar Anda."),
        FeatureTourStep("ai_tab", "Percakapan AI", "Buka ChatGPT atau Gemini untuk berlatih pengucapan dan percakapan.")
    )
    "th" -> listOf(
        FeatureTourStep("frog_header", "ไอคอนกบ", "แตะเพื่อคืนการ์ดคำศัพท์และสถานะหน้าจอกลับสู่สถานะเริ่มต้น"),
        FeatureTourStep("accent_button", "สำเนียงการออกเสียง", "สลับการออกเสียงระหว่างภาษาอังกฤษแบบบริติชและอเมริกัน"),
        FeatureTourStep("sound_button", "ปุ่มเสียง", "เปิดหรือปิดเสียงอ่านคำศัพท์และเสียงปุ่มบนการ์ด"),
        FeatureTourStep("settings_button", "การตั้งค่า", "จัดการภาษาที่แสดง การสำรองข้อมูล และการกู้คืน"),
        FeatureTourStep("progress_section", "ความคืบหน้าการเรียน", "ดูจำนวนคำที่ยังไม่เชี่ยวชาญ จำนวนคำทั้งหมด คำโปรด และคำที่เชี่ยวชาญแล้ว"),
        FeatureTourStep("progress_search", "ค้นหาในความคืบหน้าการเรียน", "แตะไอคอนแว่นขยายเพื่อค้นหาคำศัพท์จากคำหรือความหมาย คำที่พบจะเปิดดูได้ในการ์ดคำศัพท์"),
        FeatureTourStep("level_filter", "ระดับ (TOEFL)", "กรองคำศัพท์ตามระดับการเรียน TOEFL ได้ เลือกตามคะแนนด้านล่าง โดย 100+ เป็นฟีเจอร์พรีเมียม"),
        FeatureTourStep("streak_area", "การเรียนต่อเนื่อง", "แตะที่นี่เพื่อดูรายละเอียดและเคล็ดลับรักษาสตรีคการเรียน และกู้คืนสตรีคที่ขาดช่วงได้"),
        FeatureTourStep("daily_goal", "การเรียนวันนี้และเป้าหมายรายวัน", "ดูความคืบหน้าวันนี้และเลือกปริมาณการเรียนต่อวันจากตัวเลือกด้านล่าง"),
        FeatureTourStep("flashcard_tab", "การ์ดคำศัพท์", "แตะการ์ดเพื่อดูความหมาย ตัวอย่างประโยค และวลีที่ใช้ร่วมกัน"),
        FeatureTourStep("flashcard_area", "เมนูแตะค้าง", "เมื่อแสดงความหมาย ให้แตะค้างที่คำศัพท์เพื่อค้นหา ฟังการออกเสียง หรือคัดลอก ลองแตะค้างคำในคำแนะนำด้านล่าง แล้วกด “ค้นหา” แตะสั้นเพื่อปิดความหมาย", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "การควบคุมการ์ด", "ใช้ ◀ เพื่อกลับไปคำก่อนหน้า และใช้ รายการโปรด กับจำได้ เพื่อบันทึกผลการเรียน"),
        FeatureTourStep("flashcard_area", "ปัดไปทางซ้ายหรือขวา", "ปัดไปทางขวา: เหมือนปุ่ม “จำได้” ด้านล่างการ์ด\nปัดไปทางซ้าย: เหมือนปุ่ม ⭐️ “รายการโปรด”"),
        FeatureTourStep("favorites_tab", "แท็บรายการโปรด", "ดูคำศัพท์ที่เพิ่มไว้ในรายการโปรด"),
        FeatureTourStep("heatmap_area", "แท็บประวัติ", "ดูฮีตแมปการเรียนรู้และประวัติการเรียนได้ในแท็บประวัติ"),
        FeatureTourStep("ai_tab", "การสนทนากับ AI", "เปิด ChatGPT หรือ Gemini เพื่อฝึกออกเสียงและสนทนา")
    )
    "es" -> listOf(
        FeatureTourStep("frog_header", "Icono de rana", "Tócalo para devolver las tarjetas y el estado de la pantalla al inicio."),
        FeatureTourStep("accent_button", "Acento de pronunciación", "Cambia la pronunciación entre el inglés británico y el estadounidense."),
        FeatureTourStep("sound_button", "Botón de sonido", "Activa o desactiva la pronunciación de las palabras y los sonidos de los botones."),
        FeatureTourStep("settings_button", "Ajustes", "Gestiona el idioma de pantalla, las copias de seguridad y la restauración."),
        FeatureTourStep("progress_section", "Progreso de aprendizaje", "Consulta el número de palabras no dominadas, el total de palabras, las favoritas y las dominadas."),
        FeatureTourStep("progress_search", "Buscar en el progreso de aprendizaje", "Toca la lupa para buscar palabras por su palabra o significado. Puedes consultar el resultado en la tarjeta de palabra."),
        FeatureTourStep("level_filter", "Nivel (TOEFL)", "Filtra las palabras por nivel de aprendizaje del TOEFL. Elige según las puntuaciones de abajo. 100+ es una función premium."),
        FeatureTourStep("streak_area", "Racha de estudio", "Toca aquí para consultar los detalles y consejos para mantener tu racha. También puedes recuperar una racha interrumpida."),
        FeatureTourStep("daily_goal", "Estudio de hoy y objetivo diario", "Consulta tu progreso de hoy y elige tu cantidad diaria de estudio entre las opciones de abajo."),
        FeatureTourStep("flashcard_tab", "Tarjeta de palabra", "Toca la tarjeta para ver el significado, ejemplos y colocaciones."),
        FeatureTourStep("flashcard_area", "Menú de pulsación larga", "Cuando se muestre el significado, mantén pulsada una palabra para buscarla, escuchar su pronunciación o copiarla. Mantén pulsada la palabra de la guía de abajo y luego toca “Buscar”. Toca brevemente para cerrar el significado.", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "Acciones de la tarjeta", "Usa ◀ para volver a la palabra anterior y Favorita y Recordada para registrar tu resultado."),
        FeatureTourStep("flashcard_area", "Deslizar a izquierda o derecha", "Deslizar a la derecha: igual que el botón “Recordada” de la parte inferior.\nDeslizar a la izquierda: igual que el botón ⭐️ “Favoritos”."),
        FeatureTourStep("favorites_tab", "Pestaña de favoritos", "Consulta las palabras que marcaste como favoritas."),
        FeatureTourStep("heatmap_area", "Pestaña de historial", "En la pestaña de historial, consulta el mapa de calor de estudio y tu historial de aprendizaje."),
        FeatureTourStep("ai_tab", "Conversación con IA", "Abre ChatGPT o Gemini para practicar pronunciación y conversación.")
    )
    "en" -> listOf(
        FeatureTourStep("frog_header", "Frog icon", "Tap to reset the flashcards and screen state to their starting state."),
        FeatureTourStep("accent_button", "Pronunciation accent", "Switch between British and American English pronunciation."),
        FeatureTourStep("sound_button", "Sound button", "Turn word pronunciation and card button sounds on or off."),
        FeatureTourStep("settings_button", "Settings", "Manage the display language, backup, and restore."),
        FeatureTourStep("progress_section", "Learning progress", "See the number of words not yet mastered, the total number of words, the number of favorites, and the number of mastered words."),
        FeatureTourStep("progress_search", "Search learning progress", "Tap the magnifying glass to search for words by word or meaning. Open a result in its flashcard."),
        FeatureTourStep("level_filter", "Level (TOEFL)", "Filter words by TOEFL learning level. Choose from the score guides below. 100+ is a premium feature."),
        FeatureTourStep("streak_area", "Study streak", "Tap here to view streak details and tips for keeping your streak going. You can also recover an interrupted streak."),
        FeatureTourStep("daily_goal", "Today's study and daily goal", "View today's progress and choose your daily study amount from the options below."),
        FeatureTourStep("flashcard_tab", "Flashcard", "Tap a card to see its meaning, example sentence, and collocations."),
        FeatureTourStep("flashcard_area", "Long-press menu", "When the explanation is shown, long-press a word to search for it, hear its pronunciation, or copy it. Long-press the word in the guide below, then tap “Search”. Tap briefly to hide the explanation.", stepId = FeatureTourStepId.LONG_PRESS_MENU),
        FeatureTourStep("flashcard_buttons", "Card controls", "Use ◀ to return to the previous word, and Favorite and Remembered to record your result."),
        FeatureTourStep("flashcard_area", "Swipe left or right", "Swipe right: same action as the “Remembered” button in the footer.\nSwipe left: same action as the ⭐️ “Favorite” button."),
        FeatureTourStep("favorites_tab", "Favorites tab", "View your favorite words."),
        FeatureTourStep("heatmap_area", "History tab", "In the History tab, view the study heatmap and your learning history."),
        FeatureTourStep("ai_tab", "AI conversation", "Open ChatGPT or Gemini to practice pronunciation and conversation.")
    )
    else -> mainFeatureTourSteps(strings.copy(isJapanese = false, languageCode = "en"))
}).map { it.toToefl() }

@Composable
fun FeatureTourOverlay(
    visible: Boolean,
    state: FeatureTourState,
    steps: List<FeatureTourStep>,
    copy: FeatureTourCopy,
    strings: AppStrings,
    buttonHelp: FlashcardButtonHelpCopy? = null,
    selectedTargetBand: String = "BASIC",
    levelWordCounts: Map<String, Int> = emptyMap(),
    premiumUnlocked: Boolean = true,
    onTargetBandSelected: (String) -> Unit = {},
    onPremiumLevelClick: () -> Unit = {},
    selectedDailyTarget: Int = 5,
    dailyTargetOptions: List<Int> = emptyList(),
    onDailyTargetSelected: (Int) -> Unit = {},
    /** 実操作ステップで検索ダイアログを開いたか（「検索する」まで進んだか）。 */
    practiceSearching: Boolean = false,
    /**
     * 実操作ステップのガイド上で、案内した単語が長押しされたときに呼ばれる。
     * 単語カードが説明カードに隠れていても操作を体験できるようにする。
     */
    onPracticeWordLongPressed: (String) -> Unit = {},
    stepIndex: Int,
    onStepIndexChange: (Int) -> Unit,
    onFinished: () -> Unit,
    onSkipped: () -> Unit = onFinished
) {
    if (!visible || steps.isEmpty()) return

    val step = steps[stepIndex.coerceIn(0, steps.lastIndex)]
    val target = state.boundsFor(step.targetKey)
    val highlightColor = if (step.targetKey == "heatmap_area") {
        Color(0xFFE53935)
    } else {
        MaterialTheme.colorScheme.primary
    }
    val density = LocalDensity.current

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .zIndex(20f)
    ) {
        // 下部にある操作対象（カード操作・タブなど）は、説明を上部へ移す。
        // 上部のヘッダーや進捗カードは、説明を下部へ置く。
        // 長押しメニューの実操作ステップは、操作する単語がカード上部にあるため説明を下部へ置く。
        val rootHeightPx = with(density) { maxHeight.toPx() }
        val placeDialogAtTop = if (step.targetKey == "heatmap_area" || step.hasPractice) {
            false
        } else {
            target?.bottom?.let { it > rootHeightPx * 0.55f } == true
        }

        Canvas(modifier = Modifier.fillMaxSize()) {
            drawRect(Color.Black.copy(alpha = 0.64f))
            target?.let {
                drawRoundRect(
                    color = highlightColor,
                    topLeft = it.topLeft,
                    size = it.size,
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(12f, 12f),
                    style = Stroke(width = 5f)
                )
            }
        }

        Card(
            modifier = Modifier
                .align(if (placeDialogAtTop) Alignment.TopCenter else Alignment.BottomCenter)
                .fillMaxWidth()
                .then(
                    if (placeDialogAtTop) {
                        Modifier
                            .windowInsetsPadding(
                                WindowInsets.safeDrawing.only(WindowInsetsSides.Top)
                            )
                            .padding(top = 12.dp)
                    } else {
                        Modifier
                            .navigationBarsPadding()
                            .padding(bottom = 16.dp)
                    }
                )
                .padding(horizontal = 16.dp),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 10.dp)
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Text(copy.mainTitle, style = MaterialTheme.typography.titleLarge, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                Text(
                    text = "${copy.step} ${stepIndex + 1}/${steps.size}",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                LinearProgressIndicator(
                    progress = { (stepIndex + 1f) / steps.size },
                    modifier = Modifier.fillMaxWidth()
                )
                if (stepIndex == 0) {
                    Text(copy.mainIntro, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Text(step.title, style = MaterialTheme.typography.titleMedium, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                if (step.targetKey == "flashcard_buttons" && buttonHelp != null) {
                    FlashcardButtonHelpGuide(buttonHelp)
                } else {
                    Text(step.description, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                if (step.hasPractice) {
                    FeatureTourPracticeGuide(
                        step = step,
                        state = state,
                        strings = strings,
                        searching = practiceSearching,
                        onWordLongPressed = onPracticeWordLongPressed
                    )
                }
                if (step.targetKey == "level_filter") {
                    FeatureTourTargetBandSelector(
                        strings = strings,
                        selectedBand = selectedTargetBand,
                        levelWordCounts = levelWordCounts,
                        premiumUnlocked = premiumUnlocked,
                        onBandSelected = onTargetBandSelected,
                        onPremiumLevelClick = onPremiumLevelClick
                    )
                }
                if (step.targetKey == "daily_goal" && dailyTargetOptions.isNotEmpty()) {
                    FeatureTourDailyTargetSelector(
                        strings = strings,
                        selectedTarget = selectedDailyTarget,
                        options = dailyTargetOptions,
                        onTargetSelected = onDailyTargetSelected
                    )
                }
                Spacer(modifier = Modifier.height(2.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedButton(onClick = onSkipped) {
                        Text(copy.skip, style = MaterialTheme.typography.labelSmall)
                    }
                    if (stepIndex > 0) {
                        OutlinedButton(onClick = { onStepIndexChange(stepIndex - 1) }, modifier = Modifier.weight(1f)) {
                            Text("◀", style = MaterialTheme.typography.labelSmall)
                        }
                    } else {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                    Button(
                        onClick = {
                            if (stepIndex == steps.lastIndex) onFinished()
                            else onStepIndexChange(stepIndex + 1)
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            if (stepIndex == steps.lastIndex) copy.finish else "▶",
                            style = MaterialTheme.typography.labelSmall
                        )
                    }
                }
            }
        }
    }
}

/** チュートリアル内でフッターのカード操作ボタンと説明を対応づけて表示する。 */
@Composable
private fun FlashcardButtonHelpGuide(help: FlashcardButtonHelpCopy) {
    Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
        FlashcardButtonHelpRow(
            description = help.previousDescription,
            containerColor = MaterialTheme.colorScheme.primary
        ) {
            Text(
                text = help.previousLabel,
                maxLines = 1,
                style = MaterialTheme.typography.labelSmall
            )
        }
        FlashcardButtonHelpRow(
            description = help.forgotDescription,
            containerColor = MaterialTheme.colorScheme.primary
        ) {
            Icon(
                imageVector = Icons.Filled.Star,
                contentDescription = null,
                modifier = Modifier.size(24.dp)
            )
        }
        FlashcardButtonHelpRow(
            description = help.rememberedDescription,
            containerColor = MaterialTheme.colorScheme.primary
        ) {
            Image(
                painter = painterResource(R.drawable.mastery_blue_frog),
                contentDescription = null,
                modifier = Modifier.size(30.dp)
            )
        }
    }
}

@Composable
private fun FlashcardButtonHelpRow(
    description: String,
    containerColor: Color,
    content: @Composable RowScope.() -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Button(
            onClick = {},
            modifier = Modifier.width(88.dp),
            colors = ButtonDefaults.buttonColors(containerColor = containerColor),
            contentPadding = PaddingValues(horizontal = 2.dp, vertical = 5.dp),
            content = content
        )
        Text(
            text = description,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Medium
        )
    }
}

/**
 * 実操作（長押しなど）を促すステップのガイド。
 *
 * 操作対象の単語を提示し、[FeatureTourState.actionCountFor] が 1 以上になると
 * 完了チェックに切り替わる。説明カードの背景に埋もれないよう、ガイドは
 * 単語カードと同じ配色（primary 背景 + onPrimary 文字）で強調する。
 *
 * 単語カードは説明カードの背面にあり指が届かないことがあるため、ここに表示した
 * 単語自体も長押しできるようにして、単語カードを長押ししたのと同じ操作にする。
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun FeatureTourPracticeGuide(
    step: FeatureTourStep,
    state: FeatureTourState,
    strings: AppStrings,
    searching: Boolean,
    onWordLongPressed: (String) -> Unit
) {
    val word = step.practiceWord ?: return
    val practiceCopy = featureTourPracticeCopy(strings)
    val completed = step.practiceKey?.let { state.actionCountFor(it) > 0 } == true
    // 背景は primary、文字は onPrimary にして、説明カードの上でも確実に読めるようにする。
    val containerColor = if (completed) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.primaryContainer
    }
    val onContainerColor = if (completed) {
        MaterialTheme.colorScheme.onPrimary
    } else {
        MaterialTheme.colorScheme.onPrimaryContainer
    }

    Card(
        colors = CardDefaults.cardColors(containerColor = containerColor),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Text(
                text = "${if (completed) "✅" else "👉"} ${practiceCopy.instruction}",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold,
                color = onContainerColor
            )
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = onContainerColor.copy(alpha = 0.18f)
                ),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = word,
                    modifier = Modifier
                        .fillMaxWidth()
                        .combinedClickable(
                            onClick = {},
                            onLongClick = {
                                // 単語カードを長押ししたのと同じ動作にする。
                                onWordLongPressed(word)
                            }
                        )
                        .padding(horizontal = 8.dp, vertical = 10.dp),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = onContainerColor,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }
            Text(
                text = when {
                    completed -> practiceCopy.done
                    searching -> practiceCopy.searching
                    else -> practiceCopy.holdHint
                },
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = onContainerColor
            )
            Text(
                text = practiceCopy.autoAdvance,
                style = MaterialTheme.typography.labelSmall,
                color = onContainerColor.copy(alpha = 0.85f)
            )
        }
    }
}

@Composable
fun SettingsTourOverlay(
    visible: Boolean,
    state: FeatureTourState,
    steps: List<FeatureTourStep>,
    copy: FeatureTourCopy,
    stepIndex: Int,
    onStepIndexChange: (Int) -> Unit,
    onDismiss: () -> Unit
) {
    if (!visible || steps.isEmpty()) return

    val step = steps[stepIndex.coerceIn(0, steps.lastIndex)]
    val highlightColor = MaterialTheme.colorScheme.primary
    val density = LocalDensity.current
    val navigationBarHeight = with(density) {
        WindowInsets.navigationBars.getBottom(this).toDp()
    }
    val bottomSafePadding = maxOf(48.dp, navigationBarHeight)
    var overlayBounds by remember { mutableStateOf<Rect?>(null) }
    val target = state.boundsFor(step.targetKey)?.let { rootTarget ->
        overlayBounds?.let { rootOverlay ->
            Rect(
                left = rootTarget.left - rootOverlay.left,
                top = rootTarget.top - rootOverlay.top,
                right = rootTarget.right - rootOverlay.left,
                bottom = rootTarget.bottom - rootOverlay.top
            )
        }
    }

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .navigationBarsPadding()
            .padding(bottom = bottomSafePadding)
            .zIndex(20f)
            .onGloballyPositioned { coordinates ->
                overlayBounds = coordinates.boundsInRoot()
            }
    ) {
        val rootHeightPx = with(density) { maxHeight.toPx() }
        val placeDialogAtTop = target?.bottom?.let { it > rootHeightPx * 0.55f } == true

        Canvas(modifier = Modifier.fillMaxSize()) {
            drawRect(Color.Black.copy(alpha = 0.64f))
            target?.let {
                drawRoundRect(
                    color = highlightColor,
                    topLeft = it.topLeft,
                    size = it.size,
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(12f, 12f),
                    style = Stroke(width = 5f)
                )
            }
        }

        Card(
            modifier = Modifier
                .align(if (placeDialogAtTop) Alignment.TopCenter else Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(horizontal = 16.dp)
                .then(
                    if (placeDialogAtTop) {
                        Modifier
                            .windowInsetsPadding(
                                WindowInsets.safeDrawing.only(WindowInsetsSides.Top)
                            )
                            .padding(top = 8.dp)
                    } else {
                        Modifier.padding(vertical = 8.dp)
                    }
                ),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 10.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(copy.settingsTitle, style = MaterialTheme.typography.titleLarge, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                Text(
                    text = "${copy.step} ${stepIndex + 1}/${steps.size}",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                LinearProgressIndicator(
                    progress = { (stepIndex + 1f) / steps.size },
                    modifier = Modifier.fillMaxWidth()
                )
                if (stepIndex == 0) {
                    Text(copy.settingsIntro, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Text(step.title, style = MaterialTheme.typography.titleMedium, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                Text(step.description, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedButton(onClick = onDismiss) {
                        Text(copy.skip, style = MaterialTheme.typography.labelSmall)
                    }
                    if (stepIndex > 0) {
                        OutlinedButton(
                            onClick = { onStepIndexChange(stepIndex - 1) },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("◀", style = MaterialTheme.typography.labelSmall)
                        }
                    } else {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                    Button(
                        onClick = {
                            if (stepIndex == steps.lastIndex) onDismiss()
                            else onStepIndexChange(stepIndex + 1)
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            if (stepIndex == steps.lastIndex) copy.finish else "▶",
                            style = MaterialTheme.typography.labelSmall
                        )
                    }
                }
            }
        }
    }
}

fun settingsTourSteps(strings: AppStrings): List<FeatureTourStep> {
    // rawSettingsTourSteps の並びと 1:1 で対応させる。
    val targetKeys = listOf(
        "settings_language",
        "settings_backup",
        "settings_restore"
    )
    return rawSettingsTourSteps(strings).mapIndexedNotNull { index, (title, description) ->
        targetKeys.getOrNull(index)?.let { key -> FeatureTourStep(key, title, description) }
    }
}

private fun rawSettingsTourSteps(strings: AppStrings): List<Pair<String, String>> = when (strings.languageCode) {
    "ja" -> listOf(
        "言語" to "アプリ内の表示言語を変更できます。単語の意味表示にも反映されます。",
        "バックアップ" to "学習データをファイルとして保存し、端末変更や保管に使えます。",
        "レストア" to "保存したバックアップから単語・履歴・お気に入りを復元します。現在の学習データは置き換えられます。"
    )
    "zh" -> listOf(
        "语言" to "更改应用显示语言，也会影响单词释义的显示。",
        "备份" to "将学习数据保存为文件，用于保管或迁移到其他设备。",
        "恢复" to "从备份中恢复单词、历史记录和收藏夹。当前学习数据将被替换。"
    )
    "hi" -> listOf(
        "भाषा" to "ऐप की भाषा बदलें। इससे शब्दों के अर्थ की भाषा भी बदल जाएगी।",
        "बैकअप" to "अपने पढ़ाई के डेटा को सुरक्षित रखने या दूसरे डिवाइस पर ले जाने के लिए फ़ाइल में सेव करें।",
        "पुनर्स्थापित करें" to "बैकअप से शब्द, इतिहास और पसंदीदा शब्द वापस लाएँ। मौजूदा पढ़ाई का डेटा बदल दिया जाएगा।"
    )
    "vi" -> listOf(
        "Ngôn ngữ" to "Thay đổi ngôn ngữ hiển thị của ứng dụng. Ngôn ngữ hiển thị nghĩa của từ cũng sẽ thay đổi.",
        "Sao lưu" to "Lưu dữ liệu học tập thành tệp để bảo quản hoặc chuyển sang thiết bị khác.",
        "Khôi phục" to "Khôi phục từ, lịch sử và mục yêu thích từ bản sao lưu. Dữ liệu học hiện tại sẽ bị thay thế."
    )
    "ko" -> listOf(
        "언어" to "앱 표시 언어를 변경합니다. 표시되는 단어 뜻에도 반영됩니다.",
        "백업" to "학습 데이터를 파일로 저장하여 보관하거나 다른 기기로 옮길 수 있습니다.",
        "복원" to "백업에서 단어, 기록, 즐겨찾기를 복원합니다. 현재 학습 데이터는 교체됩니다."
    )
    "id" -> listOf(
        "Bahasa" to "Ubah bahasa tampilan aplikasi. Ini juga mengubah bahasa yang digunakan untuk menampilkan arti kata.",
        "Cadangkan" to "Simpan data belajar ke dalam file untuk dicadangkan atau dipindahkan ke perangkat lain.",
        "Pulihkan" to "Pulihkan kata, riwayat, dan favorit dari cadangan. Data belajar saat ini akan diganti."
    )
    "th" -> listOf(
        "ภาษา" to "เปลี่ยนภาษาที่แสดงในแอป และจะเปลี่ยนภาษาของความหมายคำศัพท์ด้วย",
        "สำรองข้อมูล" to "บันทึกข้อมูลการเรียนเป็นไฟล์เพื่อเก็บรักษาหรือย้ายไปยังอุปกรณ์อื่น",
        "กู้คืน" to "กู้คืนคำศัพท์ ประวัติ และรายการโปรดจากไฟล์สำรอง ข้อมูลการเรียนปัจจุบันจะถูกแทนที่"
    )
    "es" -> listOf(
        "Idioma" to "Cambia el idioma de la aplicación. También cambia cómo se muestran los significados de las palabras.",
        "Copia de seguridad" to "Guarda tus datos de estudio en un archivo para conservarlos o moverlos a otro dispositivo.",
        "Restaurar" to "Restaura palabras, historial y favoritos desde una copia de seguridad. Se reemplazarán los datos actuales."
    )
    else -> listOf(
        "Language" to "Change the app display language. This also changes the language used to display word meanings.",
        "Backup" to "Save your study data to a file for safekeeping or moving to another device.",
        "Restore" to "Restore words, history, and favorites from a backup. Current study data will be replaced."
    )
}
