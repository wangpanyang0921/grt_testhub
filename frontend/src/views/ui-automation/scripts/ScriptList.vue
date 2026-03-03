<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('uiAutomation.script.title') }}</h1>
        <el-select v-model="selectedProject" :placeholder="$t('uiAutomation.common.selectProject')" class="project-select" @change="onProjectChange">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </div>
      <el-button type="primary" class="create-btn" @click="goToScriptEditor">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.script.newScript') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="scripts" stripe style="width: 100%">
        <el-table-column type="index" :label="$t('uiAutomation.script.index')" width="80" header-align="center" align="center" />
        <el-table-column :label="$t('uiAutomation.script.projectColumn')" width="160" header-align="center" align="center">
          <template #default="{ row }">
            {{ row.project?.name || $t('uiAutomation.script.unknownProject') }}
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="$t('uiAutomation.script.nameColumn')" min-width="280" show-overflow-tooltip header-align="center" align="center" />
        <el-table-column :label="$t('uiAutomation.script.languageColumn')" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.language === 'python' ? 'success' : 'primary'">
              {{ getLanguageText(row.language) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.script.frameworkColumn')" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.framework === 'playwright' ? 'warning' : 'info'">
              {{ getFrameworkText(row.framework) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="$t('uiAutomation.script.createTimeColumn')" width="170" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.script.operationColumn')" width="260" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" class="action-btn view-btn" @click="viewScript(row)">
                <el-icon><View /></el-icon>
                <span>{{ $t('uiAutomation.script.viewDetail') }}</span>
              </el-button>
              <el-button size="small" class="action-btn edit-btn" @click="editScript(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('uiAutomation.script.edit') }}</span>
              </el-button>
              <el-button size="small" class="action-btn rename-btn" @click="renameScript(row)">
                <el-icon><EditPen /></el-icon>
                <span>{{ $t('uiAutomation.script.rename') }}</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="deleteScript(row)">
                <el-icon><Delete /></el-icon>
                <span>{{ $t('uiAutomation.script.delete') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 查看详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.script.scriptDetail')" width="70%">
      <div v-if="currentScript" class="script-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('uiAutomation.script.scriptName')" :span="2">{{ currentScript.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.project')">{{ currentScript.project?.name || $t('uiAutomation.script.unknownProject') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.language')">{{ getLanguageText(currentScript.language) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.framework')">{{ getFrameworkText(currentScript.framework) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.scriptType')">{{ getScriptTypeText(currentScript.script_type) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.createTime')" :span="2">{{ formatTime(currentScript.created_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.updateTime')" :span="2">{{ formatTime(currentScript.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="script-content">
          <h4>{{ $t('uiAutomation.script.scriptContent') }}</h4>
          <pre class="code-view">{{ currentScript.content || $t('uiAutomation.script.noContent') }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">{{ $t('uiAutomation.script.close') }}</el-button>
        <el-button type="primary" @click="editScript(currentScript)">{{ $t('uiAutomation.script.editScript') }}</el-button>
      </template>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog v-model="showRenameDialog" :title="$t('uiAutomation.script.renameScript')" width="400px">
      <el-form :model="renameForm" label-width="80px">
        <el-form-item :label="$t('uiAutomation.script.newName')">
          <el-input v-model="renameForm.newName" :placeholder="$t('uiAutomation.script.newNamePlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRenameDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmRename">{{ $t('uiAutomation.common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" :title="$t('uiAutomation.script.editScript')" width="80%" :close-on-click-modal="false">
      <div v-if="editingScript" class="script-editor">
        <div class="editor-header">
          <span class="script-name">{{ editingScript.name }}</span>
          <div class="editor-info">
            <el-tag size="small" :type="editingScript.language === 'python' ? 'success' : 'primary'">
              {{ getLanguageText(editingScript.language) }}
            </el-tag>
            <el-tag size="small" :type="editingScript.framework === 'playwright' ? 'warning' : 'info'" style="margin-left: 10px">
              {{ getFrameworkText(editingScript.framework) }}
            </el-tag>
          </div>
        </div>
        <div class="editor-container">
          <textarea
            v-model="editingScript.content"
            class="code-editor"
            :placeholder="$t('uiAutomation.script.scriptEditorPlaceholder')"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="showEditDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="saveEditedScript" :loading="saving">{{ $t('uiAutomation.script.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Delete, EditPen } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import {
  getUiProjects,
  getTestScripts,
  updateTestScript,
  deleteTestScript
} from '@/api/ui_automation'

const router = useRouter()
const { t } = useI18n()

// 响应式数据
const projects = ref([])
const selectedProject = ref('')
const scripts = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框控制
const showDetailDialog = ref(false)
const showRenameDialog = ref(false)
const showEditDialog = ref(false)

// 当前操作的脚本
const currentScript = ref(null)
const editingScript = ref(null)
const saving = ref(false)

// 重命名表单
const renameForm = reactive({
  scriptId: null,
  newName: ''
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.loadProjectsFailed'))
    console.error('获取项目列表失败:', error)
  }
}

// 加载脚本列表
const loadScripts = async () => {
  if (!selectedProject.value) {
    scripts.value = []
    total.value = 0
    return
  }

  try {
    const response = await getTestScripts({
      project: selectedProject.value,
      page: currentPage.value,
      page_size: pageSize.value
    })

    // 处理分页响应
    if (response.data.results) {
      scripts.value = response.data.results
      total.value = response.data.count || 0
    } else {
      scripts.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.loadScriptsFailed'))
    console.error('获取脚本列表失败:', error)
  }
}

// 项目切换
const onProjectChange = async () => {
  currentPage.value = 1
  await loadScripts()
}

// 页面大小改变
const handleSizeChange = async () => {
  currentPage.value = 1
  await loadScripts()
}

// 当前页改变
const handleCurrentChange = async () => {
  await loadScripts()
}

// 跳转到脚本编辑器
const goToScriptEditor = () => {
  router.push('/ui-automation/scripts-enhanced')
}

// 查看脚本详情
const viewScript = (script) => {
  currentScript.value = script
  showDetailDialog.value = true
}

// 编辑脚本
const editScript = (script) => {
  editingScript.value = { ...script }
  showDetailDialog.value = false
  showEditDialog.value = true
}

// 保存编辑的脚本
const saveEditedScript = async () => {
  if (!editingScript.value) return

  try {
    saving.value = true

    await updateTestScript(editingScript.value.id, {
      content: editingScript.value.content
    })

    ElMessage.success(t('uiAutomation.script.messages.saveSuccess'))
    showEditDialog.value = false

    // 重新加载脚本列表
    await loadScripts()
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.saveFailed'))
    console.error('脚本保存失败:', error)
  } finally {
    saving.value = false
  }
}

// 重命名脚本
const renameScript = (script) => {
  renameForm.scriptId = script.id
  renameForm.newName = script.name
  showRenameDialog.value = true
}

// 确认重命名
const confirmRename = async () => {
  if (!renameForm.newName.trim()) {
    ElMessage.warning(t('uiAutomation.script.messages.enterNewName'))
    return
  }

  try {
    await updateTestScript(renameForm.scriptId, {
      name: renameForm.newName
    })

    ElMessage.success(t('uiAutomation.script.messages.renameSuccess'))
    showRenameDialog.value = false

    // 重新加载脚本列表
    await loadScripts()
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.renameFailed'))
    console.error('重命名失败:', error)
  }
}

// 删除脚本
const deleteScript = async (script) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.script.messages.deleteConfirm', { name: script.name }),
      t('uiAutomation.script.messages.confirmDelete'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deleteTestScript(script.id)
    ElMessage.success(t('uiAutomation.script.messages.deleteSuccess'))

    // 重新加载脚本列表
    await loadScripts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('uiAutomation.script.messages.deleteFailed'))
      console.error('删除失败:', error)
    }
  }
}

// 辅助方法
const getScriptTypeText = (type) => {
  const typeMap = {
    'CODE': t('uiAutomation.script.scriptTypes.CODE'),
    'VISUAL': t('uiAutomation.script.scriptTypes.VISUAL'),
    'KEYWORD': t('uiAutomation.script.scriptTypes.KEYWORD')
  }
  return typeMap[type] || type
}

const getLanguageText = (language) => {
  const languageMap = {
    'python': 'Python',
    'javascript': 'JavaScript'
  }
  return languageMap[language] || language || t('uiAutomation.status.unknown')
}

const getFrameworkText = (framework) => {
  const frameworkMap = {
    'playwright': 'Playwright',
    'selenium': 'Selenium'
  }
  return frameworkMap[framework] || framework || t('uiAutomation.status.unknown')
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString()
}

// 组件挂载
onMounted(async () => {
  await loadProjects()

  if (projects.value.length > 0) {
    selectedProject.value = projects.value[0].id
    await loadScripts()
  }
})
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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
}

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
  width: 240px;

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

.create-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;
  transition: all 0.3s ease !important;

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4) !important;
  }

  .el-icon {
    color: #ffffff !important;
    margin-right: 6px;
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

    :deep(.el-table__header) {
      background: linear-gradient(135deg, #f8f7ff 0%, #ede9fe 100%) !important;

      th {
        background: transparent !important;
        color: #5a32a3 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 16px 12px !important;
        border-bottom: 2px solid rgba(147, 112, 219, 0.15) !important;

        .cell {
          color: #5a32a3 !important;
          font-weight: 600 !important;
        }
      }
    }

    :deep(.el-table__row) {
      transition: all 0.3s ease;

      &:hover {
        background-color: #f8f7ff !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.1);
      }

      td {
        padding: 14px 12px !important;
        border-bottom: 1px solid rgba(147, 112, 219, 0.08) !important;
        color: #4a4a4a;
        font-size: 14px;
      }
    }

    :deep(.el-table__empty-block) {
      min-height: 200px;
      background: #fafaff;

      .el-table__empty-text {
        color: #9370db;
        font-size: 14px;
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
    background: linear-gradient(135deg, #409eff 0%, #2c7bd0 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3) !important;
    transition: all 0.3s ease !important;
    white-space: nowrap;

    &:hover {
      background: linear-gradient(135deg, #3a8ee6 0%, #266cb5 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4) !important;
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

  &.rename-btn {
    background: linear-gradient(135deg, #e6a23c 0%, #c77f1a 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(230, 162, 60, 0.3) !important;
    transition: all 0.3s ease !important;
    white-space: nowrap;

    &:hover {
      background: linear-gradient(135deg, #d4942a 0%, #b36f15 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(230, 162, 60, 0.4) !important;
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
    background: linear-gradient(135deg, #f56c6c 0%, #c45656 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3) !important;
    transition: all 0.3s ease !important;
    white-space: nowrap;

    &:hover {
      background: linear-gradient(135deg, #e64c4c 0%, #b34545 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4) !important;
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

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px 24px;
  background: transparent;
  border-top: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.3s ease;
  margin-top: 0;

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

  :deep(.el-pagination) {
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
        opacity: 0.5;
        cursor: not-allowed;
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
          font-weight: 600;
        }

        &.btn-quicknext,
        &.btn-quickprev {
          color: #9370db;

          &:hover {
            color: #7b42f6;
          }
        }
      }
    }

    // 跳转页
    .el-pagination__jump {
      margin-left: 12px;
      color: #5a32a3;
      font-weight: 500;

      .el-input {
        width: 48px;
        margin: 0 8px;

        .el-input__wrapper {
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);
          background: #ffffff;
          box-shadow: none;
          padding: 0 8px;

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

.script-detail {
  padding: 10px;
}

.script-content {
  margin-top: 20px;
}

.script-content h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.code-view {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.script-editor {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #fafafa;
  border-bottom: 1px solid #e6e6e6;
}

.script-name {
  font-weight: bold;
  font-size: 16px;
}

.editor-info {
  display: flex;
  align-items: center;
}

.editor-container {
  flex: 1;
  position: relative;
}

.code-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  tab-size: 2;
}
</style>
