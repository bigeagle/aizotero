<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
</script>

<template>
  <div class="h-screen flex flex-col">
    <div v-if="paper" class="flex-1 flex gap-4 p-4">
      <!-- 左侧：PDF阅读器 -->
      <div class="flex-1 card overflow-hidden">
        <h2 class="text-xl font-semibold mb-4">{{ paper.title }}</h2>
        <div class="h-full bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-gray-500">
          <p class="text-lg mb-2">PDF阅读器区域</p>
          <p class="text-sm">论文ID: {{ paper.id }}</p>
        </div>
      </div>
      
      <!-- 右侧：AI对话 -->
      <div class="w-96 card flex flex-col">
        <h3 class="text-lg font-semibold mb-4">AI对话</h3>
        <div class="flex-1 flex flex-col">
          <div class="flex-1 overflow-y-auto mb-4">
            <div class="bg-blue-50 rounded-lg p-4 mb-3">
              <p class="text-sm text-blue-800">你好！我是AI助手，可以帮你理解这篇论文。请问有什么想了解的吗？</p>
            </div>
          </div>
          <div class="flex gap-2">
            <input 
              type="text" 
              placeholder="输入你的问题..." 
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button class="btn btn-primary px-4 py-2">发送</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* All styles handled by Tailwind CSS */
</style>