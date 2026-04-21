<script setup lang="ts">
import { RouterView, useRoute, useRouter } from 'vue-router';
import ArxivHoverPopup from '@/components/ArxivHoverPopup.vue';

const router = useRouter();
const route = useRoute();
const isDev = import.meta.env.DEV;
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-900 py-4">AIZotero - AI Paper Assistant</h1>
          <div class="flex items-center gap-3">
            <ArxivHoverPopup />
            <button
              v-if="isDev"
              @click="router.push('/test/markdown')"
              :class="[
                'text-sm px-3 py-1.5 rounded transition-colors',
                route.path === '/test/markdown'
                  ? 'bg-purple-100 text-purple-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100',
              ]"
              title="Markdown + LaTeX 渲染测试"
            >
              🧪 Debug
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/* All styles handled by Tailwind CSS */
</style>
