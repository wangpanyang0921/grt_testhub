<template>
  <div class="page-container">
    <div class="page-header-card">
      <div class="page-header-content">
        <h1>{{ $t('generationConfig.title') }}</h1>
      </div>
      <el-button type="primary" class="create-btn" @click="openAddModal">
        <el-icon><Plus /></el-icon>
        {{ $t('generationConfig.addConfig') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="configs" v-loading="loading" stripe style="width: 100%">
        <el-table-column :label="$t('generationConfig.configName')" min-width="180" show-overflow-tooltip header-align="center" align="left">
          <template #default="{ row }">
            <div class="config-name-cell">{{ row.name || $t('generationConfig.unnamed') }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('generationConfig.outputMode')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <span class="mode-badge">
              {{ row.default_output_mode === 'stream' ? $t('generationConfig.streamMode') : $t('generationConfig.completeMode') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('generationConfig.aiReview')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span class="review-badge" :class="{ enabled: row.enable_auto_review }">
              {{ row.enable_auto_review ? $t('generationConfig.enabled') : $t('generationConfig.disabled') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('generationConfig.reviewTimeout')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <span class="timeout-value">{{ row.review_timeout }} {{ $t('generationConfig.seconds') }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('generationConfig.status')" width="90" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="{ active: row.is_active }">
              {{ row.is_active ? $t('generationConfig.enabled') : $t('generationConfig.disabled') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('generationConfig.operation')" width="280" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button v-if="!row.is_active" size="small" type="success" class="action-btn enable-btn" @click="enableConfig(row.id)">
                <el-icon><Check /></el-icon>
                <span>{{ $t('generationConfig.enable') }}</span>
              </el-button>
              <el-button size="small" type="primary" class="action-btn edit-btn" @click="editConfig(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('generationConfig.edit') }}</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteConfig(row.id)">
                <el-icon><Delete /></el-icon>
                <span>{{ $t('generationConfig.delete') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="configs.length === 0" class="empty-state">
        <div class="empty-icon">⚙️</div>
        <h3>{{ $t('generationConfig.emptyTitle') }}</h3>
        <p>{{ $t('generationConfig.emptyDescription') }}</p>
        <el-button type="primary" class="add-first-config-btn" @click="openAddModal">
          {{ $t('generationConfig.addFirstConfig') }}
        </el-button>
      </div>
    </div>

    <el-dialog v-model="showModal" :title="isEditing ? $t('generationConfig.editTitle') : $t('generationConfig.addTitle')" width="600px" :close-on-click-modal="false" class="config-dialog">
      <el-form :model="configForm" ref="configFormRef" label-width="110px" class="config-form">
        <el-form-item :class="{ 'is-error': formErrors.name }">
          <template #label>
            <span>{{ $t('generationConfig.configName') }}</span><span class="required-star">*</span>
          </template>
          <el-input v-model="configForm.name" :placeholder="$t('generationConfig.configNamePlaceholder')" />
          <div v-if="formErrors.name" class="error-message">{{ formErrors.name }}</div>
        </el-form-item>
        <el-form-item :class="{ 'is-error': formErrors.default_output_mode }">
          <template #label>
            <span>{{ $t('generationConfig.defaultOutputMode') }}</span><span class="required-star">*</span>
          </template>
          <el-select v-model="configForm.default_output_mode" :placeholder="$t('generationConfig.selectOutputMode')" style="width: 100%">
            <el-option value="stream" :label="$t('generationConfig.realtimeStream')" />
            <el-option value="complete" :label="$t('generationConfig.completeOutput')" />
          </el-select>
          <div v-if="formErrors.default_output_mode" class="error-message">{{ formErrors.default_output_mode }}</div>
          <div class="form-hint">{{ $t('generationConfig.outputModeHint') }}</div>
        </el-form-item>
        <el-form-item>
          <template #label>
            <span>{{ $t('generationConfig.automationSettings') }}</span>
          </template>
          <el-checkbox v-model="configForm.enable_auto_review">
            {{ $t('generationConfig.enableAutoReview') }}
          </el-checkbox>
          <div class="form-hint">{{ $t('generationConfig.autoReviewHint') }}</div>
        </el-form-item>
        <el-form-item>
          <template #label>
            <span>{{ $t('generationConfig.reviewTimeoutLabel') }}</span>
          </template>
          <el-input v-model.number="configForm.review_timeout" type="number" :min="10" :max="3600" style="width: 200px" />
          <div class="form-hint">{{ $t('generationConfig.timeoutHint') }}</div>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="configForm.is_active">
            {{ $t('generationConfig.enableThisConfig') }}
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="closeModals">{{ $t('generationConfig.cancel') }}</el-button>
          <el-button type="primary" class="save-btn" @click="saveConfig" :loading="isSaving">
            {{ $t('generationConfig.saveConfig') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getGenerationConfigs, createGenerationConfig, updateGenerationConfig, deleteGenerationConfig } from '@/api/requirement-analysis'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, Edit, Delete, Check } from '@element-plus/icons-vue'

export default {
  name: 'GenerationConfigView',
  components: {
    Plus,
    Edit,
    Delete,
    Check
  },
  setup() {
    const { t, locale } = useI18n()
    return { t, locale }
  },
  data() {
    return {
      configs: [],
      loading: false,
      showModal: false,
      isEditing: false,
      isSaving: false,
      editingConfigId: null,
      configForm: {
        name: '',
        default_output_mode: 'stream',
        enable_auto_review: true,
        review_timeout: 1500,
        is_active: true
      },
      formErrors: {
        name: '',
        default_output_mode: ''
      }
    }
  },

  mounted() {
    this.configForm.name = this.t('generationConfig.defaultConfigName')
    this.loadConfigs()
  },

  methods: {
    openAddModal() {
      this.resetForm()
      this.clearFormErrors()
      this.isEditing = false
      this.showModal = true
    },

    async loadConfigs() {
      this.loading = true
      try {
        console.log('Loading generation configs...')
        const response = await getGenerationConfigs()
        console.log('Generation configs API response:', response.data)

        // 处理分页API响应格式
        if (response.data && response.data.results && Array.isArray(response.data.results)) {
          this.configs = response.data.results
        } else if (response.data && Array.isArray(response.data)) {
          this.configs = response.data
        } else {
          console.warn('Unexpected API response format:', response.data)
          this.configs = []
        }

        console.log('Final configs count:', this.configs.length)
      } catch (error) {
        console.error('Failed to load config:', error)
        this.configs = []

        if (error.response?.status === 401) {
          ElMessage.error(this.t('generationConfig.pleaseLogin'))
        } else {
          ElMessage.error(this.t('generationConfig.loadFailed') + ': ' + (error.response?.data?.error || error.message))
        }
      } finally {
        this.loading = false
      }
    },

    resetForm() {
      this.configForm = {
        name: this.t('generationConfig.defaultConfigName'),
        default_output_mode: 'stream',
        enable_auto_review: true,
        review_timeout: 1500,
        is_active: true
      }
    },

    clearFormErrors() {
      this.formErrors = {
        name: '',
        default_output_mode: ''
      }
    },

    validateForm() {
      this.clearFormErrors()
      let isValid = true

      if (!this.configForm.name || this.configForm.name.trim() === '') {
        this.formErrors.name = this.t('generationConfig.nameRequired')
        isValid = false
      }

      if (!this.configForm.default_output_mode) {
        this.formErrors.default_output_mode = this.t('generationConfig.outputModeRequired')
        isValid = false
      }

      return isValid
    },

    editConfig(config) {
      this.isEditing = true
      this.editingConfigId = config.id
      this.configForm = {
        name: config.name,
        default_output_mode: config.default_output_mode,
        enable_auto_review: config.enable_auto_review,
        review_timeout: config.review_timeout,
        is_active: config.is_active
      }
      this.clearFormErrors()
      this.showModal = true
    },

    async saveConfig() {
      if (!this.validateForm()) {
        return
      }

      this.isSaving = true

      try {
        if (this.isEditing) {
          await updateGenerationConfig(this.editingConfigId, this.configForm)
          ElMessage.success(this.t('generationConfig.updateSuccess'))
        } else {
          await createGenerationConfig(this.configForm)
          ElMessage.success(this.t('generationConfig.saveSuccess'))
        }

        this.closeModals()
        this.loadConfigs()
      } catch (error) {
        console.error('Failed to save config:', error)
        ElMessage.error(this.t('generationConfig.saveFailed') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.isSaving = false
      }
    },

    async enableConfig(configId) {
      try {
        await api.post(`/requirement-analysis/generation-config/${configId}/enable/`)
        ElMessage.success(this.t('generationConfig.enableSuccess'))
        this.loadConfigs()
      } catch (error) {
        console.error('Failed to enable config:', error)
        ElMessage.error(this.t('generationConfig.enableFailed') + ': ' + (error.response?.data?.error || error.message))
      }
    },

    async deleteConfig(configId) {
      try {
        await ElMessageBox.confirm(
          this.t('generationConfig.deleteConfirm'),
          this.t('generationConfig.deleteTitle'),
          {
            confirmButtonText: this.t('generationConfig.confirm'),
            cancelButtonText: this.t('generationConfig.cancel'),
            type: 'warning'
          }
        )
      } catch {
        return
      }

      try {
        await deleteGenerationConfig(configId)
        ElMessage.success(this.t('generationConfig.deleteSuccess'))
        this.loadConfigs()
      } catch (error) {
        console.error('Failed to delete config:', error)
        ElMessage.error(this.t('generationConfig.deleteFailed') + ': ' + (error.response?.data?.error || error.message))
      }
    },

    closeModals() {
      this.showModal = false
      this.isEditing = false
      this.editingConfigId = null
      this.resetForm()
    }
  }
}
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
  line-height: 24px;
  gap: 20px;
  width: calc(100% + 40px);
  box-sizing: border-box;
  padding: 24px;
}

.page-header-card {
  padding: 24px 28px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-header-content {
  display: flex;
  align-items: center;
}

.page-header-content h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  line-height: 1.4;
}

.create-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

  .el-icon {
    margin-right: 6px;
  }

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4) !important;
  }
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: 16px;
}

.config-name-cell {
  padding: 4px 8px;
  line-height: 1.6;
  font-weight: 400;
  color: #333;
  text-align: center;
}

.mode-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  background: #e6f7ff;
  color: #1890ff;
}

.review-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  background: #fff1f0;
  color: #f5222d;
}

.review-badge.enabled {
  background: #f6ffed;
  color: #52c41a;
}

.timeout-value {
  font-size: 14px;
  color: #333;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  background: #fff1f0;
  color: #f5222d;
}

.status-badge.active {
  background: #f6ffed;
  color: #52c41a;
}

.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px !important;
  min-width: 32px;

  .el-icon {
    font-size: 14px;
  }
}

.enable-btn {
  background: #52c41a;
  border-color: #52c41a;
}

.enable-btn:hover {
  background: #45a314;
  border-color: #45a314;
}

.edit-btn {
  background: #7b42f6;
  border-color: #7b42f6;
}

.edit-btn:hover {
  background: #6d33e6;
  border-color: #6d33e6;
}

.delete-btn {
  background: #ff4d4f;
  border-color: #ff4d4f;
}

.delete-btn:hover {
  background: #e03c3e;
  border-color: #e03c3e;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #6d5d8f;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #5a32a3;
  margin-bottom: 10px;
  font-size: 1.3rem;
  font-weight: 600;
}

.empty-state p {
  color: #6d5d8f;
  margin-bottom: 24px;
}

.add-first-config-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border: none;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.2);
}

.add-first-config-btn:hover {
  background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(147, 112, 219, 0.3);
}

:deep(.el-table) {
  border: none;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  min-height: 200px;
  box-shadow: none;
  transition: all 0.3s ease;
  background-color: transparent !important;

  --el-color-primary: #7b42f6;
  --el-color-primary-light-3: #9370db;
  --el-color-primary-light-5: #a888e0;
  --el-color-primary-light-7: #c2a9f3;
  --el-color-primary-light-9: #f8f7ff;
  --el-border-color: #e9ecef;
  --el-border-color-light: #e9ecef;
  --el-border-color-lighter: #e9ecef;
  --el-fill-color-light: #ffffff;
  --el-fill-color-lighter: #ffffff;
  --el-fill-color-blank: #ffffff;
  --el-text-color-primary: #333;
  --el-text-color-regular: #333;
  --el-text-color-secondary: #666;
  --el-text-color-placeholder: #999;
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;
  --el-table-stripe-bg-color: #fafaff;

  &::before {
    display: none;
  }

  :deep(.el-table__header-wrapper) {
    background-color: #ffffff !important;

    :deep(.el-table__header) {
      background-color: #ffffff !important;

      :deep(th) {
        background-color: #ffffff !important;
        color: #5a32a3;
        font-weight: 600;
        font-size: 14px;
        border-bottom: 1px solid #e9ecef;
        padding: 16px;
        text-align: center;
        line-height: 24px;
        transition: all 0.3s ease;

        &:hover {
          background-color: #ffffff !important;
        }
      }
    }
  }

  :deep(.el-table__body-wrapper) {
    :deep(.el-table__body) {
      :deep(tr) {
        transition: all 0.3s ease;

        &:hover {
          background-color: #f8f7ff !important;
        }

        &.el-table__row--striped {
          background-color: #fafaff !important;
        }
      }

      :deep(td) {
        border-bottom: 1px solid #e9ecef;
        padding: 16px;
        color: #333;
        transition: all 0.3s ease;
      }
    }
  }
}

.config-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
  border-bottom: 1px solid rgba(147, 112, 219, 0.15);
  padding: 20px 24px;
  margin-right: 0;
}

.config-dialog :deep(.el-dialog__title) {
  color: #5a32a3;
  font-weight: 600;
  font-size: 1.2rem;
}

.config-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.config-form :deep(.el-form-item__label) {
  color: #5a32a3;
  font-weight: 500;
}

.required-star {
  color: #ff4d4f;
  margin-left: 4px;
}

.form-hint {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
  line-height: 1.5;
}

.error-message {
  color: #ff4d4f;
  font-size: 0.8rem;
  margin-top: 4px;
}

:deep(.el-form-item.is-error .el-input__wrapper) {
  box-shadow: 0 0 0 1px #ff4d4f inset;
}

/* 下拉选择框样式 - 紫色主题 */
:deep(.el-select .el-input__wrapper) {
  box-shadow: 0 0 0 1px #7b42f6 inset !important;
}

:deep(.el-select .el-input.is-focus .el-input__wrapper),
:deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #7b42f6 inset !important;
}

:deep(.el-select:hover .el-input__wrapper) {
  box-shadow: 0 0 0 1px #7b42f6 inset !important;
}

/* 覆盖 Element Plus 默认的聚焦样式 */
:deep(.el-select .el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 1px #7b42f6 inset !important;
}

/* 针对展开状态的下拉框 */
:deep(.el-select.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 1px #7b42f6 inset !important;
}

/* 针对激活状态 */
:deep(.el-select .el-input__wrapper--focus) {
  box-shadow: 0 0 0 1px #7b42f6 inset !important;
}

/* 全局覆盖 */
:deep(.el-select .el-input__inner) {
  box-shadow: none !important;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
}

.cancel-btn {
  padding: 10px 24px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.save-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
    margin: -16px;
    min-height: calc(100% + 32px);
  }

  .page-header-card {
    padding: 20px;
    flex-direction: column;
    align-items: flex-start;
  }

  .page-header-content h1 {
    font-size: 1.4rem;
  }

  .create-btn {
    width: 100%;
    justify-content: center;
  }

  .card-container {
    padding: 16px;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .action-btn {
    padding: 4px 8px;
    font-size: 0.8rem;
  }

  .action-btn span {
    display: none;
  }
}
</style>
