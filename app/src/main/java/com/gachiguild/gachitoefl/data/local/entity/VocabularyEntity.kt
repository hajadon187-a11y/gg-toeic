package com.gachiguild.gachitoefl.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "vocabulary",
    indices = [Index(value = ["stableKey"], unique = true)]
)
data class VocabularyEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    /** 端末をまたいで単語を識別するキー。builtin:<asset id> / custom:<UUID>。 */
    val stableKey: String = "",
    val word: String,
    val wordUk: String = "",
    val phoneticUk: String = "",
    val meaning: String,
    val meaningEn: String = "",
    /** Simplified Chinese translation. */
    val meaningZh: String = "",
    /** Hindi translation. */
    val meaningHi: String = "",
    /** Vietnamese translation. */
    val meaningVi: String = "",
    /** Korean translation. */
    val meaningKo: String = "",
    /** Indonesian translation. */
    val meaningId: String = "",
    /** Thai translation. */
    val meaningTh: String = "",
    /** Spanish translation. */
    val meaningEs: String = "",
    val synonyms: String = "",
    val collocations: String = "",
    val example: String,
    val isFavorite: Boolean = false,
    /**
     * 旧・次回レビュー日時。現在は参照も更新もしない。
     *
     * 既存端末の DB とバックアップの互換のためカラムだけ残す。
     */
    @Deprecated("習熟度は isMastered 相当（intervalDays）だけで管理する。保存のみ温存。")
    val nextReviewAt: Long = System.currentTimeMillis(),
    /**
     * 習熟度。8 = マスター済み、それ以外 = 未マスター。
     *
     * ドメインモデルでは [com.gachiguild.gachitoefl.domain.model.VocabularyItem.isMastered] として扱う。
     * マジックナンバーを避けるため判定は [MASTERED_INTERVAL_DAYS] を使う。
     */
    val intervalDays: Int = UNMASTERED_INTERVAL_DAYS,
    val level: Int = 2,
    val topic: String = "General"
) {
    /** 青カエルのマスター済み状態。ドメインモデルへの変換で使う。 */
    val isMastered: Boolean
        get() = intervalDays >= MASTERED_INTERVAL_DAYS

    /** [isMastered] を intervalDays に変換した値を返す。 */
    fun intervalDaysFor(mastered: Boolean): Int =
        if (mastered) MASTERED_INTERVAL_DAYS else UNMASTERED_INTERVAL_DAYS

    companion object {
        /** 未マスター（青カエル未済み）の intervalDays。 */
        const val UNMASTERED_INTERVAL_DAYS = 1

        /** マスター済み（青カエル済み）の intervalDays。 */
        const val MASTERED_INTERVAL_DAYS = 8
    }
}
