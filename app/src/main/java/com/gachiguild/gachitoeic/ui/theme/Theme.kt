package com.gachiguild.gachitoeic.ui.theme

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

// ── TOEIC グリーン（ライトテーマ） ──
private val GreenPrimary = Color(0xFF2E7D32)
private val GreenSecondary = Color(0xFF66BB6A)
private val GreenTertiary = Color(0xFF81C784)
private val GreenBackground = Color(0xFFF3F8F3)
private val GreenSurface = Color(0xFFE8F5E9)
private val GreenSurfaceVariant = Color(0xFFD5EBD7)
private val GreenOnPrimary = Color(0xFFFFFFFF)
private val GreenOnBackground = Color(0xFF163B1B)
private val GreenOutline = Color(0xFF91B89A)
private val GreenError = Color(0xFFBA1A1A)

private val LightGreenColors = lightColorScheme(
    primary = GreenPrimary,
    onPrimary = GreenOnPrimary,
    primaryContainer = Color(0xFFC8E6C9),
    onPrimaryContainer = Color(0xFF0D3511),
    inversePrimary = Color(0xFFA5D6A7),
    secondary = GreenSecondary,
    onSecondary = Color(0xFF123B18),
    secondaryContainer = Color(0xFFCDE8CF),
    onSecondaryContainer = Color(0xFF163B1B),
    tertiary = GreenTertiary,
    onTertiary = Color(0xFF173B1B),
    tertiaryContainer = Color(0xFFD8EED9),
    onTertiaryContainer = Color(0xFF163B1B),
    background = GreenBackground,
    onBackground = GreenOnBackground,
    surface = GreenSurface,
    onSurface = GreenOnBackground,
    surfaceVariant = GreenSurfaceVariant,
    onSurfaceVariant = Color(0xFF426047),
    surfaceTint = GreenPrimary,
    inverseSurface = Color(0xFF29332A),
    inverseOnSurface = Color(0xFFEAF4EB),
    error = GreenError,
    onError = Color(0xFFFFFFFF),
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF3B0A0A),
    outline = GreenOutline,
    outlineVariant = Color(0xFFBED9C1),
    scrim = Color(0xFF000000)
)

private val DarkGreenColors = darkColorScheme(
    primary = Color(0xFFA5D6A7),
    onPrimary = Color(0xFF123B18),
    primaryContainer = Color(0xFF2E6A35),
    onPrimaryContainer = Color(0xFFC8E6C9),
    secondary = Color(0xFF81C784),
    onSecondary = Color(0xFF123B18),
    secondaryContainer = Color(0xFF255B2A),
    onSecondaryContainer = Color(0xFFCDE8CF),
    tertiary = Color(0xFFB7DDB9),
    onTertiary = Color(0xFF183B1C),
    background = Color(0xFF0F1A11),
    onBackground = Color(0xFFE0EEE1),
    surface = Color(0xFF14231A),
    onSurface = Color(0xFFE0EEE1),
    surfaceVariant = Color(0xFF354C39),
    onSurfaceVariant = Color(0xFFC2D6C4),
    outline = Color(0xFF8BAA8F),
    outlineVariant = Color(0xFF354C39),
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
fun GGToeicTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    textLocaleTag: String = "ja-JP",
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkGreenColors else LightGreenColors
    MaterialTheme(
        colorScheme = colors,
        typography = appTypography(textLocaleTag),
        content = content
    )
}
