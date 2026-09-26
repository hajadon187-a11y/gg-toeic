package com.gachiguild.gachitoefl

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.gachiguild.gachitoefl.data.local.AppDatabase
import com.gachiguild.gachitoefl.data.local.entity.FavoriteEntity
import com.gachiguild.gachitoefl.data.local.entity.StudyStreakEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyHistoryEntity
import com.gachiguild.gachitoefl.data.repository.RoomStudyContentRepository
import com.gachiguild.gachitoefl.domain.model.VocabularyItem
import com.gachiguild.gachitoefl.domain.repository.isRecoveryAvailable
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.time.LocalDate
import java.time.ZoneId

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [29])
class RoomRepositoryTest {

    private lateinit var database: AppDatabase
    private lateinit var contentRepository: RoomStudyContentRepository

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        contentRepository = RoomStudyContentRepository(
            database.studyContentDao(),
            database.favoriteDao(),
            database.studySettingDao(),
            database.studyStreakDao()
        )
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun sampleVocabularyItemCanBeCreated() {
        val item = VocabularyItem(
            word = "Analyze",
            meaning = "分析する",
            meaningEn = "To analyze",
            meaningZh = "分析",
            meaningHi = "विश्लेषण करना",
            meaningVi = "phân tích",
            meaningKo = "분석하다",
            meaningId = "menganalisis",
            meaningTh = "วิเคราะห์",
            meaningEs = "analizar",
            example = "We analyze the report"
        )
        assertTrue(item.word.isNotEmpty())
        assertEquals("分析", item.meaningFor("zh"))
        assertEquals("विश्लेषण करना", item.meaningFor("hi"))
        assertEquals("phân tích", item.meaningFor("vi"))
        assertEquals("분석하다", item.meaningFor("ko"))
        assertEquals("menganalisis", item.meaningFor("id"))
        assertEquals("วิเคราะห์", item.meaningFor("th"))
        assertEquals("analizar", item.meaningFor("es"))
        assertEquals("analizar", item.meaningFor("es-ES"))
        assertEquals("分析", item.meaningFor("zh-CN"))
        assertEquals("분석하다", item.meaningFor("ko-KR"))
        assertEquals("menganalisis", item.meaningFor("id-ID"))
        assertEquals("วิเคราะห์", item.meaningFor("th-TH"))

        val missingTranslation = item.copy(meaningZh = "", meaningKo = "", meaningId = "")
        assertEquals("To analyze", missingTranslation.meaningFor("zh"))
        assertEquals("To analyze", missingTranslation.meaningFor("ko"))
        assertEquals("To analyze", missingTranslation.meaningFor("id"))

        val missingEnglish = item.copy(meaningEn = "", meaningZh = "", meaningKo = "", meaningId = "")
        assertEquals("Analyze", missingEnglish.meaningFor("zh"))
        assertEquals("Analyze", missingEnglish.meaningFor("ko"))
        assertEquals("Analyze", missingEnglish.meaningFor("id"))

        val wrongVietnameseTranslation = item.copy(meaningVi = "前進；進歩；前もって")
        assertEquals("To analyze", wrongVietnameseTranslation.meaningFor("vi"))

        val wrongVietnameseWithChineseOnly = item.copy(meaningVi = "肠道，直觉，内脏")
        assertEquals("To analyze", wrongVietnameseWithChineseOnly.meaningFor("vi"))

        val wrongIndonesianTranslation = item.copy(meaningId = "分析する（意味を調べる）")
        assertEquals("To analyze", wrongIndonesianTranslation.meaningFor("id"))
    }

    @Test
    fun vocabularyCanBeAddedAndObserved() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        contentRepository.addVocabulary(
            VocabularyItem(word = "Benefit", meaning = "利益", example = "A benefit of exercise")
        )

