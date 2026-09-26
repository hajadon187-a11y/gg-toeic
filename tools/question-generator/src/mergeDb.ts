// DBマージモジュール
// 生成した問題DB（ai_toefl_coach.db）の内容を、アプリのRoom DB（device_ai_toefl_coach.db）にマージする。
// アプリのDBは全テーブル（study_records, users, favorites など）を持つため、上書きせずに
// 生成した問題だけを追加する。

import Database from "better-sqlite3";

/**
 * 生成DBの内容をアプリDBにマージする。
 * @param appDbPath アプリのRoom DB（全テーブルを持つ）のパス
 * @param generatedDbPath 生成した問題DBのパス
 */
export function mergeDb(appDbPath: string, generatedDbPath: string): void {
  const appDb = new Database(appDbPath);
  const genDb = new Database(generatedDbPath, { readonly: true });

  appDb.pragma("journal_mode = WAL");
  appDb.pragma("foreign_keys = ON");

  const mergeAll = appDb.transaction(() => {
    mergeVocabulary(appDb, genDb);
    mergeGrammar(appDb, genDb);
    mergeReading(appDb, genDb);
    mergeListening(appDb, genDb);
    mergeQuestions(appDb, genDb);
  });

  mergeAll();
  appDb.close();
  genDb.close();
}

/** 語彙をマージ（wordが重複しないものだけ追加） */
function mergeVocabulary(appDb: Database.Database, genDb: Database.Database): void {
  const existing = new Set(
    (appDb.prepare("SELECT word FROM vocabulary").all() as { word: string }[]).map((r) => r.word)
  );
  const rows = genDb.prepare("SELECT word, meaning, example, isFavorite, nextReviewAt, intervalDays FROM vocabulary").all() as {
    word: string;
    meaning: string;
    example: string;
    isFavorite: number;
    nextReviewAt: number;
    intervalDays: number;
  }[];
  const insert = appDb.prepare(`
    INSERT INTO vocabulary (word, meaning, example, isFavorite, nextReviewAt, intervalDays)
    VALUES (@word, @meaning, @example, @isFavorite, @nextReviewAt, @intervalDays)
  `);
  let added = 0;
  for (const row of rows) {
    if (existing.has(row.word)) continue;
    insert.run({
      word: row.word,
      meaning: row.meaning,
      example: row.example,
      isFavorite: row.isFavorite,
      nextReviewAt: row.nextReviewAt,
      intervalDays: row.intervalDays,
    });
    existing.add(row.word);
    added++;
  }
  console.log(`  vocabulary: ${added}件追加`);
}

/** 文法問題をマージ（promptが重複しないものだけ追加） */
function mergeGrammar(appDb: Database.Database, genDb: Database.Database): void {
  const existing = new Set(
    (appDb.prepare("SELECT prompt FROM grammar_questions").all() as { prompt: string }[]).map((r) => r.prompt)
  );
  const rows = genDb.prepare("SELECT prompt, correctAnswer, explanation, difficulty, options FROM grammar_questions").all() as {
    prompt: string;
    correctAnswer: string;
    explanation: string;
    difficulty: string;
    options: string;
  }[];
  const insert = appDb.prepare(`
    INSERT INTO grammar_questions (prompt, correctAnswer, explanation, difficulty, options)
    VALUES (@prompt, @correctAnswer, @explanation, @difficulty, @options)
  `);
  let added = 0;
  for (const row of rows) {
    if (existing.has(row.prompt)) continue;
    insert.run({
      prompt: row.prompt,
      correctAnswer: row.correctAnswer,
      explanation: row.explanation,
      difficulty: row.difficulty,
      options: row.options ?? "",
    });
    existing.add(row.prompt);
    added++;
  }
  console.log(`  grammar_questions: ${added}件追加`);
}


/** リーディング問題をマージ（titleが重複しないものだけ追加） */
function mergeReading(appDb: Database.Database, genDb: Database.Database): void {
  const existing = new Set(
    (appDb.prepare("SELECT title FROM reading_passages").all() as { title: string }[]).map((r) => r.title)
  );
  const rows = genDb.prepare("SELECT title, content, question, answer, explanation, options FROM reading_passages").all() as {
    title: string;
    content: string;
    question: string;
    answer: string;
    explanation: string;
    options: string;
  }[];
  const insert = appDb.prepare(`
    INSERT INTO reading_passages (title, content, question, answer, explanation, options)
    VALUES (@title, @content, @question, @answer, @explanation, @options)
  `);
  let added = 0;
  for (const row of rows) {
    if (existing.has(row.title)) continue;
    insert.run({
      title: row.title,
      content: row.content,
      question: row.question,
      answer: row.answer,
      explanation: row.explanation,
      options: row.options ?? "",
    });
    existing.add(row.title);
    added++;
  }
  console.log(`  reading_passages: ${added}件追加`);
}


/** リスニング問題をマージ（titleが重複しないものだけ追加） */
function mergeListening(appDb: Database.Database, genDb: Database.Database): void {
  const existing = new Set(
    (appDb.prepare("SELECT title FROM listening_exercises").all() as { title: string }[]).map((r) => r.title)
  );
  const rows = genDb.prepare("SELECT title, audioUrl, prompt, answer, explanation FROM listening_exercises").all() as {
    title: string;
    audioUrl: string;
    prompt: string;
    answer: string;
    explanation: string;
  }[];
  const insert = appDb.prepare(`
    INSERT INTO listening_exercises (title, audioUrl, prompt, answer, explanation)
    VALUES (@title, @audioUrl, @prompt, @answer, @explanation)
  `);
  let added = 0;
  for (const row of rows) {
    if (existing.has(row.title)) continue;
    insert.run({
      title: row.title,
      audioUrl: row.audioUrl,
      prompt: row.prompt,
      answer: row.answer,
      explanation: row.explanation,
    });
    existing.add(row.title);
    added++;
  }
  console.log(`  listening_exercises: ${added}件追加`);
}

/** スピーキング/ライティング/チューター用問題をマージ（title+promptが重複しないものだけ追加） */
function mergeQuestions(appDb: Database.Database, genDb: Database.Database): void {
  const existing = new Set(
    (appDb.prepare("SELECT title, prompt FROM questions").all() as { title: string; prompt: string }[]).map(
      (r) => `${r.title}|${r.prompt}`
    )
  );
  const rows = genDb.prepare("SELECT category, title, prompt, difficulty FROM questions").all() as {
    category: string;
    title: string;
    prompt: string;
    difficulty: string;
  }[];
  const insert = appDb.prepare(`
    INSERT INTO questions (category, title, prompt, difficulty)
    VALUES (@category, @title, @prompt, @difficulty)
  `);
  let added = 0;
  for (const row of rows) {
    const key = `${row.title}|${row.prompt}`;
    if (existing.has(key)) continue;
    insert.run({
      category: row.category,
      title: row.title,
      prompt: row.prompt,
      difficulty: row.difficulty,
    });
    existing.add(key);
    added++;
  }
  console.log(`  questions: ${added}件追加`);
}
