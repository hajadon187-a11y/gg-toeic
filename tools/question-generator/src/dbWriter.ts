// SQLite書き込みモジュール
// 生成した問題をアプリのRoom DB (SQLite) に書き込む

import Database from "better-sqlite3";
import type {
  GeneratedQuestions,
  GrammarQuestion,
  ListeningQuestion,
  PromptQuestion,
  ReadingQuestion,
  VocabularyQuestion,
} from "./types.js";

/** 書き込み結果の集計 */
export interface WriteResult {
  vocabulary: number;
  grammar: number;
  reading: number;
  listening: number;
  speaking: number;
  writing: number;
  tutor: number;
}

/**
 * 生成した問題をSQLite DBに書き込む。
 * @param dbPath SQLite DBファイルのパス
 * @param questions 生成された問題
 */
export function writeToDb(dbPath: string, questions: GeneratedQuestions): WriteResult {
  const db = new Database(dbPath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");

  // テーブルが存在しない場合は作成する（アプリのRoomスキーマと一致させる）
  ensureSchema(db);

  const result: WriteResult = {
    vocabulary: 0,
    grammar: 0,
    reading: 0,
    listening: 0,
    speaking: 0,
    writing: 0,
    tutor: 0,
  };

  const insertAll = db.transaction(() => {
    result.vocabulary = insertVocabulary(db, questions.vocabulary);
    result.grammar = insertGrammar(db, questions.grammar);
    result.reading = insertReading(db, questions.reading);
    result.listening = insertListening(db, questions.listening);
    result.speaking = insertPromptQuestions(db, questions.speaking);
    result.writing = insertPromptQuestions(db, questions.writing);
    result.tutor = insertPromptQuestions(db, questions.tutor);
  });

  insertAll();
  db.close();

  return result;
}

/**
 * アプリのRoom DBスキーマと一致するテーブルを作成する。
 * 既存のテーブルは変更しない（CREATE TABLE IF NOT EXISTS）。
 */
function ensureSchema(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS vocabulary (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      word TEXT NOT NULL,
      meaning TEXT NOT NULL,
      meaningEn TEXT NOT NULL DEFAULT '',
      synonyms TEXT NOT NULL DEFAULT '',
      example TEXT NOT NULL,
      isFavorite INTEGER NOT NULL DEFAULT 0,
      nextReviewAt INTEGER NOT NULL,
      intervalDays INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS grammar_questions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      prompt TEXT NOT NULL,
      correctAnswer TEXT NOT NULL,
      explanation TEXT NOT NULL,
      difficulty TEXT NOT NULL DEFAULT 'Medium',
      category TEXT NOT NULL DEFAULT '',
      options TEXT NOT NULL DEFAULT ''
    );


    CREATE TABLE IF NOT EXISTS reading_passages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      explanation TEXT NOT NULL,
      options TEXT NOT NULL DEFAULT ''
    );


    CREATE TABLE IF NOT EXISTS listening_exercises (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      audioUrl TEXT NOT NULL,
      prompt TEXT NOT NULL,
      answer TEXT NOT NULL,
      explanation TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS questions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      category TEXT NOT NULL,
      title TEXT NOT NULL,
      prompt TEXT NOT NULL,
      difficulty TEXT NOT NULL DEFAULT 'Medium'
    );
  `);
}


/** 語彙を挿入 */
function insertVocabulary(db: Database.Database, items: VocabularyQuestion[]): number {
  if (items.length === 0) return 0;
  const stmt = db.prepare(`
    INSERT INTO vocabulary (word, meaning, meaningEn, synonyms, example, isFavorite, nextReviewAt, intervalDays)
    VALUES (@word, @meaning, @meaningEn, @synonyms, @example, @isFavorite, @nextReviewAt, @intervalDays)
  `);
  const now = Date.now();
  for (const item of items) {
    stmt.run({
      word: item.word,
      meaning: item.meaning ?? "",
      meaningEn: item.meaningEn ?? "",
      synonyms: (item.synonyms ?? []).join(", "),
      example: item.example ?? "",
      isFavorite: item.isFavorite ? 1 : 0,
      nextReviewAt: now,
      intervalDays: 1,
    });
  }
  return items.length;
}

/** 文法問題を挿入（選択肢はJSON文字列として保存） */
function insertGrammar(db: Database.Database, items: GrammarQuestion[]): number {
  if (items.length === 0) return 0;
  const stmt = db.prepare(`
    INSERT INTO grammar_questions (prompt, correctAnswer, explanation, difficulty, category, options)
    VALUES (@prompt, @correctAnswer, @explanation, @difficulty, @category, @options)
  `);
  for (const item of items) {
    stmt.run({
      prompt: item.prompt,
      correctAnswer: item.correctAnswer,
      explanation: item.explanation,
      difficulty: item.difficulty,
      category: item.category ?? "",
      options: JSON.stringify(item.options ?? []),
    });
  }
  return items.length;
}


/** リーディング問題を挿入（選択肢はJSON文字列として保存） */
function insertReading(db: Database.Database, items: ReadingQuestion[]): number {
  if (items.length === 0) return 0;
  const stmt = db.prepare(`
    INSERT INTO reading_passages (title, content, question, answer, explanation, options)
    VALUES (@title, @content, @question, @answer, @explanation, @options)
  `);
  for (const item of items) {
    stmt.run({
      title: item.title,
      content: item.content,
      question: item.question,
      answer: item.answer,
      explanation: item.explanation,
      options: JSON.stringify(item.options ?? []),
    });
  }
  return items.length;
}


/** リスニング問題を挿入 */
function insertListening(db: Database.Database, items: ListeningQuestion[]): number {
  if (items.length === 0) return 0;
  const stmt = db.prepare(`
    INSERT INTO listening_exercises (title, audioUrl, prompt, answer, explanation)
    VALUES (@title, @audioUrl, @prompt, @answer, @explanation)
  `);
  for (const item of items) {
    stmt.run({
      title: item.title,
      audioUrl: item.audioUrl,
      prompt: item.prompt,
      answer: item.answer,
      explanation: item.explanation,
    });
  }
  return items.length;
}

/** スピーキング / ライティング / チューター用問題を挿入 */
function insertPromptQuestions(db: Database.Database, items: PromptQuestion[]): number {
  if (items.length === 0) return 0;
  const stmt = db.prepare(`
    INSERT INTO questions (category, title, prompt, difficulty)
    VALUES (@category, @title, @prompt, @difficulty)
  `);
  for (const item of items) {
    stmt.run({
      category: item.category,
      title: item.title,
      prompt: item.prompt,
      difficulty: item.difficulty,
    });
  }
  return items.length;
}

/** DB内の各テーブルの件数を取得 */
export function getTableCounts(dbPath: string): Record<string, number> {
  const db = new Database(dbPath, { readonly: true });
  const tables = [
    "vocabulary",
    "grammar_questions",
    "reading_passages",
    "listening_exercises",
    "questions",
  ];
  const counts: Record<string, number> = {};
  for (const table of tables) {
    const row = db.prepare(`SELECT COUNT(*) as count FROM ${table}`).get() as { count: number };
    counts[table] = row.count;
  }
  db.close();
  return counts;
}
