package com.gachiguild.gachitoeic.data.local

import com.gachiguild.gachitoeic.data.local.entity.VocabularyEntity

/**
 * 大規模語彙データは assets/vocabulary.json から読み込む。
 * （自動生成: scripts/rebuild_toeic_vocabulary.py）
 * 静的Kotlinリストはコンパイル負荷が大きいため、JSONアセット方式を採用。
 */
val VocabularyBatch2: List<VocabularyEntity> = emptyList()
