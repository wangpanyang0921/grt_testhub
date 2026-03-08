<template>
  <div class="page-container">
    <div class="page-header-card">
      <div class="page-header-content">
        <h1>{{ $t('configuration.aiMode.description') }}</h1>
      </div>
      <el-button type="primary" class="create-btn" @click="openAddModal">
        <el-icon><Plus /></el-icon>
        {{ $t('configuration.aiMode.addConfig') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="configs" v-loading="loading" stripe style="width: 100%">
        <el-table-column :label="$t('configuration.aiMode.configName')" min-width="180" show-overflow-tooltip header-align="center" align="center">
          <template #default="{ row }">
            <div class="config-name-cell">{{ row.name || $t('configuration.common.unnamed') }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('configuration.aiMode.modelProvider')" width="130" header-align="center" align="center">
          <template #default="{ row }">
            <span class="provider-badge" :class="row.model_type">
              {{ getProviderLabel(row.model_type) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('configuration.aiMode.modelName')" min-width="200" show-overflow-tooltip header-align="center" align="center">
          <template #default="{ row }">
            <span class="model-name">{{ row.model_name }}</span>
          </template>
        </el-table-column>

        <el-table-column :label="$t('configuration.common.status')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="{ active: row.is_active }">
              {{ row.is_active ? $t('configuration.common.enabled') : $t('configuration.common.disabled') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('configuration.common.operation')" width="260" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="success" class="action-btn test-btn" @click="testConnection(row)" :disabled="row.testing">
                <el-icon><Connection /></el-icon>
                <span>{{ $t('configuration.aiMode.testConnection') }}</span>
              </el-button>
              <el-button size="small" type="primary" class="action-btn edit-btn" @click="editConfig(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('configuration.common.edit') }}</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteConfig(row.id)">
                <el-icon><Delete /></el-icon>
                <span>{{ $t('configuration.common.delete') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="configs.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <h3>{{ $t('configuration.aiMode.emptyTitle') }}</h3>
        <p>{{ $t('configuration.aiMode.emptyDescription') }}</p>
        <el-button type="primary" class="add-first-config-btn" @click="openAddModal">
          {{ $t('configuration.aiMode.addFirstConfig') }}
        </el-button>
      </div>
    </div>

    <el-dialog v-model="showModal" :title="isEditing ? $t('configuration.aiMode.editConfig') : $t('configuration.aiMode.addConfigTitle')" width="600px" :close-on-click-modal="false" class="config-dialog">
      <el-form :model="configForm" ref="configFormRef" label-width="120px" class="config-form">
        <el-form-item :class="{ 'is-error': formErrors.name }">
          <template #label>
            <span>{{ $t('configuration.aiMode.configName') }}</span><span class="required-star">*</span>
          </template>
          <el-input v-model="configForm.name" :placeholder="$t('configuration.aiMode.configNamePlaceholder')" />
          <div v-if="formErrors.name" class="error-message">{{ formErrors.name }}</div>
        </el-form-item>
        <el-form-item :class="{ 'is-error': formErrors.model_type }">
          <template #label>
            <span>{{ $t('configuration.aiMode.modelProvider') }}</span><span class="required-star">*</span>
          </template>
          <el-select v-model="configForm.model_type" :placeholder="$t('configuration.aiMode.selectProvider')" style="width: 100%" @change="onModelTypeChange">
            <el-option value="openai" :label="$t('configuration.aiMode.providers.openai')" />
            <el-option value="azure_openai" :label="$t('configuration.aiMode.providers.azure_openai')" />
            <el-option value="anthropic" :label="$t('configuration.aiMode.providers.anthropic')" />
            <el-option value="google_gemini" :label="$t('configuration.aiMode.providers.google_gemini')" />
            <el-option value="deepseek" :label="$t('configuration.aiMode.providers.deepseek')" />
            <el-option value="siliconflow" :label="$t('configuration.aiMode.providers.siliconflow')" />
            <el-option value="zhipu" :label="$t('configuration.aiMode.providers.zhipu')" />
            <el-option value="other" :label="$t('configuration.aiMode.providers.other')" />
          </el-select>
          <div v-if="formErrors.model_type" class="error-message">{{ formErrors.model_type }}</div>
        </el-form-item>
        <el-form-item :class="{ 'is-error': formErrors.model_name }">
          <template #label>
            <span>{{ $t('configuration.aiMode.modelName') }}</span><span class="required-star">*</span>
          </template>
          <el-input v-model="configForm.model_name" :placeholder="$t('configuration.aiMode.modelNamePlaceholder')" />
          <div v-if="formErrors.model_name" class="error-message">{{ formErrors.model_name }}</div>
        </el-form-item>
        <el-form-item :class="{ 'is-error': formErrors.api_key }">
          <template #label>
            <span>API Key</span><span class="required-star">*</span>
          </template>
          <el-input v-model="configForm.api_key" type="password" show-password :placeholder="isEditing ? $t('configuration.aiMode.apiKeyPlaceholderEdit') : $t('configuration.aiMode.apiKeyPlaceholder')" />
          <div v-if="formErrors.api_key" class="error-message">{{ formErrors.api_key }}</div>
        </el-form-item>
        <el-form-item :class="{ 'is-error': formErrors.base_url }">
          <template #label>
            <span style="white-space: nowrap">API Base URL</span><span class="required-star">*</span>
          </template>
          <el-input v-model="configForm.base_url" :placeholder="$t('configuration.aiMode.baseUrlPlaceholder')" />
          <div v-if="formErrors.base_url" class="error-message">{{ formErrors.base_url }}</div>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="configForm.is_active">
            {{ $t('configuration.aiMode.enableConfig') }}
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="closeModals">{{ $t('configuration.common.cancel') }}</el-button>
          <el-button type="primary" class="test-btn-form" @click="testConnectionInModal" :loading="isTestingInModal">
            {{ isTestingInModal ? $t('configuration.aiMode.testing') : $t('configuration.aiMode.testConnection') }}
          </el-button>
          <el-button type="primary" class="save-btn" @click="saveConfig" :loading="isSaving">
            {{ isSaving ? $t('configuration.aiMode.saving') : $t('configuration.aiMode.saveConfig') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="showTestResult" :title="$t('configuration.aiMode.testResult')" width="520px" class="test-result-dialog">
      <div class="test-result" :class="{ success: testResult.success, error: !testResult.success }">
        <div class="result-icon">
          <el-icon v-if="testResult.success" :size="32" color="#ffffff"><CircleCheckFilled /></el-icon>
          <el-icon v-else :size="32" color="#ffffff"><CircleCloseFilled /></el-icon>
        </div>
        <div class="result-content">
          <h4>{{ testResult.success ? $t('configuration.aiMode.connectionSuccess') : $t('configuration.aiMode.connectionFailed') }}</h4>
          <p>{{ testResult.message }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Connection, Edit, Delete, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'

const { t } = useI18n()

const configs = ref([])
const loading = ref(false)
const showModal = ref(false)
const showTestResult = ref(false)
const isEditing = ref(false)
const isSaving = ref(false)
const isTestingInModal = ref(false)
const editingConfigId = ref(null)
const configFormRef = ref(null)

const configForm = ref({
  name: '',
  model_type: '',
  model_name: '',
  api_key: '',
  base_url: '',
  is_active: true
})

const formErrors = ref({
  name: '',
  model_type: '',
  model_name: '',
  api_key: '',
  base_url: ''
})

const testResult = ref({
  success: false,
  message: ''
})

// 模型提供商与Base URL的映射关系
const modelBaseUrlMap = {
  openai: 'https://api.openai.com/v1',
  azure_openai: '',
  anthropic: 'https://api.anthropic.com',
  google_gemini: '',
  deepseek: 'https://api.deepseek.com',
  siliconflow: 'https://api.siliconflow.cn/v1',
  zhipu: 'https://open.bigmodel.cn/api/paas/v4',
  other: ''
}

const getProviderLabel = (modelType) => {
  const key = `configuration.aiMode.providers.${modelType}`
  const translated = t(key)
  return translated !== key ? translated : modelType
}

const clearFormErrors = () => {
  formErrors.value = {
    name: '',
    model_type: '',
    model_name: '',
    api_key: '',
    base_url: ''
  }
}

const validateForm = () => {
  clearFormErrors()
  let isValid = true

  if (!configForm.value.name || configForm.value.name.trim() === '') {
    formErrors.value.name = t('configuration.aiMode.validation.nameRequired')
    isValid = false
  }
  if (!configForm.value.model_type) {
    formErrors.value.model_type = t('configuration.aiMode.validation.providerRequired')
    isValid = false
  }
  if (!configForm.value.model_name || configForm.value.model_name.trim() === '') {
    formErrors.value.model_name = t('configuration.aiMode.validation.modelNameRequired')
    isValid = false
  }
  if (!configForm.value.api_key || configForm.value.api_key.trim() === '') {
    formErrors.value.api_key = t('configuration.aiMode.validation.apiKeyRequired')
    isValid = false
  }

  return isValid
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const response = await api.get('/ui-automation/ai-models/')
    if (response.data && Array.isArray(response.data)) {
      configs.value = response.data.map(config => ({
        ...config,
        toggling: false,
        testing: false
      }))
    }
  } catch (error) {
    console.error('Load config failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  resetForm()
  clearFormErrors()
  isEditing.value = false
  showModal.value = true
}

const resetForm = () => {
  configForm.value = {
    name: '',
    model_type: '',
    model_name: '',
    api_key: '',
    base_url: '',
    is_active: true
  }
}

const editConfig = (config) => {
  isEditing.value = true
  editingConfigId.value = config.id

  const maskLength = Math.max(config.api_key_length || 8, 8)
  const maskedKey = '*'.repeat(maskLength)

  configForm.value = {
    name: config.name,
    model_type: config.model_type,
    model_name: config.model_name,
    api_key: maskedKey,
    base_url: config.base_url,
    is_active: config.is_active
  }
  clearFormErrors()
  showModal.value = true
}

const onModelTypeChange = () => {
  if (modelBaseUrlMap[configForm.value.model_type]) {
    configForm.value.base_url = modelBaseUrlMap[configForm.value.model_type]
  }
}

const saveConfig = async () => {
  if (!validateForm()) {
    return
  }

  isSaving.value = true

  try {
    const saveData = { ...configForm.value }

    if (isEditing.value) {
      if (!saveData.api_key || saveData.api_key.includes('*')) {
        delete saveData.api_key
      }

      const response = await api.put(`/ui-automation/ai-models/${editingConfigId.value}/`, saveData)

      if (response.data.disabled_configs && response.data.disabled_configs.length > 0) {
        ElMessage.success(
          t('configuration.aiMode.messages.configEnabled', { name: configForm.value.name, configs: response.data.disabled_configs.join(', ') })
        )
      } else {
        ElMessage.success(t('configuration.aiMode.messages.updateSuccess'))
      }
    } else {
      const response = await api.post('/ui-automation/ai-models/', saveData)

      if (response.data.disabled_configs && response.data.disabled_configs.length > 0) {
        ElMessage.success(
          t('configuration.aiMode.messages.configAdded', { name: configForm.value.name, configs: response.data.disabled_configs.join(', ') })
        )
      } else {
        ElMessage.success(t('configuration.aiMode.messages.saveSuccess'))
      }
    }

    closeModals()
    await loadConfigs()
  } catch (error) {
    console.error('Save config failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.saveFailed') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    isSaving.value = false
  }
}

const deleteConfig = async (configId) => {
  try {
    await ElMessageBox.confirm(
      t('configuration.aiMode.messages.deleteConfirm'),
      t('configuration.common.confirm'),
      {
        confirmButtonText: t('configuration.common.confirm'),
        cancelButtonText: t('configuration.common.cancel'),
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    await api.delete(`/ui-automation/ai-models/${configId}/`)
    ElMessage.success(t('configuration.aiMode.messages.deleteSuccess'))
    await loadConfigs()
  } catch (error) {
    console.error('Delete config failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.deleteFailed') + ': ' + (error.response?.data?.error || error.message))
  }
}

const toggleActive = async (config) => {
  if (config.is_active) {
    const activeConfigs = configs.value.filter(c => c.id !== config.id && c.is_active)
    if (activeConfigs.length > 0) {
      const activeConfigNames = activeConfigs.map(c => c.name).join(', ')
      try {
        await ElMessageBox.confirm(
          t('configuration.aiMode.messages.toggleConfirm', { name: config.name, configs: activeConfigNames }),
          t('configuration.common.confirm'),
          {
            confirmButtonText: t('configuration.common.confirm'),
            cancelButtonText: t('configuration.common.cancel'),
            type: 'warning'
          }
        )
      } catch {
        config.is_active = false
        return
      }
    }
  }

  config.toggling = true

  try {
    await api.patch(`/ui-automation/ai-models/${config.id}/`, {
      is_active: config.is_active
    })

    ElMessage.success(t('configuration.aiMode.messages.toggleSuccess', { status: config.is_active ? t('configuration.common.enabled') : t('configuration.common.disabled') }))
    await loadConfigs()
  } catch (error) {
    console.error('Toggle status failed:', error)
    ElMessage.error(t('configuration.aiMode.messages.toggleFailed') + ': ' + (error.response?.data?.error || error.message))
    config.is_active = !config.is_active
  } finally {
    config.toggling = false
  }
}

const testConnection = async (config) => {
  config.testing = true

  try {
    await api.post(
      `/ui-automation/ai-models/${config.id}/test_connection/`,
      {},
      { timeout: 90000 }
    )
    testResult.value = {
      success: true,
      message: t('configuration.aiMode.connectionSuccessMsg')
    }
    showTestResult.value = true
  } catch (error) {
    console.error('Test connection failed:', error)
    testResult.value = {
      success: false,
      message: error.response?.data?.error || error.message || t('configuration.aiMode.connectionFailed')
    }
    showTestResult.value = true
  } finally {
    config.testing = false
  }
}

const testConnectionInModal = async () => {
  if (!configForm.value.api_key) {
    ElMessage.warning(t('configuration.aiMode.messages.enterApiKey'))
    return
  }

  if (!configForm.value.model_type || !configForm.value.model_name) {
    ElMessage.warning(t('configuration.aiMode.messages.selectProviderModel'))
    return
  }

  isTestingInModal.value = true

  try {
    if (isEditing.value && configForm.value.api_key.includes('*')) {
      await api.post(
        `/ui-automation/ai-models/${editingConfigId.value}/test_connection/`,
        {},
        { timeout: 90000 }
      )
    } else {
      await api.post(
        '/ui-automation/ai-models/test_connection/',
        {
          provider: configForm.value.model_type,
          model_name: configForm.value.model_name,
          api_key: configForm.value.api_key,
          base_url: configForm.value.base_url
        },
        { timeout: 90000 }
      )
    }

    testResult.value = {
      success: true,
      message: t('configuration.aiMode.connectionSuccessMsg')
    }
    showTestResult.value = true
  } catch (error) {
    console.error('Test connection failed:', error)
    testResult.value = {
      success: false,
      message: error.response?.data?.error || error.message || t('configuration.aiMode.connectionFailed')
    }
    showTestResult.value = true
  } finally {
    isTestingInModal.value = false
  }
}

const closeModals = () => {
  showModal.value = false
  isEditing.value = false
  editingConfigId.value = null
  resetForm()
}

onMounted(() => {
  loadConfigs()
})
</script>

<style lang="scss" scoped>
:root {
  --primary-color: #7b42f6;
  --primary-dark: #5a32a3;
  --primary-light: #f8f7ff;
  --border-color: #e8e8e8;
  --text-primary: #262626;
  --text-secondary: #595959;
  --text-tertiary: #8c8c8c;
  --bg-light: #ffffff;
  --bg-gray: #fafafa;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #ff4d4f;
  --info-color: #1890ff;
}

.page-container {
  margin: -20px;
  min-height: calc(100% + 40px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  padding: 24px;
  box-sizing: border-box;
}

.page-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 24px 28px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);

  .page-header-content {
    display: flex;
    align-items: center;

    h1 {
      font-size: 20px;
      font-weight: 600;
      color: #262626;
      margin: 0;
    }

    p {
      font-size: 14px;
      color: #8c8c8c;
      margin: 0;
    }
  }

  .create-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
      transform: translateY(-1px);
    }

    .el-icon {
      margin-right: 6px;
    }
  }
}

.card-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  padding: 20px;
  flex: 1;
  overflow: auto;
}

.config-name-cell {
  font-weight: 500;
  color: #262626;
}

.provider-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #f0f0f0;
  color: #595959;

  &.openai { background: #e6f7ff; color: #1890ff; }
  &.azure_openai { background: #e6f4ff; color: #0078d4; }
  &.anthropic { background: #fff2e8; color: #fa8c16; }
  &.google_gemini { background: #e6fffb; color: #13c2c2; }
  &.deepseek { background: #f6ffed; color: #52c41a; }
  &.siliconflow { background: #f9f0ff; color: #722ed1; }
  &.zhipu { background: #fff0f6; color: #eb2f96; }
  &.other { background: #f5f5f5; color: #8c8c8c; }
}

.model-name {
  color: #262626;
  font-weight: 500;
}

.base-url {
  color: #595959;
  font-size: 13px;
  display: block;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0 auto;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #f5f5f5;
  color: #8c8c8c;

  &.active {
    background: #f6ffed;
    color: #52c41a;
  }
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  .action-btn {
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 4px;

    .el-icon {
      font-size: 14px;
    }

    span {
      margin-left: 2px;
    }
  }

  .test-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%);
    }
  }

  .edit-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
    }
  }

  .delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%);
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #8c8c8c;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 18px;
    color: #262626;
    margin-bottom: 8px;
  }

  p {
    margin-bottom: 24px;
    color: #8c8c8c;
  }

  .add-first-config-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    padding: 10px 24px;
    border-radius: 8px;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
    }
  }
}

.config-dialog {
  :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid #e8e8e8;

    .el-dialog__title {
      color: #5a32a3;
      font-weight: 600;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }

  :deep(.el-dialog__footer) {
    padding: 16px 24px;
    border-top: 1px solid #e8e8e8;
  }
}

.config-form {
  .el-form-item {
    margin-bottom: 20px;

    &.is-error {
      :deep(.el-input__wrapper) {
        box-shadow: 0 0 0 1px #ff4d4f inset;
      }
    }
  }

  .required-star {
    color: #ff4d4f;
    margin-left: 4px;
  }

  .error-message {
    color: #ff4d4f;
    font-size: 12px;
    margin-top: 4px;
  }

  .form-hint {
    color: #8c8c8c;
    font-size: 12px;
    margin-top: 4px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .cancel-btn {
    padding: 10px 24px;
    border-radius: 8px;
  }

  .test-btn-form {
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 500;
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%);
    }
  }

  .save-btn {
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 500;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
    }
  }
}

.test-result-dialog {
  :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid #e8e8e8;

    .el-dialog__title {
      color: #5a32a3;
      font-weight: 600;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }
}

.test-result {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding: 20px;
  border-radius: 12px;

  &.success {
    background: #f6ffed;

    .result-icon {
      background: #52c41a;
    }

    h4 {
      color: #52c41a;
    }
  }

  &.error {
    background: #fff2f0;

    .result-icon {
      background: #ff4d4f;
    }

    h4 {
      color: #ff4d4f;
    }
  }

  .result-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .result-content {
    flex: 1;

    h4 {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 600;
    }

    p {
      margin: 0;
      color: #595959;
      line-height: 1.5;
    }
  }
}
</style>
