// 問題生成モジュール
// 各問題タイプのプロンプト設計とAI呼び出し

import { chatJson, type AiConfig } from "./aiClient.js";
import type {
  Difficulty,
  GeneratedQuestions,
  GenerationConfig,
  GrammarCategory,
  GrammarQuestion,
  ListeningQuestion,
  PromptQuestion,
  QuestionType,
  ReadingQuestion,
  TargetTest,
  VocabularyQuestion,
} from "./types.js";
import { GRAMMAR_CATEGORIES } from "./types.js";

/** 問題タイプごとの生成関数 */
export async function generateQuestions(
  config: AiConfig,
  genConfig: GenerationConfig
): Promise<GeneratedQuestions> {
  const result: GeneratedQuestions = {
    vocabulary: [],
    grammar: [],
    reading: [],
    listening: [],
    speaking: [],
    writing: [],
    tutor: [],
  };

  switch (genConfig.type) {
    case "vocabulary":
      result.vocabulary = await generateVocabulary(config, genConfig);
      break;
    case "grammar":
      result.grammar = await generateGrammar(config, genConfig);
      break;
    case "reading":
      result.reading = await generateReading(config, genConfig);
      break;
    case "listening":
      result.listening = await generateListening(config, genConfig);
      break;
    case "speaking":
      result.speaking = await generatePromptQuestions(config, genConfig, "Speaking");
      break;
    case "writing":
      result.writing = await generatePromptQuestions(config, genConfig, "Writing");
      break;
    case "tutor":
      result.tutor = await generatePromptQuestions(config, genConfig, "Tutor");
      break;
    default:
      throw new Error(`未対応の問題タイプ: ${genConfig.type}`);
  }

  return result;
}

/** 語彙問題を生成（IELTS向け: meaningEn・類義語を含む） */
async function generateVocabulary(
  config: AiConfig,
  genConfig: GenerationConfig
): Promise<VocabularyQuestion[]> {
  const system = `あなたはIELTS対策の英語教材作成者です。高品質な語彙データを生成してください。
出力は必ず以下のJSON形式にしてください:
{"items": [{"word": "英単語", "meaning": "日本語の意味", "meaningEn": "英語での簡単な説明（英英辞典風）", "synonyms": ["類義語1", "類義語2", "類義語3", "類義語4"], "example": "その単語を使った英文例"}]}`;

  const user = `IELTS学習者向けの語彙データを${genConfig.batchSize}件生成してください。
- 対象テスト: IELTS
- 難易度: ${genConfig.difficulties.join(" / ")}
- IELTSで頻出のアカデミック単語・一般単語を選んでください
- meaningは日本語、meaningEnは英語での簡単な説明、synonymsは4つの類義語（パラフレーズ練習用）を書いてください
- exampleはその単語を使った英文例（学術的な文脈）を書いてください
- 重複しない単語を選んでください`;

  const data = (await chatJson(config, [
    { role: "system", content: system },
    { role: "user", content: user },
  ])) as { items?: VocabularyQuestion[] };

  return (data.items ?? []).map((item) => ({
    word: item.word,
    meaning: item.meaning,
    meaningEn: item.meaningEn ?? "",
    synonyms: item.synonyms ?? [],
    example: item.example,
    isFavorite: false,
  }));
}

