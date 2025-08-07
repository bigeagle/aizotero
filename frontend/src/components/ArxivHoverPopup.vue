<template>
  <div class="relative" v-click-outside="closePopup">
    <!-- 触发按钮 -->
    <button
      @click="togglePopup"
      class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200"
      :class="{ 'text-gray-900 bg-gray-100': isVisible }"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      <span>ArXiv</span>
    </button>

    <!-- 遮罩层 -->
    <transition
      enter-active-class="transition-opacity ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-show="isVisible" class="fixed inset-0 bg-black bg-opacity-25 z-40 md:hidden" @click="closePopup"></div>
    </transition>

    <!-- 弹出框 -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-1 md:translate-y-1 md:translate-x-0"
      enter-to-class="opacity-100 translate-y-0 md:translate-y-0 md:translate-x-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0 md:translate-y-0 md:translate-x-0"
      leave-to-class="opacity-0 translate-y-1 md:translate-y-1 md:translate-x-0"
    >
      <div
        v-show="isVisible"
        class="absolute right-0 mt-2 w-[500px] bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-md:fixed max-md:inset-x-4 max-md:top-20 max-md:w-auto max-md:max-h-[calc(100vh-8rem)] max-md:overflow-y-auto"
      >
        <!-- 小三角指示器 -->
        <div
          class="absolute -top-2 right-8 w-4 h-4 bg-white border-l border-t border-gray-200 transform rotate-45 max-md:hidden"
        ></div>

        <!-- 内容区域 -->
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-900">添加ArXiv论文</h3>
            <button @click="closePopup" class="md:hidden text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <ArxivInput
            ref="arxivInputRef"
            @loaded="handlePaperLoaded"
            @update:modelValue="handleInputChange"
            @read="closePopup"
            @duplicate-check="handleDuplicateCheck"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import ArxivInput from './ArxivInput.vue';
import type { DuplicateCheckResult } from '../services/arxivService';

const isVisible = ref(false);

const togglePopup = () => {
  isVisible.value = !isVisible.value;
};

const closePopup = () => {
  isVisible.value = false;
};

const handlePaperLoaded = () => {
  // 不关闭popup，让用户可以继续操作
};

const handleInputChange = () => {
  // 可以在这里添加额外的输入处理逻辑
};

const handleDuplicateCheck = (result: DuplicateCheckResult) => {
  // 可以在这里添加额外的重复检查处理逻辑
  console.log('重复检查结果:', result);
};

// 点击外部区域关闭指令
const vClickOutside = {
  mounted(el: HTMLElement, binding: { value: () => void }) {
    const handleClickOutside = (event: MouseEvent) => {
      if (!el.contains(event.target as Node)) {
        binding.value();
      }
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (el as any)._clickOutsideHandler = handleClickOutside;
    document.addEventListener('click', handleClickOutside);
  },
  unmounted(el: HTMLElement) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const handler = (el as any)._clickOutsideHandler;
    if (handler) {
      document.removeEventListener('click', handler);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (el as any)._clickOutsideHandler;
    }
  },
};

// ESC键关闭
const handleEsc = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closePopup();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleEsc);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEsc);
});
</script>

<style scoped>
/* 确保弹出框在最上层 */
.absolute {
  z-index: 1000;
}
</style>
