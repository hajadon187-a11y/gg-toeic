package com.gachiguild.gachitoefl.presentation.screens.vocabulary

import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.SoundPool
import android.net.Uri
import android.speech.tts.TextToSpeech
import android.view.SoundEffectConstants
import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Style
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.core.graphics.drawable.toBitmap
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChangeIgnoreConsumed
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.Dialog
import androidx.hilt.navigation.compose.hiltViewModel
import com.gachiguild.gachitoefl.R
import com.gachiguild.gachitoefl.data.billing.PremiumBillingMessage
import com.gachiguild.gachitoefl.data.billing.PremiumBillingState
import com.gachiguild.gachitoefl.data.billing.isPremiumUnlocked
import com.gachiguild.gachitoefl.data.ai.AiAppProvider
import com.gachiguild.gachitoefl.data.ai.AiAppLauncher
import com.gachiguild.gachitoefl.data.ai.AiLaunchResult
import com.gachiguild.gachitoefl.data.ai.InstalledAiApp
import com.gachiguild.gachitoefl.data.local.UserPreferences
import com.gachiguild.gachitoefl.data.translation.LocalTranslationDictionary
import com.gachiguild.gachitoefl.domain.model.VocabularyHistory
import com.gachiguild.gachitoefl.domain.model.VocabularyItem
import com.gachiguild.gachitoefl.domain.repository.StudyStreak
import com.gachiguild.gachitoefl.domain.repository.TodayStudyProgress
import com.gachiguild.gachitoefl.domain.repository.canRecover
import com.gachiguild.gachitoefl.domain.repository.canRecoverWithTicket
import com.gachiguild.gachitoefl.domain.repository.isRecoveryAvailable
import com.gachiguild.gachitoefl.data.local.VocabularyClassifier
import com.gachiguild.gachitoefl.presentation.viewmodel.VocabularyFilter
import com.gachiguild.gachitoefl.presentation.viewmodel.VocabularyLevel
import com.gachiguild.gachitoefl.presentation.viewmodel.VocabularyProgress
import com.gachiguild.gachitoefl.presentation.viewmodel.VocabularyViewModel
import com.gachiguild.gachitoefl.presentation.viewmodel.requiresPremium
import com.gachiguild.gachitoefl.presentation.viewmodel.BackupViewModel
import com.gachiguild.gachitoefl.presentation.viewmodel.BackupUiState
import com.gachiguild.gachitoefl.presentation.viewmodel.BackupUiMessage
import com.gachiguild.gachitoefl.presentation.viewmodel.HistoryAction
import com.gachiguild.gachitoefl.ui.AccentMode
import com.gachiguild.gachitoefl.ui.AppStrings
import com.gachiguild.gachitoefl.ui.LocalAccentMode
import com.gachiguild.gachitoefl.ui.LocalAppStrings
import com.gachiguild.gachitoefl.LocalLanguageToggle
import com.gachiguild.gachitoefl.ui.AppLanguage
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale
import kotlin.math.abs
import kotlin.math.roundToInt
import kotlin.random.Random

// 単語カードのページ遷移を確定する距離。64dp は Android 上で約1cm相当。
private const val SWIPE_COMMIT_DISTANCE_BASE_DP = 64f
// 実際の確定距離の倍率。短いスワイプでも次のカードへ進めるよう、基準距離の 0.6 倍にする。
private const val SWIPE_COMMIT_DISTANCE_SCALE = 0.6f
// 単語カードのページ遷移を確定する距離（約38dp）。短いスワイプでもページ送りできる。
private val SWIPE_COMMIT_DISTANCE_DP = SWIPE_COMMIT_DISTANCE_BASE_DP * SWIPE_COMMIT_DISTANCE_SCALE
// 単語カードの回転演出に使う距離。
private const val SWIPE_ROTATION_DISTANCE_FRACTION = 0.20f
private const val SWIPE_DRAG_ROTATION_ANGLE = 12f
private const val SWIPE_EXIT_ROTATION_ANGLE = 16f
private const val PRIVACY_POLICY_URL =
    "https://hajadon187-a11y.github.io/gg-toefl-privacy-policy/"
private const val OPERATOR_EMAIL = "gachiguild@gmail.com"
private const val SWIPE_EXIT_DISTANCE = 1600f
private const val SWIPE_EXIT_DURATION_MS = 220
private const val SWIPE_POP_DURATION_MS = 160
private const val SWIPE_ACTION_BUTTON_ANIMATION_DURATION_MS = 200
/**
 * チュートリアルの長押し練習に使うサンプル単語（優先順）。
 *
 * 初回起動で誰でも意味が分かる短い語を先頭に置き、見つからない場合だけ
 * 辞書順の先頭語にフォールバックする。プレミアム（TOEFL L4）は使わない。
 */
private val TOUR_PRACTICE_WORD_CANDIDATES = listOf(
    "she"
)

