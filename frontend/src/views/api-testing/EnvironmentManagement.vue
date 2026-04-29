<template>
  <div class="page-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-select
          v-model="activeTab"
          @change="onTabChange"
          class="scope-select"
        >
          <el-option
            :label="$t('apiTesting.environment.scopeTypes.global')"
            value="GLOBAL"
          />
          <el-option
            :label="$t('apiTesting.environment.scopeTypes.local')"
            value="LOCAL"
          />
        </el-select>
        <el-select
          v-if="activeTab === 'LOCAL'"
          v-model="selectedProject"
          :placeholder="$t('apiTesting.common.selectProject')"
          @change="loadLocalEnvironments"
          class="project-select-header"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </div>
      <el-button type="primary" @click="showCreateDialog = true" class="create-btn">
        <el-icon><Plus /></el-icon>
        {{ $t('apiTesting.environment.createEnvironment') }}
      </el-button>
    </div>

    <!-- 环境列表卡片 -->
    <div class="card-container">
      <!-- 全局环境变量表格 -->
      <div v-if="activeTab === 'GLOBAL'" class="table-wrapper">
        <el-table :data="globalEnvironments" v-loading="loading" style="width: 100%" class="custom-table">
          <el-table-column type="index" :label="$t('apiTesting.common.sequence')" width="90" header-align="center" align="center" />
          <el-table-column prop="name" :label="$t('apiTesting.environment.environmentName')" min-width="200" header-align="center" align="center" />
          <el-table-column prop="scope" :label="$t('apiTesting.environment.scope')" width="120" header-align="center" align="center">
            <template #default="scope">
              <span class="scope-badge" :class="scope.row.scope === 'GLOBAL' ? 'global' : 'local'">
                {{ scope.row.scope === 'GLOBAL' ? $t('apiTesting.environment.scopeTypes.global') : $t('apiTesting.environment.scopeTypes.local') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" :label="$t('apiTesting.environment.status')" width="100" header-align="center" align="center">
            <template #default="scope">
              <span class="status-badge" :class="scope.row.is_active ? 'success' : 'default'">
                {{ scope.row.is_active ? $t('apiTesting.environment.activated') : $t('apiTesting.environment.notActivated') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="created_by.username" :label="$t('apiTesting.environment.createdBy')" min-width="100" header-align="center" align="center" show-overflow-tooltip />
          <el-table-column :label="$t('apiTesting.common.operation')" width="380" fixed="right" header-align="center" align="center">
            <template #default="scope">
              <div class="action-buttons">
                <el-button
                  v-if="!scope.row.is_active"
                  size="small"
                  type="success"
                  class="action-btn activate-btn"
                  @click="activateEnvironment(scope.row)"
                >
                  <el-icon><Check /></el-icon>
                  <span>{{ $t('apiTesting.environment.activate') }}</span>
                </el-button>
                <el-button size="small" type="primary" class="action-btn view-btn" @click="viewEnvironment(scope.row)">
                  <el-icon><View /></el-icon>
                  <span>{{ $t('apiTesting.common.view') }}</span>
                </el-button>
                <el-button size="small" type="primary" class="action-btn edit-btn" @click="editEnvironment(scope.row)">
                  <el-icon><Edit /></el-icon>
                  <span>{{ $t('apiTesting.common.edit') }}</span>
                </el-button>
                <el-button size="small" type="info" class="action-btn copy-btn" @click="duplicateEnvironment(scope.row)">
                  <el-icon><CopyDocument /></el-icon>
                  <span>{{ $t('apiTesting.common.copy') }}</span>
                </el-button>
                <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteEnvironment(scope.row)">
                  <el-icon><Delete /></el-icon>
                  <span>{{ $t('apiTesting.common.delete') }}</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <!-- 局部环境变量表格 -->
      <div v-else class="table-wrapper">
        <el-table :data="localEnvironments" v-loading="loading" style="width: 100%" class="custom-table">
          <el-table-column type="index" :label="$t('apiTesting.common.sequence')" width="90" header-align="center" align="center" />
          <el-table-column prop="name" :label="$t('apiTesting.environment.environmentName')" min-width="200" header-align="center" align="center" />
          <el-table-column prop="scope" :label="$t('apiTesting.environment.scope')" width="120" header-align="center" align="center">
            <template #default="scope">
              <span class="scope-badge" :class="scope.row.scope === 'GLOBAL' ? 'global' : 'local'">
                {{ scope.row.scope === 'GLOBAL' ? $t('apiTesting.environment.scopeTypes.global') : $t('apiTesting.environment.scopeTypes.local') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="project_name" :label="$t('apiTesting.environment.relatedProject')" width="150" header-align="center" align="center">
            <template #default="scope">
              <span>{{ scope.row.project_name || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" :label="$t('apiTesting.environment.status')" width="100" header-align="center" align="center">
            <template #default="scope">
              <span class="status-badge" :class="scope.row.is_active ? 'success' : 'default'">
                {{ scope.row.is_active ? $t('apiTesting.environment.activated') : $t('apiTesting.environment.notActivated') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="created_by.username" :label="$t('apiTesting.environment.createdBy')" min-width="100" header-align="center" align="center" show-overflow-tooltip />
          <el-table-column :label="$t('apiTesting.common.operation')" width="380" fixed="right" header-align="center" align="center">
            <template #default="scope">
              <div class="action-buttons">
                <el-button
                  v-if="!scope.row.is_active"
                  size="small"
                  type="success"
                  class="action-btn activate-btn"
                  @click="activateEnvironment(scope.row)"
                >
                  <el-icon><Check /></el-icon>
                  <span>{{ $t('apiTesting.environment.activate') }}</span>
                </el-button>
                <el-button size="small" type="primary" class="action-btn view-btn" @click="viewEnvironment(scope.row)">
                  <el-icon><View /></el-icon>
                  <span>{{ $t('apiTesting.common.view') }}</span>
                </el-button>
                <el-button size="small" type="primary" class="action-btn edit-btn" @click="editEnvironment(scope.row)">
                  <el-icon><Edit /></el-icon>
                  <span>{{ $t('apiTesting.common.edit') }}</span>
                </el-button>
                <el-button size="small" type="info" class="action-btn copy-btn" @click="duplicateEnvironment(scope.row)">
                  <el-icon><CopyDocument /></el-icon>
                  <span>{{ $t('apiTesting.common.copy') }}</span>
                </el-button>
                <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteEnvironment(scope.row)">
                  <el-icon><Delete /></el-icon>
                  <span>{{ $t('apiTesting.common.delete') }}</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 创建/编辑环境对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingEnvironment ? $t('apiTesting.environment.editEnvironment') : $t('apiTesting.environment.createEnvironment')"
      width="800px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item :label="$t('apiTesting.environment.environmentName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('apiTesting.environment.inputEnvironmentName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.environment.scope')" prop="scope">
          <el-radio-group v-model="form.scope" @change="onScopeChange">
            <el-radio value="GLOBAL">{{ $t('apiTesting.environment.scopeTypes.global') }}</el-radio>
            <el-radio value="LOCAL">{{ $t('apiTesting.environment.scopeTypes.local') }}</el-radio>
          </el-radio-group>
          <div class="scope-help">
            <el-text size="small" type="info">
              {{ $t('apiTesting.environment.scopeHelp') }}
            </el-text>
          </div>
        </el-form-item>

        <el-form-item
          v-if="form.scope === 'LOCAL'"
          :label="$t('apiTesting.environment.relatedProject')"
          prop="project"
        >
          <el-select v-model="form.project" :placeholder="$t('apiTesting.environment.selectRelatedProject')">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.environment.environmentVariables')" prop="variables">
          <div class="variables-editor">
            <div class="variables-header">
              <div class="column">{{ $t('apiTesting.environment.variableName') }}</div>
              <div class="column">{{ $t('apiTesting.environment.initialValue') }}</div>
              <div class="column">{{ $t('apiTesting.environment.currentValue') }}</div>
              <div class="column header-column">可被接口引用</div>
              <div class="column">{{ $t('apiTesting.common.operation') }}</div>
            </div>

            <div class="variables-body">
              <div
                v-for="(variable, index) in form.variables"
                :key="index"
                class="variable-row"
              >
                <div class="column">
                  <el-input
                    v-model="variable.key"
                    :placeholder="$t('apiTesting.environment.variableName')"
                    size="small"
                  />
                </div>
                <div class="column">
                  <el-input
                    v-model="variable.initialValue"
                    :placeholder="$t('apiTesting.environment.initialValue')"
                    size="small"
                  />
                </div>
                <div class="column">
                  <el-input
                    v-model="variable.currentValue"
                    :placeholder="$t('apiTesting.environment.currentValue')"
                    size="small"
                  />
                </div>
                <div class="column header-column">
                  <el-switch
                    v-model="variable.isHeader"
                    :active-value="true"
                    :inactive-value="false"
                    size="small"
                  />
                </div>
                <div class="column action-column">
                  <el-button
                    size="small"
                    type="danger"
                    link
                    :icon="Delete"
                    class="variable-delete-btn"
                    @click="removeVariable(index)"
                    :disabled="form.variables.length <= 1"
                  />
                </div>
              </div>
            </div>

            <div class="variables-footer">
              <el-button size="small" @click="addVariable">
                <el-icon><Plus /></el-icon>
                {{ $t('apiTesting.environment.addVariable') }}
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingEnvironment ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看变量对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="$t('apiTesting.environment.environmentVariableDetail')"
      width="900px"
      class="view-dialog"
    >
      <div v-if="viewingEnvironment" class="view-variables">
        <!-- 环境基本信息 -->
        <div class="env-info-section">
          <el-descriptions :column="3" border>
            <el-descriptions-item :label="$t('apiTesting.environment.environmentName')">
              {{ viewingEnvironment.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('apiTesting.environment.scope')">
              <el-tag :type="viewingEnvironment.scope === 'GLOBAL' ? 'primary' : 'success'" size="small">
                {{ viewingEnvironment.scope === 'GLOBAL' ? $t('apiTesting.environment.scopeTypes.global') : $t('apiTesting.environment.scopeTypes.local') }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('apiTesting.environment.status')">
              <el-tag v-if="viewingEnvironment.is_active" type="success" size="small">{{ $t('apiTesting.environment.activated') }}</el-tag>
              <el-tag v-else type="info" size="small">{{ $t('apiTesting.environment.notActivated') }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 变量列表 -->
        <div class="variables-table-section">
          <div class="section-title">{{ $t('apiTesting.component.environmentTable.variableList') }}</div>
          <el-table
            :data="viewVariables"
            style="width: 100%"
            :max-height="400"
            border
            stripe
          >
            <el-table-column type="index" :label="$t('apiTesting.common.sequence')" width="60" align="center" />
            <el-table-column :label="$t('apiTesting.environment.variableName')" min-width="150">
              <template #default="{ row }">
                <el-tooltip
                  v-if="row.key"
                  placement="top"
                  popper-class="table-tooltip"
                  :show-after="500"
                  :disabled="row.key.length < 20"
                >
                  <template #content>
                    <div style="background: #303133; color: #ffffff; padding: 8px 12px; border-radius: 4px; max-width: 380px; max-height: 180px; overflow-y: auto; word-break: break-all; line-height: 1.6;">{{ row.key }}</div>
                  </template>
                  <div class="ellipsis-text">{{ row.key }}</div>
                </el-tooltip>
                <div v-else class="ellipsis-text">{{ row.key || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('apiTesting.environment.initialValue')" min-width="200">
              <template #default="{ row }">
                <el-tooltip
                  v-if="row.initialValue"
                  placement="top"
                  popper-class="table-tooltip"
                  :show-after="500"
                  :disabled="row.initialValue.length < 30"
                >
                  <template #content>
                    <div style="background: #303133; color: #ffffff; padding: 8px 12px; border-radius: 4px; max-width: 380px; max-height: 180px; overflow-y: auto; word-break: break-all; line-height: 1.6;">{{ row.initialValue }}</div>
                  </template>
                  <div class="ellipsis-text">{{ row.initialValue }}</div>
                </el-tooltip>
                <div v-else class="ellipsis-text">{{ row.initialValue || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('apiTesting.environment.currentValue')" min-width="200">
              <template #default="{ row }">
                <el-tooltip
                  v-if="row.currentValue"
                  placement="top"
                  popper-class="table-tooltip"
                  :show-after="500"
                  :disabled="row.currentValue.length < 30"
                >
                  <template #content>
                    <div style="background: #303133; color: #ffffff; padding: 8px 12px; border-radius: 4px; max-width: 380px; max-height: 180px; overflow-y: auto; word-break: break-all; line-height: 1.6;">{{ row.currentValue }}</div>
                  </template>
                  <div class="ellipsis-text">{{ row.currentValue }}</div>
                </el-tooltip>
                <div v-else class="ellipsis-text">{{ row.currentValue || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="isHeader" :label="$t('apiTesting.component.environmentTable.canBeUsedAsHeader')" width="120" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.isHeader" type="success" size="small">是</el-tag>
                <el-tag v-else type="info" size="small">否</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="showViewDialog = false">{{ $t('apiTesting.common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, Delete, Edit, View, Check, CopyDocument } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const { t } = useI18n()
const activeTab = ref('GLOBAL')
const globalEnvironments = ref([])
const localEnvironments = ref([])
const projects = ref([])
const selectedProject = ref(null)
const loading = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingEnvironment = ref(null)
const viewingEnvironment = ref(null)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  scope: 'GLOBAL',
  project: null,
  variables: [
    {
      key: '',
      initialValue: '',
      currentValue: '',
      isHeader: false
    }
  ]
})

const rules = computed(() => ({
  name: [
    { required: true, message: t('apiTesting.environment.inputEnvironmentName'), trigger: 'blur' }
  ],
  scope: [
    { required: true, message: t('apiTesting.common.pleaseSelect'), trigger: 'change' }
  ],
  project: [
    {
      validator: (rule, value, callback) => {
        if (form.scope === 'LOCAL' && !value) {
          callback(new Error(t('apiTesting.environment.selectRelatedProject')))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}))

const viewVariables = computed(() => {
  if (!viewingEnvironment.value?.variables) return []

  const vars = viewingEnvironment.value.variables
  return Object.keys(vars).map(key => {
    const value = vars[key]
    const isObject = typeof value === 'object' && value !== null
    return {
      key,
      initialValue: isObject ? (value.initialValue || '') : (value || ''),
      currentValue: isObject ? (value.currentValue || '') : (value || ''),
      isHeader: isObject ? (value.isHeader !== false) : true
    }
  })
})

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const viewEnvironment = (environment) => {
  viewingEnvironment.value = environment
  showViewDialog.value = true
}

const loadProjects = async () => {
  try {
    const response = await api.get('/api-testing/projects/')
    projects.value = response.data.results || response.data
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.projectListLoadFailed'))
  }
}

const loadGlobalEnvironments = async () => {
  loading.value = true
  try {
    const response = await api.get('/api-testing/environments/', {
      params: { scope: 'GLOBAL' }
    })
    globalEnvironments.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.globalEnvLoadFailed'))
  } finally {
    loading.value = false
  }
}

const loadLocalEnvironments = async () => {
  if (!selectedProject.value) return

  loading.value = true
  try {
    const response = await api.get('/api-testing/environments/', {
      params: {
        scope: 'LOCAL',
        project: selectedProject.value
      }
    })
    localEnvironments.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.localEnvLoadFailed'))
  } finally {
    loading.value = false
  }
}

const onTabChange = (tab) => {
  if (tab === 'GLOBAL') {
    loadGlobalEnvironments()
  } else {
    loadLocalEnvironments()
  }
}

const onScopeChange = () => {
  if (form.scope === 'GLOBAL') {
    form.project = null
  }
}

const addVariable = () => {
  form.variables.push({
    key: '',
    initialValue: '',
    currentValue: '',
    isHeader: false
  })
}

const removeVariable = (index) => {
  if (form.variables.length > 1) {
    form.variables.splice(index, 1)
  }
}

const editEnvironment = (environment) => {
  editingEnvironment.value = environment
  form.name = environment.name
  form.scope = environment.scope
  form.project = environment.project

  // 转换变量格式
  const variables = environment.variables || {}
  form.variables = Object.keys(variables).map(key => {
    const value = variables[key]
    if (typeof value === 'object') {
      return {
        key,
        initialValue: value.initialValue || '',
        currentValue: value.currentValue || '',
        isHeader: value.isHeader !== false // 默认为 true
      }
    } else {
      return {
        key,
        initialValue: value || '',
        currentValue: value || '',
        isHeader: true // 旧数据默认开启
      }
    }
  })

  if (form.variables.length === 0) {
    form.variables.push({
      key: '',
      initialValue: '',
      currentValue: '',
      isHeader: false
    })
  }

  showCreateDialog.value = true
}

const deleteEnvironment = async (environment) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.environment.confirmDeleteEnv', { name: environment.name }),
      t('apiTesting.messages.confirm.deleteTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    await api.delete(`/api-testing/environments/${environment.id}/`)
    ElMessage.success(t('apiTesting.messages.success.delete'))

    if (activeTab.value === 'GLOBAL') {
      await loadGlobalEnvironments()
    } else {
      await loadLocalEnvironments()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    }
  }
}

const activateEnvironment = async (environment) => {
  try {
    await api.post(`/api-testing/environments/${environment.id}/activate/`)
    ElMessage.success(t('apiTesting.messages.success.environmentActivated'))

    if (activeTab.value === 'GLOBAL') {
      await loadGlobalEnvironments()
    } else {
      await loadLocalEnvironments()
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.activateFailed'))
  }
}

const duplicateEnvironment = async (environment) => {
  const newEnv = {
    name: `${environment.name} - Copy`,
    scope: environment.scope,
    project: environment.scope === 'LOCAL' ?
      (typeof environment.project === 'object' ? environment.project.id : environment.project) :
      null,
    variables: environment.variables || {}
  }

  try {
    await api.post('/api-testing/environments/', newEnv)
    ElMessage.success(t('apiTesting.messages.success.copy'))

    if (activeTab.value === 'GLOBAL') {
      await loadGlobalEnvironments()
    } else {
      await loadLocalEnvironments()
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.copyFailed'))
  }
}

const submitForm = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    // 转换变量格式
    const variables = {}
    form.variables.forEach(variable => {
      if (variable.key) {
        variables[variable.key] = {
          initialValue: variable.initialValue || '',
          currentValue: variable.currentValue || variable.initialValue || '',
          isHeader: variable.isHeader !== false // 默认为 true
        }
      }
    })

    const data = {
      name: form.name,
      scope: form.scope,
      project: form.scope === 'LOCAL' ? form.project : null,
      variables
    }

    if (editingEnvironment.value) {
      await api.put(`/api-testing/environments/${editingEnvironment.value.id}/`, data)
      ElMessage.success(t('apiTesting.messages.success.environmentUpdated'))
    } else {
      await api.post('/api-testing/environments/', data)
      ElMessage.success(t('apiTesting.messages.success.environmentCreated'))
    }

    showCreateDialog.value = false

    if (activeTab.value === 'GLOBAL') {
      await loadGlobalEnvironments()
    } else {
      await loadLocalEnvironments()
    }
  } catch (error) {
    ElMessage.error(editingEnvironment.value ? t('apiTesting.messages.error.updateFailed') : t('apiTesting.messages.error.createFailed'))
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingEnvironment.value = null
  Object.assign(form, {
    name: '',
    scope: 'GLOBAL',
    project: null,
    variables: [
      {
        key: '',
        initialValue: '',
        currentValue: ''
      }
    ]
  })
  formRef.value?.resetFields()
}

onMounted(async () => {
  await loadProjects()
  await loadGlobalEnvironments()
  if (selectedProject.value) {
    await loadLocalEnvironments()
  }
})
</script>

<style lang="scss" scoped>
.page-container {
  --primary-color: #7b42f6;
  --primary-light: #a78bfa;
  --primary-lighter: #c4b5fd;
  --primary-lightest: #f5f3ff;
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
  --text-tertiary: #8c8c8c;

  /* 覆盖 Element Plus 默认主题变量 */
  --el-color-primary: var(--primary-color);
  --el-color-primary-light-3: #c4b5fd;
  --el-color-primary-light-5: #ddd6fe;
  --el-color-primary-light-7: #ede9fe;
  --el-color-primary-light-9: #f5f3ff;
  --el-border-color: rgba(167, 139, 250, 0.3);
  --el-border-color-light: rgba(167, 139, 250, 0.2);
  --el-border-color-lighter: rgba(167, 139, 250, 0.1);
  --el-fill-color-light: #f5f3ff;
  --el-fill-color-lighter: #f5f3ff;
  --el-fill-color-blank: #f5f3ff;
  --el-text-color-primary: var(--text-primary);
  --el-text-color-regular: var(--text-secondary);
  --el-text-color-secondary: var(--text-tertiary);

  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  padding: 20px 24px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .scope-select {
    width: 140px;

    :deep(.el-select__wrapper) {
      background-color: #ffffff;
      border: 1px solid rgba(147, 112, 219, 0.2);
      border-radius: 8px;
      box-shadow: none;

      &:hover,
      &.is-focused {
        border-color: #7b42f6;
      }
    }
  }

  .project-select-header {
    width: 200px;

    :deep(.el-select__wrapper) {
      background-color: #ffffff;
      border: 1px solid rgba(147, 112, 219, 0.2);
      border-radius: 8px;
      box-shadow: none;

      &:hover,
      &.is-focused {
        border-color: #7b42f6;
      }
    }
  }

  .page-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #5a32a3;
  }

  .create-btn {
    height: 36px;
    padding: 0 18px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    background: #7b42f6;
    border: 1px solid #7b42f6;
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      background: #6d33e6;
      border-color: #6d33e6;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
    }

    &:active {
      transform: translateY(0);
      background: #5a32a3;
    }

    .el-icon {
      margin-right: 6px;
      font-size: 16px;
    }
  }
}

.card-container {
  flex: 1;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px 24px 24px;
}

.scope-help {
  margin-top: 8px;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
}

.custom-table {
  border: none;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  min-height: 200px;
  box-shadow: none;
  transition: all 0.3s ease;
  background-color: transparent !important;

  /* 覆盖 Element Plus 默认主题变量 */
  --el-color-primary: #667eea;
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
  --el-text-color-primary: #262626;
  --el-text-color-regular: #595959;
  --el-text-color-secondary: #8c8c8c;
  --el-text-color-placeholder: #999;
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;
  --el-table-stripe-bg-color: #fafaff;

  &::before {
    display: none;
  }

  // 表头样式
  :deep(.el-table__header-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(.el-table__header) {
    background-color: #ffffff !important;
  }

  :deep(th) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600;
    font-size: 14px;
    border-bottom: 1px solid #e9ecef;
    padding: 16px !important;
    text-align: center;
    transition: all 0.3s ease;

    &:hover {
      background-color: #ffffff !important;
    }
  }

  :deep(th .cell) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600 !important;
    white-space: normal !important;
    line-height: 20px !important;
    word-break: break-word;
  }

  // 表格内容
  :deep(.el-table__body-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(.el-table__row) {
    transition: all 0.3s ease;
    background-color: #ffffff !important;
    line-height: 24px;

    &:hover {
      background-color: #f8f7ff !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(147, 112, 219, 0.1);
    }

    &.el-table__row--striped {
      background-color: #fafaff !important;
    }

    :deep(td) {
      padding: 14px 8px;
      border-bottom: 1px solid #e9ecef;
      color: #595959;
      font-size: 14px;
      font-weight: normal;
      line-height: 24px;
      transition: all 0.3s ease;

      :deep(.cell) {
        font-size: 14px;
        font-weight: normal;
        color: #595959;
        line-height: 24px;
        white-space: nowrap;
        overflow: visible;
      }
    }
  }

  // 空状态
  :deep(.el-table__empty-block) {
    padding: 60px 0;
    background: #ffffff !important;

    :deep(.el-table__empty-text) {
      color: #666;
      font-size: 14px;
      line-height: 24px;
    }
  }

  // 修复固定列样式
  :deep(.el-table__fixed-right) {
    background-color: #ffffff !important;
    height: 100% !important;
  }

  :deep(.el-table__fixed-right-patch) {
    background-color: #ffffff !important;
  }

  :deep(.el-table__fixed-body-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(.el-table__fixed-header-wrapper) {
    background-color: #ffffff !important;
  }
}

// 作用域徽章样式
.scope-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.global {
    background: #f6ffed;
    color: #52c41a;
  }

  &.local {
    background: #e6f7ff;
    color: #1890ff;
  }
}

// 状态徽章样式
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.success {
    background: #f6ffed;
    color: #52c41a;
  }

  &.default {
    background: #f5f5f5;
    color: #8c8c8c;
  }
}

// 操作按钮容器
.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  flex-wrap: nowrap;
}

// 操作按钮样式
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px !important;
  border-radius: 6px;
  transition: all 0.3s ease;

  .el-icon {
    font-size: 14px;
    color: #ffffff !important;
  }

  span {
    font-size: 12px;
    color: #ffffff !important;
  }

  &.activate-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
    }
  }

  &.view-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
    }
  }

  &.edit-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
    }
  }

  &.copy-btn {
    background: linear-gradient(135deg, #8c8c8c 0%, #595959 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #a6a6a6 0%, #8c8c8c 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(140, 140, 140, 0.4);
    }
  }

  &.delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #f5222d 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(245, 34, 45, 0.4);
    }
  }
}

@media screen and (max-width: 1200px) {
  .action-buttons {
    .action-btn {
      padding: 4px 8px;

      span {
        display: none;
      }

      .el-icon {
        margin: 0;
      }
    }
  }
}

.variables-editor {
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 8px;
  background: white;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.variables-header {
  display: flex;
  background: #ffffff;
  border-bottom: 1px solid rgba(147, 112, 219, 0.15);
  padding: 12px 16px;
  font-weight: 600;
  font-size: 13px;
  color: #5a32a3;
}

.variables-body {
  max-height: 300px;
  overflow-y: auto;
}

.variable-row {
  display: flex;
  border-bottom: 1px solid rgba(147, 112, 219, 0.08);
  padding: 10px 16px;
  min-height: 48px;
  align-items: center;
  transition: background 0.3s ease;
  background: #ffffff;

  &:hover {
    background: #f5f5f5;
  }
}

.column {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;

  &:last-child {
    flex: 0 0 60px;
    justify-content: center;
  }

  &.header-column {
    flex: 0 0 100px;
    justify-content: center;
  }

  &.action-column {
    flex: 0 0 60px;
    justify-content: center;
  }
}

.variables-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(147, 112, 219, 0.1);
  background: #ffffff;
}

// 变量删除按钮样式
.variable-delete-btn {
  padding: 6px !important;
  border-radius: 6px !important;
  transition: all 0.3s ease !important;

  .el-icon {
    font-size: 16px;
    color: #909399;
    transition: all 0.3s ease;
  }

  &:hover:not(:disabled) {
    background: rgba(245, 108, 108, 0.1) !important;

    .el-icon {
      color: #f56c6c;
    }
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;

    .el-icon {
      color: #c0c4cc;
    }
  }
}

// 查看对话框样式
.view-dialog {
  .view-variables {
    padding: 0;

    .env-info-section {
      margin-bottom: 20px;

      :deep(.el-descriptions) {
        .el-descriptions__label {
          color: #5a32a3;
          font-weight: 500;
          background: #f8f7ff;
          text-align: center;
        }

        .el-descriptions__content {
          color: #333;
          text-align: center;
        }

        .el-descriptions__cell {
          text-align: center;
        }
      }
    }

    .variables-table-section {
      .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #5a32a3;
        margin-bottom: 12px;
        padding-left: 8px;
        border-left: 3px solid #7b42f6;
      }

      :deep(.el-table) {
        border-radius: 8px;
        overflow: hidden;

        .el-table__header {
          th {
            background: #f8f7ff;
            color: #5a32a3;
            font-weight: 600;
            text-align: center;

            .cell {
              text-align: center;
            }
          }
        }

        .el-table__row {
          &:hover {
            background: #f8f7ff;
          }
        }

        .cell {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }

      .ellipsis-text {
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }
}

// 表格 tooltip 样式 - 使用全局样式确保生效
:global(.el-popper.table-tooltip) {
  max-width: 400px !important;
  max-height: 200px !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  background-color: #303133 !important;
  background: #303133 !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;

  .el-popper__arrow {
    &::before {
      background-color: #303133 !important;
      background: #303133 !important;
      border-color: #303133 !important;
    }
  }

  .el-popper__content {
    width: 100% !important;
    max-width: 400px !important;
    max-height: 200px !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    padding: 0 !important;
    background-color: #303133 !important;
    background: #303133 !important;
  }

  .tooltip-content {
    max-width: 380px !important;
    max-height: 180px !important;
    overflow-y: auto !important;
    word-break: break-all !important;
    white-space: pre-wrap !important;
    line-height: 1.6 !important;
    font-size: 13px !important;
    color: #ffffff !important;
    padding: 10px 12px !important;
    background-color: transparent !important;
    background: transparent !important;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.3);
      border-radius: 3px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }
  }
}

// 对话框样式
:deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(147, 112, 219, 0.2);

  .el-dialog__header {
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
    margin: 0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: #5a32a3;
    }
  }

  .el-dialog__body {
    padding: 24px;

    .el-form {
      .el-form-item {
        margin-bottom: 20px;

        .el-form-item__label {
          color: #5a32a3;
          font-weight: 500;
        }

        .el-input__wrapper,
        .el-select .el-input__wrapper {
          box-shadow: none;
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);
          background-color: transparent;

          &:hover,
          &.is-focus {
            border-color: #7b42f6;
          }
        }

        .el-select {
          width: 100%;

          .el-select__wrapper {
            background-color: transparent;
            box-shadow: none;
            border: 1px solid rgba(147, 112, 219, 0.2);
            border-radius: 8px;

            &:hover,
            &.is-focused {
              border-color: #7b42f6;
            }
          }

          .el-select__selection {
            background-color: transparent;
          }
        }

        .el-radio-group {
          .el-radio {
            margin-right: 20px;

            .el-radio__input.is-checked .el-radio__inner {
              background-color: #7b42f6;
              border-color: #7b42f6;
            }

            .el-radio__label {
              color: #5a32a3;
            }
          }
        }
      }
    }
  }

  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid #ebeef5;
    background: #fafafa;

    .el-button {
      font-weight: 500;
      padding: 8px 20px;
      border-radius: 8px;

      &.el-button--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;

        &:hover {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        }
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .page-container {
    padding: 16px;
    gap: 16px;
  }

  .page-header {
    padding: 16px 20px;

    .page-title {
      font-size: 18px;
    }
  }

  .card-container {
    padding: 12px 16px 16px;
  }
}

@media screen and (max-width: 480px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }

  .page-header {
    padding: 14px 16px;

    .page-title {
      font-size: 16px;
    }
  }

  .card-container {
    padding: 8px 12px 12px;
  }
}
</style>
