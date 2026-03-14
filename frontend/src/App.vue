<template>
  <div id="app">
    <Toast :show="toast.show" :message="toast.message" :type="toast.type" />

    <header class="header">
      <div class="header-content">
        <div class="header-title">
          <h1>历史故事创作工具</h1>
          <p class="subtitle">将史书原文转化为诙谐有趣的小红书内容</p>
        </div>
        <div class="header-provider">
          <template v-if="providerLoadError">
            <span class="provider-error">AI provider 信息加载失败</span>
          </template>
          <template v-else-if="providers.length === 0">
            <span class="provider-warning">未配置可用 AI provider</span>
          </template>
          <template v-else>
            <label>AI Provider</label>
            <select v-model="selectedProvider" class="provider-select">
              <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
            </select>
          </template>
        </div>
      </div>
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
          :can-process="canProcess"
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
    const providerLoadError = ref(false)
    const selectedProvider = ref(null)
    let toastTimer = null

    const canProcess = computed(() => {
      return providers.value.length > 0 && selectedProvider.value && !providerLoadError.value
    })

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

    const loadProviders = async () => {
      try {
        providerLoadError.value = false
        const res = await providerAPI.list()
        providers.value = res.data.available_providers || []
        selectedProvider.value = res.data.default_provider || providers.value[0] || null
      } catch (error) {
        providerLoadError.value = true
        providers.value = []
        selectedProvider.value = null
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
        if (selectedContent.value?.id === id) {
          selectedContent.value = res.data
        }
      } catch (error) {
        const status = error.response?.status
        const detail = error.response?.data?.detail || error.message
        if (status === 409) {
          showToast('该内容正在处理中', 'warning')
        } else if (status === 422) {
          if (detail.includes('not configured') || detail.includes('not available')) {
            showToast('当前选择的 provider 不可用，请重新选择', 'error')
          } else {
            showToast('配置错误: ' + detail, 'error')
          }
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
      providerLoadError,
      selectedProvider,
      canProcess,
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
  background: linear-gradient(135deg, var(--color-vermilion) 0%, #a83426 100%);
  color: var(--color-white);
  box-shadow: var(--shadow-md);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.header-title h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 4px;
  font-family: var(--font-serif);
}

.subtitle {
  font-size: 0.9rem;
  opacity: 0.9;
}

.header-provider {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.header-provider label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.provider-select {
  padding: 8px 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-md);
  background: rgba(255,255,255,0.1);
  color: var(--color-white);
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 120px;
}

.provider-select:focus {
  outline: none;
  border-color: rgba(255,255,255,0.6);
}

.provider-error {
  padding: 8px 16px;
  background: rgba(220, 38, 38, 0.8);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
}

.provider-warning {
  padding: 8px 16px;
  background: rgba(217, 119, 6, 0.8);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
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
  .header-content {
    flex-direction: column;
    gap: var(--spacing-md);
    padding: 20px 16px;
  }

  .header-title {
    text-align: center;
  }

  .header-title h1 {
    font-size: 1.5rem;
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