private const val SWIPE_ACTION_BUTTON_MAX_SCALE = 1.5f

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VocabularyScreen(
    viewModel: VocabularyViewModel = hiltViewModel(),
    userPreferences: UserPreferences,
    startLearningRequest: Int = 0
) {
    val backupViewModel: BackupViewModel = hiltViewModel()
    val strings = LocalAppStrings.current
    val context = LocalContext.current
    DisposableEffect(context) {
        ButtonSoundController.prepare(context)
        onDispose { ButtonSoundController.release() }
    }
    DisposableEffect(Unit) {
        onDispose { PronunciationPlaybackController.shutdown() }
    }
    var showAiAppPicker by remember { mutableStateOf(false) }
    var pendingAiApp by remember { mutableStateOf<InstalledAiApp?>(null) }
    var showAiLaunchError by remember { mutableStateOf(false) }
    var targetLevel by remember { mutableStateOf(userPreferences.getTargetLevel()) }
    // 初回起動は、アプリの使い方 → 設定ガイド → AI設定の順で案内する。
    val shouldShowSettingsBeforeOnboarding =
        !userPreferences.isOnboardingCompleted() &&
            userPreferences.isMainFeatureTourCompleted()
    var showOnboarding by remember { mutableStateOf(false) }
    var showMainFeatureTour by remember {
        mutableStateOf(
            !userPreferences.isMainFeatureTourCompleted()
        )
    }
    var mainFeatureTourStepIndex by rememberSaveable { mutableIntStateOf(0) }
    var showSettingsTourAfterMain by remember { mutableStateOf(shouldShowSettingsBeforeOnboarding) }
    var showAiSetupAfterTutorial by remember { mutableStateOf(false) }
    var onboardingPage by rememberSaveable { mutableIntStateOf(0) }
    val featureTourState = remember { FeatureTourState() }
    // 長押しメニューのステップ（11/16 = index 10）で実際に操作してもらう単語。
    // TOEFL L3（プレミアム不要）から選び、購入導線には触れずに長押しと検索だけを体験してもらう。
    var tourPracticeWordItem by remember { mutableStateOf<VocabularyItem?>(null) }
    // 実操作ステップで長押しされ、単語操作メニューが開いたか。
    var tourPracticeLongPressed by remember { mutableStateOf(false) }
    // 実操作ステップで検索ダイアログを開いたか（「検索する」まで進んだか）。
    var tourPracticeSearching by remember { mutableStateOf(false) }
    /**
     * ガイド上の単語を長押ししたときに開く「単語を操作」ダイアログの対象語。
     *
     * 単語カードは説明カードの背面にあり指が届かないことがあるため、
     * ガイド上の単語を長押ししても同じダイアログを開けるようにする。
     */
    var tourPracticeDialogWord by remember { mutableStateOf<String?>(null) }
    // ガイドに表示する単語。UK スペルがあればそちらを見せる（カードの表示と同じ規則）。
    val tourPracticeWord = tourPracticeWordItem?.let { item ->
        if (item.wordUk.isNotBlank()) item.wordUk else item.word
    }
    // 長押し判定用。UK / US どちらの表記でも一致するように両方を保持する。
    val tourPracticeWordAccepted = remember(tourPracticeWordItem) {
        tourPracticeWordItem?.let { item ->
            setOf(item.word, item.wordUk)
                .filter { it.isNotBlank() }
                .map { it.lowercase() }
                .toSet()
        } ?: emptySet()
    }
    val mainFeatureTourSteps = remember(strings.languageCode, tourPracticeWord) {
        val steps = mainFeatureTourSteps(strings)
        val practiceWord = tourPracticeWord
        if (practiceWord == null) {
            steps
        } else {
            steps.map { step ->
                if (step.stepId == FeatureTourStepId.LONG_PRESS_MENU) {
                    step.copy(practiceWord = practiceWord)
                } else {
                    step
                }
            }
        }
    }
    var onboardingRefreshKey by remember { mutableIntStateOf(0) }
    val installedAiApps = remember(showAiAppPicker) {
        if (showAiAppPicker) AiAppLauncher.installedApps(context) else emptyList()
    }
    val onboardingInstalledAiApps = remember(showOnboarding, onboardingRefreshKey) {
        if (showOnboarding) AiAppLauncher.installedApps(context) else emptyList()
    }
    val backupState by backupViewModel.state.collectAsState()
    val createBackupLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/octet-stream")
    ) { uri -> uri?.let(backupViewModel::writeBackup) }
    val openBackupLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocument()
    ) { uri -> uri?.let(backupViewModel::prepareRestore) }
    val accentMode by viewModel.accentMode.collectAsState()
    val buttonSoundEnabled by viewModel.buttonSoundEnabled.collectAsState()
    val items by viewModel.filteredVocabulary.collectAsState()
    val currentFilter by viewModel.filter.collectAsState()
    val progress by viewModel.progress.collectAsState()
    val streak by viewModel.streak.collectAsState()
    val todayStudyProgress by viewModel.todayStudyProgress.collectAsState()
    val studyActivityVersion by viewModel.studyActivityVersion.collectAsState()
    var showGoalDialog by remember { mutableStateOf(false) }
    var showStreakDialog by remember { mutableStateOf(false) }
    var showSettings by remember { mutableStateOf(shouldShowSettingsBeforeOnboarding) }
    var showPremiumDialog by remember { mutableStateOf(false) }
    var showFrogButtonHelp by remember {
        // 自動表示はメイン画面ツアーに統合し、こちらはカード上のヘルプボタンから開く。
        mutableStateOf(false)
    }
    var showSpeechMutedDialog by remember { mutableStateOf(false) }
    var pendingMutedSpeech by remember { mutableStateOf<(() -> Unit)?>(null) }
    var showStreakModal by remember { mutableStateOf(0) }
    // 起動時は単語カードを表示し、学習進捗は折りたたむ
    var progressExpanded by remember { mutableStateOf(false) }
    var heatmapExpanded by rememberSaveable { mutableStateOf(true) }
    // 起動時点の目標達成状態で初期化（起動時にモーダルを表示しない）
    var lastTargetReached by remember { mutableStateOf(todayStudyProgress.isTargetReached) }
    var lastHandledStudyActivityVersion by remember { mutableIntStateOf(studyActivityVersion) }
    var pendingStudyActivity by remember { mutableStateOf(false) }
    // 実際の学習操作後に、その日の目標単語数を初めて消化した時だけモーダル表示する。
    // 起動時の初期値からDB実データへの切り替えでは表示しない。
    LaunchedEffect(studyActivityVersion, todayStudyProgress.isTargetReached) {
        if (studyActivityVersion > lastHandledStudyActivityVersion) {
            pendingStudyActivity = true
        }
        if (todayStudyProgress.isTargetReached) {
            if (pendingStudyActivity && !lastTargetReached) {
                showStreakModal = streak.currentStreak
            }
            pendingStudyActivity = false
        }
        lastHandledStudyActivityVersion = studyActivityVersion
        lastTargetReached = todayStudyProgress.isTargetReached
    }
    val selectedLevel by viewModel.selectedLevel.collectAsState()
    val premiumBillingState by viewModel.premiumBillingState.collectAsState()
    val history by viewModel.history.collectAsState()
    val allVocabulary by viewModel.allVocabulary.collectAsState()
    val featureTourLevelWordCounts = remember(allVocabulary) {
        mapOf(
            "BASIC" to allVocabulary.count {
                VocabularyLevel.BASIC.matchesVocabularyItemLevel(it.level)
            },
            "STANDARD" to allVocabulary.count {
                VocabularyLevel.STANDARD.matchesVocabularyItemLevel(it.level)
            },
            "ADVANCED" to allVocabulary.count {
                VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(it.level)
            }
        )
    }
    val heatmapData by viewModel.heatmapData.collectAsState()
    var searchQuery by remember { mutableStateOf("") }
    var showWordCardSearchDialog by remember { mutableStateOf(false) }
    var wordSearchInitialQuery by remember { mutableStateOf("") }
    // 検索ダイアログで 6.5+ の単語を選んだとき、検索ダイアログが閉じた後に
    // プレミアム購入ガイドを表示するためのフラグ。
    var pendingPremiumGuideFromSearch by remember { mutableStateOf(false) }
    var requestedWordCardId by remember { mutableStateOf<Long?>(null) }
    // カエルタップ時に単語カードの現在位置・裏面表示も初期化するためのキー。
    var screenResetKey by remember { mutableStateOf(0) }

    // 起動時に Google Play の購入済み商品を確認し、6.5+ の解放状態を復元する。
    LaunchedEffect(Unit) {
        viewModel.refreshPremiumAccess()
    }

    fun resetToStartupState() {
        viewModel.resetToStartupState()
        progressExpanded = false
        heatmapExpanded = true
        searchQuery = ""
        showWordCardSearchDialog = false
        wordSearchInitialQuery = ""
        pendingPremiumGuideFromSearch = false
        requestedWordCardId = null
        showGoalDialog = false
        showStreakDialog = false
        showSettings = false
        showFrogButtonHelp = false
        showStreakModal = 0
        screenResetKey++
    }

    fun dismissFrogButtonHelp() {
        showFrogButtonHelp = false
        userPreferences.setFrogButtonHelpShown()
    }

    fun finishMainFeatureTour() {
        userPreferences.setMainFeatureTourCompleted()
        showMainFeatureTour = false
        if (userPreferences.isOnboardingCompleted()) {
            // 既存ユーザーも、アプリの使い方の後に設定説明を表示する。
            showSettings = true
            showSettingsTourAfterMain = true
        } else {
            // 新規ユーザーは、設定説明の後にAI設定を含むオンボーディングへ進む。
            showSettings = true
            showSettingsTourAfterMain = true
        }
    }

    fun skipMainFeatureTour() {
        userPreferences.setMainFeatureTourCompleted()
        showMainFeatureTour = false
        if (userPreferences.isOnboardingCompleted()) {
            if (showAiSetupAfterTutorial) {
                showSettings = true
                showSettingsTourAfterMain = true
            } else {
                showSettingsTourAfterMain = false
            }
        } else {
            // ツアーをスキップしても、設定説明の後にAI設定を案内する。
            showSettings = true
            showSettingsTourAfterMain = true
        }
    }

    fun selectFlashcardTab() {
        progressExpanded = false
        requestedWordCardId = null
        viewModel.setFilter(VocabularyFilter.REVIEW)
        searchQuery = ""
    }

    // 21:00の通知をタップした場合は、設定や履歴ではなく未マスター単語カードを開く。
    LaunchedEffect(startLearningRequest) {
        if (startLearningRequest > 0) {
            showOnboarding = false
            showMainFeatureTour = false
            showSettings = false
            showGoalDialog = false
            showStreakDialog = false
            showStreakModal = 0
            selectFlashcardTab()
            screenResetKey++
        }
    }

    /**
     * チュートリアルの長押しメニューで使う TOEFL L3 の単語を先頭カードに差し込む。
     *
     * 表示は発音アクセント設定に従う（UK なら UK スペル）ため、長押し判定で
     * 表記ゆれに悩まされないよう、判定用に両方のスペルを保持する。
     * レベルフィルターは変更しないため、ツアー終了後の学習デッキは元のまま保たれる。
     */
    fun showTourPracticeWordCard(item: VocabularyItem) {
        selectFlashcardTab()
        tourPracticeWordItem = item
        requestedWordCardId = item.id
        screenResetKey++
    }

    fun selectFavoritesTab() {
        progressExpanded = false
        requestedWordCardId = null
        viewModel.setFilter(VocabularyFilter.FAVORITES)
        searchQuery = ""
        // お気に入りタブを開くたびに、全レベルのお気に入りデッキを作り直す。
        screenResetKey++
    }

    fun selectHistoryTab(expandHeatmap: Boolean = false) {
        viewModel.setFilter(VocabularyFilter.HISTORY)
        progressExpanded = false
        heatmapExpanded = expandHeatmap
        searchQuery = ""
    }

    fun openSearchedWordCard(item: VocabularyItem) {
        // 虫眼鏡検索は全レベルを対象にするため、選択した単語のレベルを
        // 画面側のレベルフィルターにも反映して、選択状態を揃える。
        viewModel.setLevelFilter(targetLevelToVocabularyLevel(vocabularyItemLevel(item.level)))
        selectFlashcardTab()
        requestedWordCardId = item.id
        showWordCardSearchDialog = false
        wordSearchInitialQuery = ""
        // 同じ単語を続けて検索した場合でもカードを先頭から開き直す。
        screenResetKey++
    }

    /**
     * 検索ダイアログから単語が選ばれたときの入口。
     *
     * TOEFL L4 はプレミアム対象のため、未購入なら単語カードを開かずに
     * 購入ガイド（PremiumPurchaseDialog）を表示して解放を案内する。
     */
    fun onSearchedWordSelected(item: VocabularyItem) {
        val isLocked = isPremiumLevelItem(item.level) &&
            !premiumBillingState.isPremiumUnlocked()
        if (isLocked) {
            // 検索ダイアログを閉じてから購入ガイドを出す（ダイアログの重なりを避ける）。
            pendingPremiumGuideFromSearch = true
            showWordCardSearchDialog = false
            wordSearchInitialQuery = ""
            return
        }
        openSearchedWordCard(item)
    }

    fun startLearningFromOnboarding() {
        // AI設定を後回しにしても、現在の目標レベルで単語カード学習を始められるようにする。
        userPreferences.setTargetLevel(targetLevel)
        viewModel.setLevelFilter(targetLevelToVocabularyLevel(targetLevel))
        userPreferences.setOnboardingCompleted()
        showOnboarding = false
        showSettings = false
        showAiSetupAfterTutorial = false
        selectFlashcardTab()
        // 復習対象デッキを再生成し、ランダムな1語を先頭に表示する。
        screenResetKey++
    }

    fun finishSettingsTour() {
        val shouldContinue = showSettingsTourAfterMain &&
            (showAiSetupAfterTutorial || !userPreferences.isOnboardingCompleted())
        showSettingsTourAfterMain = false
        if (shouldContinue) {
            showSettings = false
            onboardingPage = 0
            showOnboarding = true
        }
    }

    fun dismissSettings() {
        val shouldContinue = showSettingsTourAfterMain &&
            (showAiSetupAfterTutorial || !userPreferences.isOnboardingCompleted())
        showSettingsTourAfterMain = false
        showSettings = false
        if (shouldContinue) {
            onboardingPage = 0
            showOnboarding = true
        }
    }

    // 5/16〜9/16は進捗エリアを展開して、検索／レベル／ストリーク／今日の学習の対象枠を表示する。
    // 単語カード関連のステップ（10/16〜13/16）は、必ず単語カードタブから開始する。
    LaunchedEffect(showMainFeatureTour, mainFeatureTourStepIndex) {
        if (showMainFeatureTour) {
            when {
                mainFeatureTourStepIndex in 4..8 -> progressExpanded = true
                mainFeatureTourStepIndex in 9..12 -> selectFlashcardTab()
                mainFeatureTourStepIndex == 14 -> selectHistoryTab(expandHeatmap = true)
                mainFeatureTourStepIndex < 4 -> progressExpanded = false
            }
        }
    }

    // 長押しメニューのステップ（11/16 = index 10）では、実操作しやすいサンプル単語をカードに出す。
    // TOEFL L4（プレミアム）だと解放が必要になり離脱しやすいため、購入導線には触れずに長押しと検索だけを体験してもらう。
    // selectFlashcardTab() が requestedWordCardId をクリアするため、必ずその後に設定する。
    val tourLongPressPracticeActive = showMainFeatureTour && mainFeatureTourStepIndex == 10
    LaunchedEffect(tourLongPressPracticeActive, allVocabulary) {
        if (!tourLongPressPracticeActive) {
            tourPracticeWordItem = null
            tourPracticeLongPressed = false
            tourPracticeSearching = false
            return@LaunchedEffect
        }
        // レベルフィルターは変更せず、カード先頭に差し込むサンプル単語だけを選ぶ。
        // プレミアム（TOEFL L4）は使わない。見つからない時だけ辞書順の先頭語にフォールバックする。
        val practiceWord = TOUR_PRACTICE_WORD_CANDIDATES
            .firstNotNullOfOrNull { candidate ->
                allVocabulary.firstOrNull {
                    !isPremiumLevelItem(it.level) && it.word.equals(candidate, ignoreCase = true)
                }
            }
            ?: allVocabulary
                .filterNot { isPremiumLevelItem(it.level) }
                .minByOrNull { it.word.lowercase() }
        if (practiceWord != null) {
            showTourPracticeWordCard(practiceWord)
        }
    }

    // 進捗カテゴリ／レベルを変更した時は、単語カードのデッキと現在位置を作り直す。
    // 単語カード内の学習結果更新ではキーを変えず、スワイプ中のデッキを維持する。
    fun refreshFlashcardDeck() {
        screenResetKey++
    }

    // 発音アクセントと発音ミュート状態を配下のコンポーザブルに提供
    CompositionLocalProvider(
        LocalAccentMode provides accentMode,
        LocalPronunciationSettings provides PronunciationSettings(
            enabled = buttonSoundEnabled,
            onMuted = { speechAction ->
                pendingMutedSpeech = speechAction
                showSpeechMutedDialog = true
            }
        )
    ) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.background,
                        MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.25f)
                    )
                )
            )
    ) {
    Scaffold(
        topBar = {
            TopAppBar(
                // ヘッダーの上下余白を抑えて、単語カードの表示領域を確保する。
                expandedHeight = 52.dp,
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        AnimatedFrogIcon(
                            contentDescription = strings.vocabulary,
                            modifier = Modifier
                                .size(width = 44.dp, height = 36.dp)
                                .featureTourTarget(featureTourState, "frog_header")
                                .clickable { resetToStartupState() },
                        )
                        Column(
                            verticalArrangement = Arrangement.spacedBy(0.dp),
                            horizontalAlignment = Alignment.Start
                        ) {
                            Text(
                                text = "TOEFL",
                                style = MaterialTheme.typography.labelSmall,
                                fontSize = 10.sp,
                                lineHeight = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = strings.vocabulary,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                maxLines = 1
                            )
                        }
                    }
                },
                actions = {
                    // 発音アクセント切り替え（🇬🇧 ⇄ 🇺🇸）
                    IconButton(
                        onClick = { viewModel.toggleAccent() },
                        modifier = Modifier.featureTourTarget(featureTourState, "accent_button")
                    ) {
                        Text(
                            text = if (accentMode == AccentMode.UK) "🇬🇧" else "🇺🇸",
                            style = MaterialTheme.typography.labelLarge.copy(fontSize = 21.sp),
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    // 単語カードのボタン音と発音音声を切り替え
                    IconButton(
                        onClick = {
                            // ミュートに切り替える時は、再生中・準備中の発音もすぐに中断する。
                            if (buttonSoundEnabled) {
                                PronunciationPlaybackController.stop()
                            }
                            viewModel.toggleButtonSound()
                        },
                        modifier = Modifier.featureTourTarget(featureTourState, "sound_button")
                    ) {
                        Icon(
                            imageVector = if (buttonSoundEnabled) Icons.Filled.VolumeUp else Icons.Filled.VolumeOff,
                            contentDescription = if (buttonSoundEnabled) strings.buttonSoundOn else strings.buttonSoundOff
                        )
                    }
                    // ⚙️設定ボタン（言語・ライセンス・バックアップ等）
                    IconButton(
                        onClick = { showSettings = true },
                        modifier = Modifier.featureTourTarget(featureTourState, "settings_button")
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Settings,
                            contentDescription = strings.settings,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant,
                    titleContentColor = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )
        },
        bottomBar = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .navigationBarsPadding()
            ) {
                // フィルタータブ（フッター位置・親指で操作しやすくする）
                val tabOrder = listOf(
                    VocabularyFilter.REVIEW,
                    VocabularyFilter.FAVORITES,
                    VocabularyFilter.HISTORY
                )
                val selectedTabIndex = if (showAiAppPicker) {
                    3
                } else {
                    tabOrder.indexOf(currentFilter).coerceAtLeast(0)
                }
                TabRow(
                    // タブ部分だけ少しコンパクトにして、下の案内行も含めて高さを抑える。
                    modifier = Modifier.height(70.dp),
                    selectedTabIndex = selectedTabIndex,
                    containerColor = MaterialTheme.colorScheme.secondary
                ) {
                    Tab(
                        selected = currentFilter == VocabularyFilter.REVIEW,
                        modifier = Modifier.featureTourTarget(featureTourState, "flashcard_tab"),
                        onClick = ::selectFlashcardTab,
                        icon = {
                            Icon(
                                imageVector = Icons.Filled.Style,
                                contentDescription = strings.vocabFlashcard,
                                modifier = Modifier.size(48.dp)
                            )
                        }
                    )
                    Tab(
                        selected = currentFilter == VocabularyFilter.FAVORITES,
                        modifier = Modifier.featureTourTarget(featureTourState, "favorites_tab"),
                        onClick = ::selectFavoritesTab,
                        icon = {
                            Icon(
                                imageVector = Icons.Filled.Star,
                                contentDescription = when {
                                    strings.isJapanese -> "お気に入り"
                                    strings.languageCode == "th" -> "รายการโปรด"
                                    else -> "Favorite"
                                },
                                modifier = Modifier.size(48.dp)
                            )
                        }
                    )
                    Tab(
                        selected = currentFilter == VocabularyFilter.HISTORY,
                        modifier = Modifier.featureTourTarget(featureTourState, "history_tab"),
                        onClick = { selectHistoryTab(expandHeatmap = true) },
                        icon = {
                            Icon(
                                imageVector = Icons.Filled.History,
                                contentDescription = strings.history,
                                modifier = Modifier.size(48.dp)
                            )
                        }
                    )
                    Tab(
                        selected = showAiAppPicker,
                        modifier = Modifier
                            .featureTourTarget(featureTourState, "ai_tab")
                            .then(
                                if (showOnboarding && onboardingPage == 0) {
                                    Modifier.border(
                                        width = 3.dp,
                                        color = MaterialTheme.colorScheme.error,
                                        shape = RoundedCornerShape(10.dp)
                                    )
                                } else {
                                    Modifier
                                }
                            ),
                        onClick = {
                            val availableApps = AiAppLauncher.installedApps(context)
                            val preferredApp = userPreferences.getPreferredAiProviderPackage()
                                ?.let { preferredPackage ->
                                    availableApps.firstOrNull { it.packageName == preferredPackage }
                                }
                            if (preferredApp != null) {
                                pendingAiApp = preferredApp
                                showAiLaunchError = false
                            } else {
                                pendingAiApp = null
                                showAiLaunchError = false
                                showAiAppPicker = true
                            }
                        },
                        icon = {
                            Image(
                                painter = painterResource(R.drawable.ai_profile_blue),
                                contentDescription = strings.aiApps,
                                modifier = Modifier.size(48.dp),
                                contentScale = ContentScale.Fit
                            )
                        }
                    )
                }
                Text(
                    text = "© 2026 Gachi Guild",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(16.dp),
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.labelSmall,
                    fontSize = 12.sp,
                    lineHeight = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // 学習進捗バー（カードタップでカテゴリ別一覧を表示）
            VocabularyProgressSection(
                progress = progress,
                streak = streak,
                todayStudyProgress = todayStudyProgress,
                strings = strings,
                selectedLevel = selectedLevel,
                premiumUnlocked = premiumBillingState.isPremiumUnlocked(),
                onLevelSelected = {
                    viewModel.setLevelFilter(it)
                    refreshFlashcardDeck()
                },
                onPremiumLevelClick = { showPremiumDialog = true },
                onSetDailyGoal = { viewModel.setDailyTarget(it) },
                showGoalDialog = showGoalDialog,
                onShowGoalDialog = { showGoalDialog = it },
                onShowStreakDialog = { showStreakDialog = it },
                onSearchWord = {
                    wordSearchInitialQuery = ""
                    showWordCardSearchDialog = true
                },
                expanded = progressExpanded,
                onExpandedChange = { progressExpanded = it },
                tourState = featureTourState
            )
            if (showWordCardSearchDialog) {
                WordCardSearchDialog(
                    vocabulary = allVocabulary,
                    strings = strings,
                    premiumUnlocked = premiumBillingState.isPremiumUnlocked(),
                    initialQuery = wordSearchInitialQuery,
                    onDismiss = {
                        showWordCardSearchDialog = false
                        wordSearchInitialQuery = ""
                    },
                    onWordSelected = ::onSearchedWordSelected
                )
            }
            // 検索ダイアログから 6.5+ の単語を選んだときは、ダイアログが閉じた後に
            // プレミアム購入ガイドを表示する。
            LaunchedEffect(showWordCardSearchDialog) {
                if (!showWordCardSearchDialog && pendingPremiumGuideFromSearch) {
                    pendingPremiumGuideFromSearch = false
                    showPremiumDialog = true
                }
            }
            // 設定ダイアログ
            if (showSettings) {
                SettingsDialog(
                    strings = strings,
                    backupState = backupState,
                    onDismiss = ::dismissSettings,
                    onCreateBackup = { createBackupLauncher.launch(backupViewModel.suggestedFileName()) },
                    onOpenBackup = { openBackupLauncher.launch(arrayOf("application/octet-stream", "application/gzip", "*/*")) },
                    onCancelRestore = backupViewModel::cancelRestore,
                    onConfirmRestore = backupViewModel::confirmRestore,
                    onClearBackupMessage = backupViewModel::clearMessage,
                    onRestoreCompleted = {
                        backupViewModel.clearMessage()
                        (context as? Activity)?.recreate()
                    },
                    onTutorial = {
                        showSettings = false
                        showOnboarding = false
                        showAiSetupAfterTutorial = true
                        mainFeatureTourStepIndex = 0
                        showMainFeatureTour = true
                    },
                    autoStartTour = showSettingsTourAfterMain,
                    onTourDismissed = ::finishSettingsTour
                )
            }
            if (showPremiumDialog) {
                PremiumPurchaseDialog(
                    strings = strings,
                    state = premiumBillingState,
                    premiumWordCount = allVocabulary.count {
                        VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(it.level)
                    },
                    onPurchase = {
                        (context as? Activity)?.let(viewModel::purchasePremium)
                    },
                    onRestore = viewModel::refreshPremiumAccess,
                    onDismiss = {
                        showPremiumDialog = false
                        viewModel.clearPremiumBillingMessage()
                    }
                )
            }
            if (showFrogButtonHelp) {
                FrogButtonHelpDialog(
                    strings = strings,
                    onDismiss = ::dismissFrogButtonHelp
                )
            }
            if (showSpeechMutedDialog) {
                AlertDialog(
                    onDismissRequest = {
                        showSpeechMutedDialog = false
                        pendingMutedSpeech = null
                    },
                    title = { Text(strings.speechMutedTitle, fontWeight = FontWeight.Bold) },
                    text = null,
                    confirmButton = {
                        TextButton(
                            onClick = {
                                val speechAction = pendingMutedSpeech
                                showSpeechMutedDialog = false
                                pendingMutedSpeech = null
                                speechAction?.invoke()
                            }
                        ) {
                            Text(strings.speechMutedPronounce)
                        }
                    },
                    dismissButton = {
                        TextButton(
                            onClick = {
                                showSpeechMutedDialog = false
                                pendingMutedSpeech = null
                            }
                        ) {
                            Text(strings.speechMutedOk)
                        }
                    }
                )
            }

            // ストリーク達成モーダル
            if (showStreakModal > 0) {
                AlertDialog(
                    onDismissRequest = { showStreakModal = 0 },
                    title = { Text(strings.streakModalTitle, fontWeight = FontWeight.Bold) },
                    text = {
                        Text(
                            strings.streakModalMessage.replace("%d", showStreakModal.toString())
                        )
                    },
                    confirmButton = {
                        TextButton(onClick = { showStreakModal = 0 }) {
                            Text(strings.streakModalOk)
                        }
                    }
                )
            }

            if (showOnboarding) {
                OnboardingScreen(
                    strings = strings,
                    installedApps = onboardingInstalledAiApps,
                    initialTargetBand = targetLevel,
                    initialDailyTarget = todayStudyProgress.dailyTarget,
                    initialPreferredProviderPackage = userPreferences.getPreferredAiProviderPackage(),
                    onRefreshInstalledApps = { onboardingRefreshKey++ },
                    onOpenStore = { provider ->
                        AiAppLauncher.openStore(context, provider)
                    },
                    onProviderSelected = { app ->
                        userPreferences.setPreferredAiProviderPackage(app?.packageName)
                    },
                    onAiPractice = { app ->
                        when (AiAppLauncher.launch(context, app)) {
                            is AiLaunchResult.Launched -> true
                            is AiLaunchResult.Failed -> {
                                showAiLaunchError = true
                                false
                            }
                        }
                    },
                    onStartLearning = ::startLearningFromOnboarding,
                    onOpenPrivacyPolicy = {
                        runCatching {
                            context.startActivity(
                                Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACY_POLICY_URL))
                            )
                        }
                    },
                    onComplete = { selectedTargetBand, selectedDailyTarget, selectedProvider ->
                        targetLevel = selectedTargetBand
                        userPreferences.setTargetLevel(selectedTargetBand)
                        selectedProvider?.let {
                            userPreferences.setPreferredAiProviderPackage(it.packageName)
                        }
                        viewModel.setDailyTarget(selectedDailyTarget)
                        viewModel.setLevelFilter(targetLevelToVocabularyLevel(selectedTargetBand))
                        // AI連携を完了した後も、学習は単語カードタブから開始する。
                        selectFlashcardTab()
                        userPreferences.setOnboardingCompleted()
                        showOnboarding = false
                        // 設定説明はAI設定より前に完了しているため、再表示しない。
                        showSettings = false
                        showSettingsTourAfterMain = false
                        showAiSetupAfterTutorial = false
                        screenResetKey++
                    },
                    onPageChanged = { onboardingPage = it }
                )
            }

            if (currentFilter == VocabularyFilter.HISTORY) {
                // 履歴タブ: ヒートマップ + アクション履歴を表示
                Column(modifier = Modifier.fillMaxSize()) {
                    // 🌱学習ヒートマップ
                    HeatmapView(
                        data = heatmapData,
                        strings = strings,
                        expanded = heatmapExpanded,
                        onExpandedChange = { heatmapExpanded = it },
                        modifier = Modifier.featureTourTarget(featureTourState, "heatmap_area")
                    )
                    // アクション履歴
                    HistoryList(
                        history = history,
                        vocabulary = allVocabulary,
                        strings = strings,
                        modifier = Modifier.weight(1f),
                        onFavoriteToggle = { viewModel.toggleFavorite(it) },
                        onToggleMastered = { viewModel.toggleMastered(it) }
                    )
                }
            } else {
                // 検索バー（単語カードタブ・お気に入りタブでは非表示）
                if (currentFilter != VocabularyFilter.REVIEW &&
                    currentFilter != VocabularyFilter.FAVORITES
                ) {
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = {
                            searchQuery = it
                            viewModel.setSearchQuery(it)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            // 検索欄の上下余白を抑えてリストの表示領域を確保する。
                            .padding(horizontal = 16.dp, vertical = 0.dp),
                        placeholder = { Text(strings.search) },
                        leadingIcon = { Text("🔍") },
                        trailingIcon = {
                            if (searchQuery.isNotEmpty()) {
                                IconButton(onClick = {
                                    searchQuery = ""
                                    viewModel.setSearchQuery("")
                                }) {
                                    Text("✕")
                                }
                            }
                        },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.primary,
                            unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant
                        )
                    )

                }

                // カテゴリ別単語一覧（進捗カードタップ時）
                Box(modifier = Modifier.weight(1f)) {
                        if (items.isEmpty()) {
                            // 単語カードタブではマスター済みで対象が空でもメッセージを表示しない
                            if (currentFilter != VocabularyFilter.REVIEW) {
                                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                    Text(
                                        text = when {
                                            strings.languageCode == "th" && currentFilter == VocabularyFilter.FAVORITES -> "ไม่มีคำศัพท์ในรายการโปรด"
                                            !strings.isJapanese && currentFilter == VocabularyFilter.FAVORITES -> "No favorite words."
                                            currentFilter == VocabularyFilter.FAVORITES -> "お気に入り登録された単語はありません。"
                                            strings.languageCode == "th" -> "ยังไม่มีคำศัพท์"
                                            !strings.isJapanese -> "No words registered."
                                            else -> "登録されている単語がありません。"
                                        },
                                        textAlign = TextAlign.Center,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        } else if (
                            currentFilter == VocabularyFilter.REVIEW ||
                                currentFilter == VocabularyFilter.FAVORITES
                        ) {
                            // 単語カード（復習タブは未マスター、お気に入りタブは全Bandのお気に入り）
                            // items は StateFlow の派生値なので、レベル選択直後に一時的に
                            // 前の一覧を返すことがある。カード用の対象は現在の選択状態から
                            // 直接作り、レベル切替時に古いデッキを再利用しない。
                            val flashcardItems = if (currentFilter == VocabularyFilter.FAVORITES) {
                                allVocabulary.filter { it.isFavorite }
                            } else {
                                allVocabulary.filter { item ->
                                    !item.isMastered &&
                                        selectedLevel.matchesVocabularyItemLevel(item.level)
                                }
                            }
                            val requestedItem = requestedWordCardId?.let { id ->
                                allVocabulary.firstOrNull { it.id == id }
                            }
                            val cardItems = if (requestedItem != null) {
                                listOf(requestedItem) + flashcardItems.filter { it.id != requestedItem.id }
                            } else {
                                flashcardItems
                            }
                            val initialDeck = remember(
                                currentFilter,
                                selectedLevel,
                                requestedWordCardId,
                                screenResetKey
                            ) {
                                // お気に入りタブを開くたびに、新しいランダム順で開始する。
                                if (currentFilter == VocabularyFilter.FAVORITES) {
                                    cardItems.shuffled()
                                } else {
                                    cardItems
                                }
                            }
                            val deckIds = remember(
                                currentFilter,
                                selectedLevel,
                                requestedWordCardId,
                                screenResetKey
                            ) {
                                if (requestedWordCardId != null && initialDeck.isNotEmpty()) {
                                    listOf(initialDeck.first().id) + initialDeck.drop(1).map { it.id }.shuffled()
                                } else if (currentFilter == VocabularyFilter.FAVORITES) {
                                    initialDeck.map { it.id }
                                } else {
                                    initialDeck.map { it.id }.shuffled()
                                }
                            }
                            var cardIndex by remember(
                                currentFilter,
                                selectedLevel,
                                requestedWordCardId,
                                screenResetKey
                            ) { mutableStateOf(0) }
                            val currentItemId = deckIds.getOrNull(cardIndex)
                            val currentItem = currentItemId?.let { id ->
                                // お気に入りカード上の★を外した直後も、現在のカードを表示し続ける。
                                allVocabulary.firstOrNull { it.id == id }
                                    ?: cardItems.firstOrNull { it.id == id }
                                    ?: initialDeck.firstOrNull { it.id == id }
                            }
                            // Tinder風カードめくり: スワイプでカードが回転しながら飛び、次のカードがデッキからポップイン
                            val scope = rememberCoroutineScope()
                            val cardOffsetX = remember(currentFilter, selectedLevel, screenResetKey) { Animatable(0f) }
                            val cardOffsetY = remember(currentFilter, selectedLevel, screenResetKey) { Animatable(0f) }
                            val cardRotation = remember(currentFilter, selectedLevel, screenResetKey) { Animatable(0f) }
                            val cardScale = remember(currentFilter, selectedLevel, screenResetKey) { Animatable(1f) }
                            var isSwiping by remember(currentFilter, selectedLevel, screenResetKey) { mutableStateOf(false) }

                            if (currentItem != null) {
                                // Tinder風スワイプ: 1回のカード遷移を最後まで完了してから、次の入力を受け付ける。
                                // 連続スワイプ中に次カードの再コンポーズが間に合わないと、
                                // 古いカードのコールバックが再度呼ばれることがあるため、
                                // itemId とロックの両方で二重処理を防ぐ。
                                fun swipeCard(
                                    direction: SwipeDirection,
                                    itemId: Long,
                                    nextCardIndex: Int,
                                    action: () -> Unit
                                ) {
                                    if (isSwiping || currentItemId != itemId) return
                                    isSwiping = true
                                    scope.launch {
                                        try {
                                            val (endX, endY, endRotation, endScale) = when (direction) {
                                                SwipeDirection.LEFT -> SwipeTarget(
                                                    -SWIPE_EXIT_DISTANCE,
                                                    0f,
                                                    -SWIPE_EXIT_ROTATION_ANGLE,
                                                    0.95f
                                                )
                                                SwipeDirection.RIGHT -> SwipeTarget(
                                                    SWIPE_EXIT_DISTANCE,
                                                    0f,
                                                    SWIPE_EXIT_ROTATION_ANGLE,
                                                    0.95f
                                                )
                                            }
                                            // 現在のカードを回転しながら画面外へスワイプ
                                            coroutineScope {
                                                launch {
                                                    cardOffsetX.animateTo(
                                                        endX,
                                                        tween(SWIPE_EXIT_DURATION_MS, easing = FastOutSlowInEasing)
                                                    )
                                                }
                                                launch {
                                                    cardOffsetY.animateTo(
                                                        endY,
                                                        tween(SWIPE_EXIT_DURATION_MS, easing = FastOutSlowInEasing)
                                                    )
                                                }
                                                launch {
                                                    cardRotation.animateTo(
                                                        endRotation,
                                                        tween(SWIPE_EXIT_DURATION_MS, easing = FastOutSlowInEasing)
                                                    )
                                                }
                                                launch {
                                                    cardScale.animateTo(
                                                        endScale,
                                                        tween(SWIPE_EXIT_DURATION_MS, easing = FastOutSlowInEasing)
                                                    )
                                                }
                                            }
                                            action()
                                            cardIndex = nextCardIndex.coerceIn(0, deckIds.size)

                                            // 次のカードをデッキ（小さめ・少し傾けた位置）からポップ表示
                                            cardOffsetX.snapTo(0f)
                                            cardOffsetY.snapTo(0f)
                                            cardRotation.snapTo(-6f)
                                            cardScale.snapTo(0.9f)
                                            coroutineScope {
                                                launch {
                                                    cardRotation.animateTo(
                                                        0f,
                                                        tween(SWIPE_POP_DURATION_MS, easing = FastOutSlowInEasing)
                                                    )
                                                }
                                                launch {
                                                    cardScale.animateTo(
                                                        1f,
                                                        tween(SWIPE_POP_DURATION_MS, easing = FastOutSlowInEasing)
                                                    )
                                                }
                                            }
                                        } finally {
                                            // アニメーション中に例外やキャンセルが起きても入力ロックを残さない。
                                            isSwiping = false
                                        }
                                    }
                                }

                                fun returnCardToOrigin() {
                                    if (isSwiping) return
                                    scope.launch {
                                        coroutineScope {
                                            launch {
                                                cardOffsetX.animateTo(
                                                    0f,
                                                    tween(220, easing = FastOutSlowInEasing)
                                                )
                                            }
                                            launch {
                                                cardOffsetY.animateTo(
                                                    0f,
                                                    tween(220, easing = FastOutSlowInEasing)
                                                )
                                            }
                                            launch {
                                                cardRotation.animateTo(
                                                    0f,
                                                    tween(220, easing = FastOutSlowInEasing)
                                                )
                                            }
                                        }
                                    }
                                }

                                val tinderCardModifier = Modifier.graphicsLayer {
                                    translationX = cardOffsetX.value
                                    translationY = cardOffsetY.value
                                    rotationZ = cardRotation.value
                                    scaleX = cardScale.value
                                    scaleY = cardScale.value
                                }

                                FlashcardReviewView(
                                    item = currentItem,
                                    showFavoriteMarker = currentFilter == VocabularyFilter.FAVORITES,
                                    showMeaningFirst = currentFilter == VocabularyFilter.FAVORITES,
                                    cardModifier = tinderCardModifier,
                                    onPrevious = {
                                        swipeCard(
                                            direction = SwipeDirection.LEFT,
                                            itemId = currentItem.id,
                                            nextCardIndex = (cardIndex - 1).coerceAtLeast(0),
                                            action = {}
                                        )
                                    },
                                    onIncrementMastery = {
                                        swipeCard(
                                            direction = SwipeDirection.RIGHT,
                                            itemId = currentItem.id,
                                            nextCardIndex = if (cardIndex < deckIds.lastIndex) {
                                                cardIndex + 1
                                            } else {
                                                deckIds.size
                                            }
                                        ) {
                                            viewModel.setMastered(
                                                currentItem.id,
                                                removeFromFavorites = currentFilter == VocabularyFilter.FAVORITES
                                            )
                                        }
                                    },
                                    onForgot = {
                                        swipeCard(
                                            direction = SwipeDirection.LEFT,
                                            itemId = currentItem.id,
                                            nextCardIndex = if (cardIndex < deckIds.lastIndex) {
                                                cardIndex + 1
                                            } else {
                                                deckIds.size
                                            }
                                        ) {
                                            // ⭐️ボタンは復習状態も更新（復習間隔を1日に戻す）が、履歴は
                                            // お気に入り切替の「お気に入り ⭐️」だけを記録する。
                                            viewModel.updateReviewStatus(
                                                currentItem.id,
                                                remembered = false,
                                                recordHistory = false
                                            )
                                            if (!currentItem.isFavorite) {
                                                viewModel.toggleFavorite(currentItem.id)
                                            }
                                        }
                                    },
                                    onToggleFavorite = { viewModel.toggleFavorite(currentItem.id) },
                                    onCardTap = { progressExpanded = false },
                                    onSearchWord = { word ->
                                        wordSearchInitialQuery = word
                                        showWordCardSearchDialog = true
                                    },
                                    currentIndex = cardIndex + 1,
                                    totalCount = deckIds.size,
                                    resetKey = screenResetKey,
                                    buttonSoundEnabled = buttonSoundEnabled,
                                    revealCard = showMainFeatureTour && mainFeatureTourStepIndex in 9..12,
                                    tourState = featureTourState,
                                    onPracticeWordLongPressed = { word ->
                                        // ツアーの長押しステップで、案内した単語が実際に長押しされたかを記録する。
                                        if (tourLongPressPracticeActive &&
                                            word.lowercase() in tourPracticeWordAccepted
                                        ) {
                                            tourPracticeLongPressed = true
                                            mainFeatureTourSteps
                                                .getOrNull(10)
                                                ?.practiceKey
                                                ?.let(featureTourState::registerAction)
                                        }
                                    },
                                    onPracticeWordSearched = {
                                        // 長押し後に「検索する」まで進んだら、次の説明へ自動で移る。
                                        if (tourLongPressPracticeActive && tourPracticeLongPressed) {
                                            tourPracticeSearching = true
                                            if (mainFeatureTourStepIndex == 10) {
                                                mainFeatureTourStepIndex = 11
                                            }
                                        }
                                    },
                                    practiceWord = if (tourLongPressPracticeActive) tourPracticeWord else null,
                                    guideDialogWord = tourPracticeDialogWord,
                                    onGuideDialogWordConsumed = { tourPracticeDialogWord = null },
                                    onSwipeDrag = { dragAmount, threshold ->
                                        if (!isSwiping) {
                                            val newOffsetX = cardOffsetX.value + dragAmount
                                            cardOffsetX.snapTo(newOffsetX)
                                            cardRotation.snapTo(
                                                (newOffsetX / threshold * SWIPE_DRAG_ROTATION_ANGLE)
                                                    .coerceIn(
                                                        -SWIPE_DRAG_ROTATION_ANGLE,
                                                        SWIPE_DRAG_ROTATION_ANGLE
                                                    )
                                            )
                                        }
                                    },
                                    onSwipeRelease = { finalDirectionDistance, finalDrag, commitDistance ->
                                        if (!isSwiping) {
                                            if (finalDirectionDistance >= commitDistance) {
                                                swipeCard(
                                                    direction = if (finalDrag > 0f) {
                                                        SwipeDirection.RIGHT
                                                    } else {
                                                        SwipeDirection.LEFT
                                                    },
                                                    itemId = currentItem.id,
                                                    nextCardIndex = if (cardIndex < deckIds.lastIndex) {
                                                        cardIndex + 1
                                                    } else {
                                                        deckIds.size
                                                    }
                                                ) {
                                                    if (finalDrag > 0f) {
                                                        // 右スワイプは「マスター」ボタンと同じ処理。
                                                        if (buttonSoundEnabled) {
                                                            playButtonSound(context, R.raw.kero_02_triple_amagael)
                                                        }
                                                        viewModel.setMastered(
                                                            currentItem.id,
                                                            removeFromFavorites = currentFilter == VocabularyFilter.FAVORITES
                                                        )
                                                    } else {
                                                        // 左スワイプは「⭐️ お気に入り」ボタンと同じ処理。
                                                        if (buttonSoundEnabled) {
                                                            playButtonSound(context, R.raw.mb_4_chord)
                                                        }
                                                        viewModel.updateReviewStatus(
                                                            currentItem.id,
                                                            remembered = false,
                                                            recordHistory = false
                                                        )
                                                        if (!currentItem.isFavorite) {
                                                            viewModel.toggleFavorite(currentItem.id)
                                                        }
                                                    }
                                                }
                                            } else {
                                                returnCardToOrigin()
                                            }
                                        }
                                    },
                                    onSwipeCancel = { returnCardToOrigin() }
                                )
                            } else {
                                if (currentFilter == VocabularyFilter.FAVORITES) {
                                    Box(
                                        modifier = Modifier.fillMaxSize(),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = when {
                                                strings.languageCode == "th" -> "ไม่มีการ์ดคำศัพท์ในรายการโปรดเพิ่มเติม"
                                                !strings.isJapanese -> "No more favorite cards."
                                                else -> "お気に入りの単語カードはこれ以上ありません。"
                                            },
                                            textAlign = TextAlign.Center,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    }
                                }
                            }
                        }
                }
            }

            if (showStreakDialog) {
                StreakDialog(
                    streak = streak,
                    todayStudyProgress = todayStudyProgress,
                    strings = strings,
                    onRepairStreak = viewModel::repairStreak,
                    onRepairStreakWithTicket = viewModel::repairStreakWithTicket,
                    onDismiss = { showStreakDialog = false }
                )
            }
        }
        if (showAiAppPicker) {
            AiAppPickerSheet(
                strings = strings,
                apps = installedAiApps,
                onDismiss = { showAiAppPicker = false },
                onAppSelected = { app ->
                    userPreferences.setPreferredAiProviderPackage(app.packageName)
                    pendingAiApp = app
                    showAiAppPicker = false
                }
            )
        }
        pendingAiApp?.let { app ->
            AlertDialog(
                onDismissRequest = { pendingAiApp = null },
                title = { Text(app.label, fontWeight = FontWeight.Bold) },
                text = { AiLiveGuidanceContent(strings, app.provider) },
                dismissButton = {
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        TextButton(onClick = {
                            pendingAiApp = null
                            showAiAppPicker = true
                        }) {
                            Text(strings.aiChange)
                        }
                        TextButton(onClick = { pendingAiApp = null }) {
                            Text(strings.close)
                        }
                    }
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            when (AiAppLauncher.launch(context, app)) {
                                is AiLaunchResult.Launched -> pendingAiApp = null
                                is AiLaunchResult.Failed -> {
                                    pendingAiApp = null
                                    showAiLaunchError = true
                                }
                            }
                        }
                    ) {
                        Text(strings.aiLaunch)
                    }
                }
            )
        }
        if (showAiLaunchError) {
            AlertDialog(
                onDismissRequest = { showAiLaunchError = false },
                text = { Text(strings.aiLaunchFailed) },
                confirmButton = {
                    TextButton(onClick = { showAiLaunchError = false }) {
                        Text(strings.close)
                    }
                }
            )
        }
    }
    if (showMainFeatureTour && !showOnboarding && !showSettings) {
        FeatureTourOverlay(
            visible = true,
            state = featureTourState,
            steps = mainFeatureTourSteps,
            copy = featureTourCopy(strings),
            strings = strings,
            buttonHelp = flashcardButtonHelpCopy(strings),
            selectedTargetBand = targetLevelToFeatureTourBand(targetLevel),
            levelWordCounts = featureTourLevelWordCounts,
            premiumUnlocked = premiumBillingState.isPremiumUnlocked(),
            onTargetBandSelected = { selectedBand ->
                val persistedTargetLevel = featureTourBandToTargetLevel(selectedBand)
                targetLevel = persistedTargetLevel
                userPreferences.setTargetLevel(persistedTargetLevel)
                viewModel.setLevelFilter(targetLevelToVocabularyLevel(persistedTargetLevel))
                refreshFlashcardDeck()
            },
            onPremiumLevelClick = { showPremiumDialog = true },
            selectedDailyTarget = todayStudyProgress.dailyTarget,
            dailyTargetOptions = strings.goalOptions,
            onDailyTargetSelected = viewModel::setDailyTarget,
            practiceSearching = tourPracticeSearching,
            onPracticeWordLongPressed = { word ->
                // ガイド上の単語を長押しした場合は、単語カードの長押しと同じ扱いにする。
                tourPracticeLongPressed = true
                tourPracticeDialogWord = word
                mainFeatureTourSteps
                    .getOrNull(10)
                    ?.practiceKey
                    ?.let(featureTourState::registerAction)
            },
            stepIndex = mainFeatureTourStepIndex,
            onStepIndexChange = { nextStepIndex ->
                if (nextStepIndex in 9..12) {
                    selectFlashcardTab()
                    // 長押しメニューの実操作ステップへ戻る時は、案内した 6.0 の単語を再掲示する。
                    if (nextStepIndex == 10) {
                        tourPracticeWordItem?.let(::showTourPracticeWordCard)
                    }
                }
                mainFeatureTourStepIndex = nextStepIndex
            },
            onFinished = ::finishMainFeatureTour,
            onSkipped = ::skipMainFeatureTour
        )
    }
    }
    }
}

