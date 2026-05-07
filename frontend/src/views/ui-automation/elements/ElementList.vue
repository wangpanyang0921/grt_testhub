<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('uiAutomation.element.title') }}</h1>
        <el-select v-model="projectId" :placeholder="$t('uiAutomation.common.selectProject')" class="project-select" @change="onProjectChange">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </div>
      <el-button type="primary" @click="handleShowCreateDialog">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.element.newElement') }}
      </el-button>
    </div>
    
    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchText"
            :placeholder="$t('uiAutomation.element.searchPlaceholder')"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="strategyFilter" :placeholder="$t('uiAutomation.element.strategyFilter')" clearable @change="handleFilter">
            <el-option v-for="strategy in strategies" :key="strategy.id" :label="strategy.name" :value="strategy.id" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="pageFilter" :placeholder="$t('uiAutomation.element.pageFilter')" clearable @change="handleFilter">
            <el-option v-for="page in pages" :key="page" :label="page" :value="page" />
          </el-select>
        </el-col>
      </el-row>
    </div>
    
    <div class="card-container">
      <el-table :data="elements" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="selection" width="55" header-align="center" align="center" />
        <el-table-column prop="name" :label="$t('uiAutomation.element.elementName')" min-width="150" header-align="center" align="center">
          <template #default="{ row }">
            <el-link @click="showElementDetail(row.id)" type="primary">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="page" :label="$t('uiAutomation.element.page')" width="120" header-align="center" align="center" />
        <el-table-column prop="description" :label="$t('uiAutomation.common.description')" min-width="200" show-overflow-tooltip header-align="center" align="center" />
        <el-table-column :label="$t('uiAutomation.element.locatorStrategy')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            {{ row.locator_strategy?.name || $t('uiAutomation.element.unknown') }}
          </template>
        </el-table-column>
        <el-table-column prop="locator_value" :label="$t('uiAutomation.element.locatorValue')" min-width="200" show-overflow-tooltip header-align="center" align="center" />
        <el-table-column prop="created_at" :label="$t('uiAutomation.common.createTime')" width="180" :formatter="formatDate" header-align="center" align="center" />
        <el-table-column prop="updated_at" :label="$t('uiAutomation.common.updateTime')" width="180" :formatter="formatDate" header-align="center" align="center" />
        <el-table-column :label="$t('uiAutomation.common.operation')" width="240" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" class="action-btn view-btn" @click="showElementDetail(row.id)">
                <el-icon><View /></el-icon>
                <span>{{ $t('uiAutomation.common.view') }}</span>
              </el-button>
              <el-button size="small" class="action-btn edit-btn" @click="editElement(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('uiAutomation.common.edit') }}</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="handleDeleteElement(row.id)">
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
    
    <!-- 创建元素对话框 -->
    <el-dialog v-model="showCreateDialog" :title="$t('uiAutomation.element.createElement')" width="600px">
      <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.element.elementName')" prop="name">
          <el-input v-model="createForm.name" :placeholder="$t('uiAutomation.element.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.page')" prop="page">
          <el-input v-model="createForm.page" :placeholder="$t('uiAutomation.element.rules.pageRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="createForm.description" type="textarea" :placeholder="$t('uiAutomation.common.description')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.locatorStrategy')" prop="strategy">
          <el-select v-model="createForm.strategy" :placeholder="$t('uiAutomation.element.rules.strategyRequired')" @change="onStrategyChange">
            <el-option v-for="strategy in strategies" :key="strategy.id" :label="strategy.name" :value="strategy.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.locatorValue')" prop="locator_value">
          <el-input v-model="createForm.locator_value" :placeholder="$t('uiAutomation.element.rules.locatorRequired')" />
          <div class="el-form-item__help">
            <small style="color: #606266;">
              {{ $t('uiAutomation.element.locatorTip.title') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.id') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.css') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.xpath') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.other') }}
            </small>
          </div>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.isUnique')" prop="is_unique">
          <el-switch v-model="createForm.is_unique" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.waitTimeout')" prop="wait_timeout">
          <el-input-number v-model="createForm.wait_timeout" :min="0" :max="30" :step="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleCreate">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑元素对话框 -->
    <el-dialog v-model="showEditDialog" :title="$t('uiAutomation.element.editElement')" width="600px">
      <el-form ref="editFormRef" :model="editForm" :rules="formRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.element.elementName')" prop="name">
          <el-input v-model="editForm.name" :placeholder="$t('uiAutomation.element.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.page')" prop="page">
          <el-input v-model="editForm.page" :placeholder="$t('uiAutomation.element.rules.pageRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="editForm.description" type="textarea" :placeholder="$t('uiAutomation.common.description')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.locatorStrategy')" prop="strategy">
          <el-select v-model="editForm.strategy" :placeholder="$t('uiAutomation.element.rules.strategyRequired')" @change="onEditStrategyChange">
            <el-option v-for="strategy in strategies" :key="strategy.id" :label="strategy.name" :value="strategy.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.locatorValue')" prop="locator_value">
          <el-input v-model="editForm.locator_value" :placeholder="$t('uiAutomation.element.rules.locatorRequired')" />
          <div class="el-form-item__help">
            <small style="color: #606266;">
              {{ $t('uiAutomation.element.locatorTip.title') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.id') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.css') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.xpath') }}<br>
              - {{ $t('uiAutomation.element.locatorTip.other') }}
            </small>
          </div>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.isUnique')" prop="is_unique">
          <el-switch v-model="editForm.is_unique" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.waitTimeout')" prop="wait_timeout">
          <el-input-number v-model="editForm.wait_timeout" :min="0" :max="30" :step="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleEdit">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 元素详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.element.elementDetail')" width="600px">
      <div v-if="Object.keys(currentElementDetail).length > 0" class="element-detail">
        <el-descriptions border column="2" :column="{ xs: 1, sm: 2 }">
          <el-descriptions-item :label="$t('uiAutomation.element.elementName')">{{ currentElementDetail.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.page')">{{ currentElementDetail.page }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.project')">{{ currentElementDetail.project?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.locatorStrategy')">{{ currentElementDetail.locator_strategy?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.locatorValue')" :span="2">
            <el-tag type="info" style="word-break: break-all; display: block; text-align: left;">
              {{ currentElementDetail.locator_value }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.isUnique')">
            <el-tag :type="currentElementDetail.is_unique ? 'success' : 'warning'">
              {{ currentElementDetail.is_unique ? $t('uiAutomation.common.yes') : $t('uiAutomation.common.no') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.waitTimeout')">{{ currentElementDetail.wait_timeout || 5 }}{{ $t('uiAutomation.element.waitTimeoutUnit') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.description')" :span="2">{{ currentElementDetail.description === undefined ? '-' : currentElementDetail.description }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.createTime')">{{ formatDate(null, null, currentElementDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.updateTime')">{{ formatDate(null, null, currentElementDetail.updated_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.element.createdBy')" :span="2">{{ currentElementDetail.created_by?.username || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else class="text-center text-gray-500 py-10">
        {{ $t('uiAutomation.element.loadingDetail') }}
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, View, Edit, Delete } from '@element-plus/icons-vue'
import {
  getUiProjects,
  getElements,
  createElement,
  updateElement,
  deleteElement,
  getElementDetail,
  getLocatorStrategies
} from '@/api/ui_automation'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 项目和元素数据
const projects = ref([])
const projectId = ref('')
const elements = ref([])

// 定位策略数据
const strategies = ref([])
const pages = ref([])
const loading = ref(false)
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

// 搜索和筛选
const searchText = ref('')
const strategyFilter = ref('')
const pageFilter = ref('')

// 表单相关
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const createFormRef = ref(null)
const editFormRef = ref(null)
const currentEditId = ref(null)
const currentElementDetail = ref({})

// 表单数据
const createForm = reactive({
  project: '',
  name: '',
  page: '',
  description: '',
  strategy: '',
  locator_value: '',
  is_unique: false,
  wait_timeout: 5
})

const editForm = reactive({
  project: '',
  name: '',
  page: '',
  description: '',
  strategy: '',
  locator_value: '',
  is_unique: false,
  wait_timeout: 5
})

// 表单验证规则
const formRules = computed(() => ({
  name: [
    { required: true, message: t('uiAutomation.element.rules.nameRequired'), trigger: 'blur' },
    { min: 2, max: 100, message: t('uiAutomation.element.rules.nameLength'), trigger: 'blur' }
  ],
  page: [
    { required: true, message: t('uiAutomation.element.rules.pageRequired'), trigger: 'blur' }
  ],
  strategy: [
    { required: true, message: t('uiAutomation.element.rules.strategyRequired'), trigger: 'change' }
  ],
  locator_value: [
    { required: true, message: t('uiAutomation.element.rules.locatorRequired'), trigger: 'blur' }
  ]
}))

// 格式化日期
const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  return new Date(cellValue).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.loadFailed'))
    console.error('获取项目列表失败:', error)
  }
}

// 加载定位策略
const loadStrategies = async () => {
  try {
    const response = await getLocatorStrategies()
    strategies.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.element.messages.loadStrategiesFailed'))
    console.error('获取定位策略失败:', error)
  }
}

// 处理显示创建对话框
const handleShowCreateDialog = () => {
  showCreateDialog.value = true
}

// 加载元素列表
const loadElements = async () => {
  if (!projectId.value) {
    elements.value = []
    total.value = 0
    return
  }
  
  loading.value = true
  try {
    const params = {
      project: projectId.value,
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }

    // 添加搜索条件
    if (searchText.value) {
      params.search = searchText.value
    }

    // 添加筛选条件
    if (strategyFilter.value) {
      params.locator_strategy = strategyFilter.value
    }

    // 页面筛选 - 使用page_name参数避免与分页page冲突
    if (pageFilter.value) {
      params.page_name = pageFilter.value
    }
    
    const response = await getElements(params)
    elements.value = response.data.results || response.data
    total.value = response.data.count || elements.value.length
    
    // 提取所有页面名称用于筛选
    const pageNames = [...new Set(elements.value.map(el => el.page))]
    pages.value = pageNames.filter(name => name)
  } catch (error) {
    ElMessage.error(t('uiAutomation.element.messages.loadFailed'))
    console.error('获取元素列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 项目变更处理
const onProjectChange = () => {
  // 清空搜索和筛选条件
  searchText.value = ''
  strategyFilter.value = ''
  pageFilter.value = ''
  pagination.currentPage = 1
  
  // 设置创建表单的项目
  createForm.project = projectId.value
  
  // 重新加载元素
  loadElements()
}

// 搜索处理
const handleSearch = () => {
  pagination.currentPage = 1
  loadElements()
}

// 筛选处理
const handleFilter = () => {
  pagination.currentPage = 1
  loadElements()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadElements()
}

const handleCurrentChange = (current) => {
  pagination.currentPage = current
  loadElements()
}

// 查看元素详情
const showElementDetail = async (id) => {
  try {
    // 清空之前的数据，避免缓存问题
    currentElementDetail.value = {}

    // 使用专门的详情API获取单个元素的完整信息
    const response = await getElementDetail(id)
    console.log('API返回的元素详情:', response.data)

    currentElementDetail.value = response.data
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error(t('uiAutomation.element.messages.loadDetailFailed'))
    console.error('获取元素详情失败:', error)
  }
}

// 编辑元素
const editElement = (element) => {
  currentEditId.value = element.id

  // 查找策略ID - 修正字段名
  const strategy = strategies.value.find(s => s.name === element.locator_strategy?.name)

  // 复制元素数据到编辑表单
  Object.assign(editForm, {
    project: element.project,
    name: element.name,
    page: element.page,
    description: element.description,
    strategy: strategy ? strategy.id : '',
    locator_value: element.locator_value,
    is_unique: element.is_unique,
    wait_timeout: element.wait_timeout || 5
  })

  showEditDialog.value = true
}

// 删除元素
const handleDeleteElement = async (id) => {
  try {
    await ElMessageBox.confirm(t('uiAutomation.element.messages.deleteConfirm'), t('uiAutomation.messages.confirm.delete'), {
      confirmButtonText: t('uiAutomation.common.confirm'),
      cancelButtonText: t('uiAutomation.common.cancel'),
      type: 'warning'
    })

    await deleteElement(id)
    ElMessage.success(t('uiAutomation.element.messages.deleteSuccess'))
    loadElements()
  } catch (error) {
    if (error === 'cancel') return
    ElMessage.error(t('uiAutomation.element.messages.deleteFailed'))
    console.error('删除元素失败:', error)
  }
}

// 定位策略变更处理
const onStrategyChange = () => {
  // 可以根据定位策略类型提供不同的输入提示或验证
}

const onEditStrategyChange = () => {
  // 可以根据定位策略类型提供不同的输入提示或验证
}

// 处理创建元素
const handleCreate = async () => {
  const validate = await createFormRef.value.validate()
  if (!validate) return
  
  try {
    // 直接使用选择的策略ID，确保是整数类型
    const apiFormData = {
      name: createForm.name,
      page: createForm.page,
      description: createForm.description,
      locator_value: createForm.locator_value,
      project_id: projectId.value, // 使用当前选择的项目ID
      locator_strategy_id: createForm.strategy, // 直接使用整数ID，无需转换
      is_unique: createForm.is_unique, // 添加缺失的字段
      wait_timeout: createForm.wait_timeout // 添加缺失的字段
    }
    
    console.log('提交的API数据:', apiFormData)
    await createElement(apiFormData)
    ElMessage.success(t('uiAutomation.element.messages.createSuccess'))
    showCreateDialog.value = false
    
    // 重置表单
    Object.assign(createForm, {
      name: '',
      page: '',
      description: '',
      strategy: '',
      locator_value: '',
      is_unique: false,
      wait_timeout: 5
    })
    
    loadElements()
  } catch (error) {
    console.error('创建元素失败:', error)
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.locator_strategy_id) {
        ElMessage.error(errorData.locator_strategy_id[0])
      } else if (errorData.project_id) {
        ElMessage.error(errorData.project_id[0])
      } else {
        ElMessage.error(t('uiAutomation.element.messages.createFailed') + ': ' + JSON.stringify(errorData))
      }
    } else {
      ElMessage.error(t('uiAutomation.element.messages.createFailed'))
    }
  }
}

// 处理编辑元素
const handleEdit = async () => {
  const validate = await editFormRef.value.validate()
  if (!validate) return
  
  try {
    // 确保project_id是有效的整数值
    const projectIdInt = parseInt(editForm.project) || projectId.value;
    
    // 构建API请求数据
    const apiFormData = {
      name: editForm.name,
      page: editForm.page,
      description: editForm.description,
      locator_value: editForm.locator_value,
      project_id: projectIdInt, // 使用有效的整数项目ID
      locator_strategy_id: editForm.strategy,
      is_unique: editForm.is_unique, // 添加缺失的字段
      wait_timeout: editForm.wait_timeout // 添加缺失的字段
    }
    
    console.log('提交的API数据:', apiFormData)
    await updateElement(currentEditId.value, apiFormData)
    ElMessage.success(t('uiAutomation.element.messages.updateSuccess'))
    showEditDialog.value = false
    loadElements()
  } catch (error) {
    ElMessage.error(t('uiAutomation.element.messages.updateFailed'))
    console.error('更新元素失败:', error)
  }
}

// 监听项目选择变化
watch(projectId, (newValue) => {
  if (newValue) {
    createForm.project = newValue
  }
})

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadProjects(),
    loadStrategies()
  ])

  // 如果有项目，默认选择第一个
  if (projects.value.length > 0) {
    projectId.value = projects.value[0].id
    createForm.project = projectId.value
    await loadElements()
  }
})
</script>

<style lang="scss" scoped>
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
      box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.25);
      border-radius: 8px;

      &:hover,
      &:focus {
        box-shadow: 0 0 0 1px #7b42f6;
      }
    }
  }

  .el-button {
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

// 筛选栏
.filter-bar {
  padding: 20px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.1);

  .el-row {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;

    .el-col {
      margin-bottom: 0;

      .el-input__wrapper,
      .el-select .el-input__wrapper {
        box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.25);
        border-radius: 8px;

        &:hover,
        &:focus {
          box-shadow: 0 0 0 1px #7b42f6;
        }
      }
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

  &.edit-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3) !important;
    transition: all 0.3s ease !important;
    white-space: nowrap;

    &:hover {
      background: linear-gradient(135deg, #0da271 0%, #047857 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
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
  padding: 20px 24px;
  display: flex;
  justify-content: flex-end;
  background: #ffffff;
  border-top: 1px solid rgba(147, 112, 219, 0.1);

  :deep(.el-pagination) {
    --el-pagination-button-bg-color: #ffffff;
    --el-pagination-hover-color: #7b42f6;

    .el-pager li {
      border-radius: 8px;
      transition: all 0.3s ease;

      &.is-active {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        color: #ffffff;
      }

      &:hover {
        color: #7b42f6;
      }
    }

    .btn-prev,
    .btn-next {
      border-radius: 8px;

      &:hover {
        color: #7b42f6;
      }
    }
  }
}
</style>