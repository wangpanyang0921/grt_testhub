<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select v-model="projectId" :placeholder="$t('uiAutomation.common.selectProject')" style="width: 220px" @change="onProjectChange" class="project-select">
        <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
      </el-select>
      <el-input
        v-model="queryParams.search"
        :placeholder="$t('uiAutomation.execution.searchPlaceholder')"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
        class="search-input"
      >
        <template #suffix>
          <el-icon @click="handleSearch" style="cursor: pointer;"><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="queryParams.status" :placeholder="$t('uiAutomation.execution.statusFilter')" clearable @change="handleSearch" style="width: 160px;">
        <el-option :label="$t('uiAutomation.status.pending')" value="pending" />
        <el-option :label="$t('uiAutomation.status.running')" value="running" />
        <el-option :label="$t('uiAutomation.status.passed')" value="passed" />
        <el-option :label="$t('uiAutomation.status.failed')" value="failed" />
        <el-option :label="$t('uiAutomation.status.error')" value="error" />
      </el-select>
      <div class="filter-bar-spacer"></div>
      <div class="filter-bar-spacer"></div>
      <el-button
        type="danger"
        class="batch-delete-btn"
        :disabled="selectedIds.length === 0"
        @click="handleBatchDelete"
      >
        <el-icon><Delete /></el-icon>
        {{ $t('uiAutomation.common.batchDelete') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="executions" v-loading="loading" stripe style="width: 100%" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" header-align="center" align="center" />
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="test_case_name" :label="$t('uiAutomation.execution.caseName')" min-width="200" header-align="center" align="center">
          <template #default="{ row }">
            <span class="case-name-cell" @click="viewExecutionDetail(row)">
              {{ row.test_case_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.execution.relatedObject')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span class="related-badge" :class="!row.test_suite ? 'case-badge' : 'suite-badge'">
              {{ !row.test_suite ? $t('uiAutomation.execution.case') : $t('uiAutomation.execution.suiteTag') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('uiAutomation.execution.statusFilter')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" :label="$t('uiAutomation.execution.executor')" width="120" header-align="center" align="center" />
        <el-table-column prop="started_at" :label="$t('uiAutomation.execution.startTime')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="finished_at" :label="$t('uiAutomation.execution.endTime')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.finished_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.execution.duration')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.execution_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.common.operation')" width="180" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" class="action-btn view-btn" @click="viewExecutionDetail(row)">
                <el-icon><View /></el-icon>
                <span>{{ $t('uiAutomation.common.details') }}</span>
              </el-button>
              <el-button
                size="small"
                type="danger"
                class="action-btn delete-btn"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                <span>{{ $t('uiAutomation.common.delete') }}</span>
              </el-button>

            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 执行详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.execution.executionDetail')" width="900px">
      <div v-if="currentExecution" class="execution-detail">
        <!-- 基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('uiAutomation.execution.caseName')">{{ currentExecution.test_case_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.execution.statusFilter')">
            <el-tag :type="getStatusType(currentExecution.status)">{{ getStatusText(currentExecution.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.execution.browserFilter')">{{ getBrowserText(currentExecution.browser) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.execution.executor')">{{ currentExecution.created_by_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.execution.startTime')">{{ formatDateTime(currentExecution.started_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.execution.endTime')">{{ formatDateTime(currentExecution.finished_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.execution.duration')" :span="2">{{ formatDuration(currentExecution.execution_time) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 执行结果选项卡 -->
        <el-tabs v-model="activeTab" class="execution-tabs" style="margin-top: 20px;">
          <!-- 执行日志 - 所有状态都显示 -->
          <el-tab-pane :label="$t('uiAutomation.execution.executionLogs')" name="logs">
            <div class="logs-container">
              <div v-if="currentExecution.execution_logs">
                <div v-for="(step, index) in parseExecutionLogs(currentExecution.execution_logs)" :key="index" class="log-item">
                  <div class="log-header">
                    <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                      {{ $t('uiAutomation.execution.step') }} {{ step.step_number }}
                    </el-tag>
                    <span class="log-action">{{ getActionText(step.action_type) }}</span>
                    <span class="log-desc">{{ step.description }}</span>
                  </div>
                  <div v-if="step.error" class="log-error">
                    <el-icon><WarningFilled /></el-icon>
                    <pre class="error-message">{{ step.error }}</pre>
                  </div>
                </div>
              </div>
              <el-empty v-else :description="$t('uiAutomation.execution.noLogs')" />
            </div>
          </el-tab-pane>

          <!-- 失败截图 - 仅失败或错误状态显示 -->
          <el-tab-pane :label="$t('uiAutomation.execution.failedScreenshots')" name="screenshots" v-if="currentExecution.status === 'failed' || currentExecution.status === 'error'">
            <div class="screenshots-container">
              <div v-if="currentExecution.screenshots && currentExecution.screenshots.length > 0">
                <div v-for="(screenshot, screenshotIndex) in currentExecution.screenshots" :key="screenshotIndex" class="screenshot-item">
                  <h5>{{ screenshot.description || `${$t('uiAutomation.execution.screenshot')} ${Number(screenshotIndex) + 1}` }}</h5>
                  <!-- 检查截图URL是否有效 -->
                  <div v-if="screenshot.url" class="screenshot-wrapper">
                    <img
                      :src="screenshot.url"
                      :alt="screenshot.description"
                      class="screenshot-img"
                      @error="handleImageError($event, screenshot)"
                    />
                  </div>
                  <div v-else class="screenshot-error">
                    <el-icon><WarningFilled /></el-icon>
                    <span>{{ $t('uiAutomation.execution.screenshotFailed') }}{{ screenshot.error || $t('uiAutomation.execution.unknownReason') }}</span>
                  </div>
                  <p class="screenshot-time">{{ formatDateTime(screenshot.timestamp) }}</p>
                </div>
              </div>
              <el-empty v-else :description="$t('uiAutomation.execution.noScreenshots')" />
            </div>
          </el-tab-pane>

          <!-- 错误信息 - 仅失败或错误状态显示 -->
          <el-tab-pane :label="$t('uiAutomation.execution.errorInfo')" name="error" v-if="currentExecution.status === 'failed' || currentExecution.status === 'error'">
            <div class="errors-container">
              <div v-if="currentExecution.error_message" class="error-item">
                <div class="error-content">
                  <pre class="error-text">{{ currentExecution.error_message }}</pre>
                </div>
              </div>
              <el-empty v-else :description="$t('uiAutomation.execution.noError')" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button class="close-btn" @click="showDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
      </template>
    </el-dialog>

    <!-- 重跑测试用例对话框 -->
    <el-dialog v-model="showRerunDialogVisible" :title="$t('uiAutomation.execution.rerunTitle')" width="500px">
      <el-form :model="rerunFormData" label-width="100px">
        <el-form-item :label="$t('uiAutomation.execution.testEngine')">
          <el-radio-group v-model="rerunFormData.engine">
            <el-radio label="playwright">Playwright</el-radio>
            <el-radio label="selenium">Selenium</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.execution.browserFilter')">
          <el-select v-model="rerunFormData.browser" style="width: 100%">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Safari" value="safari" />
            <el-option label="Edge" value="edge" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.execution.executionMode')">
          <el-radio-group v-model="rerunFormData.headless">
            <el-radio :label="false">{{ $t('uiAutomation.execution.headedMode') }}</el-radio>
            <el-radio :label="true">{{ $t('uiAutomation.execution.headlessMode') }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="showRerunDialogVisible = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button class="confirm-btn" @click="handleRerun" :loading="rerunning">{{ $t('uiAutomation.execution.confirmRerun') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, View, WarningFilled, Refresh, Delete } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import {
  getTestCaseExecutions,
  getUiProjects,
  deleteTestCaseExecution,
  batchDeleteTestCaseExecutions,
  runTestCase
} from '@/api/ui_automation'

const { t } = useI18n()

// 项目和执行数据
const projects = ref([])
const projectId = ref('')
const executions = ref([])
const loading = ref(false)
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

// 搜索和筛选
const queryParams = reactive({
  project: undefined,
  search: '',
  status: undefined,
  browser: undefined
})
const selectedIds = ref([])

// 详情对话框相关
const showDetailDialog = ref(false)
const activeTab = ref('logs')
const currentExecution = ref(null)

// 重跑对话框相关
const showRerunDialogVisible = ref(false)
const rerunning = ref(false)
const rerunFormData = reactive({
  testCaseId: null,
  engine: 'playwright',
  browser: 'chrome',
  headless: false
})

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 处理图片加载错误
const handleImageError = (event, screenshot) => {
  console.error('Screenshot load failed:', screenshot)
  const img = event.target
  img.style.display = 'none'
  // Show error message after image
  const errorDiv = img.parentElement.querySelector('.img-load-error')
  if (!errorDiv) {
    const div = document.createElement('div')
    div.className = 'img-load-error'
    div.innerHTML = `
      <i class="el-icon-warning"></i>
      <span>${t('uiAutomation.execution.imageLoadFailed')}</span>
    `
    img.parentElement.appendChild(div)
  }
}

// 格式化持续时间（execution_time单位是秒）
const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '-'

  const totalSeconds = Math.floor(seconds)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const secs = totalSeconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

// 获取状态样式（用于 el-tag）
const getStatusType = (status) => {
  const statusMap = {
    'pending': 'info',
    'running': 'warning',
    'passed': 'success',
    'failed': 'danger',
    'error': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态徽章样式类
const getStatusClass = (status) => {
  const statusMap = {
    'pending': 'pending',
    'running': 'running',
    'passed': 'passed',
    'failed': 'failed',
    'error': 'error'
  }
  return statusMap[status] || 'pending'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'pending': t('uiAutomation.status.pending'),
    'running': t('uiAutomation.status.running'),
    'passed': t('uiAutomation.status.passed'),
    'failed': t('uiAutomation.status.failed'),
    'error': t('uiAutomation.status.error')
  }
  return statusMap[status] || status
}

// 获取浏览器文本
const getBrowserText = (browser) => {
  const browserMap = {
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'edge': 'Edge'
  }
  return browserMap[browser] || browser || 'Chrome'
}

// 获取测试引擎文本
const getEngineText = (engine) => {
  const engineMap = {
    'playwright': 'Playwright',
    'selenium': 'Selenium'
  }
  return engineMap[engine] || engine || 'Playwright'
}

// 获取操作类型文本
const getActionText = (actionType) => {
  const actionMap = {
    'click': t('uiAutomation.actionTypes.click'),
    'fill': t('uiAutomation.actionTypes.fill'),
    'getText': t('uiAutomation.actionTypes.getText'),
    'waitFor': t('uiAutomation.actionTypes.waitFor'),
    'hover': t('uiAutomation.actionTypes.hover'),
    'scroll': t('uiAutomation.actionTypes.scroll'),
    'screenshot': t('uiAutomation.actionTypes.screenshot'),
    'assert': t('uiAutomation.actionTypes.assert'),
    'wait': t('uiAutomation.actionTypes.wait')
  }
  return actionMap[actionType] || actionType
}

// 解析执行日志
const parseExecutionLogs = (logs) => {
  if (!logs) return []
  try {
    return typeof logs === 'string' ? JSON.parse(logs) : logs
  } catch (e) {
    console.error('解析执行日志失败:', e)
    return []
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.loadFailed'))
    console.error('获取项目列表失败:', error)
  }
}

// 加载执行列表
const loadExecutions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      search: queryParams.search,
      browser: queryParams.browser
    }

    // 只有当status有值时才添加到params中
    if (queryParams.status) {
      params.status = queryParams.status
    }

    // 添加项目筛选
    if (projectId.value) {
      params.project = projectId.value
    } else {
      params.project = undefined // Ensure project is undefined if not selected
    }

    const response = await getTestCaseExecutions(params)
    executions.value = response.data.results || response.data
    total.value = response.data.count || executions.value.length
  } catch (error) {
    ElMessage.error(t('uiAutomation.execution.messages.loadFailed'))
    console.error('获取执行列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 项目变更处理
const onProjectChange = () => {
  queryParams.search = ''
  queryParams.status = undefined
  queryParams.browser = undefined
  pagination.currentPage = 1
  loadExecutions()
}

// 搜索处理
const handleSearch = () => {
  pagination.currentPage = 1
  loadExecutions()
}

// 重置查询
const resetQuery = () => {
  queryParams.search = ''
  queryParams.status = undefined
  queryParams.browser = undefined
  pagination.currentPage = 1
  loadExecutions()
}

// 分页处理
const handleSizeChange = (val) => {
  pagination.pageSize = val
  pagination.currentPage = 1
  loadExecutions()
}

const handleCurrentChange = (val) => {
  pagination.currentPage = val
  loadExecutions()
}

// 表格多选
const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

// 删除单个执行记录
const handleDelete = (row) => {
  ElMessageBox.confirm(t('uiAutomation.execution.messages.deleteConfirm'), t('uiAutomation.messages.confirm.tip'), {
    confirmButtonText: t('uiAutomation.common.confirm'),
    cancelButtonText: t('uiAutomation.common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await deleteTestCaseExecution(row.id)
      ElMessage.success(t('uiAutomation.execution.messages.deleteSuccess'))
      loadExecutions()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error(t('uiAutomation.execution.messages.deleteFailed'))
    }
  })
}

// 批量删除执行记录
const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return

  ElMessageBox.confirm(t('uiAutomation.execution.messages.batchDeleteConfirm', { count: selectedIds.value.length }), t('uiAutomation.messages.confirm.tip'), {
    confirmButtonText: t('uiAutomation.common.confirm'),
    cancelButtonText: t('uiAutomation.common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteTestCaseExecutions(selectedIds.value)
      ElMessage.success(t('uiAutomation.execution.messages.batchDeleteSuccess'))
      selectedIds.value = []
      loadExecutions()
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error(t('uiAutomation.execution.messages.batchDeleteFailed'))
    }
  })
}

// 查看执行详情
const viewExecutionDetail = (execution) => {
  currentExecution.value = execution
  activeTab.value = 'logs'
  showDetailDialog.value = true
}

// 显示重跑对话框
const showRerunDialog = (execution) => {
  rerunFormData.testCaseId = execution.test_case
  rerunFormData.engine = execution.engine || 'playwright'
  rerunFormData.browser = execution.browser || 'chrome'
  rerunFormData.headless = execution.headless || false
  showRerunDialogVisible.value = true
}

// 执行重跑
const handleRerun = async () => {
  if (!rerunFormData.testCaseId) {
    ElMessage.error(t('uiAutomation.execution.messages.invalidCaseId'))
    return
  }

  rerunning.value = true
  try {
    const response = await runTestCase(rerunFormData.testCaseId, {
      engine: rerunFormData.engine,
      browser: rerunFormData.browser,
      headless: rerunFormData.headless
    })

    // 无论成功失败，都关闭弹框并刷新列表
    showRerunDialogVisible.value = false

    // 延迟一下再刷新，确保后端已经保存完成
    setTimeout(async () => {
      await loadExecutions()
    }, 500)

    // 根据返回结果显示消息
    if (response.data.success) {
      ElMessage.success(t('uiAutomation.execution.messages.rerunSuccess'))
    } else {
      ElMessage.warning(t('uiAutomation.execution.messages.rerunCompleteWithFailure') + ': ' + (response.data.errors?.[0]?.message || t('uiAutomation.execution.messages.viewDetails')))
    }
  } catch (error) {
    showRerunDialogVisible.value = false
    ElMessage.error(t('uiAutomation.execution.messages.rerunFailed') + ': ' + (error.response?.data?.message || error.message || t('uiAutomation.messages.error.unknown')))
    console.error('重跑失败:', error)
    // 即使失败也刷新列表，因为可能已经创建了执行记录
    setTimeout(async () => {
      await loadExecutions()
    }, 500)
  } finally {
    rerunning.value = false
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await loadProjects()
  if (projects.value.length > 0) {
    projectId.value = projects.value[0].id
  }
  await loadExecutions()
})
</script>

<style scoped lang="scss">
// 全局变量
:root {
  --primary-color: #667eea;
  --primary-dark: #764ba2;
  --primary-light: #f8f7ff;
  --primary-lighter: #fafbff;
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

// 页面容器
.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
}

// 筛选栏
.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;

  .search-input,
  .project-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.2) inset;
      background: #ffffff;

      &:hover {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  .project-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.2) inset;
      background: #ffffff;

      &:hover {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  .filter-bar-spacer {
    flex: 1;
  }

  .query-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3) !important;
    display: flex;
    align-items: center;
    gap: 6px;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4) !important;
    }

    .el-icon {
      font-size: 14px;
    }
  }

  .reset-btn {
    background: #ffffff !important;
    border: 1px solid rgba(147, 112, 219, 0.2) !important;
    color: #5a32a3 !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;

    &:hover {
      color: #7b42f6 !important;
      border-color: #7b42f6 !important;
      background: rgba(123, 66, 246, 0.05) !important;
      transform: translateY(-2px) !important;
    }
  }

  .batch-delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3) !important;
    display: flex;
    align-items: center;
    gap: 6px;

    .el-icon {
      margin-right: 6px;
    }

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #ff7875 0%, #ffa39e 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 20px rgba(255, 77, 79, 0.4) !important;
    }

    &:active:not(:disabled) {
      transform: translateY(0) !important;
    }

    &:disabled {
      background: linear-gradient(135deg, #d9d9d9 0%, #bfbfbf 100%) !important;
      box-shadow: none !important;
      cursor: not-allowed !important;
    }

    .el-icon {
      font-size: 14px;
    }
  }
}

// 表格容器
.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;

  // 表格样式
  .el-table {
    border: none;
    border-radius: 8px;
    overflow: hidden;
    min-height: 200px;
    box-shadow: none;
    transition: all 0.3s ease;
    background-color: #ffffff !important;

    /* 覆盖 Element Plus 默认主题变量 */
    --el-color-primary: var(--primary-color);
    --el-color-primary-light-3: #9370db;
    --el-color-primary-light-5: #a888e0;
    --el-color-primary-light-7: #c2a9f3;
    --el-color-primary-light-9: #f8f7ff;
    --el-border-color: rgba(147, 112, 219, 0.1);
    --el-border-color-light: rgba(147, 112, 219, 0.08);
    --el-border-color-lighter: rgba(147, 112, 219, 0.05);
    --el-fill-color-light: #f8f7ff;
    --el-fill-color-lighter: #fafaff;
    --el-fill-color-blank: #ffffff;
    --el-text-color-primary: #262626;
    --el-text-color-regular: #595959;
    --el-text-color-secondary: #8c8c8c;
    --el-text-color-placeholder: #bfbfbf;

    &::before {
      display: none;
    }

    // 表头包装器
    :deep(.el-table__header-wrapper) {
      background-color: #ffffff !important;

      // 表头
      :deep(.el-table__header) {
        background-color: #ffffff !important;

        // 表头单元格
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
            background-color: #f8f7ff !important;
          }

          .cell {
            background-color: #ffffff !important;
            color: #5a32a3;
            font-weight: 600;
          }
        }
      }
    }

    // 直接覆盖表头单元格样式
    :deep(.el-table__header th) {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600 !important;
    }

    // 覆盖表头单元格内容样式
    :deep(.el-table__header th .cell) {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600 !important;
    }

    // 表格主体
    :deep(.el-table__body-wrapper) {
      background-color: #ffffff;

      :deep(.el-table__body) {
        background-color: #ffffff;

        :deep(tr) {
          background-color: #ffffff;
          transition: all 0.3s ease;

          &:hover {
            background-color: #f8f7ff !important;
          }

          // 斑马纹
          &.el-table__row--striped {
            background-color: #fafafa;

            &:hover {
              background-color: #f8f7ff !important;
            }
          }

          :deep(td) {
            background-color: transparent;
            border-bottom: 1px solid #f0f0f0;
            padding: 12px 16px;
            color: #595959;
            font-size: 14px;
            text-align: center;
          }
        }
      }
    }

    // 行悬停效果
    :deep(.el-table__row:hover) {
      background-color: #f8f7ff !important;
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

    // 确保整个表格容器都使用正确的背景色
    &.el-table--enable-row-hover {
      background-color: #ffffff !important;
    }

    // 覆盖表格行的默认样式
    :deep(.el-table__row) {
      background-color: #ffffff !important;
    }

    // 覆盖表格行的条纹样式
    :deep(.el-table__row.el-table__row--striped) {
      background-color: #fafaff !important;
    }

    // 覆盖表格行的 hover 样式
    :deep(.el-table__row:hover) {
      background-color: #f8f7ff !important;
    }

    // 直接覆盖表头单元格样式
    :deep(.el-table__header th) {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600 !important;
    }

    // 覆盖表头单元格内容样式
    :deep(.el-table__header th .cell) {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600 !important;
    }
  }
}

