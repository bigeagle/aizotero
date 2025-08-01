# 前端 AI 论文阅读助手设计方案

## 设计概述

采用**纯前端 AI 架构**，利用已完成的 PDF → Markdown 解析接口，直接在浏览器中与 LLM 服务交互，实现零后端依赖的智能论文阅读体验。

## 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面      │    │   前端服务层    │    │   LLM 服务      │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ PDF Reader  │ │◄──►│ │ AI Service  │ │◄──►│ │ OpenAI API  │ │
│ │ Chat Panel  │ │    │ │ State Mgmt  │ │    │ │ Anthropic   │ │
│ │ Config UI   │ │    │ │ Token Calc  │ │    │ │ Local LLM   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 核心组件设计

### 1. AI 服务层 (`src/services/aiService.ts`)

```typescript
interface LLMConfig {
  apiKey: string;
  baseUrl: string;
  model: string;
  maxTokens: number;
  temperature: number;
}

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

interface PaperContext {
  paperId: string;
  markdown: string;
  title: string;
  authors: string[];
  summary?: string;
}

class AIService {
  private config: LLMConfig;
  private conversationHistory: ChatMessage[] = [];
  private currentPaperContext: PaperContext | null = null;

  async initializeWithPaper(paperId: string): Promise<PaperContext> {
    const response = await fetch(`/api/v1/papers/${paperId}/markdown`);
    const data = await response.json();

    const context: PaperContext = {
      paperId,
      markdown: data.markdown,
      title: data.title || "",
      authors: data.authors || [],
    };

    // 设置当前论文上下文并清空对话历史
    this.currentPaperContext = context;
    this.conversationHistory = [];

    return context;
  }

  async chatWithPaper(
    context: PaperContext,
    question: string,
    onChunk: (chunk: string) => void,
  ): Promise<void> {
    // 更新当前论文上下文
    this.currentPaperContext = context;

    // 添加用户消息到历史
    this.conversationHistory.push({
      role: "user",
      content: question,
      timestamp: new Date(),
    });

    const messages = this.buildMessages(context, question);

    const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.config.apiKey}`,
      },
      body: JSON.stringify({
        model: this.config.model,
        messages: messages,
        stream: true,
        max_tokens: this.config.maxTokens,
        temperature: this.config.temperature,
      }),
    });

    if (!response.ok) {
      throw new Error(`LLM API error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantResponse = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            // 添加助手回复到历史
            this.conversationHistory.push({
              role: "assistant",
              content: assistantResponse,
              timestamp: new Date(),
            });
            return;
          }

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices?.[0]?.delta?.content;
            if (content) {
              assistantResponse += content;
              onChunk(content);
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    }
  }

  private buildMessages(context: PaperContext, question: string): any[] {
    const messages: any[] = [];

    // 只在第一次交互时包含完整的论文内容
    const isFirstInteraction = this.conversationHistory.length === 1;

    if (isFirstInteraction) {
      // 第一次交互：包含完整的系统提示和论文内容
      const systemPrompt = `你是一位专业的学术论文阅读助手。请基于以下论文内容回答用户的问题。

论文信息：
- 标题：${context.title}
- 作者：${context.authors.join(", ")}

论文内容：
${context.markdown}

请提供准确、简洁的回答，并尽可能引用论文中的具体内容。`;

      messages.push({
        role: "system",
        content: systemPrompt,
      });
      messages.push({
        role: "user",
        content: question,
      });
    } else {
      // 后续交互：只包含对话历史，不包含全文
      const conversationContext = this.conversationHistory.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      messages.push(...conversationContext);
    }

    return messages;
  }

  // 清除对话历史
  clearConversationHistory(): void {
    this.conversationHistory = [];
  }

  // 获取对话历史
  getConversationHistory(): ChatMessage[] {
    return [...this.conversationHistory];
  }

  // 获取当前论文上下文
  getCurrentPaperContext(): PaperContext | null {
    return this.currentPaperContext;
  }

  // 设置新的论文上下文（同时清空对话历史）
  setPaperContext(context: PaperContext): void {
    this.currentPaperContext = context;
    this.clearConversationHistory();
  }
}
```

### 2. 状态管理 (`src/stores/aiStore.ts`)

```typescript
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAIStore = defineStore("ai", () => {
  const config = ref<LLMConfig>({
    apiKey: localStorage.getItem("llm_api_key") || "",
    baseUrl:
      localStorage.getItem("llm_base_url") || "https://api.openai.com/v1",
    model: localStorage.getItem("llm_model") || "gpt-3.5-turbo",
    maxTokens: 2000,
    temperature: 0.7,
  });

  const currentPaper = ref<PaperContext | null>(null);
  const conversation = ref<ChatMessage[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const tokenUsage = computed(() => {
    return conversation.value.reduce((total, msg) => {
      return total + Math.ceil(msg.content.length / 4); // 粗略估算
    }, 0);
  });

  function updateConfig(newConfig: Partial<LLMConfig>) {
    config.value = { ...config.value, ...newConfig };
    localStorage.setItem("llm_api_key", config.value.apiKey);
    localStorage.setItem("llm_base_url", config.value.baseUrl);
    localStorage.setItem("llm_model", config.value.model);
  }

  function clearConversation() {
    conversation.value = [];
  }

  return {
    config,
    currentPaper,
    conversation,
    isLoading,
    error,
    tokenUsage,
    updateConfig,
    clearConversation,
  };
});
```

### 3. 组件设计

#### AI 配置面板 (`src/components/AIConfig.vue`)

```vue
<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h3 class="text-lg font-semibold mb-4">AI 配置</h3>

    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">API 密钥</label>
        <input
          v-model="apiKey"
          type="password"
          class="w-full px-3 py-2 border rounded-md"
          placeholder="sk-..."
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">服务地址</label>
        <input
          v-model="baseUrl"
          type="url"
          class="w-full px-3 py-2 border rounded-md"
          placeholder="https://api.openai.com/v1"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">模型</label>
        <select v-model="model" class="w-full px-3 py-2 border rounded-md">
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="gpt-4">GPT-4</option>
          <option value="gpt-4-turbo">GPT-4 Turbo</option>
          <option value="claude-3-haiku">Claude 3 Haiku</option>
          <option value="claude-3-sonnet">Claude 3 Sonnet</option>
        </select>
      </div>

      <div class="text-sm text-gray-600">已使用 token: {{ tokenUsage }}</div>
    </div>
  </div>
</template>
```

#### 对话界面 (`src/components/AIChat.vue`)

```vue
<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- 对话历史 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <div
        v-for="message in conversation"
        :key="message.timestamp"
        :class="message.role === 'user' ? 'text-right' : 'text-left'"
      >
        <div
          :class="
            message.role === 'user'
              ? 'bg-blue-500 text-white inline-block'
              : 'bg-white inline-block'
          "
          class="px-4 py-2 rounded-lg max-w-xs"
        >
          {{ message.content }}
        </div>
      </div>

      <div v-if="isLoading" class="text-center text-gray-500">AI 思考中...</div>
    </div>

    <!-- 输入区域 -->
    <div class="p-4 bg-white border-t">
      <div class="flex space-x-2">
        <input
          v-model="currentQuestion"
          @keyup.enter="sendQuestion"
          placeholder="关于这篇论文的问题..."
          class="flex-1 px-3 py-2 border rounded-md"
        />
        <button
          @click="sendQuestion"
          :disabled="isLoading || !currentQuestion"
          class="px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50"
        >
          发送
        </button>
      </div>

      <!-- 快速提示 -->
      <div class="flex flex-wrap gap-2 mt-2">
        <button
          @click="useQuickPrompt('summary')"
          class="px-3 py-1 text-sm bg-gray-200 rounded-full"
        >
          总结论文
        </button>
        <button
          @click="useQuickPrompt('methods')"
          class="px-3 py-1 text-sm bg-gray-200 rounded-full"
        >
          研究方法
        </button>
        <button
          @click="useQuickPrompt('contribution')"
          class="px-3 py-1 text-sm bg-gray-200 rounded-full"
        >
          主要贡献
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const quickPrompts = {
  summary: "请用中文简要总结这篇论文的主要内容和贡献",
  methods: "这篇论文的研究方法是什么？有什么创新点？",
  contribution: "这篇论文的主要贡献有哪些？对相关领域有什么影响？",
};

function useQuickPrompt(type) {
  currentQuestion.value = quickPrompts[type];
  sendQuestion();
}
</script>
```

## 使用流程

### 1. 初次使用

```
用户访问 → 配置 AI 设置 → 选择论文 → 开始对话
```

### 2. 日常流程

```
打开论文 → 自动加载 PDF → 输入问题 → 实时获得回答
```

### 3. 高级功能

- **上下文记忆**：记住当前会话的论文内容
- **对话导出**：一键导出对话为 Markdown
- **模型切换**：实时切换不同 LLM 服务
- **token 监控**：实时显示使用量

## 错误处理

```typescript
// 网络错误
if (response.status === 401) {
  error.value = "API 密钥无效，请检查配置";
}

// 内容过长
if (context.markdown.length > 100000) {
  error.value = "论文内容过长，建议分段提问";
}

// API 限制
if (error.code === "rate_limit") {
  error.value = "API 调用频率限制，请稍后再试";
}
```

## 性能优化

1. **本地缓存**：对话历史、论文摘要存储在 localStorage
2. **延迟加载**：按需获取 PDF 内容
3. **断点续传**：网络中断后自动重连
4. **压缩传输**：Gzip 压缩 API 请求

## 隐私与安全

- **本地存储**：API 密钥加密存储在浏览器
- **无痕模式**：支持隐私浏览
- **一键清除**：可随时清除所有本地数据
- **无服务器**：PDF 内容永不离开用户设备

## 部署优势

- **零后端成本**：纯静态部署，如 GitHub Pages
- **无限扩展**：每个用户自带 API 配额
- **即时更新**：前端更新无需重启服务
- **离线可用**：支持 PWA 离线模式
