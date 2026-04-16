<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">{{ $t('apiTesting.report.title') }}</h3>
      <div class="actions">
        <el-button type="primary" class="refresh-btn" @click="refreshReports">
          <el-icon><Refresh /></el-icon>
          {{ $t('apiTesting.report.refreshReport') }}
        </el-button>
        <el-button class="view-allure-btn" @click="openAllureReport">
          <el-icon><Document /></el-icon>
          {{ $t('apiTesting.report.viewAllureReport') }}
        </el-button>
      </div>
    </div>

    <div class="card-container">
      <el-table :data="reports" v-loading="loading" stripe style="width: 100%">
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="test_suite_name" :label="$t('apiTesting.report.testSuite')" min-width="200" header-align="center" align="center" />
        <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="total_requests" :label="$t('apiTesting.report.totalRequests')" width="100" header-align="center" align="center" />
        <el-table-column prop="passed_requests" :label="$t('apiTesting.report.passedCount')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: bold;">{{ row.passed_requests }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_requests" :label="$t('apiTesting.report.failedCount')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ row.failed_requests }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="executed_by.username" :label="$t('apiTesting.report.executor')" width="120" header-align="center" align="center" />
        <el-table-column prop="created_at" :label="$t('apiTesting.report.executionTime')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('apiTesting.common.operation')" width="180" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" class="action-btn view-btn" size="small" @click="viewReportDetail(row)">
                <el-icon><Document /></el-icon>
                <span>{{ $t('apiTesting.report.generateAndViewReport') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Refresh, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const { t } = useI18n()
const reports = ref([])
const loading = ref(false)

const loadReports = async () => {
  loading.value = true
  try {
    const response = await api.get('/api-testing/test-executions/')
    reports.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadReports'))
  } finally {
    loading.value = false
  }
}

const refreshReports = async () => {
  await loadReports()
}

const generateAndOpenAllureReport = async (executionId) => {
  try {
    // 调用API生成Allure报告数据
    const response = await api.post(`/api-testing/test-executions/${executionId}/generate-allure-report/`)
    ElMessage.success(t('apiTesting.messages.success.reportGenerated'))

    // 通过当前窗口的origin构造完整的URL，确保通过Vite代理访问
    const fullUrl = `${window.location.origin}${response.data.report_url}`;
    window.open(fullUrl, '_blank')
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.reportGenerateFailed'))
  }
}

const openAllureReport = () => {
  // 提示用户需要先选择一个执行记录来生成报告
  ElMessage.info(t('apiTesting.report.selectExecutionTip'))
}

const viewReportDetail = (report) => {
  // 生成并打开Allure报告
  generateAndOpenAllureReport(report.id)
}

const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger',
    'CANCELLED': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusClass = (status) => {
  const classMap = {
    'PENDING': 'pending',
    'RUNNING': 'running',
    'COMPLETED': 'success',
    'FAILED': 'failed',
    'CANCELLED': 'aborted'
  }
  return classMap[status] || 'pending'
}

const getStatusText = (status) => {
  const statusKey = {
    'PENDING': 'pending',
    'RUNNING': 'running',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled'
  }[status]
  return statusKey ? t(`apiTesting.report.status.${statusKey}`) : status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped lang="scss">
// 状态徽章样式
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

  // 成功 - 绿色
  &.success {
    background: #f6ffed;
    color: #52c41a;
  }

  // 失败 - 红色
  &.failed {
    background: #fff1f0;
    color: #ff4d4f;
  }

  // 已取消 - 橙色
  &.aborted {
    background: #fff7e6;
    color: #fa8c16;
  }
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

  .page-title {
    display: none;
  }

  .actions {
    display: flex;
    gap: 12px;
    margin-left: auto;
  }

  .refresh-btn {
    background: #7b42f6 !important;
    border: none !important;
    color: white !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(123, 66, 246, 0.25) !important;
    font-size: 13px !important;

    &:hover {
      background: #6d33e6 !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.35) !important;
    }

    &:active {
      transform: translateY(0) !important;
      background: #5a32a3 !important;
    }

    .el-icon {
      font-size: 14px;
      margin-right: 4px;
    }
  }

  .view-allure-btn {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    transition: all 0.3s ease !important;
    font-size: 13px !important;

    &:hover {
      background: #f5f3ff !important;
      border-color: #a78bfa !important;
      color: #8b5cf6 !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2) !important;
    }

    &:active {
      transform: translateY(0) !important;
      background: #ede9fe !important;
      border-color: #8b5cf6 !important;
      color: #7c3aed !important;
    }

    .el-icon {
      font-size: 14px;
      margin-right: 4px;
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
}
</style>