/** 文法問題を生成（選択問題） */
async function generateGrammar(
  config: AiConfig,
  genConfig: GenerationConfig
): Promise<GrammarQuestion[]> {
  const categoryList = GRAMMAR_CATEGORIES.join(" / ");
  const system = `あなたはTOEFL/IELTS対策の英語教材作成者です。高品質な文法の選択問題を生成してください。
出力は必ず以下のJSON形式にしてください:
{"items": [{"prompt": "空欄を含む英文", "correctAnswer": "正解の語句", "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"], "explanation": "日本語の解説", "difficulty": "Easy|Medium|Hard", "category": "Tense|Subjunctive|Relative|Participle|Comparison|Passive|Preposition|Conjunctionのいずれか"}]}`;

  const user = `TOEFL/IELTS学習者向けの文法の選択問題を${genConfig.batchSize}件生成してください。
- 対象テスト: ${genConfig.targetTests.join(" / ")}
- 難易度: ${genConfig.difficulties.join(" / ")}
- 文法カテゴリは以下のうちから均等に選んでください: ${categoryList}
- 空欄は ___ で表し、正解は1語または短い語句にしてください
- optionsは必ず4つの選択肢を含み、そのうち1つがcorrectAnswerと一致するようにしてください
- 選択肢は似た形の語句（時制・語形・前置詞などが異なる）にして、学習者が迷うようにしてください
- 解説は日本語で、なぜその答えが正しいのかを明確に説明してください
- 時制、仮定法、関係詞、分詞、比較、受動態など幅広い文法項目をカバーしてください`;

  const data = (await chatJson(config, [
    { role: "system", content: system },
    { role: "user", content: user },
  ])) as { items?: GrammarQuestion[] };

  return (data.items ?? []).map((item) => ({
    prompt: item.prompt,
    correctAnswer: item.correctAnswer,
    explanation: item.explanation,
    difficulty: normalizeDifficulty(item.difficulty),
    category: normalizeCategory(item.category),
    options: normalizeOptions(item.options, item.correctAnswer),
  }));
}

/** 選択肢を正規化（必ず4択、correctAnswerを含む） */
function normalizeOptions(options: string[] | undefined, correctAnswer: string): string[] {
  const cleaned = (options ?? [])
    .map((o) => o.trim())
    .filter((o) => o.length > 0);

  // correctAnswer が含まれていない場合は追加
  if (!cleaned.some((o) => o.toLowerCase() === correctAnswer.toLowerCase())) {
    cleaned.push(correctAnswer);
  }

  // 4択に満たない場合はダミーを追加
  while (cleaned.length < 4) {
    cleaned.push(`(選択肢${cleaned.length + 1})`);
  }

  // 最大4択に制限
  return cleaned.slice(0, 4);
}


/** リーディング問題を生成（選択問題） */
async function generateReading(
  config: AiConfig,
  genConfig: GenerationConfig
): Promise<ReadingQuestion[]> {
  const system = `あなたはTOEFL/IELTS対策の英語教材作成者です。高品質なリーディングの選択問題を生成してください。
出力は必ず以下のJSON形式にしてください:
{"items": [{"title": "タイトル", "content": "英文パッセージ", "question": "質問文", "answer": "正解", "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"], "explanation": "日本語の解説"}]}`;

  const user = `TOEFL/IELTS学習者向けのリーディングの選択問題を${genConfig.batchSize}件生成してください。
- 対象テスト: ${genConfig.targetTests.join(" / ")}
- 難易度: ${genConfig.difficulties.join(" / ")}
- パッセージは150〜300語程度のアカデミックな内容にしてください
- 質問はパッセージの内容理解を問うものにし、正解はパッセージ内の情報から導けるものにしてください
- optionsは必ず4つの選択肢を含み、そのうち1つがanswerと一致するようにしてください
- 選択肢は似た内容の語句にして、学習者が迷うようにしてください
- 解説は日本語で、パッセージのどの部分から答えが導けるかを説明してください`;

  // リーディングはパッセージが長いため、トークン上限を増やす
  const data = (await chatJson(
    config,
    [
      { role: "system", content: system },
      { role: "user", content: user },
    ],
    6000
  )) as { items?: ReadingQuestion[] };


  return (data.items ?? []).map((item) => ({
    title: item.title,
    content: item.content,
    question: item.question,
    answer: item.answer,
    explanation: item.explanation,
    options: normalizeOptions(item.options, item.answer),
  }));
}


/** リスニング問題を生成 */
async function generateListening(
  config: AiConfig,
  genConfig: GenerationConfig
): Promise<ListeningQuestion[]> {
  const system = `あなたはTOEFL/IELTS対策の英語教材作成者です。高品質なリスニング問題を生成してください。
出力は必ず以下のJSON形式にしてください:
{"items": [{"title": "タイトル", "prompt": "質問文", "answer": "正解", "explanation": "日本語の解説"}]}`;

  const user = `TOEFL/IELTS学習者向けのリスニング問題を${genConfig.batchSize}件生成してください。
- 対象テスト: ${genConfig.targetTests.join(" / ")}
- 難易度: ${genConfig.difficulties.join(" / ")}
- キャンパスでの会話や講義など、TOEFL/IELTSで出題されるシチュエーションを想定してください
- 質問は音声内容の理解を問うものにしてください
- 解説は日本語で、どの情報が正解の根拠になるかを説明してください
- audioUrlは空文字にしてください（アプリ側でTTS再生します）`;

  const data = (await chatJson(config, [
    { role: "system", content: system },
    { role: "user", content: user },
  ])) as { items?: Omit<ListeningQuestion, "audioUrl">[] };

  return (data.items ?? []).map((item) => ({
    title: item.title,
    audioUrl: "",
    prompt: item.prompt,
    answer: item.answer,
    explanation: item.explanation,
  }));
}

