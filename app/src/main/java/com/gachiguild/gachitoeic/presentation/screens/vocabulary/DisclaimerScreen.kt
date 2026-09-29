package com.gachiguild.gachitoeic.presentation.screens.vocabulary

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gachiguild.gachitoeic.ui.LocalAppStrings

private const val PRIVACY_POLICY_URL =
    "https://hajadon187-a11y.github.io/gg-toeic-privacy-policy/"

private data class DisclaimerSectionCopy(val title: String, val body: String)

private data class DisclaimerCopy(
    val title: String,
    val metadata: String,
    val operator: String,
    val contact: String,
    val introduction: String,
    val privacyLink: String,
    val acknowledgement: String,
    val start: String,
    val close: String,
    val end: String,
    val sections: List<DisclaimerSectionCopy>
)

private fun section(title: String, body: String) =
    DisclaimerSectionCopy(title, body.trimIndent())

private fun disclaimerCopy(languageCode: String): DisclaimerCopy = when (languageCode) {
    "ja" -> japaneseDisclaimer()
    "zh" -> chineseDisclaimer()
    "hi" -> hindiDisclaimer()
    "vi" -> vietnameseDisclaimer()
    "ko" -> koreanDisclaimer()
    "id" -> indonesianDisclaimer()
    "th" -> thaiDisclaimer()
    "es" -> spanishDisclaimer()
    else -> englishDisclaimer()
}

@Composable
fun DisclaimerScreen(
    initial: Boolean,
    onComplete: () -> Unit
) {
    val context = LocalContext.current
    val copy = disclaimerCopy(LocalAppStrings.current.languageCode)
    val scrollState = rememberScrollState()
    var acknowledged by rememberSaveable { mutableStateOf(false) }
    val hasReadToEnd by remember {
        derivedStateOf {
            scrollState.maxValue == 0 || scrollState.value >= scrollState.maxValue - 24
        }
    }
    val canComplete = !initial || (hasReadToEnd && acknowledged)

    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .safeDrawingPadding()
                .padding(horizontal = 20.dp, vertical = 16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = copy.title,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                if (!initial) TextButton(onClick = onComplete) { Text(copy.close) }
            }

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(scrollState),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(copy.metadata)
                Text(copy.operator)
                Text(copy.contact)
                Text(copy.introduction)
                copy.sections.forEachIndexed { index, item ->
                    DisclaimerSection(item.title) {
                        Text(item.body)
                        if (index == 5) {
                            TextButton(
                                onClick = {
                                    runCatching {
                                        context.startActivity(
                                            Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACY_POLICY_URL))
                                        )
                                    }
                                },
                                contentPadding = PaddingValues(0.dp)
                            ) { Text(copy.privacyLink) }
                        }
                    }
                }
                if (copy.end.isNotBlank()) {
                    Text(copy.end, modifier = Modifier.padding(bottom = 12.dp))
                }
            }

            if (initial) {
                Spacer(modifier = Modifier.height(8.dp))
                HorizontalDivider()
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = acknowledged,
                            onCheckedChange = { if (hasReadToEnd) acknowledged = it },
                            enabled = hasReadToEnd
                        )
                        Text(copy.acknowledgement)
                    }
                }
            }

            Button(
                onClick = onComplete,
                enabled = canComplete,
                modifier = Modifier.fillMaxWidth()
            ) { Text(if (initial) copy.start else copy.close) }
        }
    }
}

@Composable
private fun DisclaimerSection(title: String, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        content()
    }
}

private fun japaneseDisclaimer() = DisclaimerCopy(
    title = "ご利用前の重要事項・免責事項",
    metadata = "制定日：2026年9月29日\n最終更新日：2026年9月29日",
    operator = "運営者：ガチギルド",
    contact = "お問い合わせ先：gachiguild@gmail.com",
    introduction = "本アプリ「GG TOEIC」（以下「本アプリ」といいます）をご利用になる前に、以下の内容をご確認ください。\n\n本アプリを利用した場合、利用者は本免責事項の内容を確認し、了承したものとみなされます。",
    privacyLink = "プライバシーポリシーを開く",
    acknowledgement = "内容を確認しました",
    start = "確認して利用を開始",
    close = "閉じる",
    end = "以上",
    sections = listOf(
        section("1. 本アプリの目的", """
            本アプリは、TOEIC受験を目指す方のための英単語学習、発音練習および英会話練習を補助するアプリです。

            本アプリは、TOEICの公式教材、公式試験、公式採点サービス、語学学校、教育機関または試験実施団体ではありません。

            本アプリは、TOEICの運営団体、試験実施団体、大学、教育機関その他の第三者から、公式に承認、推奨、保証または提携されているものではありません。

            「TOEIC」は、関係する権利者が保有する商標です。
        """),
        section("2. 学習成果について", """
            本アプリを利用することにより、以下の結果が得られることを保証するものではありません。

            ・TOEICのスコア向上
            ・目標スコアの達成
            ・TOEIC試験への合格
            ・英語力、語彙力、発音または会話力の向上
            ・進学、就職または資格取得

            学習成果は、利用者の学習時間、学習方法、現在の英語力、試験内容、受験環境その他の事情によって異なります。

            本アプリの学習内容だけで十分とは限りません。必要に応じて、TOEIC公式教材、教師、専門家、語学学校その他の信頼できる情報源も併せてご利用ください。
        """),
        section("3. 学習コンテンツについて", """
            本アプリに掲載される単語、意味、例文、同義語、コロケーション、発音情報、難易度、スコア区分その他の学習情報について、正確性、完全性、最新性または特定の目的への適合性を保証するものではありません。

            翻訳、例文、発音表記、難易度判定などに誤り、不自然な表現、地域差または見解の相違が含まれる場合があります。

            本アプリに表示されるスコア区分や難易度は、学習上の目安であり、TOEIC公式の評価、出題範囲または採点基準を示すものではありません。

            本アプリの語彙データは、AIを活用して候補語の選定、意味、例文、翻訳および学習レベルの作成・分類を行い、運営者が確認・編集したものです。AIによる生成または分類には、誤情報や誤分類が含まれる可能性があります。
        """),
        section("4. 翻訳および多言語表示について", """
            本アプリでは、日本語、英語その他の複数の言語で表示される場合があります。

            翻訳は学習上の参考情報であり、すべての言語で正確、自然または完全に同一の内容になることを保証するものではありません。

            言語によって、表現、説明の詳しさ、例文、語順または表示内容に差が生じる場合があります。

            本免責事項の日本語版と他言語版に相違がある場合は、日本語版を優先します。
        """),
        section("5. AIサービスについて", """
            本アプリは、ChatGPTまたはGeminiなど、第三者が提供するAIアプリを起動し、英会話、発音および学習の練習に利用できる機能を提供します。

            本アプリは、ChatGPTまたはGeminiを起動しますが、本アプリが利用者の入力内容を自動的にこれらのサービスへ送信するものではありません。

            利用者が起動先のAIサービスに入力または送信した情報については、各サービス提供者の利用規約およびプライバシーポリシーが適用されます。

            AIによる回答、翻訳、発音指導、文法説明、会話内容その他の出力には、誤り、不正確な情報、不適切な表現、古い情報または利用者に適さない内容が含まれる場合があります。

            AIの出力は、TOEICの公式採点、教師や専門家による指導、医療、法律、金融その他の専門的な助言の代わりにはなりません。

            重要な判断をAIの出力だけに基づいて行わないでください。
        """),
        section("6. 個人情報および入力内容について", """
            本アプリまたは外部AIサービスに、以下のような重要または機密性の高い情報を入力しないでください。

            ・パスワード、暗証番号、認証コード
            ・クレジットカード情報、銀行口座情報
            ・パスポート番号、身分証明書番号
            ・住所、電話番号、位置情報
            ・健康情報、病歴、勤務先情報
            ・他人の個人情報
            ・その他、第三者に知られたくない情報

            本アプリにおける個人情報および利用データの取扱いについては、以下のプライバシーポリシーをご確認ください。

            ChatGPT、Geminiその他の外部サービスに入力・送信した情報は、それぞれのサービス提供者の方針に従って取り扱われます。
        """),
        section("7. バックアップおよび学習データについて", """
            本アプリでは、学習データをバックアップファイルとして保存または復元できる場合があります。

            バックアップファイルには、単語の学習状況、学習履歴、お気に入り、連続学習日数、学習設定その他のアプリ内データが含まれる場合があります。

            バックアップは自動で行われるものではありません。利用者自身が必要に応じて作成してください。

            バックアップファイルは暗号化されていないため、利用者自身の責任で安全に保管してください。第三者が取得した場合、ファイルの内容を閲覧される可能性があります。

            バックアップファイルの紛失、破損、不正利用、第三者への漏えいまたは復元失敗について、運営者は責任を負いません。

            復元操作により、現在の学習データが置き換えられる場合があります。復元前に、必要に応じて現在のデータを別途バックアップしてください。

            端末の故障、アプリの削除、端末の初期化、アプリデータの消去その他の事情により、バックアップを作成していないデータが失われる場合があります。
        """),
        section("8. AndroidのTTSおよび音声機能について", """
            本アプリの発音および読み上げ機能は、Android端末、OS、TTSエンジン、音声データ、端末設定その他の環境に依存します。

            端末やTTSエンジンによって、発音、アクセント、音声の自然さ、再生速度、利用可能な言語および音声品質が異なる場合があります。

            すべての端末または言語で、音声が正常に再生されることを保証するものではありません。

            音声が再生されない場合は、端末の音量、TTS設定、音声データ、ネットワーク接続および端末の対応状況をご確認ください。

            本アプリの音声は学習上の参考情報であり、TOEIC公式の発音評価または専門家による発音指導を保証するものではありません。

            ChatGPTまたはGeminiなどの外部アプリで音声会話を利用する場合、マイク、音声データおよび録音等の取扱いは各外部アプリの規約およびプライバシーポリシーに従います。
        """),
        section("9. 通知および端末環境について", """
            通知機能は、利用者の許可、Androidの設定、端末の状態、電池最適化、ネットワーク環境その他の事情により、表示または到達しない場合があります。

            通知が表示されなかったこと、予定した時刻と異なる時刻に表示されたこと、または通知内容が変更されたことについて、運営者は責任を負いません。

            本アプリについて、すべての端末、OS、画面サイズ、通信環境または外部サービスで正常に動作することを保証するものではありません。
        """),
        section("10. 未成年者の利用について", """
            未成年者が本アプリを利用する場合は、保護者または法定代理人の同意を得たうえで利用してください。

            未成年者は、氏名、住所、学校名、電話番号、顔写真、位置情報その他の個人情報を、本アプリまたは外部AIサービスに入力・送信しないでください。

            保護者または法定代理人は、未成年者による本アプリおよび外部AIサービスの利用状況を適切に確認してください。

            運営者が別途対象年齢を定める場合は、本アプリ内または配布ストア上に表示します。
        """),
        section("11. Google Playおよびプレミアム機能について", """
            本アプリには、TOEICの上級レベルの単語など、一部の有料機能が含まれる場合があります。

            価格は、購入時にGoogle Play上に表示される価格が適用されます。価格、通貨、税金、販売条件または提供内容は、変更される場合があります。

            購入状況の確認および購入の復元には、Google Playのアカウント、決済状況、端末環境および通信環境が影響する場合があります。

            購入処理中の状態、決済サービスの障害、購入情報の反映遅延、アカウント変更または端末変更により、購入直後に機能が利用できない場合があります。

            購入の復元を行う場合は、購入時と同じGoogle Playアカウントを使用してください。

            返金、キャンセルおよび購入に関する手続きは、Google Playの規約、手続きおよび適用される法令に従います。
        """),
        section("12. アプリの変更、停止および提供終了について", """
            運営者は、必要に応じて、本アプリの内容、機能、デザイン、対応端末、対応OS、対応する外部AIサービス、料金、掲載情報または本免責事項を変更する場合があります。

            運営者は、必要に応じて、本アプリの全部または一部の提供を停止または終了する場合があります。

            変更、停止または終了により、過去に利用できた機能、学習内容、外部サービス連携または保存データが利用できなくなる場合があります。

            重要な変更を行う場合は、可能な範囲で本アプリ内、公式ページその他の適切な方法でお知らせします。

            学習データを継続して保管する必要がある場合は、利用者自身で定期的にバックアップを作成してください。
        """),
        section("13. 知的財産権および商標について", """
            本アプリに含まれるプログラム、デザイン、文章、画像、音声、データベースその他のコンテンツに関する権利は、運営者または正当な権利者に帰属します。

            法令で認められる場合を除き、運営者の許可なく、本アプリのコンテンツを複製、転載、販売、配布、改変または二次利用することは禁止します。

            TOEIC、ChatGPT、Gemini、Android、Google Playその他の名称および商標は、それぞれの権利者に帰属します。

            本アプリは、TOEICの運営団体、ChatGPTの提供者、Geminiの提供者、Googleその他の第三者と提携、承認または保証関係にあるものではありません。
        """),
        section("14. 利用者の責任", """
            利用者は、自己の責任において本アプリを利用するものとします。

            利用者が本アプリまたは外部サービスを利用して第三者に損害を与えた場合、利用者自身の責任と費用で解決するものとします。

            本アプリを、違法行為、第三者への迷惑行為、不正アクセス、著作権侵害その他の不正な目的で利用しないでください。
        """),
        section("15. 損害賠償について", """
            運営者は、法令上許される範囲で、本アプリの利用または利用不能により生じた間接損害、特別損害、逸失利益、データの消失その他の損害について責任を負わないものとします。

            ただし、運営者の故意または重大な過失によって生じた損害、身体または生命に関する損害、その他適用される法令により免責または制限が認められない損害については、この限りではありません。
        """),
        section("16. お問い合わせ", """
            本免責事項、本アプリの内容または利用に関するお問い合わせは、以下までご連絡ください。

            運営者：ガチギルド
            メールアドレス：gachiguild@gmail.com
        """)
    )
)

