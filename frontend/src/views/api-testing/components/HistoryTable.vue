<template>
  <div class="history-table">
    <el-table
      :data="data"
      v-loading="loading"
      style="width: 100%"
      class="custom-table"
    >
      <el-table-column type="index" :label="$t('apiTesting.common.sequence')" width="90" header-align="center" align="center" />
      <el-table-column prop="request.name" :label="$t('apiTesting.component.historyTable.requestName')" min-width="200" header-align="center" align="center" />
      <el-table-column prop="status_code" :label="$t('apiTesting.component.historyTable.statusCode')" width="100" header-align="center" align="center">
        <template #default="scope">
          <span
            v-if="scope.row.status_code"
            class="status-badge"
            :class="getStatusClass(scope.row.status_code)"
          >
            {{ scope.row.status_code }}
          </span>
          <span v-else class="status-badge error">{{ $t('apiTesting.component.historyTable.error') }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="response_time" :label="$t('apiTesting.component.historyTable.responseTime')" width="120" header-align="center" align="center">
        <template #default="scope">
          <span class="response-time">{{ scope.row.response_time?.toFixed(0) || 0 }}ms</span>
        </template>
      </el-table-column>
      <el-table-column prop="environment.name" :label="$t('apiTesting.component.historyTable.environment')" width="120" header-align="center" align="center">
        <template #default="scope">
          {{ scope.row.environment?.name || $t('apiTesting.component.historyTable.noEnvironment') }}
        </template>
      </el-table-column>
      <el-table-column prop="executed_by.username" :label="$t('apiTesting.component.historyTable.executor')" width="120" header-align="center" align="center" />
      <el-table-column prop="executed_at" :label="$t('apiTesting.component.historyTable.executionTime')" width="180" header-align="center" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.executed_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('apiTesting.common.operation')" width="200" fixed="right" header-align="center" align="center">
        <template #default="scope">
          <div class="action-buttons">
            <el-button size="small" type="primary" class="action-btn view-btn" @click="$emit('view-detail', scope.row)">
              <el-icon><View /></el-icon>
              <span>{{ $t('apiTesting.component.historyTable.viewDetail') }}</span>
            </el-button>
            <el-button size="small" type="danger" class="action-btn delete-btn" @click="$emit('delete-item', scope.row)">
              <el-icon><Delete /></el-icon>
              <span>{{ $t('apiTesting.component.historyTable.delete') }}</span>
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { View, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-detail', 'delete-item'])

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
</script>

<style lang="scss" scoped>
.history-table {
  height: 100%;
}

// 自定义表格样式 - 与 EnvironmentManagement.vue 保持一致
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
  }

  span {
    font-size: 12px;
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
</style>
