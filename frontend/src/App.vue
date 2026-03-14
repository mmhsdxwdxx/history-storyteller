<template>
  <div id="app">
    <header class="header">
      <h1>历史故事创作工具</h1>
      <p class="subtitle">将史书原文转化为诙谐有趣的小红书内容</p>
    </header>

    <main class="container">
      <section class="card create-section">
        <h2>创建新内容</h2>
        <input v-model="newContent.title" placeholder="输入标题" class="input" />
        <textarea v-model="newContent.original_text" placeholder="粘贴史书原文" rows="6" class="textarea"></textarea>
        <button @click="createContent" class="btn btn-primary">创建内容</button>
      </section>

      <section class="list-section">
        <h2>内容列表</h2>
        <div class="content-grid">
          <div v-for="item in contents" :key="item.id" class="card content-card">
            <h3>{{ item.title }}</h3>
            <span :class="['status-badge', item.status]">{{ statusText(item.status) }}</span>
            <div class="card-actions">
              <button @click="processContent(item.id)" :disabled="item.status === 'processing'" class="btn btn-secondary">
                {{ item.status === 'processing' ? '处理中...' : '开始处理' }}
              </button>
              <button @click="viewContent(item.id)" class="btn btn-outline">查看详情</button>
            </div>
          </div>
        </div>
      </section>

      <section v-if="selectedContent" class="card detail-section">
        <h2>{{ selectedContent.title }}</h2>
        <div class="text-block">
          <h3>📜 原文</h3>
          <p>{{ selectedContent.original_text }}</p>
        </div>
        <div class="text-block" v-if="selectedContent.vernacular_text">
          <h3>📖 白话文</h3>
          <p>{{ selectedContent.vernacular_text }}</p>
        </div>
        <div class="text-block" v-if="selectedContent.humorous_text">
          <h3>✨ 诙谐版</h3>
          <p>{{ selectedContent.humorous_text }}</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { contentAPI } from './api/client'

export default {
  setup() {
    const contents = ref([])
    const newContent = ref({ title: '', original_text: '' })
    const selectedContent = ref(null)

    const statusText = (status) => {
      const map = { draft: '草稿', processing: '处理中', completed: '已完成' }
      return map[status] || status
    }

    const loadContents = async () => {
      const res = await contentAPI.list()
      contents.value = res.data
    }

    const createContent = async () => {
      try {
        await contentAPI.create(newContent.value)
        newContent.value = { title: '', original_text: '' }
        loadContents()
      } catch (error) {
        alert('创建失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    const processContent = async (id) => {
      try {
        await contentAPI.process(id)
        alert('处理已开始，请稍后刷新查看结果')
        setTimeout(loadContents, 3000)
      } catch (error) {
        alert('处理失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    const viewContent = async (id) => {
      try {
        const res = await contentAPI.get(id)
        selectedContent.value = res.data
      } catch (error) {
        alert('加载失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    onMounted(loadContents)

    return { contents, newContent, selectedContent, statusText, createContent, processContent, viewContent }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #faf8f5 0%, #f5f1eb 100%);
  color: #2d2d2d;
  line-height: 1.6;
}

#app { min-height: 100vh; }

.header {
  text-align: center;
  padding: 60px 20px 40px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.header h1 { font-size: 2.5rem; font-weight: 600; margin-bottom: 10px; }
.subtitle { font-size: 1.1rem; opacity: 0.95; }

.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }

.card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); }

h2 { font-size: 1.5rem; margin-bottom: 20px; color: #1a1a1a; }
h3 { font-size: 1.2rem; margin-bottom: 12px; color: #2d2d2d; }

.input, .textarea {
  width: 100%;
  padding: 12px 16px;
  margin: 10px 0;
  border: 2px solid #e5e5e5;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input:focus, .textarea:focus {
  outline: none;
  border-color: #f97316;
}

.textarea { resize: vertical; font-family: inherit; }

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 10px;
}

.btn-primary {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4); }

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover { background: #e5e7eb; }

.btn-outline {
  background: transparent;
  border: 2px solid #e5e5e5;
  color: #374151;
}

.btn-outline:hover { border-color: #f97316; color: #f97316; }

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.content-card {
  padding: 24px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  margin: 10px 0;
}

.status-badge.draft { background: #f3f4f6; color: #6b7280; }
.status-badge.processing { background: #fef3c7; color: #d97706; }
.status-badge.completed { background: #d1fae5; color: #059669; }

.card-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

.text-block {
  margin: 24px 0;
  padding: 20px;
  background: #faf8f5;
  border-radius: 12px;
  border-left: 4px solid #f97316;
}

.text-block p {
  white-space: pre-wrap;
  line-height: 1.8;
}
</style>
