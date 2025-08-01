<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const paperId = route.params.id as string

interface Paper {
  id: string
  title: string
  authors: string[]
  year?: number
  journal?: string
  abstract?: string
}

const paper = ref<Paper | null>(null)
const chatWidth = ref(400) // 默认400px
const isResizing = ref(false)

onMounted(() => {
  // 这里将来会从API获取真实数据
  paper.value = {
    id: paperId,
    title: '示例论文：深度学习的未来',
    authors: ['张三', '李四'],
    year: 2024,
    journal: 'Nature AI',
    abstract: '这是一个示例论文摘要...'
  }
})

function startResize(e: MouseEvent) {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

function handleResize(e: MouseEvent) {
  if (!isResizing.value) return
  const newWidth = window.innerWidth - e.clientX
  chatWidth.value = Math.max(300, Math.min(600, newWidth))
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
})
</script>

<template>
  <div class="h-screen w-full flex flex-col absolute inset-0">
    <div v-if="paper" class="flex-1 flex w-full">
      <!-- 左侧：PDF阅读器 -->
      <div class="flex-1 bg-white p-4 overflow-hidden">
        <div class="h-full flex flex-col">
          <h2 class="text-xl font-semibold mb-4 px-2">{{ paper.title }}</h2>
          <div class="flex-1 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-gray-500">
            <p class="text-lg mb-2">PDF阅读器区域</p>
            <p class="text-sm">论文ID: {{ paper.id }}</p>
          </div>
        </div>
      </div>
      
      <!-- 分割线 -->
      <div 
        class="w-1 bg-gray-200 hover:bg-gray-300 cursor-col-resize flex items-center justify-center"
        @mousedown="startResize"
        :class="{ 'bg-blue-500': isResizing }"
      >
        <div class="w-1 h-8 bg-gray-400 rounded"></div>
      </div>
      
      <!-- 右侧：AI对话 -->
      <div 
        class="bg-white p-4 overflow-hidden flex flex-col"
        :style="{ width: chatWidth + 'px' }"
      >
        <h3 class="text-lg font-semibold mb-4">AI对话</h3>
        <div class="flex-1 flex flex-col">
          <div class="flex-1 overflow-y-auto mb-4 space-y-3">
            <div class="bg-blue-50 rounded-lg p-3">
              <p class="text-sm text-blue-800">你好！我是AI助手，可以帮你理解这篇论文。请问有什么想了解的吗？</p>
            </div>
          </div>
          <div class="flex gap-2">
            <input 
              type="text" 
              placeholder="输入你的问题..." 
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">发送</button>
          </div>
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