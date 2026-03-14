<template>
  <div class="list">
    <h2 class="list-title">内容列表</h2>

    <div v-if="providerState !== 'ready'" class="list-provider-hint">
      <template v-if="providerState === 'loading'">
        正在加载 AI provider，请稍候...
      </template>
      <template v-else-if="providerState === 'error'">
        AI provider 加载失败，无法处理内容
      </template>
      <template v-else-if="providerState === 'empty'">
        当前未配置可用 AI provider，无法处理内容
      </template>
    </div>

    <div v-if="loading" class="list-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="list-state list-error">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="contents.length === 0" class="list-state list-empty">
      <p>暂无内容</p>
      <p class="list-empty-hint">创建第一篇历史故事吧</p>
    </div>

    <div v-else class="list-items">
      <div
        v-for="item in contents"
        :key="item.id"
        :class="['list-item', { 'list-item-active': selectedId === item.id }]"
        @click="$emit('select', item.id)"
      >
        <div class="list-item-header">
          <h3 class="list-item-title">{{ item.title }}</h3>
          <span :class="['status-badge', `status-${item.status}`]">
            {{ statusText(item.status) }}
          </span>
        </div>
        <p class="list-item-preview">{{ getPreview(item.original_text) }}</p>
        <div class="list-item-footer">
          <span class="list-item-time">{{ formatTime(item.updated_at) }}</span>
          <div class="list-item-actions">
            <button
              v-if="item.status !== 'processing' && item.status !== 'completed'"
              @click.stop="$emit('process', item.id)"
              :disabled="processingIds.has(item.id) || !hasProvider"
              class="list-item-btn"
            >
              {{ processingIds.has(item.id) ? '处理中...' : '开始处理' }}
            </button>
            <span v-if="item.status === 'completed'" class="status-done">已完成</span>
          </div>
        </div>
        <div v-if="!hasProvider && item.status === 'draft'" class="list-item-hint">
          请先配置 AI provider
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    contents: { type: Array, default: () => [] },
    loading: Boolean,
    error: String,
    selectedId: Number,
    processingIds: { type: Set, default: () => new Set() },
    providerState: { type: String, default: 'ready' },
    hasProvider: Boolean
  },
  emits: ['select', 'process'],
  setup() {
    const statusText = (status) => {
      const map = { draft: '草稿', processing: '处理中', completed: '已完成' }
      return map[status] || status
    }

    const getPreview = (text) => {
      return text.length > 50 ? text.slice(0, 50) + '...' : text
    }

    const formatTime = (time) => {
      const date = new Date(time)
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)

      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString('zh-CN')
    }

    return { statusText, getPreview, formatTime }
  }
}
</script>

<style scoped>
.list {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--spacing-md);
  font-family: var(--font-serif);
}

.list-provider-hint {
  padding: var(--spacing-md);
  background: #fef3c7;
  border-radius: var(--radius-md);
  color: var(--color-processing);
  font-size: 0.9rem;
  margin-bottom: var(--spacing-md);
  text-align: center;
}

.list-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-ink-light);
  gap: var(--spacing-sm);
}

.list-error {
  color: var(--color-error);
}

.list-empty-hint {
  font-size: 0.875rem;
  opacity: 0.7;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-vermilion);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.list-items {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.list-item {
  padding: var(--spacing-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-paper);
}

.list-item:hover {
  border-color: var(--color-vermilion);
  transform: translateX(4px);
}

.list-item-active {
  border-color: var(--color-vermilion);
  background: var(--color-white);
  box-shadow: var(--shadow-sm);
}

.list-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.list-item-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-ink);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.status-draft {
  background: #f3f4f6;
  color: var(--color-draft);
}

.status-processing {
  background: #fef3c7;
  color: var(--color-processing);
}

.status-completed {
  background: #d1fae5;
  color: var(--color-completed);
}

.list-item-preview {
  font-size: 0.875rem;
  color: var(--color-ink-light);
  line-height: 1.5;
  margin-bottom: var(--spacing-sm);
}

.list-item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

.list-item-time {
  font-size: 0.75rem;
  color: var(--color-ink-light);
}

.list-item-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.list-item-btn {
  padding: 4px 12px;
  background: var(--color-paper-dark);
  color: var(--color-ink);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.list-item-btn:hover:not(:disabled) {
  background: var(--color-vermilion);
  color: var(--color-white);
  border-color: var(--color-vermilion);
}

.list-item-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-done {
  font-size: 0.8rem;
  color: var(--color-completed);
}

.list-item-hint {
  margin-top: var(--spacing-xs);
  font-size: 0.75rem;
  color: var(--color-ink-light);
  font-style: italic;
}

@media (max-width: 768px) {
  .list {
    padding: var(--spacing-md);
  }

  .list-item-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }

  .list-item-actions {
    width: 100%;
  }

  .list-item-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