private fun translatedDisclaimer(
    title: String,
    metadata: String,
    operator: String,
    contact: String,
    introduction: String,
    privacyLink: String,
    acknowledgement: String,
    start: String,
    close: String,
    sections: List<DisclaimerSectionCopy>
) = DisclaimerCopy(
    title = title,
    metadata = metadata,
    operator = operator,
    contact = contact,
    introduction = introduction,
    privacyLink = privacyLink,
    acknowledgement = acknowledgement,
    start = start,
    close = close,
    end = "",
    sections = sections
)

private fun englishDisclaimer() = translatedDisclaimer(
    title = "Important Information and Disclaimer Before Using the App",
    metadata = "Date of enactment: September 29, 2026\nLast updated: September 29, 2026",
    operator = "Operator: GachiGuild",
    contact = "Contact: gachiguild@gmail.com",
    introduction = "Please read the following before using the “GG TOEIC” app (the “App”).\n\nBy using the App, you are considered to have read and understood this disclaimer.",
    privacyLink = "Open Privacy Policy",
    acknowledgement = "I have confirmed the information above",
    start = "Confirm and start using",
    close = "Close",
    sections = listOf(
        section("1. Purpose of the App", "The App supports TOEIC vocabulary study, pronunciation practice, and English conversation practice. It is not official TOEIC material, an official examination, an official scoring service, a language school, an educational institution, or an examination organization. It is not officially approved, recommended, guaranteed, or affiliated with TOEIC organizations, examination bodies, universities, educational institutions, or other third parties. “TOEIC” is a trademark of its respective rights holders."),
        section("2. Learning Results", "Use of the App does not guarantee improved TOEIC scores, achievement of a target score, passing the TOEIC examination, improvement in English, vocabulary, pronunciation, or conversation skills, admission, employment, or certification. Results vary according to study time and methods, language level, examination content, and examination environment. Use official materials, teachers, experts, language schools, and other reliable sources as appropriate."),
        section("3. Learning Content", "The App does not guarantee the accuracy, completeness, timeliness, or fitness for a particular purpose of its words, meanings, examples, synonyms, collocations, pronunciation information, difficulty levels, score classifications, or other learning information. Translations, examples, pronunciation notation, and difficulty classifications may contain errors, unnatural expressions, regional differences, or differences of opinion. Score ranges and difficulty levels are study references only and do not represent official TOEIC evaluations, test coverage, or scoring criteria. Vocabulary data was created and classified with AI assistance and reviewed and edited by the operator; errors or incorrect classifications may remain."),
        section("4. Translations and Multiple Languages", "The App may be displayed in English, Japanese, Chinese, Hindi, Vietnamese, Korean, Indonesian, Thai, Spanish, and other languages. Translations are for study reference only and are not guaranteed to be accurate, natural, or identical in every language. Expressions, detail, examples, word order, or displayed content may differ by language. If the Japanese and another language version of this disclaimer differ, the Japanese version prevails."),
        section("5. AI Services", "The App may launch third-party AI apps such as ChatGPT or Gemini for English conversation, pronunciation, and study practice. The App only launches those services and does not automatically send your input. Information entered or sent in an external AI service is governed by that provider’s terms and privacy policy. AI answers, translations, pronunciation guidance, grammar explanations, and conversations may contain errors, inaccurate, inappropriate, or outdated information. Do not rely on AI output alone for important decisions."),
        section("6. Personal Information and Input", "Do not enter passwords, authentication codes, card or bank details, passport or identity numbers, addresses, phone numbers, location information, health information, workplace information, another person’s personal information, or other information you do not want third parties to know into the App or an external AI service. See the Privacy Policy below for how personal information and usage data are handled. Information sent to ChatGPT, Gemini, or other external services is handled according to the relevant provider’s policy."),
        section("7. Backups and Study Data", "The App may allow study data to be saved to or restored from a backup file. A backup may include word-learning status, history, favorites, consecutive study days, study settings, and other in-app data. Backups are not automatic. Backup files are not encrypted, so keep them secure. The operator is not responsible for loss, damage, misuse, leakage, or restoration failure. Restoration may replace current study data; make a separate backup before restoring. Unbacked data may be lost due to device failure, App deletion, device reset, or clearing App data."),
        section("8. Android TTS and Audio Features", "Pronunciation and reading features depend on the Android device, operating system, TTS engine, voice data, and device settings. Pronunciation, accent, naturalness, speed, available languages, and audio quality may vary by device or TTS engine. Audio is not guaranteed to play on every device or language. If audio does not play, check the volume, TTS settings, voice data, network connection, and device compatibility. App audio is a study reference and does not provide official TOEIC pronunciation assessment or expert instruction. Voice conversations in external apps are governed by those apps’ policies regarding microphones, voice data, and recordings."),
        section("9. Notifications and Device Environment", "Notifications may not appear or arrive because of user permission, Android settings, device state, battery optimization, network conditions, or other reasons. The operator is not responsible for missing notifications, different notification times, or changed notification content. The App is not guaranteed to operate normally on every device, operating system, screen size, network, or external service."),
        section("10. Use by Minors", "Minors must obtain consent from a parent or legal guardian before using the App. Minors should not enter or send their name, address, school name, phone number, photograph, location, or other personal information to the App or an external AI service. Parents or legal guardians should appropriately monitor use of the App and external AI services. If the operator specifies an age requirement, it will be shown in the App or distribution store."),
        section("11. Google Play and Premium Features", "The App may include paid features such as advanced-level TOEIC vocabulary. The price shown on Google Play at the time of purchase applies; prices, currency, taxes, terms of sale, or content may change. Purchase verification and restoration may depend on the Google Play account, payment status, device, and network. Pending purchases, payment failures, delays, or account/device changes may prevent immediate access. Use the same Google Play account used for the purchase when restoring it. Refunds, cancellations, and purchase procedures follow Google Play’s terms and procedures and applicable law."),
        section("12. Changes, Suspension, and Termination", "The operator may change the App’s content, features, design, supported devices or operating systems, external AI services, prices, information, or this disclaimer, and may suspend or terminate all or part of the service. This may make previously available features, learning content, external connections, or saved data unavailable. Important changes will be announced through the App, an official page, or another appropriate method where practicable. Regularly back up study data that you need to keep."),
        section("13. Intellectual Property and Trademarks", "Rights in the App’s programs, design, text, images, audio, databases, and other content belong to the operator or the rightful rights holders. Unless permitted by law, copying, republishing, selling, distributing, modifying, or reusing the content without permission is prohibited. TOEIC, ChatGPT, Gemini, Android, Google Play, and other names are trademarks of their respective owners. The App is not affiliated with, approved, or endorsed by any of those third parties."),
        section("14. User Responsibility", "Users use the App at their own risk and responsibility. If use of the App or an external service causes damage to a third party, the user must resolve it at the user’s own responsibility and expense. Do not use the App for illegal acts, harassment, unauthorized access, copyright infringement, or other improper purposes."),
        section("15. Damages", "To the extent permitted by law, the operator is not responsible for indirect or special damages, lost profits, data loss, or other damages arising from use of or inability to use the App. This does not apply to damage caused by the operator’s willful misconduct or gross negligence, death or personal injury, or damage that cannot legally be excluded or limited."),
        section("16. Contact", "For questions about this disclaimer, the App’s content, or use of the App, contact:\n\nOperator: GachiGuild\nEmail: gachiguild@gmail.com")
    )

)

