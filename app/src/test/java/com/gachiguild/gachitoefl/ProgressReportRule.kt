package com.gachiguild.gachitoefl

import org.junit.rules.TestWatcher
import org.junit.runner.Description

/**
 * テスト実行の進捗を3分単位で報告するカスタムルール。
 *
 * 各テストメソッドの開始を即座に表示し、
 * それ以降は3分（180秒）ごとに経過時間を標準出力へ書き出す。
 * Robolectric などの低速テストでの「進捗が見えない」問題を解消する。
 */
class ProgressReportRule : TestWatcher() {

    private var startTimeMillis: Long = 0L
    private var reporterThread: Thread? = null

    override fun starting(description: Description) {
        val testName = description.methodName
        startTimeMillis = System.currentTimeMillis()
        println("\n[進捗] テスト開始: $testName")

        // 3分ごとに経過時間を報告するデーモンスレッドを起動
        reporterThread = Thread {
            while (!Thread.currentThread().isInterrupted) {
                try {
                    Thread.sleep(PROGRESS_INTERVAL_MILLIS)
                } catch (e: InterruptedException) {
                    break
                }
                val elapsedMinutes = elapsedSeconds() / 60
                println("[進捗] $testName 実行中... ${elapsedMinutes}分経過 (進行中)")
            }
        }.apply {
            isDaemon = true
            name = "progress-reporter-$testName"
            start()
        }
    }

    override fun succeeded(description: Description) {
        stopReporter()
        println("[進捗] ${description.methodName} 成功 (${elapsedSeconds()}秒)")
    }

    override fun failed(e: Throwable, description: Description) {
        stopReporter()
        println("[進捗] ${description.methodName} 失敗 (${elapsedSeconds()}秒)")
    }

    override fun finished(description: Description) {
        stopReporter()
    }

    private fun stopReporter() {
        reporterThread?.interrupt()
        reporterThread = null
    }

    private fun elapsedSeconds(): Long =
        (System.currentTimeMillis() - startTimeMillis) / 1000

    companion object {
        /** 進捗報告の間隔: 3分 = 180,000ミリ秒 */
        const val PROGRESS_INTERVAL_MILLIS = 180_000L
    }
}