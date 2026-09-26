// AI APIクライアント
// OpenAI互換API（OpenAI / DeepSeek）とGemini APIに対応

import type { AiProvider } from "./types.js";

/** 環境設定 */
export interface AiConfig {
  provider: AiProvider;
  apiKey: string;
  baseUrl: string;
  model: string;
}

/** チャットメッセージ */
export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

/** 環境変数からAI設定を読み込む */
export function loadAiConfig(): AiConfig {
  const provider = (process.env.AI_PROVIDER ?? "deepseek") as AiProvider;

  switch (provider) {
    case "openai":
      return {
        provider,
        apiKey: requireEnv("OPENAI_API_KEY"),
        baseUrl: process.env.OPENAI_BASE_URL ?? "https://api.openai.com/v1",
        model: process.env.OPENAI_MODEL ?? "gpt-4o-mini",
      };
    case "gemini":
      return {
        provider,
        apiKey: requireEnv("GEMINI_API_KEY"),
        baseUrl: "https://generativelanguage.googleapis.com",
        model: process.env.GEMINI_MODEL ?? "gemini-2.0-flash",
      };
    case "deepseek":
    default:
      return {
        provider: "deepseek",
        apiKey: requireEnv("DEEPSEEK_API_KEY"),
        baseUrl: process.env.DEEPSEEK_BASE_URL ?? "https://api.deepseek.com",
        model: process.env.DEEPSEEK_MODEL ?? "deepseek-chat",
      };
  }
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`環境変数 ${name} が設定されていません。.env ファイルを確認してください。`);
  }
  return value;
}

/**
 * AIにチャットリクエストを送信し、JSONオブジェクトを返す。
 * プロバイダーに応じてエンドポイント・リクエスト形式を切り替える。
 */
export async function chatJson(
  config: AiConfig,
  messages: ChatMessage[],
  maxTokens = 2000
): Promise<unknown> {
  if (config.provider === "gemini") {
    return chatGemini(config, messages, maxTokens);
  }
  return chatOpenAiCompatible(config, messages, maxTokens);
}

/** OpenAI互換API（OpenAI / DeepSeek） */
async function chatOpenAiCompatible(
  config: AiConfig,
  messages: ChatMessage[],
  maxTokens: number
): Promise<unknown> {
  const url = `${config.baseUrl.replace(/\/$/, "")}/chat/completions`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({
      model: config.model,
      messages,
      response_format: { type: "json_object" },
      max_tokens: maxTokens,
      temperature: 0.7,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`AI APIエラー (${response.status}): ${body}`);
  }

  const data = (await response.json()) as {
    choices?: { message?: { content?: string } }[];
  };
  const content = data.choices?.[0]?.message?.content;
  if (!content) {
    throw new Error("AI APIが空のレスポンスを返しました。");
  }
  return parseJson(content);
}

/** Gemini API */
async function chatGemini(
  config: AiConfig,
  messages: ChatMessage[],
  maxTokens: number
): Promise<unknown> {
  // Geminiはsystemプロンプトを先頭のuserメッセージに含める
  const systemPrompt = messages.find((m) => m.role === "system")?.content ?? "";
  const userMessages = messages.filter((m) => m.role !== "system");
  const combinedUserContent = [
    systemPrompt ? `[システム指示]\n${systemPrompt}\n\n` : "",
    ...userMessages.map((m) => m.content),
  ].join("\n");

  const url = `${config.baseUrl}/v1beta/models/${config.model}:generateContent?key=${config.apiKey}`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [
        {
          parts: [{ text: combinedUserContent }],
        },
      ],
      generationConfig: {
        maxOutputTokens: maxTokens,
        temperature: 0.7,
        responseMimeType: "application/json",
      },
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Gemini APIエラー (${response.status}): ${body}`);
  }

  const data = (await response.json()) as {
    candidates?: { content?: { parts?: { text?: string }[] } }[];
  };
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) {
    throw new Error("Gemini APIが空のレスポンスを返しました。");
  }
  return parseJson(text);
}

/** レスポンスからJSONを抽出してパースする */
function parseJson(content: string): unknown {
  // コードフェンスや余分なテキストを除去
  const cleaned = content
    .replace(/```json/gi, "")
    .replace(/```/g, "")
    .trim();
  try {
    return JSON.parse(cleaned);
  } catch {
    // JSONオブジェクトを探す
    const start = cleaned.indexOf("{");
    const end = cleaned.lastIndexOf("}");
    if (start >= 0 && end > start) {
      const candidate = cleaned.slice(start, end + 1);
      try {
        return JSON.parse(candidate);
      } catch {
        // 切り詰められたJSONを修復して再試行する
        return repairTruncatedJson(candidate);
      }
    }
    throw new Error(`AI APIが有効なJSONを返しませんでした: ${content}`);
  }
}

/**
 * 切り詰められた（不完全な）JSONを修復してパースする。
 * 例: 配列の途中で切れた場合、閉じ括弧を補完する。
 */
function repairTruncatedJson(content: string): unknown {
  // 配列の途中で切れた場合: 最後の要素を閉じて配列を閉じる
  const arrayMatch = content.match(/^(\s*\{[^]*?)\[([^]*)$/);
  if (arrayMatch) {
    const prefix = arrayMatch[1];
    const arrayBody = arrayMatch[2];
    // 最後の要素を閉じる
    const repaired = `${prefix}[${arrayBody.replace(/,\s*$/, "")}]}`;
    try {
      return JSON.parse(repaired);
    } catch {
      // さらに、オブジェクトの途中で切れた場合は閉じ括弧を補完
      const objRepaired = `${prefix}[${arrayBody.replace(/,\s*$/, "")}]}`;
      try {
        return JSON.parse(objRepaired);
      } catch {
        // 最後の手段: 閉じ括弧を追加
        const finalRepair = `${content.replace(/,\s*$/, "")}]}`;
        try {
          return JSON.parse(finalRepair);
        } catch {
          throw new Error(`AI APIが有効なJSONを返しませんでした: ${content}`);
        }
      }
    }
  }

  // オブジェクトの途中で切れた場合: 閉じ括弧を補完
  const objRepaired = `${content.replace(/,\s*$/, "")}}`;
  try {
    return JSON.parse(objRepaired);
  } catch {
    throw new Error(`AI APIが有効なJSONを返しませんでした: ${content}`);
  }
}

