package com.gachiguild.gachitoefl.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.gachiguild.gachitoefl.data.local.entity.FavoriteEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface FavoriteDao {
    @Query("SELECT * FROM favorites WHERE itemType = :itemType ORDER BY addedAt DESC, id DESC")
    fun observeFavoritesByType(itemType: String): Flow<List<FavoriteEntity>>

    @Query("SELECT EXISTS(SELECT 1 FROM favorites WHERE itemType = :itemType AND itemId = :itemId)")
    fun observeIsFavorite(itemType: String, itemId: Long): Flow<Boolean>

    @Query("SELECT EXISTS(SELECT 1 FROM favorites WHERE itemType = :itemType AND itemId = :itemId)")
    suspend fun isFavorite(itemType: String, itemId: Long): Boolean

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(favorite: FavoriteEntity): Long

    @Query("DELETE FROM favorites WHERE itemType = :itemType AND itemId = :itemId")
    suspend fun delete(itemType: String, itemId: Long)

    @Query("DELETE FROM favorites")
    suspend fun deleteAll()

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(favorites: List<FavoriteEntity>)
}
