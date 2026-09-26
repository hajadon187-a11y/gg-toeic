package com.gachiguild.gachitoeic.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.gachiguild.gachitoeic.data.local.dao.FavoriteDao
import com.gachiguild.gachitoeic.data.local.dao.StudyContentDao
import com.gachiguild.gachitoeic.data.local.dao.StudySettingDao
import com.gachiguild.gachitoeic.data.local.dao.StudyStreakDao
import com.gachiguild.gachitoeic.data.local.entity.FavoriteEntity
import com.gachiguild.gachitoeic.data.local.entity.StudySettingEntity
import com.gachiguild.gachitoeic.data.local.entity.StudyStreakEntity
import com.gachiguild.gachitoeic.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoeic.data.local.entity.VocabularyHistoryEntity

@Database(
    entities = [
        VocabularyEntity::class,
        FavoriteEntity::class,
        VocabularyHistoryEntity::class,
        StudySettingEntity::class,
        StudyStreakEntity::class
    ],
    version = 12,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun studyContentDao(): StudyContentDao
    abstract fun favoriteDao(): FavoriteDao
    abstract fun studySettingDao(): StudySettingDao
    abstract fun studyStreakDao(): StudyStreakDao
}
