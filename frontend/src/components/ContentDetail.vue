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

      <div v-if="content.generations && content.generations.length > 0" class="generation-tabs">
        <button
          v-for="(gen, index) in content.generations"
          :key="gen.id"
          :class="['gen-tab', { active: selectedGenId === gen.id }]"
          @click="selectedGenId = gen.id"
        >
          {{ gen.provider }}
          <span class="gen-time">{{ formatTime(gen.created_at) }}</span>
        </button>
        <button v-if="content.generations.length >= 2" class="compare-btn" @click="toggleCompare">
          {{ compareMode ? '退出对比' : '对比模式' }}
        </button>
      </div>

      <div v-if="compareMode && content.generations && content.generations.length >= 2" class="compare-view">
        <div class="compare-select">
          <select v-model="compareGen1">
            <option v-for="gen in content.generations" :key="gen.id" :value="gen.id">
              {{ gen.provider }} - {{ formatTime(gen.created_at) }}
            </option>
          </select>
          <span>vs</span>
          <select v-model="compareGen2">
            <option v-for="gen in content.generations" :key="gen.id" :value="gen.id">
              {{ gen.provider }} - {{ formatTime(gen.created_at) }}
            </option>
          </select>
        </div>
        <div class="compare-content">
          <div class="compare-panel">
            <h4>{{ getGenById(compareGen1)?.provider }}</h4>
            <div class="compare-text">{{ getGenById(compareGen1)?.humorous_text }}</div>
          </div>
          <div class="compare-panel">
            <h4>{{ getGenById(compareGen2)?.provider }}</h4>
            <div class="compare-text">{{ getGenById(compareGen2)?.humorous_text }}</div>
          </div>
        </div>
      </div>

      <div v-else class="detail-sections">
        <section v-if="currentGeneration" class="detail-section main-section">
          <div class="section-header" @click="toggleSection('humorous')">
            <h3>最终文案</h3>
            <span class="gen-provider">{{ currentGeneration.provider }}</span>
          </div>
          <div class="section-content">
            <p>{{ currentGeneration.humorous_text }}</p>
            <button @click="copy(currentGeneration.humorous_text)" class="copy-btn">复制</button>
          </div>
        </section>

        <section class="detail-section collapsible">
          <div class="section-header" @click="toggleSection('vernacular')">
            <h3>白话文</h3>
            <span class="toggle-icon">{{ expandedSections.vernacular ? '▼' : '▶' }}</span>
          </div>
          <div v-if="expandedSections.vernacular && currentGeneration" class="section-content">
            <p>{{ currentGeneration.vernacular_text }}</p>
            <button @click="copy(currentGeneration.vernacular_text)" class="copy-btn">复制</button>
          </div>
        </section>

        <section class="detail-section collapsible">
          <div class="section-header" @click="toggleSection('original')">
            <h3>原文</h3>
            <span class="toggle-icon">{{ expandedSections.original ? '▼' : '▶' }}</span>
          </div>
          <div v-if="expandedSections.original" class="section-content">
            <p>{{ content.original_text }}</p>
            <button @click="copy(content.original_text)" class="copy-btn">复制</button>
          </div>
        </section>
      </div>

      <div v-if="!currentGeneration && content.status === 'draft'" class="detail-hint">
        内容尚未处理，选择 provider 后点击"开始处理"
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  props: {
    content: Object
  },
  emits: ['copy-success'],
  setup(props, { emit }) {
    const expandedSections = ref({ vernacular: false, original: false })
    const selectedGenId = ref(null)
    const compareMode = ref(false)
    const compareGen1 = ref(null)
    const compareGen2 = ref(null)

    const statusText = (status) => {
      const map = { draft: '草稿', processing: '处理中', completed: '已完成' }
      return map[status] || status
    }

    const currentGeneration = computed(() => {
      if (!props.content?.generations?.length) return null
      if (selectedGenId.value) {
        return props.content.generations.find(g => g.id === selectedGenId.value)
      }
      return props.content.generations[0]
    })

    const toggleSection = (section) => {
      expandedSections.value[section] = !expandedSections.value[section]
    }

    const toggleCompare = () => {
      compareMode.value = !compareMode.value
      if (compareMode.value && props.content?.generations?.length >= 2) {
        compareGen1.value = props.content.generations[0].id
        compareGen2.value = props.content.generations[1].id
      }
    }

    const getGenById = (id) => {
      return props.content?.generations?.find(g => g.id === id)
    }

    const formatTime = (time) => {
      const date = new Date(time)
      return date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    }

    const copy = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        emit('copy-success')
      } catch (err) {
        console.error('复制失败', err)
      }
    }

    watch(() => props.content, (newContent) => {
      if (newContent?.generations?.length) {
        selectedGenId.value = newContent.generations[0].id
      }
      compareMode.value = false
    })

    return {
      expandedSections,
      selectedGenId,
      compareMode,
      compareGen1,
      compareGen2,
      currentGeneration,
      statusText,
      toggleSection,
      toggleCompare,
      getGenById,
      formatTime,
      copy
    }
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
  margin-bottom: var(--spacing-lg);
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

.status-draft { background: #f3f4f6; color: var(--color-draft); }
.status-processing { background: #fef3c7; color: var(--color-processing); }
.status-completed { background: #d1fae5; color: var(--color-completed); }

.generation-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.gen-tab {
  padding: 8px 16px;
  background: var(--color-paper);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.gen-tab:hover { border-color: var(--color-vermilion); }
.gen-tab.active { background: var(--color-vermilion); color: white; border-color: var(--color-vermilion); }

.gen-time { font-size: 0.7rem; opacity: 0.7; }

.compare-btn {
  padding: 8px 16px;
  background: var(--color-jade);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.compare-view {
  margin-bottom: var(--spacing-lg);
}

.compare-select {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.compare-select select {
  flex: 1;
  padding: 8px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.compare-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.compare-panel {
  background: var(--color-paper);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}

.compare-panel h4 {
  margin-bottom: var(--spacing-sm);
  color: var(--color-vermilion);
}

.compare-text {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 0.9rem;
}

.detail-sections {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.detail-section {
  background: var(--color-paper);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.detail-section.main-section {
  border-left: 4px solid var(--color-vermilion);
}

.section-header {
  padding: var(--spacing-md);
  background: var(--color-paper-dark);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.section-header h3 {
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-ink);
  margin: 0;
}

.gen-provider {
  font-size: 0.8rem;
  color: var(--color-vermilion);
  background: white;
  padding: 2px 8px;
  border-radius: 4px;
}

.toggle-icon {
  font-size: 0.8rem;
  color: var(--color-ink-light);
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
  opacity: 0.6;
}

.copy-btn:hover {
  opacity: 1;
  background: var(--color-vermilion);
  color: white;
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

@media (max-width: 768px) {
  .compare-content {
    grid-template-columns: 1fr;
  }
}
</style>
