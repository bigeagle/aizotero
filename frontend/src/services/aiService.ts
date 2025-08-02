/**
 * AI 论文阅读服务
 * 纯前端架构，直接对接 OpenAI compatible API
 */

export interface LLMConfig {
  apiKey: string;
  baseUrl: string;
  model: string;
  maxTokens: number;
  temperature: number;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

export interface PaperContext {
  paperId: string;
  markdown: string;
  title: string;
  authors: string[];
}

export class AIService {
  private config: LLMConfig;
  private conversationHistory: ChatMessage[] = [];
  private currentPaper: PaperContext | null = null;

  constructor(config: LLMConfig) {
    this.config = config;
  }

  setConfig(config: LLMConfig) {
    this.config = config;
  }

  async initializeWithPaper(paperContext: PaperContext) {
    this.currentPaper = paperContext;
    this.conversationHistory = [
      {
        role: "system",
        content: `你是学术论文阅读助手。默认用 markdown 格式回答问题，但不要使用表格，数学公式使用 $LaTeX$ 格式。`,
        timestamp: new Date(),
      },
    ];
  }

  private buildMessages(
    history: ChatMessage[],
  ): Array<{ role: string; content: string }> {
    const messages = [...this.conversationHistory];

    // 只在第一轮包含完整 PDF 内容
    if (this.conversationHistory.length === 1) {
      messages.push({
        role: "user",
        content: `论文全文内容：\n${this.currentPaper?.markdown}`,
        timestamp: new Date(),
      });
    }

    for (const msg of history) {
      // 过滤掉系统消息
      if (msg.role !== "system") {
        messages.push({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
        });
      }
    }

    // 转换为 OpenAI 格式
    return messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));
  }

  async chatWithPaper(
    history: ChatMessage[],
    onChunk: (chunk: string) => void,
    onResponse?: () => void,
  ): Promise<void> {
    if (!this.currentPaper) {
      throw new Error("请先初始化论文上下文");
    }

    try {
      const messages = this.buildMessages(history);

      const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.config.apiKey}`,
        },
        body: JSON.stringify({
          model: this.config.model,
          messages,
          stream: true,
          max_tokens: this.config.maxTokens,
          temperature: this.config.temperature,
        }),
      });

      if (!response.ok) {
        throw new Error(`API 错误: ${response.status}`);
      }

      // 通知开始响应，用于创建初始消息
      if (onResponse) {
        onResponse();
      }

      let fullResponse = "";

      if (!response.body) {
        throw new Error("Response body is null");
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") return;

            try {
              const parsed = JSON.parse(data);
              const content = parsed.choices?.[0]?.delta?.content;
              if (content) {
                fullResponse += content;
                onChunk(content);
              }
            } catch (e) {
              console.warn("Parse error:", e);
            }
          }
        }
      }

      // 保存对话历史
      this.conversationHistory.push(
        {
          role: "user",
          content: messages[messages.length - 1]?.content || "",
          timestamp: new Date(),
        },
        { role: "assistant", content: fullResponse, timestamp: new Date() },
      );
    } catch (error) {
      console.error("Chat error:", error);
      throw error;
    }
  }

  clearHistory() {
    this.conversationHistory = this.conversationHistory.slice(0, 1);
  }

  getConversationHistory(): ChatMessage[] {
    return this.conversationHistory.slice(1); // 排除系统消息
  }

  getCurrentPaper(): PaperContext | null {
    return this.currentPaper;
  }
}

// 全局实例
export const aiService = new AIService({
  apiKey: localStorage.getItem("llm_api_key") || "",
  baseUrl: localStorage.getItem("llm_base_url") || "https://api.openai.com/v1",
  model: localStorage.getItem("llm_model") || "gpt-3.5-turbo",
  maxTokens: 2000,
  temperature: 0.7,
});