/** インストール済みのChatGPT／Geminiを選択するシート。 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AiAppPickerSheet(
    strings: AppStrings,
    apps: List<InstalledAiApp>,
    onDismiss: () -> Unit,
    onAppSelected: (InstalledAiApp) -> Unit
) {
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp)
        ) {
            Text(
                text = strings.aiApps,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(horizontal = 24.dp, vertical = 8.dp)
            )
            if (apps.isEmpty()) {
                Text(
                    text = strings.aiNoInstalledApps,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(horizontal = 24.dp, vertical = 16.dp)
                )
            } else {
                apps.forEach { app ->
                    val appIcon = remember(app.packageName) {
                        app.icon.toBitmap(width = 96, height = 96).asImageBitmap()
                    }
                    ListItem(
                        headlineContent = { Text(app.label) },
                        supportingContent = { Text(app.provider.fallbackLabel) },
                        leadingContent = {
                            Image(
                                bitmap = appIcon,
                                contentDescription = app.label,
                                modifier = Modifier.size(40.dp)
                            )
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onAppSelected(app) }
                    )
                }
            }
        }
    }
}

internal data class AiLiveGuidanceCopy(
    val intro: String,
    val liveLabel: String,
    val liveDescription: String,
    val appsLabel: String,
    val appsDescription: String
)

internal fun aiLiveGuidanceImages(provider: AiAppProvider): Pair<Int, Int> = when (provider) {
    AiAppProvider.GEMINI -> R.drawable.gemini_live_guidance to R.drawable.gemini_app_list_guidance
    AiAppProvider.CHATGPT -> R.drawable.chatgpt_live_guidance to R.drawable.chatgpt_app_list_guidance
}

internal fun aiLiveGuidanceCopy(strings: AppStrings): AiLiveGuidanceCopy = when (strings.languageCode) {
    "ja" -> AiLiveGuidanceCopy(
        intro = "AIアプリを起動します。",
        liveLabel = "Live機能",
        liveDescription = "Live機能をオンにしてください。\n発音や会話を練習できます。\n声に出して練習すると、単語を覚えやすくなります。",
        appsLabel = "アプリの一覧",
        appsDescription = "Live機能を開始したら、アプリの一覧を開きます。\n「TOEFL単語帳」を選んで、このアプリに戻ってください。"
    )
    "zh" -> AiLiveGuidanceCopy(
        intro = "打开 AI 应用。",
        liveLabel = "Live 功能",
        liveDescription = "请开启 Live 功能。\n你可以练习发音和对话。",
        appsLabel = "应用列表",
        appsDescription = "启动 Live 功能后，打开应用列表。\n选择“TOEFL词汇本”，返回此应用。"
    )
    "hi" -> AiLiveGuidanceCopy(
        intro = "AI ऐप खोलें।",
        liveLabel = "Live मोड",
        liveDescription = "Live मोड चालू करें।\nउच्चारण और बातचीत का अभ्यास करें।",
        appsLabel = "ऐप्स की सूची",
        appsDescription = "Live मोड शुरू करने के बाद, ऐप्स की सूची खोलें।\n“TOEFL शब्दावली” चुनकर इस ऐप पर लौटें।"
    )
    "vi" -> AiLiveGuidanceCopy(
        intro = "Mở ứng dụng AI.",
        liveLabel = "Chế độ Live",
        liveDescription = "Hãy bật chế độ Live.\nBạn có thể luyện phát âm và hội thoại.",
        appsLabel = "Danh sách ứng dụng",
        appsDescription = "Sau khi bắt đầu Live, hãy mở danh sách ứng dụng.\nChọn “Từ vựng TOEFL” để quay lại ứng dụng này."
    )
    "ko" -> AiLiveGuidanceCopy(
        intro = "AI 앱을 엽니다.",
        liveLabel = "Live 기능",
        liveDescription = "Live 기능을 켜세요.\n발음과 대화를 연습할 수 있습니다.",
        appsLabel = "앱 목록",
        appsDescription = "Live를 시작한 뒤 앱 목록을 엽니다.\n‘TOEFL 단어장’을 선택해 이 앱으로 돌아오세요."
    )
    "id" -> AiLiveGuidanceCopy(
        intro = "Buka aplikasi AI.",
        liveLabel = "Mode Live",
        liveDescription = "Aktifkan Mode Live.\nAnda dapat berlatih pengucapan dan percakapan.",
        appsLabel = "Daftar aplikasi",
        appsDescription = "Setelah memulai Live, buka daftar aplikasi.\nPilih “Kosakata TOEFL” untuk kembali ke aplikasi ini."
    )
    "th" -> AiLiveGuidanceCopy(
        intro = "เปิดแอป AI",
        liveLabel = "ฟังก์ชัน Live",
        liveDescription = "เปิดฟังก์ชัน Live\nคุณสามารถฝึกออกเสียงและสนทนาได้",
        appsLabel = "รายการแอป",
        appsDescription = "หลังจากเริ่ม Live แล้ว ให้เปิดรายการแอป\nเลือก “คลังคำศัพท์ TOEFL” เพื่อกลับมายังแอปนี้"
    )
    "es" -> AiLiveGuidanceCopy(
        intro = "Abre la aplicación de IA.",
        liveLabel = "Función Live",
        liveDescription = "Activa la función Live.\nPuedes practicar la pronunciación y conversar.",
        appsLabel = "Lista de aplicaciones",
        appsDescription = "Después de iniciar Live, abre la lista de aplicaciones.\nSelecciona «Vocabulario TOEFL» para volver a esta aplicación."
    )
    else -> AiLiveGuidanceCopy(
        intro = "Open the AI app.",
        liveLabel = "Live mode",
        liveDescription = "Turn on Live mode.\nYou can practice pronunciation and conversation.",
        appsLabel = "App list",
        appsDescription = "After starting Live, open the app list.\nSelect “TOEFL Vocabulary” to return to this app."
    )
}

@Composable
private fun AiLiveGuidanceContent(
    strings: AppStrings,
    provider: AiAppProvider
) {
    val copy = aiLiveGuidanceCopy(strings)
    val images = aiLiveGuidanceImages(provider)

    Column(
        modifier = Modifier.verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Text(copy.intro)
        AiLiveGuidanceImage(strings, copy.liveLabel, images.first)
        Text(copy.liveDescription)
        AiLiveGuidanceImage(strings, copy.appsLabel, images.second)
        Text(copy.appsDescription)
    }
}

@Composable
internal fun AiLiveGuidanceImage(
    strings: AppStrings,
    label: String,
    imageRes: Int
) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = true },
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                modifier = Modifier.weight(1f),
                fontWeight = FontWeight.Bold
            )
            Image(
                painter = painterResource(imageRes),
                contentDescription = label,
                modifier = Modifier
                    .size(72.dp)
                    .clickable { expanded = true },
                contentScale = ContentScale.Fit
            )
        }
    }

    if (expanded) {
        AiLiveGuidanceImageExpandDialog(strings, imageRes) { expanded = false }
    }
}

@Composable
private fun AiLiveGuidanceImageExpandDialog(
    strings: AppStrings,
    imageRes: Int,
    onDismiss: () -> Unit
) {
    val painter = painterResource(imageRes)

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        // ステータスバー・ナビゲーションバー（◀️◯◽️）と重ならない領域に収める。
        Box(
            modifier = Modifier
                .fillMaxSize()
                .safeDrawingPadding()
                .padding(16.dp),
            contentAlignment = Alignment.Center
        ) {
            Surface(
                // ダイアログ自体も上下方向を利用可能領域の80%に制限する。
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight(0.8f),
                shape = MaterialTheme.shapes.large,
                color = MaterialTheme.colorScheme.surface
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // ナビゲーションバーと重ならないよう、安全領域内の95%に制限する。
                    BoxWithConstraints(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center
                    ) {
                        Image(
                            painter = painter,
                            contentDescription = null,
                            modifier = Modifier.fillMaxSize(fraction = 0.95f),
                            contentScale = ContentScale.Fit
                        )
                    }
                    TextButton(onClick = onDismiss) {
                        Text(strings.close)
                    }
                }
            }
        }
    }
}

/** 単語カード下部のボタンの説明ダイアログ */
@Composable
private fun FrogButtonHelpDialog(
    strings: AppStrings,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(strings.frogButtonHelpTitle, fontWeight = FontWeight.Bold) },
        text = {
            Column(
                modifier = Modifier.verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                FrogButtonHelpItem(
                    description = strings.frogPrevButtonHelp,
                    containerColor = MaterialTheme.colorScheme.error
                ) {
                    Text(
                        text = strings.vocabPrev,
                        maxLines = 1,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
                FrogButtonHelpItem(
                    description = strings.frogStarButtonHelp,
                    containerColor = MaterialTheme.colorScheme.error
                ) {
                    Text(
                        text = "⭐️",
                        maxLines = 1,
                        style = MaterialTheme.typography.titleMedium
                    )
                }
                FrogButtonHelpItem(
                    description = strings.frogButtonHelp,
                    containerColor = MaterialTheme.colorScheme.primary
                ) {
                    Image(
                        painter = painterResource(R.drawable.mastery_blue_frog),
                        contentDescription = null,
                        contentScale = ContentScale.Fit,
                        modifier = Modifier.size(30.dp)
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(strings.close)
            }
        }
    )
}

/** 説明ダイアログ内に表示する、実際のボタンと説明文の組み合わせ。 */
@Composable
private fun FrogButtonHelpItem(
    description: String,
    containerColor: Color,
    content: @Composable RowScope.() -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Button(
            onClick = {},
            modifier = Modifier.width(92.dp),
            colors = ButtonDefaults.buttonColors(containerColor = containerColor),
            contentPadding = PaddingValues(horizontal = 2.dp, vertical = 6.dp),
            content = content
        )
        Text(
            text = description,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

/** 🌱 GitHub風ヒートマップ表示 */
@Composable
private fun HeatmapView(
    data: Map<java.time.LocalDate, Int>,
    strings: AppStrings,
    expanded: Boolean,
    onExpandedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    val today = java.time.LocalDate.now()
    // 現在の週を左端にして、過去の週を右方向へ並べる
    val currentWeekStart = today.minusDays(today.dayOfWeek.value.toLong() % 7)
    val totalCount = data.values.sum()
    val heatmapScrollState = rememberScrollState()
    val dayLabels = if (strings.languageCode == "th") {
        listOf("อา", "จ", "อ", "พ", "พฤ", "ศ", "ส")
    } else {
        listOf("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
    }

    @Composable
    fun cellColor(date: java.time.LocalDate): Color {
        val count = data[date] ?: 0
        return when {
            count <= 0 -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
            count <= 5 -> Color(0xFF9BE9A8)
            count <= 10 -> Color(0xFF40C463)
            count <= 20 -> Color(0xFF30A14E)
            else -> Color(0xFF216E39)
        }
    }

    // 約1年分（53週間）を表示。横スクロールで過去へ移動できる。
    val weeks = (0 until 53).map { weekIndex ->
        (0 until 7).map { dayOfWeek ->
            currentWeekStart.minusDays((weekIndex * 7L) - dayOfWeek)
        }
    }
    // 月名を月の最初の1列だけに置かず、該当する週の幅の中央に表示する。
    val monthGroups = buildList<Pair<java.time.Month, Int>> {
        var currentMonth: java.time.Month? = null
        var currentCount = 0
        weeks.forEach { week ->
            val month = week.first().month
            if (month != currentMonth) {
                currentMonth?.let { add(it to currentCount) }
                currentMonth = month
                currentCount = 1
            } else {
                currentCount++
            }
        }
        currentMonth?.let { add(it to currentCount) }
    }

    LaunchedEffect(expanded) {
        if (expanded) heatmapScrollState.scrollTo(0)
    }

    Card(
        modifier = Modifier
            .then(modifier)
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(MaterialTheme.shapes.small)
                    .clickable { onExpandedChange(!expanded) }
                    .padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = if (expanded) "⌄" else "›",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(end = 4.dp)
                    )
                    Text(
                        text = strings.heatmapTitle,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                }
                Text(
                    text = strings.heatmapTotalLabel.replace("%d", totalCount.toString()),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            if (expanded) {
                // 曜日ラベルとマスの縦位置が端末の密度差でずれないよう、同じ行高・間隔を使う。
                // labelSmall の行高よりセル行が狭いと曜日ラベルの下端が切れるため、
                // ラベルとセルを同じ余裕のある高さで配置する。
                val heatmapHeaderHeight = 19.dp
                val heatmapCellSize = 18.dp
                val heatmapRowGap = 3.dp
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.Top
                ) {
                    Column(
                        modifier = Modifier.width(28.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = if (strings.languageCode == "th") "วัน" else "Day",
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.height(heatmapHeaderHeight),
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(heatmapRowGap))
                        dayLabels.forEachIndexed { index, label ->
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(heatmapCellSize),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = label,
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            if (index < dayLabels.lastIndex) {
                                Spacer(modifier = Modifier.height(heatmapRowGap))
                            }
                        }
                    }
                    Column(
                        modifier = Modifier.horizontalScroll(heatmapScrollState)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            monthGroups.forEachIndexed { index, (month, weekCount) ->
                                if (index > 0) {
                                    Spacer(modifier = Modifier.width(heatmapRowGap))
                                }
                                Text(
                                    text = month.name.take(3).lowercase()
                                        .replaceFirstChar { it.uppercase() },
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.Bold,
                                    textAlign = TextAlign.Center,
                                    modifier = Modifier
                                        .width(heatmapCellSize * weekCount + heatmapRowGap * (weekCount - 1))
                                        .height(heatmapHeaderHeight),
                                    color = MaterialTheme.colorScheme.onSurface
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(heatmapRowGap))
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(heatmapRowGap)
                        ) {
                            weeks.forEach { week ->
                                Column(
                                    verticalArrangement = Arrangement.spacedBy(heatmapRowGap)
                                ) {
                                    week.forEach { date ->
                                        Box(
                                            modifier = Modifier
                                                .size(heatmapCellSize)
                                                .clip(MaterialTheme.shapes.extraSmall)
                                                .background(cellColor(date))
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (expanded) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = if (strings.languageCode == "th") "น้อย" else "Less",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    listOf(
                        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                        Color(0xFF9BE9A8),
                        Color(0xFF40C463),
                        Color(0xFF30A14E),
                        Color(0xFF216E39)
                    ).forEach { color ->
                        Box(
                            modifier = Modifier
                                .padding(horizontal = 2.dp)
                                .size(10.dp)
                                .clip(MaterialTheme.shapes.extraSmall)
                                .background(color)
                        )
                    }
                    Text(
                        text = if (strings.languageCode == "th") "มาก" else "More",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

/** 単語カードのTinder風スワイプ方向 */
private enum class SwipeDirection {
    LEFT,   // 後退（左へ・戻る）
    RIGHT   // 前進（右へ）: 青カエル
}

/** 左右スワイプ時に強調するカード下部のアクションボタン */
private enum class SwipeActionButton {
    STAR,
    BLUE_FROG
}

/** スワイプアニメーションの目標値 */
private data class SwipeTarget(
    val endX: Float,
    val endY: Float,
    val endRotation: Float,
    val endScale: Float
)

/** 短い効果音を先読みし、連続タップ・スワイプでも遅延しにくく再生する。 */
private object ButtonSoundController {
    private const val MAX_STREAMS = 8

    private var soundPool: SoundPool? = null
    private val sampleIds = mutableMapOf<Int, Int>()
    private val loadedSampleIds = mutableSetOf<Int>()
    private val pendingPlayCounts = mutableMapOf<Int, Int>()

    fun prepare(context: Context) {
        if (soundPool != null) return

        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_GAME)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()
        val pool = SoundPool.Builder()
            .setAudioAttributes(audioAttributes)
            .setMaxStreams(MAX_STREAMS)
            .build()

        pool.setOnLoadCompleteListener { loadedPool, sampleId, status ->
            val resourceId = sampleIds.entries
                .firstOrNull { it.value == sampleId }
                ?.key
                ?: return@setOnLoadCompleteListener
            if (status == 0) {
                loadedSampleIds += sampleId
                val pendingCount = pendingPlayCounts.remove(resourceId) ?: 0
                repeat(pendingCount) {
                    loadedPool.play(sampleId, 1f, 1f, 1, 0, 1f)
                }
            } else {
                pendingPlayCounts.remove(resourceId)
            }
        }

        soundPool = pool
        load(pool, context, R.raw.kero_02_triple_amagael)
        load(pool, context, R.raw.mb_4_chord)
    }

    private fun load(pool: SoundPool, context: Context, resourceId: Int) {
        if (sampleIds.containsKey(resourceId)) return
        sampleIds[resourceId] = pool.load(context.applicationContext, resourceId, 1)
    }

    fun play(context: Context, soundResId: Int) {
        try {
            if (soundPool == null) prepare(context)
            val pool = soundPool ?: return
            val sampleId = sampleIds[soundResId] ?: run {
                val loadedId = pool.load(context.applicationContext, soundResId, 1)
                sampleIds[soundResId] = loadedId
                loadedId
            }
            if (sampleId in loadedSampleIds) {
                pool.play(sampleId, 1f, 1f, 1, 0, 1f)
            } else {
                // 初回ロード中だけ、音が鳴らない操作を1回分保留する。
                pendingPlayCounts[soundResId] = 1
            }
        } catch (e: Exception) {
            // 効果音の失敗でアプリ操作を止めない。
        }
    }

    fun release() {
        soundPool?.release()
        soundPool = null
        sampleIds.clear()
        loadedSampleIds.clear()
        pendingPlayCounts.clear()
    }
}

private fun playButtonSound(context: Context, soundResId: Int) {
    ButtonSoundController.play(context, soundResId)
}

/** Android標準TTSで発音を再生し、常に最新の1件だけを読み上げる。 */
private object PronunciationPlaybackController {
    private data class SpeechRequest(
        val text: String,
        val languageTag: String,
        val onUnavailable: () -> Unit
    )

    private var textToSpeech: TextToSpeech? = null
    private var initialized = false
    private var pendingRequest: SpeechRequest? = null

    fun speak(
        context: Context,
        text: String,
        languageTag: String,
        onUnavailable: () -> Unit
    ) {
        stop()
        val request = SpeechRequest(text, languageTag, onUnavailable)
        pendingRequest = request

        if (textToSpeech == null) {
            initialized = false
            textToSpeech = TextToSpeech(context.applicationContext) { status ->
                if (status == TextToSpeech.SUCCESS) {
                    initialized = true
                    pendingRequest?.let {
                        pendingRequest = null
                        speakNow(it)
                    }
                } else {
                    pendingRequest?.onUnavailable?.invoke()
                    pendingRequest = null
                    initialized = false
                    textToSpeech?.shutdown()
                    textToSpeech = null
                }
            }
        } else if (initialized) {
            pendingRequest = null
            speakNow(request)
        }
    }

    private fun speakNow(request: SpeechRequest) {
        val engine = textToSpeech ?: run {
            request.onUnavailable()
            return
        }
        val languageResult = engine.setLanguage(Locale.forLanguageTag(request.languageTag))
        if (languageResult < 0) {
            request.onUnavailable()
            return
        }

        engine.setAudioAttributes(
            AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .build()
        )
        if (engine.speak(request.text, TextToSpeech.QUEUE_FLUSH, null, "pronunciation") != TextToSpeech.SUCCESS) {
            request.onUnavailable()
        }
    }

    fun stop() {
        pendingRequest = null
        textToSpeech?.stop()
    }

    fun shutdown() {
        stop()
        textToSpeech?.shutdown()
        textToSpeech = null
        initialized = false
    }
}

/**
 * 🗣️ Android標準TTSでテキストを再生する。
 * lang: Locale.forLanguageTag()で解釈できる言語タグ（en-US / en-GBなど）
 */
private fun speakWord(
    context: android.content.Context,
    word: String,
    lang: String = "en-US",
    strings: AppStrings
) {
    PronunciationPlaybackController.speak(
        context = context,
        text = word,
        languageTag = lang,
        onUnavailable = {
            Toast.makeText(context.applicationContext, strings.speechNetworkUnavailable, Toast.LENGTH_SHORT).show()
        }
    )
}

private fun translationTtsLanguage(languageCode: String): String = when (languageCode) {
    "ja" -> "ja"
    "zh" -> "zh-CN"
    "hi" -> "hi"
    "vi" -> "vi"
    "ko" -> "ko"
    "id" -> "id"
    "th" -> "th"
    "es" -> "es"
    else -> "en-US"
}

private fun targetLevelToVocabularyLevel(targetLevel: String): VocabularyLevel = when (targetLevel) {
    "BASIC", "Basic", "L1", "L2", "5.0", "5.5" -> VocabularyLevel.BASIC
    "STANDARD", "Standard", "L3", "6.0" -> VocabularyLevel.STANDARD
    "ADVANCED", "Advanced", "L4", "6.5", "6.5+", "7.0+" -> VocabularyLevel.ADVANCED
    else -> VocabularyLevel.BASIC
}

private fun targetLevelToFeatureTourBand(targetLevel: String): String = when (targetLevel) {
    "L3", "6.0", "STANDARD" -> "STANDARD"
    "L4", "6.5", "6.5+", "7.0+", "ADVANCED" -> "ADVANCED"
    else -> "BASIC"
}

private fun featureTourBandToTargetLevel(band: String): String = when (band) {
    "STANDARD" -> "L3"
    "ADVANCED" -> "L4"
    else -> "L2"
}

private fun vocabularyItemLevel(level: Int): String = when (level) {
    VocabularyLevel.LEVEL1.ordinal,
    VocabularyLevel.LEVEL2.ordinal -> "Basic"
    VocabularyLevel.LEVEL3.ordinal -> "Standard"
    VocabularyLevel.LEVEL4.ordinal,
    VocabularyLevel.LEVEL5.ordinal -> "Advanced"
    else -> "Basic"
}

private fun vocabularyItemToeflScore(level: Int): String = when (level) {
    VocabularyLevel.LEVEL1.ordinal,
    VocabularyLevel.LEVEL2.ordinal -> "60+"
    VocabularyLevel.LEVEL3.ordinal -> "80+"
    VocabularyLevel.LEVEL4.ordinal,
    VocabularyLevel.LEVEL5.ordinal -> "100+"
    else -> "60+"
}

/**
 * 単語データの level がプレミアム対象（TOEFL Advanced = LEVEL4 / 旧LEVEL5）かどうか。
 *
 * [VocabularyLevel.requiresPremium] はロック機能自体の有効/無効（PREMIUM_LEVELS_LOCK_ENABLED）を
 * 含むため、UI 側で「TOEFL L4 の単語か」を判定する用途にはこの関数を使う。
 */
private fun isPremiumLevelItem(itemLevel: Int): Boolean =
    VocabularyLevel.ADVANCED.matchesVocabularyItemLevel(itemLevel)

/** 意味・説明の読み上げ言語。英語は選択中の発音アクセントを反映する。 */
private fun meaningTtsLanguage(languageCode: String, accentMode: AccentMode): String =
    if (languageCode == "en") accentMode.ttsLang else translationTtsLanguage(languageCode)

private data class PronunciationSettings(
    val enabled: Boolean,
    val onMuted: (() -> Unit) -> Unit
)

private val LocalPronunciationSettings = compositionLocalOf {
    PronunciationSettings(enabled = true, onMuted = { })
}

@Composable
private fun SpeechIcon(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val strings = LocalAppStrings.current
    val pronunciationSettings = LocalPronunciationSettings.current
    Image(
        painter = painterResource(id = R.drawable.speak_flog),
        contentDescription = strings.speechPlay,
        modifier = modifier
            .size(28.dp)
            .clickable {
                if (pronunciationSettings.enabled) onClick() else pronunciationSettings.onMuted(onClick)
            }
    )
}

/** テキストを生成AIなどへ貼り付けるためにクリップボードへコピーする。 */
private fun copyTextToClipboard(context: Context, text: String, strings: AppStrings) {
    if (text.isBlank()) return
    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as? ClipboardManager
        ?: return
    clipboard.setPrimaryClip(ClipData.newPlainText("TOEFL vocabulary", text))
    Toast.makeText(context, strings.copyDone, Toast.LENGTH_SHORT).show()
}

private suspend fun buildFlashcardClipboardText(
    context: Context,
    item: VocabularyItem,
    displayWord: String,
    displayMeaning: String,
    targetLanguage: String
): String {
    val collocations = item.collocations.joinToString(", ")
    val collocationTranslation = if (collocations.isNotBlank()) {
        LocalTranslationDictionary.lookup(
            context = context,
            stableKey = item.stableKey,
            phraseType = "collocations",
            sourceText = collocations,
            targetLanguage = targetLanguage
        )
    } else {
        null
    }
    val exampleTranslation = if (item.example.isNotBlank()) {
        LocalTranslationDictionary.lookup(
            context = context,
            stableKey = item.stableKey,
            phraseType = "example",
            sourceText = item.example,
            targetLanguage = targetLanguage
        )
    } else {
        null
    }

    return buildString {
        appendLine("Word: $displayWord")
        appendLine("Meaning: $displayMeaning")
        if (item.example.isNotBlank()) {
            appendLine("Example: ${item.example}")
            exampleTranslation?.takeIf { it.isNotBlank() }?.let {
                appendLine("Example translation: $it")
            }
        }
        if (collocations.isNotBlank()) {
            appendLine("Collocations: $collocations")
            collocationTranslation?.takeIf { it.isNotBlank() }?.let {
                appendLine("Collocations translation: $it")
            }
        }
        if (item.synonyms.isNotEmpty()) {
            appendLine("Synonyms: ${item.synonyms.joinToString(", ")}")
        }
    }.trim()
}

@Composable
private fun FlashcardCopyTextIcon(
    item: VocabularyItem,
    displayWord: String,
    displayMeaning: String,
    targetLanguage: String,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val strings = LocalAppStrings.current
    val scope = rememberCoroutineScope()

    IconButton(
        onClick = {
            scope.launch {
                copyTextToClipboard(
                    context = context,
                    text = buildFlashcardClipboardText(
                        context = context,
                        item = item,
                        displayWord = displayWord,
                        displayMeaning = displayMeaning,
                        targetLanguage = targetLanguage
                    ),
                    strings = strings
                )
            }
        },
        modifier = modifier.size(32.dp)
    ) {
        Icon(
            imageVector = Icons.Filled.ContentCopy,
            contentDescription = strings.copyText,
            modifier = Modifier.size(18.dp),
            tint = MaterialTheme.colorScheme.primary
        )
    }
}

private fun BackupUiMessage.toDisplayText(strings: AppStrings): String = when (this) {
    BackupUiMessage.BACKUP_SAVED -> strings.backupSaved
    BackupUiMessage.BACKUP_SAVE_FAILED -> strings.backupSaveFailed
    BackupUiMessage.BACKUP_READ_FAILED -> strings.backupReadFailed
    BackupUiMessage.RESTORE_FAILED -> strings.restoreFailed
}

@Composable
private fun VocabularyProgressSection(
    progress: VocabularyProgress,
    streak: StudyStreak,
    todayStudyProgress: TodayStudyProgress,
    strings: AppStrings,
    selectedLevel: VocabularyLevel,
    premiumUnlocked: Boolean,
    onLevelSelected: (VocabularyLevel) -> Unit,
    onPremiumLevelClick: () -> Unit,
    onSetDailyGoal: (Int) -> Unit,
    showGoalDialog: Boolean,
    onShowGoalDialog: (Boolean) -> Unit,
    onShowStreakDialog: (Boolean) -> Unit,
    onSearchWord: () -> Unit,
    expanded: Boolean,
    onExpandedChange: (Boolean) -> Unit,
    tourState: FeatureTourState? = null
) {
    val progressAnimation = animateFloatAsState(
        targetValue = progress.progressPercent / 100f,
        animationSpec = tween(durationMillis = 800, easing = FastOutSlowInEasing),
        label = "progressBar"
    )

    Card(
        modifier = Modifier
            .fillMaxWidth()
            // 進捗カードの上下の空きを抑え、単語カードの領域を広げる。
            .padding(horizontal = 16.dp, vertical = 2.dp),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 6.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .then(
                        tourState?.let { Modifier.featureTourTarget(it, "progress_section") } ?: Modifier
                    )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(MaterialTheme.shapes.medium)
                        .clickable { onExpandedChange(!expanded) }
                        .padding(vertical = 1.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = strings.vocabProgress,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (expanded) "▲" else "▼",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "%.1f%%".format(progress.progressPercent),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        IconButton(
                            onClick = onSearchWord,
                            modifier = Modifier
                                .size(36.dp)
                                .then(
                                    tourState?.let { Modifier.featureTourTarget(it, "progress_search") }
                                        ?: Modifier
                                )
                        ) {
                            Text(
                                text = "🔍",
                                fontSize = 18.sp
                            )
                        }
                    }
                }

                AnimatedVisibility(visible = expanded) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            LinearProgressIndicator(
                progress = { progressAnimation.value },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(10.dp),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
                strokeCap = StrokeCap.Round
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ProgressMetricCard(
                    label = strings.vocabReviewDue,
                    value = "${progress.reviewDueCount}",
                    modifier = Modifier.weight(1f)
                )
                ProgressMetricCard(
                    label = strings.vocabTotal,
                    value = "${progress.totalCount}",
                    modifier = Modifier.weight(1f)
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ProgressMetricCard(
                    label = strings.vocabLearned,
                    value = "${progress.favoriteCount}",
                    modifier = Modifier.weight(1f)
                )
                ProgressMetricCard(
                    label = strings.vocabMastered,
                    value = "${progress.masteredCount}",
                    modifier = Modifier.weight(1f)
                )
            }

            LevelFilterRow(
                strings = strings,
                selectedLevel = selectedLevel,
                premiumUnlocked = premiumUnlocked,
                onLevelSelected = onLevelSelected,
                onPremiumLevelClick = onPremiumLevelClick,
                tourState = tourState
            )

            // 🔥ストリーク表示 + 今日の学習進捗 + 目標設定
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    // ストリーク／目標達成行の上下余白を縮小する。
                    .padding(horizontal = 12.dp, vertical = 2.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // 🔥ストリーク
                Row(
                    modifier = Modifier
                        .weight(1f)
                        .clip(MaterialTheme.shapes.medium)
                        .clickable { onShowStreakDialog(true) }
                        .then(
                            tourState?.let { Modifier.featureTourTarget(it, "streak_area") } ?: Modifier
                        )
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = "🔥",
                        style = MaterialTheme.typography.headlineSmall
                    )
                    Column {
                        Text(
                            text = when {
                                strings.isJapanese -> "${streak.currentStreak}日"
                                strings.languageCode == "th" -> "${streak.currentStreak} วัน"
                                else -> "${streak.currentStreak} days"
                            },
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = when {
                                strings.isJapanese -> "ストリーク"
                                strings.languageCode == "th" -> "เรียนต่อเนื่อง"
                                else -> "streak"
                            },
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                // 今日の学習
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .clip(MaterialTheme.shapes.medium)
                        .clickable { onShowGoalDialog(true) }
                        .then(
                            tourState?.let { Modifier.featureTourTarget(it, "daily_goal") } ?: Modifier
                        )
                        .padding(vertical = 4.dp),
                    horizontalAlignment = Alignment.End,
                    verticalArrangement = Arrangement.spacedBy(2.dp)
                ) {
                    Text(
                        text = if (todayStudyProgress.isTargetReached) {
                            strings.goalReached
                        } else {
                            "${strings.todayLearned}: ${todayStudyProgress.todayCount}/${todayStudyProgress.dailyTarget}"
                        },
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (todayStudyProgress.isTargetReached)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    LinearProgressIndicator(
                        progress = { todayStudyProgress.progressPercent / 100f },
                        modifier = Modifier
                            .width(100.dp)
                            .height(6.dp),
                        color = if (todayStudyProgress.isTargetReached)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.tertiary,
                        trackColor = MaterialTheme.colorScheme.surfaceVariant,
                        strokeCap = StrokeCap.Round
                    )
                }
            }

                }
                }
            }
        }
}

// 目標設定ダイアログ
    if (showGoalDialog) {
        AlertDialog(
            onDismissRequest = { onShowGoalDialog(false) },
            title = { Text(strings.setDailyGoal, fontWeight = FontWeight.Bold) },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    strings.goalOptions.forEach { option ->
                        val selected = todayStudyProgress.dailyTarget == option
                        FilterChip(
                            selected = selected,
                            onClick = {
                                onSetDailyGoal(option)
                                onShowGoalDialog(false)
                            },
                            label = {
                                Text(
                                    when {
                                        strings.isJapanese -> "$option 語/日"
                                        strings.languageCode == "th" -> "$option คำ/วัน"
                                        else -> "$option words/day"
                                    }
                                )
                            }
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { onShowGoalDialog(false) }) {
                    Text(strings.streakModalOk)
                }
            }
        )
    }
}

@Composable
private fun StreakDialog(
    streak: StudyStreak,
    todayStudyProgress: TodayStudyProgress,
    strings: AppStrings,
    onRepairStreak: () -> Unit,
    onRepairStreakWithTicket: () -> Unit,
    onDismiss: () -> Unit
) {
    val recoveryProgress = streak.recoveryProgress.coerceAtMost(streak.recoveryTarget)
    val recoveryRatio = if (streak.recoveryTarget > 0) {
        recoveryProgress.toFloat() / streak.recoveryTarget
    } else {
        0f
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(strings.streakDialogTitle, fontWeight = FontWeight.Bold) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                val message = when {
                    streak.isRecovered -> strings.streakDialogRecoveredMessage
                        .replace("%d", streak.currentStreak.toString())
                    streak.isRecoveryAvailable -> strings.streakDialogRecoveryMessage
                        .replace("%1\$d", streak.recoverableStreak.toString())
                        .replace("%2\$d", streak.recoveryTarget.toString())
                    else -> strings.streakDialogActiveMessage
                        .replace("%d", streak.currentStreak.toString())
                }
                Text(message)

                if (streak.recoveryTickets > 0) {
                    Text(
                        strings.streakRecoveryTickets.replace(
                            "%d",
                            streak.recoveryTickets.toString()
                        ),
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }

                if (streak.isRecoveryAvailable) {
                    Text(
                        "${strings.todayLearned}: ${streak.recoveryProgress}/${streak.recoveryTarget}",
                        fontWeight = FontWeight.Bold
                    )
                    LinearProgressIndicator(
                        progress = { recoveryRatio },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(8.dp),
                        strokeCap = StrokeCap.Round
                    )
                    Button(
                        onClick = onRepairStreak,
                        enabled = streak.canRecover,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(strings.streakDialogRecoveryAction)
                    }
                    OutlinedButton(
                        onClick = onRepairStreakWithTicket,
                        enabled = streak.canRecoverWithTicket,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(strings.streakTicketRecoveryAction)
                    }
                } else if (!streak.isRecovered) {
                    Text(
                        "${strings.todayLearned}: ${todayStudyProgress.todayCount}/${todayStudyProgress.dailyTarget}",
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(strings.close)
            }
        }
    )
}

@Composable
private fun WordCardSearchDialog(
    vocabulary: List<VocabularyItem>,
    strings: AppStrings,
    premiumUnlocked: Boolean,
    initialQuery: String = "",
    onDismiss: () -> Unit,
    onWordSelected: (VocabularyItem) -> Unit
) {
    var query by rememberSaveable(initialQuery) { mutableStateOf(initialQuery) }
    val normalizedQuery = query.trim().lowercase()
    val directMatches = remember(normalizedQuery, vocabulary, strings.languageCode) {
        if (normalizedQuery.isBlank()) {
            emptyList()
        } else {
            vocabulary.filter { item ->
                listOf(
                    item.word,
                    item.wordUk,
                    item.meaningFor(strings.languageCode)
                ).any { text -> text.lowercase().contains(normalizedQuery) }
            }
        }
    }
    val candidates = remember(normalizedQuery, directMatches, vocabulary) {
        when {
            normalizedQuery.isBlank() -> emptyList()
            directMatches.isNotEmpty() -> directMatches.take(8)
            else -> vocabulary
                .asSequence()
                .sortedBy { item ->
                    listOf(item.word, item.wordUk)
                        .filter { it.isNotBlank() }
                        .minOf { wordSearchDistance(normalizedQuery, it.lowercase()) }
                }
                .take(8)
                .toList()
        }
    }
    val exactMatch = directMatches.firstOrNull { item ->
        item.word.equals(query.trim(), ignoreCase = true) ||
            item.wordUk.equals(query.trim(), ignoreCase = true)
    }
    val copy = wordCardSearchCopy(strings)
    val context = LocalContext.current

    fun openGoogleSearch() {
        val searchUrl = "https://www.google.com/search?q=${Uri.encode(query.trim())}"
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(searchUrl)))
        onDismiss()
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(copy.title)
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    placeholder = {
                        Text(copy.placeholder)
                    }
                )
                if (normalizedQuery.isBlank()) {
                    Text(
                        text = copy.inputHint,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else if (directMatches.isEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = copy.noExactMatch,
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        OutlinedButton(
                            onClick = ::openGoogleSearch,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(copy.googleSearch)
                        }
                    }
                }
                LazyColumn(modifier = Modifier.heightIn(max = 280.dp)) {
                    items(candidates, key = { it.id }) { item ->
                        // Level 6.5+（プレミアム対象）を未購入で選ぶと購入ガイドを表示する。
                        val isPremiumLocked =
                            isPremiumLevelItem(item.level) && !premiumUnlocked
                        ListItem(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { onWordSelected(item) },
                            // 単語名の右側に TOEFL スコア目安を表示（例: (TOEFL 60+)）
                            headlineContent = {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = item.word,
                                        modifier = Modifier.weight(1f, fill = false)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    if (isPremiumLocked) {
                                        Text(
                                            text = "🔒",
                                            style = MaterialTheme.typography.labelMedium
                                        )
                                        Spacer(modifier = Modifier.width(4.dp))
                                    }
                                    Text(
                                        text = "(TOEFL ${vocabularyItemToeflScore(item.level)})",
                                        style = MaterialTheme.typography.labelMedium,
                                        color = MaterialTheme.colorScheme.primary
                                    )
                                }
                            },
                            supportingContent = {
                                Text(item.meaningFor(strings.languageCode))
                            }
                        )
                    }
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    if (exactMatch != null) onWordSelected(exactMatch) else onDismiss()
                }
            ) {
                Text(if (exactMatch != null) {
                    copy.open
                } else {
                    copy.close
                })
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(copy.cancel)
            }
        }
    )
}

private fun wordSearchDistance(query: String, candidate: String): Int {
    val previous = IntArray(candidate.length + 1) { it }
    var previousRow = previous
    query.forEachIndexed { queryIndex, queryChar ->
        val currentRow = IntArray(candidate.length + 1)
        currentRow[0] = queryIndex + 1
        candidate.forEachIndexed { candidateIndex, candidateChar ->
            currentRow[candidateIndex + 1] = minOf(
                currentRow[candidateIndex] + 1,
                previousRow[candidateIndex + 1] + 1,
                previousRow[candidateIndex] + if (queryChar == candidateChar) 0 else 1
            )
        }
        previousRow = currentRow
    }
    return previousRow.last()
}

@Composable
private fun ProgressMetricCard(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                // 4つの進捗ボタンを縦方向にコンパクトにする。
                .padding(vertical = 2.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun PremiumPurchaseDialog(
    strings: AppStrings,
    state: PremiumBillingState,
    premiumWordCount: Int,
    onPurchase: () -> Unit,
    onRestore: () -> Unit,
    onDismiss: () -> Unit
) {
    val isUnlocked = state.isPremiumUnlocked()
    val formattedPremiumWordCount = NumberFormat.getIntegerInstance().format(premiumWordCount)
    val statusMessage = when (state.message) {
        PremiumBillingMessage.SUCCESS -> strings.premiumLevelsPurchaseSuccess
        PremiumBillingMessage.PENDING -> strings.premiumLevelsPending
        PremiumBillingMessage.ERROR -> strings.premiumLevelsPurchaseError
        PremiumBillingMessage.NONE -> null
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(strings.premiumLevelsTitle, fontWeight = FontWeight.Bold) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(strings.premiumLevelsDescription.replace("%d", formattedPremiumWordCount))
                state.productPrice?.let { price ->
                    Text(
                        text = "${strings.premiumLevelsPrice}: $price",
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                if (state.isLoading) {
                    LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                }
                if (isUnlocked) {
                    Text(
                        text = strings.premiumLevelsUnlocked,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                statusMessage?.let { message ->
                    Text(
                        text = message,
                        color = if (state.message == PremiumBillingMessage.ERROR) {
                            MaterialTheme.colorScheme.error
                        } else {
                            MaterialTheme.colorScheme.onSurfaceVariant
                        }
                    )
                }
            }
        },
        dismissButton = {
            if (!isUnlocked) {
                TextButton(
                    onClick = onRestore,
                    enabled = !state.isLoading && !state.isPurchasing
                ) {
                    Text(strings.premiumLevelsRestore)
                }
            }
        },
        confirmButton = {
            if (isUnlocked) {
                TextButton(onClick = onDismiss) {
                    Text(strings.close)
                }
            } else {
                Button(
                    onClick = onPurchase,
                    enabled = !state.isLoading &&
                        !state.isPurchasing &&
                        state.productPrice != null
                ) {
                    if (state.isPurchasing) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(18.dp),
                            strokeWidth = 2.dp
                        )
                    } else {
                        Text(strings.premiumLevelsPurchase)
                    }
                }
            }
        }
    )
}

/** ⚙️ 設定ダイアログ（言語・ライセンス・バックアップ） */
private fun AppLanguage.displayName(): String = nativeDisplayName

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SettingsDialog(
    strings: AppStrings,
    backupState: BackupUiState,
    onDismiss: () -> Unit,
    onCreateBackup: () -> Unit,
    onOpenBackup: () -> Unit,
    onCancelRestore: () -> Unit,
    onConfirmRestore: () -> Unit,
    onClearBackupMessage: () -> Unit,
    onRestoreCompleted: () -> Unit,
    onTutorial: () -> Unit,
    autoStartTour: Boolean = false,
    onTourDismissed: () -> Unit = {}
) {
    val languageToggle = LocalLanguageToggle.current
    val context = LocalContext.current
    val selectedLanguage = AppLanguage.fromCode(strings.languageCode)
    val tourCopy = featureTourCopy(strings)
    var showLicense by remember { mutableStateOf(false) }
    var showComingSoon by remember { mutableStateOf<String?>(null) }
    var showSettingsTour by remember(autoStartTour) { mutableStateOf(autoStartTour) }
    var settingsTourStepIndex by rememberSaveable { mutableIntStateOf(0) }
    val settingsTourState = remember { FeatureTourState() }
    val settingsTourSteps = remember(strings.languageCode) { settingsTourSteps(strings) }
    val settingsScrollState = rememberScrollState()
    val density = LocalDensity.current
    var settingsViewportBounds by remember { mutableStateOf<Rect?>(null) }
    val currentSettingsTarget = settingsTourSteps
        .getOrNull(settingsTourStepIndex)
        ?.let { settingsTourState.boundsFor(it.targetKey) }

    LaunchedEffect(
        showSettingsTour,
        settingsTourStepIndex,
        strings.languageCode,
        settingsViewportBounds,
        currentSettingsTarget
    ) {
        if (!showSettingsTour) return@LaunchedEffect
        delay(50L)
        val viewport = settingsViewportBounds ?: return@LaunchedEffect
        val target = currentSettingsTarget ?: return@LaunchedEffect
        val edgePadding = with(density) { 16.dp.toPx() }
        val targetTop = target.top - viewport.top
        val targetBottom = target.bottom - viewport.top
        val delta = when {
            targetTop < edgePadding -> targetTop - edgePadding
            targetBottom > viewport.height - edgePadding -> targetBottom - (viewport.height - edgePadding)
            else -> 0f
        }
        if (delta != 0f) {
            settingsScrollState.animateScrollTo(
                (settingsScrollState.value + delta.roundToInt())
                    .coerceIn(0, settingsScrollState.maxValue)
            )
        }
    }

    if (backupState.pendingRestore != null) {
        val document = backupState.pendingRestore
        AlertDialog(
            onDismissRequest = onCancelRestore,
            title = { Text(strings.restoreConfirmationTitle, fontWeight = FontWeight.Bold) },
            text = {
                Text(
                    String.format(
                        java.util.Locale.getDefault(),
                        strings.restoreConfirmationMessage,
                        java.text.SimpleDateFormat("yyyy/MM/dd HH:mm", java.util.Locale.getDefault())
                            .format(java.util.Date(document.createdAt)),
                        document.vocabulary.size,
                        document.history.size,
                        document.vocabulary.count { it.isFavorite }
                    )
                )
            },
            dismissButton = {
                TextButton(onClick = onCancelRestore) { Text(strings.close) }
            },
            confirmButton = {
                Button(onClick = onConfirmRestore) {
                    Text(strings.restoreConfirmationAction)
                }
            }
        )
        return
    }

    if (backupState.result != null || backupState.message != null || backupState.error != null) {
        val result = backupState.result
        val text = when {
            backupState.error != null -> backupState.error.toDisplayText(strings)
            result != null -> String.format(
                java.util.Locale.getDefault(),
                strings.restoreCompletedMessage,
                result.vocabularyCount,
                result.historyCount,
                result.favoriteCount
            )
            else -> backupState.message?.toDisplayText(strings)
        }
        AlertDialog(
            onDismissRequest = onClearBackupMessage,
            title = {
                Text(
                    if (backupState.error == null) {
                        strings.dataMigration
                    } else {
                        when {
                            strings.isJapanese -> "エラー"
                            strings.languageCode == "th" -> "เกิดข้อผิดพลาด"
                            else -> "Error"
                        }
                    }
                )
            },
            text = { Text(text ?: "") },
            confirmButton = {
                TextButton(onClick = if (result != null) onRestoreCompleted else onClearBackupMessage) {
                    Text(strings.close)
                }
            }
        )
        return
    }

    if (showLicense) {
        LicenseDialog(
            strings = strings,
            onDismiss = { showLicense = false }
        )
        return
    }

    if (showComingSoon != null) {
        AlertDialog(
            onDismissRequest = { showComingSoon = null },
            title = { Text(showComingSoon!!, fontWeight = FontWeight.Bold) },
            text = { Text(strings.comingSoon) },
            confirmButton = {
                TextButton(onClick = { showComingSoon = null }) {
                    Text(strings.close)
                }
            }
        )
        return
    }

    BasicAlertDialog(
        onDismissRequest = onDismiss,
        // 設定項目を読みやすくするため、標準の狭いダイアログ幅を広げる。
        modifier = Modifier
            .fillMaxWidth(if (showSettingsTour) 1f else 0.92f)
            // システムバーを除いた表示領域内に、上下の余白を残して収める。
            // 内容は中央のスクロール領域で表示するため、小さい画面でも下端が切れない。
            .fillMaxHeight(0.90f),
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            decorFitsSystemWindows = true
        ),
    ) {
        Surface(
            modifier = Modifier.fillMaxSize(),
            shape = AlertDialogDefaults.shape,
            color = AlertDialogDefaults.containerColor,
            tonalElevation = AlertDialogDefaults.TonalElevation
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp, vertical = 4.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = strings.settings,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f)
                    )
                    TextButton(
                        onClick = onDismiss,
                        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                    ) {
                        Text(strings.close)
                    }
                }

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .onGloballyPositioned { coordinates ->
                            settingsViewportBounds = coordinates.boundsInRoot()
                        }
                ) {
                    Column(
                        modifier = Modifier.verticalScroll(settingsScrollState),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                // ── 言語切り替え ──
                var languageMenuExpanded by remember { mutableStateOf(false) }
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .featureTourTarget(settingsTourState, "settings_language"),
                    verticalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Text(
                        text = strings.language,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Box(modifier = Modifier.fillMaxWidth()) {
                        OutlinedButton(
                            onClick = { languageMenuExpanded = true },
                            modifier = Modifier.fillMaxWidth(),
                            contentPadding = PaddingValues(horizontal = 16.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(selectedLanguage.displayName())
                                Text("▼", style = MaterialTheme.typography.labelSmall)
                            }
                        }
                        DropdownMenu(
                            expanded = languageMenuExpanded,
                            onDismissRequest = { languageMenuExpanded = false },
                            modifier = Modifier.fillMaxWidth(0.84f)
                        ) {
                            AppLanguage.entries.forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(option.displayName()) },
                                    onClick = {
                                        languageMenuExpanded = false
                                        if (strings.languageCode != option.code) languageToggle(option)
                                    },
                                    trailingIcon = {
                                        if (strings.languageCode == option.code) {
                                            Text("✓", fontWeight = FontWeight.Bold)
                                        }
                                    }
                                )
                            }
                        }
                    }
                }

                // ── バックアップ / レストア ──
                Text(
                    text = strings.dataMigration,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = strings.backupRestoreDescription,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onCreateBackup,
                        modifier = Modifier
                            .weight(1f)
                            .featureTourTarget(settingsTourState, "settings_backup"),
                        enabled = !backupState.busy
                    ) {
                        Text(strings.backup)
                    }
                    OutlinedButton(
                        onClick = onOpenBackup,
                        modifier = Modifier
                            .weight(1f)
                            .featureTourTarget(settingsTourState, "settings_restore"),
                        enabled = !backupState.busy
                    ) {
                        Text(strings.restore)
                    }
                }
                if (backupState.busy) {
                    LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                }

                // ── ライセンス ──
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { showLicense = true },
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)
                    )
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = if (strings.isJapanese) {
                                "📄 ライセンスとデータについて"
                            } else {
                                "Licenses & Data Notes"
                            },
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = if (strings.isJapanese) {
                                "オープンソースライブラリのライセンスと、語彙データの作成方針を表示します。"
                            } else {
                                "Open-source software licenses and vocabulary-data methodology."
                            },
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                TextButton(
                    onClick = {
                        runCatching {
                            context.startActivity(
                                Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACY_POLICY_URL))
                            )
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    contentPadding = PaddingValues(horizontal = 12.dp)
                ) {
                    Text("Privacy Policy", modifier = Modifier.fillMaxWidth())
                }
                TextButton(
                    onClick = {
                        runCatching {
                            context.startActivity(
                                Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:$OPERATOR_EMAIL"))
                            )
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    contentPadding = PaddingValues(horizontal = 12.dp)
                ) {
                    Text("Contact: $OPERATOR_EMAIL", modifier = Modifier.fillMaxWidth())
                }

                OutlinedButton(
                    onClick = onTutorial,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(strings.tutorial)
                }
                }

                    SettingsTourOverlay(
                        visible = showSettingsTour,
                        state = settingsTourState,
                        steps = settingsTourSteps,
                        copy = featureTourCopy(strings),
                        stepIndex = settingsTourStepIndex,
                        onStepIndexChange = { settingsTourStepIndex = it },
                        onDismiss = {
                            showSettingsTour = false
                            onTourDismissed()
                        }
                    )
                }
            }
        }
    }
}

