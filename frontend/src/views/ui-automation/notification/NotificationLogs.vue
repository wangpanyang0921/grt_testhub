<template>
  <div class="page-container">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchForm.taskName"
        :placeholder="$t('uiAutomation.notification.logs.searchTaskName')"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 260px;"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="searchForm.status"
        :placeholder="$t('uiAutomation.notification.logs.notificationStatus')"
        clearable
        @change="handleSearch"
        style="width: 160px;"
        class="status-select"
      >
        <el-option :label="$t('uiAutomation.notification.logs.allStatus')" value=""/>
        <el-option :label="$t('uiAutomation.notification.logs.statusSuccess')" value="success"/>
        <el-option :label="$t('uiAutomation.notification.logs.statusFailed')" value="failed"/>
        <el-option :label="$t('uiAutomation.notification.logs.statusPending')" value="pending"/>
        <el-option :label="$t('uiAutomation.notification.logs.statusSending')" value="sending"/>
      </el-select>
    </div>

    <!-- 通知列表 -->
    <div class="card-container">
      <el-table
        :data="logsData"
        v-loading="loading"
        :element-loading-text="$t('uiAutomation.notification.logs.messages.loading')"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column
          prop="task_name"
          :label="$t('uiAutomation.notification.logs.taskName')"
          min-width="150"
          header-align="center"
          align="center"
        />
        <el-table-column
          prop="task_type_display"
          :label="$t('uiAutomation.notification.logs.taskType')"
          min-width="100"
          header-align="center"
          align="center"
        >
          <template #default="{ row }">
            <span class="task-type-badge" :class="getTaskTypeClass(row.task_type_display)">
              {{ row.task_type_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="actual_notification_type_display"
          :label="$t('uiAutomation.notification.logs.notificationType')"
          min-width="120"
          header-align="center"
          align="center"
        >
          <template #default="{ row }">
            <span class="notification-type-badge" :class="getNotificationTypeClass(row.actual_notification_type_display)">
              {{ row.actual_notification_type_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="created_at"
          :label="$t('uiAutomation.notification.logs.notificationTime')"
          min-width="180"
          header-align="center"
          align="center"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status_display"
          :label="$t('uiAutomation.common.status')"
          min-width="100"
          header-align="center"
          align="center"
        >
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status_display)">
              {{ row.status_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('uiAutomation.common.operation')"
          fixed="right"
          width="120"
          header-align="center"
          align="center"
        >
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                size="small"
                class="action-btn view-btn"
                @click="viewDetail(row)"
              >
                <el-icon><View /></el-icon>
                <span>{{ $t('uiAutomation.notification.logs.viewDetail') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
        v-model="detailDialogVisible"
        :title="$t('uiAutomation.notification.logs.detailTitle')"
        width="600px"
        :before-close="handleDetailDialogClose"
    >
      <el-form
          v-if="selectedLog"
          label-position="left"
          label-width="100px"
          class="notification-detail-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('uiAutomation.notification.logs.taskName') + ':'">
              <span>{{ selectedLog.task_name }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('uiAutomation.notification.logs.taskType') + ':'">
              <span>{{ selectedLog.task_type_display }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('uiAutomation.notification.logs.notificationType') + ':'">
              <el-tag :type="getNotificationTypeTagType(selectedLog.actual_notification_type_display)">
                {{ selectedLog.actual_notification_type_display }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('uiAutomation.common.status') + ':'">
              <el-tag :type="getStatusTagType(selectedLog.status_display)">
                {{ selectedLog.status_display }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('uiAutomation.notification.logs.notificationTime') + ':'">
              <span>{{ formatDate(selectedLog.created_at) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('uiAutomation.notification.logs.sentTime') + ':'">
              <span>{{ selectedLog.sent_at ? formatDate(selectedLog.sent_at) : '-' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="selectedLog.webhook_bot_info && (selectedLog.webhook_bot_info.bot_type || selectedLog.webhook_bot_info.type)">
            <el-form-item :label="$t('uiAutomation.notification.logs.webhookBot') + ':'">
              <div class="webhook-info">
                <el-tag
                    class="webhook-tag"
                    size="small"
                    type="info"
                >
                  {{ selectedLog.webhook_bot_info.name || selectedLog.webhook_bot_info.bot_name || $t('uiAutomation.notification.logs.defaultBotName') }}
                </el-tag>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="$t('uiAutomation.notification.logs.content') + ':'" class="content-form-item">
              <div class="notification-content">
                <div v-if="parsedNotificationContent" class="notification-content-parsed">
                  <div class="content-item" v-for="(item, index) in parsedNotificationContent" :key="index">
                    <span class="content-label">{{ item.label }}:</span>
                    <span class="content-value">{{ item.value }}</span>
                  </div>
                </div>
                <div v-else class="notification-content-raw">
                  <pre>{{ selectedLog.notification_content || '-' }}</pre>
                </div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="selectedLog.error_message">
            <el-form-item :label="$t('uiAutomation.notification.logs.errorMessage') + ':'" class="error-form-item">
              <div class="error-message">
                <el-alert
                    :title="selectedLog.error_message"
                    type="error"
                    show-icon
                    :closable="false"
                />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">{{ $t('uiAutomation.common.close') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {Search, View} from '@element-plus/icons-vue'
import {ref, reactive, onMounted, computed} from 'vue'
import {ElMessage} from 'element-plus'
import { getNotificationLogs } from '@/api/ui_automation.js'
import { useI18n } from 'vue-i18n'

export default {
  name: 'NotificationLogs',
  components: {
    Search,
    View
  },
  setup() {
    const { t, locale } = useI18n()

    // 数据状态
    const loading = ref(false)
    const logsData = ref([])
    const detailDialogVisible = ref(false)
    const selectedLog = ref(null)

    // 搜索表单
    const searchForm = reactive({
      taskName: '',
      dateRange: [],
      status: ''
    })

    // 分页配置
    const pagination = reactive({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })

    // 排序参数
    const sortParams = reactive({
      prop: 'created_at',
      order: 'descending'
    })

    // 获取通知日志数据
    const fetchLogsData = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize,
          ordering: sortParams.order === 'ascending' ? sortParams.prop : `-${sortParams.prop}`
        }

        // 添加搜索条件
        if (searchForm.taskName) {
          params.search = searchForm.taskName
        }
        if (searchForm.dateRange && searchForm.dateRange.length === 2) {
          params.start_date = searchForm.dateRange[0]
          params.end_date = searchForm.dateRange[1]
        }
        if (searchForm.status) {
          params.status = searchForm.status
        }

        const response = await getNotificationLogs(params)
        logsData.value = response.data.results || []
        pagination.total = response.data.count || 0
      } catch (error) {
        console.error('Failed to fetch notification logs:', error)
        ElMessage.error(t('uiAutomation.notification.logs.messages.loadFailed'))
      } finally {
        loading.value = false
      }
    }

    // 处理搜索
    const handleSearch = () => {
      pagination.currentPage = 1
      fetchLogsData()
    }

    // 重置搜索
    const handleReset = () => {
      searchForm.taskName = ''
      searchForm.dateRange = []
      searchForm.status = ''
      pagination.currentPage = 1
      fetchLogsData()
    }

    // 处理分页变化
    const handleSizeChange = (val) => {
      pagination.pageSize = val
      pagination.currentPage = 1
      fetchLogsData()
    }

    const handleCurrentChange = (val) => {
      pagination.currentPage = val
      fetchLogsData()
    }

    // 处理排序
    const handleSortChange = ({prop, order}) => {
      sortParams.prop = prop
      sortParams.order = order || 'descending'
      fetchLogsData()
    }

    // 查看详情
    const viewDetail = (row) => {
      selectedLog.value = row
      detailDialogVisible.value = true
    }

    // 关闭详情弹窗
    const handleDetailDialogClose = (done) => {
      selectedLog.value = null
      done()
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString(locale.value === 'zh-cn' ? 'zh-CN' : 'en-US')
    }

    // 获取状态标签类型
    const getStatusTagType = (status) => {
      const typeMap = {
        // Chinese
        '发送成功': 'success',
        '发送失败': 'danger',
        '待发送': 'info',
        '发送中': 'warning',
        '已取消': 'info',
        // English
        'Success': 'success',
        'Failed': 'danger',
        'Pending': 'info',
        'Sending': 'warning',
        'Cancelled': 'info',
        // Lowercase
        'success': 'success',
        'failed': 'danger',
        'pending': 'info',
        'sending': 'warning',
        'cancelled': 'info'
      }
      return typeMap[status] || 'info'
    }

    // 获取通知类型标签类型
    const getNotificationTypeTagType = (typeDisplay) => {
      const typeMap = {
        // Chinese
        '邮箱通知': '',
        'Webhook机器人': 'primary',
        '飞书机器人': 'primary',
        '两种都发送': 'warning',
        // English
        'Email': '',
        'Webhook Bot': 'primary',
        'Both': 'warning'
      }
      return typeMap[typeDisplay] || 'info'
    }

    // 获取通知类型样式类
    const getNotificationTypeClass = (typeDisplay) => {
      const typeMap = {
        // Chinese
        '邮箱通知': 'email',
        'Webhook机器人': 'webhook',
        '飞书机器人': 'webhook',
        '两种都发送': 'both',
        // English
        'Email': 'email',
        'Webhook Bot': 'webhook',
        'Both': 'both'
      }
      return typeMap[typeDisplay] || ''
    }

    // 获取任务类型样式类
    const getTaskTypeClass = (taskTypeDisplay) => {
      const typeMap = {
        // Chinese
        '测试用例执行': 'test-case',
        '测试套件执行': 'test-suite',
        // English
        'Test Case Execution': 'test-case',
        'Test Suite Execution': 'test-suite'
      }
      return typeMap[taskTypeDisplay] || ''
    }

    // 获取状态样式类
    const getStatusClass = (status) => {
      const classMap = {
        // Chinese
        '发送成功': 'success',
        '发送失败': 'failed',
        '待发送': 'pending',
        '发送中': 'sending',
        '已取消': 'cancelled',
        // English
        'Success': 'success',
        'Failed': 'failed',
        'Pending': 'pending',
        'Sending': 'sending',
        'Cancelled': 'cancelled',
        // Lowercase
        'success': 'success',
        'failed': 'failed',
        'pending': 'pending',
        'sending': 'sending',
        'cancelled': 'cancelled'
      }
      return classMap[status] || 'default'
    }

    // 解析通知内容为结构化数据
    const parsedNotificationContent = computed(() => {
      if (!selectedLog.value || !selectedLog.value.notification_content) {
        return null
      }

      const content = selectedLog.value.notification_content

      try {
        // 尝试解析JSON格式的通知内容(Webhook)
        const jsonContent = JSON.parse(content)
        const result = []

        // 提取内容文本
        let contentText = ''

        // 处理企业微信格式
        if (jsonContent.msgtype === 'markdown' && jsonContent.markdown) {
          // 优先使用text字段(钉钉格式)
          if (jsonContent.markdown.text) {
            contentText = jsonContent.markdown.text
          } else if (jsonContent.markdown.content) {
            contentText = jsonContent.markdown.content
          }
        }
        // 处理飞书格式
        else if (jsonContent.msg_type === 'interactive' && jsonContent.card) {
          if (jsonContent.card.elements && jsonContent.card.elements[0] && jsonContent.card.elements[0].text) {
            contentText = jsonContent.card.elements[0].text.content
          }
        }

        if (contentText) {
          // 解析文本内容,提取关键信息
          const lines = contentText.split('\n').filter(line => line.trim())

          lines.forEach(line => {
            // 跳过标题行(包含**的行)和空行
            if (line.includes('**') || line.trim() === '') {
              return
            }

            // 解析键值对
            const colonIndex = line.indexOf(':')
            if (colonIndex > 0) {
              const label = line.substring(0, colonIndex).trim()
              const value = line.substring(colonIndex + 1).trim()

              if (label && value) {
                result.push({
                  label: label,
                  value: value
                })
              }
            }
          })

          return result.length > 0 ? result : null
        }
      } catch (e) {
        // JSON解析失败,尝试作为纯文本解析(邮件通知)
        console.log('Attempting to parse as plain text format')
      }

      // 解析纯文本格式的邮件内容
      try {
        const result = []
        const lines = content.split('\n').filter(line => line.trim())

        lines.forEach(line => {
          // 跳过空行
          if (!line.trim()) {
            return
          }

          // 解析键值对 (格式: "标签: 值")
          const colonIndex = line.indexOf(':')
          if (colonIndex > 0) {
            const label = line.substring(0, colonIndex).trim()
            const value = line.substring(colonIndex + 1).trim()

            // 过滤掉包含详细测试结果的行(通常会是大字典或JSON字符串)
            // 跳过包含'results'关键字的超长值
            if (label && value && !value.includes("'results':") && !value.includes('"results":')) {
              result.push({
                label: label,
                value: value
              })
            }
          }
        })

        return result.length > 0 ? result : null
      } catch (e) {
        // 如果所有解析都失败,返回null以显示原始内容
        console.error('Failed to parse notification content:', e)
        return null
      }
    })

    // 组件挂载时获取数据
    onMounted(() => {
      fetchLogsData()
    })

    return {
      loading,
      logsData,
      detailDialogVisible,
      selectedLog,
      searchForm,
      pagination,
      sortParams,
      parsedNotificationContent,
      handleSearch,
      handleReset,
      handleSizeChange,
      handleCurrentChange,
      handleSortChange,
      viewDetail,
      handleDetailDialogClose,
      formatDate,
      getStatusTagType,
      getNotificationTypeTagType,
      getNotificationTypeClass,
      getTaskTypeClass,
      getStatusClass
    }
  }
}
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
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border: 1px solid rgba(147, 112, 219, 0.1);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;

  .status-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.3);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  .search-input {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.3);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  // 日期选择器宽度限制
  :deep(.el-date-editor--daterange) {
    width: 320px !important;
    max-width: 320px !important;

    .el-input__wrapper {
      width: 100% !important;
    }

    .el-range-separator {
      color: #999;
    }
  }

  .filter-bar-spacer {
    flex: 1;
  }
}

.reset-btn {
  background: #f8f7ff !important;
  border: 1px solid rgba(147, 112, 219, 0.2) !important;
  color: #5a32a3 !important;
  font-weight: 500 !important;
  padding: 9px 20px !important;
  border-radius: 8px !important;
  transition: all 0.3s ease !important;

  &:hover {
    background: #ede9fe !important;
    border-color: #7b42f6 !important;
    transform: translateY(-1px);
  }
}

.query-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: #ffffff !important;
  font-weight: 500 !important;
  padding: 9px 24px !important;
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.25) !important;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(123, 66, 246, 0.35) !important;
  }
}

.filter-row {
  display: flex;
  align-items: center;

  .button-col {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    white-space: nowrap;
  }
}

// 卡片容器
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
          text-align: center;
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
        line-height: 24px;

        &:hover {
          background-color: #f8f7ff !important;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(147, 112, 219, 0.1);
        }

        &.el-table__row--striped {
          background-color: #fafaff !important;
        }

        // 表格单元格
        :deep(td) {
          padding: 14px 8px;
          border-bottom: 1px solid #e9ecef;
          color: #595959;
          font-size: 14px;
          font-weight: normal;
          line-height: 24px;
          transition: all 0.3s ease;

          // 单元格内部容器样式统一
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
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #9a6af5 0%, #7b42f6 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
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

// 任务类型徽章样式
.task-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.test-case {
    background: #e6fffb;
    color: #13c2c2;
  }

  &.test-suite {
    background: #f0f5ff;
    color: #2f54eb;
  }
}

// 通知类型徽章样式
.notification-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.email {
    background: #fff2e8;
    color: #fa541c;
  }

  &.webhook {
    background: #e6fffb;
    color: #13c2c2;
  }

  &.both {
    background: #f6ffed;
    color: #52c41a;
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

  &.failed {
    background: #fff1f0;
    color: #ff4d4f;
  }

  &.pending {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  &.sending {
    background: #e6f7ff;
    color: #1890ff;
  }

  &.cancelled {
    background: #fff7e6;
    color: #fa8c16;
  }

  &.default {
    background: #f5f5f5;
    color: #8c8c8c;
  }
}

.notification-detail-form :deep(.el-form-item) {
  margin-bottom: 30px;
}

.notification-detail-form :deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
  justify-content: flex-end;
  padding-right: 8px;
}

.notification-detail-form :deep(.el-form-item__content) {
  color: #303133;
  display: flex;
  align-items: center;
}

.notification-detail-form :deep(.content-form-item .el-form-item__content),
.notification-detail-form :deep(.error-form-item .el-form-item__content) {
  display: block;
}

.notification-content {
  width: 100%;
}

.notification-content-parsed {
  background: transparent;
  padding: 0;
}

.content-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.content-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.content-item:first-child {
  padding-top: 0;
}

.content-label {
  font-weight: 500;
  color: #606266;
  min-width: 100px;
  flex-shrink: 0;
  margin-right: 8px;
  font-size: 14px;
  line-height: 1.8;
  text-align: right;
}

.content-value {
  color: #303133;
  flex: 1;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.8;
}

.notification-content-raw pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  max-height: 400px;
  overflow-y: auto;
}

.notification-content-raw pre::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.notification-content-raw pre::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.notification-content-raw pre::-webkit-scrollbar-thumb:hover {
  background: #a8abb2;
}

.webhook-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.webhook-tag {
  margin: 0;
}

.error-message {
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
