package com.gachiguild.gachitoefl

import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoefl.domain.model.VocabularyItem
import com.gachiguild.gachitoefl.presentation.viewmodel.VocabularyLevel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * 単語カードの出題範囲と、青カエルの未マスター／マスター済み2状態のテスト。
 *
 * - 単語カードタブ: 未マスター かつ 選択中 TOEFL レベルの単語を出題する
 * - 星（お気に入り）タブ: お気に入りを TOEFL レベルに関係なく出題する
 * - ⭐️（忘れた）は未マスター、🐸（マスター）はマスター済みにするだけ。
 *   「N日後に復活する」といった追加学習の仕組みは持たない。
 */
class VocabularyMasteryStateTest {

    private val level1 = VocabularyLevel.LEVEL1.ordinal
    private val level3 = VocabularyLevel.LEVEL3.ordinal

    /** 単語カードタブの出題対象。VocabularyScreen の deck 構築と同じ規則。 */
    private fun flashcardDeck(
        vocabulary: List<VocabularyItem>,
        selectedLevel: VocabularyLevel
    ): List<VocabularyItem> = vocabulary.filter { item ->
        !item.isMastered && selectedLevel.matchesVocabularyItemLevel(item.level)
    }

    /** 星タブの出題対象。TOEFL レベルを問わずお気に入りだけを出す。 */
    private fun favoriteDeck(vocabulary: List<VocabularyItem>): List<VocabularyItem> =
        vocabulary.filter { it.isFavorite }

    private fun item(
        id: Long,
        word: String,
        level: Int,
        isMastered: Boolean = false,
        isFavorite: Boolean = false
    ) = VocabularyItem(
        id = id,
        word = word,
        meaning = "意味",
        example = "example",
        isFavorite = isFavorite,
        isMastered = isMastered,
        level = level
    )

    /** 単語カードタブは未マスターだけを出題する。 */
    @Test
    fun flashcardDeckExcludesMasteredWords() {
        val vocabulary = listOf(
            item(1, "unmastered", level1),
            item(2, "mastered", level1, isMastered = true)
        )

        val deck = flashcardDeck(vocabulary, VocabularyLevel.LEVEL1)

        assertEquals(listOf("unmastered"), deck.map { it.word })
    }

    /** 単語カードタブは選択中レベル以外を出題しない（お気に入りでも出さない）。 */
    @Test
    fun flashcardDeckOnlyContainsSelectedBand() {
        val vocabulary = listOf(
            item(1, "level1", level1),
            item(2, "level3", level3),
            // お気に入りでも、選択レベル外なら単語カードタブには出さない。
            item(3, "level3Favorite", level3, isFavorite = true)
        )

        val deck = flashcardDeck(vocabulary, VocabularyLevel.LEVEL1)

        assertEquals(listOf("level1"), deck.map { it.word })
    }

    /** ⭐️（忘れた）は未マスターのままにするだけで、選択レベル内に出続ける。 */
    @Test
    fun forgottenWordStaysInFlashcardDeckWithinSelectedBand() {
        val before = item(1, "forgotten", level1, isMastered = false)
        // ⭐️ は「未マスターへ戻す」だけ。追加の待ち時間は持たない。
        val after = before.copy(isMastered = false)

        assertEquals(
            listOf("forgotten"),
            flashcardDeck(listOf(after), VocabularyLevel.LEVEL1).map { it.word }
        )
    }

    /** 🐸（マスター）は単語カードタブから外れる。 */
    @Test
    fun masteredWordLeavesFlashcardDeck() {
        val after = item(1, "mastered", level1, isMastered = true)

        assertTrue(flashcardDeck(listOf(after), VocabularyLevel.LEVEL1).isEmpty())
    }

    /** 星タブはお気に入りを TOEFL レベルに関係なく出題する。 */
    @Test
    fun favoriteDeckIgnoresBand() {
        val vocabulary = listOf(
            item(1, "level1Favorite", level1, isFavorite = true),
            item(2, "level3Favorite", level3, isFavorite = true),
            item(3, "notFavorite", level1)
        )

        val deck = favoriteDeck(vocabulary)

        assertEquals(listOf("level1Favorite", "level3Favorite"), deck.map { it.word })
    }

    /** 星タブはマスター済みでもお気に入りなら出題する（⭐️で管理するため）。 */
    @Test
    fun favoriteDeckIncludesMasteredFavorites() {
        val vocabulary = listOf(
            item(1, "masteredFavorite", level3, isMastered = true, isFavorite = true)
        )

        assertEquals(listOf("masteredFavorite"), favoriteDeck(vocabulary).map { it.word })
    }

    /** ドメインモデルは intervalDays ではなく isMastered で状態を持つ。 */
    @Test
    fun domainModelExposesMasteredFlagOnly() {
        assertFalse(item(1, "a", level1).isMastered)
        assertTrue(item(2, "b", level1, isMastered = true).isMastered)
    }

    /** 旧データの intervalDays は isMastered へ正しく変換される。 */
    @Test
    fun entityConvertsLegacyIntervalDaysToMasteredFlag() {
        val unmastered = VocabularyEntity(
            word = "a",
            meaning = "意味",
            example = "example",
            intervalDays = VocabularyEntity.UNMASTERED_INTERVAL_DAYS
        )
        val mastered = VocabularyEntity(
            word = "b",
            meaning = "意味",
            example = "example",
            intervalDays = VocabularyEntity.MASTERED_INTERVAL_DAYS
        )

        assertFalse(unmastered.isMastered)
        assertTrue(mastered.isMastered)
    }

    /** マスター状態は旧データ互換の intervalDays へ戻せる。 */
    @Test
    fun masteredFlagMapsBackToLegacyIntervalDays() {
        val entity = VocabularyEntity(word = "a", meaning = "意味", example = "example")

        assertEquals(
            VocabularyEntity.MASTERED_INTERVAL_DAYS,
            entity.intervalDaysFor(mastered = true)
        )
        assertEquals(
            VocabularyEntity.UNMASTERED_INTERVAL_DAYS,
            entity.intervalDaysFor(mastered = false)
        )
    }

    /** マスター判定の境界は MASTERED_INTERVAL_DAYS（= 8）であること。 */
    @Test
    fun masteredThresholdUsesNamedConstant() {
        val justBelow = VocabularyEntity(
            word = "a",
            meaning = "意味",
            example = "example",
            intervalDays = VocabularyEntity.MASTERED_INTERVAL_DAYS - 1
        )
        val atThreshold = VocabularyEntity(
            word = "b",
            meaning = "意味",
            example = "example",
            intervalDays = VocabularyEntity.MASTERED_INTERVAL_DAYS
        )

        assertFalse("8 未満は未マスター", justBelow.isMastered)
        assertTrue("8 以上はマスター済み", atThreshold.isMastered)
    }
}