private fun chineseDisclaimer() = translatedDisclaimer(
    title = "使用前重要事项与免责声明",
    metadata = "制定日期：2026年9月29日\n最后更新日期：2026年9月29日",
    operator = "运营者：GachiGuild",
    contact = "联系方式：gachiguild@gmail.com",
    introduction = "使用“GG TOEIC”（以下简称“本应用”）前，请阅读以下内容。\n\n使用本应用即表示您已阅读并了解本免责声明。",
    privacyLink = "打开隐私政策",
    acknowledgement = "我已阅读并确认上述内容",
    start = "确认并开始使用",
    close = "关闭",
    sections = listOf(
        section("1. 本应用的目的", "本应用旨在辅助TOEIC考生学习词汇、练习发音和英语会话。本应用不是TOEIC官方教材、官方考试、官方评分服务、语言学校、教育机构或考试机构，也未获得相关机构或其他第三方的官方认可、推荐、保证或合作。“TOEIC”是相关权利人拥有的商标。"),
        section("2. 学习成果", "使用本应用不保证提高TOEIC分数、达到目标分数、通过考试、提高英语、词汇、发音或会话能力，也不保证升学、就业或取得资格。结果会因学习时间、方法、语言水平、考试内容和考试环境而不同。请根据需要结合官方教材、教师、专家和可靠来源。"),
        section("3. 学习内容", "本应用中的单词、释义、例句、同义词、搭配、发音、难度、分数区间分类及其他学习信息不保证准确、完整、最新或适合特定目的。翻译、例句、发音标记和难度判断可能存在错误、不自然表达、地区差异或观点差异。分数区间和难度仅供学习参考，不代表TOEIC官方评价、考试范围或评分标准。词汇数据使用AI辅助制作和分类，并由运营者确认、编辑，但仍可能存在错误。"),
        section("4. 翻译和多语言显示", "本应用可能以中文、日文、英文及其他语言显示。翻译仅供学习参考，不保证所有语言都准确、自然或完全一致。不同语言之间可能存在措辞、说明详略、例句、语序或显示内容的差异。本免责声明的日文版与其他语言版本不一致时，以日文版为准。"),
        section("5. AI服务", "本应用可启动ChatGPT或Gemini等第三方AI应用，用于英语会话、发音和学习练习。本应用只负责启动服务，不会自动发送您输入的内容。您在外部AI服务中输入或发送的信息适用相应服务的条款和隐私政策。AI输出可能存在错误、不准确、不适当或过时的信息，不能替代TOEIC官方评分、教师或专家指导，也不构成医疗、法律、金融等专业建议。请勿仅依据AI输出作出重要判断。"),
        section("6. 个人信息和输入内容", "请勿在本应用或外部AI服务中输入密码、验证码、银行卡信息、护照或身份证号码、地址、电话、位置、健康信息、工作信息、他人个人信息或不希望第三方知道的信息。个人信息和使用数据的处理请查看下方的隐私政策。向ChatGPT、Gemini或其他外部服务发送的信息将按相应服务提供商的政策处理。"),
        section("7. 备份和学习数据", "本应用可能支持将学习数据保存为备份文件或从备份文件恢复。备份可能包含单词学习状态、历史、收藏、连续学习天数、学习设置和其他应用内数据。备份不会自动进行。备份文件未经加密，请安全保管。运营者不对文件丢失、损坏、滥用、泄露或恢复失败负责。恢复可能替换当前学习数据，恢复前请另行备份。设备故障、删除应用、重置设备或清除应用数据可能导致未备份数据丢失。"),
        section("8. Android TTS和音频功能", "发音和朗读功能取决于Android设备、系统、TTS引擎、语音数据和设置。不同设备或TTS引擎的发音、口音、自然度、速度、语言和音质可能不同。不保证所有设备或语言都能正常播放。若无法播放，请检查音量、TTS设置、语音数据、网络和设备兼容性。本应用音频仅供学习参考，不保证TOEIC官方发音评价或专家指导。外部应用中的语音会话按其关于麦克风、语音数据和录音的政策处理。"),
        section("9. 通知和设备环境", "通知可能因用户许可、Android设置、设备状态、电池优化、网络或其他原因无法显示或送达。运营者不对通知缺失、时间不同或内容变更负责。不保证本应用能在所有设备、系统、屏幕、网络或外部服务中正常运行。"),
        section("10. 未成年人使用", "未成年人使用本应用时应取得监护人或法定代理人的同意。不得向本应用或外部AI服务输入或发送姓名、住址、学校、电话、照片、位置或其他个人信息。监护人或法定代理人应适当监督本应用及外部AI服务的使用情况。若运营者另行规定适用年龄，将在应用内或应用商店显示。"),
        section("11. Google Play和高级功能", "本应用可能包含TOEIC高级词汇等付费功能。购买时适用Google Play显示的价格，价格、货币、税费、销售条款或内容可能变化。购买验证和恢复购买可能受Google Play账号、付款状态、设备和网络影响。购买处理中、支付故障、信息延迟或账号/设备变化可能导致暂时无法使用。恢复购买请使用购买时使用的同一Google Play账号。退款、取消及购买手续遵循Google Play条款、流程和适用法律。"),
        section("12. 应用变更、停止和终止", "运营者可能变更本应用的内容、功能、设计、支持设备或系统、外部AI服务、价格、信息或本免责声明，也可能停止或终止全部或部分服务。这可能导致功能、学习内容、外部连接或保存数据无法使用。重要变更将在可行范围内通过应用、官方页面或其他适当方式通知。需要保留的学习数据请自行定期备份。"),
        section("13. 知识产权和商标", "本应用的程序、设计、文字、图像、音频、数据库及其他内容的权利属于运营者或合法权利人。除法律允许外，未经许可不得复制、转载、销售、分发、修改或二次使用。TOEIC、ChatGPT、Gemini、Android、Google Play等名称和商标属于各自权利人。本应用与这些第三方不存在关联、合作、认可或背书关系。"),
        section("14. 用户责任", "用户应自行负责使用本应用。因使用本应用或外部服务给第三方造成损害时，用户应自行承担责任和费用解决。不得将本应用用于违法、骚扰、未经授权访问、侵犯版权或其他不正当目的。"),
        section("15. 损害赔偿", "在法律允许的范围内，运营者不对因使用或无法使用本应用产生的间接损害、特别损害、利润损失、数据丢失或其他损害负责。但运营者故意或重大过失造成的损害、生命或身体损害，以及法律不允许免责或限制的损害不受此限。"),
        section("16. 联系方式", "有关本免责声明、本应用内容或使用的问题，请联系：\n\n运营者：GachiGuild\n邮箱：gachiguild@gmail.com")
    )
)

private fun koreanDisclaimer() = translatedDisclaimer(
    title = "이용 전 중요 사항 및 면책사항",
    metadata = "제정일: 2026년 9월 28일\n최종 업데이트: 2026년 9월 28일",
    operator = "운영자: GachiGuild",
    contact = "문의: gachiguild@gmail.com",
    introduction = "‘GG TOEIC’ 앱(이하 ‘본 앱’)을 이용하기 전에 다음 내용을 확인해 주세요.\n\n본 앱을 이용하면 본 면책사항을 확인하고 이해한 것으로 간주됩니다.",
    privacyLink = "개인정보처리방침 열기",
    acknowledgement = "위 내용을 확인했습니다",
    start = "확인하고 이용 시작",
    close = "닫기",
    sections = listOf(
        section("1. 본 앱의 목적", "본 앱은 TOEIC 어휘 학습, 발음 연습 및 영어 회화 연습을 돕습니다. TOEIC 공식 교재·시험·채점 서비스, 어학원, 교육기관 또는 시험기관이 아니며, 관련 기관이나 제3자로부터 공식 승인·추천·보증·제휴를 받은 것이 아닙니다. ‘TOEIC’는 관련 권리자의 상표입니다."),
        section("2. 학습 결과", "본 앱은 TOEIC 점수 향상, 목표 점수 달성, 시험 합격, 영어·어휘·발음·회화 능력 향상, 진학·취업 또는 자격 취득을 보장하지 않습니다. 결과는 학습 시간과 방법, 언어 수준, 시험 내용 및 환경에 따라 달라집니다. 필요에 따라 공식 자료, 교사, 전문가 및 신뢰할 수 있는 자료를 함께 이용하세요."),
        section("3. 학습 콘텐츠", "단어, 의미, 예문, 동의어, 연어, 발음, 난이도, 점수 구분 및 기타 학습 정보의 정확성·완전성·최신성·목적 적합성을 보장하지 않습니다. 번역과 분류에는 오류, 부자연스러운 표현, 지역 차이 또는 견해 차이가 있을 수 있습니다. 점수 구분과 난이도는 참고용이며 공식 TOEIC 평가나 채점 기준이 아닙니다. 어휘 데이터는 AI의 도움으로 만들고 운영자가 검토·편집했지만 오류가 남을 수 있습니다."),
        section("4. 번역 및 다국어 표시", "본 앱은 한국어, 일본어, 영어 및 기타 언어로 표시될 수 있습니다. 번역은 학습 참고용이며 모든 언어에서 정확하고 자연스럽거나 동일하다고 보장하지 않습니다. 표현, 설명, 예문, 어순 또는 표시 내용이 언어별로 다를 수 있습니다. 본 면책사항의 일본어판과 다른 언어판이 다르면 일본어판을 우선합니다."),
        section("5. AI 서비스", "본 앱은 ChatGPT 또는 Gemini 등 제3자 AI 앱을 실행하여 회화, 발음 및 학습 연습을 할 수 있도록 합니다. 본 앱은 해당 앱을 실행할 뿐 입력 내용을 자동으로 전송하지 않습니다. 외부 AI에 입력하거나 전송한 정보에는 해당 서비스의 약관과 개인정보처리방침이 적용됩니다. AI의 답변, 번역, 발음 지도, 문법 설명 및 대화에는 오류가 있거나 부정확하거나 부적절하거나 오래된 정보가 포함될 수 있으므로, 중요한 판단을 AI 결과만으로 하지 마세요. 의료·법률·금융 등 전문적인 조언을 대신하지도 않습니다."),
        section("6. 개인정보 및 입력 내용", "본 앱이나 외부 AI에 비밀번호, 인증코드, 카드·은행 정보, 여권·신분증 번호, 주소, 전화번호, 위치, 건강·직장 정보, 타인의 개인정보 또는 공개하고 싶지 않은 정보를 입력하지 마세요. 자세한 처리 내용은 아래 개인정보처리방침을 확인하세요. 외부 서비스에 보낸 정보는 각 제공자의 정책에 따라 처리됩니다."),
        section("7. 백업 및 학습 데이터", "본 앱은 학습 데이터를 백업 파일로 저장하거나 복원할 수 있습니다. 파일에는 학습 상태, 기록, 즐겨찾기, 연속 학습일, 설정 등이 포함될 수 있습니다. 백업은 자동이 아니며, 파일은 암호화되지 않습니다. 분실, 손상, 오용, 유출 또는 복원 실패에 대해 운영자는 책임지지 않습니다. 복원하면 현재 데이터가 바뀔 수 있으므로 먼저 별도 백업을 하세요. 기기 고장, 앱 삭제, 초기화 또는 데이터 삭제로 백업하지 않은 정보가 사라질 수 있습니다."),
        section("8. Android TTS 및 음성 기능", "발음 및 읽기 기능은 Android 기기, 운영체제, TTS 엔진, 음성 데이터 및 설정에 따라 달라집니다. 발음, 억양, 자연스러움, 속도, 지원 언어 및 음질은 기기나 TTS 엔진에 따라 다를 수 있으며, 모든 환경에서 음성 재생을 보장하지 않습니다. 음성이 나오지 않으면 볼륨, TTS 설정, 음성 데이터, 네트워크 및 기기 호환성을 확인하세요. 본 앱의 음성은 학습 참고용이며 공식 TOEIC 발음 평가나 전문가의 지도를 제공하거나 보장하지 않습니다. 외부 앱에서 마이크, 음성 데이터 및 녹음이 처리되는 방식은 해당 앱의 정책에 따릅니다."),
        section("9. 알림 및 기기 환경", "사용자 권한, Android 설정, 기기 상태, 배터리 최적화, 네트워크 등으로 알림이 표시되거나 전달되지 않을 수 있습니다. 알림 누락, 시간 차이 또는 내용 변경에 대해 운영자는 책임지지 않습니다. 모든 기기, OS, 화면, 네트워크 또는 외부 서비스에서 정상 작동을 보장하지 않습니다."),
        section("10. 미성년자의 이용", "미성년자는 보호자 또는 법정대리인의 동의를 받아 이용해야 합니다. 이름, 주소, 학교명, 전화번호, 사진, 위치 또는 기타 개인정보를 본 앱이나 외부 AI에 입력·전송하지 마세요. 보호자는 이용 상황을 적절히 확인해야 합니다. 별도 대상 연령을 정하면 앱 또는 스토어에 표시합니다."),
        section("11. Google Play 및 프리미엄 기능", "본 앱에는 TOEIC 고급 어휘 등 유료 기능이 포함될 수 있습니다. 구매 시 Google Play에 표시된 가격이 적용되며 가격, 통화, 세금, 판매 조건 또는 내용이 바뀔 수 있습니다. 구매 확인 및 복원은 Google Play 계정, 결제 상태, 기기 및 네트워크의 영향을 받을 수 있습니다. 구매 처리 중, 결제 오류, 반영 지연 또는 계정·기기 변경으로 즉시 이용하지 못할 수 있습니다. 구매 복원 시 구매에 사용한 동일한 Google Play 계정을 사용하세요. 환불, 취소 및 구매 절차는 Google Play의 약관과 절차 및 관련 법령에 따릅니다."),
        section("12. 앱 변경, 중지 및 종료", "운영자는 앱의 내용, 기능, 디자인, 지원 기기·OS, 외부 AI, 가격, 정보 또는 본 면책사항을 변경할 수 있고 서비스 전부 또는 일부를 중지·종료할 수 있습니다. 이로 인해 기능, 학습 내용, 외부 연결 또는 저장 데이터가 이용 불가능해질 수 있습니다. 중요한 변경은 가능한 범위에서 안내하며 필요한 데이터는 직접 정기적으로 백업하세요."),
        section("13. 지식재산권 및 상표", "앱의 프로그램, 디자인, 글, 이미지, 음성, 데이터베이스 및 콘텐츠의 권리는 운영자 또는 권리자에게 있습니다. 법률상 허용되는 경우를 제외하고 허가 없이 복제, 판매, 배포, 수정 또는 재사용할 수 없습니다. TOEIC, ChatGPT, Gemini, Android, Google Play 등은 각 권리자의 상표입니다. 본 앱은 해당 제3자와 제휴·승인·보증 관계가 없습니다."),
        section("14. 이용자의 책임", "이용자는 자신의 책임으로 본 앱을 이용합니다. 앱 또는 외부 서비스 사용으로 제3자에게 손해를 입힌 경우 이용자가 책임과 비용으로 해결해야 합니다. 불법, 괴롭힘, 무단 접근, 저작권 침해 또는 부정한 목적으로 사용하지 마세요."),
        section("15. 손해배상", "법률이 허용하는 범위에서 운영자는 앱 이용 또는 이용 불능으로 인한 간접·특별 손해, 일실이익, 데이터 손실 또는 기타 손해에 책임지지 않습니다. 다만 운영자의 고의 또는 중대한 과실로 인한 손해, 사망 또는 신체 손해, 법률상 면책 또는 제한이 허용되지 않는 손해에는 적용되지 않습니다."),
        section("16. 문의", "본 면책사항, 앱 내용 또는 이용에 관한 문의는 다음으로 연락해 주세요.\n\n운영자: GachiGuild\n이메일: gachiguild@gmail.com")
    )
)

