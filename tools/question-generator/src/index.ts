// 問題生成タスクのエントリーポイント
// 使い方:
//   npm run generate -- --type vocabulary --count 10
//   npm run generate -- --type grammar --count 5 --difficulty Easy,Medium
//   npm run generate -- --type all --count 10

import "dotenv/config";
import { loadAiConfig } from "./aiClient.js";
import { generateQuestions, questionTypeLabel } from "./generator.js";
import { getTableCounts, writeToDb } from "./dbWriter.js";
import type {
  Difficulty,
  GeneratedQuestions,
  GenerationConfig,
  QuestionType,
  TargetTest,
} from "./types.js";


/** CLI引数 */
interface CliArgs {
  type: QuestionType | "all";
  count: number;
  difficulties: Difficulty[];
  targetTests: TargetTest[];
  dbPath: string;
  dryRun: boolean;
}

/** コマンドライン引数をパース */
function parseArgs(argv: string[]): CliArgs {
  const args: CliArgs = {
    type: "all",
    count: parseInt(process.env.BATCH_SIZE ?? "10", 10),
    difficulties: parseList<Difficulty>(process.env.DIFFICULTIES ?? "Easy,Medium,Hard"),
    targetTests: parseList<TargetTest>(process.env.TARGET_TESTS ?? "TOEFL,IELTS"),
    dbPath: "./db/ai_toefl_coach.db",
    dryRun: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const value = argv[i + 1];
    switch (arg) {
      case "--type":
        if (value) {
          args.type = value as QuestionType | "all";
          i++;
        }
        break;
      case "--count":
        if (value) {
          args.count = parseInt(value, 10);
          i++;
        }
        break;
      case "--difficulty":
        if (value) {
          args.difficulties = parseList<Difficulty>(value);
          i++;
        }
        break;
      case "--test":
        if (value) {
          args.targetTests = parseList<TargetTest>(value);
          i++;
        }
        break;
      case "--db":
        if (value) {
          args.dbPath = value;
          i++;
        }
        break;
      case "--dry-run":
        args.dryRun = true;
        break;
      case "--help":
      case "-h":
        printHelp();
        process.exit(0);
        break;
    }
  }

  return args;
}

/** カンマ区切りのリストをパース */
function parseList<T extends string>(value: string): T[] {
  return value
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0) as T[];
}

/** ヘルプを表示 */
function printHelp(): void {
  console.log(`
問題生成タスク - TOEFL/IELTS問題を生成してアプリのRoom DB (SQLite) に積み立てる

使い方:
  npm run generate -- [オプション]

オプション:
  --type <type>        生成する問題タイプ
                       vocabulary | grammar | reading | listening | speaking | writing | tutor | all
                       (デフォルト: all)
  --count <n>          1回の実行で生成する問題数 (デフォルト: BATCH_SIZE)
  --difficulty <list>  難易度 (Easy,Medium,Hard をカンマ区切り)
  --test <list>        対象テスト (TOEFL,IELTS をカンマ区切り)
  --db <path>          SQLite DBファイルのパス (デフォルト: ./db/ai_toefl_coach.db)
  --dry-run            DBに書き込まず、生成結果のみ表示
  --help, -h           このヘルプを表示

例:
  npm run generate -- --type vocabulary --count 20
  npm run generate -- --type grammar --count 10 --difficulty Easy,Medium
  npm run generate -- --type all --count 5 --dry-run
`);
}

/** メイン処理 */
async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  console.log("=== AI問題生成タスク ===");
  console.log(`プロバイダー: ${process.env.AI_PROVIDER ?? "deepseek"}`);
  console.log(`問題タイプ: ${args.type === "all" ? "全タイプ" : questionTypeLabel(args.type)}`);
  console.log(`生成数: ${args.count}件/タイプ`);
  console.log(`難易度: ${args.difficulties.join(", ")}`);
  console.log(`対象テスト: ${args.targetTests.join(", ")}`);
  console.log(`DB: ${args.dbPath}`);
  console.log("");

  const aiConfig = loadAiConfig();

  // 生成するタイプのリスト
  const types: QuestionType[] =
    args.type === "all"
      ? ["vocabulary", "grammar", "reading", "listening", "speaking", "writing", "tutor"]
      : [args.type];

  // 各タイプを生成
  for (const type of types) {
    const genConfig: GenerationConfig = {
      type,
      batchSize: args.count,
      difficulties: args.difficulties,
      targetTests: args.targetTests,
    };

    console.log(`[${questionTypeLabel(type)}] 生成中...`);
    try {
      const questions = await generateQuestions(aiConfig, genConfig);
      const count = countGenerated(questions, type);
      console.log(`  ✓ ${count}件生成しました`);

      if (args.dryRun) {
        printPreview(questions, type);
      } else {
        const result = writeToDb(args.dbPath, questions);
        console.log(`  ✓ DBに書き込みました (${result[type] ?? 0}件)`);
      }
    } catch (error) {
      console.error(`  ✗ 生成に失敗しました: ${(error as Error).message}`);
    }
    console.log("");
  }

  // 最終集計
  if (!args.dryRun) {
    console.log("=== DB内の問題数 ===");
    const counts = getTableCounts(args.dbPath);
    for (const [table, count] of Object.entries(counts)) {
      console.log(`  ${table}: ${count}件`);
    }
  }

  console.log("");
  console.log("完了しました。");
}

/** 生成された問題数をカウント */
function countGenerated(questions: GeneratedQuestions, type: QuestionType): number {
  return questions[type].length;
}

/** 生成結果のプレビューを表示（dry-run用） */
function printPreview(questions: GeneratedQuestions, type: QuestionType): void {
  const items = questions[type];
  if (items.length === 0) return;
  const first = items[0] as unknown as Record<string, unknown>;
  console.log("  プレビュー（先頭1件）:");
  for (const [key, value] of Object.entries(first)) {
    const str = String(value);
    console.log(`    ${key}: ${str.length > 80 ? str.slice(0, 80) + "..." : str}`);
  }
}


main().catch((error) => {
  console.error("エラーが発生しました:", error);
  process.exit(1);
});
