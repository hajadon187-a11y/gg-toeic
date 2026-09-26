package com.gachiguild.gachitoeic

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.gachiguild.gachitoeic.data.backup.BackupService
import com.gachiguild.gachitoeic.data.local.AppDatabase
import com.gachiguild.gachitoeic.data.local.UserPreferences
import com.gachiguild.gachitoeic.data.local.entity.StudySettingEntity
import com.gachiguild.gachitoeic.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoeic.data.local.entity.VocabularyHistoryEntity
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [29])
class BackupServiceTest {
    private lateinit var database: AppDatabase
    private lateinit var service: BackupService

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        service = BackupService(database, UserPreferences(context))
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun backupRoundTripRestoresStudyStateAndHistory() = runBlocking {
        database.studyContentDao().insertVocabulary(
            VocabularyEntity(
                stableKey = "builtin:1",
                word = "analyze",
                meaning = "分析する",
                meaningEn = "To analyze",
                meaningId = "menganalisis",
                meaningTh = "วิเคราะห์",
                meaningEs = "analizar",
                example = "We analyze the report.",
                isFavorite = true,
                // 旧データ相当（未マスター < 8）。バックアップ経由でもそのまま復元される。
                intervalDays = 4
            )
        )
        val item = database.studyContentDao().getAllVocabulary().single()
        database.studyContentDao().insertHistory(
            VocabularyHistoryEntity(wordId = item.id, actionType = "check", timestamp = 5678L)
        )
        database.studySettingDao().insertOrUpdate(StudySettingEntity(dailyTarget = 10))

        val output = ByteArrayOutputStream()
        service.writeBackup(output)
        val document = service.readBackup(ByteArrayInputStream(output.toByteArray()))

        assertTrue(output.size() > 0)
        assertEquals(1, document.vocabulary.size)
        assertEquals("builtin:1", document.vocabulary.single().stableKey)
        assertEquals(1, document.history.size)

        database.studyContentDao().updateVocabulary(item.copy(isFavorite = false, intervalDays = 1))
        service.restore(document)

        val restored = database.studyContentDao().getAllVocabulary().single()
        assertTrue(restored.isFavorite)
        assertEquals(4, restored.intervalDays)
        assertEquals("menganalisis", restored.meaningId)
        assertEquals("วิเคราะห์", restored.meaningTh)
        assertEquals("analizar", restored.meaningEs)
        assertEquals(1, database.studyContentDao().getAllHistory().size)
        assertEquals(10, database.studySettingDao().getSetting()?.dailyTarget)
    }
}
