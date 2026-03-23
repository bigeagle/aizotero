<template>
  <div class="bg-white shrink-0 border-t border-gray-200">
    <div class="px-3 pt-3 pb-1">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="prompt in quickPrompts"
          :key="prompt.key"
          @click="submitQuestion(prompt.prompt)"
          :disabled="isLoading"
          class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ prompt.label }}
        </button>
      </div>
    </div>

    <div class="p-3">
      <div class="flex space-x-2">
        <textarea
          v-model="currentQuestion"
          @keydown="handleKeydown"
          @compositionstart="isComposing = true"
          @compositionend="isComposing = false"
          placeholder="关于这篇论文的问题..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows="1"
          :disabled="isLoading || !isConfigured"
        />
        <button
          @click="submitQuestion(currentQuestion)"
          :disabled="isLoading || !currentQuestion.trim() || !isConfigured"
          class="px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      <div class="flex justify-between items-center mt-2 text-sm text-gray-500">
        <div>
          <span v-if="tokenUsage > 0">已用 token: {{ tokenUsage }}</span>
        </div>
        <div class="flex space-x-2">
          <button @click="emit('clear')" class="text-blue-600 hover:text-blue-800" :disabled="!hasConversation">
            清空对话
          </button>
          <button @click="emit('export')" class="text-blue-600 hover:text-blue-800" :disabled="!hasConversation">
            导出
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface QuickPrompt {
  key: string;
  label: string;
  prompt: string;
}

const props = defineProps<{
  isLoading: boolean;
  isConfigured: boolean;
  tokenUsage: number;
  hasConversation: boolean;
  quickPrompts: QuickPrompt[];
}>();

const emit = defineEmits<{
  submit: [question: string];
  clear: [];
  export: [];
}>();

const currentQuestion = ref('');
const isComposing = ref(false);

function submitQuestion(question: string) {
  const normalizedQuestion = question.trim();

  if (!normalizedQuestion || props.isLoading || !props.isConfigured) {
    return;
  }

  currentQuestion.value = '';
  emit('submit', normalizedQuestion);
}

function handleKeydown(event: KeyboardEvent) {
  if (isComposing.value || event.isComposing || event.keyCode === 229) {
    return;
  }

  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    submitQuestion(currentQuestion.value);
  }
}
</script>
