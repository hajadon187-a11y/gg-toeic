package com.gachiguild.gachitoefl.di

import android.content.Context
import androidx.room.Room
import com.gachiguild.gachitoefl.data.local.AppDatabase
import com.gachiguild.gachitoefl.data.local.MIGRATION_5_6
import com.gachiguild.gachitoefl.data.local.MIGRATION_6_7
import com.gachiguild.gachitoefl.data.local.MIGRATION_7_8
import com.gachiguild.gachitoefl.data.local.MIGRATION_8_9
import com.gachiguild.gachitoefl.data.local.MIGRATION_9_10
import com.gachiguild.gachitoefl.data.local.MIGRATION_10_11
import com.gachiguild.gachitoefl.data.local.MIGRATION_11_12
import com.gachiguild.gachitoefl.data.local.dao.StudyContentDao
import com.gachiguild.gachitoefl.data.local.dao.FavoriteDao
import com.gachiguild.gachitoefl.data.local.dao.StudySettingDao
import com.gachiguild.gachitoefl.data.local.dao.StudyStreakDao
import com.gachiguild.gachitoefl.data.local.VocabularySeeder
import com.gachiguild.gachitoefl.data.repository.RoomStudyContentRepository
import com.gachiguild.gachitoefl.domain.repository.StudyContentRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "vocabulary_app.db"
        ).addMigrations(MIGRATION_5_6, MIGRATION_6_7, MIGRATION_7_8, MIGRATION_8_9, MIGRATION_9_10, MIGRATION_10_11, MIGRATION_11_12).build()
    }

    @Provides
    fun provideStudyContentDao(database: AppDatabase): StudyContentDao = database.studyContentDao()

    @Provides
    fun provideFavoriteDao(database: AppDatabase): FavoriteDao = database.favoriteDao()

    @Provides
    fun provideStudySettingDao(database: AppDatabase): StudySettingDao = database.studySettingDao()

    @Provides
    fun provideStudyStreakDao(database: AppDatabase): StudyStreakDao = database.studyStreakDao()

    @Provides
    @Singleton
    fun provideStudyContentRepository(
        studyContentDao: StudyContentDao,
        favoriteDao: FavoriteDao,
        studySettingDao: StudySettingDao,
        studyStreakDao: StudyStreakDao
    ): StudyContentRepository = RoomStudyContentRepository(studyContentDao, favoriteDao, studySettingDao, studyStreakDao)

    @Provides
    @Singleton
    fun provideVocabularySeeder(
        @ApplicationContext context: Context,
        studyContentDao: StudyContentDao
    ): VocabularySeeder = VocabularySeeder(context, studyContentDao)
}
