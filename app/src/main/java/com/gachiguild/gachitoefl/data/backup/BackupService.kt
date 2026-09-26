package com.gachiguild.gachitoefl.data.backup

import androidx.room.withTransaction
import com.gachiguild.gachitoefl.BuildConfig
import com.gachiguild.gachitoefl.data.local.AppDatabase
import com.gachiguild.gachitoefl.data.local.UserPreferences
import com.gachiguild.gachitoefl.data.local.entity.StudySettingEntity
import com.gachiguild.gachitoefl.data.local.entity.StudyStreakEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity
import com.gachiguild.gachitoefl.data.local.entity.VocabularyHistoryEntity
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.OutputStream
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import javax.inject.Inject
import javax.inject.Singleton
import org.json.JSONArray
import org.json.JSONObject

data class BackupDocument(
    val createdAt: Long,
    val appVersion: String,
    val vocabulary: List<BackupVocabulary>,
    val history: List<BackupHistory>,
    val dailyTarget: Int?,
    val streak: BackupStreak?,
    val preferences: BackupPreferences
) {
    companion object
}

data class BackupVocabulary(
    val stableKey: String,
    val word: String,
    val wordUk: String,
    val phoneticUk: String,
    val meaning: String,
    val meaningEn: String,
    val meaningZh: String,
    val meaningHi: String,
    val meaningVi: String,
    val meaningKo: String,
    val meaningId: String,
    val meaningTh: String = "",
    val meaningEs: String = "",
    val synonyms: String,
    val collocations: String,
    val example: String,
    val isFavorite: Boolean,
    /**
     * 旧・次回レビュー日時。現在は参照も更新もしない。
     *
     * 既存バックアップの JSON と互換のためフィールドだけ残す。
     */
    val nextReviewAt: Long = System.currentTimeMillis(),
    /**
     * 習熟度。8 = マスター済み、それ以外 = 未マスター。
     * マジックナンバーを避けるため [VocabularyEntity] の定数を使う。
     */
    val intervalDays: Int = VocabularyEntity.UNMASTERED_INTERVAL_DAYS,
    val level: Int,
    val topic: String
) {
    fun toEntity(id: Long = 0): VocabularyEntity = VocabularyEntity(
        id = id,
        stableKey = stableKey,
        word = word,
        wordUk = wordUk,
        phoneticUk = phoneticUk,
        meaning = meaning,
        meaningEn = meaningEn,
        meaningZh = meaningZh,
        meaningHi = meaningHi,
        meaningVi = meaningVi,
        meaningKo = meaningKo,
        meaningId = meaningId,
        meaningTh = meaningTh,
        meaningEs = meaningEs,
        synonyms = synonyms,
        collocations = collocations,
        example = example,
        isFavorite = isFavorite,
        nextReviewAt = nextReviewAt,
        intervalDays = intervalDays,
        level = level,
        topic = topic
    )

    companion object {
        /**
         * エンティティからバックアップ DTO を作る。
         *
         * 旧カラム（nextReviewAt / intervalDays）はバックアップ JSON の互換のため
         * 意図的にそのまま引き継ぐので、非推奨警告を抑止する。
         */
        @Suppress("DEPRECATION")
        fun fromEntity(entity: VocabularyEntity, stableKey: String = entity.stableKey) = BackupVocabulary(
            stableKey = stableKey,
            word = entity.word,
            wordUk = entity.wordUk,
            phoneticUk = entity.phoneticUk,
            meaning = entity.meaning,
            meaningEn = entity.meaningEn,
            meaningZh = entity.meaningZh,
            meaningHi = entity.meaningHi,
            meaningVi = entity.meaningVi,
            meaningKo = entity.meaningKo,
            meaningId = entity.meaningId,
            meaningTh = entity.meaningTh,
            meaningEs = entity.meaningEs,
            synonyms = entity.synonyms,
            collocations = entity.collocations,
            example = entity.example,
            isFavorite = entity.isFavorite,
            nextReviewAt = entity.nextReviewAt,
            intervalDays = entity.intervalDays,
            level = entity.level,
            topic = entity.topic
        )
    }
}

data class BackupHistory(
    val stableKey: String,
    val actionType: String,
    val timestamp: Long
){
    companion object
}