// 用例名称样式
.case-name-cell {
  padding: 4px 8px;
  line-height: 1.6;
  color: #595959;
  cursor: pointer;
  transition: color 0.3s ease;
  font-size: 14px;

  &:hover {
    color: #7b42f6;
  }
}

// 关联对象徽章样式
.related-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.case-badge {
    background: #e6f7ff;
    color: #1890ff;
  }

  &.suite-badge {
    background: #fff7e6;
    color: #fa8c16;
  }
}

// 执行状态徽章样式
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  // 待执行 - 灰色
  &.pending {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  // 执行中 - 蓝色
  &.running {
    background: #e6f7ff;
    color: #1890ff;
  }

  // 通过 - 绿色
  &.passed {
    background: #f6ffed;
    color: #52c41a;
  }

  // 失败 - 红色
  &.failed {
    background: #fff1f0;
    color: #ff4d4f;
  }

  // 错误 - 深红色
  &.error {
    background: #fff1f0;
    color: #cf1322;
  }
}

// 操作按钮容器
.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

// 操作按钮样式
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  padding: 6px 14px !important;
  border-radius: 6px;
  transition: all 0.3s ease;
  min-width: 70px;

  .el-icon {
    font-size: 14px;
  }

  span {
    font-size: 12px;
  }

  &.view-btn {
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

  &.rerun-btn {
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

  &.delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(255, 77, 79, 0.4);
    }
  }
}

