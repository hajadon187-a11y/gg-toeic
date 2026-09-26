// 問題生成タスクの型定義

/** 生成する問題の種類 */
export type QuestionType =
  | "vocabulary"
  | "grammar"
  | "reading"
  | "listening"
  | "speaking"
  | "writing"
  | "tutor";

/** 難易度 */
export type Difficulty = "Easy" | "Medium" | "Hard";

/** 対象テスト */
export type TargetTest = "TOEFL" | "IELTS";

/** AIプロバイダー */
export type AiProvider = "openai" | "deepseek" | "gemini";

/** 語彙問題（IELTS向け: 英語意味・類義語あり） */
export interface VocabularyQuestion {
  word: string;
  meaning: string;
  meaningEn?: string;
  synonyms?: string[];
  example: string;
  isFavorite: boolean;
}

/** 文法問題（選択問題） */
export interface GrammarQuestion {
  prompt: string;
  correctAnswer: string;
  explanation: string;
  difficulty: Difficulty;
  /** 選択肢（4択）。correctAnswer を含む */
  options: string[];
  /** 文法カテゴリ */
  category: string;
}

/** 文法カテゴリ */
export const GRAMMAR_CATEGORIES = [
  "Tense",
  "Subjunctive",
  "Relative",
  "Participle",
  "Comparison",
  "Passive",
  "Preposition",
  "Conjunction",
] as const;
export type GrammarCategory = (typeof GRAMMAR_CATEGORIES)[number];


/** リーディング問題（選択問題） */
export interface ReadingQuestion {
  title: string;
  content: string;
  question: string;
  answer: string;
  explanation: string;
  /** 選択肢（4択）。answer を含む */
  options: string[];
}


/** リスニング問題 */
export interface ListeningQuestion {
  title: string;
  audioUrl: string;
  prompt: string;
  answer: string;
  explanation: string;
}

/** スピーキング / ライティング / チューター用問題 */
export interface PromptQuestion {
  category: "Speaking" | "Writing" | "Tutor";
  title: string;
  prompt: string;
  difficulty: Difficulty;
}

/** 生成結果（種類ごとの問題リスト） */
export interface GeneratedQuestions {
  vocabulary: VocabularyQuestion[];
  grammar: GrammarQuestion[];
  reading: ReadingQuestion[];
  listening: ListeningQuestion[];
  speaking: PromptQuestion[];
  writing: PromptQuestion[];
  tutor: PromptQuestion[];
}

/** 生成設定 */
export interface GenerationConfig {
  type: QuestionType;
  batchSize: number;
  difficulties: Difficulty[];
  targetTests: TargetTest[];
}
