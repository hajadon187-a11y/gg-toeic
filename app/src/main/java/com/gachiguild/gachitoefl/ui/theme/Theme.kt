package com.gachiguild.gachitoefl.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.intl.Locale
import androidx.compose.ui.text.intl.LocaleList

// ── TOEFL ブルー（ライトテーマ） ──
private val BluePrimary = Color(0xFF1976D2)
private val BlueSecondary = Color(0xFF64B5F6)
private val BlueTertiary = Color(0xFF90CAF9)
private val BlueBackground = Color(0xFFF4F8FC)
private val BlueSurface = Color(0xFFEAF3FB)
private val BlueSurfaceVariant = Color(0xFFD9EAF7)
private val BlueOnPrimary = Color(0xFFFFFFFF)
private val BlueOnBackground = Color(0xFF19324A)
private val BlueOutline = Color(0xFF91B4D0)
private val BlueError = Color(0xFFBA1A1A)

private val LightBlueColors = lightColorScheme(
    primary = BluePrimary,
    onPrimary = BlueOnPrimary,
    primaryContainer = Color(0xFFD1E4FF),
    onPrimaryContainer = Color(0xFF001D36),
    inversePrimary = Color(0xFFA3C9FF),
    secondary = BlueSecondary,
    onSecondary = Color(0xFF062F4F),
    secondaryContainer = Color(0xFFC9E6FF),
    onSecondaryContainer = Color(0xFF001E32),
    tertiary = BlueTertiary,
    onTertiary = Color(0xFF07304F),
    tertiaryContainer = Color(0xFFD3E9FF),
    onTertiaryContainer = Color(0xFF062F4F),
    background = BlueBackground,
    onBackground = BlueOnBackground,
    surface = BlueSurface,
    onSurface = BlueOnBackground,
    surfaceVariant = BlueSurfaceVariant,
    onSurfaceVariant = Color(0xFF405E76),
    surfaceTint = BluePrimary,
    inverseSurface = Color(0xFF2B3137),
    inverseOnSurface = Color(0xFFEFF4FA),
    error = BlueError,
    onError = Color(0xFFFFFFFF),
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF3B0A0A),
    outline = BlueOutline,
    outlineVariant = Color(0xFFBED5E8),
    scrim = Color(0xFF000000)
)

private val DarkBlueColors = darkColorScheme(
    primary = Color(0xFF9CCAFF),
    onPrimary = Color(0xFF003258),
    primaryContainer = Color(0xFF004A7C),
    onPrimaryContainer = Color(0xFFD1E4FF),
    secondary = Color(0xFF8CC9F7),
    onSecondary = Color(0xFF003450),
    secondaryContainer = Color(0xFF145477),
    onSecondaryContainer = Color(0xFFC9E6FF),
    tertiary = Color(0xFFB5D8F8),
    onTertiary = Color(0xFF18344C),
    background = Color(0xFF101A24),
    onBackground = Color(0xFFE0EAF3),
    surface = Color(0xFF162431),
    onSurface = Color(0xFFE0EAF3),
    surfaceVariant = Color(0xFF394C5C),
    onSurfaceVariant = Color(0xFFC0D0DF),
    outline = Color(0xFF8A9BAC),
    outlineVariant = Color(0xFF394C5C),
    error = Color(0xFFFFB4AB),
    onError = Color(0xFF690005),
    errorContainer = Color(0xFF93000A),
    onErrorContainer = Color(0xFFFFDAD6)
)

private fun appTypography(textLocaleTag: String): Typography = Typography().let { typography ->
    val appFontFamily = FontFamily.SansSerif
    // CJK の漢字は、同じ Unicode 文字でも言語ごとに字形が異なる。
    // Android の sans-serif（Noto Sans CJK を含む端末標準フォント）に
    // 選択中の言語を渡して、日本語選択時は日本語字形を優先させる。
    val localeList = LocaleList(Locale(textLocaleTag))
    fun TextStyle.withAppLocale() = copy(localeList = localeList)

    typography.copy(
        displayLarge = typography.displayLarge.copy(fontFamily = appFontFamily).withAppLocale(),
        displayMedium = typography.displayMedium.copy(fontFamily = appFontFamily).withAppLocale(),
        displaySmall = typography.displaySmall.copy(fontFamily = appFontFamily).withAppLocale(),
        headlineLarge = typography.headlineLarge.copy(fontFamily = appFontFamily).withAppLocale(),
        headlineMedium = typography.headlineMedium.copy(fontFamily = appFontFamily).withAppLocale(),
        headlineSmall = typography.headlineSmall.copy(fontFamily = appFontFamily).withAppLocale(),
        titleLarge = typography.titleLarge.copy(fontFamily = appFontFamily).withAppLocale(),
        titleMedium = typography.titleMedium.copy(fontFamily = appFontFamily).withAppLocale(),
        titleSmall = typography.titleSmall.copy(fontFamily = appFontFamily).withAppLocale(),
        bodyLarge = typography.bodyLarge.copy(fontFamily = appFontFamily).withAppLocale(),
        bodyMedium = typography.bodyMedium.copy(fontFamily = appFontFamily).withAppLocale(),
        bodySmall = typography.bodySmall.copy(fontFamily = appFontFamily).withAppLocale(),
        labelLarge = typography.labelLarge.copy(fontFamily = appFontFamily).withAppLocale(),
        labelMedium = typography.labelMedium.copy(fontFamily = appFontFamily).withAppLocale(),
        labelSmall = typography.labelSmall.copy(fontFamily = appFontFamily).withAppLocale()
    )
}

@Composable
fun AITOEFLCoachTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    textLocaleTag: String = "ja-JP",
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkBlueColors else LightBlueColors
    MaterialTheme(
        colorScheme = colors,
        typography = appTypography(textLocaleTag),
        content = content
    )
}
