package com.gachiguild.gachitoeic.domain.model

/** 単語アクション履歴 */
data class VocabularyHistory(
    val id: Long = 0,
    val wordId: Long,
    val actionType: String, // "check", "favorite", "review_remembered", "review_forgot", "review_unmastered"
    val timestamp: Long = System.currentTimeMillis()
)
