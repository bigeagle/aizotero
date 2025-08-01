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
  <div class="paper-reader">
    <div v-if="paper" class="reader-container">
      <!-- 左侧：PDF阅读器 -->
      <div class="pdf-viewer">
        <h2>{{ paper.title }}</h2>
        <div class="pdf-placeholder">
          <p>PDF阅读器区域</p>
          <p>论文ID: {{ paper.id }}</p>
        </div>
      </div>
      
      <!-- 右侧：AI对话 -->
      <div class="ai-chat">
        <h3>AI对话</h3>
        <div class="chat-container">
          <div class="chat-messages">
            <div class="message ai">
              <p>你好！我是AI助手，可以帮你理解这篇论文。请问有什么想了解的吗？</p>
            </div>
          </div>
          <div class="chat-input">
            <input type="text" placeholder="输入你的问题..." />
            <button>发送</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paper-reader {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.reader-container {
  display: flex;
  flex: 1;
  gap: 1rem;
  padding: 1rem;
}

.pdf-viewer {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pdf-placeholder {
  height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border: 2px dashed #ccc;
  border-radius: 8px;
  color: #666;
}

.ai-chat {
  width: 400px;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.ai-chat h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.message {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: 8px;
}

.message.ai {
  background: #e3f2fd;
  margin-right: 2rem;
}

.chat-input {
  display: flex;
  gap: 0.5rem;
}

.chat-input input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.chat-input button {
  padding: 0.5rem 1rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:hover {
  background: #0056b3;
}
</style>