private fun vietnameseDisclaimer() = translatedDisclaimer(
    title = "Thông tin quan trọng và miễn trừ trách nhiệm trước khi sử dụng",
    metadata = "Ngày ban hành: 28/09/2026\nCập nhật lần cuối: 28/09/2026",
    operator = "Đơn vị vận hành: GachiGuild",
    contact = "Liên hệ: gachiguild@gmail.com",
    introduction = "Vui lòng đọc nội dung sau trước khi sử dụng ứng dụng “GG TOEIC” (gọi là “Ứng dụng”).\n\nViệc sử dụng Ứng dụng được xem là bạn đã đọc và hiểu tuyên bố miễn trừ này.",
    privacyLink = "Mở Chính sách quyền riêng tư",
    acknowledgement = "Tôi đã xác nhận nội dung trên",
    start = "Xác nhận và bắt đầu sử dụng",
    close = "Đóng",
    sections = listOf(
        section("1. Mục đích của Ứng dụng", "Ứng dụng hỗ trợ học từ vựng TOEIC, luyện phát âm và luyện hội thoại tiếng Anh. Ứng dụng không phải là tài liệu, kỳ thi hay dịch vụ chấm điểm chính thức của TOEIC, cũng không phải là trường ngoại ngữ, cơ sở giáo dục hoặc tổ chức thi. Ứng dụng không được các tổ chức TOEIC, cơ quan tổ chức thi, trường đại học, cơ sở giáo dục hoặc bên thứ ba nào khác chính thức phê duyệt, khuyến nghị, bảo đảm hoặc liên kết. “TOEIC” là nhãn hiệu của các chủ sở hữu liên quan."),
        section("2. Kết quả học tập", "Ứng dụng không bảo đảm tăng điểm TOEIC, đạt mức điểm mục tiêu, đỗ kỳ thi, cải thiện tiếng Anh, từ vựng, phát âm hoặc hội thoại, cũng như việc nhập học, có việc làm hay đạt chứng chỉ. Kết quả phụ thuộc vào thời gian, phương pháp học, trình độ, nội dung và môi trường thi. Hãy dùng thêm tài liệu chính thức, giáo viên, chuyên gia và nguồn đáng tin cậy khi cần."),
        section("3. Nội dung học tập", "Không bảo đảm tính chính xác, đầy đủ, cập nhật hoặc phù hợp với mục đích cụ thể của từ, nghĩa, ví dụ, từ đồng nghĩa, cụm từ, phát âm, độ khó, mức điểm và thông tin khác. Bản dịch và phân loại có thể có lỗi, cách diễn đạt không tự nhiên, khác biệt vùng miền hoặc quan điểm. Mức điểm và độ khó chỉ là tham khảo, không phải đánh giá hay tiêu chí chấm điểm chính thức của TOEIC. Dữ liệu từ vựng được tạo với sự hỗ trợ của AI, sau đó được đơn vị vận hành kiểm tra và chỉnh sửa, nhưng vẫn có thể còn sai sót hoặc phân loại không chính xác."),
        section("4. Bản dịch và đa ngôn ngữ", "Ứng dụng có thể hiển thị bằng tiếng Việt, Nhật, Anh và ngôn ngữ khác. Bản dịch chỉ để tham khảo học tập, không bảo đảm chính xác, tự nhiên hoặc giống nhau hoàn toàn ở mọi ngôn ngữ. Cách diễn đạt, mức độ chi tiết, ví dụ, thứ tự từ và nội dung có thể khác nhau. Nếu bản tiếng Nhật khác bản ngôn ngữ khác, bản tiếng Nhật được ưu tiên."),
        section("5. Dịch vụ AI", "Ứng dụng có thể mở ChatGPT, Gemini hoặc ứng dụng AI bên thứ ba khác để luyện hội thoại, phát âm và học tập. Ứng dụng chỉ mở dịch vụ và không tự động gửi nội dung bạn nhập. Thông tin nhập hoặc gửi trong dịch vụ bên ngoài chịu điều khoản và chính sách quyền riêng tư của nhà cung cấp. Câu trả lời, bản dịch, hướng dẫn phát âm, giải thích ngữ pháp và nội dung hội thoại do AI tạo ra có thể sai, không chính xác, không phù hợp hoặc lỗi thời; chúng không thay thế việc chấm điểm chính thức của TOEIC, hướng dẫn của giáo viên hoặc chuyên gia, hay tư vấn chuyên môn về y tế, pháp luật hoặc tài chính. Không dùng kết quả AI làm cơ sở duy nhất cho quyết định quan trọng."),
        section("6. Thông tin cá nhân và dữ liệu nhập", "Không nhập mật khẩu, mã xác thực, thông tin thẻ hoặc ngân hàng, số hộ chiếu hoặc giấy tờ, địa chỉ, điện thoại, vị trí, sức khỏe, nơi làm việc, thông tin cá nhân của người khác hoặc thông tin bí mật vào Ứng dụng hay AI bên ngoài. Vui lòng xem Chính sách quyền riêng tư bên dưới. Thông tin gửi tới ChatGPT, Gemini hoặc dịch vụ khác được xử lý theo chính sách của nhà cung cấp."),
        section("7. Sao lưu và dữ liệu học tập", "Ứng dụng có thể cho phép lưu hoặc khôi phục dữ liệu bằng tệp sao lưu, gồm trạng thái học từ, lịch sử, yêu thích, chuỗi ngày học, cài đặt và dữ liệu khác. Sao lưu không tự động. Tệp không được mã hóa, hãy tự bảo quản an toàn. Đơn vị vận hành không chịu trách nhiệm về mất, hỏng, lạm dụng, rò rỉ hoặc khôi phục thất bại. Khôi phục có thể thay thế dữ liệu hiện tại; hãy sao lưu riêng trước khi khôi phục. Dữ liệu chưa sao lưu có thể mất do hỏng thiết bị, xóa ứng dụng, đặt lại hoặc xóa dữ liệu ứng dụng."),
        section("8. TTS và âm thanh Android", "Phát âm và đọc phụ thuộc vào thiết bị Android, OS, công cụ TTS, dữ liệu giọng nói và cài đặt. Phát âm, giọng, tốc độ, ngôn ngữ và chất lượng có thể khác nhau; không bảo đảm âm thanh chạy trên mọi thiết bị hoặc ngôn ngữ. Hãy kiểm tra âm lượng, TTS, dữ liệu giọng, mạng và khả năng tương thích. Âm thanh chỉ là tham khảo học tập, không phải đánh giá phát âm chính thức của TOEIC. Âm thanh và ghi âm trong ứng dụng ngoài tuân theo chính sách của ứng dụng đó."),
        section("9. Thông báo và thiết bị", "Thông báo có thể không hiển thị hoặc không đến do quyền, cài đặt Android, thiết bị, tối ưu pin, mạng hoặc nguyên nhân khác. Không chịu trách nhiệm về thông báo bị thiếu, sai giờ hoặc đổi nội dung. Không bảo đảm hoạt động trên mọi thiết bị, OS, màn hình, mạng hay dịch vụ ngoài."),
        section("10. Người chưa thành niên", "Người chưa thành niên cần sự đồng ý của cha mẹ hoặc người đại diện hợp pháp. Không gửi tên, địa chỉ, trường học, điện thoại, ảnh, vị trí hoặc thông tin cá nhân khác vào Ứng dụng hay AI bên ngoài. Người giám hộ nên kiểm tra việc sử dụng phù hợp. Nếu có độ tuổi riêng, độ tuổi đó sẽ được hiển thị trong Ứng dụng hoặc cửa hàng."),
        section("11. Google Play và tính năng cao cấp", "Ứng dụng có thể có tính năng trả phí như bộ từ vựng TOEIC nâng cao. Giá được hiển thị trên Google Play tại thời điểm mua sẽ được áp dụng; giá, tiền tệ, thuế, điều kiện bán hoặc nội dung có thể thay đổi. Việc xác nhận và khôi phục giao dịch mua phụ thuộc vào tài khoản, trạng thái thanh toán, thiết bị và mạng. Giao dịch đang chờ xử lý, lỗi thanh toán, chậm cập nhật hoặc thay đổi tài khoản/thiết bị có thể làm chậm việc sử dụng. Khi khôi phục, hãy dùng cùng tài khoản Google Play đã sử dụng để mua. Việc hoàn tiền và hủy giao dịch tuân theo Google Play và pháp luật áp dụng."),
        section("12. Thay đổi, tạm dừng và kết thúc", "Đơn vị vận hành có thể thay đổi nội dung, chức năng, thiết kế, thiết bị hoặc hệ điều hành được hỗ trợ, AI bên ngoài, giá, thông tin hoặc tuyên bố miễn trừ trách nhiệm này, và có thể tạm dừng hoặc kết thúc một phần hay toàn bộ dịch vụ. Chức năng, nội dung học, liên kết ngoài hoặc dữ liệu lưu có thể không còn dùng được. Thay đổi quan trọng sẽ được thông báo trong phạm vi có thể. Hãy tự sao lưu định kỳ dữ liệu cần giữ."),
        section("13. Sở hữu trí tuệ và nhãn hiệu", "Quyền đối với chương trình, thiết kế, chữ, hình ảnh, âm thanh, cơ sở dữ liệu và nội dung khác thuộc về đơn vị vận hành hoặc chủ sở hữu hợp pháp. Trừ khi luật cho phép, không được sao chép, bán, phân phối, sửa đổi hoặc tái sử dụng nếu chưa được phép. TOEIC, ChatGPT, Gemini, Android, Google Play và tên khác là nhãn hiệu của chủ sở hữu tương ứng. Ứng dụng không có quan hệ hợp tác, phê duyệt hoặc bảo đảm với các bên đó."),
        section("14. Trách nhiệm người dùng", "Người dùng tự chịu trách nhiệm khi sử dụng Ứng dụng. Nếu gây thiệt hại cho bên thứ ba qua Ứng dụng hoặc dịch vụ ngoài, người dùng tự giải quyết bằng chi phí và trách nhiệm của mình. Không dùng cho hành vi trái luật, quấy rối, truy cập trái phép, vi phạm bản quyền hoặc mục đích không phù hợp."),
        section("15. Thiệt hại", "Trong phạm vi luật cho phép, đơn vị vận hành không chịu trách nhiệm về thiệt hại gián tiếp, đặc biệt, mất lợi nhuận, mất dữ liệu hoặc thiệt hại khác do sử dụng hoặc không thể sử dụng Ứng dụng. Quy định này không áp dụng cho hành vi cố ý hoặc sơ suất nghiêm trọng của đơn vị vận hành, thiệt hại về tính mạng hoặc thân thể, hoặc thiệt hại mà pháp luật không cho phép miễn hay giới hạn trách nhiệm."),
        section("16. Liên hệ", "Câu hỏi về tuyên bố này, nội dung hoặc việc sử dụng Ứng dụng xin gửi tới:\n\nĐơn vị vận hành: GachiGuild\nEmail: gachiguild@gmail.com")
    )
)

