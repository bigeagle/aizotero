<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AIChat from '@/components/AIChat.vue';
import AIConfig from '@/components/AIConfig.vue';
import { zoteroService, type ZoteroPaper } from '@/services/zoteroService';
import { arxivService, type ArxivPaper } from '@/services/arxivService';

interface Props {
  source: 'zotero' | 'arxiv';
}

const props = defineProps<Props>();
const route = useRoute();
const router = useRouter();

// 统一 Paper 接口
interface Paper {
  id: string;
  title: string;
  authors: string;
  year?: string;
  journal?: string;
  abstract?: string;
  pdf_path?: string;
}

const paperId = route.params.id as string;

const paper = ref<Paper | null>(null);
const chatWidth = ref(600);
const isResizing = ref(false);
const showAIConfig = ref(false);
const loading = ref(true);

const pdfUrl = computed(() => {
  if (!paper.value?.pdf_path) return null;

  const id = route.params.id as string;
  if (props.source === 'arxiv') {
    return arxivService.getPdfURL(id);
  } else {
    return zoteroService.getPdfURL(id);
  }
});

async function fetchPaper() {
  loading.value = true;
  try {
    const id = route.params.id as string;
    let paperData: ZoteroPaper | ArxivPaper;

    if (props.source === 'arxiv') {
      paperData = await arxivService.getPaper(id);
    } else {
      paperData = await zoteroService.getPaper(id);
    }

    paper.value = {
      id: paperData.id,
      title: paperData.title,
      authors: paperData.authors,
      year: paperData.year,
      journal: paperData.journal,
      abstract: paperData.abstract,
      pdf_path: paperData.pdf_path,
    };
  } catch (error) {
    console.error('Failed to fetch paper:', error);
    paper.value = {
      id: paperId,
      title: '论文加载中...',
      authors: '未知作者',
    };
  } finally {
    loading.value = false;
  }
}

function startResize(e: MouseEvent) {
  isResizing.value = true;
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  document.addEventListener('mouseleave', stopResize);
  e.preventDefault();
}

function handleResize(e: MouseEvent) {
  if (!isResizing.value) return;
  const newWidth = window.innerWidth - e.clientX;
  chatWidth.value = Math.max(300, Math.min(800, newWidth));
}

function stopResize() {
  if (!isResizing.value) return;
  isResizing.value = false;
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
}

onMounted(() => {
  fetchPaper();
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
});
</script>

<template>
  <div class="h-screen w-full flex flex-col absolute inset-0 overflow-hidden">
    <div v-if="paper" class="flex-1 flex w-full h-full">
      <!-- 左侧：PDF阅读器 -->
      <div class="flex-1 bg-white p-4 overflow-hidden">
        <div class="h-full flex flex-col">
          <div class="flex items-center justify-between mb-4 px-2">
            <div class="flex items-center gap-2">
              <span v-if="loading" class="text-sm text-gray-500">
                {{ props.source === 'arxiv' ? 'arXiv' : 'Zotero' }} 加载中...
              </span>
              <h2 class="text-xl font-semibold">{{ paper.title }}</h2>
            </div>
            <button
              @click="router.push('/')"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200"
            >
              Home
            </button>
          </div>
          <div class="flex-1 border border-gray-300 rounded-lg bg-gray-50 overflow-hidden">
            <div class="w-full h-full flex flex-col items-center justify-center text-gray-500" v-if="!pdfUrl">
              <p class="text-lg mb-2">PDF文件不可用</p>
              <p class="text-sm">论文ID: {{ paper.id }}</p>
            </div>
            <iframe
              v-if="pdfUrl"
              :src="pdfUrl"
              class="w-full h-full border-none"
              :class="{ invisible: isResizing }"
              type="application/pdf"
            >
            </iframe>
          </div>
        </div>
      </div>

      <!-- 分割线 -->
      <div
        class="w-2 bg-gray-200 hover:bg-gray-300 cursor-col-resize flex items-center justify-center"
        @mousedown="startResize"
        :class="{ 'bg-blue-500': isResizing }"
      >
        <div class="w-1 h-8 bg-gray-400 rounded"></div>
      </div>

      <!-- 右侧：AI配置和对话 -->
      <div class="bg-white overflow-hidden flex flex-col h-full" :style="{ width: chatWidth + 'px' }">
        <!-- AI配置 -->
        <div class="p-4 border-b border-gray-200">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-lg font-semibold">AI 助手</h3>
            <button @click="showAIConfig = !showAIConfig" class="text-sm text-blue-600 hover:text-blue-800">
              {{ showAIConfig ? '隐藏配置' : '显示配置' }}
            </button>
          </div>
          <AIConfig v-if="showAIConfig" />
        </div>

        <!-- AI对话 -->
        <div class="flex-1 overflow-hidden">
          <AIChat :paper-id="paperId" :source="props.source" @show-config="showAIConfig = true" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 拖拽时的光标样式 */
.cursor-col-resize {
  cursor: col-resize;
}

.cursor-col-resize:active {
  cursor: col-resize !important;
}

/* 拖拽状态样式 */
.bg-blue-500 {
  transition: background-color 0.2s;
}
</style>
