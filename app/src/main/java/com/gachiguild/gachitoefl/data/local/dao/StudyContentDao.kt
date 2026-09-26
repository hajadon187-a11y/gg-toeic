package com.gachiguild.gachitoefl.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyHistoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface StudyContentDao {
    // id（登録順）で固定ソート。nextReviewAt でソートすると、
    // 🙆チェックなどで nextReviewAt が更新された際にリストの順序が変わってしまうため。
    @Query("SELECT * FROM vocabulary ORDER BY id ASC")
    fun observeVocabulary(): Flow<List<VocabularyEntity>>

    @Query("SELECT COUNT(*) FROM vocabulary")
    suspend fun vocabularyCount(): Int

    @Query("SELECT * FROM vocabulary ORDER BY id ASC")
    suspend fun getAllVocabulary(): List<VocabularyEntity>

    @Query("SELECT * FROM vocabulary WHERE stableKey = :stableKey LIMIT 1")
    suspend fun findVocabularyByStableKey(stableKey: String): VocabularyEntity?

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertVocabulary(entity: VocabularyEntity): Long

    @Update
    suspend fun updateVocabulary(entity: VocabularyEntity)

    /**
     * 習熟度だけを更新する。
     *
     * 次回日時（nextReviewAt）は現在使わないため更新しない。既存端末のカラムは
     * バックアップ互換のため温存する。
     */
    @Query("UPDATE vocabulary SET intervalDays = :intervalDays WHERE id = :id")
    suspend fun updateMastery(id: Long, intervalDays: Int)

    /**
     * 学習状態を初期化する（マスター解除・お気に入り解除）。
     *
     * intervalDays は VocabularyEntity.UNMASTERED_INTERVAL_DAYS（= 1）を使う。
     * 次回日時（nextReviewAt）は現在使わないため更新しない。
     */
    @Query("UPDATE vocabulary SET isFavorite = 0, intervalDays = 1")
    suspend fun resetLearningState()

    @Query("DELETE FROM vocabulary WHERE stableKey LIKE 'custom:%'")
    suspend fun deleteCustomVocabulary()

    @Query("DELETE FROM vocabulary_history")
    suspend fun deleteAllHistory()

    @Query("SELECT * FROM vocabulary_history ORDER BY timestamp ASC, id ASC")
    suspend fun getAllHistory(): List<VocabularyHistoryEntity>

    @Insert
    suspend fun insertHistoryAll(entities: List<VocabularyHistoryEntity>)

    /**
     * 同梱アセットの内容に語彙行を同期する（お気に入り・SRS学習状態は保持される）。
     * 見出し語そのものを更新するため、TOEFLレベル別デッキの入れ替えを既存端末にも反映できる。
     */
    @Query(
        """
        UPDATE vocabulary
        SET word = :word,
            wordUk = :wordUk,
            phoneticUk = :phoneticUk,
            meaning = :meaning,
            meaningEn = :meaningEn,
            meaningZh = :meaningZh,
            meaningHi = :meaningHi,
            meaningVi = :meaningVi,
            meaningKo = :meaningKo,
            meaningId = :meaningId,
            meaningTh = :meaningTh,
            meaningEs = :meaningEs,
            synonyms = :synonyms,
            collocations = :collocations,
            example = :example,
            topic = :topic
        WHERE id = :id
        """
    )
    suspend fun syncVocabularyContent(
        id: Long,
        word: String,
        wordUk: String,
        phoneticUk: String,
        meaning: String,
        meaningEn: String,
        meaningZh: String,
        meaningHi: String,
        meaningVi: String,
        meaningKo: String,
        meaningId: String,
        meaningTh: String,
        meaningEs: String,
        synonyms: String,
        collocations: String,
        example: String,
        topic: String
    )

    // ── 履歴 ──

    /** アクション履歴を新しい順で取得 */
    @Query("SELECT * FROM vocabulary_history ORDER BY timestamp DESC, id DESC")
    fun observeHistory(): Flow<List<VocabularyHistoryEntity>>

    /** アクション履歴を記録 */
    @Insert
    suspend fun insertHistory(entity: VocabularyHistoryEntity)

    /** 指定日の学習アクション件数をカウント（check / review_remembered / review_forgot / review_unmastered） */
    @Query(
        """
        SELECT COUNT(*) FROM vocabulary_history
        WHERE actionType IN ('check', 'review_remembered', 'review_forgot', 'review_unmastered')
          AND timestamp BETWEEN :startOfDay AND :endOfDay
        """
    )
    fun observeStudyCountByDate(startOfDay: Long, endOfDay: Long): Flow<Int>

    /** 日別の学習アクション件数を集計（ヒートマップ用） */
    @Query(
        """
        SELECT 
          date(timestamp / 1000, 'unixepoch', 'localtime') AS day,
          COUNT(*) AS count
        FROM vocabulary_history
        WHERE actionType IN ('check', 'review_remembered', 'review_forgot', 'review_unmastered')
          AND timestamp >= :startTime
        GROUP BY day
        """
    )
    fun observeDailyStudyCounts(startTime: Long): Flow<List<DailyStudyCount>>
}

/** 日別の学習件数（ヒートマップ用） */
data class DailyStudyCount(
    val day: String,
    val count: Int
)