private fun indonesianDisclaimer() = translatedDisclaimer(
    title = "Informasi Penting dan Penafian Sebelum Menggunakan Aplikasi",
    metadata = "Tanggal ditetapkan: 28 September 2026\nTerakhir diperbarui: 28 September 2026",
    operator = "Pengelola: GachiGuild",
    contact = "Kontak: gachiguild@gmail.com",
    introduction = "Baca informasi berikut sebelum menggunakan aplikasi “GG TOEIC” (selanjutnya disebut “Aplikasi”).\n\nDengan menggunakan Aplikasi, Anda dianggap telah membaca dan memahami penafian ini.",
    privacyLink = "Buka Kebijakan Privasi",
    acknowledgement = "Saya telah mengonfirmasi isi di atas",
    start = "Konfirmasi dan mulai menggunakan",
    close = "Tutup",
    sections = listOf(
        section("1. Tujuan Aplikasi", "Aplikasi membantu mempelajari kosakata TOEIC serta berlatih pelafalan dan percakapan bahasa Inggris. Aplikasi bukan materi resmi, ujian resmi, atau layanan penilaian resmi TOEIC, dan bukan sekolah bahasa, lembaga pendidikan, atau penyelenggara ujian. Aplikasi tidak secara resmi disetujui, direkomendasikan, dijamin, atau berafiliasi dengan organisasi TOEIC maupun pihak ketiga lainnya. “TOEIC” adalah merek dagang pemegang hak terkait."),
        section("2. Hasil Belajar", "Penggunaan Aplikasi tidak menjamin peningkatan skor TOEIC, pencapaian skor target, kelulusan ujian, peningkatan kemampuan bahasa Inggris, kosakata, pelafalan atau percakapan, penerimaan di institusi pendidikan, pekerjaan, atau sertifikasi. Hasil berbeda menurut waktu dan metode belajar, tingkat bahasa, isi ujian, dan lingkungan ujian. Gunakan juga materi resmi, guru, ahli, sekolah bahasa, dan sumber tepercaya bila perlu."),
        section("3. Konten Pembelajaran", "Keakuratan, kelengkapan, kemutakhiran, atau kesesuaian untuk tujuan tertentu dari kata, arti, contoh, sinonim, kolokasi, pelafalan, tingkat kesulitan, rentang skor, dan informasi lain tidak dijamin. Terjemahan dan klasifikasi dapat memiliki kesalahan, ungkapan tidak alami, perbedaan daerah, atau perbedaan pendapat. Rentang skor dan tingkat kesulitan hanya referensi belajar, bukan penilaian atau kriteria resmi TOEIC. Data kosakata dibuat dengan bantuan AI lalu diperiksa dan diedit oleh pengelola, tetapi kesalahan dapat tetap ada."),
        section("4. Terjemahan dan Multibahasa", "Aplikasi dapat ditampilkan dalam bahasa Indonesia, Jepang, Inggris, dan bahasa lain. Terjemahan hanya merupakan referensi belajar dan tidak dijamin akurat, alami, atau sepenuhnya sama dalam semua bahasa. Ungkapan, tingkat perincian, contoh, urutan kata, dan isi tampilan dapat berbeda. Jika versi bahasa Jepang dan versi bahasa lain berbeda, versi bahasa Jepang yang berlaku."),
        section("5. Layanan AI", "Aplikasi dapat membuka ChatGPT, Gemini, atau aplikasi AI pihak ketiga untuk latihan percakapan, pelafalan, dan belajar. Aplikasi hanya membuka layanan tersebut dan tidak mengirim input secara otomatis. Informasi yang dimasukkan ke layanan eksternal tunduk pada syarat dan kebijakan privasinya. Hasil AI dapat salah, tidak akurat, tidak sesuai, atau usang. Jangan gunakan hasil AI sebagai satu-satunya dasar keputusan penting."),
        section("6. Informasi Pribadi dan Input", "Jangan masukkan kata sandi, kode autentikasi, informasi kartu atau rekening bank, nomor paspor atau identitas, alamat, nomor telepon, informasi lokasi, kesehatan, pekerjaan, data pribadi orang lain, atau informasi rahasia ke Aplikasi atau AI eksternal. Lihat Kebijakan Privasi di bawah untuk penanganan data pribadi dan data penggunaan. Informasi yang dikirim ke ChatGPT, Gemini, atau layanan lain diproses sesuai kebijakan penyedianya."),
        section("7. Cadangan dan Data Belajar", "Aplikasi dapat menyimpan atau memulihkan data belajar melalui berkas cadangan yang mungkin berisi status belajar, riwayat, favorit, hari belajar beruntun, pengaturan, dan data lain. Cadangan tidak otomatis. Berkas tidak dienkripsi, jadi simpan dengan aman. Pengelola tidak bertanggung jawab atas kehilangan, kerusakan, penyalahgunaan, kebocoran, atau kegagalan pemulihan. Pemulihan dapat mengganti data saat ini; buat cadangan lain sebelum memulihkan. Data yang belum dicadangkan dapat hilang karena perangkat rusak, aplikasi dihapus, perangkat direset, atau data aplikasi dihapus."),
        section("8. TTS dan Audio Android", "Fungsi pelafalan dan pembacaan bergantung pada perangkat Android, OS, mesin TTS, data suara, dan pengaturan. Pelafalan, aksen, kecepatan, bahasa, dan kualitas dapat berbeda, serta tidak dijamin berfungsi di semua perangkat atau bahasa. Jika audio tidak berjalan, periksa volume, TTS, data suara, jaringan, dan kompatibilitas. Audio hanya referensi belajar, bukan penilaian resmi TOEIC atau bimbingan ahli. Suara dan rekaman di aplikasi eksternal mengikuti kebijakan aplikasi tersebut."),
        section("9. Notifikasi dan Perangkat", "Notifikasi dapat tidak tampil atau sampai karena izin, pengaturan Android, kondisi perangkat, pengoptimalan baterai, jaringan, atau alasan lain. Pengelola tidak bertanggung jawab atas notifikasi yang hilang, berbeda waktu, atau berubah isinya. Tidak dijamin Aplikasi berjalan normal di semua perangkat, OS, layar, jaringan, atau layanan eksternal."),
        section("10. Pengguna di Bawah Umur", "Pengguna di bawah umur harus memperoleh persetujuan orang tua atau wali sah. Jangan masukkan nama, alamat, sekolah, telepon, foto, lokasi, atau data pribadi lain ke Aplikasi atau AI eksternal. Orang tua atau wali sebaiknya memantau penggunaan. Jika ditetapkan usia tertentu, usia itu akan ditampilkan di Aplikasi atau toko distribusi."),
        section("11. Google Play dan Fitur Premium", "Aplikasi dapat memiliki fitur berbayar seperti kosakata TOEIC tingkat lanjut. Harga yang ditampilkan di Google Play pada saat pembelian berlaku; harga, mata uang, pajak, syarat penjualan, atau isi dapat berubah. Verifikasi dan pemulihan pembelian dapat dipengaruhi oleh akun Google Play, status pembayaran, perangkat, dan jaringan. Pembelian tertunda, kegagalan pembayaran, keterlambatan, atau perubahan akun/perangkat dapat menunda akses. Gunakan akun Google Play yang sama dengan akun yang digunakan saat membeli untuk memulihkan pembelian. Pengembalian dana, pembatalan, dan prosedur pembelian mengikuti ketentuan dan prosedur Google Play serta hukum yang berlaku."),
        section("12. Perubahan, Penghentian, dan Berakhirnya Aplikasi", "Pengelola dapat mengubah isi, fungsi, desain, perangkat/OS yang didukung, AI eksternal, harga, informasi, atau penafian ini dan dapat menghentikan sebagian atau seluruh layanan. Fungsi, konten belajar, koneksi eksternal, atau data tersimpan dapat menjadi tidak tersedia. Perubahan penting akan diberitahukan sejauh mungkin. Cadangkan sendiri data yang perlu disimpan."),
        section("13. Kekayaan Intelektual dan Merek", "Hak atas program, desain, teks, gambar, audio, basis data, dan konten lain dimiliki pengelola atau pemegang hak yang sah. Kecuali diizinkan hukum, dilarang menyalin, menjual, mendistribusikan, mengubah, atau menggunakan kembali tanpa izin. TOEIC, ChatGPT, Gemini, Android, Google Play, dan nama lain adalah merek pemiliknya. Aplikasi tidak memiliki hubungan kerja sama, persetujuan, atau jaminan dengan pihak tersebut."),
        section("14. Tanggung Jawab Pengguna", "Pengguna memakai Aplikasi atas tanggung jawab sendiri. Jika penggunaan Aplikasi atau layanan eksternal merugikan pihak ketiga, pengguna menyelesaikannya dengan tanggung jawab dan biaya sendiri. Jangan gunakan untuk tindakan ilegal, gangguan, akses tanpa izin, pelanggaran hak cipta, atau tujuan tidak patut."),
        section("15. Kerugian", "Sejauh diizinkan hukum, pengelola tidak bertanggung jawab atas kerugian tidak langsung atau khusus, kehilangan keuntungan, kehilangan data, atau kerugian lain akibat penggunaan atau ketidakmampuan menggunakan Aplikasi. Hal ini tidak berlaku untuk tindakan sengaja atau kelalaian berat pengelola, kematian atau cedera fisik, atau kerugian yang menurut hukum tidak boleh dikecualikan atau dibatasi."),
        section("16. Kontak", "Untuk pertanyaan tentang penafian ini, isi, atau penggunaan Aplikasi, hubungi:\n\nPengelola: GachiGuild\nEmail: gachiguild@gmail.com")
    )
)

