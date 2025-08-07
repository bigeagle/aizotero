<template>
  <div class="space-y-4">
    <div class="flex gap-2">
      <input
        v-model="inputText"
        type="text"
        placeholder="输入 arXiv ID 或 URL (如: 2401.12345 或 https://arxiv.org/abs/2401.12345)"
        class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        @keyup.enter="loadArxivPaper"
      />
      <button
        @click="loadArxivPaper"
        :disabled="!inputText || loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? '加载中...' : '加载论文' }}
      </button>
    </div>

    <!-- 缓存状态 -->
    <div v-if="cacheInfo" class="text-sm text-gray-600 space-y-1">
      <div class="flex items-center gap-2">
        <span>PDF缓存: {{ cacheInfo.pdf_cached ? '已缓存' : '未缓存' }}</span>
        <span v-if="cacheInfo.pdf_cached" class="text-green-600">
          ({{ (cacheInfo.pdf_size / 1024 / 1024).toFixed(1) }} MB)
        </span>
      </div>
      <div>元数据缓存: {{ cacheInfo.metadata_cached ? '已缓存' : '未缓存' }}</div>
      <div v-if="cacheInfo.cache_age_hours > 0" class="text-gray-500">
        缓存年龄: {{ Math.round(cacheInfo.cache_age_hours) }} 小时
      </div>
    </div>

    <!-- 重复检查状态 -->
    <div v-if="checkingDuplicate" class="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">⏳ 正在检查Zotero库...</div>
    <div v-else-if="duplicateCheck" class="space-y-3">
      <div v-if="duplicateCheck.exists" class="text-green-600 bg-green-50 p-4 rounded-md">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center mb-2">
              <span class="text-lg mr-2">📚</span>
              <span class="font-medium">论文已存在于Zotero库中</span>
            </div>
            <p class="text-sm text-green-700">{{ duplicateCheck.title }}</p>
          </div>
          <button
            @click="openExistingPaper"
            class="ml-4 px-4 py-2 bg-white text-green-600 border border-green-300 rounded-md text-sm hover:bg-green-100 transition-colors"
          >
            阅读
          </button>
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-md">
      <p class="text-red-700">{{ error }}</p>
    </div>

    <!-- 论文预览 -->
    <div v-if="paper" class="p-4 border border-gray-200 rounded-md">
      <div class="flex items-start justify-between mb-3">
        <h3 class="text-lg font-semibold flex-1 mr-4">{{ paper.title }}</h3>
        <div class="flex flex-col gap-2">
          <button
            @click="openReader"
            class="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 whitespace-nowrap"
          >
            开始阅读
          </button>
        </div>
      </div>
      <p class="text-sm text-gray-600">作者: {{ paper.authors }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { arxivService } from '../services/arxivService';
import type { ArxivPaper, CacheInfo, DuplicateCheckResult } from '../services/arxivService';

const props = defineProps<{
  modelValue?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'loaded', paper: ArxivPaper): void;
  (e: 'read', paper: ArxivPaper): void;
  (e: 'duplicate-check', result: DuplicateCheckResult): void;
}>();

const router = useRouter();
const inputText = ref(props.modelValue || '');
const loading = ref(false);
const paper = ref<ArxivPaper | null>(null);
const cacheInfo = ref<CacheInfo | null>(null);
const duplicateCheck = ref<DuplicateCheckResult | null>(null);
const checkingDuplicate = ref(false);
const error = ref('');

// 提取arXiv ID的函数
const extractArxivId = (input: string): string | null => {
  const trimmed = input.trim();

  // 匹配arXiv ID格式：2401.12345 或 2401.12345v1
  const arxivIdRegex = /(\d{4}\.\d{4,5}(?:v\d+)?)/;

  // 匹配URL中的arXiv ID
  const urlRegex = /(?:abs|pdf)\/(\d{4}\.\d{4,5}(?:v\d+)?)/;

  let match = trimmed.match(arxivIdRegex);
  if (match) {
    return match[1];
  }

  match = trimmed.match(urlRegex);
  if (match) {
    return match[1];
  }

  return null;
};

// 检查论文是否已存在于Zotero库中
const checkDuplicateInZotero = async (arxivId: string) => {
  if (!arxivId) return;

  checkingDuplicate.value = true;
  try {
    const result = await arxivService.checkExistenceInZotero(arxivId);
    duplicateCheck.value = result;
    emit('duplicate-check', result);
  } catch (e) {
    console.error('检查重复失败:', e);
    duplicateCheck.value = { exists: false, error: '检查失败' };
  } finally {
    checkingDuplicate.value = false;
  }
};

// 监听输入变化，更新缓存信息
watch(
  inputText,
  async (newText) => {
    emit('update:modelValue', newText);

    const extractedId = extractArxivId(newText);
    if (extractedId) {
      try {
        cacheInfo.value = await arxivService.getCacheInfo(extractedId);
        // 自动检查重复
        await checkDuplicateInZotero(extractedId);
      } catch {
        cacheInfo.value = null;
        duplicateCheck.value = null;
      }
    } else {
      cacheInfo.value = null;
      duplicateCheck.value = null;
    }
  },
  { immediate: true }
);

const loadArxivPaper = async () => {
  if (!inputText.value.trim()) return;

  loading.value = true;
  error.value = '';
  paper.value = null;

  const extractedId = extractArxivId(inputText.value);
  if (!extractedId) {
    error.value = '无效的 arXiv ID 或 URL 格式';
    loading.value = false;
    return;
  }

  try {
    const data = await arxivService.getPaper(extractedId);
    paper.value = data;
    emit('loaded', data);
    // 确保重复检查完成
    await checkDuplicateInZotero(extractedId);
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载论文失败';
  } finally {
    loading.value = false;
  }
};

const openReader = () => {
  if (paper.value) {
    router.push(`/read/arxiv/${paper.value.id}`);
    // 通知父组件关闭popup
    emit('read', paper.value);
  }
};

const openExistingPaper = () => {
  if (duplicateCheck.value?.item_id) {
    router.push(`/read/zotero/${duplicateCheck.value.item_id}`);
    // 通知父组件关闭popup
    emit('read', {
      id: duplicateCheck.value.item_id,
      title: duplicateCheck.value.title || '',
      authors: '',
      abstract: '',
      tags: [],
      has_pdf: false,
    } as ArxivPaper);
  }
};

// 暴露给父组件的方法
const focusInput = () => {
  const inputEl = document.querySelector('input[type="text"]') as HTMLInputElement;
  if (inputEl) {
    inputEl.focus();
  }
};

const clearInput = () => {
  inputText.value = '';
  paper.value = null;
  cacheInfo.value = null;
  error.value = '';
};

// 将方法暴露给父组件
defineExpose({
  focusInput,
  clearInput,
});
</script>
