<template>
  <div id="app">
    <Toast :show="toast.show" :message="toast.message" :type="toast.type" />

    <header class="header">
      <div class="header-brand">
        <h1>历史故事创作工具</h1>
        <p class="subtitle">将史书原文转化为诙谐有趣的小红书内容</p>
      </div>
    </header>

    <div class="provider-bar">
      <div class="provider-bar-content">
        <div class="provider-status">
          <span class="provider-label">AI Provider</span>
          <template v-if="providerState === 'loading'">
            <span class="provider-loading">正在加载 AI provider...</span>
          </template>
          <template v-else-if="providerState === 'error'">
            <span class="provider-error-text">AI provider 加载失败</span>
            <button @click="loadProviders" class="retry-btn">重新加载</button>
          </template>
          <template v-else-if="providerState === 'empty'">
            <span class="provider-empty-text">当前未配置可用 AI provider</span>
          </template>
          <template v-else>
            <span class="provider-current">当前使用：</span>
            <select v-model="selectedProvider" class="provider-select">
              <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
            </select>
          </template>
        </div>
      </div>
    </div>

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
          :provider-state="providerState"
          :has-provider="canProcess"
          @select="handleSelect"
          @process="handleProcess"
        />
      </aside>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { contentAPI, providerAPI } from './api/client'
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
    const providers = ref([])
    const selectedProvider = ref(null)
    const providerLoadError = ref(false)
    const providerLoading = ref(true)
    let toastTimer = null

    const providerState = computed(() => {
      if (providerLoading.value) return 'loading'
      if (providerLoadError.value) return 'error'
      if (providers.value.length === 0) return 'empty'
      return 'ready'
    })

    const canProcess = computed(() => {
      return providerState.value === 'ready' && selectedProvider.value
    })

    const showToast = (message, type = 'info') => {
      if (toastTimer) clearTimeout(toastTimer)
      toast.value = { show: true, message, type }
      toastTimer = setTimeout(() => { toast.value.show = false }, 3000)
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

    const loadProviders = async () => {
      providerLoading.value = true
      providerLoadError.value = false
      try {
        const res = await providerAPI.list()
        providers.value = res.data.available_providers || []
        selectedProvider.value = res.data.default_provider || providers.value[0] || null
      } catch (error) {
        providerLoadError.value = true
        providers.value = []
        selectedProvider.value = null
      } finally {
        providerLoading.value = false
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
      if (!selectedProvider.value) {
        showToast('请先选择 AI provider', 'warning')
        return
      }
      processingIds.value.add(id)
      try {
        const res = await contentAPI.process(id, selectedProvider.value)
        showToast('处理完成', 'success')
        await loadContents()
        // 重新加载选中的内容以获取最新生成结果
        if (selectedContent.value?.id === id) {
          const contentRes = await contentAPI.get(id)
          selectedContent.value = contentRes.data
        }
      } catch (error) {
        const status = error.response?.status
        const detail = error.response?.data?.detail || error.message
        if (status === 409) {
          showToast('该内容正在处理中', 'warning')
        } else if (status === 422) {
          showToast('当前选择的 provider 不可用，请重新选择', 'error')
        } else {
          showToast('处理失败: ' + detail, 'error')
        }
      } finally {
        processingIds.value.delete(id)
      }
    }

    onMounted(() => {
      loadProviders()
      loadContents()
    })

    return {
      contents,
      selectedContent,
      processingIds,
      loading,
      loadError,
      toast,
      providers,
      selectedProvider,
      providerLoading,
      providerLoadError,
      providerState,
      canProcess,
      showToast,
      handleCreate,
      handleSelect,
      handleProcess,
      loadProviders
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
  background: linear-gradient(135deg, var(--color-vermilion) 0%, #a83426 100%);
  color: var(--color-white);
  box-shadow: var(--shadow-md);
}

.header-brand {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
}

.header-brand h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 4px;
  font-family: var(--font-serif);
}

.subtitle {
  font-size: 0.9rem;
  opacity: 0.9;
}

.provider-bar {
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.provider-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 32px;
  max-width: 1600px;
  margin: 0 auto;
}

.provider-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.provider-label {
  font-weight: 600;
  color: var(--color-ink);
  font-size: 0.9rem;
}

.provider-loading { color: var(--color-ink-light); font-size: 0.9rem; }
.provider-error-text { color: var(--color-error); font-size: 0.9rem; }
.provider-empty-text { color: var(--color-processing); font-size: 0.9rem; }
.provider-current { color: var(--color-ink-light); font-size: 0.9rem; }

.provider-select {
  padding: 8px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-paper);
  color: var(--color-ink);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  min-width: 140px;
}

.provider-select:focus {
  outline: none;
  border-color: var(--color-vermilion);
}

.retry-btn {
  padding: 6px 14px;
  background: var(--color-vermilion);
  color: var(--color-white);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
}

.retry-btn:hover { background: var(--color-vermilion-light); }

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
  .workspace-sidebar { grid-column: 1 / -1; }
  .workspace-main { grid-column: 1; }
  .workspace-list { grid-column: 2; }
}

@media (max-width: 768px) {
  .header-brand {
    padding: 20px 16px;
    text-align: center;
  }
  .header-brand h1 { font-size: 1.5rem; }
  .provider-bar-content {
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px;
  }
  .provider-status {
    flex-wrap: wrap;
    justify-content: center;
  }
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
}
</style>
