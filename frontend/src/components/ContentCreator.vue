<template>
  <div class="creator">
    <h2 class="creator-title">创作新内容</h2>
    <div class="creator-form">
      <input
        v-model="form.title"
        placeholder="输入标题"
        class="creator-input"
        :disabled="creating"
      />
      <textarea
        v-model="form.original_text"
        placeholder="粘贴史书原文，开始创作..."
        rows="8"
        class="creator-textarea"
        :disabled="creating"
      ></textarea>
      <button
        @click="handleCreate"
        :disabled="creating || !canCreate"
        class="creator-btn"
      >
        {{ creating ? '创建中...' : '开始创作' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  emits: ['create'],
  setup(props, { emit }) {
    const form = ref({ title: '', original_text: '' })
    const creating = ref(false)

    const canCreate = computed(() => {
      return form.value.title.trim() && form.value.original_text.trim()
    })

    const handleCreate = () => {
      if (!canCreate.value) return
      emit('create', { ...form.value }, (success) => {
        creating.value = false
        if (success) {
          form.value = { title: '', original_text: '' }
        }
      })
      creating.value = true
    }

    return { form, creating, canCreate, handleCreate }
  }
}
</script>

<style scoped>
.creator {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}

.creator-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--spacing-lg);
  font-family: var(--font-serif);
}

.creator-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.creator-input,
.creator-textarea {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-family: var(--font-sans);
  color: var(--color-ink);
  background: var(--color-paper);
  transition: border-color 0.2s;
}

.creator-input:focus,
.creator-textarea:focus {
  outline: none;
  border-color: var(--color-vermilion);
}

.creator-input:disabled,
.creator-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.creator-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.creator-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-vermilion);
  color: var(--color-white);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.creator-btn:hover:not(:disabled) {
  background: var(--color-vermilion-light);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.creator-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