private fun spanishDisclaimer() = translatedDisclaimer(
    title = "Información importante y exención de responsabilidad antes de utilizar la aplicación",
    metadata = "Fecha de creación: 29 de septiembre de 2026\nÚltima actualización: 29 de septiembre de 2026",
    operator = "Operador: GachiGuild",
    contact = "Contacto: gachiguild@gmail.com",
    introduction = "Lee la siguiente información antes de utilizar la aplicación “GG TOEIC” (la “Aplicación”).\n\nEl uso de la Aplicación implica que has leído y comprendido esta exención.",
    privacyLink = "Abrir la Política de privacidad",
    acknowledgement = "He confirmado el contenido anterior",
    start = "Confirmar y comenzar a usar",
    close = "Cerrar",
    sections = listOf(
        section("1. Finalidad de la Aplicación", "La Aplicación ayuda a estudiar vocabulario del TOEIC y a practicar la pronunciación y la conversación en inglés. No constituye material oficial, examen oficial ni servicio oficial de calificación del TOEIC, ni es una academia de idiomas, institución educativa u organismo examinador. No está aprobada, recomendada, garantizada ni afiliada oficialmente por organizaciones del TOEIC u otros terceros. “TOEIC” es una marca de sus respectivos titulares."),
        section("2. Resultados del aprendizaje", "El uso de la Aplicación no garantiza mejorar la puntuación, alcanzar la banda objetivo, aprobar el examen, mejorar el inglés, el vocabulario, la pronunciación o la conversación, ni obtener admisión, empleo o certificación. Los resultados dependen del tiempo y método de estudio, nivel, contenido y entorno del examen. Usa también materiales oficiales, profesores, expertos y fuentes fiables cuando sea necesario."),
        section("3. Contenido educativo", "No se garantiza la exactitud, integridad, actualidad o adecuación de palabras, significados, ejemplos, sinónimos, colocaciones, pronunciación, dificultad, rangos de puntuación u otra información. Las traducciones y clasificaciones pueden contener errores, expresiones poco naturales, diferencias regionales o de criterio. Los rangos de puntuación y los niveles son solo referencias de estudio, no criterios oficiales del TOEIC. Los datos se crean con ayuda de IA y son revisados por el operador, pero pueden quedar errores."),
        section("4. Traducciones y varios idiomas", "La Aplicación puede mostrarse en español, japonés, inglés y otros idiomas. Las traducciones son referencias de estudio y no se garantiza que sean exactas, naturales o idénticas. Pueden variar expresiones, detalle, ejemplos, orden de palabras y contenido. Si la versión japonesa y otra versión difieren, prevalece la japonesa."),
        section("5. Servicios de IA", "La Aplicación puede abrir ChatGPT, Gemini u otras aplicaciones de IA para practicar conversación, pronunciación y estudio. Solo abre esos servicios y no envía automáticamente la información que introduzcas. La información introducida o enviada en servicios externos se rige por sus condiciones y política de privacidad. Las respuestas, traducciones, indicaciones de pronunciación, explicaciones gramaticales y conversaciones generadas por la IA pueden ser erróneas, inexactas, inadecuadas u obsoletas; no sustituyen la calificación oficial del TOEIC, la orientación de profesores o expertos ni el asesoramiento médico, jurídico o financiero. No bases decisiones importantes únicamente en ellas."),
        section("6. Información personal y datos introducidos", "No introduzcas contraseñas, códigos de autenticación, datos de tarjetas o cuentas bancarias, números de pasaporte o identidad, dirección, teléfono, ubicación, información de salud o laboral, datos personales de terceros ni información confidencial en la Aplicación o en una IA externa. Consulta la Política de privacidad para conocer el tratamiento de los datos personales y de uso. La información enviada a ChatGPT, Gemini u otros servicios se procesa según la política de su proveedor."),
        section("7. Copias de seguridad y datos de estudio", "La Aplicación puede guardar o restaurar datos mediante archivos de copia de seguridad que pueden incluir estado, historial, favoritos, días consecutivos, ajustes y otros datos. Las copias no son automáticas. Los archivos no están cifrados; guárdalos de forma segura. El operador no responde por pérdida, daño, uso indebido, filtración o fallo de restauración. Restaurar puede sustituir datos actuales; haz otra copia antes. Los datos no respaldados pueden perderse por avería, eliminación, reinicio o borrado de datos."),
        section("8. TTS y audio de Android", "La pronunciación y la lectura dependen del dispositivo Android, el sistema operativo, el motor TTS, los datos de voz y la configuración. La pronunciación, el acento, la velocidad, los idiomas disponibles y la calidad pueden variar, y no se garantiza la reproducción en todos los dispositivos o idiomas. Si no hay audio, comprueba el volumen, la configuración del TTS, los datos de voz, la red y la compatibilidad del dispositivo. El audio de la Aplicación es una referencia de estudio y no constituye una evaluación oficial de la pronunciación en el TOEIC ni una instrucción especializada. El uso del micrófono, los datos de voz y las grabaciones en aplicaciones externas se rige por las políticas de dichas aplicaciones."),
        section("9. Notificaciones y dispositivo", "Las notificaciones pueden no mostrarse o no llegar por los permisos, los ajustes de Android, el estado del dispositivo, la optimización de la batería, la red u otras causas. El operador no será responsable de las notificaciones ausentes, tardías o modificadas. No se garantiza el funcionamiento en todos los dispositivos, sistemas operativos, tamaños de pantalla, redes o servicios externos."),
        section("10. Uso por menores", "Los menores deben obtener el consentimiento de sus padres o representantes legales. No deben introducir ni enviar nombre, dirección, escuela, teléfono, fotos, ubicación u otros datos personales a la Aplicación o a una IA externa. Los responsables deben supervisar adecuadamente el uso. Si se establece una edad, se mostrará en la Aplicación o tienda."),
        section("11. Google Play y funciones Premium", "La Aplicación puede incluir funciones de pago, como vocabulario TOEIC avanzado. Se aplica el precio mostrado en Google Play en el momento de la compra; el precio, la moneda, los impuestos, las condiciones de venta o el contenido pueden cambiar. La verificación y restauración de compras pueden depender de la cuenta de Google Play, el estado del pago, el dispositivo y la red. Las compras pendientes, los errores de pago, los retrasos o los cambios de cuenta o dispositivo pueden impedir el acceso inmediato. Para restaurar una compra, usa la misma cuenta de Google Play utilizada para adquirirla. Los reembolsos, las cancelaciones y los procedimientos de compra se rigen por las condiciones y procedimientos de Google Play y por la ley aplicable."),
        section("12. Cambios, suspensión y finalización", "El operador puede cambiar el contenido, las funciones, el diseño, los dispositivos o sistemas operativos compatibles, los servicios de IA externos, los precios, la información o esta exención de responsabilidad, y suspender o finalizar parte o todo el servicio. Esto puede dejar sin acceso funciones, contenido, conexiones externas o datos guardados. Los cambios importantes se anunciarán cuando sea posible. Haz copias periódicas de los datos que necesites conservar."),
        section("13. Propiedad intelectual y marcas", "Los derechos sobre los programas, el diseño, los textos, las imágenes, el audio, las bases de datos y otros contenidos pertenecen al operador o a sus titulares legítimos. Salvo autorización legal, no se permite copiar, publicar, vender, distribuir, modificar o reutilizar el contenido sin permiso. TOEIC, ChatGPT, Gemini, Android y Google Play son marcas de sus titulares. La Aplicación no está afiliada, aprobada ni respaldada por dichos terceros."),
        section("14. Responsabilidad del usuario", "El usuario utiliza la Aplicación bajo su propia responsabilidad. Si causa daños a terceros mediante la Aplicación o servicios externos, deberá resolverlo por su cuenta y coste. No uses la Aplicación para actos ilegales, acoso, acceso no autorizado, infracción de derechos de autor u otros fines indebidos."),
        section("15. Daños y perjuicios", "En la medida permitida por la ley, el operador no responde por daños indirectos o especiales, lucro cesante, pérdida de datos u otros daños derivados del uso o imposibilidad de uso. Esto no se aplica al dolo o negligencia grave, daños a la vida o integridad física, ni a daños que la ley no permita excluir o limitar."),
        section("16. Contacto", "Para consultas sobre esta exención, el contenido o el uso de la Aplicación, contacta con:\n\nOperador: GachiGuild\nCorreo: gachiguild@gmail.com")
    )
)

