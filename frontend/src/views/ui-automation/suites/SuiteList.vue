<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select v-model="projectId" :placeholder="$t('uiAutomation.common.selectProject')" class="project-select" @change="onProjectChange">
        <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
      </el-select>
      <el-input
        v-model="searchText"
        placeholder="搜索套件名称"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="handleNewSuite">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.suite.newSuite') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="suites" v-loading="loading" stripe style="width: 100%" class="suite-table">
        <el-table-column type="index" label="序号" width="60" header-align="center" align="center">
          <template #default="{ $index }">
            {{ $index + 1 + (pagination.currentPage - 1) * pagination.pageSize }}
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="$t('uiAutomation.suite.suiteName')" min-width="200" header-align="center" align="center">
          <template #default="{ row }">
            <span class="suite-name-cell" @click="editSuite(row.id)">
              {{ row.name }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="包含数量" width="150" header-align="center" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ (row.test_case_count || 0) + (row.script_count || 0) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.suite.executionStatus')" width="110" header-align="center" align="center">
          <template #default="{ row }">
            <span :class="['status-badge', getExecutionStatusClass(row.execution_status)]">
              {{ getExecutionStatusText(row.execution_status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.suite.passedCount')" width="90" header-align="center" align="center">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: bold;">{{ row.passed_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.suite.failedCount')" width="90" header-align="center" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ row.failed_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="$t('uiAutomation.common.createTime')" width="180" :formatter="formatDate" header-align="center" align="center" />
        <el-table-column prop="updated_at" :label="$t('uiAutomation.common.updateTime')" width="180" :formatter="formatDate" header-align="center" align="center" />
        <el-table-column :label="$t('uiAutomation.common.operation')" width="260" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" class="action-btn edit-btn" @click="editSuite(row.id)">
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
              </el-button>
              <el-button size="small" type="success" class="action-btn run-btn" @click="runSuite(row)">
                <el-icon><RefreshRight /></el-icon>
                <span>执行</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteSuite(row.id)">
                <el-icon><Delete /></el-icon>
                <span>删除</span>
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

    <!-- 创建/编辑套件对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? $t('uiAutomation.suite.editSuite') : $t('uiAutomation.suite.createSuite')"
      width="85%"
      :close-on-click-modal="false"
      class="suite-edit-dialog"
      :max-width="1200"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.suite.suiteName')" prop="name">
          <el-input v-model="createForm.name" :placeholder="$t('uiAutomation.suite.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="createForm.description" type="textarea" :placeholder="$t('uiAutomation.common.description')" />
        </el-form-item>
        <!-- 脚本选择 -->
        <el-form-item label="测试脚本">
          <div class="test-case-selector">
            <div class="selector-panel">
              <div class="panel-header">
                <h4>可用脚本</h4>
                <el-input
                  v-model="scriptSearchText"
                  placeholder="搜索脚本"
                  size="small"
                  clearable
                  style="width: 200px;"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="panel-content">
                <el-table
                  :data="filteredAvailableScripts"
                  height="200"
                  @row-click="handleScriptRowClick"
                  :row-class-name="getScriptRowClassName"
                >
                  <el-table-column prop="name" label="脚本名称" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="language" label="语言" width="70">
                    <template #default="{ row }">
                      <el-tag size="small" :type="row.language === 'python' ? 'success' : 'primary'">
                        {{ row.language }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="framework" label="框架" width="80">
                    <template #default="{ row }">
                      <el-tag size="small" type="info">
                        {{ row.framework }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="60" align="center">
                    <template #default="{ row }">
                      <el-button size="small" text @click.stop="addScript(row)">
                        <el-icon><ArrowRight /></el-icon>
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>

            <div class="selector-panel">
              <div class="panel-header">
                <h4>已选脚本 ({{ selectedScripts.length }})</h4>
              </div>
              <div class="panel-content">
                <el-table
                  :data="selectedScripts"
                  height="200"
                >
                  <el-table-column prop="name" label="脚本名称" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="language" label="语言" width="70">
                    <template #default="{ row }">
                      <el-tag size="small" :type="row.language === 'python' ? 'success' : 'primary'">
                        {{ row.language }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="90" align="center">
                    <template #default="{ row, $index }">
                      <el-button
                        size="small"
                        text
                        @click="moveScriptUp($index)"
                        :disabled="$index === 0"
                        title="上移"
                      >
                        <el-icon><Top /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        @click="moveScriptDown($index)"
                        :disabled="$index === selectedScripts.length - 1"
                        title="下移"
                      >
                        <el-icon><Bottom /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        type="danger"
                        @click="removeScript($index)"
                        title="删除"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </el-form-item>

        <!-- 测试用例选择 -->
        <el-form-item :label="$t('uiAutomation.suite.testCases')">
          <div class="test-case-selector">
            <div class="selector-panel">
              <div class="panel-header">
                <h4>{{ $t('uiAutomation.suite.availableCases') }}</h4>
                <el-input
                  v-model="testCaseSearchText"
                  :placeholder="$t('uiAutomation.suite.searchCases')"
                  size="small"
                  clearable
                  style="width: 200px;"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="panel-content">
                <el-table
                  :data="filteredAvailableTestCases"
                  height="200"
                  @row-click="handleTestCaseRowClick"
                  :row-class-name="getTestCaseRowClassName"
                >
                  <el-table-column prop="name" :label="$t('uiAutomation.suite.caseName')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="priority" :label="$t('uiAutomation.suite.priority')" width="70">
                    <template #default="{ row }">
                      <el-tag size="small" :type="getPriorityTag(row.priority)">
                        {{ getPriorityText(row.priority) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" :label="$t('uiAutomation.common.status')" width="70">
                    <template #default="{ row }">
                      <el-tag size="small" :type="getCaseStatusTag(row.status)">
                        {{ getCaseStatusText(row.status) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column :label="$t('uiAutomation.common.operation')" width="60" align="center">
                    <template #default="{ row }">
                      <el-button size="small" text @click.stop="addTestCase(row)">
                        <el-icon><ArrowRight /></el-icon>
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>

            <div class="selector-panel">
              <div class="panel-header">
                <h4>{{ $t('uiAutomation.suite.selectedCases') }} ({{ selectedTestCases.length }})</h4>
              </div>
              <div class="panel-content">
                <el-table
                  :data="selectedTestCases"
                  height="200"
                >
                  <el-table-column prop="name" :label="$t('uiAutomation.suite.caseName')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="priority" :label="$t('uiAutomation.suite.priority')" width="70">
                    <template #default="{ row }">
                      <el-tag size="small" :type="getPriorityTag(row.priority)">
                        {{ getPriorityText(row.priority) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column :label="$t('uiAutomation.common.operation')" width="90" align="center">
                    <template #default="{ row, $index }">
                      <el-button
                        size="small"
                        text
                        @click="moveUp($index)"
                        :disabled="$index === 0"
                        :title="$t('uiAutomation.common.moveUp')"
                      >
                        <el-icon><Top /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        @click="moveDown($index)"
                        :disabled="$index === selectedTestCases.length - 1"
                        :title="$t('uiAutomation.common.moveDown')"
                      >
                        <el-icon><Bottom /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        type="danger"
                        @click="removeTestCase($index)"
                        :title="$t('uiAutomation.common.delete')"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelCreate">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleCreate" :loading="saving">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 运行配置对话框 -->
    <el-dialog v-model="showRunDialog" :title="$t('uiAutomation.suite.runConfig')" width="600px">
      <el-form :model="runConfig" label-width="120px">
        <el-form-item :label="$t('uiAutomation.suite.testEngine')">
          <el-select v-model="runConfig.engine" :placeholder="$t('uiAutomation.suite.testEngine')">
            <el-option label="Playwright" value="playwright" />
            <el-option label="Selenium" value="selenium" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.suite.browser')">
          <el-select v-model="runConfig.browser" :placeholder="$t('uiAutomation.suite.browser')">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Safari" value="safari" />
            <el-option label="Edge" value="edge" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.suite.executionMode')">
          <el-radio-group v-model="runConfig.headless">
            <el-radio :label="false">{{ $t('uiAutomation.suite.headedMode') }}</el-radio>
            <el-radio :label="true">{{ $t('uiAutomation.suite.headlessMode') }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRunDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button
            type="primary"
            @click="confirmRunSuite"
            :loading="running"
          >
            {{ $t('uiAutomation.suite.startExecution') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Edit, Delete, RefreshRight, Collection,
  ArrowRight, Top, Bottom
} from '@element-plus/icons-vue'
import {
  getUiProjects,
  getTestSuites,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  getTestCases,
  getTestSuiteTestCases,
  addTestCaseToTestSuite,
  removeTestCaseFromTestSuite,
  updateTestCaseOrder,
  runTestSuite,
  getTestScripts,
  getTestSuiteScripts
} from '@/api/ui_automation'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 响应式数据
const projects = ref([])
const projectId = ref('')
const suites = ref([])
const loading = ref(false)
const searchText = ref('')
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

// 对话框控制
const showCreateDialog = ref(false)
const showRunDialog = ref(false)
const isEditing = ref(false)
const currentSuiteId = ref(null)
const saving = ref(false)
const running = ref(false)

// 表单数据
const createForm = reactive({
  name: '',
  description: ''
})

// 表单验证规则 - 使用 computed 实现动态国际化
const formRules = computed(() => ({
  name: [{ required: true, message: t('uiAutomation.suite.rules.nameRequired'), trigger: 'blur' }]
}))

// 测试用例相关
const availableTestCases = ref([])
const selectedTestCases = ref([])
const testCaseSearchText = ref('')

// 脚本相关
const availableScripts = ref([])
const selectedScripts = ref([])
const scriptSearchText = ref('')

// 运行配置
const runConfig = reactive({
  engine: 'playwright',
  browser: 'chrome',
  headless: false
})
const currentRunningSuite = ref(null)

// 计算属性 - 过滤后的可用测试用例
const filteredAvailableTestCases = computed(() => {
  if (!testCaseSearchText.value) {
    return availableTestCases.value
  }
  return availableTestCases.value.filter(tc =>
    tc.name.toLowerCase().includes(testCaseSearchText.value.toLowerCase()) ||
    (tc.description && tc.description.toLowerCase().includes(testCaseSearchText.value.toLowerCase()))
  )
})

// 计算属性 - 过滤后的可用脚本
const filteredAvailableScripts = computed(() => {
  if (!scriptSearchText.value) {
    return availableScripts.value
  }
  return availableScripts.value.filter(script =>
    script.name.toLowerCase().includes(scriptSearchText.value.toLowerCase())
  )
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error(t('uiAutomation.project.messages.loadFailed'))
  }
}

// 加载测试套件列表
const loadSuites = async () => {
  if (!projectId.value) {
    suites.value = []
    total.value = 0
    return
  }

  loading.value = true
  try {
    const response = await getTestSuites({
      project: projectId.value,
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      search: searchText.value
    })

    if (response.data.results) {
      suites.value = response.data.results
      total.value = response.data.count || 0
    } else {
      suites.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    console.error('获取测试套件列表失败:', error)
    ElMessage.error(t('uiAutomation.suite.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

// 加载可用测试用例
const loadAvailableTestCases = async () => {
  if (!projectId.value) return

  try {
    const response = await getTestCases({
      project: projectId.value,
      page_size: 1000  // 加载所有用例
    })
    availableTestCases.value = response.data.results || response.data
  } catch (error) {
    console.error('获取测试用例列表失败:', error)
    ElMessage.error(t('uiAutomation.suite.messages.loadCasesFailed'))
  }
}

// 加载可用脚本
const loadAvailableScripts = async () => {
  if (!projectId.value) return

  try {
    const response = await getTestScripts({
      project: projectId.value,
      page_size: 1000  // 加载所有脚本
    })
    availableScripts.value = response.data.results || response.data
  } catch (error) {
    console.error('获取脚本列表失败:', error)
    ElMessage.error('获取脚本列表失败')
  }
}

// 项目切换
const onProjectChange = async () => {
  pagination.currentPage = 1
  await loadSuites()
}

// 搜索处理
const handleSearch = async () => {
  pagination.currentPage = 1
  await loadSuites()
}

// 分页处理
const handleSizeChange = async () => {
  pagination.currentPage = 1
  await loadSuites()
}

const handleCurrentChange = async () => {
  await loadSuites()
}

// 新增套件
const handleCreate = async () => {
  if (!createForm.name) {
    ElMessage.warning(t('uiAutomation.suite.messages.inputName'))
    return
  }

  if (!projectId.value) {
    ElMessage.warning(t('uiAutomation.suite.messages.selectProject'))
    return
  }

  saving.value = true
  try {
    // 准备脚本数据
    const scriptsData = selectedScripts.value.map((script, index) => ({
      id: script.id,
      order: index
    }))

    // 准备测试用例数据
    const testCasesData = selectedTestCases.value.map((testCase, index) => ({
      id: testCase.id,
      order: index
    }))

    const suiteData = {
      project: projectId.value,
      name: createForm.name,
      description: createForm.description,
      scripts: scriptsData,
      test_cases: testCasesData
    }

    if (isEditing.value) {
      // 更新套件
      await updateTestSuite(currentSuiteId.value, suiteData)
      ElMessage.success(t('uiAutomation.suite.messages.updateSuccess'))
    } else {
      // 创建套件
      await createTestSuite(suiteData)
      ElMessage.success(t('uiAutomation.suite.messages.createSuccess'))
    }

    showCreateDialog.value = false
    await loadSuites()
    resetForm()
  } catch (error) {
    console.error('保存测试套件失败:', error)
    ElMessage.error(t('uiAutomation.suite.messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

// 编辑套件
const editSuite = async (id) => {
  try {
    // 加载套件详情
    const suites_data = suites.value.find(s => s.id === id)
    if (!suites_data) return

    currentSuiteId.value = id
    isEditing.value = true
    createForm.name = suites_data.name
    createForm.description = suites_data.description

    // 并行加载可用脚本和用例
    await Promise.all([
      loadAvailableTestCases(),
      loadAvailableScripts()
    ])

    // 加载已选测试用例
    const testCasesResponse = await getTestSuiteTestCases(id)
    selectedTestCases.value = testCasesResponse.data.map(item => item.test_case).sort((a, b) => a.order - b.order)

    // 加载已选脚本
    const scriptsResponse = await getTestSuiteScripts(id)
    selectedScripts.value = scriptsResponse.data.map(item => item.test_script).sort((a, b) => a.order - b.order)

    showCreateDialog.value = true
  } catch (error) {
    console.error('加载套件详情失败:', error)
    ElMessage.error(t('uiAutomation.suite.messages.loadDetailFailed'))
  }
}

// 删除套件
const deleteSuite = async (id) => {
  try {
    await ElMessageBox.confirm(t('uiAutomation.suite.messages.deleteConfirm'), t('uiAutomation.messages.confirm.tip'), {
      confirmButtonText: t('uiAutomation.common.confirm'),
      cancelButtonText: t('uiAutomation.common.cancel'),
      type: 'warning'
    })

    await deleteTestSuite(id)
    ElMessage.success(t('uiAutomation.suite.messages.deleteSuccess'))
    await loadSuites()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试套件失败:', error)
      ElMessage.error(t('uiAutomation.suite.messages.deleteFailed'))
    }
  }
}

// 运行套件
const runSuite = (suite) => {
  // 检查是否包含测试用例或脚本
  const totalCount = (suite.test_case_count || 0) + (suite.script_count || 0)
  if (totalCount === 0) {
    ElMessage.warning('该测试套件未包含任何测试用例或脚本，无法执行')
    return
  }

  currentRunningSuite.value = suite
  showRunDialog.value = true
}

// 确认运行套件
const confirmRunSuite = async () => {
  running.value = true
  try {
    const requestData = {
      use_ai: false,
      engine: runConfig.engine,
      browser: runConfig.browser,
      headless: runConfig.headless
    }

    const response = await runTestSuite(currentRunningSuite.value.id, requestData)

    ElMessage.success(t('uiAutomation.suite.messages.startSuccess'))
    showRunDialog.value = false

    // 立即刷新一次以显示"运行中"状态
    await loadSuites()

    // 开始轮询检查执行状态
    pollSuiteStatus(currentRunningSuite.value.id)
  } catch (error) {
    console.error('执行测试套件失败:', error)
    // 如果后端返回了错误消息，显示具体错误
    const errorMsg = error.response?.data?.error || t('uiAutomation.suite.messages.executeFailed')
    ElMessage.error(errorMsg)
  } finally {
    running.value = false
  }
}

// 轮询检查套件执行状态
const pollSuiteStatus = (suiteId) => {
  let pollCount = 0
  const maxPolls = 120 // 最多轮询2分钟（每秒一次）

  const pollInterval = setInterval(async () => {
    pollCount++

    try {
      // 重新加载套件列表
      await loadSuites()

      // 查找当前套件的状态
      const currentSuite = suites.value.find(s => s.id === suiteId)

      if (currentSuite && currentSuite.execution_status !== 'running') {
        // 执行完成，停止轮询
        clearInterval(pollInterval)

        // 根据状态显示消息
        if (currentSuite.execution_status === 'passed') {
          ElMessage.success(`${t('uiAutomation.suite.messages.executionComplete')}: ${t('uiAutomation.suite.messages.allPassed')} (${currentSuite.passed_count}/${currentSuite.passed_count + currentSuite.failed_count})`)
        } else if (currentSuite.execution_status === 'failed') {
          ElMessage.warning(`${t('uiAutomation.suite.messages.executionComplete')}: ${t('uiAutomation.suite.messages.partialFailed')} (${t('uiAutomation.suite.messages.passed')}: ${currentSuite.passed_count}, ${t('uiAutomation.status.failed')}: ${currentSuite.failed_count})`)
        }
      }

      // 超过最大轮询次数，停止轮询
      if (pollCount >= maxPolls) {
        clearInterval(pollInterval)
        ElMessage.info(t('uiAutomation.suite.messages.longExecution'))
      }
    } catch (error) {
      console.error('轮询套件状态失败:', error)
      // 发生错误时停止轮询
      clearInterval(pollInterval)
    }
  }, 3000) // 每3秒轮询一次
}

// 测试用例管理方法
const handleTestCaseRowClick = (row) => {
  // 双击添加测试用例
  addTestCase(row)
}

const getTestCaseRowClassName = ({ row }) => {
  // 如果已选中，添加特殊样式
  return selectedTestCases.value.some(tc => tc.id === row.id) ? 'selected-row' : ''
}

const addTestCase = (testCase) => {
  // 检查是否已存在
  if (selectedTestCases.value.some(tc => tc.id === testCase.id)) {
    ElMessage.warning(t('uiAutomation.suite.messages.caseAdded'))
    return
  }
  selectedTestCases.value.push({ ...testCase })
}

const removeTestCase = (index) => {
  selectedTestCases.value.splice(index, 1)
}

const moveUp = (index) => {
  if (index > 0) {
    const temp = selectedTestCases.value[index]
    selectedTestCases.value[index] = selectedTestCases.value[index - 1]
    selectedTestCases.value[index - 1] = temp
  }
}

const moveDown = (index) => {
  if (index < selectedTestCases.value.length - 1) {
    const temp = selectedTestCases.value[index]
    selectedTestCases.value[index] = selectedTestCases.value[index + 1]
    selectedTestCases.value[index + 1] = temp
  }
}

// 脚本管理方法
const handleScriptRowClick = (row) => {
  // 双击添加脚本
  addScript(row)
}

const getScriptRowClassName = ({ row }) => {
  // 如果已选中，添加特殊样式
  return selectedScripts.value.some(s => s.id === row.id) ? 'selected-row' : ''
}

const addScript = (script) => {
  // 检查是否已存在
  if (selectedScripts.value.some(s => s.id === script.id)) {
    ElMessage.warning('脚本已添加')
    return
  }
  selectedScripts.value.push({ ...script })
}

const removeScript = (index) => {
  selectedScripts.value.splice(index, 1)
}

const moveScriptUp = (index) => {
  if (index > 0) {
    const temp = selectedScripts.value[index]
    selectedScripts.value[index] = selectedScripts.value[index - 1]
    selectedScripts.value[index - 1] = temp
  }
}

const moveScriptDown = (index) => {
  if (index < selectedScripts.value.length - 1) {
    const temp = selectedScripts.value[index]
    selectedScripts.value[index] = selectedScripts.value[index + 1]
    selectedScripts.value[index + 1] = temp
  }
}

// 重置表单
const resetForm = () => {
  createForm.name = ''
  createForm.description = ''
  selectedTestCases.value = []
  selectedScripts.value = []
  testCaseSearchText.value = ''
  scriptSearchText.value = ''
  isEditing.value = false
  currentSuiteId.value = null
}

// 取消创建
const cancelCreate = () => {
  showCreateDialog.value = false
  resetForm()
}

// 新增套件按钮点击
const handleCreateButtonClick = async () => {
  resetForm()
  await Promise.all([
    loadAvailableTestCases(),
    loadAvailableScripts()
  ])
  showCreateDialog.value = true
}

// 辅助方法
const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  return new Date(cellValue).toLocaleString()
}

const getExecutionStatusClass = (status) => {
  const statusMap = {
    'not_run': 'status-not-run',
    'passed': 'status-passed',
    'failed': 'status-failed',
    'running': 'status-running'
  }
  return statusMap[status] || 'status-not-run'
}

const getExecutionStatusText = (status) => {
  const statusKey = {
    'not_run': 'notRun',
    'passed': 'passed',
    'failed': 'failed',
    'running': 'running'
  }[status]
  return statusKey ? t(`uiAutomation.status.${statusKey}`) : t('uiAutomation.status.unknown')
}

const getPriorityTag = (priority) => {
  const priorityMap = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return priorityMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const priorityKey = {
    'high': 'high',
    'medium': 'medium',
    'low': 'low'
  }[priority]
  return priorityKey ? t(`uiAutomation.priority.${priorityKey}`) : t('uiAutomation.status.unknown')
}

const getCaseStatusTag = (status) => {
  const statusMap = {
    'draft': 'info',
    'ready': 'primary',
    'running': 'warning',
    'passed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getCaseStatusText = (status) => {
  const statusKey = {
    'draft': 'draft',
    'ready': 'ready',
    'running': 'running',
    'passed': 'passed',
    'failed': 'failed'
  }[status]
  return statusKey ? t(`uiAutomation.status.${statusKey}`) : t('uiAutomation.status.unknown')
}

// 监听新增套件按钮
const originalShowCreateDialog = showCreateDialog
onMounted(async () => {
  await loadProjects()
  if (projects.value.length > 0) {
    projectId.value = projects.value[0].id
    await loadSuites()
  }
})

// 监听对话框打开事件
const openCreateDialog = async () => {
  if (!isEditing.value) {
    await loadAvailableTestCases()
  }
}

// 修改新增套件按钮点击事件
const handleNewSuite = async () => {
  resetForm()
  await Promise.all([
    loadAvailableTestCases(),
    loadAvailableScripts()
  ])
  showCreateDialog.value = true
}
</script>

<style scoped lang="scss">
.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
}



.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);

  .filter-bar-spacer {
    flex: 1;
  }

  .project-select {
    width: 220px;

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

  .reset-btn {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: #ffffff;
    border: 1px solid rgba(147, 112, 219, 0.4);
    color: #5a32a3;

    &:hover {
      background: #f8f7ff;
      border-color: #7b42f6;
      color: #7b42f6;
    }
  }

  .query-btn {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
    }

    .el-icon {
      margin-right: 6px;
    }
  }

  .create-btn {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
    }

    .el-icon {
      margin-right: 6px;
    }
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
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);

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

    // 行悬停效果
    :deep(.el-table__row:hover) {
      background-color: #f8f7ff !important;
    }

    // 套件名称样式
    .suite-name-cell {
      padding: 4px 8px;
      line-height: 1.6;
      color: #595959;
      cursor: pointer;
      transition: color 0.3s ease;

      &:hover {
        color: #7b42f6;
      }
    }

    // 步骤计数样式
    .step-count {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 16px;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.3s ease;
      white-space: nowrap;
      background: #f5f5f5;
      color: #8c8c8c;
    }
  }
}

.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  flex-wrap: nowrap;

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
}

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

// 测试用例选择器样式
.test-case-selector {
  display: flex;
  gap: 20px;
  width: 100%;
}

.selector-panel {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.panel-header {
  background: #f5f7fa;
  padding: 12px 15px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;

  h4 {
    margin: 0;
    font-size: 14px;
    color: #303133;
  }
}

.panel-content {
  padding: 10px;
}


:deep(.selected-row) {
  background-color: #f0f9ff !important;
}

:deep(.el-table__row) {
  cursor: pointer;

  &:hover {
    background-color: #f5f7fa;
  }
}

.mode-description {
  margin-top: 8px;

  .description-text {
    font-size: 12px;
    color: #909399;
    line-height: 1.5;
  }
}

// 套件编辑弹窗样式优化
.suite-edit-dialog {
  :deep(.el-dialog__body) {
    max-height: 70vh;
    overflow-y: auto;
    padding: 20px 24px;
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid rgba(147, 112, 219, 0.15);
    padding: 16px 24px;

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .el-button {
        min-width: 80px;
      }
    }
  }

  .test-case-selector {
    display: flex;
    gap: 16px;
    width: 100%;
    min-width: 0;

    .selector-panel {
      flex: 1;
      min-width: 0;
      border: 1px solid rgba(147, 112, 219, 0.2);
      border-radius: 8px;
      overflow: hidden;
      background: #ffffff;

      .panel-header {
        background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
        padding: 10px 12px;
        border-bottom: 1px solid rgba(147, 112, 219, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;

        h4 {
          margin: 0;
          font-size: 13px;
          color: #5a32a3;
          font-weight: 600;
          white-space: nowrap;
        }

        .el-input {
          width: 140px !important;

          :deep(.el-input__wrapper) {
            border-radius: 4px;
            border: 1px solid rgba(147, 112, 219, 0.2);
            box-shadow: none;
            padding: 0 8px;

            .el-input__inner {
              font-size: 12px;
            }
          }
        }
      }

      .panel-content {
        padding: 8px;

        :deep(.el-table) {
          font-size: 12px;

          .el-table__cell {
            padding: 4px 0;
          }

          .el-button {
            padding: 2px;
            height: 22px;
            width: 22px;
            min-height: 22px;
            margin: 0 1px;

            .el-icon {
              font-size: 12px;
            }
          }

          .el-tag {
            font-size: 11px;
            padding: 0 4px;
            height: 18px;
          }

          // 操作列按钮容器
          .cell {
            display: flex;
            justify-content: center;
            align-items: center;
            white-space: nowrap;
            padding: 0 4px;
          }
        }
      }
    }
  }
}

// 响应式适配
@media screen and (max-width: 1200px) {
  .suite-edit-dialog {
    width: 95% !important;

    .test-case-selector {
      gap: 12px;

      .selector-panel {
        .panel-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;

          .el-input {
            width: 100% !important;
          }
        }
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .suite-edit-dialog {
    .test-case-selector {
      flex-direction: column;

      .selector-panel {
        .panel-header {
          flex-direction: row;

          .el-input {
            width: 120px !important;
          }
        }
      }
    }
  }
}

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

  // 未运行 - 灰色
  &.status-not-run {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  // 已通过 - 绿色
  &.status-passed {
    background: #f6ffed;
    color: #52c41a;
  }

  // 已失败 - 红色
  &.status-failed {
    background: #fff2f0;
    color: #ff4d4f;
  }

  // 运行中 - 蓝色
  &.status-running {
    background: #e6f7ff;
    color: #1890ff;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
