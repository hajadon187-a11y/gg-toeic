package com.gachiguild.gachitoeic.presentation.viewmodel

import android.app.Activity
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gachiguild.gachitoeic.BuildConfig
import com.gachiguild.gachitoeic.data.billing.PremiumAccess
import com.gachiguild.gachitoeic.data.billing.PremiumBillingManager
import com.gachiguild.gachitoeic.data.billing.PremiumBillingState
import com.gachiguild.gachitoeic.data.billing.isPremiumUnlocked
import com.gachiguild.gachitoeic.data.billing.isPremiumUnlocked
import com.gachiguild.gachitoeic.data.local.UserPreferences
import com.gachiguild.gachitoeic.domain.model.VocabularyHistory
import com.gachiguild.gachitoeic.domain.model.VocabularyItem
import com.gachiguild.gachitoeic.domain.repository.StudyContentRepository
import com.gachiguild.gachitoeic.domain.repository.StudyStreak
import com.gachiguild.gachitoeic.domain.repository.TodayStudyProgress
import com.gachiguild.gachitoeic.ui.AccentMode
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

enum class VocabularyFilter {
    ALL,
    FAVORITES,
    REVIEW,
    HISTORY
}

/** アクション履歴の種類 */
object HistoryAction {
    // 旧データ互換用。現在は青カエルの2状態のみを使用する。
    const val CHECK = "check"
    const val FAVORITE = "favorite"               // ⭐️お気に入り切替
    const val REVIEW_REMEMBERED = "review_remembered" // 単語カード: 覚えた
    const val REVIEW_FORGOT = "review_forgot"     // 単語カード: ⭐️お気に入り登録（復習間隔を1日に戻す）
    const val REVIEW_UNMASTERED = "review_unmastered" // 履歴タブ: マスター解除
}

/**
 * 語彙レベルのフィルター。
 *
 * LEVEL1〜LEVEL4 は assets の4つのTOEICスコア帯に対応する。
 * LEVEL5 と BASIC〜ADVANCED は旧データ・旧設定との互換用に残す。
 */
enum class VocabularyLevel {
    ALL,
    LEVEL1, // TOEIC 500+
    LEVEL2, // TOEIC 600+
    LEVEL3, // TOEIC 700+
    LEVEL4, // TOEIC 800+
    LEVEL5, // 旧アセット互換用。800+として扱う
    BASIC, // 旧3段階の Basic（LEVEL1 + LEVEL2）
    STANDARD, // 旧3段階の Standard（LEVEL3）
    ADVANCED, // 旧3段階の Advanced（LEVEL4 + LEVEL5）
    TOEIC_500,
    TOEIC_600,
    TOEIC_700,
    TOEIC_800;

    fun matchesVocabularyItemLevel(itemLevel: Int): Boolean = when (this) {
        ALL -> true
        LEVEL1, TOEIC_500 -> itemLevel == LEVEL1.ordinal
        LEVEL2, TOEIC_600 -> itemLevel == LEVEL2.ordinal
        LEVEL3, TOEIC_700 -> itemLevel == LEVEL3.ordinal
        LEVEL4, TOEIC_800 -> itemLevel == LEVEL4.ordinal || itemLevel == LEVEL5.ordinal
        LEVEL5 -> itemLevel == LEVEL5.ordinal
        BASIC -> itemLevel == LEVEL1.ordinal || itemLevel == LEVEL2.ordinal
        STANDARD -> itemLevel == LEVEL3.ordinal
        ADVANCED -> itemLevel == LEVEL4.ordinal || itemLevel == LEVEL5.ordinal
    }

    /** 旧保存値を現在の4段階表示へ束ねる。enum ordinalは変更しない。 */
    fun toStudyTier(): VocabularyLevel = when (this) {
        LEVEL1, BASIC, TOEIC_500 -> TOEIC_500
        LEVEL2, TOEIC_600 -> TOEIC_600
        LEVEL3, STANDARD, TOEIC_700 -> TOEIC_700
        LEVEL4, LEVEL5, ADVANCED, TOEIC_800 -> TOEIC_800
        ALL -> ALL
    }
}

/**
 * 800+（旧ADVANCED / LEVEL4 / LEVEL5）のみをプレミアム対象にする。
 *
 * productionDebug/release の本番相当ビルドで true になる。
 * 通常の debug ビルドでは false とし、Advanced vocabulary を確認できるようにする。
 * 課金状態の判定は PremiumBillingState.isPremiumUnlocked() に集約する。
 */
val PREMIUM_LEVELS_LOCK_ENABLED = BuildConfig.PRODUCTION_MODE

