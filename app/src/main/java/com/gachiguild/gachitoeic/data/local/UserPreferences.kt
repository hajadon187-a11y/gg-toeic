package com.gachiguild.gachitoeic.data.local

import android.content.Context
import android.os.LocaleList
import com.gachiguild.gachitoeic.ui.AccentMode
import com.gachiguild.gachitoeic.ui.AppLanguage
import com.gachiguild.gachitoeic.presentation.viewmodel.VocabularyLevel
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * アプリ設定（SharedPreferences）の保存・読み込みを管理する。
 * - accentMode: 発音アクセント（"US" / "UK"。TOEIC向けデフォルトは "US"）
 */
@Singleton
class UserPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val prefs = context.getSharedPreferences("app_settings", Context.MODE_PRIVATE)

    companion object {
        private const val LANGUAGE_KEY = "language"
        private const val LANGUAGE_INITIALIZED_KEY = "language_initialized"
        private const val BUTTON_SOUND_ENABLED_KEY = "button_sound_enabled"
        private const val VOCABULARY_LEVEL_KEY = "vocabulary_level"
        private const val FROG_BUTTON_HELP_SHOWN_KEY = "frog_button_help_shown"
        private const val ONBOARDING_COMPLETED_KEY = "onboarding_completed"
        private const val MAIN_FEATURE_TOUR_VERSION_KEY = "main_feature_tour_version"
        // キー名は既存インストールとの互換性のため維持する。保存値はTOEIC L1〜L4。
        private const val TARGET_LEVEL_KEY = "target_level"
        private const val DEFAULT_TARGET_LEVEL = "BASIC"
        private const val AI_PROVIDER_PACKAGE_KEY = "ai_provider_package"
        private const val NOTIFICATION_PERMISSION_REQUESTED_KEY = "notification_permission_requested"
    }

    /** 発音アクセントを取得（TOEIC向けデフォルト: US） */
    fun getAccentMode(): AccentMode = when (prefs.getString("accent", "US")) {
        "US" -> AccentMode.US
        else -> AccentMode.UK
    }

    /** 発音アクセントを保存 */
    fun setAccentMode(accent: AccentMode) {
        prefs.edit().putString("accent", accent.code).apply()
    }

    /** 単語カードのフッターボタン音を取得（デフォルト: オン） */
    fun isButtonSoundEnabled(): Boolean = prefs.getBoolean(BUTTON_SOUND_ENABLED_KEY, true)

    /** 単語カードのフッターボタン音を保存 */
    fun setButtonSoundEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(BUTTON_SOUND_ENABLED_KEY, enabled).apply()
    }

    /** 学習進捗のレベルフィルターを取得（旧LEVEL1〜4/5は3段階へ移行） */
    fun getVocabularyLevel(): VocabularyLevel = runCatching {
        val storedLevel = VocabularyLevel.valueOf(
            prefs.getString(VOCABULARY_LEVEL_KEY, VocabularyLevel.LEVEL1.name)
                ?: VocabularyLevel.LEVEL1.name
        )
        storedLevel.toStudyTier()
    }.getOrDefault(VocabularyLevel.BASIC)

    /** 学習進捗のレベルフィルターを保存 */
    fun setVocabularyLevel(level: VocabularyLevel) {
        prefs.edit().putString(VOCABULARY_LEVEL_KEY, level.toStudyTier().name).apply()
    }

    /** 初回起動ガイド（カエルボタン説明）を表示済みか取得する。 */
    fun isFrogButtonHelpShown(): Boolean =
        prefs.getBoolean(FROG_BUTTON_HELP_SHOWN_KEY, false)

    /** 初回起動ガイドを表示済みとして保存する。 */
    fun setFrogButtonHelpShown() {
        prefs.edit().putBoolean(FROG_BUTTON_HELP_SHOWN_KEY, true).apply()
    }

    /** 初回オンボーディングを完了したか。 */
    fun isOnboardingCompleted(): Boolean =
        prefs.getBoolean(ONBOARDING_COMPLETED_KEY, false)

    /** 初回オンボーディングを完了済みにする。 */
    fun setOnboardingCompleted() {
        prefs.edit().putBoolean(ONBOARDING_COMPLETED_KEY, true).apply()
    }

    /** メイン画面の機能ツアーを現在のバージョンまで確認済みか。 */
    fun isMainFeatureTourCompleted(currentVersion: Int = 1): Boolean =
        prefs.getInt(MAIN_FEATURE_TOUR_VERSION_KEY, 0) >= currentVersion

    /** メイン画面の機能ツアーを確認済みにする。 */
    fun setMainFeatureTourCompleted(currentVersion: Int = 1) {
        prefs.edit().putInt(MAIN_FEATURE_TOUR_VERSION_KEY, currentVersion).apply()
    }

    /** TOEICの目標レベル（AI会話の難易度にも使用）。 */
    fun getTargetLevel(): String = when (
        prefs.getString(TARGET_LEVEL_KEY, DEFAULT_TARGET_LEVEL) ?: DEFAULT_TARGET_LEVEL
    ) {
        "BASIC", "Basic", "L1", "L2" -> "BASIC"
        "STANDARD", "Standard", "L3" -> "STANDARD"
        "ADVANCED", "Advanced", "L4" -> "ADVANCED"
        else -> DEFAULT_TARGET_LEVEL
    }

    fun setTargetLevel(level: String) {
        val normalizedLevel = when (level) {
            "STANDARD", "Standard", "L3" -> "STANDARD"
            "ADVANCED", "Advanced", "L4" -> "ADVANCED"
            else -> DEFAULT_TARGET_LEVEL
        }
        prefs.edit().putString(TARGET_LEVEL_KEY, normalizedLevel).apply()
    }

    /** 優先して起動するAIアプリのパッケージ名。 */
    fun getPreferredAiProviderPackage(): String? =
        prefs.getString(AI_PROVIDER_PACKAGE_KEY, null)

    fun setPreferredAiProviderPackage(packageName: String?) {
        prefs.edit().apply {
            if (packageName.isNullOrBlank()) remove(AI_PROVIDER_PACKAGE_KEY)
            else putString(AI_PROVIDER_PACKAGE_KEY, packageName)
        }.apply()
    }

    /** Android 13以降の通知権限リクエストを一度だけ表示するための状態。 */
    fun isNotificationPermissionRequested(): Boolean =
        prefs.getBoolean(NOTIFICATION_PERMISSION_REQUESTED_KEY, false)

    fun setNotificationPermissionRequested() {
        prefs.edit().putBoolean(NOTIFICATION_PERMISSION_REQUESTED_KEY, true).apply()
    }

    fun getLanguageCode(): String = AppLanguage.fromCode(prefs.getString(LANGUAGE_KEY, null)).code

    /**
     * 初回起動時だけ端末の優先言語をアプリの表示言語へ反映する。
     * 端末の優先言語が複数ある場合は、上位から対応言語を探す。
     */
    fun initializeLanguageIfNeeded(): String {
        if (prefs.getBoolean(LANGUAGE_INITIALIZED_KEY, false)) {
            return getLanguageCode()
        }

        // 既存インストールで既に言語が保存されている場合は、ユーザー設定を尊重する。
        val languageCode = prefs.getString(LANGUAGE_KEY, null)?.let {
            AppLanguage.fromCode(it).code
        } ?: preferredDeviceLanguageCode()

        prefs.edit()
            .putString(LANGUAGE_KEY, languageCode)
            .putBoolean(LANGUAGE_INITIALIZED_KEY, true)
            .apply()

        return languageCode
    }

    /** 言語を手動変更したことを保存し、初回自動判定を完了済みにする。 */
    fun setLanguageCode(languageCode: String) {
        prefs.edit()
            .putString(LANGUAGE_KEY, AppLanguage.fromCode(languageCode).code)
            .putBoolean(LANGUAGE_INITIALIZED_KEY, true)
            .apply()
    }

    private fun preferredDeviceLanguageCode(): String {
        val locales = LocaleList.getDefault()
        for (index in 0 until locales.size()) {
            AppLanguage.fromLocale(locales[index])?.let { return it.code }
        }
        return AppLanguage.English.code
    }

    fun isDarkMode(): Boolean = prefs.getBoolean("dark_mode", false)

    fun restoreDisplaySettings(
        languageCode: String,
        accentCode: String,
        darkMode: Boolean
    ) {
        prefs.edit()
            .putString(LANGUAGE_KEY, AppLanguage.fromCode(languageCode).code)
            .putBoolean(LANGUAGE_INITIALIZED_KEY, true)
            .putString("accent", if (accentCode == "US") "US" else "UK")
            .putBoolean("dark_mode", darkMode)
            .apply()
    }
}
