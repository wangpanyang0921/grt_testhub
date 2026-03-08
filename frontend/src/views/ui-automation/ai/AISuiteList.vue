<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索套件"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button class="reset-btn" @click="handleReset">重置</el-button>
      <el-button type="primary" class="query-btn" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="handleNewSuite">
        <el-icon><Plus /></el-icon>
        新增套件
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="suites" v-loading="loading" stripe style="width: 100%">
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="套件名称" min-width="200" show-overflow-tooltip header-align="center" align="left">
          <template #default="{ row }">
            <div class="suite-name-cell">{{ row.name }}</div>
          </template>
        </el-table-column>

        <el-table-column label="执行状态" width="110" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="row.execution_status">
              {{ getExecutionStatusText(row.execution_status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" :formatter="formatDate" header-align="center" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180" :formatter="formatDate" header-align="center" align="center" />
        <el-table-column prop="creator_name" label="创建人" width="120" header-align="center" align="center" />
        <el-table-column label="操作" width="280" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="success" class="action-btn run-btn" @click="runSuite(row)">
                <el-icon><VideoPlay /></el-icon>
                <span>运行</span>
              </el-button>
              <el-button size="small" type="primary" class="action-btn edit-btn" @click="editSuite(row.id)">
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
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

    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑套件' : '创建套件'"
      width="1000px"
      :close-on-click-modal="false"
      class="suite-dialog"
    >
      <div class="dialog-content">
        <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="90px">
          <div class="form-section">
            <div class="section-title">基本信息</div>
            <div class="form-inputs-panel">
              <el-form-item label="套件名称" prop="name">
                <el-input v-model="createForm.name" placeholder="请输入套件名称" />
              </el-form-item>
              <el-form-item label="描述" prop="description">
                <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
              </el-form-item>
            </div>
          </div>
          <div class="form-section">
            <div class="section-title">AI 测试用例</div>
            <div class="test-case-selector">
            <div class="selector-panel">
              <div class="panel-header">
                <h4>可用用例</h4>
                <el-input
                  v-model="testCaseSearchText"
                  placeholder="搜索用例"
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
                  height="300"
                  @row-click="handleTestCaseRowClick"
                  :row-class-name="getTestCaseRowClassName"
                >
                  <el-table-column prop="name" label="用例名称" width="180" show-overflow-tooltip />
                  <el-table-column prop="description" label="描述" min-width="480" show-overflow-tooltip />
                  <el-table-column label="操作" width="70" fixed="right">
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
                <h4>已选用例 ({{ selectedTestCases.length }})</h4>
              </div>
              <div class="panel-content">
                <el-table
                  :data="selectedTestCases"
                  height="300"
                >
                  <el-table-column prop="name" label="用例名称" width="180" show-overflow-tooltip />
                  <el-table-column prop="description" label="描述" min-width="480" show-overflow-tooltip />
                  <el-table-column label="操作" width="150" fixed="right">
                    <template #default="{ row, $index }">
                      <div class="action-buttons-inline">
                        <el-button
                          size="small"
                          text
                          @click="moveUp($index)"
                          :disabled="$index === 0"
                        >
                          <el-icon><Top /></el-icon>
                        </el-button>
                        <el-button
                          size="small"
                          text
                          @click="moveDown($index)"
                          :disabled="$index === selectedTestCases.length - 1"
                        >
                          <el-icon><Bottom /></el-icon>
                        </el-button>
                        <el-button
                          size="small"
                          text
                          type="danger"
                          @click="removeTestCase($index)"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
          </div>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelCreate">取消</el-button>
          <el-button type="primary" @click="handleCreate" :loading="saving">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="showRunDialog" title="运行配置" width="600px">
      <el-form :model="runConfig" label-width="120px">
        <el-form-item label="浏览器">
          <el-select v-model="runConfig.browser" placeholder="请选择浏览器">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Safari" value="safari" />
            <el-option label="Edge" value="edge" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行模式">
          <el-radio-group v-model="runConfig.headless">
            <el-radio :label="false">有头模式</el-radio>
            <el-radio :label="true">无头模式</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRunDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="confirmRunSuite"
            :loading="running"
          >
            开始执行
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
  Plus, Search, Edit, Delete, VideoPlay,
  ArrowRight, Top, Bottom
} from '@element-plus/icons-vue'
import {
  getAICases,
  getAITestSuites,
  createAITestSuite,
  updateAITestSuite,
  deleteAITestSuite,
  getAITestSuiteAICases,
  addAICaseToAITestSuite,
  removeAICaseFromAITestSuite,
  updateAICaseOrder,
  runAITestSuite
} from '@/api/ui_automation'
import { useRouter } from 'vue-router'

const router = useRouter()

const suites = ref([])
const loading = ref(false)
const searchText = ref('')
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

const showCreateDialog = ref(false)
const showRunDialog = ref(false)
const isEditing = ref(false)
const currentSuiteId = ref(null)
const saving = ref(false)
const running = ref(false)

const createForm = reactive({
  name: '',
  description: ''
})

const formRules = computed(() => ({
  name: [{ required: true, message: '请输入套件名称', trigger: 'blur' }]
}))

const availableTestCases = ref([])
const selectedTestCases = ref([])
const testCaseSearchText = ref('')

const runConfig = reactive({
  browser: 'chrome',
  headless: false
})
const currentRunningSuite = ref(null)

const filteredAvailableTestCases = computed(() => {
  if (!testCaseSearchText.value) {
    return availableTestCases.value
  }
  return availableTestCases.value.filter(tc =>
    tc.name.toLowerCase().includes(testCaseSearchText.value.toLowerCase()) ||
    (tc.description && tc.description.toLowerCase().includes(testCaseSearchText.value.toLowerCase()))
  )
})

const loadSuites = async () => {
  loading.value = true
  try {
    const response = await getAITestSuites({
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
    ElMessage.error('获取测试套件列表失败')
  } finally {
    loading.value = false
  }
}

const loadAvailableTestCases = async () => {
  try {
    const response = await getAICases({
      page_size: 1000
    })
    availableTestCases.value = response.data.results || response.data
  } catch (error) {
    console.error('获取测试用例列表失败:', error)
    ElMessage.error('获取测试用例列表失败')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadSuites()
}

const handleReset = () => {
  searchText.value = ''
  pagination.currentPage = 1
  loadSuites()
}

const handleSizeChange = () => {
  pagination.currentPage = 1
  loadSuites()
}

const handleCurrentChange = () => {
  loadSuites()
}

const handleCreate = async () => {
  if (!createForm.name) {
    ElMessage.warning('请输入套件名称')
    return
  }

  if (selectedTestCases.value.length === 0) {
    ElMessage.warning('请至少选择一个 AI 测试用例')
    return
  }

  saving.value = true
  try {
    const aiCasesData = selectedTestCases.value.map((testCase, index) => ({
      id: testCase.id,
      order: index
    }))

    const suiteData = {
      name: createForm.name,
      description: createForm.description,
      ai_cases: aiCasesData
    }

    if (isEditing.value) {
      await updateAITestSuite(currentSuiteId.value, suiteData)
      ElMessage.success('更新套件成功')
    } else {
      await createAITestSuite(suiteData)
      ElMessage.success('创建套件成功')
    }

    showCreateDialog.value = false
    await loadSuites()
    resetForm()
  } catch (error) {
    console.error('保存测试套件失败:', error)
    ElMessage.error('保存测试套件失败')
  } finally {
    saving.value = false
  }
}

const editSuite = async (id) => {
  try {
    const suite_data = suites.value.find(s => s.id === id)
    if (!suite_data) return

    currentSuiteId.value = id
    isEditing.value = true
    createForm.name = suite_data.name
    createForm.description = suite_data.description

    await loadAvailableTestCases()

    const testCasesResponse = await getAITestSuiteAICases(id)
    selectedTestCases.value = testCasesResponse.data.map(item => ({
      ...item.ai_case,
      order: item.order
    })).sort((a, b) => a.order - b.order)

    showCreateDialog.value = true
  } catch (error) {
    console.error('加载套件详情失败:', error)
    ElMessage.error('加载套件详情失败')
  }
}

const deleteSuite = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该测试套件吗？', '确认提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteAITestSuite(id)
    ElMessage.success('删除套件成功')
    await loadSuites()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试套件失败:', error)
      ElMessage.error('删除测试套件失败')
    }
  }
}

const runSuite = (suite) => {
  const totalCount = suite.ai_case_count || 0
  if (totalCount === 0) {
    ElMessage.warning('该测试套件未包含任何AI测试用例，无法执行')
    return
  }

  currentRunningSuite.value = suite
  showRunDialog.value = true
}

const confirmRunSuite = async () => {
  running.value = true
  try {
    const requestData = {
      browser: runConfig.browser,
      headless: runConfig.headless
    }

    const response = await runAITestSuite(currentRunningSuite.value.id, requestData)

    ElMessage.success('套件执行已启动')
    showRunDialog.value = false

    await loadSuites()

    pollSuiteStatus(currentRunningSuite.value.id)
  } catch (error) {
    console.error('执行测试套件失败:', error)
    const errorMsg = error.response?.data?.error || '执行测试套件失败'
    ElMessage.error(errorMsg)
  } finally {
    running.value = false
  }
}

const pollSuiteStatus = (suiteId) => {
  let pollCount = 0
  const maxPolls = 120

  const pollInterval = setInterval(async () => {
    pollCount++

    try {
      await loadSuites()

      const currentSuite = suites.value.find(s => s.id === suiteId)

      if (currentSuite && currentSuite.execution_status !== 'running') {
        clearInterval(pollInterval)

        if (currentSuite.execution_status === 'passed') {
          ElMessage.success(`套件执行完成: 全部通过 (${currentSuite.passed_count}/${currentSuite.passed_count + currentSuite.failed_count})`)
        } else if (currentSuite.execution_status === 'failed') {
          ElMessage.warning(`套件执行完成: 部分失败 (通过: ${currentSuite.passed_count}, 失败: ${currentSuite.failed_count})`)
        }
      }

      if (pollCount >= maxPolls) {
        clearInterval(pollInterval)
        ElMessage.info('套件执行时间较长，请稍后查看执行结果')
      }
    } catch (error) {
      console.error('轮询套件状态失败:', error)
      clearInterval(pollInterval)
    }
  }, 3000)
}

const handleTestCaseRowClick = (row) => {
  addTestCase(row)
}

const getTestCaseRowClassName = ({ row }) => {
  return selectedTestCases.value.some(tc => tc.id === row.id) ? 'selected-row' : ''
}

const addTestCase = (testCase) => {
  if (selectedTestCases.value.some(tc => tc.id === testCase.id)) {
    ElMessage.warning('该用例已添加')
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

const resetForm = () => {
  createForm.name = ''
  createForm.description = ''
  selectedTestCases.value = []
  testCaseSearchText.value = ''
  isEditing.value = false
  currentSuiteId.value = null
}

const cancelCreate = () => {
  showCreateDialog.value = false
  resetForm()
}

const handleNewSuite = async () => {
  resetForm()
  await loadAvailableTestCases()
  showCreateDialog.value = true
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  return new Date(cellValue).toLocaleString()
}

const getExecutionStatusTag = (status) => {
  const statusMap = {
    'not_run': 'info',
    'passed': 'success',
    'failed': 'danger',
    'running': 'warning'
  }
  return statusMap[status] || 'info'
}

const getExecutionStatusText = (status) => {
  const statusText = {
    'not_run': '未执行',
    'passed': '通过',
    'failed': '失败',
    'running': '运行中'
  }
  return statusText[status] || '未知'
}

onMounted(() => {
  loadSuites()
})
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

  // 未执行 - 灰色
  &.not_run {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  // 通过 - 绿色
  &.passed {
    background: #f6ffed;
    color: #52c41a;
  }

  // 失败 - 红色
  &.failed {
    background: #fff1f0;
    color: #f5222d;
  }

  // 运行中 - 橙色
  &.running {
    background: #fff7e6;
    color: #fa8c16;
  }
}

.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
}

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
}

.suite-name-cell {
  padding: 4px 8px;
  line-height: 1.6;
}

.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;

  :deep(.el-input__wrapper) {
    box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    background: #ffffff;

    &:hover,
    &:focus {
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
      border-color: #7b42f6;
    }
  }

  :deep(.el-input__inner) {
    color: #5a32a3;
    font-weight: 500;
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
    font-weight: 600 !important;
    padding: 10px 24px !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;
    transition: all 0.3s ease !important;

    .el-icon {
      margin-right: 6px;
    }

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4) !important;
    }
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

    :deep(.el-table__body-wrapper) {
      background-color: #ffffff !important;

      :deep(.el-table__row) {
        transition: all 0.3s ease;
        background-color: #ffffff !important;
        line-height: 24px;

        &:hover {
          background-color: #f8f7ff !important;
        }

        &.el-table__row--striped {
          background-color: #fafaff !important;
        }

        :deep(td) {
          padding: 14px 16px;
          border-bottom: 1px solid #e9ecef;
          color: #333;
          font-size: 14px;
          font-weight: 400;
          line-height: 24px;
          transition: all 0.3s ease;
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

    .el-pagination {
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
          }

          &.is-active:hover {
            background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
          }
        }
      }

      // 跳转输入框
      .el-pagination__jump {
        color: #5a32a3;
        font-weight: 500;
        margin-left: 12px;

        .el-input {
          width: 50px;
          margin: 0 4px;

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
            text-align: center;
          }
        }
      }
    }
  }
}