private fun hindiDisclaimer() = translatedDisclaimer(
    title = "उपयोग से पहले महत्वपूर्ण जानकारी और अस्वीकरण",
    metadata = "निर्धारण तिथि: 29 सितंबर 2026\nअंतिम अपडेट: 29 सितंबर 2026",
    operator = "संचालक: GachiGuild",
    contact = "संपर्क: gachiguild@gmail.com",
    introduction = "“GG TOEIC” ऐप (आगे “ऐप”) का उपयोग करने से पहले निम्न जानकारी पढ़ें।\n\nऐप का उपयोग करने पर माना जाएगा कि आपने इस अस्वीकरण को पढ़ और समझ लिया है।",
    privacyLink = "गोपनीयता नीति खोलें",
    acknowledgement = "मैंने ऊपर दी गई सामग्री की पुष्टि कर दी है",
    start = "पुष्टि करें और उपयोग शुरू करें",
    close = "बंद करें",
    sections = listOf(
        section("1. ऐप का उद्देश्य", "यह ऐप TOEIC शब्दावली सीखने, उच्चारण और अंग्रेज़ी बातचीत का अभ्यास करने में सहायता करता है। यह TOEIC की आधिकारिक सामग्री, परीक्षा या स्कोरिंग सेवा, भाषा विद्यालय, शैक्षणिक संस्था या परीक्षा संस्था नहीं है और TOEIC से संबंधित किसी संस्था या अन्य तृतीय पक्ष से आधिकारिक रूप से अनुमोदित, अनुशंसित, गारंटीकृत या संबद्ध नहीं है। “TOEIC” संबंधित अधिकारधारकों का ट्रेडमार्क है।"),
        section("2. सीखने के परिणाम", "ऐप TOEIC स्कोर में सुधार, लक्षित स्कोर प्राप्त करने, परीक्षा में सफलता, अंग्रेज़ी, शब्दावली, उच्चारण या बातचीत में सुधार, प्रवेश, नौकरी या प्रमाणपत्र की गारंटी नहीं देता। परिणाम अध्ययन के समय और तरीके, भाषा स्तर, परीक्षा सामग्री और वातावरण पर निर्भर हैं। आवश्यकता होने पर आधिकारिक सामग्री, शिक्षक, विशेषज्ञ और विश्वसनीय स्रोत भी उपयोग करें।"),
        section("3. अध्ययन सामग्री", "शब्द, अर्थ, उदाहरण, समानार्थी शब्द, collocations, उच्चारण, कठिनाई, स्कोर-सीमा और अन्य जानकारी की सटीकता, पूर्णता, नवीनता या विशेष उद्देश्य के लिए उपयुक्तता की गारंटी नहीं है। अनुवाद और वर्गीकरण में त्रुटि, अस्वाभाविक अभिव्यक्ति, क्षेत्रीय अंतर या मतभेद हो सकते हैं। स्कोर-सीमा और कठिनाई केवल अध्ययन संदर्भ हैं, आधिकारिक TOEIC मूल्यांकन या स्कोरिंग मानदंड नहीं। शब्दावली डेटा AI की सहायता से बनाया और संचालक द्वारा जाँचा गया है, फिर भी त्रुटियां हो सकती हैं।"),
        section("4. अनुवाद और बहुभाषी प्रदर्शन", "ऐप हिंदी, जापानी, अंग्रेज़ी और अन्य भाषाओं में दिख सकता है। अनुवाद केवल अध्ययन संदर्भ हैं और सभी भाषाओं में सटीक, स्वाभाविक या समान होने की गारंटी नहीं है। अभिव्यक्ति, विवरण, उदाहरण, शब्द-क्रम या सामग्री भाषा के अनुसार बदल सकती है। इस अस्वीकरण के जापानी और अन्य संस्करणों में अंतर होने पर जापानी संस्करण मान्य होगा।"),
        section("5. AI सेवाएं", "ऐप ChatGPT या Gemini जैसी तृतीय-पक्ष AI ऐप खोल सकता है, ताकि बातचीत, उच्चारण और अध्ययन का अभ्यास किया जा सके। ऐप केवल सेवा खोलता है और इनपुट अपने-आप नहीं भेजता। बाहरी AI में डाली या भेजी गई जानकारी उसकी शर्तों और गोपनीयता नीति के अधीन होगी। AI के उत्तर, अनुवाद, उच्चारण संबंधी मार्गदर्शन, व्याकरण की व्याख्या और बातचीत में त्रुटियां, गलत, अनुपयुक्त या पुरानी जानकारी हो सकती है। ये TOEIC की आधिकारिक स्कोरिंग, शिक्षक या विशेषज्ञ के मार्गदर्शन, अथवा चिकित्सा, कानूनी या वित्तीय सलाह का विकल्प नहीं हैं। महत्वपूर्ण निर्णय केवल AI पर आधारित न करें।"),
        section("6. व्यक्तिगत जानकारी और इनपुट", "ऐप या बाहरी AI में पासवर्ड, प्रमाणीकरण कोड, कार्ड/बैंक जानकारी, पासपोर्ट या पहचान संख्या, पता, फोन, स्थान, स्वास्थ्य, काम, किसी अन्य व्यक्ति की निजी जानकारी या गोपनीय जानकारी न डालें। व्यक्तिगत और उपयोग डेटा के लिए नीचे दी गई गोपनीयता नीति देखें। ChatGPT, Gemini या अन्य सेवा को भेजी जानकारी उनके प्रदाता की नीति के अनुसार संभाली जाएगी।"),
        section("7. बैकअप और अध्ययन डेटा", "ऐप अध्ययन डेटा को बैकअप फ़ाइल में सहेजने या पुनर्स्थापित करने की सुविधा दे सकता है। इसमें सीखने की स्थिति, इतिहास, पसंदीदा, लगातार अध्ययन दिन, सेटिंग और अन्य डेटा हो सकते हैं। बैकअप अपने-आप नहीं बनता और फ़ाइल एन्क्रिप्टेड नहीं है। उसे सुरक्षित रखें। नुकसान, खराबी, दुरुपयोग, लीक या पुनर्स्थापना विफलता के लिए संचालक जिम्मेदार नहीं है। पुनर्स्थापना वर्तमान डेटा बदल सकती है; पहले अलग बैकअप लें। डिवाइस खराब होने, ऐप हटाने, डिवाइस रीसेट करने या ऐप डेटा मिटाने से बिना बैकअप वाला डेटा खो सकता है।"),
        section("8. Android TTS और ऑडियो", "उच्चारण और पढ़ने की सुविधा Android डिवाइस, OS, TTS इंजन, आवाज़ डेटा और सेटिंग पर निर्भर है। उच्चारण, लहजा, गति, भाषाएं और गुणवत्ता अलग हो सकती हैं तथा सभी डिवाइसों पर ऑडियो चलने की गारंटी नहीं है। ध्वनि न चले तो वॉल्यूम, TTS, आवाज़ डेटा, नेटवर्क और संगतता जाँचें। ऑडियो अध्ययन संदर्भ है, आधिकारिक TOEIC मूल्यांकन नहीं। बाहरी ऐप की आवाज़ और रिकॉर्डिंग उसकी नीति के अधीन हैं।"),
        section("9. सूचनाएं और डिवाइस", "उपयोगकर्ता की अनुमति, Android सेटिंग, डिवाइस, बैटरी, नेटवर्क या अन्य कारणों से सूचनाएं न दिख सकती हैं या न पहुंच सकती हैं। सूचना न मिलने, गलत समय पर दिखने या सामग्री बदलने के लिए संचालक जिम्मेदार नहीं है। सभी डिवाइस, OS, स्क्रीन, नेटवर्क या बाहरी सेवाओं पर सामान्य संचालन की गारंटी नहीं है।"),
        section("10. नाबालिगों का उपयोग", "नाबालिगों को माता-पिता या कानूनी अभिभावक की सहमति लेनी चाहिए। नाम, पता, स्कूल, फोन, फोटो, स्थान या अन्य निजी जानकारी ऐप या बाहरी AI में न डालें। अभिभावक को उपयोग की उचित निगरानी करनी चाहिए। यदि कोई आयु सीमा तय की जाएगी, तो उसे ऐप या स्टोर में दिखाया जाएगा।"),
        section("11. Google Play और प्रीमियम सुविधाएं", "ऐप में शब्दावली TOEIC के उन्नत स्तर की जैसी भुगतान वाली सुविधाएं हो सकती हैं। खरीद के समय Google Play पर प्रदर्शित मूल्य लागू होगा और मूल्य, मुद्रा, कर, बिक्री की शर्तें या सामग्री बदल सकती है। खरीद की पुष्टि और पुनर्स्थापना Google Play खाते, भुगतान की स्थिति, डिवाइस और नेटवर्क पर निर्भर हो सकती है। लंबित खरीद, भुगतान संबंधी त्रुटि, देरी या खाते/डिवाइस में बदलाव से सुविधा तुरंत उपलब्ध न हो सकती है। खरीद की पुनर्स्थापना के लिए खरीद में उपयोग किया गया वही Google Play खाता उपयोग करें। रिफंड, रद्दीकरण और खरीद संबंधी प्रक्रियाएं Google Play की शर्तों और प्रक्रियाओं तथा लागू कानून के अनुसार होंगी।"),
        section("12. बदलाव, रोक और समाप्ति", "संचालक ऐप की सामग्री, सुविधाएं, डिजाइन, समर्थित डिवाइस/OS, बाहरी AI, मूल्य, जानकारी या इस अस्वीकरण को बदल सकता है और सेवा रोक या समाप्त कर सकता है। इससे सुविधाएं, सामग्री, बाहरी कनेक्शन या सहेजा डेटा अनुपलब्ध हो सकता है। महत्वपूर्ण बदलाव संभव होने पर बताए जाएंगे। आवश्यक डेटा का नियमित बैकअप स्वयं लें।"),
        section("13. बौद्धिक संपदा और ट्रेडमार्क", "ऐप के कार्यक्रम, डिजाइन, पाठ, चित्र, ऑडियो, डेटाबेस और अन्य सामग्री के अधिकार संचालक या संबंधित अधिकारधारकों के हैं। कानून द्वारा अनुमति के अलावा बिना अनुमति कॉपी, बिक्री, वितरण, बदलाव या पुनः उपयोग निषिद्ध है। TOEIC, ChatGPT, Gemini, Android और Google Play अपने-अपने अधिकारधारकों के ट्रेडमार्क हैं। ऐप उन तृतीय पक्षों से संबद्ध, अनुमोदित या समर्थित नहीं है।"),
        section("14. उपयोगकर्ता की जिम्मेदारी", "उपयोगकर्ता ऐप का उपयोग अपने जोखिम और जिम्मेदारी पर करता है। ऐप या बाहरी सेवा के उपयोग से तीसरे पक्ष को नुकसान होने पर उपयोगकर्ता अपनी जिम्मेदारी और खर्च पर समाधान करेगा। ऐप का उपयोग अवैध कार्य, उत्पीड़न, अनधिकृत पहुंच, कॉपीराइट उल्लंघन या अन्य अनुचित उद्देश्य के लिए न करें।"),
        section("15. नुकसान", "कानून द्वारा अनुमत सीमा तक संचालक ऐप के उपयोग या उपयोग न कर पाने से हुई अप्रत्यक्ष या विशेष क्षति, लाभ की हानि, डेटा की हानि या अन्य नुकसान के लिए जिम्मेदार नहीं होगा। यह संचालक के जानबूझकर किए गए कार्य या गंभीर लापरवाही, मृत्यु या शारीरिक चोट, या कानून द्वारा बाहर न की जा सकने वाली या सीमित न की जा सकने वाली क्षति पर लागू नहीं होगा।"),
        section("16. संपर्क", "इस अस्वीकरण, ऐप की सामग्री या उपयोग के बारे में प्रश्नों के लिए संपर्क करें:\n\nसंचालक: GachiGuild\nईमेल: gachiguild@gmail.com")
    )
)

