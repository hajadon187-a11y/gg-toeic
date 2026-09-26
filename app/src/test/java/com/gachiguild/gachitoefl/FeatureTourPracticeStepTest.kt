import com.gachiguild.gachitoefl.presentation.viewmodel.VocabularyLevel
import com.gachiguild.gachitoefl.presentation.screens.vocabulary.FeatureTourState
import com.gachiguild.gachitoefl.presentation.screens.vocabulary.FeatureTourStep
import com.gachiguild.gachitoefl.presentation.screens.vocabulary.FeatureTourStepId
import com.gachiguild.gachitoefl.presentation.screens.vocabulary.mainFeatureTourSteps
import com.gachiguild.gachitoefl.ui.AppStrings
import com.gachiguild.gachitoefl.ui.ChineseStrings
import com.gachiguild.gachitoefl.ui.EnglishStrings
import com.gachiguild.gachitoefl.ui.HindiStrings
import com.gachiguild.gachitoefl.ui.IndonesianStrings
import com.gachiguild.gachitoefl.ui.JapaneseStrings
import com.gachiguild.gachitoefl.ui.KoreanStrings
import com.gachiguild.gachitoefl.ui.SpanishStrings
import com.gachiguild.gachitoefl.ui.ThaiStrings
import com.gachiguild.gachitoefl.ui.VietnameseStrings
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * チュートリアル「長押しメニュー」（11/16）で実際に長押し・検索してもらう実操作ステップのテスト。
 *
 * 実操作の対象は TOEFL L1 の基礎語 `she` にする。L4 だと解放が必要になり
 * 初回起動で離脱しやすいため、購入導線には触れず長押しと検索だけを体験してもらう。
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [33], manifest = Config.NONE)
class FeatureTourPracticeStepTest {

    /** 長押しメニューのステップが 11 番目（index 10）にあることを前提にする。 */
    private val longPressStepIndex = 10

    /** 全対応言語で、長押しメニューのステップが同じ位置・同じ ID で識別できること。 */
    @Test
    fun longPressMenuStepIsIdentifiedByStepIdInEveryLanguage() {
        supportedLanguageCodes.forEach { languageCode ->
            val steps = mainFeatureTourSteps(appStringsForLanguage(languageCode))

            val practiceSteps = steps.filter { it.stepId == FeatureTourStepId.LONG_PRESS_MENU }
            assertEquals(
                "長押しメニューのステップは1つだけ: $languageCode",
                1,
                practiceSteps.size
            )
            assertEquals(
                "長押しメニューは 11/16（index 10）: $languageCode",
                longPressStepIndex,
                steps.indexOfFirst { it.stepId == FeatureTourStepId.LONG_PRESS_MENU }
            )
            // 単語カードの枠を指すステップであること。
            assertEquals("flashcard_area", practiceSteps.single().targetKey)
        }
    }

    /**
     * 実操作の対象語を差し込む前は実操作なし、差し込むと実操作ステップになること。
     * VocabularyScreen はこの practiceWord の有無でガイド表示を切り替える。
     */
    @Test
    fun practiceWordTurnsLongPressStepIntoPracticeStep() {
        val baseStep = mainFeatureTourSteps(appStringsForLanguage("ja"))
            .first { it.stepId == FeatureTourStepId.LONG_PRESS_MENU }

        assertFalse("語を差し込む前は実操作なし", baseStep.hasPractice)
        assertNull(baseStep.practiceWord)
        assertNull(baseStep.practiceKey)

        val practiceStep = baseStep.copy(practiceWord = "aberration")

        assertTrue("語を差し込むと実操作ステップになる", practiceStep.hasPractice)
        assertEquals("aberration", practiceStep.practiceWord)
        assertNotNull(practiceStep.practiceKey)
    }

