<template>
  <div class="page-container">
    <div class="page-header-card">
      <div class="page-header-content">
        <h1>{{ $t('uiAutomation.scheduledTask.title') }}</h1>
      </div>
      <el-button type="primary" class="create-btn" @click="handleCreateClick">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.scheduledTask.newTask') }}
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar card-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.task_type" :placeholder="$t('uiAutomation.scheduledTask.taskType')" clearable>
            <el-option :label="$t('uiAutomation.scheduledTask.taskTypes.testSuite')" value="TEST_SUITE" />
            <el-option :label="$t('uiAutomation.scheduledTask.taskTypes.testCase')" value="TEST_CASE" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.trigger_type" :placeholder="$t('uiAutomation.scheduledTask.triggerType')" clearable>
            <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.cron')" value="CRON" />
            <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.interval')" value="INTERVAL" />
            <el-option :label="$t('uiAutomation.scheduledTask.triggerTypes.once')" value="ONCE" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.status" :placeholder="$t('uiAutomation.scheduledTask.status')" clearable>
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.active')" value="ACTIVE" />
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.paused')" value="PAUSED" />
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.completed')" value="COMPLETED" />
            <el-option :label="$t('uiAutomation.scheduledTask.statusTypes.failed')" value="FAILED" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button class="reset-btn" @click="resetFilters">{{ $t('uiAutomation.common.reset') }}</el-button>
          <el-button type="primary" class="query-btn" @click="loadTasks">{{ $t('uiAutomation.common.search') }}</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表 -->
    <div class="card-container">
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="name" :label="$t('uiAutomation.scheduledTask.taskName')" min-width="160" header-align="center" align="center" />
        <el-table-column prop="task_type" :label="$t('uiAutomation.scheduledTask.taskType')" width="100" header-align="center" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.task_type === 'TEST_SUITE' ? 'success' : 'primary'">
              {{ scope.row.task_type === 'TEST_SUITE' ? $t('uiAutomation.scheduledTask.taskTypes.testSuiteShort') : $t('uiAutomation.scheduledTask.taskTypes.testCaseShort') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notification_type_display" :label="$t('uiAutomation.scheduledTask.notificationType')" width="110" header-align="center" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.notification_type_display && scope.row.notification_type_display !== '-'"
                    :type="getNotificationTypeTagType(scope.row.notification_type_display)"
                    size="small">
              {{ getNotificationTypeText(scope.row.notification_type) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" :label="$t('uiAutomation.scheduledTask.triggerType')" width="100" header-align="center" align="center">
          <template #default="scope">
            <el-tag>
              {{ getTriggerTypeText(scope.row.trigger_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('uiAutomation.scheduledTask.status')" width="90" header-align="center" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'ACTIVE' ? 'success' : scope.row.status === 'PAUSED' ? 'warning' : 'info'">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="engine" :label="$t('uiAutomation.scheduledTask.executionEngine')" width="110" header-align="center" align="center">
          <template #default="scope">
            <el-tag size="small" type="info">
              {{ scope.row.engine === 'playwright' ? 'Playwright' : 'Selenium' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="browser" :label="$t('uiAutomation.scheduledTask.browser')" width="90" header-align="center" align="center">
          <template #default="scope">
            {{ scope.row.browser || 'chrome' }}
          </template>
        </el-table-column>
        <el-table-column prop="next_run_time" :label="$t('uiAutomation.scheduledTask.nextRunTime')" width="170" header-align="center" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.next_run_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" :label="$t('uiAutomation.scheduledTask.lastRunTime')" width="170" header-align="center" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.last_run_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.common.operation')" width="180" fixed="right" header-align="center" align="center">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" class="action-btn run-btn" @click="runTaskNow(scope.row)" :loading="scope.row.running">
                <span>{{ $t('uiAutomation.scheduledTask.runNow') }}</span>
              </el-button>
              <el-dropdown @command="(command) => handleTaskAction(command, scope.row)">
                <el-button size="small" class="action-btn more-btn">
                  <span>{{ $t('uiAutomation.scheduledTask.more') }}</span><el-icon><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">{{ $t('uiAutomation.scheduledTask.actions.edit') }}</el-dropdown-item>
                    <el-dropdown-item command="pause" v-if="scope.row.status === 'ACTIVE'">{{ $t('uiAutomation.scheduledTask.actions.pause') }}</el-dropdown-item>
                    <el-dropdown-item command="resume" v-if="scope.row.status === 'PAUSED'">{{ $t('uiAutomation.scheduledTask.actions.resume') }}</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>{{ $t('uiAutomation.scheduledTask.actions.delete') }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
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
        <el-form-item v-if="taskForm.trigger_type === 'CRON'" :label="$t('uiAutomation.scheduledTask.cronExpression')" required>
          <el-input v-model="taskForm.cron_expression" :placeholder="$t('uiAutomation.scheduledTask.cronPlaceholder')" />
          <div class="cron-help">
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
              <span style="cursor: pointer; color: #409EFF;">{{ $t('uiAutomation.scheduledTask.cronHelpLink') }}</span>
            </el-tooltip>
          </div>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
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
  }
}

// 任务类型变化
const onTaskTypeChange = () => {
  taskForm.test_suite = ''
  taskForm.test_cases = []
}

// 新建按钮点击
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
}

// 重置筛选
const resetFilters = () => {
  Object.assign(filters, {
    task_type: '',
    trigger_type: '',
    status: ''
  })
  loadTasks()
}

// 提交任务表单
const submitTaskForm = async () => {
  submitting.value = true
  try {
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

<style scoped lang="scss">
:root {
  --primary-color: #7b42f6;
  --primary-dark: #5a32a3;
  --primary-light: #f8f7ff;
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

.page-container {
  margin: -20px;
  min-height: calc(100% + 40px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
  width: calc(100% + 40px);
  box-sizing: border-box;
  padding: 24px;
}

.page-header-card {
  padding: 24px 28px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;

  .page-header-content {
    display: flex;
    align-items: center;

    h1 {
      font-size: 20px;
      font-weight: 600;
      color: #262626;
      margin: 0;
    }
  }
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

.filter-bar {
  padding: 20px 24px;

  :deep(.el-select) {
    width: 100%;
  }
}

.reset-btn {
  padding: 10px 24px !important;
  border-radius: 8px !important;
  font-weight: 500 !important;

  &:hover {
    color: #7b42f6;
    border-color: #7b42f6;
    background: #f8f7ff;
  }
}

.query-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 10px 24px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;
  transition: all 0.3s ease !important;

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4) !important;
  }
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: 16px;

  .el-table {
    border: none;
    border-radius: 8px 8px 0 0;
    overflow: hidden;
    min-height: 200px;
    box-shadow: none;
    transition: all 0.3s ease;
    background-color: transparent !important;

    --el-color-primary: #7b42f6;
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

    :deep(.el-table__header-wrapper) {
      background-color: #ffffff !important;

      :deep(.el-table__header) {
        background-color: #ffffff !important;

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

          :deep(.cell) {
            background-color: #ffffff !important;
            color: #5a32a3 !important;
            font-weight: 600 !important;
          }
        }
      }
    }

    :deep(.el-table__body-wrapper) {
      :deep(.el-table__body) {
        :deep(tr) {
          transition: all 0.3s ease;

          &:hover {
            background-color: #f8f7ff !important;
          }

          &.el-table__row--striped {
            background-color: #fafaff !important;
          }
        }

        :deep(td) {
          border-bottom: 1px solid #e9ecef;
          padding: 16px;
          color: #333;
          text-align: center;
          transition: all 0.3s ease;
        }
      }
    }
  }
}

.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px !important;
  min-width: 32px;

  .el-icon {
    font-size: 14px;
  }

  &.run-btn {
    background: #52c41a;
    border-color: #52c41a;
    color: white !important;

    &:hover {
      background: #73d13d !important;
      border-color: #73d13d !important;
    }

    span {
      font-size: 12px;
    }
  }

  &.more-btn {
    background: #7c3aed;
    border-color: #7c3aed;
    color: white !important;

    &:hover {
      background: #8b5cf6 !important;
      border-color: #8b5cf6 !important;
    }

    span {
      font-size: 12px;
    }

    .el-icon {
      margin-left: 3px;
      font-size: 12px;
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 24px;
  background: transparent;
  border-top: 1px solid rgba(147, 112, 219, 0.1);

  :deep(.el-pagination) {
    --el-color-primary: #7b42f6;

    .el-pagination__total {
      color: #5a32a3;
      font-weight: 500;
    }

    .btn-prev,
    .btn-next {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff;
      color: #5a32a3;

      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border-color: transparent;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .el-pager li {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff;
      color: #5a32a3;
      font-weight: 500;

      &.is-active {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border-color: transparent;
        color: white;
      }
    }

    .el-pagination__jump {
      color: #5a32a3;
      font-weight: 500;
    }
  }
}

// 对话框样式
:deep(.task-dialog) {
  .el-dialog__header {
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid #f0f0f0;

    .el-dialog__title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-form-item__label {
    font-weight: 500;
    color: #333;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 24px 0;

    .cancel-btn {
      padding: 10px 24px;
      border-radius: 8px;
      font-weight: 500;

      &:hover {
        color: #7b42f6;
        border-color: #7b42f6;
        background: #f8f7ff;
      }
    }

    .save-btn {
      padding: 10px 24px;
      border-radius: 8px;
      font-weight: 500;
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
        box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
      }
    }
  }
}

.cron-help {
  margin-top: 8px;
  font-size: 12px;
}

.unit {
  margin-left: 8px;
  color: #606266;
}
</style>
