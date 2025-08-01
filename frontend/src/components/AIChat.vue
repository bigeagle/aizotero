<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- 对话历史 -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div
        v-for="(message, index) in conversation"
        :key="index"
        :class="message.role === 'user' ? 'text-right' : 'text-left'"
      >
        <div
          :class="message.role === 'user'
            ? 'bg-blue-500 text-white inline-block'
            : 'bg-white inline-block'"
          class="px-4 py-2 rounded-lg max-w-xs sm:max-w-md lg:max-w-lg"
        >
          <div class="whitespace-pre-wrap">{{ message.content }}</div>
          <div class="text-xs opacity-70 mt-1">{{ formatTime(message.timestamp) }}</div>
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

    <!-- 快速提示 -->
    <div class="p-3 bg-white border-t border-gray-200">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="prompt in quickPrompts"
          :key="prompt.key"
          @click="useQuickPrompt(prompt)"
          :disabled="isLoading"
          class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ prompt.label }}
        </button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="p-4 bg-white border-t border-gray-200">
      <div class="flex space-x-2">
        <textarea
          v-model="currentQuestion"
          @keydown="handleKeydown"
          placeholder="关于这篇论文的问题..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows="1"
          :disabled="isLoading || !isConfigured"
        />
        <button
          @click="sendQuestion"
          :disabled="isLoading || !currentQuestion.trim() || !isConfigured"
          class="px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      <div class="flex justify-between items-center mt-2 text-sm text-gray-500">
        <div>
          <span v-if="tokenUsage > 0">已用 token: {{ tokenUsage }}</span>
        </div>
        <div class="flex space-x-2">
          <button
            @click="clearConversation"
            class="text-blue-600 hover:text-blue-800"
            :disabled="conversation.length === 0"
          >
            清空对话
          </button>
          <button
            @click="exportConversation"
            class="text-blue-600 hover:text-blue-800"
            :disabled="conversation.length === 0"
          >
            导出
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue';
import { useAIStore } from '@/stores/aiStore';
import { AIService } from '@/services/aiService';

interface Props {
  paperId: string;
}

const props = defineProps<Props>();

const aiStore = useAIStore();
const aiService = new AIService(aiStore.config);

const currentQuestion = ref('');
const chatContainer = ref<HTMLElement | null>(null);

const conversation = computed(() => aiStore.conversation);
const isLoading = computed(() => aiStore.isLoading);
const error = computed(() => aiStore.error);
const isConfigured = computed(() => aiStore.isConfigured);
const tokenUsage = computed(() => aiStore.tokenUsage);

const quickPrompts = [
  { key: 'summary', label: '总结论文', prompt: '请用中文简要总结这篇论文的主要内容和贡献' },
  { key: 'methods', label: '研究方法', prompt: '这篇论文的研究方法是什么？有什么创新点？' },
  { key: 'contribution', label: '主要贡献', prompt: '这篇论文的主要贡献有哪些？对相关领域有什么影响？' },
  { key: 'limitations', label: '局限性', prompt: '这篇论文有哪些局限性？作者提到了哪些未来工作？' },
  { key: 'related', label: '相关研究', prompt: '这篇论文与哪些相关研究有关联？解决了什么问题？' },
  { key: 'practical', label: '实际应用', prompt: '这项研究在实际中有哪些应用场景？' }
];

// 初始化 AI 服务
async function initializeAI() {
  if (!isConfigured.value) return;

  try {
    aiStore.setLoading(true);
    aiStore.setError(null);

    // 获取论文内容
    const response = await fetch(`/api/v1/papers/${props.paperId}/markdown`);
    if (!response.ok) throw new Error('获取论文内容失败');

    const data = await response.json();

    // 初始化论文上下文
    const paperContext = {
      paperId: props.paperId,
      markdown: data.markdown,
      title: data.title || '',
      authors: data.authors || []
    };

    aiStore.setCurrentPaper(paperContext);
    await aiService.initializeWithPaper(paperContext);

  } catch (err) {
    aiStore.setError(err instanceof Error ? err.message : '未知错误');
  } finally {
    aiStore.setLoading(false);
  }
}

// 发送问题
async function sendQuestion() {
  if (!currentQuestion.value.trim() || !isConfigured.value) return;

  const question = currentQuestion.value.trim();
  currentQuestion.value = '';

  try {
    aiStore.setLoading(true);
    aiStore.setError(null);

    aiStore.addMessage({
      role: 'user',
      content: question,
      timestamp: new Date()
    });

    let responseContent = '';
    let assistantMessageIndex = -1;

    await aiService.chatWithPaper(
      question,
      (chunk) => {
        responseContent += chunk;

        // 更新现有的 assistant 消息
        if (assistantMessageIndex >= 0 && assistantMessageIndex < aiStore.conversation.length) {
          aiStore.conversation[assistantMessageIndex].content = responseContent;
          // 触发响应式更新
          aiStore.conversation.splice(assistantMessageIndex, 1, aiStore.conversation[assistantMessageIndex]);
        }
      },
      () => {
        // 响应开始时创建空的 assistant 消息
        const newMessage = {
          role: 'assistant' as const,
          content: '',
          timestamp: new Date()
        };
        aiStore.addMessage(newMessage);
        assistantMessageIndex = aiStore.conversation.length - 1;
      }
    );

  } catch (err) {
    aiStore.setError(err instanceof Error ? err.message : '发送消息失败');
  } finally {
    aiStore.setLoading(false);
  }
}

// 使用快速提示
function useQuickPrompt(prompt: any) {
  currentQuestion.value = prompt.prompt;
  sendQuestion();
}

// 处理键盘事件
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendQuestion();
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

  const content = aiStore.conversation
    .map(msg => `**${msg.role.toUpperCase()}**: ${msg.content}`)
    .join('\n\n');

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
    minute: '2-digit'
  });
}

// 自动滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
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

// 初始化
initializeAI();
</script>

<style scoped>
textarea:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

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
