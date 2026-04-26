<template>
  <div class="page-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div class="filter-section">
        <el-select v-model="selectedProject" :placeholder="$t('apiTesting.common.selectProject')" @change="onProjectChange" class="project-select" style="width: 200px;">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索合集名称"
          clearable
          class="search-input"
          style="width: 200px; margin-left: 12px;"
          @input="onSearchInput"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="header-actions">
        <el-button type="primary" class="create-btn" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          <span>创建合集</span>
        </el-button>
      </div>
    </div>

    <!-- 合集列表卡片 -->
    <div class="card-container">
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="10" animated />
      </div>
      
      <div v-else-if="filteredCollectionList.length === 0" class="empty-state">
        <el-empty description="暂无合集数据" />
      </div>

      <div v-else class="collection-table-wrapper">
        <el-table
          :data="filteredCollectionList"
          v-loading="loading"
          style="width: 100%"
          class="custom-table"
        >
          <el-table-column label="序号" width="80" header-align="center" align="center">
            <template #default="{ $index }">
              <span>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column label="合集名称" min-width="200" header-align="center" align="center">
            <template #default="{ row }">
              <span>{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="父级合集" width="150" header-align="center" align="center">
            <template #default="{ row }">
              <span>{{ getParentName(row.parent) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="创建人" width="150" header-align="center" align="center">
            <template #default="{ row }">
              <span>{{ formatCreatedBy(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250" header-align="center" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" class="action-btn edit-btn" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>
                  <span>编辑</span>
                </el-button>
                <el-button size="small" type="warning" class="action-btn move-btn" @click="handleMove(row)">
                  <el-icon><Rank /></el-icon>
                  <span>移动</span>
                </el-button>
                <el-button size="small" type="danger" class="action-btn delete-btn" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 创建/编辑合集对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑合集' : '创建合集'"
      width="500px"
    >
      <el-form :model="collectionForm" label-width="100px">
        <el-form-item label="合集名称" required>
          <el-input v-model="collectionForm.name" placeholder="请输入合集名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="collectionForm.description" type="textarea" placeholder="请输入合集描述" />
        </el-form-item>
        <el-form-item label="父级合集">
          <el-select v-model="collectionForm.parent" clearable placeholder="请选择父级合集" style="width: 100%;">
            <el-option label="无" :value="null" />
            <el-option
              v-for="collection in availableParentCollections"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 移动合集对话框 -->
    <el-dialog
      v-model="showMoveDialog"
      title="移动合集"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前位置">
          <span>{{ currentCollection?.name }}</span>
        </el-form-item>
        <el-form-item label="目标父级">
          <el-select v-model="moveTargetParent" clearable placeholder="请选择目标父级合集" style="width: 100%;">
            <el-option label="根目录" :value="null" />
            <el-option
              v-for="collection in availableMoveTargets"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMove" :loading="moving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Folder, Plus, Edit, Delete, Rank, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const { t } = useI18n()

const loading = ref(false)
const projects = ref([])
const selectedProject = ref('')
const collectionList = ref([])
const flatCollections = ref([])
const searchKeyword = ref('')
const filteredCollectionList = ref([])

// 对话框相关
const showCreateDialog = ref(false)
const showMoveDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const moving = ref(false)
const currentCollection = ref(null)
const moveTargetParent = ref(null)

const collectionForm = ref({
  id: null,
  name: '',
  description: '',
  parent: null
})

// 可用的父级合集（排除自身及其子集）
const availableParentCollections = computed(() => {
  if (!isEdit.value) return flatCollections.value
  return flatCollections.value.filter(c => c.id !== collectionForm.value.id)
})

// 可用的移动目标（排除自身及其子集）
const availableMoveTargets = computed(() => {
  if (!currentCollection.value) return []
  return flatCollections.value.filter(c => {
    // 不能选择自己
    if (c.id === currentCollection.value.id) return false
    // 不能选择自己的子集
    if (isChildOf(c.id, currentCollection.value.id)) return false
    return true
  })
})

// 检查是否为子集
const isChildOf = (childId, parentId) => {
  const child = flatCollections.value.find(c => c.id === childId)
  if (!child) return false
  if (child.parent === parentId) return true
  if (child.parent) return isChildOf(child.parent, parentId)
  return false
}

onMounted(() => {
  loadProjects()
})

const loadProjects = async () => {
  try {
    const res = await api.get('/api-testing/projects/')
    const projectList = res.data.results || res.data || []
    projects.value = projectList
    if (projects.value.length > 0) {
      selectedProject.value = projects.value[0].id
      await loadCollections()
    }
  } catch (error) {
    console.error('Load projects error:', error)
    ElMessage.error('加载项目列表失败')
  }
}

const onProjectChange = () => {
  loadCollections()
}

const loadCollections = async () => {
  if (!selectedProject.value) return

  loading.value = true
  try {
    const res = await api.get('/api-testing/collections/', {
      params: { project: selectedProject.value }
    })
    const collections = res.data.results || res.data || []
    flatCollections.value = collections
    collectionList.value = collections
    filterCollections()
  } catch (error) {
    console.error('Load collections error:', error)
    ElMessage.error('加载合集列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索过滤函数
const filterCollections = () => {
  if (!searchKeyword.value) {
    filteredCollectionList.value = collectionList.value
    return
  }
  const keyword = searchKeyword.value.toLowerCase()
  filteredCollectionList.value = collectionList.value.filter(item =>
    item.name && item.name.toLowerCase().includes(keyword)
  )
}

// 搜索输入事件
const onSearchInput = () => {
  filterCollections()
}

const buildTree = (data) => {
  if (!data || !Array.isArray(data)) return []
  
  const map = {}
  const tree = []
  
  data.forEach(item => {
    if (item && item.id) {
      map[item.id] = { ...item, children: [] }
    }
  })
  
  data.forEach(item => {
    if (!item || !item.id) return
    
    if (item.parent && map[item.parent]) {
      map[item.parent].children.push(map[item.id])
    } else if (!item.parent) {
      tree.push(map[item.id])
    }
  })
  
  return tree
}

const getParentName = (parentId) => {
  if (!parentId) return '根目录'
  const parent = flatCollections.value.find(c => c.id === parentId)
  return parent ? parent.name : '根目录'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCreatedBy = (row) => {
  if (!row) return '-'
  if (row.created_by && row.created_by.username) {
    return row.created_by.username
  }
  return '-'
}

const handleEdit = (row) => {
  isEdit.value = true
  collectionForm.value = {
    id: row.id,
    name: row.name,
    description: row.description || '',
    parent: row.parent
  }
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  if (!collectionForm.value.name.trim()) {
    ElMessage.error('请输入合集名称')
    return
  }

  submitting.value = true
  try {
    const data = {
      name: collectionForm.value.name.trim(),
      description: collectionForm.value.description,
      parent: collectionForm.value.parent || null,
      project: selectedProject.value
    }

    if (isEdit.value) {
      await api.put(`/api-testing/collections/${collectionForm.value.id}/`, data)
      ElMessage.success('合集更新成功')
    } else {
      await api.post('/api-testing/collections/', data)
      ElMessage.success('合集创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    await loadCollections()
  } catch (error) {
    console.error('Submit error:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除合集"${row.name}"吗？删除后该合集中的接口将变为未分类状态。`,
      '确认删除',
      { type: 'warning' }
    )

    await api.delete(`/api-testing/collections/${row.id}/`)
    ElMessage.success('合集删除成功')
    await loadCollections()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleMove = (row) => {
  currentCollection.value = row
  moveTargetParent.value = row.parent
  showMoveDialog.value = true
}

const confirmMove = async () => {
  if (!currentCollection.value) return

  moving.value = true
  try {
    const data = {
      name: currentCollection.value.name,
      description: currentCollection.value.description,
      parent: moveTargetParent.value,
      project: selectedProject.value
    }

    await api.put(`/api-testing/collections/${currentCollection.value.id}/`, data)
    ElMessage.success('合集移动成功')
    showMoveDialog.value = false
    currentCollection.value = null
    moveTargetParent.value = null
    await loadCollections()
  } catch (error) {
    console.error('Move error:', error)
    ElMessage.error(error.response?.data?.detail || '移动失败')
  } finally {
    moving.value = false
  }
}

const resetForm = () => {
  collectionForm.value = {
    id: null,
    name: '',
    description: '',
    parent: null
  }
  isEdit.value = false
}
</script>

<style scoped lang="scss">
.page-container {
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

  .filter-section {
    display: flex;
    align-items: center;
    gap: 12px;

    // 覆盖全局的紫色背景变量
    --el-fill-color-blank: #ffffff;

    :deep(.el-input__wrapper),
    :deep(.el-select .el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff !important;
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

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }

    .project-select {
      :deep(.el-input__wrapper) {
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

      :deep(.el-input__inner) {
        color: #5a32a3;
        font-weight: 500;
      }
    }

    .search-input {
      :deep(.el-input__wrapper) {
        border-radius: 8px;
        border: 1px solid rgba(147, 112, 219, 0.2);
        background: #ffffff !important;
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

      :deep(.el-input__inner) {
        color: #5a32a3;
        font-weight: 500;
      }

      :deep(.el-input__prefix) {
        color: #7b42f6;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 8px;
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

.loading-state {
  padding: 40px;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collection-table-wrapper {
  padding: 0 20px 20px;
  height: 100%;
}

// 自定义表格样式
.custom-table {
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
  --el-fill-color-blank: #ffffff;

  :deep(.el-table__inner-wrapper) {
    background-color: transparent !important;
  }

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
    font-weight: 600;
    color: #5a32a3;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  :deep(.el-table__body-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(tr) {
    transition: all 0.3s ease;
    cursor: pointer;
    background-color: #ffffff !important;

    &:hover {
      background-color: #f8f7ff !important;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(123, 66, 246, 0.1);
    }
  }

  :deep(td) {
    padding: 12px 16px;
    border-bottom: 1px solid #e9ecef;
    color: #333;
    font-size: 14px;
    font-weight: 400;
    line-height: 24px;
    transition: all 0.3s ease;
    vertical-align: middle;
    text-align: center;
    background-color: transparent !important;

    .cell {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 24px;
    }
  }

  :deep(.el-table__empty-block) {
    background-color: #ffffff !important;
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

  // 第一列单元格居中对齐
  :deep(td:first-child .cell) {
    padding-left: 8px !important;
    padding-right: 8px !important;
    text-align: center !important;
  }

  // 第一列表头居中对齐
  :deep(th:first-child .cell) {
    justify-content: center !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
  }
}

.collection-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;

  .folder-icon {
    color: #e6a23c;
    font-size: 18px;
  }

  span {
    color: #5a32a3;
    font-weight: 500;
  }
}

.description-text {
  color: #666;
  display: block;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

  &.move-btn {
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

// 按钮样式
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
  }
}

.batch-delete-btn {
  height: 36px;
  padding: 0 18px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: #ff4d4f;
  border: 1px solid #ff4d4f;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);

  &:hover {
    background: #f5222d;
    border-color: #f5222d;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 77, 79, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
}

// 对话框样式
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;

  .el-dialog__header {
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);

    .el-dialog__title {
      color: #5a32a3;
      font-weight: 600;
      font-size: 16px;
    }
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid rgba(147, 112, 219, 0.1);
  }
}

:deep(.el-form-item__label) {
  color: #5a32a3;
  font-weight: 500;
}

// 对话框中的输入框样式 - 覆盖所有输入框
:deep(.el-dialog .el-input__wrapper),
:deep(.el-dialog .el-select .el-input__wrapper),
:deep(.el-dialog .el-select-v2 .el-input__wrapper),
:deep(.el-dialog .el-select .el-select__wrapper) {
  background-color: #ffffff !important;
  background: #ffffff !important;
  --el-input-bg-color: #ffffff !important;
  --el-fill-color-blank: #ffffff !important;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;

  &:hover {
    box-shadow: 0 0 0 1px #7b42f6 inset;
  }

  &.is-focus {
    box-shadow: 0 0 0 1px #7b42f6 inset;
  }
}

// 选择框内部输入框
:deep(.el-dialog .el-select .el-input__inner) {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

// 下拉选择框弹出菜单背景 - 全局生效
:deep(.el-select-dropdown),
:global(.el-select-dropdown) {
  background-color: #ffffff !important;
}

// 下拉选项背景
:deep(.el-select-dropdown__item),
:global(.el-select-dropdown__item) {
  background-color: #ffffff !important;

  &:hover {
    background-color: #f5f3ff !important;
  }

  &.selected {
    background-color: #ede9fe !important;
  }
}

// 下拉菜单内部容器
:deep(.el-select-dropdown__wrap),
:global(.el-select-dropdown__wrap) {
  background-color: #ffffff !important;
}

// 下拉菜单列表
:deep(.el-select-dropdown__list),
:global(.el-select-dropdown__list) {
  background-color: #ffffff !important;
}

// 对话框中的 textarea 背景
:deep(.el-dialog .el-textarea__inner) {
  background-color: #ffffff !important;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;

  &:hover {
    box-shadow: 0 0 0 1px #7b42f6 inset;
  }

  &.is-focus {
    box-shadow: 0 0 0 1px #7b42f6 inset;
  }
}
</style>