data class BackupStreak(
    val currentStreak: Int,
    val lastCompletedDate: String?,
    val recoveryDate: String? = null,
    val recoveryTickets: Int = 0,
    val lastTicketAwardedStreak: Int = 0
) {
    companion object
}

data class BackupPreferences(
    val languageCode: String,
    val accentCode: String,
    val darkMode: Boolean
)

data class RestoreResult(
    val vocabularyCount: Int,
    val historyCount: Int,
    val favoriteCount: Int
)

/** 暗号化なしの、アプリ独自ポータブルバックアップを扱う。 */
@Singleton
class BackupService @Inject constructor(
    private val database: AppDatabase,
    private val userPreferences: UserPreferences
) {
    suspend fun writeBackup(output: OutputStream) {
        val vocabulary = database.studyContentDao().getAllVocabulary()
        val idToStableKey = vocabulary.associate { it.id to stableKeyFor(it) }
        val history = database.studyContentDao().getAllHistory().mapNotNull { entity ->
            idToStableKey[entity.wordId]?.let { stableKey ->
                BackupHistory(stableKey, entity.actionType, entity.timestamp)
            }
        }
        val setting = database.studySettingDao().getSetting()
        val streak = database.studyStreakDao().getStreak()

        val document = BackupDocument(
            createdAt = System.currentTimeMillis(),
            appVersion = BuildConfig.VERSION_NAME,
            vocabulary = vocabulary.map { BackupVocabulary.fromEntity(it, stableKeyFor(it)) },
            history = history,
            dailyTarget = setting?.dailyTarget,
            streak = streak?.let {
                BackupStreak(
                    currentStreak = it.currentStreak,
                    lastCompletedDate = it.lastCompletedDate,
                    recoveryDate = it.recoveryDate,
                    recoveryTickets = it.recoveryTickets,
                    lastTicketAwardedStreak = it.lastTicketAwardedStreak
                )
            },
            preferences = BackupPreferences(
                languageCode = userPreferences.getLanguageCode(),
                accentCode = userPreferences.getAccentMode().code,
                darkMode = userPreferences.isDarkMode()
            )
        )

        val compressed = ByteArrayOutputStream().also { buffer ->
            GZIPOutputStream(buffer).use { gzip ->
                gzip.write(document.toJson().toString().toByteArray(Charsets.UTF_8))
            }
        }.toByteArray()
        output.use { it.write(compressed) }
    }

    suspend fun readBackup(input: InputStream): BackupDocument {
        val compressed = input.use { it.readLimited(MAX_BACKUP_BYTES) }
        val json = GZIPInputStream(ByteArrayInputStream(compressed))
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }
        return BackupDocument.fromJson(JSONObject(json))
    }

    suspend fun restore(document: BackupDocument): RestoreResult {
        require(document.vocabulary.all { it.stableKey.isNotBlank() }) {
            "バックアップ内に単語キーがありません。"
        }
        require(document.vocabulary.map { it.stableKey }.distinct().size == document.vocabulary.size) {
            "バックアップ内の単語キーが重複しています。"
        }

        val resolvedIds = mutableMapOf<String, Long>()
        database.withTransaction {
            val contentDao = database.studyContentDao()
            val favoriteDao = database.favoriteDao()

            // レストアは「置き換え」。現在のユーザー追加単語と履歴も除去する。
            contentDao.resetLearningState()
            contentDao.deleteCustomVocabulary()
            contentDao.deleteAllHistory()
            favoriteDao.deleteAll()

            // カスタム単語を削除した後の、現在の固定語彙だけをキーで引けるようにする。
            val currentByStableKey = contentDao.getAllVocabulary().associateBy { it.stableKey }

            document.vocabulary.forEach { backup ->
                val current = currentByStableKey[backup.stableKey]
                val resolvedId = if (current == null) {
                    val insertedId = contentDao.insertVocabulary(backup.toEntity())
                    if (insertedId > 0) insertedId
                    else contentDao.findVocabularyByStableKey(backup.stableKey)?.id
                } else {
                    contentDao.updateVocabulary(backup.toEntity(id = current.id))
                    current.id
                }
                resolvedId?.let { resolvedIds[backup.stableKey] = it }
            }

            val restoredHistory = document.history.mapNotNull { history ->
                resolvedIds[history.stableKey]?.let { wordId ->
                    VocabularyHistoryEntity(
                        wordId = wordId,
                        actionType = history.actionType,
                        timestamp = history.timestamp
                    )
                }
            }
            if (restoredHistory.isNotEmpty()) contentDao.insertHistoryAll(restoredHistory)

            val restoredFavorites = document.vocabulary.mapNotNull { backup ->
                if (!backup.isFavorite) return@mapNotNull null
                resolvedIds[backup.stableKey]?.let { itemId ->
                    com.gachiguild.gachitoefl.data.local.entity.FavoriteEntity(
                        itemType = "vocabulary",
                        itemId = itemId,
                        addedAt = System.currentTimeMillis()
                    )
                }
            }
            if (restoredFavorites.isNotEmpty()) favoriteDao.insertAll(restoredFavorites)

            document.dailyTarget?.let {
                database.studySettingDao().insertOrUpdate(StudySettingEntity(dailyTarget = it))
            }
            document.streak?.let {
                database.studyStreakDao().insertOrUpdate(
                    StudyStreakEntity(
                        currentStreak = it.currentStreak,
                        lastCompletedDate = it.lastCompletedDate,
                        recoveryDate = it.recoveryDate,
                        recoveryTickets = it.recoveryTickets,
                        lastTicketAwardedStreak = it.lastTicketAwardedStreak
                    )
                )
            }
        }

        userPreferences.restoreDisplaySettings(
            languageCode = document.preferences.languageCode,
            accentCode = document.preferences.accentCode,
            darkMode = document.preferences.darkMode
        )
        return RestoreResult(
            vocabularyCount = document.vocabulary.size,
            historyCount = document.history.size,
            favoriteCount = document.vocabulary.count { it.isFavorite }
        )
    }

    private fun BackupDocument.toJson(): JSONObject = JSONObject().apply {
        put("magic", MAGIC)
        put("formatVersion", FORMAT_VERSION)
        put("createdAt", createdAt)
        put("appVersion", appVersion)
        put("databaseVersion", 10)
        put("vocabulary", JSONArray().also { array -> vocabulary.forEach { array.put(it.toJson()) } })
        put("history", JSONArray().also { array -> history.forEach { array.put(it.toJson()) } })
        put("dailyTarget", dailyTarget ?: JSONObject.NULL)
        put("streak", streak?.toJson() ?: JSONObject.NULL)
        put("preferences", preferences.toJson())
    }

    private fun BackupVocabulary.toJson() = JSONObject().apply {
        put("stableKey", stableKey); put("word", word); put("wordUk", wordUk)
        put("phoneticUk", phoneticUk); put("meaning", meaning); put("meaningEn", meaningEn)
        put("meaningZh", meaningZh); put("meaningHi", meaningHi); put("meaningVi", meaningVi)
        put("meaningKo", meaningKo); put("meaningId", meaningId); put("meaningTh", meaningTh); put("meaningEs", meaningEs)
        put("synonyms", synonyms); put("collocations", collocations)
        put("example", example); put("isFavorite", isFavorite); put("nextReviewAt", nextReviewAt)
        put("intervalDays", intervalDays); put("level", level); put("topic", topic)
    }

    private fun BackupHistory.toJson() = JSONObject().apply {
        put("stableKey", stableKey); put("actionType", actionType); put("timestamp", timestamp)
    }

    private fun BackupStreak.toJson() = JSONObject().apply {
        put("currentStreak", currentStreak)
        put("lastCompletedDate", lastCompletedDate ?: JSONObject.NULL)
        put("recoveryDate", recoveryDate ?: JSONObject.NULL)
        put("recoveryTickets", recoveryTickets)
        put("lastTicketAwardedStreak", lastTicketAwardedStreak)
    }

    private fun BackupPreferences.toJson() = JSONObject().apply {
        put("languageCode", languageCode); put("accentCode", accentCode); put("darkMode", darkMode)
    }

    companion object {
        private const val MAGIC = "AITOEFL_COACH_BACKUP"
        private const val FORMAT_VERSION = 1
        private const val MAX_BACKUP_BYTES = 100L * 1024L * 1024L

        private fun stableKeyFor(entity: VocabularyEntity): String =
            entity.stableKey.ifBlank { "builtin:${entity.id}" }

        private fun BackupDocument.Companion.fromJson(root: JSONObject): BackupDocument {
            require(root.optString("magic") == MAGIC) { "このアプリのバックアップファイルではありません。" }
            require(root.optInt("formatVersion") == FORMAT_VERSION) { "対応していないバックアップ形式です。" }

            val vocabularyArray = root.optJSONArray("vocabulary")
                ?: error("バックアップに単語データがありません。")
            val historyArray = root.optJSONArray("history") ?: JSONArray()
            val preferences = root.optJSONObject("preferences")
                ?: error("バックアップに設定データがありません。")

            return BackupDocument(
                createdAt = root.optLong("createdAt"),
                appVersion = root.optString("appVersion", "unknown"),
                vocabulary = List(vocabularyArray.length()) { i -> BackupVocabulary.fromJson(vocabularyArray.getJSONObject(i)) },
                history = List(historyArray.length()) { i -> BackupHistory.fromJson(historyArray.getJSONObject(i)) },
                dailyTarget = if (root.isNull("dailyTarget")) null else root.optInt("dailyTarget"),
                streak = if (root.isNull("streak")) null else BackupStreak.fromJson(root.getJSONObject("streak")),
                preferences = BackupPreferences(
                    languageCode = preferences.optString("languageCode", "ja"),
                    accentCode = preferences.optString("accentCode", "US"),
                    darkMode = preferences.optBoolean("darkMode", false)
                )
            )
        }

        private fun BackupVocabulary.Companion.fromJson(json: JSONObject) = BackupVocabulary(
            stableKey = json.getString("stableKey"), word = json.getString("word"),
            wordUk = json.optString("wordUk", json.getString("word")), phoneticUk = json.optString("phoneticUk"),
            meaning = json.getString("meaning"), meaningEn = json.optString("meaningEn"),
            meaningZh = json.optString("meaningZh"), meaningHi = json.optString("meaningHi"),
            meaningVi = json.optString("meaningVi"), meaningKo = json.optString("meaningKo"),
            meaningId = json.optString("meaningId"),
            meaningTh = json.optString("meaningTh"),
            meaningEs = json.optString("meaningEs"),
            synonyms = json.optString("synonyms"), collocations = json.optString("collocations"),
            example = json.getString("example"), isFavorite = json.optBoolean("isFavorite", false),
            nextReviewAt = json.optLong("nextReviewAt", System.currentTimeMillis()),
            // 旧バックアップは intervalDays（1 = 未マスター / 8 = マスター済み）で保存されている。
            intervalDays = json.optInt(
                "intervalDays",
                VocabularyEntity.UNMASTERED_INTERVAL_DAYS
            ),
            level = json.optInt("level", 2),
            topic = json.optString("topic", "General")
        )

        private fun BackupHistory.Companion.fromJson(json: JSONObject) = BackupHistory(
            stableKey = json.getString("stableKey"),
            actionType = json.getString("actionType"),
            timestamp = json.getLong("timestamp")
        )

        private fun BackupStreak.Companion.fromJson(json: JSONObject) = BackupStreak(
            currentStreak = json.optInt("currentStreak", 0),
            lastCompletedDate = if (json.isNull("lastCompletedDate")) null else json.optString("lastCompletedDate"),
            recoveryDate = if (json.isNull("recoveryDate")) null else json.optString("recoveryDate"),
            recoveryTickets = json.optInt("recoveryTickets", 0),
            lastTicketAwardedStreak = json.optInt("lastTicketAwardedStreak", 0)
        )

        private fun InputStream.readLimited(maxBytes: Long): ByteArray {
            val result = ByteArrayOutputStream()
            val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
            var total = 0L
            while (true) {
                val count = read(buffer)
                if (count < 0) break
                total += count
                require(total <= maxBytes) { "バックアップファイルが大きすぎます。" }
                result.write(buffer, 0, count)
            }
            return result.toByteArray()
        }
    }
}