/** ヘッダーのカエル。3〜15秒ごとに口を2回パクパクさせる。 */
@Composable
private fun AnimatedFrogIcon(
    contentDescription: String,
    modifier: Modifier = Modifier
) {
    var mouthClosed by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        while (isActive) {
            delay(Random.nextLong(3_000L, 15_001L))
            repeat(2) {
                mouthClosed = true
                delay(110L)
                mouthClosed = false
                delay(110L)
            }
        }
    }

    val mouthPatchAlpha by animateFloatAsState(
        targetValue = if (mouthClosed) 1f else 0f,
        animationSpec = tween(90),
        label = "frogMouth"
    )

    Box(modifier = modifier, contentAlignment = Alignment.Center) {
        Image(
            // マスター済みアイコンと同じ青いカエルを、ヘッダーの口パクにも使う。
            painter = painterResource(R.drawable.mastery_blue_frog),
            contentDescription = contentDescription,
            modifier = Modifier.matchParentSize(),
            contentScale = ContentScale.Fit
        )
        if (mouthPatchAlpha > 0f) {
            Canvas(modifier = Modifier.matchParentSize()) {
                val mouthLeft = size.width * 0.10f
                val mouthTop = size.height * 0.49f
                val mouthWidth = size.width * 0.80f
                val mouthHeight = size.height * 0.28f

                // 元画像の開いた口を下あご色で覆い、閉じた口を描く。
                drawOval(
                    brush = Brush.verticalGradient(
                        colors = listOf(Color(0xFF25BDEB), Color(0xFF65D4F2))
                    ),
                    topLeft = Offset(mouthLeft, mouthTop),
                    size = Size(mouthWidth, mouthHeight),
                    alpha = mouthPatchAlpha
                )

                val closedMouth = Path().apply {
                    moveTo(mouthLeft + mouthWidth * 0.08f, mouthTop + mouthHeight * 0.50f)
                    cubicTo(
                        mouthLeft + mouthWidth * 0.30f,
                        mouthTop + mouthHeight * 0.82f,
                        mouthLeft + mouthWidth * 0.70f,
                        mouthTop + mouthHeight * 0.82f,
                        mouthLeft + mouthWidth * 0.92f,
                        mouthTop + mouthHeight * 0.50f
                    )
                }
                drawPath(
                    path = closedMouth,
                    color = Color(0xFF3A260F),
                    style = Stroke(width = size.minDimension * 0.045f, cap = StrokeCap.Round),
                    alpha = mouthPatchAlpha
                )
            }
        }
    }

}