    /**
     * 実操作キーは「対象枠 + 単語」で決まるため、カードの単語が変われば
     * 検知結果が混ざらないこと。
     */
    @Test
    fun practiceKeyIsUniquePerTargetAndWord() {
        val wordStep = practiceStep("aberration")
        val otherWordStep = practiceStep("abolish")
        val otherTargetStep = wordStep.copy(targetKey = "flashcard_buttons")

        assertEquals("flashcard_area:aberration", wordStep.practiceKey)
        assertFalse(
            "別の単語とは別のキーになる",
            wordStep.practiceKey == otherWordStep.practiceKey
        )
        assertFalse(
            "別の対象枠とは別のキーになる",
            wordStep.practiceKey == otherTargetStep.practiceKey
        )
    }

    /**
     * 長押しを記録する前は未達成、記録すると達成になること。
     * FeatureTourPracticeGuide はこの回数で ✅ 表示と文言を切り替える。
     */
    @Test
    fun longPressActionIsTrackedPerStep() {
        val step = practiceStep("aberration")
        val state = FeatureTourState()
        val key = requireNotNull(step.practiceKey)

        assertEquals("未実施のステップは 0 回", 0, state.actionCountFor(key))

        state.registerAction(key)

        assertEquals("長押し成功で 1 回", 1, state.actionCountFor(key))
        assertFalse(
            "他のステップには影響しない",
            state.actionCountFor("flashcard_buttons:aberration") > 0
        )
    }

    /** ツアーをやり直したときに、前回の実操作の記録が残らないこと。 */
    @Test
    fun clearingActionsResetsLongPressProgress() {
        val step = practiceStep("aberration")
        val state = FeatureTourState()
        val key = requireNotNull(step.practiceKey)

        state.registerAction(key)
        state.registerAction(key)
        assertEquals(2, state.actionCountFor(key))

        state.clearActions()

        assertEquals("クリア後は未達成に戻る", 0, state.actionCountFor(key))
    }

    private fun practiceStep(word: String): FeatureTourStep =
        mainFeatureTourSteps(appStringsForLanguage("ja"))
            .first { it.stepId == FeatureTourStepId.LONG_PRESS_MENU }
            .copy(practiceWord = word)
    /**
     * ガイド上の単語を長押ししたときに「単語を操作」ダイアログを開くかどうかの規則。
     *
     * 単語カードは説明カードの背面にあり指が届かないことがあるため、
     * ガイドに表示した単語を長押ししても同じダイアログを開けるようにする。
     * カードの表示語（UK / US どちらもありうる）と一致すればダイアログを開く。
     */
    private fun opensWordActionDialog(
        requestedWord: String?,
        cardDisplayWord: String
    ): Boolean = requestedWord?.equals(cardDisplayWord, ignoreCase = true) == true

    @Test
    fun guideLongPressOpensDialogForSameWordAsCard() {
        // ガイドに出している語とカードの表示語が同じなら、ダイアログを開く。
        assertTrue(opensWordActionDialog("abrupt", "abrupt"))
        // 大文字小文字は無視する。
        assertTrue(opensWordActionDialog("Abrupt", "abrupt"))
    }

    @Test
    fun guideLongPressIgnoresOtherWordsAndNull() {
        // 別の語や未設定ではダイアログを開かない。
        assertFalse(opensWordActionDialog("absorb", "abrupt"))
        assertFalse(opensWordActionDialog(null, "abrupt"))
    }

    /**
     * ガイドに表示する語は UK スペルを優先し、長押し判定は UK / US 両方を受け付けること。
     * showTourPracticeWordCard / tourPracticeWordAccepted と同じ規則を保つ。
     */
    @Test
    fun guideShowsUkSpellingAndAcceptsBothSpellings() {
        val word = "she"
        val wordUk = "she"
        // ガイドの表示語（UK があれば優先）。
        val displayed = if (wordUk.isNotBlank()) wordUk else word
        // 長押し判定用の語集合。
        val accepted = setOf(word, wordUk)
            .filter { it.isNotBlank() }
            .map { it.lowercase() }
            .toSet()

        assertEquals("she", displayed)
        assertTrue("UK スペルで一致する", displayed.lowercase() in accepted)

        // UK と US でスペルが違う語でも、どちらも受け付ける。
        val colourAccepted = setOf("colour", "color")
            .filter { it.isNotBlank() }
            .map { it.lowercase() }
            .toSet()
        assertTrue("colour" in colourAccepted)
        assertTrue("color" in colourAccepted)
    }

