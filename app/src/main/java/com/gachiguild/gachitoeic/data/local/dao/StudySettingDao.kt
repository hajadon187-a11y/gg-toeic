package com.gachiguild.gachitoeic.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.gachiguild.gachitoeic.data.local.entity.StudySettingEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface StudySettingDao {
    @Query("SELECT * FROM study_settings WHERE id = 1")
    fun observeSetting(): Flow<StudySettingEntity?>

    @Query("SELECT * FROM study_settings WHERE id = 1")
    suspend fun getSetting(): StudySettingEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdate(setting: StudySettingEntity)
}