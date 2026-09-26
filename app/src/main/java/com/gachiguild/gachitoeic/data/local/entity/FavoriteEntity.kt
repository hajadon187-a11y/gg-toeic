package com.gachiguild.gachitoeic.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "favorites")
data class FavoriteEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val itemType: String, // "vocabulary", "grammar", "question"
    val itemId: Long,
    val addedAt: Long = System.currentTimeMillis()
)
