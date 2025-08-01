<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface Paper {
  id: string
  title: string
  authors: string[]
  year?: number
  journal?: string
  abstract?: string
}

const papers = ref<Paper[]>([])
const loading = ref(true)
const router = useRouter()

onMounted(async () => {
  try {
    const response = await fetch('/api/v1/papers')
    papers.value = await response.json()
  } catch (error) {
    console.error('Failed to load papers:', error)
    // 使用示例数据
    papers.value = [
      {
        id: 'sample-1',
        title: '示例论文：深度学习的未来',
        authors: ['张三', '李四'],
        year: 2024,
        journal: 'Nature AI',
        abstract: '这是一个示例论文摘要...'
      }
    ]
  } finally {
    loading.value = false
  }
})

function openPaper(id: string) {
  router.push(`/read/${id}`)
}
</script>

<template>
  <div class="max-w-6xl mx-auto p-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">论文列表</h1>
    
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-4 text-gray-600">加载中...</p>
    </div>
    
    <div v-else class="grid gap-6">
      <div 
        v-for="paper in papers" 
        :key="paper.id"
        class="card hover:shadow-lg transition-shadow duration-300 cursor-pointer"
        @click="openPaper(paper.id)"
      >
        <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ paper.title }}</h3>
        <p class="text-gray-700 mb-2">{{ paper.authors.join(', ') }}</p>
        <p class="text-sm text-gray-500 mb-3">
          <span v-if="paper.year">{{ paper.year }}</span>
          <span v-if="paper.journal" class="ml-2">• {{ paper.journal }}</span>
        </p>
        <p v-if="paper.abstract" class="text-gray-600 text-sm leading-relaxed">{{ paper.abstract }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* All styles handled by Tailwind CSS */
</style>