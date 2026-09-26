package com.gachiguild.gachitoeic.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/** 単語へのアクション履歴 */
@Entity(tableName = "vocabulary_history")
data class VocabularyHistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val wordId: Long,
    val actionType: String, // "check", "favorite", "review_remembered", "review_forgot", "review_unmastered"
    val timestamp: Long = System.currentTimeMillis()
)
