<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

// Debounce utility function
const debounce = (func: Function, delay: number) => {
  let timeoutId: number
  return (...args: any[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

interface Paper {
  id: string
  title: string
  authors: string
  year?: string
  journal?: string
  abstract?: string
  doi?: string
  url?: string
  tags: string[]
  pdf_path?: string
  has_pdf: boolean
}

const papers = ref<Paper[]>([])
const loading = ref(true)
const searchQuery = ref('')
const router = useRouter()

const fetchPapers = async (query?: string) => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (query && query.trim()) {
      params.set('q', query.trim())
    }
    const response = await fetch(`/api/v1/papers?${params.toString()}`)
    papers.value = await response.json()
  } catch (error) {
    console.error('Failed to load papers:', error)
    // 使用示例数据
    papers.value = [
      {
        id: 'sample-1',
        title: '示例论文：深度学习的未来',
        authors: '张三, 李四',
        year: '2024',
        journal: 'Nature AI',
        abstract: '这是一个示例论文摘要...',
        doi: '',
        url: '',
        tags: [],
        pdf_path: '',
        has_pdf: true
      }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPapers()
})

// Debounced search
const debouncedSearch = debounce(fetchPapers, 300)

watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery)
})

function openPaper(id: string) {
  router.push(`/read/${id}`)
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-3xl font-bold text-gray-900">论文列表</h1>

      <!-- 搜索框 -->
      <div class="relative w-full max-w-md">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索论文标题、摘要或标签..."
          class="w-full px-4 py-2 pl-10 pr-4 text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
        <div class="absolute inset-y-0 left-0 flex items-center pl-3">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-4 text-gray-600">加载中...</p>
    </div>

    <div v-else class="grid gap-6">
      <div
        v-for="paper in papers"
        :key="paper.id"
        class="card hover:shadow-lg transition-shadow duration-300"
      >
        <h3
          class="text-xl font-semibold text-gray-900 mb-2 cursor-pointer hover:text-blue-600 transition-colors duration-200"
          @click="openPaper(paper.id)"
        >
          {{ paper.title }}
        </h3>
        <p class="text-gray-700 mb-2">{{ paper.authors }}</p>
        <p class="text-sm text-gray-500 mb-3">
          <span v-if="paper.year">{{ paper.year }}</span>
          <span v-if="paper.journal" class="ml-2">• {{ paper.journal }}</span>
        </p>

        <!-- Tags with special styling -->
        <div v-if="paper.tags.length" class="mb-3 flex flex-wrap gap-2">
          <span
            v-for="tag in paper.tags"
            :key="tag"
            :class="{
              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium': true,
              'bg-red-100 text-red-800': tag === '♥️',
              'bg-blue-100 text-blue-800': tag === '/unread',
              'bg-gray-100 text-gray-800': tag !== '♥️' && tag !== '/unread'
            }"
          >
            {{ tag }}
          </span>
        </div>

        <p v-if="paper.abstract" class="text-gray-600 text-sm leading-relaxed">{{ paper.abstract }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* All styles handled by Tailwind CSS */
</style>
