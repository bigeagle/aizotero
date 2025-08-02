<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h3 class="text-lg font-semibold mb-4 text-gray-900">AI 配置</h3>

    <div class="space-y-4">
      <!-- API 密钥 -->
      <div>
        <label class="block text-sm font-medium mb-1 text-gray-700">API 密钥</label>
        <div class="relative">
          <input
            v-model="config.apiKey"
            :type="showApiKey ? 'text' : 'password'"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="sk-..."
            @input="updateConfig"
          />
          <button
            type="button"
            @click="showApiKey = !showApiKey"
            class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            <span v-if="showApiKey">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L5.636 5.636m9.546 9.546l4.242 4.242M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <span v-else>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </span>
          </button>
        </div>
      </div>

      <!-- 服务地址 -->
      <div>
        <label class="block text-sm font-medium mb-1 text-gray-700">服务地址</label>
        <input
          v-model="config.baseUrl"
          type="url"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="https://api.openai.com/v1"
          @input="updateConfig"
        />
      </div>

      <!-- 模型选择 -->
      <div>
        <label class="block text-sm font-medium mb-1 text-gray-700">模型</label>
        <select
          v-model="config.model"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          @change="updateConfig"
          :disabled="!isConfigured || models.length === 0"
        >
          <option v-if="models.length === 0" value="">请先连接获取模型</option>
          <option v-for="model in models" :key="model.id" :value="model.id">
            {{ model.id }}
          </option>
        </select>
      </div>

      <!-- 高级设置 -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">最大 Token</label>
          <input
            v-model.number="config.maxTokens"
            type="number"
            min="100"
            max="8000"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            @input="updateConfig"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">温度</label>
          <input
            v-model.number="config.temperature"
            type="number"
            min="0"
            max="2"
            step="0.1"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            @input="updateConfig"
          />
        </div>
      </div>

      <!-- 状态显示 -->
      <div class="mt-4 p-3 bg-gray-50 rounded-md">
        <div class="text-sm text-gray-600 space-y-1">
          <div>状态：{{ isConfigured ? '✅ 已配置' : '❌ 需要配置' }}</div>
          <div v-if="tokenUsage > 0">已用 token：{{ tokenUsage }}</div>
        </div>
      </div>

      <!-- 测试按钮 -->
      <div class="mt-4 flex space-x-2">
        <button
          @click="testConnection"
          :disabled="!isConfigured || testing"
          class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600"
        >
          {{ testing ? '测试中...' : '测试连接' }}
        </button>
        <button
          @click="clearConfig"
          class="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
        >
          清除配置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAIStore } from '@/stores/aiStore';

const aiStore = useAIStore();
const showApiKey = ref(false);
const testing = ref(false);
const models = ref<Array<{id: string, object: string, owned_by: string}>>([]);

const config = computed(() => aiStore.config);
const isConfigured = computed(() => aiStore.isConfigured);
const tokenUsage = computed(() => aiStore.tokenUsage);

function updateConfig() {
  aiStore.updateConfig({
    apiKey: config.value.apiKey,
    baseUrl: config.value.baseUrl,
    model: config.value.model,
    maxTokens: config.value.maxTokens,
    temperature: config.value.temperature
  });
}

async function fetchModels() {
  if (!config.value.apiKey || !config.value.baseUrl) {
    models.value = [];
    return;
  }

  try {
    const response = await fetch(`${config.value.baseUrl}/models`, {
      headers: {
        'Authorization': `Bearer ${config.value.apiKey}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      models.value = (data.data || []).sort((a: any, b: any) => a.id.localeCompare(b.id));
    } else {
      console.error('获取模型失败:', response.status);
      models.value = [];
    }
  } catch (error) {
    console.error('获取模型错误:', error);
    models.value = [];
  }
}

async function testConnection() {
  if (!config.value.apiKey) {
    alert('请先输入 API 密钥');
    return;
  }

  testing.value = true;
  try {
    const response = await fetch(`${config.value.baseUrl}/models`, {
      headers: {
        'Authorization': `Bearer ${config.value.apiKey}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      models.value = (data.data || []).sort((a: any, b: any) => a.id.localeCompare(b.id));

      if (models.value.length > 0 && !config.value.model) {
        // 自动选择第一个可用模型
        aiStore.updateConfig({
          ...config.value,
          model: models.value[0].id
        });
      }

      alert(`✅ 连接成功！发现 ${models.value.length} 个可用模型`);
    } else {
      alert(`❌ 连接失败: ${response.status} ${response.statusText}`);
      models.value = [];
    }
  } catch (error) {
    alert(`❌ 网络错误: ${error}`);
    models.value = [];
  } finally {
    testing.value = false;
  }
}

function clearConfig() {
  if (confirm('确定要清除所有 AI 配置吗？')) {
    aiStore.updateConfig({
      apiKey: '',
      baseUrl: 'https://api.openai.com/v1',
      model: 'gpt-3.5-turbo',
      maxTokens: 2000,
      temperature: 0.7
    });
    models.value = [];
  }
}

// 监听配置变化，自动获取模型
watch(() => [config.value.apiKey, config.value.baseUrl], ([newApiKey, newBaseUrl]) => {
  if (newApiKey && newBaseUrl) {
    fetchModels();
  } else {
    models.value = [];
  }
}, { immediate: true });

// 组件挂载时获取模型
onMounted(() => {
  if (config.value.apiKey && config.value.baseUrl) {
    fetchModels();
  }
});
</script>

<style scoped>
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>