private fun thaiDisclaimer() = translatedDisclaimer(
    title = "ข้อมูลสำคัญและข้อจำกัดความรับผิดก่อนใช้งาน",
    metadata = "วันที่จัดทำ: 29 กันยายน 2026\nอัปเดตล่าสุด: 29 กันยายน 2026",
    operator = "ผู้ดำเนินการ: GachiGuild",
    contact = "ติดต่อ: gachiguild@gmail.com",
    introduction = "โปรดอ่านข้อมูลต่อไปนี้ก่อนใช้แอป “GG TOEIC” (เรียกว่า “แอป”)\n\nการใช้แอปถือว่าผู้ใช้ได้อ่านและเข้าใจข้อจำกัดความรับผิดนี้แล้ว",
    privacyLink = "เปิดนโยบายความเป็นส่วนตัว",
    acknowledgement = "ฉันได้ยืนยันว่าอ่านข้อมูลข้างต้นแล้ว",
    start = "ยืนยันและเริ่มใช้งาน",
    close = "ปิด",
    sections = listOf(
        section("1. วัตถุประสงค์ของแอป", "แอปช่วยเสริมการเรียนคำศัพท์ TOEIC การฝึกออกเสียง และการฝึกสนทนาภาษาอังกฤษ แอปไม่ใช่สื่อการเรียน การสอบ หรือบริการให้คะแนนอย่างเป็นทางการของ TOEIC ไม่ใช่โรงเรียนภาษา สถาบันการศึกษา หรือหน่วยงานจัดสอบ และไม่ได้รับการอนุมัติ แนะนำ รับรอง หรือเป็นพันธมิตรอย่างเป็นทางการจากองค์กร TOEIC หรือบุคคลที่สามใด ๆ “TOEIC” เป็นเครื่องหมายการค้าของผู้ถือสิทธิ์ที่เกี่ยวข้อง"),
        section("2. ผลลัพธ์การเรียน", "การใช้แอปไม่รับประกันคะแนน TOEIC ที่สูงขึ้น การบรรลุ เป้าหมายคะแนน การสอบผ่าน การพัฒนาภาษาอังกฤษ คำศัพท์ การออกเสียงหรือการสนทนา การเข้าศึกษา การได้งาน หรือใบรับรอง ผลลัพธ์ขึ้นอยู่กับเวลา วิธีเรียน ระดับภาษา เนื้อหาและสภาพแวดล้อมการสอบ โปรดใช้เอกสารทางการ ครู ผู้เชี่ยวชาญ และแหล่งข้อมูลที่เชื่อถือได้ร่วมด้วยเมื่อจำเป็น"),
        section("3. เนื้อหาการเรียน", "ไม่รับประกันความถูกต้อง ความครบถ้วน ความเป็นปัจจุบัน หรือความเหมาะสมของคำศัพท์ ความหมาย ตัวอย่าง คำพ้อง คำที่ใช้ร่วมกัน การออกเสียง ระดับความยาก ช่วงคะแนนและข้อมูลอื่น ๆ คำแปลและการจัดประเภทอาจมีข้อผิดพลาด สำนวนไม่เป็นธรรมชาติ ความแตกต่างตามภูมิภาคหรือความเห็นต่าง ช่วงคะแนนและระดับความยากเป็นเพียงข้อมูลอ้างอิง ไม่ใช่เกณฑ์ทางการของ TOEIC ข้อมูลคำศัพท์ใช้ AI ช่วยจัดทำและตรวจแก้โดยผู้ดำเนินการ แต่อาจยังมีข้อผิดพลาด"),
        section("4. คำแปลและการแสดงหลายภาษา", "แอปอาจแสดงเป็นภาษาไทย ญี่ปุ่น อังกฤษ และภาษาอื่น คำแปลมีไว้เพื่ออ้างอิงการเรียน ไม่รับประกันว่าถูกต้อง เป็นธรรมชาติ หรือเหมือนกันทุกภาษา สำนวน รายละเอียด ตัวอย่าง ลำดับคำ หรือเนื้อหาอาจแตกต่างกัน หากฉบับภาษาญี่ปุ่นและภาษาอื่นแตกต่าง ให้ยึดฉบับภาษาญี่ปุ่น"),
        section("5. บริการ AI", "แอปสามารถเปิด ChatGPT, Gemini หรือแอป AI ของบุคคลที่สามเพื่อฝึกสนทนา การออกเสียง และการเรียน แอปเพียงเปิดบริการและไม่ส่งข้อมูลที่ป้อนโดยอัตโนมัติ ข้อมูลในบริการภายนอกอยู่ภายใต้ข้อกำหนดและนโยบายความเป็นส่วนตัวของผู้ให้บริการ คำตอบและคำแปลของ AI อาจผิด ไม่ถูกต้อง ไม่เหมาะสม หรือล้าสมัย อย่าใช้ผลลัพธ์ AI เพียงอย่างเดียวในการตัดสินใจสำคัญ"),
        section("6. ข้อมูลส่วนบุคคลและข้อมูลที่ป้อน", "อย่าป้อนรหัสผ่าน รหัสยืนยัน ข้อมูลบัตรหรือบัญชีธนาคาร เลขหนังสือเดินทางหรือบัตรประชาชน ที่อยู่ หมายเลขโทรศัพท์ ตำแหน่งที่ตั้ง ข้อมูลสุขภาพ ข้อมูลเกี่ยวกับที่ทำงาน ข้อมูลของผู้อื่น หรือข้อมูลลับลงในแอปหรือ AI ภายนอก โปรดดูนโยบายความเป็นส่วนตัวด้านล่าง ข้อมูลที่ส่งไปยัง ChatGPT, Gemini หรือบริการอื่นจะได้รับการจัดการตามนโยบายของผู้ให้บริการ"),
        section("7. การสำรองข้อมูลและข้อมูลการเรียน", "แอปอาจรองรับการบันทึกหรือกู้คืนข้อมูลการเรียนด้วยไฟล์สำรอง ซึ่งอาจมีสถานะ ประวัติ รายการโปรด วันเรียนต่อเนื่อง การตั้งค่า และข้อมูลอื่น ไฟล์สำรองไม่ได้เข้ารหัสและไม่ได้สร้างโดยอัตโนมัติ โปรดเก็บรักษาให้ปลอดภัย ผู้ดำเนินการไม่รับผิดชอบต่อการสูญหาย ความเสียหาย การนำไปใช้โดยมิชอบ การรั่วไหล หรือการกู้คืนไม่สำเร็จ การกู้คืนอาจแทนที่ข้อมูลปัจจุบัน โปรดสำรองข้อมูลปัจจุบันแยกไว้ก่อนกู้คืน"),
        section("8. TTS และเสียงบน Android", "การออกเสียงและอ่านข้อความขึ้นอยู่กับอุปกรณ์ Android ระบบ เครื่องมือหรือเอนจิน TTS ข้อมูลเสียง และการตั้งค่า การออกเสียง สำเนียง ความเร็ว ภาษา และคุณภาพอาจแตกต่างกัน ไม่รับประกันว่าจะเล่นได้ทุกอุปกรณ์หรือภาษา หากเสียงไม่ทำงานให้ตรวจสอบระดับเสียง การตั้งค่า TTS ข้อมูลเสียง เครือข่าย และความเข้ากันได้ เสียงเป็นเพียงข้อมูลอ้างอิง ไม่ใช่การประเมินการออกเสียง TOEIC อย่างเป็นทางการ การใช้ไมโครโฟน ข้อมูลเสียง และการบันทึกในแอปภายนอกเป็นไปตามนโยบายของแอปนั้น"),
        section("9. การแจ้งเตือนและอุปกรณ์", "การแจ้งเตือนอาจไม่แสดงหรือไม่ถึงผู้ใช้เนื่องจากสิทธิ์ การตั้งค่า Android สถานะอุปกรณ์ การประหยัดแบตเตอรี่ เครือข่าย หรือเหตุอื่น ผู้ดำเนินการไม่รับผิดชอบต่อการแจ้งเตือนที่หาย ช้า หรือเปลี่ยนเนื้อหา ไม่รับประกันการทำงานบนทุกอุปกรณ์ ระบบ หน้าจอ เครือข่าย หรือบริการภายนอก"),
        section("10. การใช้งานโดยผู้เยาว์", "ผู้เยาว์ต้องได้รับความยินยอมจากผู้ปกครองหรือผู้แทนโดยชอบด้วยกฎหมาย ห้ามป้อนหรือส่งชื่อ ที่อยู่ โรงเรียน โทรศัพท์ รูปภาพ ตำแหน่ง หรือข้อมูลส่วนบุคคลอื่นในแอปหรือ AI ภายนอก ผู้ปกครองควรตรวจสอบการใช้งานอย่างเหมาะสม หากผู้ดำเนินการกำหนดอายุขั้นต่ำเพิ่มเติม จะแสดงในแอปหรือร้านค้า"),
        section("11. Google Play และฟังก์ชันพรีเมียม", "แอปอาจมีฟังก์ชันแบบชำระเงิน เช่น ชุดคำศัพท์ TOEIC ระดับสูง ราคาที่แสดงบน Google Play ณ เวลาซื้อมีผล และราคา สกุลเงิน ภาษี เงื่อนไขการขาย หรือเนื้อหาอาจเปลี่ยน การยืนยันและกู้คืนการซื้อขึ้นอยู่กับบัญชี Google Play สถานะการชำระเงิน อุปกรณ์ และเครือข่าย การซื้อที่รอดำเนินการ ข้อผิดพลาดในการชำระเงิน ความล่าช้า หรือการเปลี่ยนบัญชี/อุปกรณ์อาจทำให้ใช้ฟังก์ชันไม่ได้ทันที เมื่อกู้คืนการซื้อ โปรดใช้บัญชี Google Play เดิมที่ใช้ซื้อ การคืนเงิน การยกเลิก และขั้นตอนการซื้อเป็นไปตามข้อกำหนดและขั้นตอนของ Google Play และกฎหมายที่ใช้บังคับ"),
        section("12. การเปลี่ยนแปลง หยุด และยุติแอป", "ผู้ดำเนินการอาจเปลี่ยนเนื้อหา ฟังก์ชัน ดีไซน์ อุปกรณ์/ระบบที่รองรับ AI ภายนอก ราคา ข้อมูล หรือข้อจำกัดความรับผิดนี้ และอาจหยุดหรือยุติบริการบางส่วนหรือทั้งหมด การเปลี่ยนแปลงอาจทำให้ฟังก์ชัน เนื้อหา การเชื่อมต่อ หรือข้อมูลใช้ไม่ได้ การเปลี่ยนแปลงสำคัญจะแจ้งเท่าที่ทำได้ โปรดสำรองข้อมูลที่ต้องการเก็บไว้เป็นประจำ"),
        section("13. ทรัพย์สินทางปัญญาและเครื่องหมายการค้า", "สิทธิในโปรแกรม ดีไซน์ ข้อความ รูปภาพ เสียง ฐานข้อมูล และเนื้อหาอื่นเป็นของผู้ดำเนินการหรือผู้ถือสิทธิ์ ห้ามคัดลอก ขาย แจกจ่าย ดัดแปลง หรือใช้ต่อโดยไม่ได้รับอนุญาต TOEIC, ChatGPT, Gemini, Android และ Google Play เป็นเครื่องหมายการค้าของเจ้าของแต่ละราย แอปไม่มีความร่วมมือหรือการรับรองจากบุคคลที่สามเหล่านั้น"),
        section("14. ความรับผิดชอบของผู้ใช้", "ผู้ใช้ใช้แอปด้วยความรับผิดชอบของตนเอง หากทำให้บุคคลที่สามเสียหาย ผู้ใช้ต้องแก้ไขด้วยค่าใช้จ่ายของตนเอง ห้ามใช้แอปเพื่อการผิดกฎหมาย รบกวนผู้อื่น เข้าถึงโดยไม่ได้รับอนุญาต ละเมิดลิขสิทธิ์ หรือวัตถุประสงค์ไม่เหมาะสม"),
        section("15. ค่าเสียหาย", "เท่าที่กฎหมายอนุญาต ผู้ดำเนินการไม่รับผิดชอบต่อความเสียหายทางอ้อม ความเสียหายพิเศษ การสูญเสียกำไร การสูญเสียข้อมูล หรือความเสียหายอื่นจากการใช้หรือไม่สามารถใช้แอปได้ ทั้งนี้ไม่รวมความเสียหายที่เกิดจากการจงใจหรือประมาทเลินเล่ออย่างร้ายแรงของผู้ดำเนินการ ความเสียหายต่อชีวิตหรือร่างกาย หรือความเสียหายที่กฎหมายไม่อนุญาตให้ยกเว้นหรือจำกัดความรับผิด"),
        section("16. ติดต่อ", "หากมีคำถามเกี่ยวกับข้อจำกัดความรับผิดนี้ เนื้อหา หรือการใช้แอป โปรดติดต่อ:\n\nผู้ดำเนินการ: GachiGuild\nอีเมล: gachiguild@gmail.com")
    )
)
