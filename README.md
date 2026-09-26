# Gachi Guild Flashcard for TOEFL （GG TOEFL）

Kotlin と Jetpack Compose で作成した、TOEFL 英単語学習用の Android アプリです。単語データと学習状態は Room に保存し、基本的な学習はオフラインで利用できます。

現在 `app/src/main/assets/vocabulary.json` は **6,384語**です。TOEFL学習レベル別の語彙を監査したうえで、場違いな語を正しいレベルへ移動し、不足するレベルには学術語彙リストから選んだ語を補充しています。

| level | TOEFLレベル | 語数 | 備考 |
|---|---|---|---|
| 1 | L1 | 830 | |
| 2 | L2 | 2,105 | |
| 3 | L3 | 1,676 | |
| 4 | L4 | 996 | |
| 5 | L4 | 777 | 旧データ互換用 |
| 4 + 5 | **L4 合計** | **1,773** | UI 上のL4（プレミアム解放対象） |
| | **合計** | **6,384** | |

アプリのレベルフィルターは level 4 と level 5 を「Advanced（L4）」に統合するため（`VocabularyLevel.ADVANCED.matchesVocabularyItemLevel`）、画面上でTOEFL Advancedとして学習できる語数は **1,773語**です。

うち **314語**（L3: 129語 / L4: 185語）は、キャンパスライフ（履修登録・図書館・寮など）と講義（天文学・地質学・考古学・心理学など）に特化した追加語です。選定と投入は `tools/vocabulary-builder/select_campus_academic_words.py` と `tools/vocabulary-builder/add_campus_academic_words.py` で行っています。

`tools/vocabulary-builder/build_vocabulary.py` の分類ルールでレベル妥当性を監査し、基準に満たない語は本来のレベルへ移動、基準を超える語は学術語彙リスト（AVL / COCA-Academic）から選んだ語に置き換えています。

収録している英単語の example 文の多く（約95%）を、アメリカの大学の講義・教科書・教授と学生の会話に近い文脈で再生成しています。対応する example 文の日本語訳も、同じ文脈に合わせて再生成しています。

## 語彙データのライセンス

- 語彙の**選定に使用した学術語彙リスト**（AVL / COCA-Academic、<https://www.academicvocabulary.info>）は、配布元が「学術利用に限る」「他サイトへ再配布しないこと」を条件としています。このため**リスト本体は本リポジトリに含めていません**（`tools/vocabulary-builder/.gitignore` で除外）。必要な場合は `tools/vocabulary-builder/fetch_academic_lists.py` で各自取得してください。
- アプリに同梱しているのは、**本プロジェクトが選定・編集した個々の単語、訳語、定義、例文**です。リストの内容そのものは再配布していません。
- **商用リリースの際は、配布元（academicvocabulary.info）への利用条件確認を推奨します。**

### アプリ内表示用の語彙データに関する表示

本アプリの語彙データは、複数の第三者語彙リストを参考に選定・編集しています。
各語彙リストの著作権および利用条件は、それぞれの権利者に帰属します。
本アプリに収録されている日本語訳、英語定義、例文、同義語、コロケーションおよび多言語訳は、本プロジェクトが選定・編集したデータです。
これらはETS、その他の試験実施団体が提供・承認した公式教材ではありません。

出典：

- New General Service List（NGSL） — New General Service List Project — <https://www.newgeneralservicelist.com/>
- New Academic Word List（NAWL）およびAcademic Word List（AWL） — 各リストの配布元および利用条件に従って使用しています。
- Academic Vocabulary List（AVL）およびCOCA-Academic — Mark Davies / Dee Gardner — <https://www.academicvocabulary.info/> — 商用利用については配布元の許諾条件に従います。
- google-10000-english — first20hours / Josh Kaufman et al. — <https://github.com/first20hours/google-10000-english> — データの商用利用および再配布には、元データのライセンス条件が適用されます。

語彙リストそのものの再配布を目的としたアプリではありません。各出典の利用条件に反する再配布・転載を行わないでください。

## 主な機能

- 6,384語の TOEFL 語彙を初回起動時に Room データベースへ投入（L1〜L4、旧L5を含む）
- 単語カードによる復習。カードをタップして意味・コロケーション・例文を表示
- Tinder 風のスワイプ操作
  - 右: 青カエルをマスター済みにして次のカードへ進む
  - 左: ⭐️お気に入りに登録して次のカードへ進む
