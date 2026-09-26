package com.gachiguild.gachitoefl

import android.app.Application
import com.gachiguild.gachitoefl.data.local.VocabularySeeder
import com.gachiguild.gachitoefl.notification.StreakReminderScheduler
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

@HiltAndroidApp
class AIToeflCoachApplication : Application() {

    @Inject
    lateinit var vocabularySeeder: VocabularySeeder

    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        // アプリ起動時にも翌日の21:00通知を再登録する。
        StreakReminderScheduler.schedule(this)
        // テスト用の1分通知は PRODUCTION_MODE=false のビルドにだけ存在する。
        if (!BuildConfig.PRODUCTION_MODE) {
            StreakReminderScheduler.scheduleForTest(this)
        }
        applicationScope.launch {
            // 語彙データを assets/vocabulary.json から投入
            vocabularySeeder.seedIfNeeded()
        }
    }
}
