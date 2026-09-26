package com.gachiguild.gachitoefl.data.ai

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.graphics.drawable.Drawable
import android.net.Uri

enum class AiAppProvider(
    val packageName: String,
    val fallbackLabel: String
) {
    CHATGPT("com.openai.chatgpt", "ChatGPT"),
    GEMINI("com.google.android.apps.bard", "Gemini")
}

data class InstalledAiApp(
    val provider: AiAppProvider,
    val packageName: String,
    val label: String,
    val icon: Drawable
)

sealed interface AiLaunchResult {
    data class Launched(val app: InstalledAiApp) : AiLaunchResult
    data class Failed(val app: InstalledAiApp) : AiLaunchResult
}

/**
 * インストール済みの対応AIアプリの検出と、通常の起動画面へのIntent起動を担当する。
 * Live専用の外部Intentは各社が公開していないため、Live操作は起動後にユーザーへ案内する。
 */
object AiAppLauncher {
    private val supportedProviders = AiAppProvider.entries

    fun installedApps(context: Context): List<InstalledAiApp> {
        val packageManager = context.packageManager
        return supportedProviders.mapNotNull { provider ->
            runCatching {
                val applicationInfo = packageManager.getApplicationInfo(provider.packageName, 0)
                InstalledAiApp(
                    provider = provider,
                    packageName = provider.packageName,
                    label = applicationInfo.loadLabel(packageManager).toString()
                        .ifBlank { provider.fallbackLabel },
                    icon = applicationInfo.loadIcon(packageManager)
                )
            }.getOrNull()
        }
    }

    fun launch(context: Context, app: InstalledAiApp): AiLaunchResult {
        val launchIntent = context.packageManager.getLaunchIntentForPackage(app.packageName)
            ?: return AiLaunchResult.Failed(app)

        return try {
            context.startActivity(launchIntent)
            AiLaunchResult.Launched(app)
        } catch (_: ActivityNotFoundException) {
            AiLaunchResult.Failed(app)
        } catch (_: SecurityException) {
            AiLaunchResult.Failed(app)
        }
    }

    /** Google Playの公式アプリページを開く。未インストール時のオンボーディングで使用する。 */
    fun openStore(context: Context, provider: AiAppProvider): Boolean {
        val marketIntent = Intent(
            Intent.ACTION_VIEW,
            Uri.parse("market://details?id=${provider.packageName}")
        ).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        return try {
            context.startActivity(marketIntent)
            true
        } catch (_: ActivityNotFoundException) {
            val webIntent = Intent(
                Intent.ACTION_VIEW,
                Uri.parse("https://play.google.com/store/apps/details?id=${provider.packageName}")
            ).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            runCatching {
                context.startActivity(webIntent)
                true
            }.getOrDefault(false)
        } catch (_: SecurityException) {
            false
        }
    }

}