// 关闭按钮样式
.close-btn {
  background: #ffffff !important;
  border-color: #d1d5db !important;
  color: #6b7280 !important;
  border-radius: 8px !important;

  &:hover {
    background: #f5f3ff !important;
    border-color: #a78bfa !important;
    color: #8b5cf6 !important;
  }

  &:active {
    background: #ede9fe !important;
    border-color: #8b5cf6 !important;
    color: #7c3aed !important;
  }
}

// 对话框底部按钮样式
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .cancel-btn {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;

    &:hover {
      background: #f5f3ff !important;
      border-color: #a78bfa !important;
      color: #8b5cf6 !important;
    }
  }

  .confirm-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4) !important;
    }
  }
}

// 分页容器
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
  margin-top: 8px;
  background: transparent;
  border: none;
  transition: all 0.3s ease;

  /* 定义主题变量 - 浅紫色风格 */
  --primary-color: #a78bfa;
  --primary-dark: #8b5cf6;
  --primary-light: #f3f0ff;
  --text-primary: #262626;
  --text-secondary: #595959;
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

  :deep(.el-pagination) {
    display: flex;
    align-items: center;
    gap: 4px;
    font-weight: 500;

    // 总条数
    .el-pagination__total {
      color: #6b7280;
      font-size: 14px;
      font-weight: 500;
      margin-right: 12px;
    }

    // 每页条数选择器
    .el-pagination__sizes {
      margin-right: 12px;

      .el-select {
        .el-input__wrapper {
          border-radius: 8px;
          border: 1px solid #e5e7eb;
          background: #ffffff;
          box-shadow: none;

          &:hover {
            border-color: #a78bfa;
            box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
          }

          &.is-focus {
            border-color: #a78bfa;
            box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15);
          }
        }

        .el-input__inner {
          color: #374151;
          font-weight: 500;
        }
      }
    }

    // 上一页/下一页按钮
    .btn-prev,
    .btn-next {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      border: 1px solid #e5e7eb;
      background: #ffffff;
      color: #6b7280;
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        background: #f5f3ff;
        border-color: #a78bfa;
        color: #8b5cf6;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2);
      }

      &:disabled {
        background: #f5f5f5;
        border-color: #e0e0e0;
        color: #c0c0c0;
      }

      .el-icon {
        font-size: 14px;
        font-weight: bold;
      }
    }

    // 页码按钮
    .el-pager {
      display: flex;
      gap: 8px;

      li {
        min-width: 32px;
        height: 32px;
        padding: 0 8px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        background: #ffffff;
        color: #6b7280;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;

        &:hover:not(.is-active) {
          background: #f5f3ff;
          border-color: #a78bfa;
          color: #8b5cf6;
          transform: translateY(-1px);
        }

        &.is-active {
          background: #f5f3ff;
          border-color: #a78bfa;
          color: #8b5cf6;
          box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2);
        }

        &.is-active:hover {
          background: #ede9fe;
          border-color: #8b5cf6;
        }
      }
    }

    // 跳转输入框
    .el-pagination__jump {
      color: #6b7280;
      font-weight: 500;
      margin-left: 12px;

      .el-input {
        width: 50px;
        margin: 0 4px;

        .el-input__wrapper {
          border-radius: 8px;
          border: 1px solid #e5e7eb;
          background: #ffffff;
          box-shadow: none;

          &:hover {
            border-color: #a78bfa;
            box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
          }

          &.is-focus {
            border-color: #a78bfa;
            box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15);
          }
        }

        .el-input__inner {
          color: #374151;
          font-weight: 500;
          text-align: center;
        }
      }
    }
  }
}

