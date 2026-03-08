<template>
  <div class="page-container">
    <div class="card-container">
      <el-form :model="form" :rules="rules" ref="configForm" label-width="120px" class="config-form">
        <el-form-item :label="$t('configuration.dify.apiUrl')" prop="api_url">
          <el-input
            v-model="form.api_url"
            :placeholder="$t('configuration.dify.apiUrlPlaceholder')"
            clearable
          />
          <div class="form-tip">{{ $t('configuration.dify.apiUrlTip') }}</div>
        </el-form-item>

        <el-form-item :label="$t('configuration.dify.apiKey')" prop="api_key">
          <el-input
            v-model="form.api_key"
            type="password"
            :placeholder="currentConfig ? $t('configuration.dify.apiKeyPlaceholderEdit') : $t('configuration.dify.apiKeyPlaceholder')"
            show-password
            clearable
          />
          <div class="form-tip">{{ $t('configuration.dify.apiKeyTip') }}</div>
        </el-form-item>

        <el-form-item :label="$t('configuration.dify.enableStatus')" prop="is_active">
          <el-switch v-model="form.is_active" />
          <span class="switch-label">{{ form.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}</span>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button type="primary" class="test-btn" @click="testConnection" :loading="testing">
            <el-icon><Connection /></el-icon>
            {{ $t('configuration.dify.testConnection') }}
          </el-button>
          <el-button type="primary" class="save-btn" @click="saveConfig" :loading="saving">
            <el-icon><Check /></el-icon>
            {{ $t('configuration.common.save') }}
          </el-button>
          <el-button class="reset-btn" @click="resetForm">
            <el-icon><RefreshLeft /></el-icon>
            {{ $t('configuration.common.reset') }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card-container" v-if="currentConfig">
      <div class="section-title">{{ $t('configuration.dify.currentConfig') }}</div>
      <el-descriptions :column="1" border class="config-descriptions">
        <el-descriptions-item :label="$t('configuration.dify.apiUrl')">
          {{ currentConfig.api_url }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('configuration.dify.apiKey')">
          {{ currentConfig.api_key_masked || '****' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('configuration.common.status')">
          <span class="status-badge" :class="{ active: currentConfig.is_active }">
            {{ currentConfig.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('configuration.common.createdAt')">
          {{ formatDate(currentConfig.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('configuration.common.updatedAt')">
          {{ formatDate(currentConfig.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Link, Key, Connection, Check, RefreshLeft } from '@element-plus/icons-vue'
import api from '@/utils/api'

const { t, locale } = useI18n()

const configForm = ref(null)
const currentConfig = ref(null)
const testing = ref(false)
const saving = ref(false)

const form = ref({
  api_url: '',
  api_key: '',
  is_active: true
})

const rules = computed(() => ({
  api_url: [
    { required: true, message: t('configuration.dify.validation.apiUrlRequired'), trigger: 'blur' },
    { type: 'url', message: t('configuration.dify.validation.apiUrlInvalid'), trigger: 'blur' }
  ],
  api_key: [
    { min: 8, message: t('configuration.dify.validation.apiKeyMinLength'), trigger: 'blur' }
  ]
}))

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString(locale.value === 'zh-cn' ? 'zh-CN' : 'en-US')
}

const loadConfig = async () => {
  try {
    const response = await api.get('/assistant/config/dify/')
    currentConfig.value = response.data
    form.value = {
      api_url: response.data.api_url,
      api_key: '', // Don't populate API key for security
      is_active: response.data.is_active
    }
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error(t('configuration.dify.messages.loadFailed'), error)
    }
  }
}

const testConnection = async () => {
  if (!configForm.value) return

  await configForm.value.validate(async (valid) => {
    if (!valid) return

    testing.value = true
    try {
      const response = await api.post('/assistant/config/dify/test_connection/', {
        api_url: form.value.api_url,
        api_key: form.value.api_key
      })

      if (response.data.success) {
        ElMessage.success(t('configuration.dify.messages.testSuccess'))
      } else {
        ElMessage.error(response.data.error || t('configuration.dify.messages.testFailed'))
      }
    } catch (error) {
      console.error(t('configuration.dify.messages.testFailed'), error)
      ElMessage.error(error.response?.data?.error || t('configuration.dify.messages.testFailed'))
    } finally {
      testing.value = false
    }
  })
}

const saveConfig = async () => {
  if (!configForm.value) return

  await configForm.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      // Prepare data to save
      const dataToSave = {
        api_url: form.value.api_url,
        is_active: form.value.is_active
      }

      // Only send API Key if user entered a new one
      if (form.value.api_key && form.value.api_key.trim()) {
        dataToSave.api_key = form.value.api_key
      }

      if (currentConfig.value) {
        // Update existing config
        await api.patch(`/assistant/config/dify/${currentConfig.value.id}/`, dataToSave)
        ElMessage.success(t('configuration.dify.messages.updateSuccess'))
      } else {
        // Create new config - API key is required
        if (!form.value.api_key || !form.value.api_key.trim()) {
          ElMessage.error(t('configuration.dify.messages.apiKeyRequired'))
          saving.value = false
          return
        }
        await api.post('/assistant/config/dify/', dataToSave)
        ElMessage.success(t('configuration.dify.messages.saveSuccess'))
      }

      // Clear API Key input for security
      form.value.api_key = ''
      await loadConfig()
    } catch (error) {
      console.error(t('configuration.dify.messages.saveFailed'), error)
      ElMessage.error(error.response?.data?.error || t('configuration.dify.messages.saveFailed'))
    } finally {
      saving.value = false
    }
  })
}

const resetForm = () => {
  if (configForm.value) {
    configForm.value.resetFields()
  }
  if (currentConfig.value) {
    form.value = {
      api_url: currentConfig.value.api_url,
      api_key: '',
      is_active: currentConfig.value.is_active
    }
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped lang="scss">
.page-container {
  margin: -20px;
  min-height: calc(100% + 40px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
  width: calc(100% + 40px);
  box-sizing: border-box;
  padding: 24px;
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #262626;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;
  }
}

.config-form {
  .el-form-item {
    margin-bottom: 24px;

    :deep(.el-form-item__label) {
      font-weight: 500;
      color: #333;
    }

    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px #d9d9d9 inset;

      &:hover {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }
    }

    :deep(.el-input-group__prepend) {
      background: #f5f5f5;
      border-color: #d9d9d9;
      color: #666;
    }
  }

  .form-actions {
    margin-bottom: 0;
    padding-top: 8px;
  }
}

.form-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 6px;
  line-height: 1.5;
}

.switch-label {
  margin-left: 10px;
  color: #333;
  font-weight: 500;
}

.test-btn {
  background: #52c41a !important;
  border-color: #52c41a !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;

  &:hover {
    background: #73d13d !important;
    border-color: #73d13d !important;
  }

  .el-icon {
    margin-right: 6px;
  }
}

.save-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4) !important;
  }

  .el-icon {
    margin-right: 6px;
  }
}

.reset-btn {
  font-weight: 500 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  border-color: #d9d9d9 !important;
  color: #595959 !important;
  background: #ffffff !important;

  &:hover {
    color: #7b42f6 !important;
    border-color: #7b42f6 !important;
    background: #f8f7ff !important;
  }

  .el-icon {
    margin-right: 6px;
  }
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  background: #fff1f0;
  color: #f5222d;

  &.active {
    background: #f6ffed;
    color: #52c41a;
  }
}

.config-descriptions {
  :deep(.el-descriptions__label) {
    font-weight: 500;
    color: #333;
    background: #fafafa;
    width: 120px;
  }

  :deep(.el-descriptions__content) {
    color: #595959;
  }
}

// 隐藏原始 header
.page-header {
  display: none;
}
</style>
