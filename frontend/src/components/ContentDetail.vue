<template>
  <div class="detail">
    <div v-if="!content" class="detail-empty">
      <p>选择一篇内容查看详情</p>
    </div>

    <div v-else class="detail-content">
      <div class="detail-header">
        <h2 class="detail-title">{{ content.title }}</h2>
        <span :class="['status-badge', `status-${content.status}`]">
          {{ statusText(content.status) }}
        </span>
      </div>

      <div class="detail-sections">
        <section class="detail-section">
          <div class="section-header">
            <h3>📜 原文</h3>
          </div>
          <div class="section-content">
            <p>{{ content.original_text }}</p>
            <button @click="copy(content.original_text)" class="copy-btn">复制</button>
          </div>
        </section>

        <section v-if="content.vernacular_text" class="detail-section">
          <div class="section-header">
            <h3>📖 白话文</h3>
          </div>
          <div class="section-content">
            <p>{{ content.vernacular_text }}</p>
            <button @click="copy(content.vernacular_text)" class="copy-btn">复制</button>
          </div>
        </section>

        <section v-if="content.humorous_text" class="detail-section">
          <div class="section-header">
            <h3>✨ 诙谐版</h3>
          </div>
          <div class="section-content">
            <p>{{ content.humorous_text }}</p>
            <button @click="copy(content.humorous_text)" class="copy-btn">复制</button>
          </div>
        </section>

        <div v-if="content.status === 'draft'" class="detail-hint">
          内容尚未处理，点击"开始处理"生成白话文和诙谐版
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    content: Object
  },
  emits: ['copy-success'],
  setup(props, { emit }) {
    const statusText = (status) => {
      const map = { draft: '草稿', processing: '处理中', completed: '已完成' }
      return map[status] || status
    }

    const copy = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        emit('copy-success')
      } catch (err) {
        console.error('复制失败', err)
      }
    }

    return { statusText, copy }
  }
}
</script>

<style scoped>
.detail {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
  height: 100%;
  overflow-y: auto;
}

.detail-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-ink-light);
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--color-border);
}

.detail-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-ink);
  font-family: var(--font-serif);
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
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

.detail-sections {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.detail-section {
  background: var(--color-paper);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-vermilion);
  overflow: hidden;
}

.section-header {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-paper-dark);
  border-bottom: 1px solid var(--color-border);
}

.section-header h3 {
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-ink);
  margin: 0;
}

.section-content {
  padding: var(--spacing-lg);
  position: relative;
}

.section-content p {
  white-space: pre-wrap;
  line-height: 1.8;
  color: var(--color-ink);
  margin: 0;
  font-size: 0.95rem;
}

.copy-btn {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  padding: 4px 12px;
  background: var(--color-white);
  color: var(--color-ink);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0.6;
}

.copy-btn:hover {
  opacity: 1;
  background: var(--color-vermilion);
  color: var(--color-white);
  border-color: var(--color-vermilion);
}

.detail-hint {
  padding: var(--spacing-md);
  background: #fef3c7;
  border-radius: var(--radius-md);
  color: var(--color-processing);
  font-size: 0.875rem;
  text-align: center;
}
</style>
