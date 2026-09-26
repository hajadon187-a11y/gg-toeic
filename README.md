# Gachi Guild Flashcard for TOEIC（GG TOEIC）

Kotlin と Jetpack Compose で作成する、TOEIC 向け英単語学習 Android アプリです。単語データと学習状態は端末内の Room に保存し、基本的な学習はオフラインで利用できます。

## 現在の状態

このリポジトリは、別リポジトリで管理している旧アプリの共通機能を土台にした TOEIC 用の再構築版です。

- Android package: `com.gachiguild.gachitoeic`
- applicationId: `com.gachiguild.gachitoeic`
- 初回データ: `app/src/main/assets/vocabulary.json`
- 学習状態: Room Database
- バックアップ拡張子: `.toeic-backup`

語彙 JSON は現時点では再構築前の初期資産です。TOEIC の出題範囲・Part 別分類・スコア帯に合わせたデータへ順次差し替えます。

## 主な機能

- 単語カード、検索、お気に入り、復習履歴
- Basic / Standard / Advanced のレベルフィルター
- 英語発音（US / UK）の切り替え
- 日本語、英語、中国語、ヒンディー語、ベトナム語、韓国語、インドネシア語、タイ語、スペイン語の UI
- 学習進捗、連続学習日数、リマインダー通知
- 端末内バックアップと復元
- ChatGPT / Gemini アプリの起動ガイド

## ビルド

```bash
./gradlew assembleDebug
./gradlew test
```

Android Studio ではプロジェクトルートを開き、`app` モジュールを実行してください。

## ディレクトリ

```text
app/src/main/java/com/gachiguild/gachitoeic/
├── data/          # Room、バックアップ、課金、AI 起動
├── domain/        # 学習モデルとリポジトリ
├── presentation/  # ViewModel と Compose 画面
└── ui/            # 多言語文言とテーマ
```

## 注意

TOEIC は ETS の登録商標です。本アプリは ETS と提携・承認・認可されていません。
