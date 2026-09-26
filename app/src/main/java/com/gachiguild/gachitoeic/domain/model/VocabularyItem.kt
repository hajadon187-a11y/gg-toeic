package com.gachiguild.gachitoeic.domain.model

import java.util.Locale

data class VocabularyItem(
    val id: Long = 0,
    val stableKey: String = "",
    val word: String,
    val wordUk: String = "",
    val phoneticUk: String = "",
    val meaning: String,
    val meaningEn: String = "",
    val meaningZh: String = "",
    val meaningHi: String = "",
    val meaningVi: String = "",
    val meaningKo: String = "",
    val meaningId: String = "",
    val meaningTh: String = "",
    val meaningEs: String = "",
    val synonyms: List<String> = emptyList(),
    val collocations: List<String> = emptyList(),
    val example: String,
    val isFavorite: Boolean = false,
    /**
     * 青カエルのマスター済みかどうか。
     *
     * 未マスター／マスター済みの2状態だけを扱う。単語カードタブは未マスターのみを
     * 出題し、星タブはお気に入りを TOEIC レベルに関係なく出題する。
     * 旧データの intervalDays（1 = 未マスター / 8 = マスター済み）から変換する。
     */
    val isMastered: Boolean = false,
    val level: Int = 2,
    val topic: String = "General"
) {
    /** Returns the translation for the selected app language. Non-Japanese languages fall back to English. */
    fun meaningFor(languageCode: String): String {
        // 設定やバックアップ由来の zh-CN / ko-KR なども基本言語コードとして扱う。
        val baseLanguage = languageCode.trim().lowercase(Locale.ROOT)
            .substringBefore('-')
            .substringBefore('_')
        val englishFallback = meaningEn.ifBlank { word }

        // 翻訳処理の失敗で、日本語の意味が別言語欄に入っているデータがある。
        // ベトナム語・インドネシア語はラテン文字を使うため、日本語・中国語などの文字が入った値も英語へ戻す。
        fun localizedOrEnglish(localized: String): String {
            val containsJapaneseKana = localized.any { it in '\u3040'..'\u30ff' }
            val containsNonLatinScript = localized.any {
                it in '\u3400'..'\u9fff' ||
                    it in '\uac00'..'\ud7af' ||
                    it in '\u0900'..'\u097f'
            }
            val hasLatinLetter = localized.any {
                it in 'A'..'Z' || it in 'a'..'z' || it in '\u00c0'..'\u024f'
            }
            val invalidLatinLanguage = (baseLanguage == "vi" || baseLanguage == "id") &&
                (!hasLatinLetter || containsNonLatinScript)

            return if (localized.isBlank() || containsJapaneseKana || invalidLatinLanguage) {
                englishFallback
            } else {
                localized
            }
        }

        return when (baseLanguage) {
        "ja" -> meaning
        "en" -> englishFallback
        "zh" -> localizedOrEnglish(meaningZh)
        "hi" -> localizedOrEnglish(meaningHi)
        "vi" -> localizedOrEnglish(meaningVi)
        "ko" -> localizedOrEnglish(meaningKo)
        "id" -> localizedOrEnglish(meaningId)
        "th" -> localizedOrEnglish(meaningTh)
        "es" -> localizedOrEnglish(meaningEs)
        else -> englishFallback
        }
    }
}
