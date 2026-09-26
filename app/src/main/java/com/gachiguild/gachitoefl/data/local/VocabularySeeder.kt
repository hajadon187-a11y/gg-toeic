package com.gachiguild.gachitoefl.data.local

import android.content.Context
import com.gachiguild.gachitoefl.data.local.dao.StudyContentDao
import com.gachiguild.gachitoefl.data.local.entity.VocabularyEntity
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton
import org.json.JSONArray
import org.json.JSONObject

/**
 * 語彙データを assets/vocabulary.json から読み込んで DB に投入する。
 * 静的Kotlinリストにするとコンパイル負荷が大きくなるため、JSONアセット方式を採用。
 */
@Singleton
open class VocabularySeeder @Inject constructor(
    @ApplicationContext private val context: Context,
    private val studyContentDao: StudyContentDao
) {
    /** assets/vocabulary.json から単語を読み込み、DBへ投入・内容を同期する */
    open suspend fun seedIfNeeded() {
        val vocabulary = readVocabularyJson()
        if (studyContentDao.vocabularyCount() < vocabulary.size) {
            vocabulary.forEach { (entity, _) ->
                studyContentDao.insertVocabulary(entity)
            }
        }

        // 既存端末にもアセットの内容（見出し語・訳・レベル）を反映する。
        // レストアや過去バージョンのDBではRoomの内部IDがassetのIDと異なることがあるため、
        // 端末間で不変なstableKeyで対象行を解決する。学習状態は更新対象に含めないため保持される。
        // 見出し語も同期するので、TOEFLレベル別デッキの入れ替え（プレースホルダー化）も反映される。
        val existingByStableKey = studyContentDao.getAllVocabulary().associateBy { it.stableKey }
        vocabulary.forEach { (entity, _) ->
            val existing = existingByStableKey[entity.stableKey]
            if (existing != null) {
                studyContentDao.syncVocabularyContent(
                    id = existing.id,
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
                    topic = entity.topic
                )
            }
        }
    }

    private fun readVocabularyJson(): List<Pair<VocabularyEntity, JSONObject>> {
        val raw = context.assets.open(VOCABULARY_ASSET)
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }

        val arr = JSONArray(raw)
        return List(arr.length()) { i ->
            val obj = arr.getJSONObject(i)
            VocabularyEntity(
                id = obj.optLong("id", (i + 1).toLong()),
                stableKey = "builtin:${obj.optLong("id", (i + 1).toLong())}",
                word = obj.optString("word"),
                wordUk = obj.optString("wordUk", obj.optString("word")),
                phoneticUk = obj.optString("phoneticUk"),
                meaning = obj.optString("meaning"),
                meaningEn = obj.optString("meaningEn"),
                meaningZh = obj.optString("meaningZh"),
                meaningHi = obj.optString("meaningHi"),
                meaningVi = obj.optString("meaningVi"),
                meaningKo = obj.optString("meaningKo"),
                meaningId = obj.optString("meaningId"),
                meaningTh = obj.optString("meaningTh"),
                meaningEs = obj.optString("meaningEs"),
                synonyms = obj.optString("synonyms"),
                collocations = obj.optString("collocations"),
                example = obj.optString("example"),
                // 旧データの level 5 は、現在の TOEFL L4（level 4）へ統合する。
                level = obj.optInt("level", 2).let { if (it == 5) 4 else it },
                topic = obj.optString("topic", "General")
            ) to obj
        }
    }

    companion object {
        private const val VOCABULARY_ASSET = "vocabulary.json"
    }
}
