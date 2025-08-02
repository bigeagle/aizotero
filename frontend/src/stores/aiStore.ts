import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type {
  AIService,
  LLMConfig,
  ChatMessage,
  PaperContext,
} from "@/services/aiService";

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
      return total + Math.ceil(msg.content.length / 4);
    }, 0);
  });

  const isConfigured = computed(() => {
    return (
      config.value.apiKey.trim() !== "" &&
      config.value.baseUrl.trim() !== "" &&
      config.value.model.trim() !== ""
    );
  });

  function updateConfig(newConfig: Partial<LLMConfig>) {
    config.value = { ...config.value, ...newConfig };
    localStorage.setItem("llm_api_key", config.value.apiKey);
    localStorage.setItem("llm_base_url", config.value.baseUrl);
    localStorage.setItem("llm_model", config.value.model);
  }

  function setCurrentPaper(paper: PaperContext) {
    currentPaper.value = paper;
    clearConversation();
  }

  function addMessage(message: ChatMessage) {
    conversation.value.push(message);
    // 限制历史长度，避免内存泄漏
    if (conversation.value.length > 50) {
      conversation.value = conversation.value.slice(-20);
    }
  }

  function clearConversation() {
    conversation.value = [];
    error.value = null;
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading;
  }

  function setError(err: string | null) {
    error.value = err;
  }

  return {
    config,
    currentPaper,
    conversation,
    isLoading,
    error,
    tokenUsage,
    isConfigured,
    updateConfig,
    setCurrentPaper,
    addMessage,
    clearConversation,
    setLoading,
    setError,
  };
});