/** 📄 ライセンス情報ダイアログ */
@Composable
private fun LicenseDialog(
    strings: AppStrings,
    onDismiss: () -> Unit
) {
    val isJapanese = strings.isJapanese

    // Keep this inventory aligned with app/build.gradle.kts. The version is shown so
    // the applicable license can be identified for the exact build being used.
    data class LicenseItem(
        val name: String,
        val version: String,
        val license: String
    )

    val runtimeItems = listOf(
        LicenseItem("AndroidX Core KTX", "1.13.1", "Apache License 2.0"),
        LicenseItem("AndroidX Core Splashscreen", "1.0.1", "Apache License 2.0"),
        LicenseItem("AndroidX Lifecycle Runtime KTX", "2.8.4", "Apache License 2.0"),
        LicenseItem("AndroidX Lifecycle ViewModel Compose", "2.8.4", "Apache License 2.0"),
        LicenseItem("AndroidX Activity Compose", "1.2.9", "Apache License 2.0"),
        LicenseItem("Jetpack Compose UI / Graphics / Tooling", "BOM 2024.10.00", "Apache License 2.0"),
        LicenseItem("Material 3 / Material Icons Extended", "BOM 2024.10.00", "Apache License 2.0"),
        LicenseItem("Room Runtime / KTX", "2.7.1", "Apache License 2.0"),
        LicenseItem("Room Compiler", "2.7.1", "Apache License 2.0"),
        LicenseItem("Dagger / Hilt", "2.56.2", "Apache License 2.0"),
        LicenseItem("Dagger / Hilt Compiler", "2.56.2", "Apache License 2.0"),
        LicenseItem("Hilt Navigation Compose", "1.0.0", "Apache License 2.0"),
        LicenseItem("Kotlin", "project compiler/runtime", "Apache License 2.0"),
        LicenseItem("kotlinx-coroutines-android", "1.8.1", "Apache License 2.0"),
        LicenseItem("Google Play Billing KTX", "8.0.0", "Apache License 2.0")
    )

    val testItems = listOf(
        LicenseItem("JUnit 4", "4.13.2", "Eclipse Public License 1.0"),
        LicenseItem("Room Testing", "2.7.1", "Apache License 2.0"),
        LicenseItem("kotlinx-coroutines-test", "1.8.1", "Apache License 2.0"),
        LicenseItem("Robolectric", "4.12.2", "MIT License"),
        LicenseItem("AndroidX Test Core", "1.6.1", "Apache License 2.0"),
        LicenseItem("AndroidX Test JUnit Extension", "1.2.1", "Apache License 2.0"),
        LicenseItem("AndroidX Compose UI Tooling / Test", "BOM 2024.10.00", "Apache License 2.0")
    )

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                if (isJapanese) "ライセンスとデータについて" else "Licenses & Data Notes",
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(
                modifier = Modifier.verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = if (isJapanese) "実行時の依存ライブラリ" else "Runtime dependencies",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                runtimeItems.forEach { item ->
                    Column(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = item.name,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "${item.version} · ${item.license}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = if (isJapanese) "開発・テスト用の依存ライブラリ" else "Development and test dependencies",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                testItems.forEach { item ->
                    Column(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = item.name,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "${item.version} · ${item.license}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = if (isJapanese) {
                        "ライセンス本文と通知：\n" +
                            "Apache License 2.0 — https://www.apache.org/licenses/LICENSE-2.0\n" +
                            "Eclipse Public License 1.0 — https://www.eclipse.org/legal/epl-v10.html\n" +
                            "MIT License — https://opensource.org/license/mit\n\n" +
                            "記載しているバージョンは、このビルドで使用している依存ライブラリを示します。完全な利用条件と通知については、各プロジェクトの公式ドキュメントを確認してください。"
                    } else {
                        "License texts and notices:\n" +
                            "Apache License 2.0 — https://www.apache.org/licenses/LICENSE-2.0\n" +
                            "Eclipse Public License 1.0 — https://www.eclipse.org/legal/epl-v10.html\n" +
                            "MIT License — https://opensource.org/license/mit\n\n" +
                            "The listed versions identify the dependencies used by this build. " +
                            "Refer to each project's official documentation for complete terms and notices."
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = if (isJapanese) {
                        "商標に関する注意：\n" +
                            "TOEFL® は ETS の登録商標です。\n" +
                            "このアプリは ETS と提携、承認、認可されていません。TOEFL は、説明対象の試験を識別する目的でのみ使用しています。"
                    } else {
                        "Trademark notice:\n" +
                            "TOEFL® is a registered trademark of ETS.\n" +
                            "This app is not affiliated with, endorsed or approved by ETS. " +
                            "TOEFL is used only to identify the examination discussed."
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = if (isJapanese) {
                        "語彙データの作成方針と注意\n" +
                            "本アプリの語彙データは、本プロジェクトが選定・編集したデータです。作成過程ではAIを活用して候補語の選定、意味・例文・訳の作成、学習レベルの設定を行い、プロジェクト側で妥当性を検証・編集しています。\n" +
                            "語彙データの作成にはAIを利用していますが、語彙データの表示・学習のためにユーザー情報を外部AIへ送信するものではありません。\n" +
                            "AIによる生成・分類には、ハルシネーション（もっともらしい誤情報）などの誤りが含まれる可能性があります。内容の正確性・完全性を保証するものではありません。\n" +
                            "学習上の目安として利用し、重要な判断や公式教材の代わりには使用しないでください。\n" +
                            "本アプリのコンテンツは、ETSその他の試験実施団体が提供・承認した公式教材ではありません。"
                    } else {
                        "Vocabulary data methodology and notice\n" +
                            "The vocabulary data in this app was selected and edited by this project. During preparation, AI was used to select candidate words, create meanings, examples and translations, and assign learning levels; the project then reviewed and edited the results for validity.\n" +
                            "AI was used to prepare the vocabulary data, but user information is not sent to external AI services for displaying or studying the vocabulary data.\n" +
                            "AI-generated or AI-assisted selection and classification may contain errors, including hallucinations. Accuracy and completeness are not guaranteed.\n" +
                            "Use this content as a study guide, not as a substitute for official materials or for important decisions.\n" +
                            "This app is not official material provided, endorsed, or approved by ETS or any other test organization."
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.outline
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = if (isJapanese) "プライバシーと連絡先" else "Privacy and contact",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                val context = LocalContext.current
                TextButton(
                    onClick = {
                        runCatching {
                            context.startActivity(
                                Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACY_POLICY_URL))
                            )
                        }
                    },
                    contentPadding = PaddingValues(horizontal = 0.dp)
                ) {
                    Text(if (isJapanese) "プライバシーポリシー" else "Privacy Policy")
                }
                TextButton(
                    onClick = {
                        runCatching {
                            context.startActivity(
                                Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:$OPERATOR_EMAIL"))
                            )
                        }
                    },
                    contentPadding = PaddingValues(horizontal = 0.dp)
                ) {
                    Text(if (isJapanese) "連絡先: $OPERATOR_EMAIL" else "Contact: $OPERATOR_EMAIL")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(strings.close)
            }
        }
    )
}

/** レベルフィルター行（進捗カテゴリ・お気に入りタブで表示） */
@Composable
private fun LevelFilterRow(
    strings: AppStrings,
    selectedLevel: VocabularyLevel,
    premiumUnlocked: Boolean,
    onLevelSelected: (VocabularyLevel) -> Unit,
    onPremiumLevelClick: () -> Unit,
    tourState: FeatureTourState? = null
) {
    val levelOptions = listOf(
        Pair(VocabularyLevel.BASIC, "60+"),
        Pair(VocabularyLevel.STANDARD, "80+"),
        Pair(VocabularyLevel.ADVANCED, "100+")
    )
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
            .then(
                tourState?.let { Modifier.featureTourTarget(it, "level_filter") } ?: Modifier
            )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 2.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Level",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = if (strings.isJapanese) "TOEFL iBTスコアの目安" else "TOEFL iBT score guide",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            levelOptions.forEach { (level, score) ->
                val isPremiumLocked = level.requiresPremium() && !premiumUnlocked
                FilterChip(
                    selected = selectedLevel == level && !isPremiumLocked,
                    onClick = {
                        if (isPremiumLocked) onPremiumLevelClick() else onLevelSelected(level)
                    },
                    label = {
                        Text(if (isPremiumLocked) "🔒 $score" else score)
                    }
                )
            }
        }
    }
}