        val vocabulary = contentRepository.observeVocabulary().first()
        assertEquals(2, vocabulary.size)
        assertEquals("Analyze", vocabulary.first().word)
    }

    @Test
    fun placeholderVocabularyRecordsAreHiddenFromStudyLists() = runBlocking {
        // TOEFL L4 の入れ替え待ち枠（word が空）は、学習リストに出してはいけない。
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        database.studyContentDao().insertVocabulary(
            com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity(
                id = 9001L,
                stableKey = "builtin:9001",
                word = "",
                meaning = "",
                example = "",
                level = 4
            )
        )

        val vocabulary = contentRepository.observeVocabulary().first()
        assertEquals(1, vocabulary.size)
        assertEquals("Analyze", vocabulary.first().word)
    }

    @Test
    fun syncVocabularyContentReplacesHeadwordAndKeepsStudyState() = runBlocking {
        // TOEFLレベル別デッキの入れ替えを既存端末へ反映する際、
        // 見出し語は更新しつつ、お気に入りとSRS学習状態は保持されること。
        database.studyContentDao().insertVocabulary(
            VocabularyEntity(
                stableKey = "builtin:2252",
                word = "infection",
                wordUk = "infection",
                meaning = "感染、感染症",
                meaningEn = "The invasion of body tissues",
                example = "Hand hygiene prevents infection.",
                isFavorite = true,
                intervalDays = 6,
                level = 3,
                topic = "Health"
            )
        )
        val before = database.studyContentDao().getAllVocabulary().single()
        assertTrue("未マスターとして扱われる", before.intervalDays < 8)

        // 入れ替え待ちスロット相当（word が空）へ同期する。
        database.studyContentDao().syncVocabularyContent(
            id = before.id,
            word = "",
            wordUk = "",
            phoneticUk = "",
            meaning = "",
            meaningEn = "",
            meaningZh = "",
            meaningHi = "",
            meaningVi = "",
            meaningKo = "",
            meaningId = "",
            meaningTh = "",
            meaningEs = "",
            synonyms = "",
            collocations = "",
            example = "",
            topic = "General"
        )

        val after = database.studyContentDao().getAllVocabulary().single()
        assertEquals("", after.word)
        assertEquals("", after.meaning)
        assertEquals("General", after.topic)
        // 学習状態は保持される。
        assertTrue(after.isFavorite)
        assertEquals(6, after.intervalDays)
        assertEquals(3, after.level)
    }


    @Test
    fun vocabularyCanBeFavoritedAndUnfavorited() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )

        val added = contentRepository.observeVocabulary().first().first()
        contentRepository.toggleFavorite(added.id)
        assertTrue(contentRepository.observeVocabulary().first().first().isFavorite)

        contentRepository.toggleFavorite(added.id)
        assertEquals(false, contentRepository.observeVocabulary().first().first().isFavorite)
    }

    @Test
    fun favoriteVocabularyIdsAreObservedNewestFirst() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        contentRepository.addVocabulary(
            VocabularyItem(word = "Benefit", meaning = "利益", example = "A benefit of exercise")
        )
        val vocabulary = contentRepository.observeVocabulary().first()

        database.favoriteDao().insert(
            FavoriteEntity(itemType = "vocabulary", itemId = vocabulary[0].id, addedAt = 1000L)
        )
        database.favoriteDao().insert(
            FavoriteEntity(itemType = "vocabulary", itemId = vocabulary[1].id, addedAt = 2000L)
        )

        assertEquals(
            listOf(vocabulary[1].id, vocabulary[0].id),
            contentRepository.observeFavoriteVocabularyIds().first()
        )
    }

    @Test
    fun vocabularyReviewStatusCanBeUpdated() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )

        val added = contentRepository.observeVocabulary().first().first()
        assertFalse("追加直後は未マスター", added.isMastered)

        contentRepository.setMastered(added.id, isMastered = true)

        val mastered = contentRepository.observeVocabulary().first().first()
        assertTrue("マスター済みへ更新される", mastered.isMastered)
        // デッキ判定に使う intervalDays も合わせて更新される（旧データ互換）。
        assertEquals(
            VocabularyEntity.MASTERED_INTERVAL_DAYS,
            database.studyContentDao().getAllVocabulary().single().intervalDays
        )

        contentRepository.setMastered(added.id, isMastered = false)

        val unmastered = contentRepository.observeVocabulary().first().first()
        assertFalse("未マスターへ戻せる", unmastered.isMastered)
        assertEquals(
            VocabularyEntity.UNMASTERED_INTERVAL_DAYS,
            database.studyContentDao().getAllVocabulary().single().intervalDays
        )
    }

    @Test
    fun historyCanBeRecordedAndObserved() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()

        contentRepository.recordHistory(added.id, "check")
        contentRepository.recordHistory(added.id, "review_remembered")

        val history = contentRepository.observeHistory().first()
        assertEquals(2, history.size)
        // 新しい順（降順）で取得される
        assertEquals("review_remembered", history.first().actionType)
        assertEquals("check", history.last().actionType)
        assertEquals(added.id, history.first().wordId)
    }

    // ── ストリーク ──

    @Test
    fun streakNotUpdatedBelowDailyTarget() = runBlocking {
        contentRepository.setDailyTarget(20)
        // 1語だけ学習（目標20未達）→ ストリークは更新されない
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()
        contentRepository.recordHistory(added.id, "check")
        contentRepository.recordStudyActivity()

        val streak = contentRepository.observeStreak().first()
        assertEquals(0, streak.currentStreak)
        assertEquals(null, streak.lastCompletedDate)
    }

    @Test
    fun streakIncrementsWhenDailyTargetMet() = runBlocking {
        contentRepository.setDailyTarget(20)
        // 20回の学習アクション → 目標達成 → ストリーク=1
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()

        repeat(19) {
            contentRepository.recordHistory(added.id, "check")
            contentRepository.recordStudyActivity()
        }
        // 19回目時点ではまだ未達
        assertEquals(0, contentRepository.observeStreak().first().currentStreak)

        // 20回目で達成 → ストリーク=1
        contentRepository.recordHistory(added.id, "check")
        contentRepository.recordStudyActivity()

        val streak = contentRepository.observeStreak().first()
        assertEquals(1, streak.currentStreak)
        assertEquals(LocalDate.now().toString(), streak.lastCompletedDate)
    }

    @Test
    fun sameDayStudyActivityDoesNotIncreaseStreak() = runBlocking {
        contentRepository.setDailyTarget(20)
        // 目標達成後、同じ日にさらに学習してもストリークは増えない
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()

        repeat(20) {
            contentRepository.recordHistory(added.id, "check")
            contentRepository.recordStudyActivity()
        }
        assertEquals(1, contentRepository.observeStreak().first().currentStreak)

        // 同じ日にもう20回
        repeat(20) {
            contentRepository.recordHistory(added.id, "check")
            contentRepository.recordStudyActivity()
        }

        val streak = contentRepository.observeStreak().first()
        assertEquals(1, streak.currentStreak)
    }

    @Test
    fun streakIsRecomputedFromHistoryInsteadOfCachedValue() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()
        contentRepository.setDailyTarget(2)

        repeat(2) {
            contentRepository.recordHistory(added.id, "check")
        }
        database.studyStreakDao().insertOrUpdate(
            StudyStreakEntity(
                currentStreak = 90,
                lastCompletedDate = LocalDate.now().minusDays(90).toString()
            )
        )

        val streak = contentRepository.observeStreak().first()
        assertEquals(1, streak.currentStreak)
        assertEquals(LocalDate.now().toString(), streak.lastCompletedDate)
    }

    @Test
    fun streakCanBeRepairedAfterOneMissedDayWithTwoDaysOfStudy() = runBlocking {
        contentRepository.setDailyTarget(2)
        val today = LocalDate.now()
        val twoDaysAgo = today.minusDays(2)
        val itemId = 1L
        fun timestamp(date: LocalDate): Long =
            date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli() + 1_000L

        repeat(2) {
            database.studyContentDao().insertHistory(
                VocabularyHistoryEntity(
                    wordId = itemId,
                    actionType = "check",
                    timestamp = timestamp(twoDaysAgo)
                )
            )
        }
        repeat(4) {
            database.studyContentDao().insertHistory(
                VocabularyHistoryEntity(
                    wordId = itemId,
                    actionType = "check",
                    timestamp = timestamp(today)
                )
            )
        }

        val beforeRepair = contentRepository.observeStreak().first()
        assertEquals(0, beforeRepair.currentStreak)
        assertEquals(1, beforeRepair.recoverableStreak)
        assertEquals(4, beforeRepair.recoveryTarget)
        assertEquals(4, beforeRepair.recoveryProgress)

        assertTrue(contentRepository.repairStreak())
        val repaired = contentRepository.observeStreak().first()
        assertEquals(2, repaired.currentStreak)
        assertTrue(repaired.isRecovered)
        assertTrue(!repaired.isRecoveryAvailable)
    }

    @Test
    fun recoveryTicketIsAwardedAtSevenDayMilestoneAndNotDuplicated() = runBlocking {
        contentRepository.setDailyTarget(1)
        val today = LocalDate.now()
        fun timestamp(date: LocalDate): Long =
            date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli() + 1_000L

        repeat(7) { offset ->
            database.studyContentDao().insertHistory(
                VocabularyHistoryEntity(
                    wordId = 1L,
                    actionType = "check",
                    timestamp = timestamp(today.minusDays((6 - offset).toLong()))
                )
            )
        }
        contentRepository.recordStudyActivity()

        val awarded = contentRepository.observeStreak().first()
        assertEquals(7, awarded.currentStreak)
        assertEquals(1, awarded.recoveryTickets)

        contentRepository.recordStudyActivity()
        assertEquals(1, contentRepository.observeStreak().first().recoveryTickets)
    }

    @Test
    fun recoveryTicketCanRepairOneMissedDayWithoutDoubleStudy() = runBlocking {
        contentRepository.setDailyTarget(2)
        val today = LocalDate.now()
        fun timestamp(date: LocalDate): Long =
            date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli() + 1_000L

        repeat(2) {
            database.studyContentDao().insertHistory(
                VocabularyHistoryEntity(
                    wordId = 1L,
                    actionType = "check",
                    timestamp = timestamp(today.minusDays(2))
                )
            )
            database.studyContentDao().insertHistory(
                VocabularyHistoryEntity(
                    wordId = 1L,
                    actionType = "check",
                    timestamp = timestamp(today)
                )
            )
        }
        database.studyStreakDao().insertOrUpdate(
            StudyStreakEntity(recoveryTickets = 1)
        )

        assertTrue(contentRepository.repairStreakWithTicket())
        val repaired = contentRepository.observeStreak().first()
        assertEquals(2, repaired.currentStreak)
        assertEquals(0, repaired.recoveryTickets)
        assertTrue(repaired.isRecovered)
    }

    // ── 1日の目標 ──

    @Test
    fun dailyTargetCanBeSetAndObserved() = runBlocking {
        // デフォルトは5
        assertEquals(5, contentRepository.observeDailyTarget().first())

        contentRepository.setDailyTarget(10)
        assertEquals(10, contentRepository.observeDailyTarget().first())

        contentRepository.setDailyTarget(30)
        assertEquals(30, contentRepository.observeDailyTarget().first())
    }

    @Test
    fun heatmapDataReflectsDailyStudyCounts() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()

        contentRepository.recordHistory(added.id, "check")
        contentRepository.recordHistory(added.id, "review_remembered")

        val heatmap = contentRepository.observeHeatmapData().first()
        assertEquals(2, heatmap[java.time.LocalDate.now()] ?: 0)
    }

    @Test
    fun todayStudyProgressReflectsStudyActions() = runBlocking {
        contentRepository.addVocabulary(
            VocabularyItem(word = "Analyze", meaning = "分析する", example = "We analyze the report")
        )
        val added = contentRepository.observeVocabulary().first().first()

        val progress = contentRepository.observeTodayStudyProgress().first()
        assertEquals(0, progress.todayCount)

        contentRepository.recordHistory(added.id, "check")
        contentRepository.recordHistory(added.id, "review_remembered")

        val progressAfter = contentRepository.observeTodayStudyProgress().first()
        assertEquals(2, progressAfter.todayCount)
        assertEquals(5, progressAfter.dailyTarget)
    }
}
