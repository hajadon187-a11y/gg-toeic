# Gachi Guild Flashcard for TOEFL（GG TOEFL）アーキテクチャ

## 1. 概要

Gachi Guild Flashcard for TOEFL（GG TOEFL）は、Kotlin と Jetpack Compose で実装された Android 向けの語彙学習アプリです。現在のアプリ本体は単語学習に集中しており、語彙・学習状態・履歴は端末内の Room に保存します。

設計上の基本方針は次のとおりです。

- ローカルデータを中心としたオフラインファースト
- UI は Compose、状態は `StateFlow`、非同期処理は Kotlin Coroutines
- UI / ViewModel と永続化の間を `StudyContentRepository` で分離
- Hilt による依存性注入
- 外部通信は Google Play Billing に限定し、発音は Android 標準 TTS を利用
- 端末固有の Room ID に依存しないバックアップ／レストア

## 2. 全体構成

```text
┌──────────────────────────────────────────────────────────────┐
│ Android Application                                           │
│                                                              │
│  MainActivity                                                 │
│      └─ AITOEFLCoachTheme                                     │
│          └─ VocabularyScreen (Jetpack Compose)                │
│              ├─ VocabularyViewModel                          │
│              └─ BackupViewModel                               │
│                                                              │
│  Domain                                                       │
│      ├─ VocabularyItem / VocabularyHistory                    │
│      └─ StudyContentRepository                                │
│                                                              │
│  Data                                                         │
│      ├─ RoomStudyContentRepository                            │
│      │   └─ DAO ─ AppDatabase (Room v9)                       │
│      ├─ VocabularySeeder ─ assets/vocabulary.json             │
│      ├─ BackupService                                         │
│      ├─ PremiumBillingManager ─ Google Play Billing           │
│      └─ UserPreferences ─ SharedPreferences                   │
└──────────────────────────────────────────────────────────────┘
            │                         │
            ├─ Android TextToSpeech  └─ Google Play Billing
            └─ Android Storage Access Framework
```

画面遷移ライブラリは使用していません。`MainActivity` が起動後に単一の `VocabularyScreen` を表示し、画面内のタブと Compose の状態で「復習・お気に入り・履歴・進捗・設定」を切り替えます。

## 3. レイヤーと責務

### Presentation

`presentation/screens/vocabulary/VocabularyScreen.kt` が現在のメイン画面です。単語カード、スワイプ、検索、進捗、ヒートマップ、設定、バックアップ操作、購入ダイアログなどを Compose で描画します。

`VocabularyViewModel` は次の状態を `StateFlow` として公開します。

- 現在のタブ、検索条件、TOEFL レベルフィルター
- 単語一覧、履歴、進捗、お気に入り、ヒートマップ
- 今日の目標とストリーク
- 発音アクセント、ボタン効果音設定
- Google Play のプレミアム購入状態

学習操作は ViewModel から Repository へ委譲します。単語の同時更新で変更が上書きされないよう、状態変更には `Mutex` を使用しています。

`BackupViewModel` は Android のファイル選択 UI と `BackupService` の間を仲介し、読み込み後に確認状態を挟んでから復元します。

### Domain

`domain/model` は UI や Room に直接依存しない学習モデルを定義します。

- `VocabularyItem`: 単語、発音、翻訳、例文、類義語、コロケーション、習熟度、レベル
- `VocabularyHistory`: 単語に対する学習アクションと時刻
- `StudyStreak` / `TodayStudyProgress`: 学習目標・ストリークの表示用モデル

`StudyContentRepository` は語彙、履歴、目標、ストリーク、ヒートマップの監視と更新を定義するインターフェースです。Domain 層は Room の Entity や DAO を知りません。

### Data

`RoomStudyContentRepository` が DAO の Flow を Domain モデルへ変換し、更新処理を Room に委譲します。

`AppModule` は Room Database、各 DAO、Repository、Seeder を Hilt の SingletonComponent に登録します。

## 4. 起動とデータ初期化

1. `AIToeflCoachApplication` が Hilt により生成される。
2. Application のバックグラウンドスコープで `VocabularySeeder.seedIfNeeded()` を実行する。
3. Seeder が `app/src/main/assets/vocabulary.json` を読み込み、Room の `vocabulary` テーブルへ投入する。
4. 既存データがある場合は `stableKey` で既存行を解決し、翻訳とレベルだけを更新する。お気に入りや習熟度などの学習状態は保持する。
5. `MainActivity` が表示言語、テーマ、スプラッシュを初期化し、`VocabularyScreen` を表示する。

