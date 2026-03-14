<template>
  <div id="app">
    <Toast :show="toast.show" :message="toast.message" :type="toast.type" />

    <header class="header">
      <h1>历史故事创作工具</h1>
      <p class="subtitle">将史书原文转化为诙谐有趣的小红书内容</p>
    </header>

    <main class="workspace">
      <aside class="workspace-sidebar">
        <ContentCreator @create="handleCreate" />
      </aside>

      <section class="workspace-main">
        <ContentDetail
          :content="selectedContent"
          @copy-success="showToast('已复制到剪贴板', 'success')"
        />
      </section>

      <aside class="workspace-list">
        <ContentList
          :contents="contents"
          :loading="loading"
          :error="loadError"
          :selected-id="selectedContent?.id"
          :processing-ids="processingIds"
          @select="handleSelect"
          @process="handleProcess"
        />
      </aside>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { contentAPI } from './api/client'
import Toast from './components/Toast.vue'
import ContentCreator from './components/ContentCreator.vue'
import ContentList from './components/ContentList.vue'
import ContentDetail from './components/ContentDetail.vue'

export default {
  components: { Toast, ContentCreator, ContentList, ContentDetail },
  setup() {
    const contents = ref([])
    const selectedContent = ref(null)
    const processingIds = ref(new Set())
    const loading = ref(false)
    const loadError = ref(null)
    const toast = ref({ show: false, message: '', type: 'info' })
    let toastTimer = null

    const showToast = (message, type = 'info') => {
      if (toastTimer) clearTimeout(toastTimer)
      toast.value = { show: true, message, type }
      toastTimer = setTimeout(() => {
        toast.value.show = false
      }, 3000)
    }

    const loadContents = async () => {
      loading.value = true
      loadError.value = null
      try {
        const res = await contentAPI.list()
        contents.value = res.data
      } catch (error) {
        loadError.value = '加载失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    const handleCreate = async (data, callback) => {
      try {
        await contentAPI.create(data)
        await loadContents()
        showToast('创建成功', 'success')
        callback(true)
      } catch (error) {
        const detail = error.response?.data?.detail || error.message
        showToast('创建失败: ' + detail, 'error')
        callback(false)
      }
    }

    const handleSelect = async (id) => {
      try {
        const res = await contentAPI.get(id)
        selectedContent.value = res.data
      } catch (error) {
        showToast('加载失败', 'error')
      }
    }

    const handleProcess = async (id) => {
      processingIds.value.add(id)
      try {
        const res = await contentAPI.process(id)
        showToast('处理完成', 'success')
        await loadContents()
        if (selectedContent.value?.id === id) {
          selectedContent.value = res.data
        }
      } catch (error) {
        const status = error.response?.status
        const detail = error.response?.data?.detail || error.message
        if (status === 409) {
          showToast('该内容正在处理中', 'warning')
        } else if (status === 422) {
          showToast('配置错误: ' + detail, 'error')
        } else {
          showToast('处理失败: ' + detail, 'error')
        }
      } finally {
        processingIds.value.delete(id)
      }
    }

    onMounted(loadContents)

    return {
      contents,
      selectedContent,
      processingIds,
      loading,
      loadError,
      toast,
      showToast,
      handleCreate,
      handleSelect,
      handleProcess
    }
  }
}
</script>

<style>
@import './styles/variables.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--color-paper);
  color: var(--color-ink);
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  padding: 48px 20px 32px;
  background: linear-gradient(135deg, var(--color-vermilion) 0%, #a83426 100%);
  color: var(--color-white);
  box-shadow: var(--shadow-md);
}

.header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 8px;
  font-family: var(--font-serif);
}

.subtitle {
  font-size: 1rem;
  opacity: 0.95;
}

.workspace {
  flex: 1;
  display: grid;
  grid-template-columns: 360px 1fr 320px;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.workspace-sidebar,
.workspace-main,
.workspace-list {
  min-height: 600px;
}

@media (max-width: 1200px) {
  .workspace {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
  }

  .workspace-sidebar {
    grid-column: 1 / -1;
  }

  .workspace-main {
    grid-column: 1;
  }

  .workspace-list {
    grid-column: 2;
  }
}

@media (max-width: 768px) {
  .workspace {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
  }

  .workspace-sidebar,
  .workspace-main,
  .workspace-list {
    grid-column: 1;
    min-height: auto;
  }

  .header h1 {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.875rem;
  }
}
</style>
