<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('uiAutomation.report.title') }}</h1>
        <el-select v-model="selectedProject" :placeholder="$t('uiAutomation.common.selectProject')" class="project-select" @change="onProjectChange">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </div>
      <el-button type="primary" class="refresh-btn" @click="refreshReports">
        <el-icon><Refresh /></el-icon>
        {{ $t('uiAutomation.report.refreshReport') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="reports" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" header-align="center" align="center" />
        <el-table-column prop="test_suite_name" :label="$t('uiAutomation.report.testSuite')" min-width="200" header-align="center" align="center" />
        <el-table-column prop="status" :label="$t('uiAutomation.common.status')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.testEngine')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getEngineText(row.engine) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.browser')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            {{ getBrowserText(row.browser) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_cases" :label="$t('uiAutomation.report.totalCases')" width="100" header-align="center" align="center" />
        <el-table-column prop="passed_cases" :label="$t('uiAutomation.report.passedCases')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: bold;">{{ row.passed_cases }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_cases" :label="$t('uiAutomation.report.failedCases')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ row.failed_cases }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.passRate')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="getProgressColor(row.pass_rate)"
              :stroke-width="16"
            />
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.duration')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="executed_by_name" :label="$t('uiAutomation.report.executor')" width="120" header-align="center" align="center" />
        <el-table-column prop="created_at" :label="$t('uiAutomation.report.executionTime')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.common.operation')" width="200" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" class="action-btn view-btn" size="small" @click="viewReportDetail(row)">
                <el-icon><Document /></el-icon>
                <span>{{ $t('uiAutomation.report.viewDetail') }}</span>
              </el-button>
              <el-button type="danger" class="action-btn delete-btn" size="small" @click="deleteReport(row)">
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

    <!-- 报告详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="$t('uiAutomation.report.reportDetail')"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentReport" class="report-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('uiAutomation.report.reportId')">{{ currentReport.id }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.testSuite')">{{ currentReport.test_suite_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.executionStatus')">
            <el-tag :type="getStatusType(currentReport.status)">
              {{ getStatusText(currentReport.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.executor')">{{ currentReport.executed_by_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.testEngine')">{{ getEngineText(currentReport.engine) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.browser')">{{ getBrowserText(currentReport.browser) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.executionMode')">{{ currentReport.headless ? $t('uiAutomation.report.headlessMode') : $t('uiAutomation.report.headedMode') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.duration')">{{ formatDuration(currentReport.duration) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.startTime')">{{ formatDate(currentReport.started_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.endTime')">{{ formatDate(currentReport.finished_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="statistics-section">
          <h4>{{ $t('uiAutomation.report.testStatistics') }}</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-label">{{ $t('uiAutomation.report.totalCases') }}</div>
                <div class="stat-value">{{ currentReport.total_cases }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card success">
                <div class="stat-label">{{ $t('uiAutomation.report.passedCases') }}</div>
                <div class="stat-value">{{ currentReport.passed_cases }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card danger">
                <div class="stat-label">{{ $t('uiAutomation.report.failedCases') }}</div>
                <div class="stat-value">{{ currentReport.failed_cases }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card warning">
                <div class="stat-label">{{ $t('uiAutomation.report.skippedCases') }}</div>
                <div class="stat-value">{{ currentReport.skipped_cases }}</div>
              </div>
            </el-col>
          </el-row>

          <div class="pass-rate-chart">
            <h5>{{ $t('uiAutomation.report.passRate') }}: {{ currentReport.pass_rate }}%</h5>
            <el-progress
              :percentage="currentReport.pass_rate"
              :color="getProgressColor(currentReport.pass_rate)"
              :stroke-width="20"
            />
          </div>
        </div>

        <div class="result-section">
          <h4>{{ $t('uiAutomation.report.executionResultDetail') }}</h4>
          <el-table
            :data="getCaseExecutionList(currentReport)"
            border
            style="margin-top: 15px;"
          >
            <el-table-column type="index" :label="$t('uiAutomation.report.sequence')" width="60" />
            <el-table-column prop="test_case_name" :label="$t('uiAutomation.report.testCase')" min-width="200" />
            <el-table-column :label="$t('uiAutomation.report.executionStatus')" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'passed' ? 'success' : 'danger'">
                  {{ row.status === 'passed' ? $t('uiAutomation.report.casePassed') : $t('uiAutomation.report.caseFailed') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('uiAutomation.report.stepCount')" width="100" align="center">
              <template #default="{ row }">
                {{ row.steps ? row.steps.length : 0 }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('uiAutomation.common.operation')" width="120" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  @click="viewCaseDetail(row)"
                >
                  {{ $t('uiAutomation.report.viewDetail') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="error-section" v-if="currentReport.error_message">
          <h4>{{ $t('uiAutomation.report.errorInfo') }}</h4>
          <div class="errors-container">
            <div class="error-item">
              <div class="error-content">
                <pre class="error-text">{{ currentReport.error_message }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
      </template>
    </el-dialog>

    <!-- 用例详情对话框 -->
    <el-dialog
      v-model="showCaseDetailDialog"
      :title="`${$t('uiAutomation.report.caseDetail')} - ${currentCase?.test_case_name || ''}`"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentCase" class="case-detail">
        <!-- 用例执行成功 - 只显示执行日志 -->
        <div v-if="currentCase.status === 'passed'">
          <h4>{{ $t('uiAutomation.report.executionLogs') }}</h4>
          <div class="log-container">
            <div v-for="(step, index) in currentCase.steps" :key="index" class="log-item">
              <div class="log-header">
                <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                  {{ $t('uiAutomation.report.step') }} {{ step.step_number }}
                </el-tag>
                <span class="log-action">{{ getActionText(step.action_type) }}</span>
                <span class="log-desc">{{ step.description }}</span>
              </div>
              <div v-if="step.error" class="log-error">
                <el-icon><WarningFilled /></el-icon>
                {{ step.error }}
              </div>
            </div>
          </div>
        </div>

        <!-- 用例执行失败 - 显示执行日志、失败截图、错误信息三个tab -->
        <div v-else>
          <el-tabs v-model="activeTab" type="border-card">
            <!-- 执行日志 Tab -->
            <el-tab-pane :label="$t('uiAutomation.report.executionLogs')" name="logs">
              <div class="log-container">
                <div v-for="(step, index) in currentCase.steps" :key="index" class="log-item">
                  <div class="log-header">
                    <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                      {{ $t('uiAutomation.report.step') }} {{ step.step_number }}
                    </el-tag>
                    <span class="log-action">{{ getActionText(step.action_type) }}</span>
                    <span class="log-desc">{{ step.description }}</span>
                  </div>
                  <div v-if="step.error" class="log-error">
                    <el-icon><WarningFilled /></el-icon>
                    {{ step.error }}
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 失败截图 Tab -->
            <el-tab-pane :label="$t('uiAutomation.report.failedScreenshots')" name="screenshots">
              <div v-if="currentCase.screenshots && currentCase.screenshots.length > 0" class="screenshot-container">
                <div v-for="(screenshot, index) in currentCase.screenshots" :key="index" class="screenshot-item">
                  <h5>{{ screenshot.description || `${$t('uiAutomation.report.screenshot')} ${index + 1}` }}</h5>
                  <img :src="screenshot.url" :alt="screenshot.description" class="screenshot-img" />
                  <p class="screenshot-time">{{ screenshot.timestamp }}</p>
                </div>
              </div>
              <el-empty v-else :description="$t('uiAutomation.report.noScreenshots')" />
            </el-tab-pane>

            <!-- 错误信息 Tab -->
            <el-tab-pane :label="$t('uiAutomation.report.errorInfo')" name="error">
              <div class="errors-container">
                <div v-if="currentCase.error" class="error-item">
                  <div class="error-content">
                    <pre class="error-text">{{ currentCase.error }}</pre>
                  </div>
                </div>
                <el-empty v-else :description="$t('uiAutomation.report.noError')" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCaseDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Document, Delete, WarningFilled } from '@element-plus/icons-vue'
import {
  getUiProjects,
  getTestExecutions,
  deleteTestExecution
} from '@/api/ui_automation'

const { t } = useI18n()

const reports = ref([])
const projects = ref([])
const selectedProject = ref('')
const loading = ref(false)
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

// 详情对话框
const showDetailDialog = ref(false)
const currentReport = ref(null)

// 用例详情对话框
const showCaseDetailDialog = ref(false)
const currentCase = ref(null)
const activeTab = ref('logs')

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load projects:', error)
    ElMessage.error(t('uiAutomation.report.messages.loadProjectsFailed'))
  }
}

// 加载报告列表
const loadReports = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }

    if (selectedProject.value) {
      params.project = selectedProject.value
    }

    const response = await getTestExecutions(params)

    if (response.data.results) {
      reports.value = response.data.results
      total.value = response.data.count || 0
    } else {
      reports.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    console.error('Failed to load test reports:', error)
    ElMessage.error(t('uiAutomation.report.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

// 项目切换
const onProjectChange = async () => {
  pagination.currentPage = 1
  await loadReports()
}

// 刷新报告
const refreshReports = async () => {
  await loadReports()
  ElMessage.success(t('uiAutomation.report.messages.refreshed'))
}

// 分页处理
const handleSizeChange = async () => {
  pagination.currentPage = 1
  await loadReports()
}

const handleCurrentChange = async () => {
  await loadReports()
}

// 查看报告详情
const viewReportDetail = (report) => {
  currentReport.value = report
  showDetailDialog.value = true
}

// 获取用例执行列表
const getCaseExecutionList = (report) => {
  if (!report || !report.result_data || !report.result_data.test_cases) {
    return []
  }
  return report.result_data.test_cases
}

// 查看用例详情
const viewCaseDetail = (caseData) => {
  currentCase.value = caseData
  activeTab.value = 'logs'
  showCaseDetailDialog.value = true
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

// 删除报告
const deleteReport = async (report) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.report.messages.deleteConfirm', { name: report.test_suite_name }),
      t('uiAutomation.report.messages.confirmDelete'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deleteTestExecution(report.id)
    ElMessage.success(t('uiAutomation.report.messages.deleteSuccess'))
    await loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete report:', error)
      ElMessage.error(t('uiAutomation.report.messages.deleteFailed'))
    }
  }
}

// 辅助方法
const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'SUCCESS': 'success',
    'FAILED': 'danger',
    'ABORTED': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'PENDING': t('uiAutomation.report.statusPending'),
    'RUNNING': t('uiAutomation.report.statusRunning'),
    'SUCCESS': t('uiAutomation.report.statusSuccess'),
    'FAILED': t('uiAutomation.report.statusFailed'),
    'ABORTED': t('uiAutomation.report.statusAborted')
  }
  return textMap[status] || status
}

const getEngineText = (engine) => {
  const engineMap = {
    'playwright': 'Playwright',
    'selenium': 'Selenium'
  }
  return engineMap[engine] || engine || 'Playwright'
}

const getBrowserText = (browser) => {
  const browserMap = {
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'edge': 'Edge'
  }
  return browserMap[browser] || browser || 'Chrome'
}

const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const formatDuration = (seconds) => {
  if (!seconds) return `0${t('uiAutomation.report.seconds')}`
  if (seconds < 60) return `${seconds.toFixed(1)}${t('uiAutomation.report.seconds')}`
  const minutes = Math.floor(seconds / 60)
  const secs = (seconds % 60).toFixed(0)
  return `${minutes}${t('uiAutomation.report.minutes')}${secs}${t('uiAutomation.report.seconds')}`
}

onMounted(async () => {
  await loadProjects()
  if (projects.value.length > 0) {
    selectedProject.value = projects.value[0].id
  }
  await loadReports()
})
</script>

<style scoped lang="scss">
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

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: #5a32a3;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .project-select {
    width: 200px;

    :deep(.el-input__wrapper) {
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
      border-radius: 8px;

      &:hover,
      &:focus {
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
      }
    }
  }

  .refresh-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4) !important;
    }

    &:active {
      transform: translateY(0) !important;
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
  padding-top: 16px;

  // 表格样式
  .el-table {
    border: none;
    border-radius: 8px 8px 0 0;
    overflow: hidden;
    min-height: 200px;
    box-shadow: none;
    transition: all 0.3s ease;
    background-color: transparent !important;

    /* 覆盖 Element Plus 默认主题变量 */
    --el-color-primary: var(--primary-color);
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
          text-align: left;
          line-height: 24px;
          transition: all 0.3s ease;

          &:hover {
            background-color: #ffffff !important;
          }

          // 表头单元格内部
          :deep(.cell) {
            background-color: #ffffff !important;
            color: #5a32a3 !important;
            font-weight: 600 !important;
          }
        }
      }
    }

    // 表格体包装器
    :deep(.el-table__body-wrapper) {
      background-color: #ffffff !important;

      // 表格行
      :deep(.el-table__row) {
        transition: all 0.3s ease;
        background-color: #ffffff !important;

        &:hover {
          background-color: #f8f7ff !important;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(147, 112, 219, 0.1);
        }

        // 表格单元格
        :deep(td) {
          background-color: #ffffff !important;
          border-bottom: 1px solid #e9ecef;
          padding: 16px;
          text-align: left;
          line-height: 24px;
          transition: all 0.3s ease;
        }

        &:hover :deep(td) {
          background-color: #f8f7ff !important;
        }
      }
    }
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
  &.view-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3) !important;
    transition: all 0.3s ease !important;
    white-space: nowrap;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4) !important;
    }

    .el-icon {
      color: #ffffff !important;
      margin-right: 3px;
      font-size: 12px;
    }

    span {
      font-size: 12px;
    }
  }

  &.delete-btn {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3) !important;
    transition: all 0.3s ease !important;
    white-space: nowrap;

    &:hover {
      background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
    }

    .el-icon {
      color: #ffffff !important;
      margin-right: 3px;
      font-size: 12px;
    }

    span {
      font-size: 12px;
    }
  }
}

// 分页容器
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px 24px;
  background: transparent;
  border-top: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.3s ease;
  margin-top: 0;

  /* 覆盖 Element Plus 默认主题变量 */
  --el-color-primary: var(--primary-color);
  --el-color-primary-light-3: #9370db;
  --el-color-primary-light-5: #a888e0;
  --el-color-primary-light-7: #c2a9f3;
  --el-color-primary-light-9: #f8f7ff;
  --el-border-color: rgba(147, 112, 219, 0.2);
  --el-border-color-light: rgba(147, 112, 219, 0.15);
  --el-border-color-lighter: rgba(147, 112, 219, 0.1);
  --el-fill-color-light: #f8f7ff;
  --el-fill-color-lighter: #f8f7ff;
  --el-fill-color-blank: #f8f7ff;
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
      color: #5a32a3;
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
          border: 1px solid rgba(147, 112, 219, 0.2);
          background: #ffffff;
          box-shadow: none;

          &:hover {
            border-color: #7b42f6;
            box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
          }

          &.is-focus {
            border-color: #7b42f6;
            box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.15);
          }
        }

        .el-input__inner {
          color: #5a32a3;
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
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff;
      color: #5a32a3;
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border-color: transparent;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
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

    // 页码
    .el-pager {
      display: flex;
      gap: 4px;

      li {
        min-width: 32px;
        height: 32px;
        padding: 0 8px;
        border-radius: 8px;
        border: 1px solid rgba(147, 112, 219, 0.2);
        background: #ffffff;
        color: #5a32a3;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;

        &:hover:not(.is-active) {
          background: rgba(123, 66, 246, 0.1);
          border-color: #7b42f6;
          color: #7b42f6;
          transform: translateY(-1px);
        }

        &.is-active {
          background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
          border-color: transparent;
          color: white;
          box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
          font-weight: 600;
        }

        &.btn-quicknext,
        &.btn-quickprev {
          border: 1px solid rgba(147, 112, 219, 0.2);
          color: #9370db;

          &:hover {
            background: rgba(123, 66, 246, 0.1);
            color: #7b42f6;
          }
        }
      }
    }

    // 跳转页
    .el-pagination__jump {
      margin-left: 12px;
      color: #5a32a3;
      font-weight: 500;

      .el-input__wrapper {
        width: 48px;
        border-radius: 8px;
        border: 1px solid rgba(147, 112, 219, 0.2);
        background: #ffffff;
        box-shadow: none;

        &:hover {
          border-color: #7b42f6;
          box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
        }

        &.is-focus {
          border-color: #7b42f6;
          box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.15);
        }
      }

      .el-input__inner {
        color: #5a32a3;
        font-weight: 500;
        text-align: center;
      }
    }
  }
}

// 报告详情样式
.report-detail {
  .statistics-section {
    margin-top: 30px;

    h4 {
      margin: 0 0 20px 0;
      color: #303133;
    }

    .stat-card {
      background: #f5f7fa;
      padding: 20px;
      border-radius: 4px;
      text-align: center;

      &.success {
        background: #f0f9ff;
        border: 1px solid #b3e5fc;
      }

      &.danger {
        background: #fef0f0;
        border: 1px solid #fde2e2;
      }

      &.warning {
        background: #fdf6ec;
        border: 1px solid #faecd8;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 10px;
      }

      .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #303133;
      }
    }

    .pass-rate-chart {
      margin-top: 30px;

      h5 {
        margin: 0 0 15px 0;
        color: #303133;
        font-size: 16px;
      }
    }
  }

  .result-section {
    margin-top: 30px;

    h4 {
      margin: 0 0 15px 0;
      color: #303133;
    }

    .result-data {
      background: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      max-height: 400px;
      overflow: auto;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 12px;
      line-height: 1.5;
    }
  }

  .error-section {
    margin-top: 30px;

    h4 {
      margin: 0 0 15px 0;
      color: #303133;
    }
  }
}

// 统一的错误信息样式
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

// 用例详情样式
.case-detail {
  h4 {
    margin: 0 0 20px 0;
    color: #303133;
    font-size: 16px;
  }

  .log-container {
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
      border-left: 3px solid #409eff;

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
        align-items: center;
        gap: 8px;
        color: #f56c6c;
        background: #fef0f0;
        padding: 8px 12px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 14px;
      }
    }
  }

  .screenshot-container {
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

      .screenshot-img {
        max-width: 100%;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .screenshot-time {
        margin: 10px 0 0 0;
        color: #909399;
        font-size: 12px;
      }
    }
  }
}
</style>