/** スピーキング / ライティング / チューター用問題を生成 */
async function generatePromptQuestions(
  config: AiConfig,
  genConfig: GenerationConfig,
  category: "Speaking" | "Writing" | "Tutor"
): Promise<PromptQuestion[]> {
  const categoryLabel =
    category === "Speaking"
      ? "スピーキング"
      : category === "Writing"
        ? "ライティング"
        : "AIチューター";

  const system = `あなたはTOEFL/IELTS対策の英語教材作成者です。高品質な${categoryLabel}問題を生成してください。
出力は必ず以下のJSON形式にしてください:
{"items": [{"title": "タイトル", "prompt": "問題文", "difficulty": "Easy|Medium|Hard"}]}`;

  const user = `TOEFL/IELTS学習者向けの${categoryLabel}問題を${genConfig.batchSize}件生成してください。
- 対象テスト: ${genConfig.targetTests.join(" / ")}
- 難易度: ${genConfig.difficulties.join(" / ")}
${
  category === "Speaking"
    ? "- 自分の意見を述べるタスクや、特定のトピックについて話すタスクを出題してください"
    : category === "Writing"
      ? "- 意見文（Opinion Essay）や、賛否を問うタスクを出題してください"
      : "- ロールプレイや面接練習など、AIと対話するシチュエーションを出題してください"
}
- 問題文は英語で書いてください`;

  const data = (await chatJson(config, [
    { role: "system", content: system },
    { role: "user", content: user },
  ])) as { items?: Omit<PromptQuestion, "category">[] };

  return (data.items ?? []).map((item) => ({
    category,
    title: item.title,
    prompt: item.prompt,
    difficulty: normalizeDifficulty(item.difficulty),
  }));
}

/** 難易度を正規化 */
function normalizeDifficulty(value: string): Difficulty {
  const normalized = value.trim().toLowerCase();
  if (normalized.includes("easy")) return "Easy";
  if (normalized.includes("hard")) return "Hard";
  return "Medium";
}

/** 文法カテゴリを正規化 */
function normalizeCategory(value: string | undefined): string {
  if (!value) return "";
  const trimmed = value.trim();
  // 完全一致
  if ((GRAMMAR_CATEGORIES as readonly string[]).includes(trimmed)) return trimmed;
  // 部分一致でマッピング
  const lower = trimmed.toLowerCase();
  if (lower.includes("tense") || lower.includes("時制")) return "Tense";
  if (lower.includes("subjunctive") || lower.includes("仮定法")) return "Subjunctive";
  if (lower.includes("relative") || lower.includes("関係詞") || lower.includes("関係代名詞")) return "Relative";
  if (lower.includes("participle") || lower.includes("分詞")) return "Participle";
  if (lower.includes("compar") || lower.includes("比較")) return "Comparison";
  if (lower.includes("passive") || lower.includes("受動態")) return "Passive";
  if (lower.includes("preposition") || lower.includes("前置詞")) return "Preposition";
  if (lower.includes("conjunction") || lower.includes("接続詞")) return "Conjunction";
  return "";
}

/** 問題タイプの表示名 */
export function questionTypeLabel(type: QuestionType): string {
  const labels: Record<QuestionType, string> = {
    vocabulary: "語彙",
    grammar: "文法",
    reading: "リーディング",
    listening: "リスニング",
    speaking: "スピーキング",
    writing: "ライティング",
    tutor: "AIチューター",
  };
  return labels[type];
}

/** 対象テストの表示 */
export function targetTestsLabel(targetTests: TargetTest[]): string {
  return targetTests.join(" / ");
}