- 前のカードへ戻る ◀ ボタン
- 青カエルによる未マスター／マスター済みの2状態管理
- お気に入り一覧、検索、展開表示、マスター状態操作
- 学習アクション履歴（お気に入り・マスター・マスター解除）
- 学習進捗（総単語数、マスター済み、未マスター、お気に入り）
- 1日の学習目標（5 / 10 / 20 / 30語）と連続学習日数（ストリーク）
- ストリーク救済（当日2日分の学習、または7日継続ごとに付与される救済チケット）
- 過去365日分の学習ヒートマップ
- 毎日21:00のストリーク危機通知（継続中で、当日の目標未達成時）
- TOEFLレベル別フィルター（Basic / Standard / Advanced）
- Google Play の買い切り商品による Advanced（L4、1,773語）の解放
- 日本語、英語、中国語（簡体字）、ヒンディー語、ベトナム語、韓国語、インドネシア語、タイ語、スペイン語の UI と意味表示
- US / UK 発音の切り替え（TOEFL向けデフォルトは US）
- Android 標準 TTS による単語・意味・コロケーション・例文の読み上げ
- 単語カードの効果音、および通常アイコンのフッターボタン
- 初回オンボーディング（目標レベル、1日の学習量、ChatGPT / Gemini の設定）
- ChatGPT / Gemini の起動と、Live／音声会話の利用ガイド
- 初回および設定画面からの操作ツアー（長押し検索の練習を含む）
- 学習データのバックアップ / レストアと、オープンソースライセンス一覧

## 画面構成

### 単語カード

起動時に表示されるメイン画面です。未マスター（`!isMastered`）の単語から、選択中のレベルに合うカードをランダムな順番で表示します。カード上の発音アイコンで単語を読み上げ、カード本体をタップすると意味を表示します。

画面下部には次の4つの操作があります。

1. ボタンの使い方
2. 前のカード
3. ⭐️ お気に入り（お気に入りに登録して次のカードへ）
4. マスター（青カエルをマスター済みにする）

右スワイプは「マスター」、左スワイプは「⭐️ お気に入り」、◀ ボタンは前のカードと同じ動作です。マスター済みの単語がカードデッキから自動的に除外されます。

### お気に入り

お気に入り登録した単語を、登録日時の新しい順に表示します。英単語の部分一致検索、単語の展開、意味・発音・例文・コロケーション・類義語の確認、習熟度とお気に入りの変更に対応しています。

### 履歴

学習アクションを新しい順に表示します。各履歴からも発音、意味、習熟度、お気に入りを操作できます。履歴画面には日別学習件数のヒートマップも表示されます。

### AI 練習

画面下部の AI タブから、端末にインストールされている ChatGPT または Gemini を起動できます。アプリから AI の Live モードを直接制御するのではなく、起動後に Live／音声機能を有効にし、最近使ったアプリ一覧から GG TOEFL に戻る手順を案内します。AI アプリを使わず、単語帳だけをオフラインで利用することもできます。

### 初回オンボーディングと操作ツアー

初回起動時は、TOEFL の目標レベル（Basic / Standard / Advanced）、1日の学習目標、AI アプリの利用有無を設定できます。後から設定画面で変更できます。メイン画面の操作ツアーでは主要ボタンを説明し、カードの長押し検索を実際に試せます。

### 進捗・設定

進捗カードを展開すると、カテゴリ別の単語一覧とレベルフィルターを表示できます。進捗は青カエルの状態で「未マスター」「マスター済み」を集計します。

設定ダイアログでは次の項目を変更できます。

- 表示言語
- 発音アクセント（メイン画面上部でも切り替え可能）
- 学習データのバックアップ / レストア
- 使用ライブラリのライセンス表示

## 学習ロジック

### 習熟度と出題範囲

習熟度は青カエルの**未マスター／マスター済みの2状態**だけで管理します。ドメインモデルは `VocabularyItem.isMastered`（boolean）で持ちます。

| 状態 | `isMastered` | 操作例 |
|---:|:---:|---|
| 未マスター | `false` | 未学習、または「⭐️ お気に入り」 |
| マスター済み | `true` | 青カエル／マスター |

出題範囲は次のとおりです。

| タブ | 対象 |
|---|---|
| 単語カード | 未マスター（`!isMastered`）かつ選択中TOEFLレベルの単語 |
| ⭐️ お気に入り | お気に入り（TOEFLレベルは問わない） |

「⭐️ お気に入り」は単語を未マスターに戻し、青カエル／マスターはマスター済みにします。**次回日時による自動復活や追加学習の仕組みは持たず**、マスター済みの単語は単語カードタブに戻りません（お気に入りタブで管理します）。

