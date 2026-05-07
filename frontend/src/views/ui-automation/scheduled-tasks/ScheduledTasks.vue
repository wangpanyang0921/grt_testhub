<template>
  <div class="page-container">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select v-model="filters.task_type" :placeholder="$t('uiAutomation.scheduledTask.taskType')" clearable style="width: 160px;" @change="handleFilterChange">
        <el-option :label="$t('uiAutomation.scheduledTask.taskTypes.testSuite')" value="TEST_SUITE" />
        <el-option :label="$t('uiAutomation.scheduledTask.taskTypes.testCase')" value="TEST_CASE" />
      </el-select>
      <el-select v-model="filters.trigger_type" :placeholder="$t('uiAutomation.scheduledTask.triggerType')" clearable style="width: 160px;" @change="handleFilterChange">
        <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.cron')" value="CRON" />
        <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.interval')" value="INTERVAL" />
        <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.once')" value="ONCE" />
      </el-select>
      <el-select v-model="filters.status" :placeholder="$t('uiAutomation.scheduledTask.status')" clearable style="width: 160px;" @change="handleFilterChange">
        <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.active')" value="ACTIVE" />
        <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.paused')" value="PAUSED" />
        <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.completed')" value="COMPLETED" />
        <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.failed')" value="FAILED" />
      </el-select>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="handleCreateClick">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.scheduledTask.newTask') }}
      </el-button>
    </div>

    <!-- 任务列表 -->
    <div class="card-container">
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (pagination.current - 1) * pagination.size + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="$t('uiAutomation.scheduledTask.taskName')" min-width="180" header-align="center" align="center" show-overflow-tooltip />
        <el-table-column prop="task_type" :label="$t('uiAutomation.scheduledTask.taskType')" width="120" header-align="center" align="center">
          <template #default="scope">
            <span class="task-type-badge" :class="scope.row.task_type === 'TEST_SUITE' ? 'test-suite' : 'test-case'">
              {{ scope.row.task_type === 'TEST_SUITE' ? $t('uiAutomation.scheduledTask.taskTypes.testSuiteShort') : $t('uiAutomation.scheduledTask.taskTypes.testCaseShort') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="notification_type_display" :label="$t('uiAutomation.scheduledTask.notificationType')" min-width="140" header-align="center" align="center">
          <template #default="scope">
            <span v-if="scope.row.notification_type_display && scope.row.notification_type_display !== '-'"
                  class="notification-type-badge"
                  :class="getNotificationTypeClass(scope.row.notification_type_display)">
              {{ scope.row.notification_type_display }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" :label="$t('uiAutomation.scheduledTask.triggerType')" width="120" header-align="center" align="center">
          <template #default="scope">
            <span class="trigger-type-badge">
              {{ getTriggerTypeText(scope.row.trigger_type) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('uiAutomation.scheduledTask.status')" width="100" header-align="center" align="center">
          <template #default="scope">
            <span class="status-badge" :class="getStatusClass(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="next_run_time" :label="$t('uiAutomation.scheduledTask.nextRunTime')" width="180" header-align="center" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.next_run_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" :label="$t('uiAutomation.scheduledTask.lastRunTime')" width="180" header-align="center" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.last_run_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.common.operation')" width="310" fixed="right" header-align="center" align="center">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" class="action-btn run-btn" @click="runTaskNow(scope.row)" :loading="scope.row.running">
                <span>{{ $t('uiAutomation.scheduledTask.runNow') }}</span>
              </el-button>
              <el-button size="small" class="action-btn edit-btn" @click="editTask(scope.row)">
                <span>{{ $t('uiAutomation.scheduledTask.actions.edit') }}</span>
              </el-button>
              <el-button size="small" class="action-btn pause-btn" v-if="scope.row.status === 'ACTIVE'" @click="pauseTask(scope.row)">
                <span>{{ $t('uiAutomation.scheduledTask.actions.pause') }}</span>
              </el-button>
              <el-button size="small" class="action-btn resume-btn" v-if="scope.row.status === 'PAUSED'" @click="resumeTask(scope.row)">
                <span>{{ $t('uiAutomation.scheduledTask.actions.resume') }}</span>
              </el-button>
              <el-button size="small" class="action-btn delete-btn" @click="deleteTask(scope.row)">
                <span>{{ $t('uiAutomation.scheduledTask.actions.delete') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTask ? $t('uiAutomation.scheduledTask.editTask') : $t('uiAutomation.scheduledTask.createTask')"
      width="800px"
      :close-on-click-modal="false"
      @close="resetTaskForm"
      class="task-dialog"
    >
      <el-form :model="taskForm" label-width="120px">
        <el-form-item :label="$t('uiAutomation.scheduledTask.taskName')" required>
          <el-input v-model="taskForm.name" :placeholder="$t('uiAutomation.scheduledTask.taskNamePlaceholder')" />
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.taskDesc')">
          <el-input v-model="taskForm.description" type="textarea" :placeholder="$t('uiAutomation.scheduledTask.taskDescPlaceholder')" />
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.relatedProject')" required>
          <el-select v-model="taskForm.project" :placeholder="$t('uiAutomation.scheduledTask.selectProject')" @change="onProjectChange">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.taskType')" required>
          <el-radio-group v-model="taskForm.task_type" @change="onTaskTypeChange">
            <el-radio value="TEST_SUITE">{{ $t('uiAutomation.scheduledTask.taskTypes.testSuite') }}</el-radio>
            <el-radio value="TEST_CASE">{{ $t('uiAutomation.scheduledTask.taskTypes.testCase') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据任务类型显示不同配置 - 移到任务类型下面 -->
        <el-form-item v-if="taskForm.task_type === 'TEST_SUITE'" :label="$t('uiAutomation.scheduledTask.testSuite')" required>
          <el-select v-model="taskForm.test_suite" :placeholder="$t('uiAutomation.scheduledTask.selectSuite')">
            <el-option
              v-for="suite in testSuites"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="taskForm.task_type === 'TEST_CASE'" :label="$t('uiAutomation.scheduledTask.testCase')" required>
          <el-select
            v-model="taskForm.test_cases"
            multiple
            filterable
            :placeholder="$t('uiAutomation.scheduledTask.selectTestCase')"
          >
            <el-option
              v-for="testCase in testCases"
              :key="testCase.id"
              :label="testCase.name"
              :value="testCase.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.triggerType')" required>
          <el-radio-group v-model="taskForm.trigger_type">
            <el-radio value="CRON">{{ $t('uiAutomation.scheduledTask.triggerTypes.cron') }}</el-radio>
            <el-radio value="INTERVAL">{{ $t('uiAutomation.scheduledTask.triggerTypes.interval') }}</el-radio>
            <el-radio value="ONCE">{{ $t('uiAutomation.scheduledTask.triggerTypes.once') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据触发器类型显示不同配置 -->
        <el-form-item v-if="taskForm.trigger_type === 'CRON'" required>
          <template #label>
            <span style="white-space: nowrap;">{{ $t('uiAutomation.scheduledTask.cronExpression') }}</span>
            <el-tooltip raw-content placement="top">
              <template #content>
                <div style="line-height: 1.6; text-align: left;">
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.format') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.minute') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.hour') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.day') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.month') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.week') }}</div>
                  <div style="margin-top: 8px;">{{ $t('uiAutomation.scheduledTask.cronHelp.examples') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyDay') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyHour') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyMonday') }}</div>
                  <div>{{ $t('uiAutomation.scheduledTask.cronHelp.everyMonth') }}</div>
                </div>
              </template>
              <el-icon class="cron-help-icon"><Warning /></el-icon>
            </el-tooltip>
          </template>
          <el-input v-model="taskForm.cron_expression" :placeholder="$t('uiAutomation.scheduledTask.cronPlaceholder')" />
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'INTERVAL'" :label="$t('uiAutomation.scheduledTask.intervalTime')" required>
          <el-input-number v-model="taskForm.interval_seconds" :min="60" :step="60" />
          <span class="unit">{{ $t('uiAutomation.scheduledTask.intervalUnit') }}</span>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'ONCE'" :label="$t('uiAutomation.scheduledTask.executeTime')" required>
          <el-date-picker
            v-model="taskForm.execute_at"
            type="datetime"
            :placeholder="$t('uiAutomation.scheduledTask.selectExecuteTime')"
          />
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.executionEngine')" required>
          <el-radio-group v-model="taskForm.engine">
            <el-radio value="playwright">Playwright</el-radio>
            <el-radio value="selenium">Selenium</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.browserType')" required>
          <el-select v-model="taskForm.browser" :placeholder="$t('uiAutomation.scheduledTask.selectBrowser')">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Edge" value="edge" />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.runMode')">
          <el-checkbox v-model="taskForm.headless">{{ $t('uiAutomation.scheduledTask.headlessMode') }}</el-checkbox>
        </el-form-item>

        <el-form-item :label="$t('uiAutomation.scheduledTask.notificationSettings')">
          <el-checkbox v-model="taskForm.notify_on_success">{{ $t('uiAutomation.scheduledTask.notifyOnSuccess') }}</el-checkbox>
          <el-checkbox v-model="taskForm.notify_on_failure">{{ $t('uiAutomation.scheduledTask.notifyOnFailure') }}</el-checkbox>
        </el-form-item>

        <el-form-item v-if="taskForm.notify_on_success || taskForm.notify_on_failure" :label="$t('uiAutomation.scheduledTask.notificationType')">
          <el-select v-model="taskForm.notification_type" :placeholder="$t('uiAutomation.scheduledTask.selectNotificationType')">
            <el-option :label="$t('uiAutomation.scheduledTask.notificationTypes.email')" value="email" />
            <el-option :label="$t('uiAutomation.scheduledTask.notificationTypes.webhook')" value="webhook" />
            <el-option :label="$t('uiAutomation.scheduledTask.notificationTypes.both')" value="both" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="(taskForm.notify_on_success || taskForm.notify_on_failure) && (taskForm.notification_type === 'email' || taskForm.notification_type === 'both')" :label="$t('uiAutomation.scheduledTask.notifyEmails')">
          <el-select
            v-model="taskForm.notify_emails"
            multiple
            filterable
            :placeholder="$t('uiAutomation.scheduledTask.selectNotifyEmails')"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.display_name"
              :value="user.email"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="showCreateDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" class="save-btn" @click="submitTaskForm" :loading="submitting">
            {{ editingTask ? $t('uiAutomation.scheduledTask.saveTask') : $t('uiAutomation.scheduledTask.createTaskBtn') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown, Warning } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import {
  getScheduledTasks,
  createScheduledTask,
  updateScheduledTask,
  deleteScheduledTask,
  runScheduledTask,
  pauseScheduledTask,
  resumeScheduledTask,
  getUiProjects,
  getTestSuites,
  getTestCases,
  getUiUsers
} from '@/api/ui_automation.js'

const { t, locale } = useI18n()

// 数据状态
const tasks = ref([])
const projects = ref([])
const testSuites = ref([])
const testCases = ref([])
const users = ref([])
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingTask = ref(null)

// 筛选条件
const filters = reactive({
  task_type: '',
  trigger_type: '',
  status: ''
})

// 分页配置
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 表单数据
const taskForm = reactive({
  name: '',
  description: '',
  project: '',
  task_type: 'TEST_SUITE',
  trigger_type: 'CRON',
  cron_expression: '0 0 * * *',
  interval_seconds: 3600,
  execute_at: '',
  test_suite: '',
  test_cases: [],
  engine: 'playwright',
  browser: 'chrome',
  headless: false,
  notify_on_success: false,
  notify_on_failure: false,
  notification_type: '',
  notify_emails: []
})

// 获取触发器类型文本
const getTriggerTypeText = (type) => {
  const typeMap = {
    'CRON': t('uiAutomation.scheduledTask.triggerTypes.cronShort'),
    'INTERVAL': t('uiAutomation.scheduledTask.triggerTypes.intervalShort'),
    'ONCE': t('uiAutomation.scheduledTask.triggerTypes.onceShort')
  }
  return typeMap[type] || type
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'ACTIVE': t('uiAutomation.scheduledTask.statusTypes.active'),
    'PAUSED': t('uiAutomation.scheduledTask.statusTypes.paused'),
    'COMPLETED': t('uiAutomation.scheduledTask.statusTypes.completedShort'),
    'FAILED': t('uiAutomation.scheduledTask.statusTypes.failed')
  }
  return statusMap[status] || status
}

// 获取通知类型文本
const getNotificationTypeText = (type) => {
  const typeMap = {
    'email': t('uiAutomation.scheduledTask.notificationTypes.email'),
    'webhook': t('uiAutomation.scheduledTask.notificationTypes.webhook'),
    'both': t('uiAutomation.scheduledTask.notificationTypes.both')
  }
  return typeMap[type] || type
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadProjects()
  loadUsers()
})

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.size,
      ...filters
    }
    const response = await getScheduledTasks(params)
    tasks.value = response.data.results
    pagination.total = response.data.count
  } catch (error) {
    ElMessage.error(t('uiAutomation.scheduledTask.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

// 处理筛选变化
const handleFilterChange = () => {
  pagination.current = 1
  loadTasks()
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects()
    projects.value = response.data.results
  } catch (error) {
    console.error('Load projects failed:', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await getUiUsers()
    // 处理分页数据结构
    const usersData = response.data.results || response.data
    users.value = usersData.map(user => ({
      ...user,
      display_name: user.first_name ? `${user.first_name}（${user.email}）` : `${user.username}（${user.email}）`
    }))
  } catch (error) {
    console.error('Load users failed:', error)
  }
}

// 项目变化时加载对应的套件和用例
const onProjectChange = async (projectId) => {
  if (!projectId) return

  try {
    // 加载测试套件
    const suitesResponse = await getTestSuites({ project: projectId })
    testSuites.value = suitesResponse.data.results

    // 加载测试用例
    const casesResponse = await getTestCases({ project: projectId })
    testCases.value = casesResponse.data.results
  } catch (error) {
    console.error('Load project data failed:', error)
    ElMessage.error(t('uiAutomation.scheduledTask.messages.loadProjectDataFailed'))
  }
}

// 任务类型变化时清空已选数据
const onTaskTypeChange = () => {
  taskForm.test_suite = ''
  taskForm.test_cases = []
}

// 处理创建按钮点击
const handleCreateClick = () => {
  editingTask.value = null
  resetTaskForm()
  showCreateDialog.value = true
}

// 重置表单
const resetTaskForm = () => {
  Object.assign(taskForm, {
    name: '',
    description: '',
    project: '',
    task_type: 'TEST_SUITE',
    trigger_type: 'CRON',
    cron_expression: '0 0 * * *',
    interval_seconds: 3600,
    execute_at: '',
    test_suite: '',
    test_cases: [],
    engine: 'playwright',
    browser: 'chrome',
    headless: false,
    notify_on_success: false,
    notify_on_failure: false,
    notification_type: '',
    notify_emails: []
  })
  testSuites.value = []
  testCases.value = []
}

// 提交表单
const submitTaskForm = async () => {
  if (!taskForm.name || !taskForm.project) {
    ElMessage.warning(t('uiAutomation.scheduledTask.messages.requiredFields'))
    return
  }

  if (taskForm.task_type === 'TEST_SUITE' && !taskForm.test_suite) {
    ElMessage.warning(t('uiAutomation.scheduledTask.messages.selectTestSuite'))
    return
  }

  if (taskForm.task_type === 'TEST_CASE' && taskForm.test_cases.length === 0) {
    ElMessage.warning(t('uiAutomation.scheduledTask.messages.selectTestCases'))
    return
  }

  submitting.value = true
  try {
    // 构建提交数据
    const submitData = {
      name: taskForm.name,
      description: taskForm.description,
      project: taskForm.project,
      task_type: taskForm.task_type,
      trigger_type: taskForm.trigger_type,
      engine: taskForm.engine,
      browser: taskForm.browser,
      headless: taskForm.headless,
      notify_on_success: taskForm.notify_on_success,
      notify_on_failure: taskForm.notify_on_failure
    }

    // 添加通知相关字段
    if (taskForm.notify_on_success || taskForm.notify_on_failure) {
      if (taskForm.notification_type) {
        submitData.notification_type = taskForm.notification_type
      }
      if (taskForm.notify_emails && taskForm.notify_emails.length > 0) {
        submitData.notify_emails = taskForm.notify_emails
      }
    }

    // 根据触发器类型添加对应字段
    if (taskForm.trigger_type === 'CRON') {
      submitData.cron_expression = taskForm.cron_expression
    } else if (taskForm.trigger_type === 'INTERVAL') {
      submitData.interval_seconds = taskForm.interval_seconds
    } else if (taskForm.trigger_type === 'ONCE') {
      submitData.execute_at = taskForm.execute_at
    }

    // 根据任务类型添加对应字段
    if (taskForm.task_type === 'TEST_SUITE') {
      submitData.test_suite = taskForm.test_suite
    } else if (taskForm.task_type === 'TEST_CASE') {
      submitData.test_cases = taskForm.test_cases
    }

    if (editingTask.value) {
      await updateScheduledTask(editingTask.value.id, submitData)
      ElMessage.success(t('uiAutomation.scheduledTask.messages.updateSuccess'))
    } else {
      await createScheduledTask(submitData)
      ElMessage.success(t('uiAutomation.scheduledTask.messages.createSuccess'))
    }
    showCreateDialog.value = false
    loadTasks()
  } catch (error) {
    console.error('Task operation failed:', error)
    ElMessage.error(error.response?.data?.error ||
                   error.response?.data?.detail ||
                   (editingTask.value ? t('uiAutomation.scheduledTask.messages.updateFailed') : t('uiAutomation.scheduledTask.messages.createFailed')))
  } finally {
    submitting.value = false
  }
}

// 立即执行任务
const runTaskNow = async (task) => {
  try {
    task.running = true
    await runScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.runSuccess'))
    setTimeout(() => {
      loadTasks()
    }, 2000)
  } catch (error) {
    ElMessage.error(t('uiAutomation.scheduledTask.messages.runFailed'))
  } finally {
    task.running = false
  }
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const localeStr = locale.value === 'en' ? 'en-US' : 'zh-CN'
  return date.toLocaleString(localeStr, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 获取通知类型标签类型
const getNotificationTypeTagType = (typeDisplay) => {
  const typeMap = {
    '邮箱通知': '',
    'Email Notification': '',
    'Webhook机器人': 'primary',
    'Webhook Robot': 'primary',
    '两者都发送': 'warning',
    'Both': 'warning'
  }
  return typeMap[typeDisplay] || 'info'
}

// 获取通知类型样式类
const getNotificationTypeClass = (typeDisplay) => {
  const typeMap = {
    '邮箱通知': 'email',
    'Email Notification': 'email',
    'Webhook机器人': 'webhook',
    'Webhook Robot': 'webhook',
    '两者都发送': 'both',
    'Both': 'both'
  }
  return typeMap[typeDisplay] || ''
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classMap = {
    'ACTIVE': 'active',
    'PAUSED': 'paused',
    'COMPLETED': 'completed',
    'FAILED': 'failed'
  }
  return classMap[status] || 'default'
}

// 处理任务操作
const handleTaskAction = (command, task) => {
  switch (command) {
    case 'pause':
      pauseTask(task)
      break
    case 'resume':
      resumeTask(task)
      break
    case 'edit':
      editTask(task)
      break
    case 'delete':
      deleteTask(task)
      break
  }
}

// 编辑任务
const editTask = async (task) => {
  editingTask.value = task
  Object.assign(taskForm, {
    name: task.name,
    description: task.description,
    project: task.project,
    task_type: task.task_type,
    trigger_type: task.trigger_type,
    cron_expression: task.cron_expression,
    interval_seconds: task.interval_seconds,
    execute_at: task.execute_at,
    test_suite: task.test_suite || '',
    test_cases: task.test_cases || [],
    engine: task.engine || 'playwright',
    browser: task.browser || 'chrome',
    headless: task.headless || false,
    notify_on_success: task.notify_on_success || false,
    notify_on_failure: task.notify_on_failure || false,
    notification_type: task.notification_type || '',
    notify_emails: task.notify_emails || []
  })

  // 加载项目相关数据
  if (task.project) {
    await onProjectChange(task.project)
  }

  showCreateDialog.value = true
}

// 暂停任务
const pauseTask = async (task) => {
  try {
    await pauseScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.pauseSuccess'))
    loadTasks()
  } catch (error) {
    console.error('Pause task failed:', error)
    ElMessage.error(t('uiAutomation.scheduledTask.messages.pauseFailed'))
  }
}

// 恢复任务
const resumeTask = async (task) => {
  try {
    await resumeScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.resumeSuccess'))
    loadTasks()
  } catch (error) {
    ElMessage.error(t('uiAutomation.scheduledTask.messages.resumeFailed'))
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(t('uiAutomation.scheduledTask.messages.deleteConfirm'), t('uiAutomation.scheduledTask.messages.deleteConfirmTitle'), {
      confirmButtonText: t('uiAutomation.common.confirm'),
      cancelButtonText: t('uiAutomation.common.cancel'),
      type: 'warning'
    })
    await deleteScheduledTask(task.id)
    ElMessage.success(t('uiAutomation.scheduledTask.messages.deleteSuccess'))
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('uiAutomation.scheduledTask.messages.deleteFailed'))
    }
  }
}
</script>

<style lang="scss" scoped>
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

  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
    box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.25);
    border-radius: 8px;
    background: #ffffff;

    &:hover,
    &:focus {
      box-shadow: 0 0 0 1px #7b42f6;
    }
  }

  :deep(.el-input__inner) {
    color: #5a32a3;
    font-weight: 500;
  }

  .filter-bar-spacer {
    flex: 1;
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

    &.test-suite {
      background: #f6ffed;
      color: #52c41a;
    }

    &.test-case {
      background: #e6f7ff;
      color: #1890ff;
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
      background: #f5f5f5;
      color: #8c8c8c;
    }

    &.webhook {
      background: #e6f7ff;
      color: #1890ff;
    }

    &.both {
      background: #fff7e6;
      color: #fa8c16;
    }
  }

  // 触发器类型徽章样式
  .trigger-type-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    white-space: nowrap;
    background: #f5f5f5;
    color: #8c8c8c;
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

    &.active {
      background: #f6ffed;
      color: #52c41a;
    }

    &.paused {
      background: #fff7e6;
      color: #fa8c16;
    }

    &.completed {
      background: #e6f7ff;
      color: #1890ff;
    }

    &.failed {
      background: #fff1f0;
      color: #ff4d4f;
    }

    &.default {
      background: #f5f5f5;
      color: #8c8c8c;
    }
  }

  // 引擎类型徽章样式
  .engine-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    white-space: nowrap;

    &.playwright {
      background: #f0f9ff;
      color: #52c41a;
    }

    &.selenium {
      background: #e6f7ff;
      color: #1890ff;
    }
  }

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

  &.run-btn {
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
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
    }
  }

  &.pause-btn {
    background: linear-gradient(135deg, #faad14 0%, #d48806 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #ffc53d 0%, #faad14 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(250, 173, 20, 0.4);
    }
  }

  &.resume-btn {
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

// Cron帮助图标样式
:deep(.cron-help-icon) {
  margin-left: 6px;
  font-size: 20px;
  color: #7b42f6;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  transition: all 0.3s ease;
  vertical-align: baseline;

  &:hover {
    background: rgba(123, 66, 246, 0.1);
    transform: scale(1.1);
  }
}
</style>