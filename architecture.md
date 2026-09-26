# GG TOEIC アーキテクチャ

## 方針

アプリ本体は、TOEIC 用の語彙データを Room に投入して学習するオフライン中心の構成です。Compose の画面は ViewModel を介してドメインのリポジトリへアクセスします。

```text
MainActivity
└── VocabularyScreen
    └── VocabularyViewModel
        └── StudyContentRepository
            ├── RoomStudyContentRepository
            └── AppDatabase
```

## データフロー

1. `GgToeicApplication` が起動する。
2. `VocabularySeeder` が `assets/vocabulary.json` を読み込む。
3. 語彙と学習状態を Room に保存する。
4. `VocabularyViewModel` がカード、検索、履歴、進捗を公開する。
5. Compose 画面が StateFlow を購読して表示を更新する。

## 主な責務

- `data/local`: Room Database、DAO、語彙投入、ユーザー設定
- `data/backup`: GZIP 圧縮した学習データの書き出しと復元
- `data/billing`: Advanced レベルの買い切り解放
- `data/ai`: インストール済み AI アプリの起動
- `domain`: 語彙モデルと学習リポジトリの契約
- `presentation`: ViewModel と Compose UI
- `ui`: 多言語文言、テーマ、発音設定

## 永続化

語彙、学習履歴、お気に入り、ストリーク、設定を Room に保存します。バックアップは `.toeic-backup` ファイルに GZIP 圧縮した JSON として保存します。

## TOEIC データ移行

現在の JSON は再構築前の初期資産です。TOEIC 用データへ差し替える際は、次の項目を確認します。

- Part 1〜7 の出題文脈
- 語彙のスコア帯または学習レベル
- 例文、意味、発音、同義語
- Room の stable key と既存学習状態の扱い
