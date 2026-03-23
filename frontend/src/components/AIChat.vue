<template>
  <div class="flex flex-col h-full bg-gray-50 max-h-full">
    <!-- 配置提示 -->
    <div v-if="!isConfigured" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
      <div class="max-w-md">
        <div class="text-6xl mb-4">🤖</div>
        <h3 class="text-xl font-semibold text-gray-800 mb-2">AI 助手未配置</h3>
        <p class="text-gray-600 mb-6">请先配置 AI 服务信息，才能开始与论文对话。</p>
        <button
          @click="$emit('show-config')"
          class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200 font-medium"
        >
          立即配置 AI
        </button>
      </div>
    </div>

    <!-- 对话历史 -->
    <div v-else ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth min-h-0">
      <div
        v-for="(message, index) in conversation"
        :key="index"
        :class="message.role === 'user' ? 'text-right' : 'text-left'"
      >
        <div
          :class="message.role === 'user' ? 'bg-blue-500 text-white inline-block' : 'bg-white inline-block'"
          class="px-4 py-2 rounded-lg"
        >
          <div
            v-if="message.role === 'assistant'"
            class="text-sm max-w-none [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:mb-2 [&>ol]:list-decimal [&>ol]:pl-5 [&>ol]:mb-2 [&>h1]:text-lg [&>h1]:font-bold [&>h1]:mb-2 [&>h2]:text-base [&>h2]:font-bold [&>h2]:mb-2 [&>h3]:text-sm [&>h3]:font-bold [&>h3]:mb-1 [&>blockquote]:border-l-4 [&>blockquote]:border-gray-300 [&>blockquote]:pl-4 [&>blockquote]:italic [&>blockquote]:mb-2 [&>code]:bg-gray-100 [&>code]:px-1 [&>code]:py-0.5 [&>code]:rounded [&>code]:text-sm [&>pre]:bg-gray-50 [&>pre]:p-2 [&>pre]:rounded [&>pre]:overflow-x-auto [&>pre]:mb-2 [&>a]:text-blue-600 [&>a]:hover:text-blue-800 [&>a]:underline"
            v-html="renderMarkdown(message.content)"
          ></div>
          <div v-else class="whitespace-pre-wrap">{{ message.content }}</div>
          <div class="text-xs opacity-70 mt-2">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <div v-if="isLoading" class="text-center">
        <div class="inline-flex items-center space-x-2 text-gray-500">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          <span>AI 思考中...</span>
        </div>
      </div>

      <div v-if="error" class="text-center text-red-500 bg-red-50 p-3 rounded-md">
        <p class="font-medium">{{ error }}</p>
        <button @click="clearError" class="text-sm underline">清除错误</button>
      </div>
    </div>

    <AIChatInput
      :is-loading="isLoading"
      :is-configured="isConfigured"
      :token-usage="tokenUsage"
      :has-conversation="conversation.length > 0"
      :quick-prompts="quickPrompts"
      @submit="sendQuestion"
      @clear="clearConversation"
      @export="exportConversation"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted } from 'vue';
import AIChatInput from '@/components/AIChatInput.vue';
import { useAIStore } from '@/stores/aiStore';
import { AIService } from '@/services/aiService';
import { zoteroService } from '@/services/zoteroService';
import { arxivService } from '@/services/arxivService';
import { marked } from 'marked';
import markedKatex from '@/utils/marked-katex-custom';
import 'katex/dist/katex.css';

interface Props {
  paperId: string;
  source?: 'zotero' | 'arxiv';
}

const props = defineProps<Props>();

const aiStore = useAIStore();
const aiService = new AIService(aiStore.config);

const chatContainer = ref<HTMLElement | null>(null);
const markdownCache = new Map<string, string>();
let scrollFrameId: number | null = null;

const markedWithKatex = marked.use(
  markedKatex({
    throwOnError: false,
    displayMode: false,
    nonStandard: true,
  })
);

const conversation = computed(() => aiStore.conversation);
const isLoading = computed(() => aiStore.isLoading);
const error = computed(() => aiStore.error);
const isConfigured = computed(() => aiStore.isConfigured);
const tokenUsage = computed(() => aiStore.tokenUsage);

const quickPrompts = [
  { key: 'summary', label: '总结论文', prompt: '深入解读这篇论文，不要使用表格。' },
  { key: 'methods', label: '研究方法', prompt: '这篇论文的研究方法是什么？有什么创新点？' },
  { key: 'contribution', label: '主要贡献', prompt: '这篇论文的主要贡献有哪些？对相关领域有什么影响？' },
  { key: 'limitations', label: '局限性', prompt: '这篇论文有哪些局限性？作者提到了哪些未来工作？' },
  { key: 'related', label: '相关研究', prompt: '这篇论文与哪些相关研究有关联？解决了什么问题？' },
  { key: 'practical', label: '实际应用', prompt: '这项研究在实际中有哪些应用场景？' },
];

