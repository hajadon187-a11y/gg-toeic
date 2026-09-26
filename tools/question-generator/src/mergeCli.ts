// DBマージタスクのエントリーポイント
// 使い方:
//   npm run merge -- --app ./db/device_ai_toefl_coach.db --gen ./db/ai_toefl_coach.db

import { mergeDb } from "./mergeDb.js";

/** CLI引数 */
interface CliArgs {
  appDbPath: string;
  generatedDbPath: string;
}

/** コマンドライン引数をパース */
function parseArgs(argv: string[]): CliArgs {
  const args: CliArgs = {
    appDbPath: "./db/device_ai_toefl_coach.db",
    generatedDbPath: "./db/ai_toefl_coach.db",
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const value = argv[i + 1];
    switch (arg) {
      case "--app":
        if (value) {
          args.appDbPath = value;
          i++;
        }
        break;
      case "--gen":
        if (value) {
          args.generatedDbPath = value;
          i++;
        }
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

/** ヘルプを表示 */
function printHelp(): void {
  console.log(`
DBマージタスク - 生成した問題DBをアプリのRoom DBにマージする

使い方:
  npm run merge -- [オプション]

オプション:
  --app <path>  アプリのRoom DB（全テーブルを持つ）のパス (デフォルト: ./db/device_ai_toefl_coach.db)
  --gen <path>  生成した問題DBのパス (デフォルト: ./db/ai_toefl_coach.db)
  --help, -h    このヘルプを表示

例:
  npm run merge
  npm run merge -- --app ./db/device_ai_toefl_coach.db --gen ./db/ai_toefl_coach.db
`);
}

/** メイン処理 */
function main(): void {
  const args = parseArgs(process.argv.slice(2));

  console.log("=== DBマージタスク ===");
  console.log(`アプリDB: ${args.appDbPath}`);
  console.log(`生成DB: ${args.generatedDbPath}`);
  console.log("");

  mergeDb(args.appDbPath, args.generatedDbPath);

  console.log("");
  console.log("マージが完了しました。");
}

main();
