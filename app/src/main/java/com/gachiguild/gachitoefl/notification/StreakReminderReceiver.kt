package com.gachiguild.gachitoefl.notification

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.gachiguild.gachitoefl.data.local.UserPreferences
import com.gachiguild.gachitoefl.domain.repository.StudyContentRepository
import com.gachiguild.gachitoefl.ui.AppLanguage
import com.gachiguild.gachitoefl.ui.ChineseStrings
import com.gachiguild.gachitoefl.ui.EnglishStrings
import com.gachiguild.gachitoefl.ui.HindiStrings
import com.gachiguild.gachitoefl.ui.IndonesianStrings
import com.gachiguild.gachitoefl.ui.JapaneseStrings
import com.gachiguild.gachitoefl.ui.KoreanStrings
import com.gachiguild.gachitoefl.ui.SpanishStrings
import com.gachiguild.gachitoefl.ui.ThaiStrings
import com.gachiguild.gachitoefl.ui.VietnameseStrings
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

@AndroidEntryPoint
class StreakReminderReceiver : BroadcastReceiver() {
    @Inject
    lateinit var repository: StudyContentRepository

    @Inject
    lateinit var userPreferences: UserPreferences

    override fun onReceive(context: Context, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_TIMEZONE_CHANGED,
            Intent.ACTION_TIME_CHANGED -> {
                StreakReminderScheduler.schedule(context)
                return
            }

            StreakReminderScheduler.ACTION_STREAK_REMINDER -> showReminder(context)
            StreakReminderScheduler.ACTION_STREAK_REMINDER_TEST -> showTestReminder(context)
        }
    }

    private fun showReminder(context: Context) {
        val pendingResult = goAsync()
        CoroutineScope(SupervisorJob() + Dispatchers.IO).launch {
            try {
                // アラーム登録時ではなく発火時に再確認して、直前に学習した場合の誤通知を防ぐ。
                val progress = repository.observeTodayStudyProgress().first()
                val streak = repository.observeStreak().first()
                if (streak.currentStreak > 0 && !progress.isTargetReached) {
                    val language = AppLanguage.fromCode(userPreferences.getLanguageCode())
                    val strings = when (language) {
                        AppLanguage.English -> EnglishStrings
                        AppLanguage.Japanese -> JapaneseStrings
                        AppLanguage.Chinese -> ChineseStrings
                        AppLanguage.Hindi -> HindiStrings
                        AppLanguage.Vietnamese -> VietnameseStrings
                        AppLanguage.Korean -> KoreanStrings
                        AppLanguage.Indonesian -> IndonesianStrings
                        AppLanguage.Thai -> ThaiStrings
                        AppLanguage.Spanish -> SpanishStrings
                    }
                    StreakNotificationManager.showAtRiskNotification(
                        context = context,
                        strings = strings
                    )
                }
            } finally {
                // 今日の判定後、必ず翌日の21:00を登録する。
                StreakReminderScheduler.schedule(context)
                pendingResult.finish()
            }
        }
    }

    private fun showTestReminder(context: Context) {
        val language = AppLanguage.fromCode(userPreferences.getLanguageCode())
        val strings = when (language) {
            AppLanguage.English -> EnglishStrings
            AppLanguage.Japanese -> JapaneseStrings
            AppLanguage.Chinese -> ChineseStrings
            AppLanguage.Hindi -> HindiStrings
            AppLanguage.Vietnamese -> VietnameseStrings
            AppLanguage.Korean -> KoreanStrings
            AppLanguage.Indonesian -> IndonesianStrings
            AppLanguage.Thai -> ThaiStrings
            AppLanguage.Spanish -> SpanishStrings
        }
        StreakNotificationManager.showAtRiskNotification(
            context = context,
            strings = strings
        )
        StreakReminderScheduler.schedule(context)
    }
}
