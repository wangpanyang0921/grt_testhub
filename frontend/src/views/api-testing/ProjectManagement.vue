<template>
  <div class="page-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div></div>
      <el-button type="primary" @click="showCreateDialog = true" class="create-btn">
        <el-icon><Plus /></el-icon>
        {{ $t('apiTesting.project.createProject') }}
      </el-button>
    </div>

    <!-- 项目列表卡片 -->
    <div class="card-container">
      <el-table :data="projects" v-loading="loading" style="width: 100%" class="custom-table">
      <el-table-column label="序号" width="90" header-align="center" align="center">
        <template #default="{ $index }">
          {{ (currentPage - 1) * pageSize + $index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="name" :label="$t('apiTesting.project.projectName')" min-width="160" header-align="center" align="center" />
      <el-table-column prop="project_type" :label="$t('apiTesting.project.projectType')" width="140" header-align="center" align="center">
        <template #default="scope">
          <span class="status-badge" :class="scope.row.project_type === 'HTTP' ? 'http' : 'websocket'">
            {{ scope.row.project_type }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="$t('apiTesting.project.projectStatus')" width="140" header-align="center" align="center">
        <template #default="scope">
          <span class="status-badge" :class="getStatusClass(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="owner.username" :label="$t('apiTesting.project.owner')" width="150" header-align="center" align="center" />
      <el-table-column prop="created_at" :label="$t('apiTesting.project.createdAt')" width="180" header-align="center" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('apiTesting.common.operation')" width="260" fixed="right" header-align="center" align="center">
        <template #default="scope">
          <div class="action-buttons">
            <el-button size="small" type="primary" class="action-btn edit-btn" @click="editProject(scope.row)">
              <el-icon><Edit /></el-icon>
              <span>{{ $t('apiTesting.common.edit') }}</span>
            </el-button>
            <el-button size="small" type="success" class="action-btn view-btn" @click="viewProject(scope.row)">
              <el-icon><View /></el-icon>
              <span>{{ $t('apiTesting.common.view') }}</span>
            </el-button>
            <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteProject(scope.row)">
              <el-icon><Delete /></el-icon>
              <span>{{ $t('apiTesting.common.delete') }}</span>
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

    <!-- 新建/编辑项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? $t('apiTesting.project.editProject') : $t('apiTesting.project.createProject')"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item :label="$t('apiTesting.project.projectName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('apiTesting.project.inputProjectName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.projectDescription')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('apiTesting.project.inputProjectDesc')"
          />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.projectType')" prop="project_type">
          <el-radio-group v-model="form.project_type">
            <el-radio value="HTTP">HTTP</el-radio>
            <el-radio value="WEBSOCKET">WebSocket</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.projectStatus')" prop="status">
          <el-select v-model="form.status" :placeholder="$t('apiTesting.project.selectStatus')">
            <el-option :label="$t('apiTesting.project.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('apiTesting.project.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('apiTesting.project.status.completed')" value="COMPLETED" />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.owner')" prop="owner">
          <el-select v-model="form.owner" :placeholder="$t('apiTesting.project.selectOwner')" filterable>
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.teamMembers')" prop="member_ids">
          <el-select
            v-model="form.member_ids"
            multiple
            :placeholder="$t('apiTesting.project.selectMembers')"
            filterable
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.startDate')" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            :placeholder="$t('apiTesting.project.selectStartDate')"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.endDate')" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            :placeholder="$t('apiTesting.project.selectEndDate')"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingProject ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看项目详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="$t('apiTesting.project.viewProject')"
      width="600px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item :label="$t('apiTesting.project.projectName')">{{ viewedProject?.name }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.projectDescription')">{{ viewedProject?.description || $t('apiTesting.project.none') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.projectType')">
          <span class="status-badge" :class="viewedProject?.project_type === 'HTTP' ? 'http' : 'websocket'">
            {{ viewedProject?.project_type }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.projectStatus')">
          <span class="status-badge" :class="getStatusClass(viewedProject?.status)">
            {{ getStatusText(viewedProject?.status) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.owner')">{{ viewedProject?.owner?.username }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.teamMembers')">
          <div v-if="viewedProject?.members?.length">
            <el-tag
              v-for="member in viewedProject.members"
              :key="member.id"
              size="small"
              style="margin-right: 5px; margin-bottom: 5px;"
            >
              {{ member.username }}
            </el-tag>
          </div>
          <span v-else>{{ $t('apiTesting.project.none') }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.startDate')">{{ viewedProject?.start_date || $t('apiTesting.project.notSet') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.endDate')">{{ viewedProject?.end_date || $t('apiTesting.project.notSet') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.createdAt')">{{ formatDate(viewedProject?.created_at) }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.updatedAt')">{{ formatDate(viewedProject?.updated_at) }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="showViewDialog = false">{{ $t('apiTesting.common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElDescriptions, ElDescriptionsItem } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, Edit, View, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const { t } = useI18n()
const loading = ref(false)
const projects = ref([])
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingProject = ref(null)
const viewedProject = ref(null)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  description: '',
  project_type: 'HTTP',
  status: 'NOT_STARTED',
  owner: null,
  member_ids: [],
  start_date: '',
  end_date: ''
})

const rules = computed(() => ({
  name: [
    { required: true, message: t('apiTesting.project.inputProjectName'), trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: t('apiTesting.common.pleaseSelect'), trigger: 'change' }
  ],
  status: [
    { required: true, message: t('apiTesting.project.selectStatus'), trigger: 'change' }
  ],
  owner: [
    { required: true, message: t('apiTesting.project.selectOwner'), trigger: 'change' }
  ]
}))

const getStatusClass = (status) => {
  const classMap = {
    'NOT_STARTED': 'pending',
    'IN_PROGRESS': 'processing',
    'COMPLETED': 'success'
  }
  return classMap[status] || 'pending'
}

const getStatusTagType = (status) => {
  const typeMap = {
    'NOT_STARTED': 'info',
    'IN_PROGRESS': 'warning',
    'COMPLETED': 'success'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusKey = {
    'NOT_STARTED': 'notStarted',
    'IN_PROGRESS': 'inProgress',
    'COMPLETED': 'completed'
  }[status]
  return statusKey ? t(`apiTesting.project.status.${statusKey}`) : status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await api.get('/api-testing/projects/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    projects.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadProjects'))
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await api.get('/api-testing/users/')
    users.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadUsers'))
    console.error(error)
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadProjects()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadProjects()
}

const editProject = (project) => {
  editingProject.value = project
  form.name = project.name
  form.description = project.description
  form.project_type = project.project_type
  form.status = project.status
  form.owner = project.owner.id
  form.member_ids = project.members.map(m => m.id)
  form.start_date = project.start_date
  form.end_date = project.end_date
  showCreateDialog.value = true
}

const viewProject = (project) => {
  // 显示项目详情弹框
  showViewDialog.value = true
  viewedProject.value = project
}

const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.project.confirmDelete', { name: project.name }),
      t('apiTesting.messages.confirm.deleteTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    await api.delete(`/api-testing/projects/${project.id}/`)
    ElMessage.success(t('apiTesting.messages.success.delete'))
    await loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
      console.error(error)
    }
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const data = { ...form }
    if (data.start_date) {
      data.start_date = dayjs(data.start_date).format('YYYY-MM-DD')
    }
    if (data.end_date) {
      data.end_date = dayjs(data.end_date).format('YYYY-MM-DD')
    }
    
    if (editingProject.value) {
      await api.put(`/api-testing/projects/${editingProject.value.id}/`, data)
      ElMessage.success(t('apiTesting.messages.success.projectUpdated'))
    } else {
      await api.post('/api-testing/projects/', data)
      ElMessage.success(t('apiTesting.messages.success.projectCreated'))
    }

    showCreateDialog.value = false
    await loadProjects()
  } catch (error) {
    ElMessage.error(editingProject.value ? t('apiTesting.messages.error.updateFailed') : t('apiTesting.messages.error.createFailed'))
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingProject.value = null
  Object.assign(form, {
    name: '',
    description: '',
    project_type: 'HTTP',
    status: 'NOT_STARTED',
    owner: null,
    member_ids: [],
    start_date: '',
    end_date: ''
  })
  formRef.value?.resetFields()
}

onMounted(async () => {
  await Promise.all([loadProjects(), loadUsers()])
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

  .page-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #5a32a3;
  }

  .create-btn {
    height: 36px;
    padding: 0 18px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    background: #7b42f6;
    border: 1px solid #7b42f6;
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      background: #6d33e6;
      border-color: #6d33e6;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
    }

    &:active {
      transform: translateY(0);
      background: #5a32a3;
    }

    .el-icon {
      margin-right: 6px;
      font-size: 16px;
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
  padding-top: 16px;
}

.custom-table {
  border: none;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  min-height: 200px;
  box-shadow: none;
  transition: all 0.3s ease;
  background-color: transparent !important;

  /* 覆盖 Element Plus 默认主题变量 */
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
    white-space: nowrap !important;
    line-height: 24px !important;
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
    }

    &.el-table__row--striped {
      background-color: #fafaff !important;
    }
  }

  :deep(td) {
    padding: 14px 16px;
    border-bottom: 1px solid #e9ecef;
    color: #333;
    font-size: 14px;
    font-weight: 400;
    line-height: 24px;
    transition: all 0.3s ease;
    vertical-align: middle;
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

  // 成功 - 绿色
  &.success {
    background: #f6ffed;
    color: #52c41a;
  }

  // 失败 - 红色
  &.failed {
    background: #fff1f0;
    color: #f5222d;
  }

  // 处理中 - 橙色
  &.processing {
    background: #fff7e6;
    color: #fa8c16;
  }

  // 待处理 - 灰色
  &.pending {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  // HTTP - 紫色
  &.http {
    background: #f5f3ff;
    color: #7b42f6;
  }

  // WebSocket - 绿色
  &.websocket {
    background: #f6ffed;
    color: #52c41a;
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

// 操作按钮样式
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
    color: #ffffff !important;
  }

  span {
    font-size: 12px;
    color: #ffffff !important;
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
    background: linear-gradient(135deg, #ff4d4f 0%, #f5222d 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(245, 34, 45, 0.4);
    }
  }
}

// 响应式适配
@media screen and (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .page-header {
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
    padding: 16px 20px;

    .page-title {
      font-size: 18px;
    }

    .create-btn {
      width: auto;
    }
  }

  .card-container {
    padding-top: 12px;
  }

  .custom-table {
    :deep(th) {
      padding: 12px !important;
    }

    :deep(td) {
      padding: 10px 12px;
    }
  }

  .pagination-container {
    padding: 12px 0;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;

      .el-pagination__total,
      .el-pagination__sizes,
      .el-pagination__jump {
        margin: 0;
      }
    }
  }

  .action-buttons {
    flex-wrap: wrap;
    gap: 4px;
  }

  .action-btn {
    padding: 4px 8px !important;

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
    gap: 16px;
  }

  .page-header {
    justify-content: flex-end;
    padding: 14px 16px;

    .page-title {
      font-size: 16px;
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

    // 项目详情描述列表样式
    .el-descriptions {
      .el-descriptions__body {
        background-color: transparent;

        .el-descriptions__table {
          background-color: transparent;

          .el-descriptions__cell {
            background-color: transparent;
          }

          .el-descriptions__label {
            background-color: transparent;
          }

          .el-descriptions__content {
            background-color: transparent;
          }
        }
      }
    }

    .el-form {
      .el-form-item {
        margin-bottom: 20px;

        .el-form-item__label {
          color: #5a32a3;
          font-weight: 500;
        }

        .el-input__wrapper,
        .el-select .el-input__wrapper,
        .el-date-picker .el-input__wrapper {
          box-shadow: none;
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);
          background-color: transparent;

          &:hover,
          &.is-focus {
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
          background-color: transparent;

          &:hover,
          &:focus {
            border-color: #7b42f6;
          }
        }

        // 下拉选择器
        .el-select {
          width: 100%;

          .el-select__wrapper {
            background-color: transparent;
            box-shadow: none;
            border: 1px solid rgba(147, 112, 219, 0.2);
            border-radius: 8px;

            &:hover,
            &.is-focused {
              border-color: #7b42f6;
            }
          }

          .el-select__selection {
            background-color: transparent;
          }
        }

        .el-radio-group {
          .el-radio {
            margin-right: 20px;

            .el-radio__input.is-checked .el-radio__inner {
              background-color: #7b42f6;
              border-color: #7b42f6;
            }

            .el-radio__label {
              color: #5a32a3;
            }
          }
        }
      }
    }
  }

  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid #ebeef5;
    background: #fafafa;

    .el-button {
      font-weight: 500;
      padding: 8px 20px;
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
</style>