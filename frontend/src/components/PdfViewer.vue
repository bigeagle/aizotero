<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { PDFViewer } from '@embedpdf/vue-pdf-viewer';
import type { PDFViewerConfig } from '@embedpdf/vue-pdf-viewer';

export type SpreadModeLiteral = 'none' | 'odd' | 'even';

interface Props {
  src: string | null;
  spreadMode?: SpreadModeLiteral;
  disabledCategories?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  spreadMode: 'none',
  disabledCategories: () => [
    'annotation',
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
  }
);

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
