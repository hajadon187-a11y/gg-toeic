package com.gachiguild.gachitoeic.domain.repository

import com.gachiguild.gachitoeic.domain.model.VocabularyHistory
import com.gachiguild.gachitoeic.domain.model.VocabularyItem
import kotlinx.coroutines.flow.Flow

/** ストリーク情報 */
data class StudyStreak(
    val currentStreak: Int = 0,
    val lastCompletedDate: String? = null,
    /** 直近1日だけ空いた場合に救済できる、切れる前のストリーク日数。 */
    val recoverableStreak: Int = 0,
    /** 救済に必要な今日の学習アクション数。 */
    val recoveryTarget: Int = 0,
    /** 救済判定に使う今日の学習アクション数。 */
    val recoveryProgress: Int = 0,
    /** 救済によって現在のストリークを維持している状態。 */
    val isRecovered: Boolean = false,
    /** 7日継続ごとに付与される救済チケットの残数。 */
    val recoveryTickets: Int = 0
)

val StudyStreak.isRecoveryAvailable: Boolean
    get() = recoverableStreak > 0

val StudyStreak.canRecover: Boolean
    get() = isRecoveryAvailable && recoveryProgress >= recoveryTarget

val StudyStreak.canRecoverWithTicket: Boolean
    get() = isRecoveryAvailable && recoveryTickets > 0

/** 今日の学習状況 */
data class TodayStudyProgress(
    val todayCount: Int = 0,
    val dailyTarget: Int = 5
) {
    val isTargetReached: Boolean get() = todayCount >= dailyTarget
    val progressPercent: Float
        get() = if (dailyTarget == 0) 0f else (todayCount * 100f / dailyTarget).coerceIn(0f, 100f)
}

interface StudyContentRepository {
    fun observeVocabulary(): Flow<List<VocabularyItem>>

    /** お気に入り登録日時の新しい順で、語彙のお気に入りIDを監視 */
    fun observeFavoriteVocabularyIds(): Flow<List<Long>>

    /** アクション履歴を新しい順で取得（wordIdとactionTypeを含む） */
    fun observeHistory(): Flow<List<VocabularyHistory>>

    /** 1日の目標単語数を監視 */
    fun observeDailyTarget(): Flow<Int>

    /** ストリーク情報を監視 */
    fun observeStreak(): Flow<StudyStreak>

    /** 今日の学習状況を監視（学習アクション数 + 目標） */
    fun observeTodayStudyProgress(): Flow<TodayStudyProgress>

    /** 過去N日間の日別学習件数を監視（ヒートマップ用） */
    fun observeHeatmapData(): Flow<Map<java.time.LocalDate, Int>>

    suspend fun addVocabulary(item: VocabularyItem)
    suspend fun toggleFavorite(itemId: Long)

    /**
     * 青カエルのマスター状態を更新する。
     *
     * 未マスター／マスター済みの2状態だけを扱う。デッキの対象判定は次回日時ではなく
     * この状態で決めるため、次回日時は保存しない。
     */
    suspend fun setMastered(itemId: Long, isMastered: Boolean)

    /** アクション履歴を記録（check / favorite / review_remembered / review_forgot / review_unmastered） */
    suspend fun recordHistory(wordId: Long, actionType: String)

    /** 1日の目標単語数を設定 */
    suspend fun setDailyTarget(target: Int)

    /** 学習アクションを記録し、ストリークを更新 */
    suspend fun recordStudyActivity()

    /** 直近1日分の未達成を、今日2日分学習して救済する */
    suspend fun repairStreak(): Boolean

    /** 救済チケットを1枚使って、直近1日分の未達成を救済する */
    suspend fun repairStreakWithTicket(): Boolean
}
