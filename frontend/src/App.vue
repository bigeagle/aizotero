<script setup lang="ts">
import { RouterView } from 'vue-router';
import ArxivHoverPopup from '@/components/ArxivHoverPopup.vue';
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-900 py-4">AIZotero - AI Paper Assistant</h1>
          <div class="flex items-center">
            <ArxivHoverPopup />
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