// 初始化 AI 服务
async function initializeAI() {
  if (!isConfigured.value) {
    aiStore.setError('请先配置 AI 服务信息');
    return;
  }

  try {
    aiStore.clearConversation();
    aiStore.setLoading(true);
    aiStore.setError(null);

    // 获取论文内容
    let data;
    if (props.source === 'arxiv') {
      data = await arxivService.getMarkdown(props.paperId);
    } else {
      data = await zoteroService.getMarkdown(props.paperId);
    }

    // 初始化论文上下文
    const paperContext = {
      paperId: props.paperId,
      markdown: data.markdown,
    };

    aiStore.setCurrentPaper(paperContext);
    await aiService.initializeWithPaper(paperContext);

    loadConversation();
  } catch (err) {
    aiStore.setError(err instanceof Error ? err.message : '未知错误');
  } finally {
    aiStore.setLoading(false);
  }
}

// 发送问题
async function sendQuestion(question: string) {
  if (!question.trim() || !isConfigured.value) return;

  const normalizedQuestion = question.trim();

  try {
    aiStore.setLoading(true);
    aiStore.setError(null);

    aiStore.addMessage({
      role: 'user',
      content: normalizedQuestion,
      timestamp: new Date(),
    });

    let responseContent = '';
    let assistantMessageIndex = -1;

    await aiService.chatWithPaper(
      aiStore.conversation,
      (chunk) => {
        responseContent += chunk;

        // 更新现有的 assistant 消息
        if (assistantMessageIndex >= 0 && assistantMessageIndex < aiStore.conversation.length) {
          aiStore.conversation[assistantMessageIndex].content = responseContent;
        }
      },
      () => {
        // 响应开始时创建空的 assistant 消息
        const newMessage = {
          role: 'assistant' as const,
          content: '',
          timestamp: new Date(),
        };
        aiStore.addMessage(newMessage);
        assistantMessageIndex = aiStore.conversation.length - 1;
      }
    );

    // 自动保存
    saveConversation();
  } catch (err) {
    aiStore.setError(err instanceof Error ? err.message : '发送消息失败');
  } finally {
    aiStore.setLoading(false);
  }
}

// 清空对话
function clearConversation() {
  aiStore.clearConversation();
}

// 清除错误
function clearError() {
  aiStore.setError(null);
}

// 导出对话
function exportConversation() {
  if (aiStore.conversation.length === 0) return;

  const content = aiStore.conversation.map((msg) => `**${msg.role.toUpperCase()}**: ${msg.content}`).join('\n\n');

  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `conversation-${props.paperId}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// 格式化时间
function formatTime(timestamp: Date) {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// 配置 marked 支持 KaTeX
function renderMarkdown(content: string): string {
  if (!content.trim()) return '';

  const cachedHtml = markdownCache.get(content);
  if (cachedHtml) {
    return cachedHtml;
  }

  const renderedHtml = markedWithKatex.parse(content) as string;

  if (markdownCache.size > 200) {
    const oldestKey = markdownCache.keys().next().value;
    if (oldestKey) {
      markdownCache.delete(oldestKey);
    }
  }

  markdownCache.set(content, renderedHtml);
  return renderedHtml;
}

// 自动滚动到底部
function scrollToBottom() {
  if (scrollFrameId !== null) {
    return;
  }

  scrollFrameId = requestAnimationFrame(() => {
    scrollFrameId = null;

    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    });
  });
}

// 保存对话到后端数据库
async function saveConversation() {
  if (conversation.value.length === 0) return;

  try {
    const chatMessages = conversation.value.map((msg) => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp.toISOString(),
    }));

    const endpoint = `/api/v1/chat/${props.paperId}`;

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(chatMessages),
    });

    if (!response.ok) {
      throw new Error(`保存失败: ${response.status}`);
    }

    // console.log('对话已保存到后端');
  } catch (err) {
    console.error('保存对话失败:', err);
  }
}

// 从后端数据库加载对话
async function loadConversation() {
  // 清空当前对话
  aiStore.clearConversation();

  try {
    const endpoint = `/api/v1/chat/${props.paperId}`;

    const response = await fetch(endpoint);
    if (!response.ok) {
      if (response.status === 404) {
        // 没有找到聊天记录，这是正常的
        return;
      }
      throw new Error(`加载失败: ${response.status}`);
    }

    const data = await response.json();
    const chatMessages = data.chat || [];

    for (const msg of chatMessages) {
      aiStore.addMessage({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.timestamp),
      });
    }

    // console.log(`已加载 ${chatMessages.length} 条消息`);
  } catch (err) {
    console.error('加载对话失败:', err);
  }
}

// 监听对话变化
watch(() => aiStore.conversation, scrollToBottom, { deep: true });

// 监听配置变化
watch(
  () => aiStore.config,
  (newConfig) => {
    aiService.setConfig(newConfig);
  },
  { deep: true }
);

// paperId 变化时重新初始化 AI
watch(props, async () => {
  await nextTick();
  await initializeAI();
});

// 自动检查是否有保存的对话
onMounted(() => {
  // 初始化
  initializeAI();
});
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
