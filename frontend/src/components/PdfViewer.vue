<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { PDFViewer } from '@embedpdf/vue-pdf-viewer';
import type { PDFViewerConfig } from '@embedpdf/vue-pdf-viewer';
import { usePdfNavigation } from '@/composables/usePdfNavigation';

export type SpreadModeLiteral = 'none' | 'odd' | 'even';

interface Props {
  src: string | null;
  spreadMode?: SpreadModeLiteral;
  disabledCategories?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  spreadMode: () => {
    try {
      const stored = localStorage.getItem('pdf-spread-mode');
      if (stored === 'none' || stored === 'odd' || stored === 'even') {
        return stored;
      }
    } catch {
      // ignore storage errors
    }
    return 'none';
  },
  disabledCategories: () => [
    'mode-annotate',
    'mode-shapes',
    'redaction',
    'print',
    'export',
    'stamp',
    'signature',
    'insert',
    'form',
    'document-open',
    'document-close',
  ],
});

const emit = defineEmits<{
  (e: 'ready', registry: unknown): void;
  (e: 'error', error: Error): void;
  (e: 'update:spreadMode', mode: SpreadModeLiteral): void;
}>();

const loading = ref(true);
const error = ref<string | null>(null);
const registryRef = ref<unknown>(null);
const { canGoBack, trackPage, recordJump, goBack, reset } = usePdfNavigation();
const listeners: (() => void)[] = [];
let lastKnownPage = 1;
let pageBeforeJump = 1;

const config = computed<PDFViewerConfig>(() => {
  if (!props.src) return {};
  return {
    src: props.src,
    worker: true,
    theme: { preference: 'light' },
    disabledCategories: props.disabledCategories,
    tabBar: 'never',
    spread: {
      defaultSpreadMode: props.spreadMode as unknown as 'none' | 'odd' | 'even',
    },
    render: {
      withAnnotations: true,
    },
  } as PDFViewerConfig;
});

interface SpreadPluginLike {
  provides(): { setSpreadMode(mode: string): void };
}

interface RegistryLike {
  getPlugin(id: string): SpreadPluginLike | null;
}

function applySpreadMode(mode: SpreadModeLiteral) {
  const registry = registryRef.value as RegistryLike | null;
  if (!registry || typeof registry.getPlugin !== 'function') return;
  const plugin = registry.getPlugin('spread');
  if (plugin && typeof plugin.provides === 'function') {
    const capability = plugin.provides();
    if (capability && typeof capability.setSpreadMode === 'function') {
      capability.setSpreadMode(mode);
    }
  }
}

function onReady(registry: unknown) {
  loading.value = false;
  registryRef.value = registry;

  // Setup PDF internal navigation history
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const r = registry as any;
    const docs = Object.keys(r.getStore().getState().core.documents);
    if (docs.length > 0) {
      const docId = docs[0];

      // Track current page from scroll (does NOT record history)
      const scrollPlugin = r.getPlugin('scroll');
      if (scrollPlugin) {
        const scrollScope = scrollPlugin.provides().forDocument(docId);
        const offPageChange = scrollScope.onPageChange((event: { pageNumber: number }) => {
          pageBeforeJump = lastKnownPage;
          lastKnownPage = event.pageNumber;
          trackPage(event.pageNumber);
        });
        listeners.push(offPageChange);

        // Initialize page tracking
        const metrics = scrollScope.getMetrics();
        if (metrics?.currentPage != null) {
          lastKnownPage = metrics.currentPage;
          pageBeforeJump = metrics.currentPage;
          trackPage(metrics.currentPage);
        }
      }

      // Record history only when annotation link is clicked
      const annotationPlugin = r.getPlugin('annotation');
      if (annotationPlugin) {
        const annScope = annotationPlugin.provides().forDocument(docId);
        const offNavigate = annScope.onNavigate(() => {
          // Use the page BEFORE this jump
          recordJump(pageBeforeJump);
        });
        listeners.push(offNavigate);
      }

      // Listen for spread mode changes from embedpdf UI and sync back
      const spreadPlugin = r.getPlugin('spread');
      if (spreadPlugin) {
        const spreadScope = spreadPlugin.provides().forDocument(docId);
        const offSpreadChange = spreadScope.onSpreadChange((mode: string) => {
          const modeLiteral = mode as SpreadModeLiteral;
          emit('update:spreadMode', modeLiteral);
          try {
            localStorage.setItem('pdf-spread-mode', modeLiteral);
          } catch {
            // ignore storage errors
          }
        });
        listeners.push(offSpreadChange);
      }
    }
  } catch (e) {
    console.warn('Failed to setup PDF navigation history:', e);
  }

  emit('ready', registry);
}

function onInit() {
  // initialization started
}

// Watch src changes to reset state
watch(
  () => props.src,
  () => {
    loading.value = true;
    error.value = null;
    registryRef.value = null;
    listeners.forEach((fn) => fn());
    listeners.length = 0;
    reset();
  }
);

onUnmounted(() => {
  listeners.forEach((fn) => fn());
  listeners.length = 0;
});

function handleGoBack() {
  const pageNumber = goBack();
  if (!pageNumber || !registryRef.value) return;

  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const r = registryRef.value as any;
    const scrollPlugin = r.getPlugin('scroll');
    if (!scrollPlugin) return;

    const docs = Object.keys(r.getStore().getState().core.documents);
    if (docs.length === 0) return;
    const docId = docs[0];
    const scope = scrollPlugin.provides().forDocument(docId);

    scope.scrollToPage({ pageNumber, behavior: 'auto' });
  } catch (e) {
    console.warn('Failed to navigate back:', e);
  }
}

// Watch spreadMode changes and apply via registry capability
watch(
  () => props.spreadMode,
  (newMode) => {
    if (newMode && registryRef.value) {
      applySpreadMode(newMode);
    }
  }
);
</script>

<template>
  <div class="w-full h-full flex flex-col relative">
    <!-- Content area -->
    <div class="flex-1 relative overflow-hidden">
      <!-- Loading state -->
      <div
        v-if="loading"
        class="absolute inset-0 flex items-center justify-center bg-gray-50 z-10"
        data-testid="pdf-loading"
      >
        <div class="flex flex-col items-center gap-2">
          <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm text-gray-500">正在加载 PDF 引擎...</span>
        </div>
      </div>

      <!-- Error state -->
      <div
        v-if="error"
        class="absolute inset-0 flex items-center justify-center bg-gray-50 z-20"
        data-testid="pdf-error"
      >
        <div class="text-center">
          <p class="text-lg text-red-500 mb-2">{{ error }}</p>
        </div>
      </div>

      <!-- Back button for PDF internal navigation -->
      <button
        v-if="canGoBack()"
        @click="handleGoBack"
        class="absolute bottom-4 left-4 z-30 flex items-center gap-1.5 px-3 py-2 bg-white/90 hover:bg-white text-gray-700 rounded-lg shadow-lg border border-gray-200 backdrop-blur-sm transition-all hover:scale-105 active:scale-95"
        title="返回上一位置"
        data-testid="pdf-back-button"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M9 14 4 9l5-5" />
          <path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11" />
        </svg>
        <span class="text-sm font-medium">返回</span>
      </button>

      <!-- EmbedPDF viewer -->
      <PDFViewer
        v-if="src"
        :config="config"
        @init="onInit"
        @ready="onReady"
        class="w-full h-full"
        data-testid="pdf-embed"
      />

      <!-- No src -->
      <div v-else class="w-full h-full flex items-center justify-center text-gray-500" data-testid="pdf-empty">
        <p>PDF 文件不可用</p>
      </div>
    </div>
  </div>
</template>