同梱語彙は現在 6,070 件です。語彙データの生成・更新はアプリ実行時ではなく、`tools/vocabulary-builder` の Python パイプラインで行います。

## 5. 永続化

### Room

- DB 名: `vocabulary_app.db`
- Room スキーマ: version 9
- マイグレーション: 5→6、6→7、7→8、8→9

| テーブル | 役割 |
| --- | --- |
| `vocabulary` | 単語、翻訳、発音、例文、レベル、習熟度、お気に入り状態 |
| `favorites` | お気に入りの種別、単語 ID、登録日時 |
| `vocabulary_history` | `check`、`favorite`、`review_remembered`、`review_forgot` の履歴 |
| `study_settings` | 1日の学習目標。ID=1 の1行を保持 |
| `study_streak` | 連続学習日数と最終達成日。ID=1 の1行を保持 |

`vocabulary.stableKey` は端末内の自動採番 ID と別の識別子です。

- 同梱語彙: `builtin:<asset id>`
- ユーザー追加語彙: `custom:<UUID>`

バックアップではこのキーを使って、端末ごとに異なる Room の ID を解決します。

### SharedPreferences

`app_settings` に表示言語、発音アクセント、レベルフィルター、効果音、初回ガイド表示済み、ダークモードを保存します。初回起動時の表示言語は端末ロケールから決定し、以後はユーザー設定を優先します。

## 6. 学習ロジック

単語の習熟度は青カエルの未マスター／マスター済みの2状態として `VocabularyItem.isMastered`（boolean）で表現します。

| 状態 | `isMastered` | 意味 |
| ---: | :---: | --- |
| 未マスター | `false` | 未学習／忘れた |
| マスター済み | `true` | 青カエルでマスター |

- 「マスター」: マスター済みにする
- 「忘れた」: 未マスターへ戻す
- 単語カードタブの出題: `!isMastered` かつ選択中TOEFLレベルの単語
- お気に入りタブの出題: お気に入り（TOEFLレベルは問わない）
- 次回日時による自動復活や追加学習の仕組みは持たない
- 学習件数: `review_remembered`、`review_forgot` のみを集計
- 目標達成後: 同日中はストリークを重複加算しない
- ヒートマップ: 過去 365 日の日別学習アクションを集計

### 6.1 旧データ互換

Room の `vocabulary` テーブルには旧設計のカラムが残っています。

| カラム | 現在の扱い |
|---|---|
| `intervalDays` | 旧・復習間隔。1 = 未マスター / 8 = マスター済み。1 と 8 は `VocabularyEntity` の定数（`UNMASTERED_INTERVAL_DAYS` / `MASTERED_INTERVAL_DAYS`）で扱い、リポジトリ層で `isMastered` と相互変換する |
| `nextReviewAt` | 旧・次回レビュー日時。**参照も更新もしない**（保存のみ温存） |

カラムを削除しないのは、既存端末の DB と過去に出力したバックアップ JSON の互換を保つためです。

お気に入り操作は `favorites` と `vocabulary.isFavorite` の両方を更新し、`favorite` 履歴を追加します。お気に入り一覧は登録日時の降順で表示します。

## 7. 主要なデータフロー

### 学習アクション

```text
ユーザー操作
  → VocabularyScreen
  → VocabularyViewModel
  → StudyContentRepository
  → vocabulary 更新 + vocabulary_history 追加
  → 目標／ストリーク集計
  → Room Flow
  → ViewModel StateFlow
  → Compose 再描画
```

### バックアップとレストア

バックアップは `.toeflg-backup` ファイルとして保存します。JSON を GZIP 圧縮し、単語データ、履歴、目標、ストリーク、表示設定を含めます。

復元は次の処理を Room のトランザクション内で行います。

1. バックアップのマジック値、形式バージョン、`stableKey` の存在と重複を検証する。
2. 現在の学習状態、カスタム単語、履歴、お気に入りを置き換える。
3. `stableKey` で同梱語彙を現在の Room ID に対応付ける。
4. 履歴とお気に入りを対応付けた Room ID で復元する。
5. トランザクション完了後に表示言語、アクセント、テーマを SharedPreferences へ反映する。

