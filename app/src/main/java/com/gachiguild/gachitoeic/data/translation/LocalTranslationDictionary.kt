package com.gachiguild.gachitoeic.data.translation

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.util.Locale

/**
 * ネイティブ確認済みの翻訳だけをアプリへ同梱するローカル辞書。
 *
 * 辞書キーは stableKey だけでなく原文も保持する。語彙データを更新したときに、
 * 古い翻訳を別の例文へ誤って表示しないためである。翻訳の追加は
 * assets/vocabulary_phrase_translations.json へ行い、実行時の通信は発生しない。
 */
object LocalTranslationDictionary {
    private const val ASSET_NAME = "vocabulary_phrase_translations.json"

    private data class Entry(
        val source: String,
        val translations: Map<String, String>
    )

    @Volatile
    private var entries: Map<String, Map<String, Entry>>? = null

    suspend fun lookup(
        context: Context,
        stableKey: String,
        phraseType: String,
        sourceText: String,
        targetLanguage: String
    ): String? = withContext(Dispatchers.IO) {
        val target = targetLanguage.normalizeLanguageCode()
        val source = sourceText.trim()
        if (stableKey.isBlank() || source.isBlank()) return@withContext null
        if (target == "en") return@withContext source

        val dictionary = entries ?: runCatching { load(context) }
            .getOrDefault(emptyMap())
            .also { entries = it }
        val entry = dictionary[stableKey]?.get(phraseType) ?: return@withContext null
        if (entry.source.trim() != source) return@withContext null
        entry.translations[target]?.takeIf { it.isNotBlank() }
    }

    private fun load(context: Context): Map<String, Map<String, Entry>> {
        val raw = context.assets.open(ASSET_NAME).bufferedReader(Charsets.UTF_8).use { it.readText() }
        val root = JSONObject(raw)
        val translationRoot = root.optJSONObject("translations") ?: return emptyMap()
        val result = mutableMapOf<String, Map<String, Entry>>()

        translationRoot.keys().forEach { stableKey ->
            val itemRoot = translationRoot.optJSONObject(stableKey) ?: return@forEach
            val itemEntries = mutableMapOf<String, Entry>()
            itemRoot.keys().forEach { phraseType ->
                val phraseRoot = itemRoot.optJSONObject(phraseType) ?: return@forEach
                val source = phraseRoot.optString("source").trim()
                if (source.isBlank()) return@forEach

                val translations = mutableMapOf<String, String>()
                phraseRoot.keys().forEach { key ->
                    if (key == "source") return@forEach
                    val value = phraseRoot.optString(key).trim()
                    if (value.isNotBlank()) {
                        translations[key.normalizeLanguageCode()] = value
                    }
                }
                itemEntries[phraseType] = Entry(source, translations)
            }
            result[stableKey] = itemEntries
        }
        return result
    }

    private fun String.normalizeLanguageCode(): String =
        trim().lowercase(Locale.ROOT).substringBefore('-').substringBefore('_')
}