Room のテーブルには旧データ互換のため `intervalDays`（1 = 未マスター / 8 = マスター済み）と `nextReviewAt` が残っています。`nextReviewAt` は現在参照も更新もせず、`intervalDays` はリポジトリ層で `isMastered` と相互変換するだけです。

### TOEFLレベル

画面上のレベルフィルターは、内部データの5段階を次の3段階にまとめて表示します。

| UI | 内部 level | 語数 |
|---|---|---:|
| Basic | 1 + 2 | 2,935 |
| Standard | 3 | 1,676 |
| Advanced | 4 + 5 | 1,773 |

`level 5` は旧データ互換のために残しており、UI では `Advanced`（L4）に統合されます。debug、`productionDebug`、release ビルドでは購入状態に応じて Advanced をロックします。

### 目標とストリーク

`check`、`review_remembered`、`review_forgot`、`review_unmastered` の学習アクションを1日の学習件数として集計します。お気に入り操作は学習件数に含みません。設定した1日の目標に達するとストリークを更新し、同じ日に何度達成しても日数は1回だけ増えます。

直近1日だけ未達成の日がある場合は、当日に目標の2倍を学習してストリークを救済できます。また、7日継続するたびに救済チケットを1枚獲得し、チケットを1枚使って救済することもできます。

## 音声

単語・コロケーション・例文は、Android 標準の `TextToSpeech` で読み上げます。US（`en-US`）または UK（`en-GB`）の発音アクセントを切り替えられます。意味は選択中のアプリ言語に応じた言語コードで読み上げます。

アプリ側で `INTERNET` 権限や Wi-Fi 接続を必要とする実装ではありません。端末に対応する TTS 音声データがインストールされていれば、音声読み上げもオフラインで利用できます。音声データが未導入の場合や、端末の TTS エンジンが対象言語に対応していない場合は再生できないことがあります。アプリ内の効果音は `res/raw` の WAV ファイルを `MediaPlayer` で再生します。

## プレミアムレベル

TOEFL Advanced（内部 level 4 + 旧 level 5、1,773語）は、Google Play Billing の非消費型商品で解放します。Basic と Standard は購入なしで利用できます。

- 商品 ID: `toefl_premium_levels_unlock`
- 解放対象: `VocabularyLevel.ADVANCED.requiresPremium()`（レベル4 + 旧レベル5 = 1,773語）
- 一度購入すると購入済み状態を再確認して復元
- 購入処理中、保留、エラーの状態を画面に表示
- Play Console 側に同じ商品 ID の商品が設定されていない場合、購入や価格取得は利用できません

debug、`productionDebug`、release ビルドでは `PREMIUM_LEVELS_LOCK_ENABLED` が有効になり、Google Play の購入状態が支払い完了（`PURCHASED`）になった場合だけ Advanced が解放されます。

## バックアップ / レストア

設定画面から `.toeflg-backup` ファイルを作成・読み込みできます。バックアップには次のデータを含みます。

- 単語データ、翻訳、発音情報、コロケーション、例文
- 習熟度、次回復習日時、お気に入り状態
- 学習履歴
- 1日の目標とストリーク
- 表示言語、発音アクセント、テーマ

レストア前に内容を確認するダイアログを表示します。確定すると、現在の学習状態・履歴・お気に入り・カスタム単語を置き換えてバックアップ内容を復元します。端末固有の Room ID ではなく `stableKey` を使って単語を対応付けます。

## 技術構成

- Android application module
- Kotlin 2.2.10 / JVM 17
- Jetpack Compose（Compose BOM 2024.10.00）/ Material 3
- Android Gradle Plugin 9.0.1
- Room 2.7.1
- Hilt 2.56.2
- Kotlin Coroutines 1.8.1
- Google Play Billing 8.0.0
- Robolectric による Room リポジトリのユニットテスト

| 設定 | 値 |
|---|---|
| `compileSdk` | 36 |
| `targetSdk` | 36 |
| `minSdk` | 29 |
| `applicationId` | `com.gachiguild.gachitoefl` |
| `versionCode` | `2` |
| `versionName` | `1.0` |

### アーキテクチャ

```text
UI: MainActivity → VocabularyScreen（Jetpack Compose）
    ↳ VocabularyViewModel / BackupViewModel
Domain: VocabularyItem / VocabularyHistory / StudyContentRepository
Data: Room entities / DAO / RoomStudyContentRepository
       ↳ VocabularySeeder / BackupService / PremiumBillingManager
DI: Hilt（AppModule）
```

