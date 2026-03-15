<template>
  <div class="provider-config">
    <div class="config-header">
      <h3>AI Provider 配置</h3>
      <button @click="$emit('close')" class="close-btn">&times;</button>
    </div>

    <div class="config-tabs">
      <button
        v-for="p in ['openai', 'anthropic', 'gemini']"
        :key="p"
        :class="['tab-btn', { active: activeProvider === p }]"
        @click="activeProvider = p"
      >
        {{ p.toUpperCase() }}
      </button>
    </div>

    <form @submit.prevent="handleSave" class="config-form">
      <div class="form-group">
        <label>API URL</label>
        <input
          v-model="form.api_url"
          type="url"
          placeholder="https://api.example.com/v1"
          required
        />
      </div>

      <div class="form-group">
        <label>API Key</label>
        <input
          v-model="form.api_key"
          type="password"
          placeholder="sk-..."
          required
        />
      </div>

      <div class="form-group">
        <label>Model</label>
        <input
          v-model="form.model"
          type="text"
          placeholder="gpt-4, claude-3-opus, gemini-pro"
          required
        />
      </div>

      <div class="form-group checkbox">
        <label>
          <input v-model="form.is_default" type="checkbox" />
          设为默认 Provider
        </label>
      </div>

      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn-cancel">
          取消
        </button>
        <button type="submit" :disabled="saving" class="btn-save">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>

    <div v-if="savedConfigs.length > 0" class="saved-configs">
      <h4>已保存的配置</h4>
      <div v-for="config in savedConfigs" :key="config.id" class="config-item">
        <span class="config-name">{{ config.provider_name }}</span>
        <span class="config-model">{{ config.model }}</span>
        <span v-if="config.is_default" class="config-default">默认</span>
        <button @click="loadConfig(config)" class="btn-edit">编辑</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, onMounted } from 'vue'
import { providerAPI } from '../api/client'

export default {
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const activeProvider = ref('openai')
    const saving = ref(false)
    const savedConfigs = ref([])

    const form = reactive({
      api_url: '',
      api_key: '',
      model: '',
      is_default: false
    })

    const defaultModels = {
      openai: 'gpt-4o',
      anthropic: 'claude-3-5-sonnet-latest',
      gemini: 'gemini-pro'
    }

    const loadSavedConfigs = async () => {
      try {
        const res = await providerAPI.getConfigs()
        savedConfigs.value = res.data || []
      } catch (e) {
        console.error('Failed to load configs:', e)
      }
    }

    const loadConfig = (config) => {
      activeProvider.value = config.provider_name
      form.api_url = config.api_url
      form.api_key = '' // 安全考虑，不回显 key
      form.model = config.model
      form.is_default = config.is_default
    }

    const handleSave = async () => {
      saving.value = true
      try {
        await providerAPI.saveConfig({
          provider_name: activeProvider.value,
          api_url: form.api_url,
          api_key: form.api_key,
          model: form.model,
          is_default: form.is_default
        })
        emit('saved')
        emit('close')
      } catch (e) {
        console.error('Failed to save config:', e)
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        saving.value = false
      }
    }

    watch(activeProvider, (newProvider) => {
      // 切换 provider 时设置默认 model
      if (!form.model || Object.values(defaultModels).includes(form.model)) {
        form.model = defaultModels[newProvider] || ''
      }
    })

    onMounted(() => {
      loadSavedConfigs()
      form.model = defaultModels[activeProvider.value]
    })

    return {
      activeProvider,
      form,
      saving,
      savedConfigs,
      loadConfig,
      handleSave
    }
  }
}
</script>

<style scoped>
.provider-config {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 480px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.config-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-ink-light);
  line-height: 1;
}

.close-btn:hover {
  color: var(--color-ink);
}

.config-tabs {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: 2px solid var(--color-border);
  background: var(--color-paper);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: var(--color-vermilion-light);
}

.tab-btn.active {
  border-color: var(--color-vermilion);
  background: var(--color-vermilion);
  color: var(--color-white);
}

.config-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.form-group input[type="text"],
.form-group input[type="url"],
.form-group input[type="password"] {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-vermilion);
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-cancel,
.btn-save {
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--color-paper);
  border: 2px solid var(--color-border);
  color: var(--color-ink);
}

.btn-cancel:hover {
  border-color: var(--color-ink-light);
}

.btn-save {
  background: var(--color-vermilion);
  border: none;
  color: var(--color-white);
}

.btn-save:hover {
  background: var(--color-vermilion-light);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.saved-configs {
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-paper);
}

.saved-configs h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--color-ink-light);
}

.config-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--color-white);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
}

.config-name {
  font-weight: 500;
  text-transform: capitalize;
}

.config-model {
  color: var(--color-ink-light);
  font-size: 0.85rem;
}

.config-default {
  background: var(--color-vermilion);
  color: var(--color-white);
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.btn-edit {
  margin-left: auto;
  padding: 4px 12px;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-edit:hover {
  border-color: var(--color-vermilion);
  color: var(--color-vermilion);
}
</style>
