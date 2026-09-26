package com.gachiguild.gachitoefl.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.gachiguild.gachitoefl.data.local.entity.StudyStreakEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface StudyStreakDao {
    @Query("SELECT * FROM study_streak WHERE id = 1")
    fun observeStreak(): Flow<StudyStreakEntity?>

    @Query("SELECT * FROM study_streak WHERE id = 1")
    suspend fun getStreak(): StudyStreakEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdate(streak: StudyStreakEntity)
}