### ディレクトリ構成

```text
app/src/main/
├── assets/vocabulary.json
├── assets/vocabulary_phrase_translations.json
├── java/com/gachiguild/gachitoefl/
│   ├── AIToeflCoachApplication.kt
│   ├── MainActivity.kt
│   ├── data/
│   │   ├── backup/
│   │   ├── billing/
│   │   ├── local/       # Room、DAO、Seeder、設定
│   │   └── repository/
│   ├── di/AppModule.kt
│   ├── domain/
│   ├── presentation/
│   │   ├── screens/vocabulary/VocabularyScreen.kt
│   │   └── viewmodel/
│   └── ui/              # 文字列、テーマ、言語・アクセント
└── res/                 # アイコン、フッター画像、効果音、テーマ
```

## データベース

- DB 名: `vocabulary_app.db`
- Room version: 12
- マイグレーション: 5→6（4言語の翻訳列）、6→7（端末間対応用 `stableKey`）、7→8（インドネシア語の翻訳列）、8→9（タイ語の翻訳列）、9→10（スペイン語の翻訳列）、10→11（ストリーク救済日）、11→12（救済チケット）
- 初回起動時に `assets/vocabulary.json` を読み込み
- 既存データがある場合も翻訳とレベル情報を更新し、学習状態は保持

主なテーブルは次のとおりです。

| テーブル | 内容 |
|---|---|
| `vocabulary` | 単語、日本語・英語＋7言語の意味、UK表記・発音記号、類義語、コロケーション、例文、習熟度、レベル、トピック |
| `favorites` | お気に入りの単語 ID と登録日時 |
| `vocabulary_history` | 学習アクションと時刻 |
| `study_settings` | 1日の学習目標 |
| `study_streak` | 連続学習日数と最終達成日 |

## ビルドとテスト

JDK 17 と Android SDK 36 が必要です。

```bash
# デバッグ APK をビルド
./gradlew :app:assembleDebug

# 本番相当（Advancedロック・通常の21:00通知）でデバッガ接続可能な APK をビルド
./gradlew :app:assembleProductionDebug

# Kotlin のコンパイル確認
./gradlew :app:compileDebugKotlin

# Room / Repository のユニットテスト
./gradlew :app:testDebugUnitTest
```

主なテスト対象は、語彙の追加・監視、多言語フォールバック、お気に入り、復習状態、履歴、1日の目標、ストリーク、ヒートマップです（`RoomRepositoryTest`）。

`productionDebug` は、デバッガを接続したまま本番相当の挙動を確認するためのビルドです。`debug` でも TOEFL Advanced は購入済みでない限りロックされ、デバッグ用の起動1分後通知は登録されません。

## 語彙データビルダー

`tools/vocabulary-builder` には、語彙リストの取得、重複排除、レベル分類、AI 補完、翻訳、出力を行う Python ツールがあります。DeepSeek API はアプリ実行時ではなく、語彙データ生成時に使用します。

```bash
cd tools/vocabulary-builder
pip install -r requirements.txt
cp .env.example .env
# .env に DeepSeek API キーを設定

python build_vocabulary.py --all
```

個別実行:

```bash
python build_vocabulary.py --download
python build_vocabulary.py --enrich
python build_vocabulary.py --export
python generate_translations.py
```

生成途中のデータは `data/enriched.json` に保存されます。翻訳・AI 補完の結果は自動生成データのため、公開前に内容を確認してください。

## AI 問題生成ツール（実験用）

`tools/question-generator` には、OpenAI 互換 API（OpenAI / DeepSeek）または Gemini API を使って TOEFL / IELTS の語彙・文法・リーディング・リスニング・スピーキング・ライティング・チューター問題を生成し、SQLite に書き込む TypeScript CLI があります。これは現在の単語帳画面の学習機能とは別のデータ生成ツールです。

```bash
cd tools/question-generator
npm install
# .env に DEEPSEEK_API_KEY など、選択したプロバイダーの API キーを設定
npm run generate -- --type vocabulary --count 20 --test TOEFL --dry-run
```

生成 DB と端末から取得したアプリ DB のマージには `npm run merge -- --app <アプリDB> --gen <生成DB>` を使います。API キーをソースコードやリポジトリに保存しないでください。

## 未実装・準備中

- リスニング、リーディング、文法などの追加学習モジュール
- AI による採点・添削
- Supabase 等を使ったアカウント認証・クラウド同期
- スピーキングの音声認識（STT）
- 詳細な学習統計グラフ
