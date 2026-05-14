<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">{{ $t('apiTesting.report.title') }}</h3>
      <div class="header-search">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索测试场景"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #suffix>
            <el-icon @click="handleSearch" style="cursor: pointer;"><Search /></el-icon>
          </template>
        </el-input>
      </div>

    </div>

    <div class="card-container">
      <el-table :data="reports" v-loading="loading" stripe style="width: 100%">
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (currentPage - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="test_suite_name" :label="$t('apiTesting.report.testSuite')" min-width="200" header-align="center" align="center" />
        <el-table-column prop="status" label="执行结果" width="120" header-align="center" align="center">
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
        <el-table-column label="通过率" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span :style="{ color: getPassRateColor(row), fontWeight: 'bold' }">{{ calculatePassRate(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="executed_by.username" :label="$t('apiTesting.report.executor')" width="120" header-align="center" align="center" />
        <el-table-column prop="created_at" :label="$t('apiTesting.report.executionTime')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('apiTesting.common.operation')" width="220" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" class="action-btn view-btn" size="small" @click="viewReportDetail(row)">
                <el-icon><View /></el-icon>
                <span>查看报告</span>
              </el-button>
              <el-button type="danger" class="action-btn delete-btn" size="small" @click="deleteReport(row)">
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Refresh, Document, Search, View, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const { t } = useI18n()
const reports = ref([])
const loading = ref(false)
const searchKeyword = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 过滤后的报告列表
const filteredReports = computed(() => {
  if (!searchKeyword.value.trim()) {
    return reports.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return reports.value.filter(report => {
    const suiteName = report.test_suite_name || ''
    return suiteName.toLowerCase().includes(keyword)
  })
})

const loadReports = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 添加搜索参数
    if (searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim()
    }
    
    const response = await api.get('/api-testing/test-executions/', { params })
    reports.value = response.data.results || response.data
    total.value = response.data.count || reports.value.length
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadReports'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadReports()
}

const refreshReports = async () => {
  await loadReports()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadReports()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadReports()
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
    // 显示后端返回的详细错误信息
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || t('apiTesting.messages.error.reportGenerateFailed')
    ElMessage.error(`生成报告失败: ${errorMsg}`)
    console.error('生成报告错误:', error.response?.data || error)
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

const deleteReport = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试报告 "${report.test_suite_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/api-testing/test-executions/${report.id}/`)
    ElMessage.success('删除成功')
    await loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.detail || error.message || '删除失败'
      ElMessage.error(errorMsg)
    }
  }
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

const calculatePassRate = (row) => {
  const total = row.total_requests || 0
  const passed = row.passed_requests || 0
  if (total === 0) return '0.0%'
  return ((passed / total) * 100).toFixed(1) + '%'
}

const getPassRateColor = (row) => {
  const total = row.total_requests || 0
  const passed = row.passed_requests || 0
  if (total === 0) return '#9ca3af'
  const rate = passed / total
  if (rate === 1) return '#52c41a' // 100% 绿色
  if (rate >= 0.8) return '#73d13d' // 80%+ 浅绿
  if (rate >= 0.6) return '#faad14' // 60%+ 黄色
  return '#f5222d' // 低于60% 红色
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

  .header-search {
    flex: 1;
    max-width: 200px;
    margin: 0 auto 0 0;

    .search-input {
      width: 100%;

      :deep(.el-input__wrapper) {
        border-radius: 8px;
        background: #ffffff !important;
        box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.2) inset;

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

        &::placeholder {
          color: #9ca3af;
        }
      }

      :deep(.el-input__suffix) {
        color: #9ca3af;

        .el-icon {
          &:hover {
            color: #7b42f6;
          }
        }
      }
    }
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
  padding: 6px 12px !important;
  border-radius: 6px;
  transition: all 0.3s ease;
  border: none !important;
  color: #ffffff !important;
  min-width: 70px;

  .el-icon {
    font-size: 13px;
    color: #ffffff !important;
  }

  span {
    font-size: 12px;
    color: #ffffff !important;
  }

  &.view-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;

    &:hover {
      background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
    }
  }

  &.delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #f5222d 100%) !important;

    &:hover {
      background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(245, 34, 45, 0.4);
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

          &:hover {
            background: #ede9fe;
            border-color: #8b5cf6;
          }
        }
      }
    }

    // 跳转输入框
    .el-pagination__jump {
      margin-left: 12px;
      color: #6b7280;
      font-size: 14px;
      font-weight: 500;

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
</style>