.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  flex-wrap: nowrap;
}

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

.test-case-selector {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.selector-panel {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;

  h4 {
    margin: 0;
    font-size: 14px;
    color: #303133;
    font-weight: 600;
  }
}

.panel-content {
  padding: 0;

  .el-table {
    font-size: 13px;
    width: 100%;

    .el-table__cell {
      padding: 8px 0;
    }
  }
}

.selected-row {
  background-color: #f0f9ff !important;
}

.action-buttons-inline {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  flex-wrap: nowrap;
}

.dialog-content {
  max-height: 650px;
  overflow-y: auto;
  padding: 8px 4px 8px 8px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 4px;
  border-left: 3px solid #7b42f6;
}

.form-inputs-panel {
  width: 100%;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 20px 24px;
  box-sizing: border-box;
}

.form-inputs-panel :deep(.el-form-item) {
  margin-bottom: 20px;
}

.form-inputs-panel :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.form-inputs-panel :deep(.el-input__wrapper) {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.3s;
}

.form-inputs-panel :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.form-inputs-panel :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #7b42f6 inset;
}

.form-inputs-panel :deep(.el-textarea__inner) {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s;
}

.form-inputs-panel :deep(.el-textarea__inner:hover) {
  border-color: #c0c4cc;
}

.form-inputs-panel :deep(.el-textarea__inner:focus) {
  border-color: #7b42f6;
}

.selector-panel {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: linear-gradient(135deg, #f8f7ff 0%, #f0f0ff 100%);
  border-bottom: 1px solid #ebeef5;

  h4 {
    margin: 0;
    font-size: 14px;
    color: #5a32a3;
    font-weight: 600;
  }
}

.test-case-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

:deep(.suite-dialog) {
  .el-dialog__header {
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
    margin: 0;
  }

  .el-dialog__title {
    font-size: 18px;
    font-weight: 600;
    color: #5a32a3;
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




</style>