.execution-detail {
  .execution-tabs {
    margin-top: 20px;
  }

  .logs-container {
    max-height: 500px;
    overflow-y: auto;
    background: #f5f7fa;
    padding: 15px;
    border-radius: 4px;

    .log-item {
      margin-bottom: 15px;
      padding: 12px;
      background: white;
      border-radius: 4px;
      border-left: 3px solid #a78bfa;

      &:last-child {
        margin-bottom: 0;
      }

      .log-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;

        .log-action {
          font-weight: 500;
          color: #606266;
        }

        .log-desc {
          color: #909399;
          font-size: 14px;
        }
      }

      .log-error {
        display: flex;
        align-items: flex-start;  /* 改为 flex-start，适配多行文本 */
        gap: 8px;
        color: #f56c6c;
        background: #fef0f0;
        padding: 8px 12px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 14px;

        .error-message {
          margin: 0;
          padding: 0;
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          font-size: 13px;
          line-height: 1.6;
          white-space: pre-wrap;  /* 保留换行符和空格 */
          word-break: break-word;  /* 长单词换行 */
          flex: 1;
        }

        .el-icon {
          margin-top: 2px;  /* 图标与文本顶部对齐 */
          flex-shrink: 0;  /* 图标不缩小 */
        }
      }
    }
  }

  .screenshots-container {
    max-height: 600px;
    overflow-y: auto;
    padding: 10px;

    .screenshot-item {
      margin-bottom: 30px;
      text-align: center;

      h5 {
        margin: 0 0 15px 0;
        color: #303133;
        font-size: 14px;
      }

      .screenshot-wrapper {
        position: relative;
      }

      .screenshot-img {
        max-width: 100%;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .screenshot-error {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: #fef0f0;
        color: #f56c6c;
        border: 1px solid #fbc4c4;
        border-radius: 4px;
        font-size: 14px;

        .el-icon {
          font-size: 16px;
        }
      }

      .img-load-error {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: #fff7e6;
        color: #e6a23c;
        border: 1px solid #f5dab1;
        border-radius: 4px;
        font-size: 14px;
        margin-top: 10px;

        i {
          font-size: 16px;
        }
      }

      .screenshot-time {
        margin: 10px 0 0 0;
        color: #909399;
        font-size: 12px;
      }
    }
  }

  .errors-container {
    padding: 10px;
    height: 100%;
    overflow-y: auto;
  }

  .error-item {
    background: #fff;
    border: 2px solid #f56c6c;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 15px;
  }

  .error-item:last-child {
    margin-bottom: 0;
  }

  .error-content {
    display: flex;
    flex-direction: column;
  }

  .error-text {
    margin: 0;
    padding: 15px;
    background: #2d2d2d;
    color: #ff6b6b;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-x: auto;
  }

  .error-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #f5f5f5;
  }

  .error-header .el-tag {
    font-size: 16px;
    padding: 10px 15px;
    font-weight: 600;
  }
}
</style>