fun VocabularyLevel.requiresPremium(): Boolean =
    PREMIUM_LEVELS_LOCK_ENABLED &&
        (this == VocabularyLevel.TOEIC_800 ||
            this == VocabularyLevel.ADVANCED ||
            this == VocabularyLevel.LEVEL4 ||
            this == VocabularyLevel.LEVEL5)

/** 進捗カテゴリ（タップで単語一覧を表示する対象） */
enum class ProgressCategory {
    ALL,
    MASTERED,
    REVIEW_DUE
}

/** 単語学習の進捗状況 */
data class VocabularyProgress(
    val totalCount: Int = 0,
    val masteredCount: Int = 0,
    val reviewDueCount: Int = 0,
    val favoriteCount: Int = 0
) {
    /** 学習進捗率（%）= マスター済み / 全件。totalCount が 0 の場合は 0.0 */
    val progressPercent: Float
        get() = if (totalCount == 0) 0f else (masteredCount * 100f / totalCount)
}

@HiltViewModel
class VocabularyViewModel @Inject constructor(
    private val repository: StudyContentRepository,
    private val userPreferences: UserPreferences,
    private val premiumBillingManager: PremiumBillingManager
) : ViewModel() {

    // 同じ単語へのお気に入り変更と学習状態変更が同時に走って、
    // 片方の更新がもう片方を上書きしないようにする
    private val vocabularyMutationMutex = Mutex()

    /** 発音アクセント（US / UK。TOEIC向けデフォルトは US） */
    private val _accentMode = MutableStateFlow(userPreferences.getAccentMode())
    val accentMode: StateFlow<AccentMode> = _accentMode.asStateFlow()

    /** 単語カードのフッターボタン音（デフォルトはオン） */
    private val _buttonSoundEnabled = MutableStateFlow(userPreferences.isButtonSoundEnabled())
    val buttonSoundEnabled: StateFlow<Boolean> = _buttonSoundEnabled.asStateFlow()

    private val _filter = MutableStateFlow(VocabularyFilter.REVIEW)
    val filter: StateFlow<VocabularyFilter> = _filter.asStateFlow()

    private val _searchQuery = MutableStateFlow("")

    private val _selectedLevel = MutableStateFlow(userPreferences.getVocabularyLevel().toStudyTier())
    val premiumBillingState: StateFlow<PremiumBillingState> = premiumBillingManager.state
    val selectedLevel: StateFlow<VocabularyLevel> = combine(
        _selectedLevel,
        premiumBillingState
    ) { level, billingState ->
        if (level.requiresPremium() && !billingState.isPremiumUnlocked()) {
            VocabularyLevel.TOEIC_500
        } else {
            level
        }
    }.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        accessibleLevel(_selectedLevel.value, premiumBillingState.value.access)
    )

    /** 1日の目標単語数（デフォルト: 20語） */
    val dailyTarget: StateFlow<Int> = repository.observeDailyTarget()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 20)

    /** ストリーク情報 */
    val streak: StateFlow<StudyStreak> = repository.observeStreak()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), StudyStreak())

    /** 今日の学習状況（学習アクション数 + 目標） */
    val todayStudyProgress: StateFlow<TodayStudyProgress> = repository.observeTodayStudyProgress()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), TodayStudyProgress())

    /** 画面起動時のデータ読み込みと区別するため、実際の学習操作ごとに増える通知番号。 */
    private val _studyActivityVersion = MutableStateFlow(0)
    val studyActivityVersion: StateFlow<Int> = _studyActivityVersion.asStateFlow()

    /** 学習ヒートマップ（日付 → 学習件数） */
    val heatmapData: StateFlow<Map<java.time.LocalDate, Int>> = repository.observeHeatmapData()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyMap())

    // リポジトリから全ての単語を監視
    private val _allVocabulary = repository.observeVocabulary()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    /** 全単語リスト（履歴表示用・単語ID→単語の解決に使用） */
    val allVocabulary: StateFlow<List<VocabularyItem>> = _allVocabulary

    // レベルで絞り込んだ語彙（検索・タブフィルターの前段）
    private val levelFiltered: StateFlow<List<VocabularyItem>> = combine(
        _allVocabulary,
        _selectedLevel,
    ) { list, level ->
        list.filter { item -> level.matchesVocabularyItemLevel(item.level) }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    // 学習進捗（総単語数・未マスター・マスター済み・お気に入り数）。
    // 習熟度は青カエルの未マスター／マスター済みの2状態で集計する。
    val progress: StateFlow<VocabularyProgress> = _allVocabulary
        .map { list ->
            val mastered = list.count { it.isMastered }
            VocabularyProgress(
                totalCount = list.size,
                masteredCount = mastered,
                reviewDueCount = list.size - mastered,
                favoriteCount = list.count { it.isFavorite }
            )
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), VocabularyProgress())

    // 起動時は「未マスター」を選択状態にする。
    // 単語カードを表示するか、カテゴリ一覧を表示するかは画面側で別に管理する。
    private val _selectedProgressCategory = MutableStateFlow<ProgressCategory?>(ProgressCategory.REVIEW_DUE)
    val selectedProgressCategory: StateFlow<ProgressCategory?> = _selectedProgressCategory.asStateFlow()

    // 選択されたカテゴリに該当する単語リスト（検索クエリも適用）
    val progressCategoryVocabulary: StateFlow<List<VocabularyItem>> = combine(
        levelFiltered,
        _selectedProgressCategory,
        _searchQuery
    ) { list, category, query ->
        val filtered = when (category) {
            ProgressCategory.ALL -> list
            ProgressCategory.MASTERED -> list.filter { it.isMastered }
            // 未マスター = 青カエルが未済みの単語
            ProgressCategory.REVIEW_DUE -> list.filter { !it.isMastered }
            null -> emptyList()
        }
        // 部分マッチ検索（英単語のみを対象）
        if (query.isBlank() || category == null) {
            filtered
        } else {
            val q = query.trim().lowercase()
            filtered.filter { it.word.lowercase().contains(q) }
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    /** 進捗カテゴリを選択（null で解除） */
    fun selectProgressCategory(category: ProgressCategory?) {
        _selectedProgressCategory.value = category
    }

    // フィルター・検索クエリで絞り込まれた単語リスト
    val filteredVocabulary: StateFlow<List<VocabularyItem>> = combine(
        levelFiltered,
        _allVocabulary,
        _filter,
        _searchQuery,
        repository.observeFavoriteVocabularyIds()
    ) { levelFilteredList, allVocabularyList, filterType, query, favoriteIds ->
        val filtered = when (filterType) {
            VocabularyFilter.ALL -> levelFilteredList
            // FavoriteDao は登録日時の新しい順で返すため、その順序をそのまま表示順に使う。
            // お気に入りタブはレベルフィルターを無視し、全レベルを対象にする。
            VocabularyFilter.FAVORITES -> favoriteIds.mapNotNull { favoriteId ->
                allVocabularyList.firstOrNull { it.id == favoriteId }
            }
            // 未マスター（マスター済みは除外）
            VocabularyFilter.REVIEW -> levelFilteredList.filter { !it.isMastered }
            VocabularyFilter.HISTORY -> emptyList() // 履歴は history フローで別途取得
        }
        // 部分マッチ検索（英単語のみを対象）
        if (query.isBlank()) {
            filtered
        } else {
            val q = query.trim().lowercase()
            filtered.filter { it.word.lowercase().contains(q) }
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    // アクション履歴（新しい順）
    val history: StateFlow<List<VocabularyHistory>> = repository.observeHistory()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private suspend fun recordStudyActivity() {
        _studyActivityVersion.value += 1
        repository.recordStudyActivity()
    }

    // フィルタの設定（タブ切替時に検索クエリもリセット）
    fun setFilter(filterType: VocabularyFilter) {
        _filter.value = filterType
        _searchQuery.value = ""
    }

    /** レベルフィルターの設定 */
    fun setLevelFilter(level: VocabularyLevel) {
        val normalizedLevel = level.toStudyTier()
        if (normalizedLevel.requiresPremium() && !premiumBillingState.value.isPremiumUnlocked()) {
            return
        }
        _selectedLevel.value = normalizedLevel
        userPreferences.setVocabularyLevel(normalizedLevel)
    }

    /** プレミアムレベルの購入フローを開始 */
    fun purchasePremium(activity: Activity) {
        premiumBillingManager.purchase(activity)
    }

    /** Google Play の購入済み商品を再確認する */
    fun refreshPremiumAccess() {
        premiumBillingManager.refresh()
    }

    fun clearPremiumBillingMessage() {
        premiumBillingManager.clearMessage()
    }

    // 検索クエリの設定（部分マッチ対応）
    fun setSearchQuery(query: String) {
        _searchQuery.value = query
    }

    /** 発音アクセントを切り替える（US ⇄ UK）*/
    fun toggleAccent() {
        val newMode = if (_accentMode.value == AccentMode.UK) AccentMode.US else AccentMode.UK
        _accentMode.value = newMode
        userPreferences.setAccentMode(newMode)
    }

    /** ヘッダーのカエルから戻る、単語帳の起動時状態。 */
    fun resetToStartupState() {
        _accentMode.value = AccentMode.US
        userPreferences.setAccentMode(AccentMode.US)
        _filter.value = VocabularyFilter.REVIEW
        _searchQuery.value = ""
        _selectedProgressCategory.value = ProgressCategory.REVIEW_DUE
    }

    /** 単語カードのフッターボタン音を切り替える */
    fun toggleButtonSound() {
        val enabled = !_buttonSoundEnabled.value
        _buttonSoundEnabled.value = enabled
        userPreferences.setButtonSoundEnabled(enabled)
    }

    /** 1日の目標単語数を設定 */
    fun setDailyTarget(target: Int) {
        viewModelScope.launch {
            repository.setDailyTarget(target)
        }
    }

    /** 直近1日だけ空いたストリークを、今日2日分学習して救済する。 */
    fun repairStreak() {
        viewModelScope.launch {
            repository.repairStreak()
        }
    }

    /** 救済チケットを1枚使って、直近1日分の未達成を救済する。 */
    fun repairStreakWithTicket() {
        viewModelScope.launch {
            repository.repairStreakWithTicket()
        }
    }

    // お気に入りの切り替え
    fun toggleFavorite(itemId: Long) {
        viewModelScope.launch {
            vocabularyMutationMutex.withLock {
                repository.toggleFavorite(itemId)
                repository.recordHistory(itemId, HistoryAction.FAVORITE)
            }
        }
    }

    // 学習結果の更新。習熟度は未マスター／マスター済みの2状態だけで管理する。
    // recordHistory=false は、復習状態だけを更新して履歴を別操作にまとめる場合に使用する。
    fun updateReviewStatus(itemId: Long, remembered: Boolean, recordHistory: Boolean = true) {
        viewModelScope.launch {
            vocabularyMutationMutex.withLock {
                repository.setMastered(itemId, isMastered = remembered)
                if (recordHistory) {
                    repository.recordHistory(
                        itemId,
                        if (remembered) HistoryAction.REVIEW_REMEMBERED else HistoryAction.REVIEW_FORGOT
                    )
                }
                recordStudyActivity()
            }
        }
    }

    // 単語カード: 青カエルをマスター済みにして次の単語へ。
    // お気に入りフラッシュカードでは、マスター時にお気に入りも解除する。
    fun setMastered(itemId: Long, removeFromFavorites: Boolean = false) {
        viewModelScope.launch {
            vocabularyMutationMutex.withLock {
                val item = _allVocabulary.value.firstOrNull { it.id == itemId }
                    ?: return@withLock

                repository.setMastered(itemId, isMastered = true)
                repository.recordHistory(itemId, HistoryAction.REVIEW_REMEMBERED)
                if (removeFromFavorites && item.isFavorite) {
                    // お気に入りタブでのマスターは、マスター履歴1件だけを記録する。
                    // お気に入り解除はカードをデッキから外すための内部処理であり、
                    // 別の学習アクション履歴としては扱わない。
                    repository.toggleFavorite(itemId)
                }
                recordStudyActivity()
            }
        }
    }

    // 履歴タブ: 青カエルの状態を青カエル ⇄ ○で切り替える。
    fun toggleMastered(itemId: Long) {
        viewModelScope.launch {
            vocabularyMutationMutex.withLock {
                val item = _allVocabulary.value.firstOrNull { it.id == itemId }
                    ?: return@withLock
                val mastered = !item.isMastered

                repository.setMastered(itemId, isMastered = mastered)
                repository.recordHistory(
                    itemId,
                    if (mastered) HistoryAction.REVIEW_REMEMBERED else HistoryAction.REVIEW_UNMASTERED
                )
                recordStudyActivity()
            }
        }
    }

    // 新しい単語をローカルに追加（ユーザー作成用）
    fun addCustomVocabulary(word: String, meaning: String, example: String) {
        viewModelScope.launch {
            if (word.isNotBlank() && meaning.isNotBlank()) {
                repository.addVocabulary(
                    VocabularyItem(
                        id = 0, // Room generates ID automatically
                        word = word.trim(),
                        meaning = meaning.trim(),
                        example = example.trim()
                    )
                )
            }
        }
    }
}

private fun accessibleLevel(
    level: VocabularyLevel,
    access: PremiumAccess
): VocabularyLevel = if (level.requiresPremium() && !access.isPremiumUnlocked()) {
    VocabularyLevel.TOEIC_500
} else {
    level.toStudyTier()
}