### プレミアムレベル

`PremiumBillingManager` が Google Play Billing の非消費型商品 `toefl_premium_levels_unlock` を管理します。購入済み状態はアプリ起動時・復帰時に再照会し、購入済みならTOEFL L4を解放します。購入処理中、保留、成功、エラーを `PremiumBillingState` で UI に通知します。

通常のデバッグビルドでは検証用にレベル制限を無効化します。`productionDebug` と release ビルドではレベル制限を有効化し、Google Play の購入状態が支払い完了（`PURCHASED`）の場合だけ解放します。

### 発音と効果音

- 単語・コロケーション・例文: Android 標準 `TextToSpeech` の `en-GB` / `en-US`
- 意味: 選択中のアプリ言語の言語コード
- カード操作音: `res/raw` の WAV を `MediaPlayer` で再生
- TTS は端末の音声エンジンを利用し、アプリ側では `INTERNET` 権限を要求しない。対応する音声データが端末にあればオフライン再生が可能

## 8. ディレクトリ構成

```text
app/src/main/
├── assets/
│   └── vocabulary.json
├── java/com/gachiguild/gachitoefl/
│   ├── AIToeflCoachApplication.kt
│   ├── MainActivity.kt
│   ├── data/
│   │   ├── backup/          # GZIP JSON のバックアップ／レストア
│   │   ├── billing/         # Google Play Billing
│   │   ├── local/           # Room、DAO、Seeder、SharedPreferences
│   │   └── repository/      # Repository の Room 実装
│   ├── di/AppModule.kt
│   ├── domain/
│   │   ├── model/
│   │   └── repository/
│   ├── presentation/
│   │   ├── screens/vocabulary/
│   │   └── viewmodel/
│   └── ui/                  # 多言語文字列、テーマ、CompositionLocal
└── res/
    ├── drawable*/            # スプラッシュ、キャラクター画像
    ├── mipmap*/              # アプリアイコン
    └── raw/                  # カード操作音

tools/
├── vocabulary-builder/       # 語彙データ生成・翻訳・レベル分類
└── question-generator/       # AI 問題生成 CLI（アプリ本体とは分離）
```

## 9. 外部サービスと権限

| 接続先 | 用途 | 状態 |
| --- | --- | --- |
| Android 標準 TextToSpeech | 発音・読み上げ | 現在使用 |
| Google Play Billing | プレミアムレベル購入 | 現在使用 |
| DeepSeek などの AI API | 語彙・問題の生成 | 開発ツール側で使用 |
| Supabase / OpenAI / Gemini / DeepSeek | 採点・添削・チャット等 | 将来設計のみ |

`docs/AI_API_INTEGRATION.md` は将来の AI 接続設計です。現行 Android アプリには、同ドキュメントに記載された `AiRepository` や Supabase 接続はまだ実装されていません。

## 10. テストとビルド

主なテストは `app/src/test` にあり、Room Repository、バックアップ、学習進捗、履歴、ストリークを検証します。Room のユニットテストは Robolectric を使用します。

```bash
./gradlew :app:assembleDebug
./gradlew :app:assembleProductionDebug
./gradlew :app:compileDebugKotlin
./gradlew :app:testDebugUnitTest
```

主要な実行環境は次のとおりです。

- Kotlin 2.2.10 / JVM 17
- Android Gradle Plugin 9.0.1
- `compileSdk` / `targetSdk`: 36
- `minSdk`: 29
- Jetpack Compose BOM 2024.10.00
- Room 2.7.1
- Hilt 2.56.2
- Google Play Billing 8.0.0

## 11. 今後の拡張方針

新しい学習モジュールを追加する場合は、まず Domain にモデルと Repository インターフェースを定義し、Data に Room またはリモート実装を追加します。UI は ViewModel の `StateFlow` を購読し、Hilt の `AppModule` で実装を束ねます。

AI 採点、クラウド同期、認証、音声認識は現在未実装です。復習リマインダー通知は実装済みで、毎日21:00にストリーク状況を確認し、当日の学習目標が未達成の場合に通知します。今後追加する機能も、既存のローカル学習機能を保つため、ネットワーク依存処理は Data 層または専用 Repository に閉じ込める方針です。
