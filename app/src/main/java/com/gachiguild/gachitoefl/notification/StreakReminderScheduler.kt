package com.gachiguild.gachitoefl.notification

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import java.time.ZonedDateTime

/** 毎日21:00（端末のローカルタイム）にストリーク判定を起動するスケジューラ。 */
object StreakReminderScheduler {
    const val ACTION_STREAK_REMINDER = "com.gachiguild.gachitoefl.action.STREAK_REMINDER"
    const val ACTION_STREAK_REMINDER_TEST = "com.gachiguild.gachitoefl.action.STREAK_REMINDER_TEST"

    private const val REQUEST_CODE = 21_00

    fun schedule(context: Context) {
        val alarmManager = context.getSystemService(AlarmManager::class.java) ?: return
        val pendingIntent = pendingIntent(context, ACTION_STREAK_REMINDER)
        alarmManager.cancel(pendingIntent)

        val now = ZonedDateTime.now()
        var next = now.withHour(21).withMinute(0).withSecond(0).withNano(0)
        if (!next.isAfter(now)) {
            next = next.plusDays(1)
        }
        val triggerAtMillis = next.toInstant().toEpochMilli()

        // Android 12+では、正確なアラーム権限がない場合に近い時刻へ安全にフォールバックする。
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && alarmManager.canScheduleExactAlarms()) {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent
            )
        } else {
            alarmManager.setAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent
            )
        }
    }

    /** デバッグビルド専用。アプリ起動から1分後に通知を発火させる。 */
    fun scheduleForTest(context: Context, delayMillis: Long = 60_000L) {
        val alarmManager = context.getSystemService(AlarmManager::class.java) ?: return
        val pendingIntent = pendingIntent(context, ACTION_STREAK_REMINDER_TEST)
        alarmManager.cancel(pendingIntent)
        val triggerAtMillis = System.currentTimeMillis() + delayMillis

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && alarmManager.canScheduleExactAlarms()) {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent
            )
        } else {
            alarmManager.setAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent
            )
        }
    }

    private fun pendingIntent(context: Context, action: String): PendingIntent =
        PendingIntent.getBroadcast(
            context,
            REQUEST_CODE,
            Intent(context, StreakReminderReceiver::class.java).setAction(action),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
}
