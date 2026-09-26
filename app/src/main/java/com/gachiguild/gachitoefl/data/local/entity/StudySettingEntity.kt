package com.gachiguild.gachitoefl.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/** 学習設定（常に1行のみ保持） */
@Entity(tableName = "study_settings")
data class StudySettingEntity(
    @PrimaryKey val id: Int = 1,
    val dailyTarget: Int = 5
)
