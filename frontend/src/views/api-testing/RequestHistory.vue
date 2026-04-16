<template>
  <div class="page-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-input
          v-model="searchText"
          :placeholder="$t('apiTesting.history.searchRequest')"
          class="search-input"
          clearable
          @input="loadHistory"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="activeTab"
          @change="onTabChange"
          class="type-select"
        >
          <el-option
            :label="$t('apiTesting.history.httpRequest')"
            value="HTTP"
          />
          <el-option
            :label="$t('apiTesting.history.websocketRequest')"
            value="WEBSOCKET"
          />
        </el-select>
      </div>
      <div class="header-actions">
        <el-button
          type="danger"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
          class="action-btn batch-delete-btn"
        >
          <el-icon><Delete /></el-icon>
          <span>{{ $t('apiTesting.history.batchDelete') }}</span>
        </el-button>
        <el-button @click="clearHistory" type="danger" plain class="action-btn clear-btn">
          <el-icon><DeleteFilled /></el-icon>
          <span>{{ $t('apiTesting.history.clearHistory') }}</span>
        </el-button>
      </div>
    </div>

    <!-- 历史记录卡片 -->
    <div class="card-container">
      <!-- HTTP 请求历史表格 -->
      <div v-if="activeTab === 'HTTP'" class="table-wrapper">
        <HistoryTable
          :data="httpHistory"
          :loading="loading"
          @view-detail="viewDetail"
          @retry-request="retryRequest"
          @selection-change="handleSelectionChange"
          @delete-item="handleDelete"
        />
      </div>
      <!-- WebSocket 请求历史表格 -->
      <div v-else class="table-wrapper">
        <HistoryTable
          :data="websocketHistory"
          :loading="loading"
          @view-detail="viewDetail"
          @retry-request="retryRequest"
          @selection-change="handleSelectionChange"
          @delete-item="handleDelete"
        />
      </div>

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

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="$t('apiTesting.history.requestDetail')"
      width="80%"
      :top="'5vh'"
      class="detail-dialog"
    >
      <div v-if="selectedHistory" class="history-detail">
        <el-descriptions :title="$t('apiTesting.history.basicInfo')" :column="2" border class="custom-descriptions">
          <el-descriptions-item :label="$t('apiTesting.interface.requestName')">
            {{ selectedHistory.request.name }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.requestMethod')">
            <span class="method-badge" :class="getMethodClass(selectedHistory.request.method)">
              {{ selectedHistory.request.method }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.statusCode')">
            <span class="status-badge" :class="getStatusClass(selectedHistory.status_code)">
              {{ selectedHistory.status_code || $t('apiTesting.history.noResponse') }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.responseTime')">
            <span class="response-time">{{ selectedHistory.response_time?.toFixed(0) || 0 }}ms</span>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.executionTime')">
            {{ formatDate(selectedHistory.executed_at) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.executor')">
            {{ selectedHistory.executed_by.username }}
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="detailTab" class="detail-tabs custom-tabs">
          <el-tab-pane :label="$t('apiTesting.history.requestInfo')" name="request">
            <div class="detail-section">
              <h4 class="section-title">{{ $t('apiTesting.history.requestUrl') }}</h4>
              <el-input v-model="selectedHistory.request_data.url" readonly class="readonly-input" />

              <h4 class="section-title">{{ $t('apiTesting.history.requestHeaders') }}</h4>
              <el-table :data="formatHeaders(selectedHistory.request_data.headers)" style="width: 100%" class="custom-table">
                <el-table-column prop="key" label="Key" width="200" header-align="center" align="center" />
                <el-table-column prop="value" label="Value" header-align="center" align="center" />
              </el-table>

              <h4 v-if="selectedHistory.request_data.params && Object.keys(selectedHistory.request_data.params).length > 0" class="section-title">
                {{ $t('apiTesting.history.requestParams') }}
              </h4>
              <el-table
                v-if="selectedHistory.request_data.params && Object.keys(selectedHistory.request_data.params).length > 0"
                :data="formatHeaders(selectedHistory.request_data.params)"
                style="width: 100%"
                class="custom-table"
              >
                <el-table-column prop="key" label="Key" width="200" header-align="center" align="center" />
                <el-table-column prop="value" label="Value" header-align="center" align="center" />
              </el-table>

              <h4 v-if="selectedHistory.request_data.body" class="section-title">{{ $t('apiTesting.history.requestBody') }}</h4>
              <pre v-if="selectedHistory.request_data.body" class="json-content">
                {{ JSON.stringify(selectedHistory.request_data.body, null, 2) }}
              </pre>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('apiTesting.history.responseInfo')" name="response">
            <div v-if="selectedHistory.response_data" class="detail-section">
              <h4 class="section-title">{{ $t('apiTesting.history.responseHeaders') }}</h4>
              <el-table :data="formatHeaders(selectedHistory.response_data.headers)" style="width: 100%" class="custom-table">
                <el-table-column prop="key" label="Key" width="200" header-align="center" align="center" />
                <el-table-column prop="value" label="Value" header-align="center" align="center" />
              </el-table>

              <h4 class="section-title">{{ $t('apiTesting.history.responseBody') }}</h4>
              <div class="response-actions">
                <el-button size="small" @click="formatResponseBody" class="action-btn">
                  <el-icon><DocumentChecked /></el-icon>
                  <span>{{ $t('apiTesting.interface.format') }}</span>
                </el-button>
                <el-button size="small" @click="copyResponseBody" class="action-btn">
                  <el-icon><DocumentCopy /></el-icon>
                  <span>{{ $t('apiTesting.common.copy') }}</span>
                </el-button>
              </div>
              <pre class="json-content">{{ responseBodyText }}</pre>
            </div>

            <div v-else-if="selectedHistory.error_message" class="error-section">
              <h4 class="section-title">{{ $t('apiTesting.automation.status.failed') }}</h4>
              <el-alert
                :title="selectedHistory.error_message"
                type="error"
                :closable="false"
                show-icon
              />
            </div>

            <div v-else class="empty-response">
              <el-empty :description="$t('apiTesting.history.noResponseData')" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false" class="cancel-btn">{{ $t('apiTesting.common.close') }}</el-button>
        <el-button type="primary" @click="retryRequest(selectedHistory)" class="confirm-btn">
          <el-icon><RefreshRight /></el-icon>
          <span>{{ $t('apiTesting.history.retryRequest') }}</span>
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Search, Delete, DeleteFilled, DocumentChecked, DocumentCopy, RefreshRight } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { deleteRequestHistory, batchDeleteRequestHistory } from '@/api/api-testing'
import dayjs from 'dayjs'
import HistoryTable from './components/HistoryTable.vue'

const { t } = useI18n()
const activeTab = ref('HTTP')
const httpHistory = ref([])
const websocketHistory = ref([])
const loading = ref(false)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const showDetailDialog = ref(false)
const selectedHistory = ref(null)
const detailTab = ref('request')
const selectedIds = ref([])

const currentHistory = computed(() => {
  return activeTab.value === 'HTTP' ? httpHistory.value : websocketHistory.value
})

const responseBodyText = computed(() => {
  if (!selectedHistory.value?.response_data) return ''
  
  try {
    if (selectedHistory.value.response_data.json) {
      return JSON.stringify(selectedHistory.value.response_data.json, null, 2)
    } else {
      return selectedHistory.value.response_data.body || ''
    }
  } catch (e) {
    return selectedHistory.value.response_data.body || ''
  }
})

const getMethodClass = (method) => {
  const classMap = {
    'GET': 'get',
    'POST': 'post',
    'PUT': 'put',
    'DELETE': 'delete',
    'PATCH': 'patch'
  }
  return classMap[method] || 'default'
}

const getStatusClass = (status) => {
  if (!status) return 'default'
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'error'
  return 'default'
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

const formatHeaders = (headers) => {
  if (!headers || typeof headers !== 'object') return []
  return Object.keys(headers).map(key => ({
    key,
    value: headers[key]
  }))
}

const loadHistory = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      request__request_type: activeTab.value
    }

    if (searchText.value) {
      params.search = searchText.value
    }

    const response = await api.get('/api-testing/histories/', { params })
    const data = response.data.results || response.data

    if (activeTab.value === 'HTTP') {
      httpHistory.value = data
    } else {
      websocketHistory.value = data
    }

    total.value = response.data.count || data.length
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadHistory'))
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onTabChange = () => {
  currentPage.value = 1
  selectedIds.value = []
  loadHistory()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadHistory()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadHistory()
}

const viewDetail = (history) => {
  selectedHistory.value = history
  detailTab.value = 'request'
  showDetailDialog.value = true
}

const retryRequest = async (history) => {
  try {
    const response = await api.post(`/api-testing/requests/${history.request.id}/execute/`, {
      environment_id: history.environment?.id
    })
    ElMessage.success(t('apiTesting.messages.success.requestRetried'))
    showDetailDialog.value = false
    await loadHistory()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.sendFailed'))
    console.error(error)
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.history.confirmClearHistory'),
      t('apiTesting.messages.confirm.clearTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    // 这里需要后端提供批量删除接口
    // 目前先用批量删除当前页的方式模拟，或者需要后端增加清空接口
    // 暂时提示未实现
    ElMessage.warning(t('apiTesting.history.clearNotImplemented'))
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(t('apiTesting.history.confirmDelete'), t('apiTesting.common.tip'), {
    confirmButtonText: t('apiTesting.common.confirm'),
    cancelButtonText: t('apiTesting.common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await deleteRequestHistory(row.id)
      ElMessage.success(t('apiTesting.messages.success.delete'))
      loadHistory()
    } catch (error) {
      console.error('Delete failed:', error)
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    }
  })
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return

  ElMessageBox.confirm(t('apiTesting.history.confirmBatchDelete', { n: selectedIds.value.length }), t('apiTesting.common.tip'), {
    confirmButtonText: t('apiTesting.common.confirm'),
    cancelButtonText: t('apiTesting.common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteRequestHistory(selectedIds.value)
      ElMessage.success(t('apiTesting.messages.success.batchDeleteSuccess'))
      selectedIds.value = []
      loadHistory()
    } catch (error) {
      console.error('Batch delete failed:', error)
      ElMessage.error(t('apiTesting.messages.error.batchDeleteFailed'))
    }
  })
}

const formatResponseBody = () => {
  if (selectedHistory.value?.response_data?.json) {
    // 已经格式化了
  }
}

const copyResponseBody = () => {
  if (responseBodyText.value) {
    navigator.clipboard.writeText(responseBodyText.value)
    ElMessage.success(t('apiTesting.messages.success.copiedToClipboard'))
  }
}

onMounted(() => {
  loadHistory()
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
    gap: 12px;
  }

  .type-select {
    width: 160px;

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

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .search-input {
    width: 240px;

    :deep(.el-input__wrapper) {
      background-color: #ffffff;
      border: 1px solid rgba(147, 112, 219, 0.2);
      border-radius: 8px;
      box-shadow: none;
      padding: 0 11px;

      &:hover,
      &.is-focus {
        border-color: #7b42f6;
      }
    }

    :deep(.el-input__inner) {
      height: 30px;
      line-height: 30px;
    }

    :deep(.el-input__prefix) {
      color: #7b42f6;
    }

    :deep(.el-input__prefix-inner) {
      height: 30px;
      display: flex;
      align-items: center;
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

.table-wrapper {
  flex: 1;
  overflow: auto;
}

// 自定义表格样式
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
}

// 分页容器样式 - 参考 ProjectManagement.vue
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

        &.btn-quicknext,
        &.btn-quickprev {
          border: none;
          background: transparent;
          color: #9ca3af;

          &:hover {
            background: #f5f3ff;
            color: #8b5cf6;
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
          padding: 0 8px;

          &:hover,
          &.is-focus {
            border-color: #a78bfa;
            box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
          }
        }

        .el-input__inner {
          height: 32px;
          line-height: 32px;
          color: #374151;
          font-weight: 500;
          text-align: center;
        }
      }
    }
  }
}

// 操作按钮样式
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 16px !important;
  border-radius: 8px;
  transition: all 0.3s ease;

  .el-icon {
    font-size: 14px;
  }

  span {
    font-size: 13px;
  }

  &.batch-delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(255, 77, 79, 0.4);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  &.clear-btn {
    border: 1px solid #ff4d4f !important;
    color: #ff4d4f !important;
    background: transparent !important;

    &:hover {
      background: rgba(255, 77, 79, 0.1) !important;
      transform: translateY(-2px);
    }
  }
}

// 详情对话框样式
.detail-dialog {
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
    }

    .el-dialog__footer {
      padding: 16px 24px 20px;
      border-top: 1px solid #ebeef5;
      background: #fafafa;
    }
  }
}

.history-detail {
  max-height: 70vh;
  overflow-y: auto;
}

// 自定义描述列表样式
.custom-descriptions {
  :deep(.el-descriptions__header) {
    margin-bottom: 16px;

    .el-descriptions__title {
      font-size: 16px;
      font-weight: 600;
      color: #5a32a3;
    }
  }

  :deep(.el-descriptions__label) {
    color: #5a32a3;
    font-weight: 500;
    background: #f8f7ff;
  }

  :deep(.el-descriptions__content) {
    color: #595959;
  }
}

// 方法徽章样式
.method-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.get {
    background: #f6ffed;
    color: #52c41a;
  }

  &.post {
    background: #e6f7ff;
    color: #1890ff;
  }

  &.put {
    background: #fff7e6;
    color: #fa8c16;
  }

  &.delete {
    background: #fff1f0;
    color: #ff4d4f;
  }

  &.patch {
    background: #f9f0ff;
    color: #722ed1;
  }

  &.default {
    background: #f5f5f5;
    color: #8c8c8c;
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
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.success {
    background: #f6ffed;
    color: #52c41a;
  }

  &.warning {
    background: #fff7e6;
    color: #fa8c16;
  }

  &.error {
    background: #fff1f0;
    color: #ff4d4f;
  }

  &.default {
    background: #f5f5f5;
    color: #8c8c8c;
  }
}

.response-time {
  color: #7b42f6;
  font-weight: 600;
}

.detail-tabs {
  margin-top: 24px;
}

.detail-section {
  padding: 10px 0;
}

.section-title {
  margin: 20px 0 12px 0;
  color: #5a32a3;
  font-size: 14px;
  font-weight: 600;

  &:first-child {
    margin-top: 0;
  }
}

.readonly-input {
  :deep(.el-input__wrapper) {
    background: #f8f7ff;
    border: 1px solid rgba(147, 112, 219, 0.2);
    border-radius: 8px;
    box-shadow: none;
  }

  :deep(.el-input__inner) {
    color: #595959;
  }
}

.json-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid rgba(147, 112, 219, 0.15);
  color: #595959;
}

.response-actions {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
}

.error-section {
  padding: 20px 0;
}

.empty-response {
  padding: 40px 0;
  text-align: center;
}

.cancel-btn {
  font-weight: 500;
  padding: 8px 20px;
  border-radius: 8px;
}

.confirm-btn {
  font-weight: 600;
  padding: 8px 20px;
  border-radius: 8px;
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: white !important;

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
  }
}

@media screen and (max-width: 1200px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;

    .header-actions {
      width: 100%;
      flex-wrap: wrap;
    }

    .search-input {
      width: 100%;
      max-width: 300px;
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

  .action-btn {
    span {
      display: none;
    }

    .el-icon {
      margin: 0;
    }
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
