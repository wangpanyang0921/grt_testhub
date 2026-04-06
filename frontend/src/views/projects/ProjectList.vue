<template>
  <div class="page-container">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        :placeholder="$t('project.searchAiProjectPlaceholder')"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 280px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="statusFilter" :placeholder="$t('project.statusFilter')" clearable @change="handleFilter" style="width: 150px;">
        <el-option :label="$t('project.active')" value="active" />
        <el-option :label="$t('project.paused')" value="paused" />
        <el-option :label="$t('project.completed')" value="completed" />
      </el-select>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="action-btn edit-btn" @click="handleCreateProject">
        <el-icon><Plus /></el-icon>
        <span>{{ $t('project.newAiProject') }}</span>
      </el-button>
    </div>

    <!-- 表格容器 -->
    <div class="card-container">
      <el-table ref="tableRef" :data="projects" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="index" :label="$t('project.serialNumber')" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (currentPage - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="$t('project.aiProjectName')" min-width="300" show-overflow-tooltip header-align="center" align="center" />
        <el-table-column :label="$t('project.status')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="row.status">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="owner.username" :label="$t('project.owner')" width="120" header-align="center" align="center" />
        <el-table-column :label="$t('project.createdAt')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('project.actions')" width="280" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="success" class="action-btn detail-btn" @click="goToProject(row.id)">
                <el-icon><View /></el-icon>
                <span>{{ $t('common.detail') }}</span>
              </el-button>
              <el-button size="small" type="primary" class="action-btn edit-btn" @click="editProject(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('common.edit') }}</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteProject(row)">
                <el-icon><Delete /></el-icon>
                <span>{{ $t('common.delete') }}</span>
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
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 创建/编辑应用对话框 -->
    <el-dialog
      :title="isEdit ? $t('project.editAiProject') : $t('project.createAiProject')"
      v-model="showCreateDialog"
      :close-on-click-modal="false"
      width="600px"
      class="project-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="project-form">
        <el-form-item :label="$t('project.aiProjectName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('project.aiProjectNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('project.aiProjectDescription')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            :placeholder="$t('project.aiProjectDescriptionPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="$t('project.status')" prop="status">
          <el-select v-model="form.status" :placeholder="$t('project.selectStatus')" style="width: 100%;">
            <el-option :label="$t('project.active')" value="active" />
            <el-option :label="$t('project.paused')" value="paused" />
            <el-option :label="$t('project.completed')" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false" class="action-btn cancel-btn">
            <span>{{ $t('common.cancel') }}</span>
          </el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting" class="action-btn edit-btn">
            <span>{{ isEdit ? $t('project.update') : $t('project.create') }}</span>
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onActivated, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, View } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const router = useRouter()
const { t } = useI18n()
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const isEdit = ref(false)
const formRef = ref()
const tableRef = ref(null)

const projects = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const statusFilter = ref('')

const form = reactive({
  id: null,
  name: '',
  description: '',
  status: 'active'
})

const rules = {
  name: [
    { required: true, message: computed(() => t('project.projectNameRequired')), trigger: 'blur' },
    { min: 2, max: 200, message: computed(() => t('project.projectNameLength')), trigger: 'blur' }
  ],
  status: [
    { required: true, message: computed(() => t('project.projectStatusRequired')), trigger: 'change' }
  ]
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      search: searchText.value,
      status: statusFilter.value
    }
    const response = await api.get('/projects/', { params })
    projects.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error(t('project.fetchListFailed'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProjects()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchProjects()
}

const handlePageChange = () => {
  fetchProjects()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchProjects()
}

const goToProject = (id) => {
  router.push(`/ai-generation/projects/${id}`)
}

const handleCreateProject = () => {
  resetForm()
  showCreateDialog.value = true
}

const editProject = (project) => {
  isEdit.value = true
  form.id = project.id
  form.name = project.name
  form.description = project.description
  form.status = project.status
  showCreateDialog.value = true
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.description = ''
  form.status = 'active'
  isEdit.value = false
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/projects/${form.id}/`, form)
          ElMessage.success(t('project.updateSuccess'))
        } else {
          await api.post('/projects/', form)
          ElMessage.success(t('project.createSuccess'))
        }
        showCreateDialog.value = false
        resetForm()
        fetchProjects()
      } catch (error) {
        ElMessage.error(isEdit.value ? t('project.updateFailed') : t('project.createFailed'))
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(t('project.deleteConfirm'), t('common.warning'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    })

    await api.delete(`/projects/${project.id}/`)
    ElMessage.success(t('project.deleteSuccess'))
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('project.deleteFailed'))
    }
  }
}

const getStatusText = (status) => {
  const textMap = {
    active: t('project.active'),
    paused: t('project.paused'),
    completed: t('project.completed'),
    archived: t('project.archived')
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchProjects()
})

// 在页面切换回来时刷新表格布局，修复固定列显示异常问题
onActivated(() => {
  nextTick(() => {
    if (tableRef.value) {
      tableRef.value.doLayout()
    }
  })
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
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
    box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    background: #ffffff;

    &:hover,
    &:focus,
    &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15), 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }

  :deep(.el-input__inner) {
    color: #333;
    font-size: 14px;

    &::placeholder {
      color: #999;
    }
  }

  .filter-bar-spacer {
    flex: 1;
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
  padding: 20px;
}

// 表格样式 - 完全参考 XMindConverter.vue
:deep(.el-table) {
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
}

// 表头样式 - 移到外部确保优先级
:deep(.el-table__header-wrapper) {
  background-color: #ffffff !important;
}

:deep(.el-table__header) {
  background-color: #ffffff !important;
}

:deep(.el-table__header th) {
  background-color: #ffffff !important;
  color: #5a32a3 !important;
  font-weight: 600 !important;
  font-size: 14px;
  border-bottom: 1px solid #e9ecef;
  padding: 0 !important;
  text-align: center;
  transition: all 0.3s ease;

  &:hover {
    background-color: #ffffff !important;
  }
}

:deep(.el-table__header th .cell) {
  background-color: #ffffff !important;
  color: #5a32a3 !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
  line-height: 24px !important;
  padding: 16px !important;
}

// 项目链接
.project-link {
  color: #7b42f6;
  font-weight: 500;
  transition: all 0.3s ease;

  &:hover {
    color: #5a32a3;
    text-decoration: underline;
  }
}

// 状态标签
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;

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

  &.archived {
    background: #f5f5f5;
    color: #666;
  }
}

// 时间文本
.time-text {
  color: #666;
  font-size: 13px;
}

// 操作按钮样式 - 使用 .page-container 作为前缀避免样式冲突
.page-container {
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

      .el-icon,
      span {
        color: #ffffff !important;
      }
    }

    &.detail-btn {
      background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;
      border: none !important;
      color: #ffffff !important;
      font-weight: 600 !important;

      &:hover {
        background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
      }

      .el-icon,
      span {
        color: #ffffff !important;
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

      .el-icon,
      span {
        color: #ffffff !important;
      }
    }

    &.cancel-btn {
      border: 1px solid rgba(147, 112, 219, 0.3) !important;
      color: #5a32a3 !important;
      background: #ffffff !important;

      &:hover {
        border-color: #7b42f6 !important;
        color: #7b42f6 !important;
        background: rgba(123, 66, 246, 0.05) !important;
        transform: translateY(-1px);
      }

      .el-icon,
      span {
        color: #5a32a3 !important;
      }
    }
  }
}

// 分页容器 - 完全参考 XMindConverter.vue
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
      }
    }

    .el-pagination__jump {
      color: #5a32a3;
      font-weight: 500;
      margin-left: 12px;

      .el-input__wrapper {
        border-radius: 8px;
        border: 1px solid rgba(147, 112, 219, 0.2);
        background: #ffffff;
        box-shadow: none;

        &:hover {
          border-color: #7b42f6;
        }
      }

      .el-input__inner {
        color: #5a32a3;
        font-weight: 500;
      }
    }
  }
}

// 对话框样式
:deep(.project-dialog) {
  border-radius: 12px;
  overflow: hidden;

  .el-dialog__header {
    background: linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%);
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);

    .el-dialog__title {
      color: #5a32a3;
      font-weight: 600;
      font-size: 18px;
    }
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid rgba(147, 112, 219, 0.1);

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }
}

// 表单样式
.project-form {
  :deep(.el-form-item__label) {
    color: #5a32a3;
    font-weight: 500;
  }

  :deep(.el-input__wrapper),
  :deep(.el-textarea__inner),
  :deep(.el-select .el-input__wrapper) {
    box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.15);
    background: #ffffff;

    &:hover,
    &:focus,
    &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15), 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }

  :deep(.el-input__inner),
  :deep(.el-textarea__inner) {
    color: #333;
    font-size: 14px;

    &::placeholder {
      color: #999;
    }
  }
}

// 响应式布局
@media (max-width: 1200px) {
  .page-container {
    padding: 16px;
  }

  .filter-bar {
    padding: 16px 20px;
    flex-wrap: wrap;
  }

  .card-container {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;

    .filter-bar {
      padding: 12px 16px;
      flex-direction: column;
      align-items: stretch;

      .filter-bar-spacer {
        display: none;
      }

      .action-btn {
        width: 100%;
        justify-content: center;
      }
    }

    .card-container {
      padding: 12px;
    }

    .action-buttons {
      flex-direction: column;
      gap: 4px;

      .action-btn {
        width: 100%;
        justify-content: center;
      }
    }

    .pagination-container {
      padding: 12px;
    }
  }
}
</style>
