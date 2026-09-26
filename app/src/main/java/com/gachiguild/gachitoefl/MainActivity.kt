package com.gachiguild.gachitoefl

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.core.content.ContextCompat
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.gachiguild.gachitoefl.presentation.screens.vocabulary.VocabularyScreen
import com.gachiguild.gachitoefl.data.local.UserPreferences
import com.gachiguild.gachitoefl.ui.AppLanguage
import com.gachiguild.gachitoefl.ui.ChineseStrings
import com.gachiguild.gachitoefl.ui.EnglishStrings
import com.gachiguild.gachitoefl.ui.HindiStrings
import com.gachiguild.gachitoefl.ui.IndonesianStrings
import com.gachiguild.gachitoefl.ui.JapaneseStrings
import com.gachiguild.gachitoefl.ui.KoreanStrings
import com.gachiguild.gachitoefl.ui.LocalAppStrings
import com.gachiguild.gachitoefl.ui.SpanishStrings
import com.gachiguild.gachitoefl.ui.ThaiStrings
import com.gachiguild.gachitoefl.ui.VietnameseStrings
import com.gachiguild.gachitoefl.ui.theme.AITOEFLCoachTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    companion object {
        private const val SPLASH_DURATION_MS = 2_000L
        const val EXTRA_START_LEARNING_FROM_NOTIFICATION =
            "com.gachiguild.gachitoefl.extra.START_LEARNING_FROM_NOTIFICATION"
    }

    private val notificationLearningRequest = MutableStateFlow(0)

    @Inject
    lateinit var userPreferences: UserPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        // The Android system splash treats windowSplashScreenAnimatedIcon as
        // an icon and constrains it to the platform icon frame. The actual
        // splash artwork is rendered below as a normal full-screen image.
        splashScreen.setKeepOnScreenCondition { false }

        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        if (intent.getBooleanExtra(EXTRA_START_LEARNING_FROM_NOTIFICATION, false)) {
            notificationLearningRequest.value = 1
        }

        val prefs = getSharedPreferences("app_settings", MODE_PRIVATE)
        val initialLanguageCode = userPreferences.initializeLanguageIfNeeded()

        setContent {
            var showSplash by remember { mutableStateOf(true) }
            val learningRequest by notificationLearningRequest.asStateFlow().collectAsState()
            val notificationPermissionLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.RequestPermission()
            ) { }

            LaunchedEffect(Unit) {
                delay(SPLASH_DURATION_MS)
                showSplash = false
            }

            LaunchedEffect(showSplash) {
                if (!showSplash &&
                    Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
                    ContextCompat.checkSelfPermission(
                        this@MainActivity,
                        Manifest.permission.POST_NOTIFICATIONS
                    ) != PackageManager.PERMISSION_GRANTED &&
                    !userPreferences.isNotificationPermissionRequested()
                ) {
                    userPreferences.setNotificationPermissionRequested()
                    notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }

            var isDarkMode by remember {
                mutableStateOf(prefs.getBoolean("dark_mode", false))
            }
            // 言語設定（日本語がデフォルト）
            var language by remember {
                mutableStateOf(AppLanguage.fromCode(initialLanguageCode))
            }
            val strings = when (language) {
                AppLanguage.English -> EnglishStrings
                AppLanguage.Japanese -> JapaneseStrings
                AppLanguage.Chinese -> ChineseStrings
                AppLanguage.Hindi -> HindiStrings
                AppLanguage.Vietnamese -> VietnameseStrings
                AppLanguage.Korean -> KoreanStrings
                AppLanguage.Indonesian -> IndonesianStrings
                AppLanguage.Thai -> ThaiStrings
                AppLanguage.Spanish -> SpanishStrings
            }

            val textLocaleTag = when (language) {
                AppLanguage.Japanese -> "ja-JP"
                AppLanguage.Chinese -> "zh-CN"
                AppLanguage.Korean -> "ko-KR"
                AppLanguage.Hindi -> "hi-IN"
                AppLanguage.Vietnamese -> "vi-VN"
                AppLanguage.English -> "en-US"
                AppLanguage.Indonesian -> "id-ID"
                AppLanguage.Thai -> "th-TH"
                AppLanguage.Spanish -> "es-ES"
            }

            AITOEFLCoachTheme(
                darkTheme = isDarkMode,
                textLocaleTag = textLocaleTag
            ) {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    if (showSplash) {
                        Image(
                            painter = painterResource(R.drawable.splash_flog),
                            contentDescription = null,
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Fit
                        )
                    } else {
                        CompositionLocalProvider(
                            LocalAppStrings provides strings,
                            LocalLanguageToggle provides { newValue: AppLanguage ->
                                language = newValue
                                userPreferences.setLanguageCode(newValue.code)
                            }
                        ) {
                            // 単語帳アプリ: ログイン・ダッシュボードなしで直接表示
                            VocabularyScreen(
                                userPreferences = userPreferences,
                                startLearningRequest = learningRequest
                            )
                        }
                    }
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        if (intent.getBooleanExtra(EXTRA_START_LEARNING_FROM_NOTIFICATION, false)) {
            notificationLearningRequest.value += 1
        }
    }
}

/** CompositionLocal for language switching */
val LocalLanguageToggle = compositionLocalOf<((AppLanguage) -> Unit)> { {} }