    /**
     * 実操作に使うサンプル語は語彙データに存在し、L4（プレミアム）ではないこと。
     * 購入導線を出さずに長押しと検索を体験させるための前提条件。
     */
    @Test
    fun tourPracticeSampleWordIsNotPremium() {
        val vocabulary = loadVocabularyLevels()
        val levelByWord = vocabulary.associate { it.first to it.second }
        val sampleWord = "she"

        val level = levelByWord[sampleWord]
        assertNotNull("サンプル語が語彙データに存在する: $sampleWord", level)
        if (level != null) {
            assertFalse(
                "サンプル語はプレミアム対象ではない: $sampleWord",
                VocabularyLevel.LEVEL4.matchesVocabularyItemLevel(level)
            )
            // 初回起動の誰にでも分かる基礎語（TOEFL L1 = LEVEL1）を使う。
            assertEquals(
                "サンプル語は TOEFL L1（LEVEL1）: $sampleWord",
                VocabularyLevel.LEVEL1.ordinal,
                level
            )
        }
    }

    /** サンプル語 `she` は単語カードに出す意味・例文・コロケーションが揃っていること。 */
    @Test
    fun tourPracticeSampleWordHasCardContent() {
        val asset = java.io.File("src/main/assets/vocabulary.json")
        val text = asset.readText()
        // "word": "she" のブロックを抜き出して中身を確認する。
        val blockStart = text.indexOf("\"word\": \"she\"")
        assertTrue("サンプル語 she が語彙アセットにある", blockStart >= 0)
        val block = text.substring(blockStart, minOf(blockStart + 1500, text.length))

        assertTrue("意味がある", block.contains("\"meaning\":"))
        assertTrue("例文がある", block.contains("\"example\":"))
        assertTrue("コロケーションがある", block.contains("\"collocations\":"))
    }

    /** 語彙アセットから (単語小文字, level) の一覧を読み込む。 */
    private fun loadVocabularyLevels(): List<Pair<String, Int>> {
        val asset = java.io.File(
            "src/main/assets/vocabulary.json"
        )
        val text = asset.readText()
        // 語彙アセットは巨大なため、必要な word / level だけを軽量に抜き出す。
        val wordPattern = Regex("\"word\"\\s*:\\s*\"([^\"]+)\"")
        val levelPattern = Regex("\"level\"\\s*:\\s*(\\d+)")
        val entries = mutableListOf<Pair<String, Int>>()
        var currentWord: String? = null
        text.lineSequence().forEach { line ->
            wordPattern.find(line)?.let { match ->
                if (currentWord == null) currentWord = match.groupValues[1]
            }
            levelPattern.find(line)?.let { match ->
                currentWord?.let { word ->
                    entries += word.lowercase() to match.groupValues[1].toInt()
                    currentWord = null
                }
            }
        }
        assertTrue("語彙アセットを読み込めた", entries.size > 1000)
        return entries
    }

    private fun appStringsForLanguage(languageCode: String): AppStrings = when (languageCode) {
        "ja" -> JapaneseStrings
        "zh" -> ChineseStrings
        "hi" -> HindiStrings
        "vi" -> VietnameseStrings
        "ko" -> KoreanStrings
        "id" -> IndonesianStrings
        "th" -> ThaiStrings
        "es" -> SpanishStrings
        else -> EnglishStrings
    }

    /** アプリが対応する表示言語。FeatureTourCopy と同じ並び。 */
    private val supportedLanguageCodes = listOf(
        "ja", "en", "zh", "hi", "vi", "ko", "id", "th", "es"
    )
}
