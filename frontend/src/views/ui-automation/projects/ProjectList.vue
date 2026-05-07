<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        :placeholder="$t('uiAutomation.project.searchPlaceholder')"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
        class="search-input"
      >
        <template #suffix>
          <el-icon @click="handleSearch" style="cursor: pointer;"><Search /></el-icon>
        </template>
      </el-input>
      <!-- 状态筛选已隐藏 -->
      <!--
      <el-select v-model="statusFilter" :placeholder="$t('uiAutomation.project.statusFilter')" clearable @change="handleFilter" style="width: 160px;">
        <el-option :label="$t('uiAutomation.status.notStarted')" value="NOT_STARTED" />
        <el-option :label="$t('uiAutomation.status.inProgress')" value="IN_PROGRESS" />
        <el-option :label="$t('uiAutomation.status.completed')" value="COMPLETED" />
      </el-select>
      -->
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.project.newProject') }}
      </el-button>
    </div>

    <div class="card-container">
      
      <el-table :data="projects" v-loading="loading" stripe style="width: 100%">
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="$t('uiAutomation.project.projectName')" min-width="200" header-align="center" align="center">
          <template #default="{ row }">
            <span class="project-name-cell" @click="goToProjectDetail(row.id)">
              {{ row.name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('uiAutomation.common.status')" width="110" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="base_url" :label="$t('uiAutomation.project.baseUrl')" min-width="200" show-overflow-tooltip header-align="center" align="center" />
        <el-table-column prop="owner.username" :label="$t('uiAutomation.project.owner')" width="100" header-align="center" align="center" />
        <el-table-column :label="$t('uiAutomation.common.operation')" width="240" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" class="action-btn view-btn" @click="goToProjectDetail(row.id)">
                <el-icon><View /></el-icon>
                <span>{{ $t('uiAutomation.common.view') }}</span>
              </el-button>
              <el-button size="small" class="action-btn edit-btn" @click="editProject(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('uiAutomation.common.edit') }}</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteProject(row.id)">
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
    
    <!-- 创建项目对话框 -->
    <el-dialog v-model="showCreateDialog" :title="$t('uiAutomation.project.createProject')" width="500px">
      <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="80px">
        <el-form-item :label="$t('uiAutomation.project.projectName')" prop="name">
          <el-input v-model="createForm.name" :placeholder="$t('uiAutomation.project.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.projectDesc')" prop="description">
          <el-input v-model="createForm.description" type="textarea" :placeholder="$t('uiAutomation.project.projectDesc')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.status')" prop="status">
          <el-select v-model="createForm.status" :placeholder="$t('uiAutomation.project.rules.selectStatus')">
            <el-option :label="$t('uiAutomation.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('uiAutomation.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('uiAutomation.status.completed')" value="COMPLETED" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.baseUrl')" prop="base_url">
          <el-input v-model="createForm.base_url" :placeholder="$t('uiAutomation.project.rules.baseUrlRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.startDate')" prop="start_date">
          <el-date-picker v-model="createForm.start_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.endDate')" prop="end_date">
          <el-date-picker v-model="createForm.end_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleCreate">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑项目对话框 -->
    <el-dialog v-model="showEditDialog" :title="$t('uiAutomation.project.editProject')" width="500px">
      <el-form ref="editFormRef" :model="editForm" :rules="formRules" label-width="80px">
        <el-form-item :label="$t('uiAutomation.project.projectName')" prop="name">
          <el-input v-model="editForm.name" :placeholder="$t('uiAutomation.project.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.projectDesc')" prop="description">
          <el-input v-model="editForm.description" type="textarea" :placeholder="$t('uiAutomation.project.projectDesc')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.status')" prop="status">
          <el-select v-model="editForm.status" :placeholder="$t('uiAutomation.project.rules.selectStatus')">
            <el-option :label="$t('uiAutomation.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('uiAutomation.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('uiAutomation.status.completed')" value="COMPLETED" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.baseUrl')" prop="base_url">
          <el-input v-model="editForm.base_url" :placeholder="$t('uiAutomation.project.rules.baseUrlRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.startDate')" prop="start_date">
          <el-date-picker v-model="editForm.start_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.endDate')" prop="end_date">
          <el-date-picker v-model="editForm.end_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleEdit">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 项目详情弹框 -->
    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.project.projectDetail')" width="600px">
      <div v-if="currentProjectDetail" class="project-detail">
        <el-descriptions bordered column="1" class="detail-descriptions" label-width="120px">
          <el-descriptions-item :label="$t('uiAutomation.project.projectName')" label-class-name="label-right">{{ currentProjectDetail.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.projectDesc')" :span="2" label-class-name="label-right">{{ currentProjectDetail.description || $t('uiAutomation.project.noDescription') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.status')" label-class-name="label-right">
            <span class="detail-status-text" :class="getStatusClass(currentProjectDetail.status)">
              {{ getStatusText(currentProjectDetail.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.baseUrl')" label-class-name="label-right">{{ currentProjectDetail.base_url }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.owner')" label-class-name="label-right">{{ currentProjectDetail.owner?.username || $t('uiAutomation.project.none') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.startDate')" label-class-name="label-right">{{ currentProjectDetail.start_date ? formatDate(null, null, currentProjectDetail.start_date) : $t('uiAutomation.project.notSet') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.endDate')" label-class-name="label-right">{{ currentProjectDetail.end_date ? formatDate(null, null, currentProjectDetail.end_date) : $t('uiAutomation.project.notSet') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.createTime')" label-class-name="label-right">{{ formatDate(null, null, currentProjectDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.updateTime')" label-class-name="label-right">{{ formatDate(null, null, currentProjectDetail.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else class="text-center text-gray-500">
        {{ $t('uiAutomation.common.loading') }}
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
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, View, Edit, Delete } from '@element-plus/icons-vue'
import { getUiProjects, createUiProject, updateUiProject, deleteUiProject } from '@/api/ui_automation'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const router = useRouter()

// 项目数据
const projects = ref([])
const loading = ref(false)
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

// 搜索和筛选
const searchText = ref('')
const statusFilter = ref('')

// 表单相关
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const createFormRef = ref(null)
const editFormRef = ref(null)
const currentEditId = ref(null)

// 表单数据
const createForm = reactive({
  name: '',
  description: '',
  status: 'IN_PROGRESS',
  base_url: '',
  start_date: null,
  end_date: null
})

const editForm = reactive({
  name: '',
  description: '',
  status: 'IN_PROGRESS',
  base_url: '',
  start_date: null,
  end_date: null
})

// 表单验证规则
const formRules = computed(() => ({
  name: [
    { required: true, message: t('uiAutomation.project.rules.nameRequired'), trigger: 'blur' },
    { min: 2, max: 200, message: t('uiAutomation.project.rules.nameLength'), trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: t('uiAutomation.project.rules.baseUrlRequired'), trigger: 'blur' },
    { type: 'url', message: t('uiAutomation.project.rules.baseUrlInvalid'), trigger: 'blur' }
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
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取状态样式（用于 el-tag）
const getStatusType = (status) => {
  const statusMap = {
    'NOT_STARTED': 'warning',
    'IN_PROGRESS': 'primary',
    'COMPLETED': 'success'
  }
  return statusMap[status] || 'default'
}

// 获取状态徽章样式类
const getStatusClass = (status) => {
  const statusMap = {
    'NOT_STARTED': 'not_started',
    'IN_PROGRESS': 'in_progress',
    'COMPLETED': 'completed'
  }
  return statusMap[status] || 'not_started'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusKey = {
    'NOT_STARTED': 'notStarted',
    'IN_PROGRESS': 'inProgress',
    'COMPLETED': 'completed'
  }[status]
  return statusKey ? t(`uiAutomation.status.${statusKey}`) : status
}

// 加载项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    // 添加搜索条件
    if (searchText.value) {
      params.search = searchText.value
    }
    
    // 添加筛选条件
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await getUiProjects(params)
    projects.value = response.data.results || response.data
    total.value = response.data.count || projects.value.length
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.loadFailed'))
    console.error('获取项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.currentPage = 1
  loadProjects()
}

// 筛选处理
const handleFilter = () => {
  pagination.currentPage = 1
  loadProjects()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadProjects()
}

const handleCurrentChange = (current) => {
  pagination.currentPage = current
  loadProjects()
}

// 详情相关
const showDetailDialog = ref(false)
const currentProjectDetail = ref(null)

// 查看项目详情
const goToProjectDetail = (id) => {
  // 查找当前项目
  const project = projects.value.find(p => p.id === id)
  if (project) {
    currentProjectDetail.value = project
    showDetailDialog.value = true
  } else {
    ElMessage.error(t('uiAutomation.project.messages.notFound'))
  }
}

// 编辑项目
const editProject = (project) => {
  currentEditId.value = project.id
  // 复制项目数据到编辑表单
  Object.assign(editForm, {
    name: project.name,
    description: project.description,
    status: project.status,
    base_url: project.base_url,
    start_date: project.start_date ? new Date(project.start_date) : null,
    end_date: project.end_date ? new Date(project.end_date) : null
  })
  showEditDialog.value = true
}

// 删除项目
const deleteProject = async (id) => {
  try {
    await ElMessageBox.confirm(t('uiAutomation.project.messages.deleteConfirm'), t('uiAutomation.messages.confirm.delete'), {
      confirmButtonText: t('uiAutomation.common.confirm'),
      cancelButtonText: t('uiAutomation.common.cancel'),
      type: 'warning'
    })

    await deleteUiProject(id)
    ElMessage.success(t('uiAutomation.project.messages.deleteSuccess'))
    loadProjects()
  } catch (error) {
    if (error === 'cancel') return
    ElMessage.error(t('uiAutomation.project.messages.deleteFailed'))
    console.error('删除项目失败:', error)
  }
}

// 导入用户store
import { useUserStore } from '@/stores/user'

// 日期格式化辅助函数
const formatDateToISO = (date) => {
  if (!date) return null
  // 确保是Date对象
  const d = new Date(date)
  // 格式化为YYYY-MM-DD格式
  return d.toISOString().split('T')[0]
}

// 处理创建项目
const handleCreate = async () => {
  const validate = await createFormRef.value.validate()
  if (!validate) return
  
  try {
    const userStore = useUserStore()
    // 确保用户信息已加载
    if (!userStore.user?.id) {
      await userStore.fetchProfile()
    }
    
    // 创建包含owner字段的项目数据，并格式化日期字段
    const projectData = {
      ...createForm,
      owner: userStore.user.id,  // 添加owner字段，值为当前登录用户ID
      // 格式化日期为YYYY-MM-DD格式
      start_date: formatDateToISO(createForm.start_date),
      end_date: formatDateToISO(createForm.end_date)
    }
    
    await createUiProject(projectData)
    ElMessage.success(t('uiAutomation.project.messages.createSuccess'))
    showCreateDialog.value = false
    
    // 重置表单
    Object.keys(createForm).forEach(key => {
      createForm[key] = ''
    })
    createForm.status = 'IN_PROGRESS'
    
    loadProjects()
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.createFailed'))
    console.error('创建项目失败:', error)
  }
}

// 处理编辑项目
const handleEdit = async () => {
  const validate = await editFormRef.value.validate()
  if (!validate) return
  
  try {
    // 创建包含格式化日期字段的项目数据
    const projectData = {
      ...editForm,
      // 格式化日期为YYYY-MM-DD格式
      start_date: formatDateToISO(editForm.start_date),
      end_date: formatDateToISO(editForm.end_date)
    }
    
    await updateUiProject(currentEditId.value, projectData)
    ElMessage.success(t('uiAutomation.project.messages.updateSuccess'))
    showEditDialog.value = false
    loadProjects()
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.updateFailed'))
    console.error('更新项目失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadProjects()
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

  // 未开始 - 灰色
  &.not_started {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  // 进行中 - 绿色
  &.in_progress {
    background: #f6ffed;
    color: #52c41a;
  }

  // 已完成 - 绿色
  &.completed {
    background: #f6ffed;
    color: #52c41a;
  }
}

// 详情弹窗中的状态文本样式（与其他字段对齐）
.detail-status-text {
  font-size: 14px;
  line-height: 22px;

  &.not_started {
    color: #8c8c8c;
  }

  &.in_progress {
    color: #52c41a;
  }

  &.completed {
    color: #52c41a;
  }
}

// 标签右对齐样式 - 应用于 el-descriptions 的 bordered 模式
:deep(.detail-descriptions) {
  // 针对 bordered 模式的标签单元格
  .el-descriptions__cell.is-bordered-label {
    text-align: right !important;
    justify-content: flex-end !important;
    
    .el-descriptions__label {
      text-align: right !important;
      justify-content: flex-end !important;
      width: 100%;
    }
  }
  
  // 标签类名样式
  .label-right {
    text-align: right !important;
    justify-content: flex-end !important;
    display: inline-flex;
    width: 100%;
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

  .search-input {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.2) inset;
      background: #ffffff;

      &:hover, &.is-focus {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
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
        line-height: 24px;

        &:hover {
          background-color: #f8f7ff !important;
        }

        &.el-table__row--striped {
          background-color: #fafaff !important;
        }

        // 表格单元格
        :deep(td) {
          padding: 14px 16px;
          border-bottom: 1px solid #e9ecef;
          color: #595959;
          font-size: 14px;
          font-weight: normal;
          line-height: 24px;
          transition: all 0.3s ease;

          // 项目名称样式 - 与其他字段一致
          .project-name-cell {
            font-size: 14px;
            font-weight: normal;
            color: #595959;
            line-height: 24px;
            cursor: pointer;
            transition: color 0.3s ease;

            &:hover {
              color: #7b42f6;
            }
          }

          // 标签样式
          .el-tag {
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            padding: 2px 8px;
            transition: all 0.3s ease;
          }

          // 单元格内部容器样式统一
          :deep(.cell) {
            font-size: 14px;
            font-weight: normal;
            color: #595959;
            line-height: 24px;
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
            border: 1px solid #d1d5db;
            color: #6b7280;

            &:hover {
              background: #f5f3ff;
              color: #8b5cf6;
            }
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
}

// 对话框样式
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

    .el-form {
      .el-form-item {
        .el-form-item__label {
          color: #5a32a3;
          font-weight: 500;
        }

        .el-input__wrapper,
        .el-select .el-input__wrapper,
        .el-date-picker .el-input__wrapper {
          box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);

          &:hover,
          &:focus {
            box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
            border-color: #7b42f6;
          }
        }

        .el-date-picker {
          width: 100%;

          .el-input__wrapper {
            width: 100%;
          }
        }

        .el-textarea__inner {
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);

          &:hover,
          &:focus {
            border-color: #7b42f6;
          }
        }
      }
    }
  }

  // 项目详情样式
  .project-detail {
    :deep(.detail-descriptions) {
      .el-descriptions__label {
        text-align: right !important;
        justify-content: flex-end !important;
      }
    }
  }

  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid #ebeef5;
    background: #fafafa;

    .el-button {
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 8px;

      &.el-button--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;

        &:hover {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
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

// 响应式布局
@media (max-width: 1200px) {
  .page-container {
    padding: 16px;
  }

  .page-header {
    padding: 20px;

    .page-title {
      font-size: 20px;
    }
  }

  .filter-bar {
    padding: 16px;

    .el-row {
      gap: 12px;
    }
  }

  .card-container {
    .pagination-container {
      padding: 16px;
    }
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;

    .el-button {
      align-self: flex-end;
    }
  }

  .filter-bar {
    padding: 16px;

    .el-row {
      flex-direction: column;
      align-items: stretch;

      .el-col {
        width: 100% !important;

        .el-input,
        .el-select {
          width: 100%;
        }
      }
    }
  }

  .card-container {
    .pagination-container {
      padding: 12px;
      justify-content: center;

      .el-pagination {
        flex-wrap: wrap;
        justify-content: center;
      }
    }
  }
}
</style>