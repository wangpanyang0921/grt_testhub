<template>
  <el-dialog
    v-model="visible"
    :title="$t('apiTesting.apifox.importTitle')"
    width="600px"
    :close-on-click-modal="false"
    custom-class="apifox-import-dialog"
    destroy-on-close
  >
    <div class="import-container">
      <!-- 步骤 1: 上传 + 验证 + 配置 -->
      <div v-if="currentStep === 0" class="step-content">
        <!-- 未上传文件时显示上传区域 -->
        <template v-if="!selectedFile">
          <div class="upload-section">
            <el-upload
              ref="uploadRef"
              class="apifox-uploader"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :limit="1"
              accept=".json"
            >
              <el-icon class="upload-icon"><upload-filled /></el-icon>
              <div class="upload-text">
                <span class="primary-text">{{ $t('apiTesting.apifox.dragText') }}</span>
                <span class="secondary-text">{{ $t('apiTesting.apifox.supportFormat') }}</span>
              </div>
            </el-upload>
          </div>
        </template>

        <!-- 验证中状态 -->
        <div v-if="validationStatus === 'validating'" class="status-section">
          <el-progress :percentage="validationProgress" :indeterminate="true" status="exception" />
          <p class="status-text">{{ $t('apiTesting.apifox.validating') }}</p>
        </div>

        <!-- 验证成功 - 显示文件信息和配置 -->
        <template v-else-if="validationStatus === 'success' || validationStatus === 'warning'">
          <!-- 文件信息卡片 -->
          <div class="file-info-card">
            <div class="file-info-header">
              <el-icon class="file-icon"><document /></el-icon>
              <div class="file-info-content">
                <span class="file-name">{{ selectedFile?.name }}</span>
                <span class="file-meta">共 {{ validationResult.total_requests }} 个请求</span>
              </div>
              <el-button link type="danger" size="small" @click="handleFileRemove">
                {{ $t('common.delete') }}
              </el-button>
            </div>
          </div>

          <!-- 警告信息 -->
          <el-alert
            v-if="validationStatus === 'warning' && validationResult.unsupported_functions?.length"
            :title="$t('apiTesting.apifox.unsupportedFunctions')"
            type="warning"
            :closable="false"
            class="warning-alert"
          >
            <div class="unsupported-list">
              <el-tag
                v-for="func in validationResult.unsupported_functions"
                :key="func"
                type="danger"
                size="small"
              >
                {{ func }}
              </el-tag>
            </div>
          </el-alert>

          <!-- 配置表单 -->
          <el-form :model="importConfig" label-position="top" class="import-form">
            <el-form-item :label="$t('apiTesting.apifox.labels.targetProject')" required>
              <el-select
                v-model="importConfig.projectId"
                :placeholder="$t('apiTesting.apifox.placeholders.selectProject')"
                @change="handleProjectChange"
                class="full-width"
              >
                <el-option
                  v-for="project in projectList"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item :label="$t('apiTesting.apifox.labels.targetCollection')">
              <el-select
                v-model="importConfig.collectionId"
                :placeholder="$t('apiTesting.apifox.placeholders.selectCollection')"
                clearable
                class="full-width"
              >
                <el-option
                  v-for="collection in collectionList"
                  :key="collection.id"
                  :label="collection.name"
                  :value="collection.id"
                />
              </el-select>
              <div class="form-hint">{{ $t('apiTesting.apifox.hints.newCollectionIfEmpty') }}</div>
            </el-form-item>
          </el-form>
        </template>

        <!-- 验证错误 -->
        <el-result
          v-else-if="validationStatus === 'error'"
          icon="error"
          :title="$t('apiTesting.apifox.validationError')"
          :sub-title="validationError"
        />
      </div>

      <!-- 步骤 2: 导入结果 -->
      <div v-if="currentStep === 1" class="step-content">
        <el-result
          v-if="importStatus === 'importing'"
          icon="info"
          :title="$t('apiTesting.apifox.importing')"
        >
          <template #extra>
            <el-progress :percentage="importProgress" />
          </template>
        </el-result>

        <template v-else-if="importStatus === 'success'">
          <el-result
            icon="success"
            :title="$t('apiTesting.apifox.importSuccess')"
            :sub-title="$t('apiTesting.apifox.importSuccessDesc')"
          >
            <template #extra>
              <el-descriptions :column="2" border class="result-descriptions">
                <el-descriptions-item :label="$t('apiTesting.apifox.labels.createdCollection')">
                  <el-link type="primary" @click="navigateToCollection">
                    {{ importResult.collection_name }}
                  </el-link>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('apiTesting.apifox.labels.createdSuite')">
                  <el-link type="primary" @click="navigateToSuite">
                    {{ importResult.suite_name }}
                  </el-link>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('apiTesting.apifox.labels.importedRequests')">
                  <el-tag type="success">{{ importResult.imported_requests }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item :label="$t('apiTesting.apifox.labels.importTime')">
                  {{ importResult.import_time }}
                </el-descriptions-item>
              </el-descriptions>

              <div v-if="importResult.warnings?.length" class="import-warnings">
                <el-alert
                  :title="$t('apiTesting.apifox.importWarnings')"
                  type="warning"
                  :closable="false"
                >
                  <ul>
                    <li v-for="(warning, index) in importResult.warnings" :key="index">
                      {{ warning }}
                    </li>
                  </ul>
                </el-alert>
              </div>
            </template>
          </el-result>
        </template>

        <el-result
          v-else-if="importStatus === 'error'"
          icon="error"
          :title="$t('apiTesting.apifox.importError')"
          :sub-title="importError"
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button v-if="currentStep === 1 && importStatus !== 'importing'" @click="handlePrev">
          {{ $t('common.previous') }}
        </el-button>
        <el-button
          v-if="currentStep === 0 && (validationStatus === 'success' || validationStatus === 'warning')"
          type="primary"
          @click="handleImport"
          :loading="processing"
          :disabled="!importConfig.projectId"
        >
          {{ $t('apiTesting.apifox.buttons.startImport') }}
        </el-button>
        <el-button v-if="currentStep === 1 && importStatus === 'success'" type="primary" @click="handleFinish">
          {{ $t('common.finish') }}
        </el-button>
        <el-button v-if="currentStep === 1 && importStatus === 'error'" type="primary" @click="handleRetry">
          {{ $t('common.retry') }}
        </el-button>
        <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, CircleCheckFilled, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'

const { t } = useI18n()
const router = useRouter()

const props = defineProps({
  modelValue: Boolean,
  projects: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 步骤控制 (0: 配置, 1: 结果)
const currentStep = ref(0)
const processing = ref(false)

// 文件上传
const uploadRef = ref(null)
const selectedFile = ref(null)

// 验证状态
const validationStatus = ref('')
const validationProgress = ref(0)
const validationResult = ref({
  valid: false,
  unsupported_functions: [],
  total_requests: 0,
  warnings: [],
  scenario_name: ''
})
const validationError = ref('')

// 导入配置
const importConfig = ref({
  projectId: '',
  collectionId: '',
  importEnv: false
})

// 数据列表
const projectList = ref([])
const collectionList = ref([])

// 导入状态
const importStatus = ref('')
const importProgress = ref(0)
const importResult = ref({
  collection_id: null,
  collection_name: '',
  suite_id: null,
  suite_name: '',
  imported_requests: 0,
  import_time: '',
  warnings: []
})
const importError = ref('')

// 监听对话框打开
watch(() => props.modelValue, (val) => {
  if (val) {
    resetState()
    loadProjects()
  }
})

watch(() => props.projects, (val) => {
  projectList.value = val
}, { immediate: true })

// 方法
const resetState = () => {
  currentStep.value = 0
  selectedFile.value = null
  validationStatus.value = ''
  validationProgress.value = 0
  validationResult.value = { valid: false, unsupported_functions: [], total_requests: 0, warnings: [], scenario_name: '' }
  validationError.value = ''
  importConfig.value = { projectId: '', collectionId: '', importEnv: false }
  collectionList.value = []
  importStatus.value = ''
  importProgress.value = 0
  importResult.value = { collection_id: null, collection_name: '', suite_id: null, suite_name: '', imported_requests: 0, import_time: '', warnings: [] }
  importError.value = ''

  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const loadProjects = async () => {
  try {
    const response = await api.get('/api-testing/projects/')
    projectList.value = response.data.results || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file
  // 自动开始验证
  if (file) {
    setTimeout(() => {
      validateFile()
    }, 300)
  }
}

const handleFileRemove = () => {
  selectedFile.value = null
  validationStatus.value = ''
  validationResult.value = { valid: false, unsupported_functions: [], total_requests: 0, warnings: [], scenario_name: '' }
}

const handleProjectChange = async (projectId) => {
  importConfig.value.collectionId = ''
  if (!projectId) {
    collectionList.value = []
    return
  }

  try {
    const response = await api.get(`/api-testing/collections/?project=${projectId}`)
    collectionList.value = response.data.results || []
  } catch (error) {
    console.error('加载集合列表失败:', error)
    collectionList.value = []
  }
}

const validateFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning(t('apiTesting.apifox.messages.selectFile'))
    return false
  }

  processing.value = true
  validationStatus.value = 'validating'
  validationProgress.value = 0

  const formData = new FormData()
  formData.append('file', selectedFile.value.raw)

  try {
    const response = await api.post('/api-testing/apifox/validate/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        validationProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })

    validationResult.value = response.data

    if (response.data.unsupported_functions?.length > 0) {
      validationStatus.value = 'warning'
    } else {
      validationStatus.value = 'success'
    }

    return true
  } catch (error) {
    validationStatus.value = 'error'
    validationError.value = error.response?.data?.error || error.message
    ElMessage.error(t('apiTesting.apifox.messages.validationFailed'))
    return false
  } finally {
    processing.value = false
  }
}

const handleImport = async () => {
  if (!importConfig.value.projectId) {
    ElMessage.warning(t('apiTesting.apifox.messages.selectProject'))
    return
  }

  processing.value = true
  importStatus.value = 'importing'
  importProgress.value = 0
  currentStep.value = 1

  const formData = new FormData()
  formData.append('file', selectedFile.value.raw)
  formData.append('project_id', importConfig.value.projectId)
  if (importConfig.value.collectionId) {
    formData.append('collection_id', importConfig.value.collectionId)
  }
  formData.append('import_env', String(importConfig.value.importEnv))

  const startTime = Date.now()

  try {
    const response = await api.post('/api-testing/apifox/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        importProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })

    const endTime = Date.now()

    importResult.value = {
      ...response.data,
      import_time: `${((endTime - startTime) / 1000).toFixed(2)}s`,
      imported_requests: response.data.stats?.requests_created || 0,
      collection_name: response.data.collection_name || t('apiTesting.apifox.defaultCollectionName'),
      suite_name: response.data.suite_name || t('apiTesting.apifox.defaultSuiteName'),
      warnings: response.data.warnings || []
    }

    importStatus.value = 'success'
    ElMessage.success(t('apiTesting.apifox.messages.importSuccess'))
    emit('success', response.data)
  } catch (error) {
    importStatus.value = 'error'
    importError.value = error.response?.data?.error || error.message
    ElMessage.error(t('apiTesting.apifox.messages.importFailed'))
  } finally {
    processing.value = false
  }
}

const handlePrev = () => {
  currentStep.value = 0
}

const handleCancel = () => {
  if (importStatus.value === 'importing') {
    ElMessageBox.confirm(
      t('apiTesting.apifox.messages.confirmCancel'),
      t('common.warning'),
      { confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel'), type: 'warning' }
    ).then(() => {
      visible.value = false
    })
  } else {
    visible.value = false
  }
}

const handleFinish = () => {
  visible.value = false
}

const handleRetry = () => {
  currentStep.value = 0
  importStatus.value = ''
  handleImport()
}

const navigateToCollection = () => {
  if (importResult.value.collection_id) {
    router.push(`/api-testing/collections/${importResult.value.collection_id}`)
    visible.value = false
  }
}

const navigateToSuite = () => {
  if (importResult.value.suite_id) {
    router.push(`/api-testing/test-suites/${importResult.value.suite_id}`)
    visible.value = false
  }
}
</script>

<style lang="scss" scoped>
.apifox-import-dialog {
  :deep(.el-dialog__body) {
    padding: 20px 30px;
  }
}

.import-container {
  min-height: auto;
}

.step-content {
  padding: 10px 0;
}

// 上传区域
.upload-section {
  margin-bottom: 0;
}

.apifox-uploader {
  :deep(.el-upload) {
    width: 100%;
  }

  :deep(.el-upload-dragger) {
    width: 100%;
    height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: #faf5ff;
    border: 2px dashed #d4a5ff;
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      border-color: #7B2FF7;
      background-color: #f3e8ff;
    }
  }
}

.upload-icon {
  font-size: 40px;
  color: #7B2FF7;
  margin-bottom: 12px;
}

.upload-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;

  .primary-text {
    font-size: 15px;
    color: #303133;
  }

  .secondary-text {
    font-size: 12px;
    color: #909399;
  }
}

// 状态区域
.status-section {
  margin-top: 20px;
  text-align: center;

  .status-text {
    margin-top: 10px;
    color: #606266;
    font-size: 14px;
  }
}

// 文件信息卡片
.file-info-card {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;

  .file-info-header {
    display: flex;
    align-items: center;
    gap: 12px;

    .file-icon {
      font-size: 32px;
      color: #7B2FF7;
    }

    .file-info-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;

      .file-name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        word-break: break-all;
      }

      .file-meta {
        font-size: 12px;
        color: #67c23a;
      }
    }
  }
}

.warning-alert {
  margin-bottom: 16px;
}

.unsupported-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

// 表单样式
.import-form {
  margin: 16px 0;
}

.full-width {
  width: 100%;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

// 结果样式
.result-descriptions {
  margin-bottom: 16px;
}

.import-warnings {
  margin-top: 16px;
  text-align: left;

  ul {
    margin: 8px 0 0 0;
    padding-left: 20px;

    li {
      margin-bottom: 4px;
      color: #e6a23c;
    }
  }
}

// 底部按钮
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
