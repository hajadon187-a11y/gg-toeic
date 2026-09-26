package com.gachiguild.gachitoefl.data.repository

import com.gachiguild.gachitoefl.data.local.dao.StudyContentDao
import com.gachiguild.gachitoefl.data.local.dao.FavoriteDao
import com.gachiguild.gachitoefl.data.local.dao.StudySettingDao
import com.gachiguild.gachitoefl.data.local.dao.StudyStreakDao
import com.gachiguild.gachitoefl.data.local.entity.FavoriteEntity
import com.gachiguild.gachitoefl.data.local.entity.StudySettingEntity
import com.gachiguild.gachitoefl.data.local.entity.StudyStreakEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyHistoryEntity
import com.gachiguild.gachitoefl.data.local.dao.DailyStudyCount
import com.gachiguild.gachitoefl.domain.model.VocabularyHistory
import com.gachiguild.gachitoefl.domain.model.VocabularyItem
import com.gachiguild.gachitoefl.domain.repository.StudyContentRepository
import com.gachiguild.gachitoefl.domain.repository.StudyStreak
import com.gachiguild.gachitoefl.domain.repository.TodayStudyProgress
import java.time.LocalDate
import java.time.ZoneId
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject


class RoomStudyContentRepository @Inject constructor(
    private val studyContentDao: StudyContentDao,
    private val favoriteDao: FavoriteDao,
    private val studySettingDao: StudySettingDao,
    private val studyStreakDao: StudyStreakDao
) : StudyContentRepository {
    /** マスター状態を、既存端末と互換の intervalDays 表現へ変換する。 */
    private fun intervalDaysFor(isMastered: Boolean): Int =
        if (isMastered) {
            VocabularyEntity.MASTERED_INTERVAL_DAYS
        } else {
            VocabularyEntity.UNMASTERED_INTERVAL_DAYS
        }

    override fun observeVocabulary(): Flow<List<VocabularyItem>> = studyContentDao.observeVocabulary().map { list ->
        // TOEFL L4 の入れ替え待ち枠は word が空。学習対象に出すと空カードになるため除外する。
        list.filter { it.word.isNotBlank() }.map { entity ->
            VocabularyItem(
                id = entity.id,
                stableKey = entity.stableKey,
                word = entity.word,
                wordUk = entity.wordUk.ifBlank { entity.word },
                phoneticUk = entity.phoneticUk,
                meaning = entity.meaning,
                meaningEn = entity.meaningEn,
                meaningZh = entity.meaningZh,
                meaningHi = entity.meaningHi,
                meaningVi = entity.meaningVi,
                meaningKo = entity.meaningKo,
                meaningId = entity.meaningId,
                meaningTh = entity.meaningTh,
                meaningEs = entity.meaningEs,
                synonyms = parseSynonyms(entity.synonyms),
                collocations = parseCollocations(entity.collocations),
                example = entity.example,
                isFavorite = entity.isFavorite,
                isMastered = entity.isMastered,
                level = entity.level,
                topic = entity.topic
            )
        }
    }

    override fun observeFavoriteVocabularyIds(): Flow<List<Long>> =
        favoriteDao.observeFavoritesByType("vocabulary")
            .map { favorites -> favorites.map { it.itemId } }

    private fun parseSynonyms(raw: String): List<String> {
        if (raw.isBlank()) return emptyList()
        return raw.split(",").map { it.trim() }.filter { it.isNotEmpty() }
    }

    private fun parseCollocations(raw: String): List<String> {
        if (raw.isBlank()) return emptyList()
        return raw.split(",").map { it.trim() }.filter { it.isNotEmpty() }
    }

    override suspend fun addVocabulary(item: VocabularyItem) {
        studyContentDao.insertVocabulary(
            VocabularyEntity(
                id = item.id,
                stableKey = item.stableKey.ifBlank { "custom:${java.util.UUID.randomUUID()}" },
                word = item.word,
                wordUk = item.wordUk.ifBlank { item.word },
                phoneticUk = item.phoneticUk,
                meaning = item.meaning,
                meaningEn = item.meaningEn,
                meaningZh = item.meaningZh,
                meaningHi = item.meaningHi,
                meaningVi = item.meaningVi,
                meaningKo = item.meaningKo,
                meaningId = item.meaningId,
                meaningTh = item.meaningTh,
                meaningEs = item.meaningEs,
                synonyms = item.synonyms.joinToString(", "),
                collocations = item.collocations.joinToString(", "),
                example = item.example,
                isFavorite = item.isFavorite,
                intervalDays = intervalDaysFor(item.isMastered),
                level = item.level,
                topic = item.topic
            )
        )
    }

    override suspend fun toggleFavorite(itemId: Long) {
        val entity = studyContentDao.observeVocabulary().first().firstOrNull { it.id == itemId } ?: return
        val newFavoriteState = !entity.isFavorite
        studyContentDao.updateVocabulary(
            entity.copy(isFavorite = newFavoriteState)
        )
        if (newFavoriteState) {
            favoriteDao.insert(FavoriteEntity(itemType = "vocabulary", itemId = itemId))
        } else {
            favoriteDao.delete(itemType = "vocabulary", itemId = itemId)
        }
    }

    override suspend fun setMastered(itemId: Long, isMastered: Boolean) {
        // デッキの対象判定は「マスター済みかどうか」だけで決まるため、
        // intervalDays のみ更新する（nextReviewAt は現在使わない）。
        studyContentDao.updateMastery(itemId, intervalDaysFor(isMastered))
    }

    override fun observeHistory(): Flow<List<VocabularyHistory>> =
        studyContentDao.observeHistory().map { list ->
            list.map { entity ->
                VocabularyHistory(
                    id = entity.id,
                    wordId = entity.wordId,
                    actionType = entity.actionType,
                    timestamp = entity.timestamp
                )
            }
        }

    override suspend fun recordHistory(wordId: Long, actionType: String) {
        studyContentDao.insertHistory(
            VocabularyHistoryEntity(wordId = wordId, actionType = actionType)
        )
    }

    // ── 学習設定 ──

    override fun observeDailyTarget(): Flow<Int> =
        studySettingDao.observeSetting().map { it?.dailyTarget ?: 5 }

    override suspend fun setDailyTarget(target: Int) {
        val current = studySettingDao.getSetting()
        studySettingDao.insertOrUpdate(
            StudySettingEntity(dailyTarget = target)
        )
    }

    // ── ストリーク ──

    override fun observeStreak(): Flow<StudyStreak> =
        combine(
            // 保存済みの currentStreak は、アプリが閉じている間の日付経過を反映できない。
            // 学習履歴を正本として、表示時にも現在の連続日数を再計算する。
            studyContentDao.observeDailyStudyCounts(0L),
            observeDailyTarget(),
            studyStreakDao.observeStreak()
        ) { dailyCounts, dailyTarget, savedStreak ->
            calculateStudyStreak(dailyCounts, dailyTarget, savedStreak)
        }

    override suspend fun recordStudyActivity() {
        // 現在の履歴から再計算して保存する。既存データに残った古い値もここで補正する。
        val dailyTarget = studySettingDao.getSetting()?.dailyTarget ?: 5
        val dailyCounts = studyContentDao.observeDailyStudyCounts(0L).first()
        val savedStreak = studyStreakDao.getStreak()
        val today = LocalDate.now()
        val todayStr = today.toString()
        val yesterdayStr = today.minusDays(1).toString()
        val todayCount = dailyCounts.firstOrNull { it.day == todayStr }?.count ?: 0

        val streakEntity = when {
            // 救済後は、同じ日にさらに学習しても救済状態を維持する。
            savedStreak?.recoveryDate == todayStr -> savedStreak
            // 救済翌日に目標を達成したら、その日も連続日数へ加える。
            savedStreak?.recoveryDate == yesterdayStr && todayCount >= dailyTarget ->
                savedStreak.copy(
                    currentStreak = savedStreak.currentStreak + 1,
                    lastCompletedDate = todayStr,
                    recoveryDate = todayStr
                )
            // 救済翌日でまだ目標未達成なら、昨日の救済済みストリークを保持する。
            savedStreak?.recoveryDate == yesterdayStr -> savedStreak
            else -> {
                val streak = calculateStudyStreak(dailyCounts, dailyTarget, savedStreak)
                StudyStreakEntity(
                    currentStreak = streak.currentStreak,
                    lastCompletedDate = streak.lastCompletedDate,
                    recoveryTickets = streak.recoveryTickets,
                    lastTicketAwardedStreak = if (streak.currentStreak > 0) {
                        savedStreak?.lastTicketAwardedStreak ?: 0
                    } else {
                        0
                    }
                )
            }
        }

        studyStreakDao.insertOrUpdate(awardTicketIfMilestone(streakEntity))
    }

    override suspend fun repairStreak(): Boolean {
        val dailyTarget = studySettingDao.getSetting()?.dailyTarget ?: 5
        if (dailyTarget <= 0) return false

        val dailyCounts = studyContentDao.observeDailyStudyCounts(0L).first()
        val savedStreak = studyStreakDao.getStreak()
        val streak = calculateStudyStreak(dailyCounts, dailyTarget, savedStreak)
        if (streak.recoverableStreak <= 0 || streak.recoveryProgress < streak.recoveryTarget) {
            return false
        }

        val today = LocalDate.now().toString()
        studyStreakDao.insertOrUpdate(
            awardTicketIfMilestone(StudyStreakEntity(
                currentStreak = streak.recoverableStreak + 1,
                lastCompletedDate = today,
                recoveryDate = today,
                recoveryTickets = streak.recoveryTickets,
                lastTicketAwardedStreak = savedStreak?.lastTicketAwardedStreak ?: 0
            ))
        )
        return true
    }

    override suspend fun repairStreakWithTicket(): Boolean {
        val dailyTarget = studySettingDao.getSetting()?.dailyTarget ?: 5
        if (dailyTarget <= 0) return false

        val dailyCounts = studyContentDao.observeDailyStudyCounts(0L).first()
        val savedStreak = studyStreakDao.getStreak()
        val streak = calculateStudyStreak(dailyCounts, dailyTarget, savedStreak)
        if (streak.recoverableStreak <= 0 || streak.recoveryTickets <= 0) return false

        val today = LocalDate.now().toString()
        studyStreakDao.insertOrUpdate(
            awardTicketIfMilestone(StudyStreakEntity(
                currentStreak = streak.recoverableStreak + 1,
                lastCompletedDate = today,
                recoveryDate = today,
                recoveryTickets = streak.recoveryTickets - 1,
                lastTicketAwardedStreak = savedStreak?.lastTicketAwardedStreak ?: 0
            ))
        )
        return true
    }

    // ── 今日の学習状況 ──

    override fun observeTodayStudyProgress(): Flow<TodayStudyProgress> {
        val startOfToday = LocalDate.now().atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        val endOfToday = LocalDate.now().plusDays(1).atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli() - 1

        val countFlow = studyContentDao.observeStudyCountByDate(startOfToday, endOfToday)
        val targetFlow = studySettingDao.observeSetting().map { it?.dailyTarget ?: 5 }

        return combine(countFlow, targetFlow) { count, target ->
            TodayStudyProgress(
                todayCount = count,
                dailyTarget = target
            )
        }
    }

    // ── ヒートマップ ──

    /** 過去365日間（約1年）の日別学習件数を監視 */
    override fun observeHeatmapData(): Flow<Map<java.time.LocalDate, Int>> {
        val startTime = java.time.LocalDate.now().minusDays(364)
            .atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()

        return studyContentDao.observeDailyStudyCounts(startTime).map { dailyCounts ->
            dailyCounts.mapNotNull { item ->
                runCatching { java.time.LocalDate.parse(item.day) }.getOrNull()?.let { date ->
                    date to item.count
                }
            }.toMap()
        }
    }

    /** 目標達成日を最新日から遡り、途切れない連続日数を求める。 */
    private fun calculateStudyStreak(
        dailyCounts: List<DailyStudyCount>,
        dailyTarget: Int,
        savedStreak: StudyStreakEntity? = null
    ): StudyStreak {
        val savedTickets = savedStreak?.recoveryTickets ?: 0
        if (dailyTarget <= 0) return StudyStreak(recoveryTickets = savedTickets)

        val today = LocalDate.now()
        val todayStr = today.toString()
        val yesterdayStr = today.minusDays(1).toString()
        val savedRecoveryDate = savedStreak?.recoveryDate

        // 救済済みの日付を履歴だけで再現できないため、保存したストリークを優先する。
        if (savedStreak != null && savedRecoveryDate in listOf(todayStr, yesterdayStr)) {
            return StudyStreak(
                currentStreak = savedStreak.currentStreak,
                lastCompletedDate = savedStreak.lastCompletedDate ?: savedRecoveryDate,
                isRecovered = true,
                recoveryTickets = savedTickets
            )
        }

        val completedDates = dailyCounts
            .asSequence()
            .filter { it.count >= dailyTarget }
            .mapNotNull { runCatching { LocalDate.parse(it.day) }.getOrNull() }
            .toSet()
        val latestCompletedDate = completedDates.maxOrNull()
            ?: return StudyStreak(recoveryTickets = savedTickets)

        // 昨日を空けて今日だけ目標達成した場合も、救済操作までは通常の1日 streak にしない。
        val recoveryBaseDate = when {
            today in completedDates && today.minusDays(1) !in completedDates &&
                today.minusDays(2) in completedDates -> today.minusDays(2)
            latestCompletedDate == today.minusDays(2) -> latestCompletedDate
            else -> null
        }
        if (recoveryBaseDate != null) {
            val recoveryTarget = dailyTarget * 2
            return StudyStreak(
                currentStreak = 0,
                lastCompletedDate = recoveryBaseDate.toString(),
                recoverableStreak = countStreakEndingAt(recoveryBaseDate, completedDates),
                recoveryTarget = recoveryTarget,
                recoveryProgress = dailyCounts.firstOrNull { it.day == todayStr }?.count ?: 0,
                recoveryTickets = savedTickets
            )
        }

        // 今日も昨日も目標未達成なら、過去の連続日数は現在のストリークではない。
        if (latestCompletedDate.isBefore(today.minusDays(1))) {
            return StudyStreak(
                currentStreak = 0,
                lastCompletedDate = latestCompletedDate.toString(),
                recoveryTickets = savedTickets
            )
        }

        val streak = countStreakEndingAt(latestCompletedDate, completedDates)

        return StudyStreak(
            currentStreak = streak,
            lastCompletedDate = latestCompletedDate.toString(),
            recoveryTickets = savedTickets
        )
    }

    private fun awardTicketIfMilestone(entity: StudyStreakEntity): StudyStreakEntity {
        if (entity.currentStreak <= 0) {
            return entity.copy(lastTicketAwardedStreak = 0)
        }
        val reachedMilestone = entity.currentStreak % 7 == 0
        val alreadyAwarded = entity.currentStreak <= entity.lastTicketAwardedStreak
        return if (reachedMilestone && !alreadyAwarded) {
            entity.copy(
                recoveryTickets = entity.recoveryTickets + 1,
                lastTicketAwardedStreak = entity.currentStreak
            )
        } else {
            entity
        }
    }

    private fun countStreakEndingAt(endDate: LocalDate, completedDates: Set<LocalDate>): Int {
        var streak = 1
        var date = endDate.minusDays(1)
        while (date in completedDates) {
            streak++
            date = date.minusDays(1)
        }
        return streak
    }
}
