package com.gachiguild.gachitoeic.presentation.viewmodel

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gachiguild.gachitoeic.data.backup.BackupDocument
import com.gachiguild.gachitoeic.data.backup.BackupService
import com.gachiguild.gachitoeic.data.backup.RestoreResult
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class BackupUiState(
    val busy: Boolean = false,
    val pendingRestore: BackupDocument? = null,
    val result: RestoreResult? = null,
    val message: BackupUiMessage? = null,
    val error: BackupUiMessage? = null
)

/** バックアップ処理の結果。表示文言は画面側の言語設定で解決する。 */
enum class BackupUiMessage {
    BACKUP_SAVED,
    BACKUP_SAVE_FAILED,
    BACKUP_READ_FAILED,
    RESTORE_FAILED
}

@HiltViewModel
class BackupViewModel @Inject constructor(
    private val backupService: BackupService,
    @ApplicationContext context: Context
) : ViewModel() {
    private val contentResolver = context.contentResolver
    private val _state = MutableStateFlow(BackupUiState())
    val state: StateFlow<BackupUiState> = _state.asStateFlow()

    fun suggestedFileName(): String = "TOEIC_G_${
        SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
    }.toeic-backup"

    fun writeBackup(uri: Uri) {
        if (_state.value.busy) return
        viewModelScope.launch {
            _state.value = BackupUiState(busy = true)
            try {
                val output = contentResolver.openOutputStream(uri)
                    ?: run {
                        _state.value = BackupUiState(error = BackupUiMessage.BACKUP_SAVE_FAILED)
                        return@launch
                    }
                withContext(Dispatchers.IO) { backupService.writeBackup(output) }
                _state.value = BackupUiState(message = BackupUiMessage.BACKUP_SAVED)
            } catch (_: Exception) {
                _state.value = BackupUiState(error = BackupUiMessage.BACKUP_SAVE_FAILED)
            }
        }
    }

    fun prepareRestore(uri: Uri) {
        if (_state.value.busy) return
        viewModelScope.launch {
            _state.value = BackupUiState(busy = true)
            try {
                val input = contentResolver.openInputStream(uri)
                    ?: run {
                        _state.value = BackupUiState(error = BackupUiMessage.BACKUP_READ_FAILED)
                        return@launch
                    }
                val document = withContext(Dispatchers.IO) { backupService.readBackup(input) }
                _state.value = BackupUiState(pendingRestore = document)
            } catch (_: Exception) {
                _state.value = BackupUiState(error = BackupUiMessage.BACKUP_READ_FAILED)
            }
        }
    }

    fun cancelRestore() {
        if (!_state.value.busy) _state.value = BackupUiState()
    }

    fun confirmRestore() {
        val document = _state.value.pendingRestore ?: return
        if (_state.value.busy) return
        viewModelScope.launch {
            _state.value = _state.value.copy(busy = true)
            try {
                val result = withContext(Dispatchers.IO) { backupService.restore(document) }
                _state.value = BackupUiState(result = result)
            } catch (_: Exception) {
                _state.value = BackupUiState(error = BackupUiMessage.RESTORE_FAILED)
            }
        }
    }

    fun clearMessage() {
        _state.value = _state.value.copy(result = null, message = null, error = null)
    }
}
