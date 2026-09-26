package com.gachiguild.gachitoeic.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/** 学習ストリーク（連続日数）管理（常に1行のみ保持） */
@Entity(tableName = "study_streak")
data class StudyStreakEntity(
    @PrimaryKey val id: Int = 1,
    val currentStreak: Int = 0,
    val lastCompletedDate: String? = null, // yyyy-MM-dd
    /** 救済後の連続日数を履歴から再計算するときの基準日。 */
    val recoveryDate: String? = null, // yyyy-MM-dd
    val recoveryTickets: Int = 0,
    val lastTicketAwardedStreak: Int = 0
)
