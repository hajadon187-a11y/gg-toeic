import com.gachiguild.gachitoeic.BuildConfig
import com.gachiguild.gachitoeic.data.billing.PremiumAccess
import com.gachiguild.gachitoeic.data.billing.isPremiumUnlocked
import com.gachiguild.gachitoeic.presentation.viewmodel.PREMIUM_LEVELS_LOCK_ENABLED
import com.gachiguild.gachitoeic.presentation.viewmodel.VocabularyLevel
import com.gachiguild.gachitoeic.presentation.viewmodel.requiresPremium
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * TOEIC Advanced（内部LEVEL4/旧LEVEL5）のプレミアムロックに関するテスト。
 */
class PremiumLevelLockTest {

    @Test
    fun debugBuildUnlocksAdvancedWithoutPurchase() {
        // testDebugUnitTest は通常の debug バリアントで実行される。
        assertFalse(BuildConfig.PRODUCTION_MODE)
        assertFalse(PREMIUM_LEVELS_LOCK_ENABLED)
        assertFalse(VocabularyLevel.ADVANCED.requiresPremium())
        assertTrue(PremiumAccess.UNKNOWN.isPremiumUnlocked())
    }

    /**
     * 検索ダイアログの TOEIC level 表示・ロック判定に使う level -> level 文字列の変換。
     * VocabularyScreen.vocabularyItemLevel と同じ規則を保つ。
     */
    private fun vocabularyItemLevel(level: Int): String = when (level) {
        VocabularyLevel.LEVEL1.ordinal,
        VocabularyLevel.LEVEL2.ordinal -> "Basic"
        VocabularyLevel.LEVEL3.ordinal -> "Standard"
        VocabularyLevel.LEVEL4.ordinal,
        VocabularyLevel.LEVEL5.ordinal -> "Advanced"
        else -> "Basic"
    }

    /**
     * 検索ダイアログの 🔒 表示と購入ガイド判定に使う。
     * VocabularyScreen.isPremiumLevelItem と同じ規則を保つ。
     */
    private fun isPremiumLevelItem(level: Int): Boolean =
        VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(level)

    /**
     * 検索ダイアログで単語を選んだときに購入ガイドを出すかどうか。
     * VocabularyScreen.onSearchedWordSelected と同じ規則を保つ。
     */
    private fun requiresPurchaseGuide(itemLevel: Int, premiumUnlocked: Boolean): Boolean =
        isPremiumLevelItem(itemLevel) && !premiumUnlocked

    @Test
    fun advancedIsTheOnlyPremiumLevel() {
        // ロックが有効なときは Advanced（内部LEVEL4/LEVEL5）だけがプレミアム対象。
        assertFalse(VocabularyLevel.LEVEL1.requiresPremium())
        assertFalse(VocabularyLevel.LEVEL2.requiresPremium())
        assertFalse(VocabularyLevel.LEVEL3.requiresPremium())
        assertFalse(VocabularyLevel.BASIC.requiresPremium())
        assertFalse(VocabularyLevel.STANDARD.requiresPremium())
        if (PREMIUM_LEVELS_LOCK_ENABLED) {
            assertTrue(VocabularyLevel.ADVANCED.requiresPremium())
            assertTrue(VocabularyLevel.LEVEL4.requiresPremium())
            assertTrue(VocabularyLevel.LEVEL5.requiresPremium())
        } else {
            // ロック無効時は Advanced も誰でも閲覧できる。
            assertFalse(VocabularyLevel.ADVANCED.requiresPremium())
            assertFalse(VocabularyLevel.LEVEL4.requiresPremium())
            assertFalse(VocabularyLevel.LEVEL5.requiresPremium())
        }
    }

    @Test
    fun threeToeicTiersMatchInternalLevels() {
        // Basic は内部Level 1 + Level 2。
        assertTrue(VocabularyLevel.BASIC.matchesVocabularyItemLevel(1))
        assertTrue(VocabularyLevel.BASIC.matchesVocabularyItemLevel(2))
        assertFalse(VocabularyLevel.BASIC.matchesVocabularyItemLevel(3))

        // Standard は内部Level 3。
        assertTrue(VocabularyLevel.STANDARD.matchesVocabularyItemLevel(3))
        assertFalse(VocabularyLevel.STANDARD.matchesVocabularyItemLevel(2))

        // Advanced は内部Level 4 + 旧データのLevel 5。
        assertTrue(VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(4))
        assertTrue(VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(5))
        assertFalse(VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(3))
        assertTrue(VocabularyLevel.ALL.matchesVocabularyItemLevel(5))
    }

    @Test
    fun searchListShowsToeicLevelForEachItem() {
        // 検索結果の右側に出す (TOEIC tier) の表示内容。
        assertEquals("Basic", vocabularyItemLevel(VocabularyLevel.LEVEL1.ordinal))
        assertEquals("Basic", vocabularyItemLevel(VocabularyLevel.LEVEL2.ordinal))
        assertEquals("Standard", vocabularyItemLevel(VocabularyLevel.LEVEL3.ordinal))
        assertEquals("Advanced", vocabularyItemLevel(VocabularyLevel.LEVEL4.ordinal))
        // 旧 level 5 も Advanced として表示する。
        assertEquals("Advanced", vocabularyItemLevel(VocabularyLevel.LEVEL5.ordinal))
    }

    @Test
    fun onlyLevel4ItemsAreTreatedAsPremiumInSearch() {
        // 検索結果で 🔒 を付けるのは TOEIC L4（level 4 / 旧 level 5）だけ。
        assertFalse(isPremiumLevelItem(VocabularyLevel.LEVEL1.ordinal))
        assertFalse(isPremiumLevelItem(VocabularyLevel.LEVEL2.ordinal))
        assertFalse(isPremiumLevelItem(VocabularyLevel.LEVEL3.ordinal))
        assertTrue(isPremiumLevelItem(VocabularyLevel.LEVEL4.ordinal))
        assertTrue(isPremiumLevelItem(VocabularyLevel.LEVEL5.ordinal))
    }

    @Test
    fun searchSelectionGuidesToPurchaseOnlyForLockedLevel4() {
        // 未購入で TOEIC L4 を選ぶと購入ガイドを表示する（単語カードは開かない）。
        assertTrue(requiresPurchaseGuide(VocabularyLevel.LEVEL4.ordinal, premiumUnlocked = false))
        assertTrue(requiresPurchaseGuide(VocabularyLevel.LEVEL5.ordinal, premiumUnlocked = false))

        // 購入済みならそのまま単語カードを開く。
        assertFalse(requiresPurchaseGuide(VocabularyLevel.LEVEL4.ordinal, premiumUnlocked = true))
        assertFalse(requiresPurchaseGuide(VocabularyLevel.LEVEL5.ordinal, premiumUnlocked = true))

        // TOEIC L4 未満は購入状態に関わらず購入ガイドを出さない。
        listOf(
            VocabularyLevel.LEVEL1.ordinal,
            VocabularyLevel.LEVEL2.ordinal,
            VocabularyLevel.LEVEL3.ordinal
        ).forEach { level ->
            assertFalse(requiresPurchaseGuide(level, premiumUnlocked = false))
            assertFalse(requiresPurchaseGuide(level, premiumUnlocked = true))
        }
    }
}