/** 履歴リスト表示 */
@Composable
private fun HistoryList(
    history: List<VocabularyHistory>,
    vocabulary: List<VocabularyItem>,
    strings: AppStrings,
    modifier: Modifier = Modifier,
    onFavoriteToggle: (Long) -> Unit,
    onToggleMastered: (Long) -> Unit
) {
    // 履歴の単語情報を解決。履歴件数が増えても毎回の線形検索を避ける。
    val vocabularyById = remember(vocabulary) { vocabulary.associateBy { it.id } }
    val historyItems = remember(history, vocabularyById) {
        history.mapNotNull { hist -> vocabularyById[hist.wordId]?.let { item -> hist to item } }
    }

    Column(modifier = modifier) {
        Text(
            text = "🕐 Action History (${historyItems.size})",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
        )

        if (historyItems.isEmpty()) {
            Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
                Text(
                    text = strings.historyEmpty,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                items(historyItems, key = { it.first.id }) { (hist, item) ->
                    HistoryRow(
                        history = hist,
                        item = item,
                        strings = strings,
                        onFavoriteToggle = { onFavoriteToggle(item.id) },
                        onToggleMastered = { onToggleMastered(item.id) }
                    )
                }
            }
        }
    }
}

/** 履歴1件の表示（お気に入りリストと同じレイアウト + 履歴の日時・アクション情報） */
@Composable
private fun HistoryRow(
    history: VocabularyHistory,
    item: VocabularyItem,
    strings: AppStrings,
    onFavoriteToggle: () -> Unit,
    onToggleMastered: () -> Unit
) {
    val accentMode = LocalAccentMode.current
    var expanded by remember { mutableStateOf(false) }
    // 表示する単語（UK モード時は UK スペルが存在すれば優先）
    val displayWord = if (accentMode == AccentMode.UK && item.wordUk.isNotBlank()) item.wordUk else item.word
    // TTS言語（UK=en-GB / US=en-US）
    val ttsLang = accentMode.ttsLang

    // 時刻フォーマット（例: 14:32）
    val timeText = remember(history.timestamp) {
        java.text.SimpleDateFormat("HH:mm", java.util.Locale.getDefault())
            .format(java.util.Date(history.timestamp))
    }
    // 日付フォーマット（例: 8/15）
    val dateText = remember(history.timestamp) {
        java.text.SimpleDateFormat("M/d", java.util.Locale.getDefault())
            .format(java.util.Date(history.timestamp))
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)
        )
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            // 1行目: 発音ボタン + 単語
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // 🗣️発音ボタン（Google Translate TTSで再生・アクセント切替に対応）
                val context = LocalContext.current
                SpeechIcon(
                    onClick = { speakWord(context, displayWord, ttsLang, strings) },
                    modifier = Modifier
                        .padding(end = 8.dp)
                )
                Text(
                    text = displayWord,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.weight(1f)
                )
            }

        // 2行目: 更新日時・TOEFLレベル・お気に入り・マスター状態
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "$dateText $timeText : TOEFL ${vocabularyItemToeflScore(item.level)}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.outline,
                    modifier = Modifier.weight(1f)
                )
                val favoriteIconStyle = MaterialTheme.typography.titleMedium.copy(
                    fontSize = MaterialTheme.typography.titleMedium.fontSize * 1.2f
                )
                val masteredIconStyle = MaterialTheme.typography.titleMedium.copy(
                    fontSize = MaterialTheme.typography.titleMedium.fontSize * 0.6f
                )
                IconButton(
                    onClick = onFavoriteToggle,
                    modifier = Modifier.size(32.dp)
                ) {
                    Text(
                        text = if (item.isFavorite) "★" else "☆",
                        style = favoriteIconStyle,
                        color = if (item.isFavorite) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            MaterialTheme.colorScheme.outline
                        }
                    )
                }
                MasteredButton(
                    onClick = onToggleMastered,
                    isMastered = item.isMastered,
                    iconTextStyle = masteredIconStyle,
                    modifier = Modifier
                )
            }

            // 意味・説明（全幅で表示）+ 発話アイコン（言語設定に応じた朗読）
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                val meaningContext = LocalContext.current
                SpeechIcon(
                    onClick = {
                        speakWord(
                            meaningContext,
                            item.meaningFor(strings.languageCode),
                            meaningTtsLanguage(strings.languageCode, accentMode),
                            strings
                        )
                    },
                    modifier = Modifier
                        .padding(end = 4.dp)
                )
                Text(
                    text = item.meaningFor(strings.languageCode),
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium
                )
            }
            if (expanded) {
                Divider(modifier = Modifier.padding(vertical = 8.dp))
                // 発音記号・別スペル（上部を「単語1行 + ボタン行」の2行にするため、展開時に表示）
                val otherWord = if (accentMode == AccentMode.UK) item.word else item.wordUk.ifBlank { item.word }
                val otherPhonetic = if (accentMode == AccentMode.US) item.phoneticUk else ""
                if (otherWord != displayWord || otherPhonetic.isNotBlank()) {
                    Text(
                        text = (if (accentMode == AccentMode.UK) "🇺🇸 " else "🇬🇧 ") +
                            (if (otherWord != displayWord) "$otherWord " else "") +
                            (if (otherPhonetic.isNotBlank()) "[$otherPhonetic]" else ""),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.secondary
                    )
                }

                if (item.example.isNotBlank()) {
                    Text(
                        text = if (strings.languageCode == "th") "ตัวอย่าง:" else "Example:",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.secondary
                    )
                    // 例文の左先頭に発話アイコン（タップで例文を英語朗読）
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val exampleContext = LocalContext.current
                        SpeechIcon(
                            onClick = { speakWord(exampleContext, item.example, ttsLang, strings) },
                            modifier = Modifier
                                .padding(end = 4.dp)
                        )
                        Text(
                            text = item.example,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    TranslationDisclosure(
                        stableKey = item.stableKey,
                        phraseType = "example",
                        sourceText = item.example,
                        targetLanguage = strings.languageCode,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }
                if (item.collocations.isNotEmpty()) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (strings.languageCode == "th") "📚 คำที่ใช้ร่วมกัน:" else "Collocations:",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.secondary
                        )
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val collocationContext = LocalContext.current
                        SpeechIcon(
                            onClick = {
                                speakWord(
                                    collocationContext,
                                    item.collocations.joinToString(", "),
                                    ttsLang,
                                    strings
                                )
                            },
                            modifier = Modifier.padding(end = 4.dp)
                        )
                        Text(
                            text = item.collocations.joinToString(", "),
                            modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    TranslationDisclosure(
                        stableKey = item.stableKey,
                        phraseType = "collocations",
                        sourceText = item.collocations.joinToString(", "),
                        targetLanguage = strings.languageCode,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }
                if (item.synonyms.isNotEmpty()) {
                    Text(
                        text = if (strings.languageCode == "th") "คำพ้องความหมาย (การถอดความ):" else "Synonyms (Paraphrases):",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.secondary
                    )
                    // 類義語の左先頭に発話アイコン（タップで類義語を英語朗読）
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val synonymContext = LocalContext.current
                        SpeechIcon(
                            onClick = {
                                speakWord(
                                    synonymContext,
                                    item.synonyms.joinToString(", "),
                                    ttsLang,
                                    strings
                                )
                            },
                            modifier = Modifier.padding(end = 4.dp)
                        )
                        Text(
                            text = item.synonyms.joinToString(", "),
                            modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun MasteredButton(
    onClick: () -> Unit,
    isMastered: Boolean,
    iconTextStyle: TextStyle,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = Modifier
            .then(modifier)
            .clip(MaterialTheme.shapes.medium)
            .clickable { onClick() }
            .padding(horizontal = 4.dp, vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(2.dp)
    ) {
        if (isMastered) {
            Image(
                painter = painterResource(R.drawable.mastery_blue_frog),
                contentDescription = null,
                contentScale = ContentScale.Fit,
                modifier = Modifier.size(24.dp)
            )
        } else {
            Text(
                text = "◯",
                style = iconTextStyle,
                modifier = Modifier.size(24.dp),
                textAlign = TextAlign.Center
            )
        }
    }
}

/**
 * Shows a collapsed translation row below the original English card text.
 * The local dictionary is read only after the learner opens the row.
 */
@Composable
private fun TranslationDisclosure(
    stableKey: String,
    phraseType: String,
    sourceText: String,
    targetLanguage: String,
    centerText: Boolean = false,
    modifier: Modifier = Modifier
) {
    // 英語表示時は原文がそのまま表示されるため、重複する翻訳エリアを出さない。
    val normalizedLanguage = targetLanguage.trim().lowercase()
        .substringBefore('-')
        .substringBefore('_')
    if (normalizedLanguage == "en") return

    // 例文・コロケーションの訳では、ローカル言語の読み上げカエルアイコンを表示しない。
    // 翻訳カードは常にローカル言語の訳文だけを表示する。
    val context = LocalContext.current
    var expanded by rememberSaveable(stableKey, phraseType, sourceText, targetLanguage) {
        mutableStateOf(false)
    }
    var translatedText by remember(stableKey, phraseType, sourceText, targetLanguage) {
        mutableStateOf<String?>(null)
    }
    var isLoading by remember(stableKey, phraseType, sourceText, targetLanguage) {
        mutableStateOf(false)
    }

    LaunchedEffect(expanded, stableKey, phraseType, sourceText, targetLanguage) {
        if (!expanded || translatedText != null) return@LaunchedEffect

        isLoading = true
        translatedText = LocalTranslationDictionary.lookup(
            context = context,
            stableKey = stableKey,
            phraseType = phraseType,
            sourceText = sourceText,
            targetLanguage = targetLanguage
        )
        isLoading = false
    }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(MaterialTheme.shapes.small)
            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.45f))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = !expanded }
                .padding(horizontal = 8.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.secondary
            )
            Text(
                text = translationDisclosureLabel(targetLanguage),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.secondary,
                modifier = Modifier.padding(start = 4.dp)
            )
        }

        if (expanded) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(start = 12.dp, end = 12.dp, bottom = 8.dp),
                contentAlignment = Alignment.Center
            ) {
                when {
                    isLoading -> CircularProgressIndicator(modifier = Modifier.size(18.dp))
                    translatedText != null -> Text(
                        text = translatedText.orEmpty(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = if (centerText) TextAlign.Center else TextAlign.Start,
                        modifier = Modifier.fillMaxWidth()
                    )
                    else -> Text(
                        text = translationUnavailableLabel(targetLanguage),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.outline,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
    }
}

private fun translationDisclosureLabel(languageCode: String): String = when (
    languageCode.trim().lowercase().substringBefore('-').substringBefore('_')
) {
    "ja" -> "翻訳を表示"
    "zh" -> "显示翻译"
    "hi" -> "अनुवाद दिखाएँ"
    "vi" -> "Hiển thị bản dịch"
    "ko" -> "번역 보기"
    "id" -> "Tampilkan terjemahan"
    "th" -> "แสดงคำแปล"
    "es" -> "Mostrar traducción"
    else -> "Show translation"
}

private fun translationUnavailableLabel(languageCode: String): String = when (
    languageCode.trim().lowercase().substringBefore('-').substringBefore('_')
) {
    "ja" -> "この文の翻訳は端末内に未収録です。"
    "zh" -> "设备中尚未收录这句话的翻译。"
    "hi" -> "इस वाक्य का अनुवाद डिवाइस में अभी उपलब्ध नहीं है।"
    "vi" -> "Bản dịch của câu này chưa được lưu trong ứng dụng."
    "ko" -> "이 문장의 번역은 기기에 아직 수록되지 않았습니다."
    "id" -> "Terjemahan kalimat ini belum tersedia di perangkat."
    "th" -> "ยังไม่มีคำแปลของประโยคนี้ในอุปกรณ์"
    "es" -> "La traducción de esta frase aún no está incluida en el dispositivo."
    else -> "This phrase is not yet included in the local dictionary."
}

@Composable
private fun WordActionText(
    text: String,
    modifier: Modifier = Modifier,
    style: TextStyle,
    fontWeight: FontWeight? = null,
    color: Color = Color.Unspecified,
    textAlign: TextAlign? = null,
    onTap: () -> Unit,
    onWordLongPressed: (String) -> Unit,
    /**
     * true のとき、Text 内の語を判定せずテキスト全体を長押し対象にする。
     * チュートリアルの実操作ステップで、確実に長押しを検知するために使う。
     */
    longPressWholeText: Boolean = false
) {
    var textLayoutResult by remember(text) { mutableStateOf<TextLayoutResult?>(null) }
    val latestTextLayoutResult by rememberUpdatedState(textLayoutResult)

    /**
     * 長押しの受け取り方を切り替えられる WordActionText。
     *
     * 単語カードが縦スクロール領域の中にあるため、通常は Text 内の 1 語判定で長押しを拾う。
     * ツアーの実操作ステップでは、確実に反応させるため語単位の判定に加えて
     * テキスト全体の長押しも受け取る。
     */
    Text(
        text = text,
        modifier = modifier.pointerInput(text, longPressWholeText) {
            detectTapGestures(
                onTap = { onTap() },
                onLongPress = { position ->
                    if (longPressWholeText) {
                        onWordLongPressed(text)
                        return@detectTapGestures
                    }
                    val layoutResult = latestTextLayoutResult ?: return@detectTapGestures
                    val offset = layoutResult
                        .getOffsetForPosition(position)
                        .coerceIn(0, text.lastIndex.coerceAtLeast(0))
                    wordAtTextOffset(text, offset)?.let(onWordLongPressed)
                }
            )
        },
        style = style,
        fontWeight = fontWeight,
        color = color,
        textAlign = textAlign,
        onTextLayout = { textLayoutResult = it }
    )
}

private fun wordAtTextOffset(text: String, offset: Int): String? {
    if (text.isBlank()) return null
    val safeOffset = offset.coerceIn(0, text.lastIndex)
    if (!text[safeOffset].isWordCharacter()) return null

    var start = safeOffset
    while (start > 0 && text[start - 1].isWordCharacter()) start--
    var end = safeOffset + 1
    while (end < text.length && text[end].isWordCharacter()) end++
    return text.substring(start, end)
}

private fun Char.isWordCharacter(): Boolean =
    isLetterOrDigit() || this == '\'' || this == '’' || this == '-'

private fun flashcardWordActionTitle(strings: AppStrings): String = when (strings.languageCode) {
    "ja" -> "単語を操作"
    "zh" -> "操作单词"
    "hi" -> "शब्द विकल्प"
    "vi" -> "Thao tác với từ"
    "ko" -> "단어 작업"
    "id" -> "Tindakan kata"
    "th" -> "การจัดการคำศัพท์"
    "es" -> "Acciones de palabra"
    else -> "Word actions"
}

private fun flashcardWordSearchLabel(strings: AppStrings): String = when (strings.languageCode) {
    "ja" -> "検索する"
    "zh" -> "搜索"
    "hi" -> "खोजें"
    "vi" -> "Tìm kiếm"
    "ko" -> "검색"
    "id" -> "Cari"
    "th" -> "ค้นหา"
    "es" -> "Buscar"
    else -> "Search"
}

private fun flashcardWordPronounceLabel(strings: AppStrings): String = when (strings.languageCode) {
    "ja" -> "発音する"
    "zh" -> "发音"
    "hi" -> "उच्चारण करें"
    "vi" -> "Phát âm"
    "ko" -> "발음하기"
    "id" -> "Ucapkan"
    "th" -> "ออกเสียง"
    "es" -> "Pronunciar"
    else -> "Pronounce"
}

private fun flashcardWordCopyLabel(strings: AppStrings): String = when (strings.languageCode) {
    "ja" -> "コピーする"
    "zh" -> "复制"
    "hi" -> "कॉपी करें"
    "vi" -> "Sao chép"
    "ko" -> "복사"
    "id" -> "Salin"
    "th" -> "คัดลอก"
    "es" -> "Copiar"
    else -> "Copy"
}

private fun flashcardWordCancelLabel(strings: AppStrings): String = when (strings.languageCode) {
    "ja" -> "やめる"
    "zh" -> "取消"
    "hi" -> "रद्द करें"
    "vi" -> "Hủy"
    "ko" -> "취소"
    "id" -> "Batal"
    "th" -> "ยกเลิก"
    "es" -> "Cancelar"
    else -> "Cancel"
}

private data class WordCardSearchCopy(
    val title: String,
    val placeholder: String,
    val inputHint: String,
    val noExactMatch: String,
    val googleSearch: String,
    val open: String,
    val close: String,
    val cancel: String
)

private fun wordCardSearchCopy(strings: AppStrings): WordCardSearchCopy = when (strings.languageCode) {
    "ja" -> WordCardSearchCopy(
        title = "単語カードを検索",
        placeholder = "単語を入力",
        inputHint = "単語を入力すると候補が表示されます。",
        noExactMatch = "該当なし。近い候補：",
        googleSearch = "Google単語検索",
        open = "開く",
        close = "閉じる",
        cancel = "キャンセル"
    )
    "zh" -> WordCardSearchCopy(
        title = "搜索单词卡",
        placeholder = "输入单词",
        inputHint = "输入单词后会显示候选项。",
        noExactMatch = "没有完全匹配项。相近候选：",
        googleSearch = "在 Google 中搜索单词",
        open = "打开",
        close = "关闭",
        cancel = "取消"
    )
    "hi" -> WordCardSearchCopy(
        title = "शब्द कार्ड खोजें",
        placeholder = "शब्द दर्ज करें",
        inputHint = "शब्द दर्ज करने पर सुझाव दिखाई देंगे।",
        noExactMatch = "सटीक मिलान नहीं मिला। मिलते-जुलते शब्द:",
        googleSearch = "Google पर शब्द खोजें",
        open = "खोलें",
        close = "बंद करें",
        cancel = "रद्द करें"
    )
    "vi" -> WordCardSearchCopy(
        title = "Tìm thẻ từ",
        placeholder = "Nhập từ",
        inputHint = "Các từ phù hợp sẽ hiện ở đây.",
        noExactMatch = "Không có kết quả chính xác. Từ gần giống:",
        googleSearch = "Tìm từ trên Google",
        open = "Mở",
        close = "Đóng",
        cancel = "Hủy"
    )
    "ko" -> WordCardSearchCopy(
        title = "단어 카드 검색",
        placeholder = "단어 입력",
        inputHint = "단어를 입력하면 후보가 표시됩니다.",
        noExactMatch = "정확히 일치하는 단어가 없습니다. 비슷한 단어:",
        googleSearch = "Google에서 단어 검색",
        open = "열기",
        close = "닫기",
        cancel = "취소"
    )
    "id" -> WordCardSearchCopy(
        title = "Cari kartu kata",
        placeholder = "Masukkan kata",
        inputHint = "Kata yang cocok akan muncul di sini.",
        noExactMatch = "Tidak ada kecocokan tepat. Kata yang mirip:",
        googleSearch = "Cari kata di Google",
        open = "Buka",
        close = "Tutup",
        cancel = "Batal"
    )
    "th" -> WordCardSearchCopy(
        title = "ค้นหาบัตรคำศัพท์",
        placeholder = "ป้อนคำศัพท์",
        inputHint = "คำศัพท์ที่ตรงกันจะแสดงที่นี่",
        noExactMatch = "ไม่พบคำที่ตรงกัน คำที่ใกล้เคียง:",
        googleSearch = "ค้นหาคำศัพท์ใน Google",
        open = "เปิด",
        close = "ปิด",
        cancel = "ยกเลิก"
    )
    "es" -> WordCardSearchCopy(
        title = "Buscar tarjeta de palabra",
        placeholder = "Introduce una palabra",
        inputHint = "Las palabras coincidentes aparecerán aquí.",
        noExactMatch = "No hay coincidencias exactas. Palabras similares:",
        googleSearch = "Buscar la palabra en Google",
        open = "Abrir",
        close = "Cerrar",
        cancel = "Cancelar"
    )
    else -> WordCardSearchCopy(
        title = "Search word card",
        placeholder = "Enter a word",
        inputHint = "Matching words will appear here.",
        noExactMatch = "No exact match. Similar words:",
        googleSearch = "Search word on Google",
        open = "Open",
        close = "Close",
        cancel = "Cancel"
    )
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun FlashcardReviewView(
    item: VocabularyItem,
    showFavoriteMarker: Boolean = false,
    showMeaningFirst: Boolean = false,
    cardModifier: Modifier = Modifier,
    onPrevious: () -> Unit,
    onIncrementMastery: () -> Unit,
    onForgot: () -> Unit,
    onToggleFavorite: () -> Unit,
    onCardTap: () -> Unit,
    onSearchWord: (String) -> Unit,
    currentIndex: Int,
    totalCount: Int,
    resetKey: Int,
    buttonSoundEnabled: Boolean,
    revealCard: Boolean = false,
    tourState: FeatureTourState? = null,
    /** ツアーの実操作ステップで、案内した単語が長押しされたときに呼ばれる。 */
    onPracticeWordLongPressed: (String) -> Unit = {},
    /** ツアーの実操作ステップで「検索する」が押されたときに呼ばれる。 */
    onPracticeWordSearched: () -> Unit = {},
    /** ツアーで「この単語を長押ししてください」と案内している単語。 */
    practiceWord: String? = null,
    /**
     * チュートリアルのガイド上で長押しされた単語。
     * 指定されると「単語を操作」ダイアログを開く（単語カードの長押しと同じ動作）。
     */
    guideDialogWord: String? = null,
    /** [guideDialogWord] をダイアログに反映した後に呼ばれる。 */
    onGuideDialogWordConsumed: () -> Unit = {},
    onSwipeDrag: suspend (dragAmount: Float, threshold: Float) -> Unit = { _, _ -> },
    onSwipeRelease: (finalDirectionDistance: Float, finalDrag: Float, commitDistance: Float) -> Unit = { _, _, _ -> },
    onSwipeCancel: () -> Unit = {}
) {
    val strings = LocalAppStrings.current
    val accentMode = LocalAccentMode.current
    val context = LocalContext.current
    val view = LocalView.current
    val pronunciationSettings = LocalPronunciationSettings.current
    var showBack by remember(item.id, resetKey) { mutableStateOf(false) }
    var actionWord by remember(item.id, resetKey) { mutableStateOf<String?>(null) }
    // 表示する単語（UK モード時は UK スペルが存在すれば優先）
    val displayWord = if (accentMode == AccentMode.UK && item.wordUk.isNotBlank()) item.wordUk else item.word
    val displayMeaning = item.meaningFor(strings.languageCode)
    // TTS言語（UK=en-GB / US=en-US）
    val ttsLang = accentMode.ttsLang
    // お気に入りカードは、英単語を考えてから答え合わせできるように意味を先に表示する。
    val showWordOnCard = showBack || !showMeaningFirst
    val cardDisplayText = if (showWordOnCard) displayWord else displayMeaning
    val cardSpeechLanguage = if (showWordOnCard) {
        ttsLang
    } else {
        meaningTtsLanguage(strings.languageCode, accentMode)
    }
    val swipeButtonAnimationScope = rememberCoroutineScope()
    val swipeButtonScale = remember { Animatable(1f) }
    var animatedSwipeButton by remember { mutableStateOf<SwipeActionButton?>(null) }
    var swipeButtonAnimationJob by remember { mutableStateOf<Job?>(null) }

    fun animateSwipeActionButton(button: SwipeActionButton) {
        swipeButtonAnimationJob?.cancel()
        swipeButtonAnimationJob = swipeButtonAnimationScope.launch {
            animatedSwipeButton = button
            swipeButtonScale.snapTo(1f)
            swipeButtonScale.animateTo(
                SWIPE_ACTION_BUTTON_MAX_SCALE,
                tween(
                    SWIPE_ACTION_BUTTON_ANIMATION_DURATION_MS / 2,
                    easing = FastOutSlowInEasing
                )
            )
            swipeButtonScale.animateTo(
                1f,
                tween(
                    SWIPE_ACTION_BUTTON_ANIMATION_DURATION_MS / 2,
                    easing = FastOutSlowInEasing
                )
            )
            animatedSwipeButton = null
        }
    }

    // チュートリアルの単語カード説明では、タブを選択した時点で内容まで見せる。
    LaunchedEffect(revealCard, item.id, resetKey) {
        if (revealCard) showBack = true
    }

    /**
     * チュートリアルのガイド上で単語が長押しされたときは、単語カードを長押しした
     * ときと同じ「単語を操作」ダイアログを開く。
     */
    LaunchedEffect(guideDialogWord, item.id) {
        val requestedWord = guideDialogWord ?: return@LaunchedEffect
        if (requestedWord.equals(displayWord, ignoreCase = true)) {
            actionWord = requestedWord
        }
        onGuideDialogWordConsumed()
    }

    fun handleCardTap() {
        onCardTap()
        showBack = !showBack
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 24.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // カード番号のみ表示（🙆・🗣️・⭐️は削除し、発音はカード内の単語の左に配置）
        Text(
            text = when {
                strings.isJapanese -> "単語カード: $currentIndex / $totalCount"
                strings.languageCode == "th" -> "บัตรคำศัพท์: $currentIndex / $totalCount"
                else -> "Flashcard: $currentIndex / $totalCount"
            },
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.outline
        )

        // 単語カード
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .padding(vertical = 4.dp)
                .then(
                    tourState?.let { Modifier.featureTourTarget(it, "flashcard_area") } ?: Modifier
                )
                .then(cardModifier)
                .pointerInput(item.id, resetKey, showBack) {
                    // タップ・長押し・横スワイプを同じ検出器で処理する。
                    // combinedClickable と横ドラッグ検出器を併用すると、タップ側が
                    // down イベントを先に消費して、連続操作時に横ドラッグが開始できない。
                    coroutineScope {
                        val gestureScope = this
                        awaitEachGesture {
                            val down = awaitFirstDown(requireUnconsumed = false)
                            var totalHorizontalDrag = 0f
                            var totalVerticalDrag = 0f
                            var finalDirectionDragDistance = 0f
                            var lastHorizontalDirection = 0f
                            var swipeStarted = false
                            var gestureCanceled = false
                            var longPressTriggered = false
                            var dragUpdateJob: Job? = null

                            val longPressJob = if (showBack) {
                                gestureScope.launch {
                                    delay(viewConfiguration.longPressTimeoutMillis)
                                    if (!swipeStarted && !gestureCanceled) {
                                        longPressTriggered = true
                                        actionWord = displayWord
                                        // ツアーの実操作ステップでは、案内した単語の長押しを記録する。
                                        onPracticeWordLongPressed(displayWord)
                                    }
                                }
                            } else {
                                null
                            }

                            while (true) {
                                val event = awaitPointerEvent()
                                val change = event.changes.firstOrNull { it.id == down.id }
                                    ?: break
                                if (!change.pressed) {
                                    longPressJob?.cancel()
                                    if (swipeStarted) {
                                        // 指を離した時点で確定処理を同期的に開始する。
                                        // 待機中のドラッグ更新がカード遷移後に走ると、
                                        // cardIndex の更新と競合して次カードへ進めなくなる。
                                        dragUpdateJob?.cancel()
                                        dragUpdateJob = null
                                        val commitDistance = SWIPE_COMMIT_DISTANCE_DP.dp.toPx()
                                        if (finalDirectionDragDistance >= commitDistance) {
                                            animateSwipeActionButton(
                                                if (lastHorizontalDirection > 0f) {
                                                    SwipeActionButton.BLUE_FROG
                                                } else {
                                                    SwipeActionButton.STAR
                                                }
                                            )
                                        }
                                        onSwipeRelease(
                                            finalDirectionDragDistance,
                                            lastHorizontalDirection,
                                            commitDistance
                                        )
                                    } else if (!gestureCanceled &&
                                        !longPressTriggered &&
                                        !change.isConsumed
                                    ) {
                                        handleCardTap()
                                    }
                                    break
                                }

                                val delta = change.positionChangeIgnoreConsumed()
                                if (delta.x != 0f) {
                                    val horizontalDirection = if (delta.x > 0f) 1f else -1f
                                    finalDirectionDragDistance = if (
                                        lastHorizontalDirection != 0f &&
                                            horizontalDirection != lastHorizontalDirection
                                    ) {
                                        abs(delta.x)
                                    } else {
                                        finalDirectionDragDistance + abs(delta.x)
                                    }
                                    lastHorizontalDirection = horizontalDirection
                                }
                                if (!swipeStarted && !gestureCanceled) {
                                    totalHorizontalDrag += delta.x
                                    totalVerticalDrag += delta.y

                                    val touchSlop = viewConfiguration.touchSlop
                                    when {
                                        abs(totalHorizontalDrag) > touchSlop &&
                                            abs(totalHorizontalDrag) > abs(totalVerticalDrag) -> {
                                            swipeStarted = true
                                            longPressJob?.cancel()
                                        }
                                        abs(totalVerticalDrag) > touchSlop &&
                                            abs(totalVerticalDrag) > abs(totalHorizontalDrag) -> {
                                            // カード本文の縦スクロールに譲り、タップも確定しない。
                                            gestureCanceled = true
                                            longPressJob?.cancel()
                                        }
                                    }
                                }

                                if (swipeStarted) {
                                    change.consume()
                                    val previousJob = dragUpdateJob
                                    dragUpdateJob = gestureScope.launch {
                                        previousJob?.join()
                                        onSwipeDrag(
                                            delta.x,
                                            size.width * SWIPE_ROTATION_DISTANCE_FRACTION
                                        )
                                    }
                                }
                            }
                        }
                    }
                },
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
            )
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    // 発音アイコンをカードの右端まで寄せ、本文の横幅も確保する。
                    .padding(horizontal = 8.dp, vertical = 24.dp),
                contentAlignment = Alignment.TopCenter
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // 単語の右端に発音アイコンを配置（アイコンのみ右寄せ、単語は中央）
                    Box(modifier = Modifier.fillMaxWidth()) {
                        val context = LocalContext.current
                        // チュートリアルで長押しを案内している単語は、どれを触ればよいか分かるよう枠で強調する。
                        val isPracticeWord = practiceWord != null &&
                            displayWord.equals(practiceWord, ignoreCase = true)
                        val practiceHighlightAlpha by animateFloatAsState(
                            targetValue = if (isPracticeWord) 1f else 0f,
                            animationSpec = tween(durationMillis = 300),
                            label = "practiceWordHighlight"
                        )
                        if (showFavoriteMarker) {
                            Box(
                                modifier = Modifier
                                    .align(Alignment.CenterStart)
                                    .size(48.dp)
                                    .clickable(onClick = onToggleFavorite),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = if (item.isFavorite) "★" else "☆",
                                    fontSize = 28.sp,
                                    color = if (item.isFavorite) {
                                        MaterialTheme.colorScheme.error
                                    } else {
                                        MaterialTheme.colorScheme.onSurfaceVariant
                                    }
                                )
                            }
                        }
                        Column(
                            modifier = Modifier.align(Alignment.CenterEnd),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            FlashcardCopyTextIcon(
                                item = item,
                                displayWord = displayWord,
                                displayMeaning = displayMeaning,
                                targetLanguage = strings.languageCode
                            )
                            SpeechIcon(
                                onClick = {
                                    speakWord(context, cardDisplayText, cardSpeechLanguage, strings)
                                }
                            )
                        }
                        WordActionText(
                            text = cardDisplayText,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(
                                    start = if (showFavoriteMarker) 48.dp else 8.dp,
                                    end = 42.dp
                                )
                                .then(
                                    if (practiceHighlightAlpha > 0f) {
                                        Modifier
                                            .border(
                                                width = 3.dp,
                                                color = MaterialTheme.colorScheme.primary.copy(
                                                    alpha = practiceHighlightAlpha
                                                ),
                                                shape = RoundedCornerShape(12.dp)
                                            )
                                            .background(
                                                color = MaterialTheme.colorScheme.primaryContainer.copy(
                                                    alpha = practiceHighlightAlpha
                                                ),
                                                shape = RoundedCornerShape(12.dp)
                                            )
                                            .padding(horizontal = 8.dp, vertical = 4.dp)
                                    } else {
                                        Modifier
                                    }
                                ),
                            style = MaterialTheme.typography.headlineLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary,
                            textAlign = TextAlign.Center,
                            onTap = ::handleCardTap,
                            onWordLongPressed = { word ->
                                if (showBack) actionWord = word
                                // ツアーの実操作ステップでは、単語を直接長押ししても検知できるようにする。
                                onPracticeWordLongPressed(word)
                            },
                            // ツアーで案内している単語は、指の位置に関係なく長押しを確実に拾う。
                            longPressWholeText = isPracticeWord
                        )
                    }

                    if (showBack) {
                        Divider()
                        // 説明の右端に朗読アイコン（言語設定に応じた朗読。アイコンのみ右寄せ）
                        Box(modifier = Modifier.fillMaxWidth()) {
                            val meaningContext = LocalContext.current
                            Column(
                                modifier = Modifier.align(Alignment.CenterEnd),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                SpeechIcon(
                                    onClick = {
                                        speakWord(
                                            meaningContext,
                                            displayMeaning,
                                            meaningTtsLanguage(strings.languageCode, accentMode),
                                            strings
                                        )
                                    }
                                )
                            }
                            WordActionText(
                                text = displayMeaning,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(start = 8.dp, end = 42.dp),
                                style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.SemiBold,
                                textAlign = TextAlign.Center,
                                onTap = ::handleCardTap,
                                onWordLongPressed = { word -> actionWord = word }
                            )
                        }
                        if (item.example.isNotBlank()) {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "Example",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.secondary
                                )
                                Box(modifier = Modifier.fillMaxWidth()) {
                                    val exampleContext = LocalContext.current
                                    Column(
                                        modifier = Modifier.align(Alignment.CenterEnd),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        SpeechIcon(
                                            onClick = { speakWord(exampleContext, item.example, ttsLang, strings) }
                                        )
                                    }
                                    WordActionText(
                                        text = item.example,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(start = 8.dp, end = 42.dp),
                                        style = MaterialTheme.typography.bodyLarge,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        textAlign = TextAlign.Center,
                                        onTap = ::handleCardTap,
                                        onWordLongPressed = { word -> actionWord = word }
                                    )
                                }
                                TranslationDisclosure(
                                    stableKey = item.stableKey,
                                    phraseType = "example",
                                    sourceText = item.example,
                                    targetLanguage = strings.languageCode,
                                    centerText = true,
                                    modifier = Modifier.padding(top = 8.dp)
                                )
                            }
                        }
                        if (item.collocations.isNotEmpty()) {
                            val collocations = item.collocations.joinToString(", ")
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(top = 8.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "Collocations",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.secondary
                                )
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(top = 8.dp)
                                ) {
                                    val collocationContext = LocalContext.current
                                    Column(
                                        modifier = Modifier.align(Alignment.CenterEnd),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        SpeechIcon(
                                            onClick = {
                                                speakWord(collocationContext, collocations, ttsLang, strings)
                                            }
                                        )
                                    }
                                    WordActionText(
                                        text = collocations,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(start = 8.dp, end = 42.dp),
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.primary,
                                        textAlign = TextAlign.Center,
                                        onTap = ::handleCardTap,
                                        onWordLongPressed = { word -> actionWord = word }
                                    )
                                }
                                TranslationDisclosure(
                                    stableKey = item.stableKey,
                                    phraseType = "collocations",
                                    sourceText = collocations,
                                    targetLanguage = strings.languageCode,
                                    centerText = true,
                                    modifier = Modifier.padding(top = 8.dp)
                                )
                            }
                        }
                        if (item.synonyms.isNotEmpty()) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(top = 8.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                val synonyms = item.synonyms.joinToString(", ")
                                Text(
                                    text = if (strings.languageCode == "th") {
                                        "คำพ้องความหมาย (การถอดความ)"
                                    } else {
                                        "Synonyms (Paraphrases)"
                                    },
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.secondary
                                )
                                Box(modifier = Modifier.fillMaxWidth()) {
                                    val synonymContext = LocalContext.current
                                    Column(
                                        modifier = Modifier.align(Alignment.CenterEnd),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        SpeechIcon(
                                            onClick = {
                                                speakWord(synonymContext, synonyms, ttsLang, strings)
                                            }
                                        )
                                    }
                                    WordActionText(
                                        text = synonyms,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(top = 8.dp, start = 8.dp, end = 42.dp),
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.primary,
                                        textAlign = TextAlign.Center,
                                        onTap = ::handleCardTap,
                                        onWordLongPressed = { word -> actionWord = word }
                                    )
                                }
                            }
                        }
                    } else {
                        if (!showMeaningFirst) {
                            Text(
                                text = strings.tapToShowMeaning,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.outline
                            )
                        }
                    }
                }
            }
        }

        // 3ボタン: 戻る / お気に入り / マスター
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .then(
                    tourState?.let { Modifier.featureTourTarget(it, "flashcard_buttons") } ?: Modifier
                ),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Button(
                onClick = {
                    if (buttonSoundEnabled) view.playSoundEffect(SoundEffectConstants.CLICK)
                    onPrevious()
                },
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
                contentPadding = PaddingValues(horizontal = 4.dp, vertical = 6.dp),
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = strings.vocabPrev,
                    maxLines = 1,
                    style = MaterialTheme.typography.labelSmall
                )
            }

            Button(
                onClick = {
                    if (buttonSoundEnabled) {
                        playButtonSound(context, R.raw.mb_4_chord)
                    }
                    animateSwipeActionButton(SwipeActionButton.STAR)
                    onForgot()
                },
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
                contentPadding = PaddingValues(horizontal = 4.dp, vertical = 6.dp),
                modifier = Modifier
                    .weight(1f)
                    .graphicsLayer {
                        val scale = if (animatedSwipeButton == SwipeActionButton.STAR) {
                            swipeButtonScale.value
                        } else {
                            1f
                        }
                        scaleX = scale
                        scaleY = scale
                    }
            ) {
                Icon(
                    imageVector = Icons.Filled.Star,
                    contentDescription = when {
                        strings.isJapanese -> "お気に入り"
                        strings.languageCode == "th" -> "รายการโปรด"
                        else -> "Favorite"
                    },
                    modifier = Modifier.size(24.dp)
                )
            }

            // 青カエル: マスター済みにして次の単語へ
            Button(
                onClick = {
                    if (buttonSoundEnabled) {
                        playButtonSound(context, R.raw.kero_02_triple_amagael)
                    }
                    animateSwipeActionButton(SwipeActionButton.BLUE_FROG)
                    onIncrementMastery()
                },
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
                contentPadding = PaddingValues(horizontal = 4.dp, vertical = 6.dp),
                modifier = Modifier
                    .weight(1f)
                    .graphicsLayer {
                        val scale = if (animatedSwipeButton == SwipeActionButton.BLUE_FROG) {
                            swipeButtonScale.value
                        } else {
                            1f
                        }
                        scaleX = scale
                        scaleY = scale
                    }
            ) {
                Image(
                    painter = painterResource(R.drawable.mastery_blue_frog),
                    contentDescription = when {
                        strings.isJapanese -> "マスター済み"
                        strings.languageCode == "th" -> "เชี่ยวชาญแล้ว"
                        else -> "Mastered"
                    },
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.size(28.dp),
                )
            }

        }
    }

    actionWord?.let { selectedWord ->
        AlertDialog(
            onDismissRequest = { actionWord = null },
            title = { Text(flashcardWordActionTitle(strings)) },
            text = { Text(selectedWord) },
            confirmButton = {
                Column(modifier = Modifier.fillMaxWidth()) {
                    // 表示順: 検索する → 発音する → コピーする → キャンセル
                    TextButton(
                        onClick = {
                            actionWord = null
                            onPracticeWordSearched()
                            onSearchWord(selectedWord)
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(flashcardWordSearchLabel(strings))
                    }
                    TextButton(
                        onClick = {
                            if (pronunciationSettings.enabled) {
                                speakWord(context, selectedWord, ttsLang, strings)
                            } else {
                                pronunciationSettings.onMuted {
                                    speakWord(context, selectedWord, ttsLang, strings)
                                }
                            }
                            actionWord = null
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(flashcardWordPronounceLabel(strings))
                    }
                    TextButton(
                        onClick = {
                            copyTextToClipboard(context, selectedWord, strings)
                            actionWord = null
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(flashcardWordCopyLabel(strings))
                    }
                    TextButton(
                        onClick = { actionWord = null },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(flashcardWordCancelLabel(strings))
                    }
                }
            }
        )
    }
}
