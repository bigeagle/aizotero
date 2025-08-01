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
  <div class="paper-list">
    <h2>论文列表</h2>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else class="papers">
      <div 
        v-for="paper in papers" 
        :key="paper.id"
        class="paper-card"
        @click="openPaper(paper.id)"
      >
        <h3>{{ paper.title }}</h3>
        <p class="authors">{{ paper.authors.join(', ') }}</p>
        <p class="meta">
          <span v-if="paper.year">{{ paper.year }}</span>
          <span v-if="paper.journal">• {{ paper.journal }}</span>
        </p>
        <p v-if="paper.abstract" class="abstract">{{ paper.abstract }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paper-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.paper-list h2 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

.papers {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.paper-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.paper-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.paper-card h3 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.authors {
  color: #666;
  margin-bottom: 0.5rem;
}

.meta {
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.abstract {
  color: #555;
  line-height: 1.5;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>