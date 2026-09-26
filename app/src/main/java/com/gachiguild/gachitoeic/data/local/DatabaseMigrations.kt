package com.gachiguild.gachitoeic.data.local

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

/** 多言語翻訳列を追加するRoomマイグレーション。既存データは空文字で安全に保持する。 */
val MIGRATION_5_6 = object : Migration(5, 6) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningZh TEXT NOT NULL DEFAULT ''")
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningHi TEXT NOT NULL DEFAULT ''")
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningVi TEXT NOT NULL DEFAULT ''")
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningKo TEXT NOT NULL DEFAULT ''")
    }
}

/** バックアップ／レストア用の端末非依存キーを追加する。 */
val MIGRATION_6_7 = object : Migration(6, 7) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN stableKey TEXT NOT NULL DEFAULT ''")
        // 既存の同梱語彙は asset の id が端末間で安定しているため、その値を利用する。
        db.execSQL("UPDATE vocabulary SET stableKey = 'builtin:' || id WHERE stableKey = ''")
        db.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS index_vocabulary_stableKey ON vocabulary(stableKey)")
    }
}

/** インドネシア語翻訳列を追加する。既存データは空文字で安全に保持する。 */
val MIGRATION_7_8 = object : Migration(7, 8) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningId TEXT NOT NULL DEFAULT ''")
    }
}

/** タイ語翻訳列を追加する。既存データは空文字で安全に保持する。 */
val MIGRATION_8_9 = object : Migration(8, 9) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningTh TEXT NOT NULL DEFAULT ''")
    }
}

/** スペイン語翻訳列を追加する。既存データは空文字で安全に保持する。 */
val MIGRATION_9_10 = object : Migration(9, 10) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE vocabulary ADD COLUMN meaningEs TEXT NOT NULL DEFAULT ''")
    }
}

/** ストリーク救済後の基準日を追加する。 */
val MIGRATION_10_11 = object : Migration(10, 11) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE study_streak ADD COLUMN recoveryDate TEXT")
    }
}

/** 7日継続ごとの救済チケット情報を追加する。 */
val MIGRATION_11_12 = object : Migration(11, 12) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE study_streak ADD COLUMN recoveryTickets INTEGER NOT NULL DEFAULT 0")
        db.execSQL("ALTER TABLE study_streak ADD COLUMN lastTicketAwardedStreak INTEGER NOT NULL DEFAULT 0")
    }
}
