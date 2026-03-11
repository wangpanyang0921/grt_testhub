<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select v-model="selectedProject" :placeholder="$t('uiAutomation.common.selectProject')" class="project-select" @change="onProjectChange">
        <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
      </el-select>
      <el-input
        v-model="searchQuery"
        placeholder="搜索脚本名称"
        clearable
        @clear="handleSearch"
        @keydown="($event) => { if ($event.key === 'Enter') handleSearch() }"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="goToScriptEditor">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.script.newScript') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="scripts" v-loading="loading" stripe style="width: 100%" class="script-table">
        <el-table-column type="index" label="序号" width="60" header-align="center" align="center">
          <template #default="{ $index }">
            {{ $index + 1 + (currentPage - 1) * pageSize }}
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="$t('uiAutomation.script.nameColumn')" min-width="280" show-overflow-tooltip header-align="center" align="center">
          <template #default="{ row }">
            <span class="script-name-cell" @click="viewScript(row)">
              {{ row.name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.script.languageColumn')" width="110" header-align="center" align="center">
          <template #default="{ row }">
            <span class="lang-badge" :class="row.language === 'python' ? 'python-badge' : 'js-badge'">
              {{ getLanguageText(row.language) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.script.frameworkColumn')" width="140" header-align="center" align="center">
          <template #default="{ row }">
            <span class="framework-badge" :class="row.framework === 'playwright' ? 'playwright-badge' : 'selenium-badge'">
              {{ getFrameworkText(row.framework) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="$t('uiAutomation.script.createTimeColumn')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.script.operationColumn')" width="260" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="success" class="action-btn view-btn" @click="viewScript(row)">
                <el-icon><View /></el-icon>
                <span>详情</span>
              </el-button>
              <el-button size="small" class="action-btn edit-btn" @click="editScript(row)">
                <el-icon><Edit /></el-icon>
                <span>{{ $t('uiAutomation.script.edit') }}</span>
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
    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.script.scriptDetail')" width="70%" class="custom-dialog">
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
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false" class="btn-cancel">{{ $t('uiAutomation.script.close') }}</el-button>
          <el-button type="primary" @click="editScript(currentScript)" class="btn-confirm">{{ $t('uiAutomation.script.editScript') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog v-model="showRenameDialog" :title="$t('uiAutomation.script.renameScript')" width="400px" class="custom-dialog">
      <el-form :model="renameForm" label-width="80px">
        <el-form-item :label="$t('uiAutomation.script.newName')">
          <el-input v-model="renameForm.newName" :placeholder="$t('uiAutomation.script.newNamePlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRenameDialog = false" class="btn-cancel">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="confirmRename" class="btn-confirm">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" :title="$t('uiAutomation.script.editScript')" width="80%" :close-on-click-modal="false" class="custom-dialog">
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
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false" class="btn-cancel">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="saveEditedScript" :loading="saving" class="btn-confirm">{{ $t('uiAutomation.script.save') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, EditPen, Delete, Search } from '@element-plus/icons-vue'
import { getUiProjects, getTestScripts, updateTestScript, deleteTestScript } from '@/api/ui_automation'

const { t } = useI18n()
const router = useRouter()

// 数据
const projects = ref([])
const selectedProject = ref('')
const scripts = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const selectedIds = ref([])

// 对话框控制
const showDetailDialog = ref(false)
const showRenameDialog = ref(false)
const showEditDialog = ref(false)
const currentScript = ref(null)
const renameForm = ref({ newName: '' })
const editingScript = ref(null)
const saving = ref(false)

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load projects:', error)
    ElMessage.error(t('uiAutomation.script.loadProjectsFailed'))
  }
}

// 加载脚本列表
const loadScripts = async () => {
  if (!selectedProject.value) {
    scripts.value = []
    return
  }

  loading.value = true
  try {
    const params = {
      project: selectedProject.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await getTestScripts(params)
    scripts.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    console.error('Failed to load scripts:', error)
    ElMessage.error(t('uiAutomation.script.loadScriptsFailed'))
  } finally {
    loading.value = false
  }
}

// 项目切换
const onProjectChange = () => {
  currentPage.value = 1
  loadScripts()
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadScripts()
}

// 重置查询
const resetQuery = () => {
  searchQuery.value = ''
  currentPage.value = 1
  loadScripts()
}

// 多选变化
const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

// 分页
const handleSizeChange = (val) => {
  pageSize.value = val
  loadScripts()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadScripts()
}

// 跳转到脚本编辑器
const goToScriptEditor = () => {
  router.push({ name: 'UiScriptEditor' })
}

// 查看脚本详情
const viewScript = (row) => {
  currentScript.value = row
  showDetailDialog.value = true
}

// 编辑脚本
const editScript = (row) => {
  editingScript.value = JSON.parse(JSON.stringify(row))
  showEditDialog.value = true
}

// 保存编辑的脚本
const saveEditedScript = async () => {
  if (!editingScript.value.content.trim()) {
    ElMessage.warning('脚本内容不能为空')
    return
  }

  saving.value = true
  try {
    await updateTestScript(editingScript.value.id, {
      content: editingScript.value.content
    })
    ElMessage.success('脚本保存成功')
    showEditDialog.value = false
    loadScripts()
  } catch (error) {
    console.error('Failed to save script:', error)
    ElMessage.error('脚本保存失败')
  } finally {
    saving.value = false
  }
}

// 重命名脚本
const renameScript = (row) => {
  renameForm.value.newName = row.name
  currentScript.value = row
  showRenameDialog.value = true
}

// 确认重命名
const confirmRename = async () => {
  if (!renameForm.value.newName.trim()) {
    ElMessage.warning(t('uiAutomation.script.emptyName'))
    return
  }

  try {
    await updateTestScript(currentScript.value.id, {
      name: renameForm.value.newName.trim()
    })
    ElMessage.success(t('uiAutomation.script.renameSuccess'))
    showRenameDialog.value = false
    loadScripts()
  } catch (error) {
    console.error('Failed to rename script:', error)
    ElMessage.error(t('uiAutomation.script.renameFailed'))
  }
}

// 删除脚本
const deleteScript = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除脚本 "${row.name}" 吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteTestScript(row.id)
    ElMessage.success('脚本删除成功')
    loadScripts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete script:', error)
      ElMessage.error('脚本删除失败')
    }
  }
}

// 获取语言文本
const getLanguageText = (language) => {
  const languageMap = {
    'javascript': 'JavaScript',
    'python': 'Python'
  }
  return languageMap[language] || language || t('uiAutomation.status.unknown')
}

// 获取框架文本
const getFrameworkText = (framework) => {
  const frameworkMap = {
    'playwright': 'Playwright',
    'selenium': 'Selenium'
  }
  return frameworkMap[framework] || framework || t('uiAutomation.status.unknown')
}

// 获取脚本类型文本
const getScriptTypeText = (scriptType) => {
  const typeMap = {
    'CODE': t('uiAutomation.script.codeScript'),
    'RECORD': t('uiAutomation.script.recordScript')
  }
  return typeMap[scriptType] || scriptType || t('uiAutomation.status.unknown')
}

// 格式化时间
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

  .filter-bar-spacer {
    flex: 1;
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

  .script-table {
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

    // 行悬停效果
    :deep(.el-table__row:hover) {
      background-color: #f8f7ff !important;
    }

    // 脚本名称样式
    .script-name-cell {
      padding: 4px 8px;
      line-height: 1.6;
      color: #595959;
      cursor: pointer;
      transition: color 0.3s ease;

      &:hover {
        color: #7b42f6;
      }
    }

    // 语言徽章样式
    .lang-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 16px;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.3s ease;
      white-space: nowrap;

      &.python-badge {
        background: #e6f7ff;
        color: #1890ff;
      }

      &.js-badge {
        background: #fff7e6;
        color: #fa8c16;
      }
    }

    // 框架徽章样式
    .framework-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 16px;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.3s ease;
      white-space: nowrap;

      &.playwright-badge {
        background: #f6ffed;
        color: #52c41a;
      }

      &.selenium-badge {
        background: #fff2f0;
        color: #ff4d4f;
      }
    }

    // 操作按钮组
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

        &.view-btn {
          background: linear-gradient(135deg, #67c23a 0%, #529b2d 100%) !important;
          border: none !important;
          color: #ffffff !important;
          font-weight: 600 !important;

          &:hover {
            background: linear-gradient(135deg, #85ce61 0%, #6eb34e 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
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

        &.rename-btn {
          background: linear-gradient(135deg, #e6a23c 0%, #c77f1a 100%) !important;
          border: none !important;
          color: #ffffff !important;
          font-weight: 600 !important;

          &:hover {
            background: linear-gradient(135deg, #d4942a 0%, #b36f15 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(230, 162, 60, 0.4);
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
}

// 脚本详情
.script-detail {
  padding: 10px;
}

.script-content {
  margin-top: 20px;

  h4 {
    margin: 0 0 10px 0;
    color: #5a32a3;
    font-weight: 600;
  }
}

.code-view {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 8px;
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
  padding: 12px 16px;
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
  border-bottom: 1px solid rgba(147, 112, 219, 0.15);
  border-radius: 8px 8px 0 0;
}

.script-name {
  font-weight: 600;
  font-size: 16px;
  color: #5a32a3;
}

.editor-info {
  display: flex;
  align-items: center;
}

.editor-container {
  flex: 1;
  position: relative;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.code-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  padding: 16px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  tab-size: 2;
}

// 统一弹窗样式
.custom-dialog {
  :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);
    padding: 20px 24px;
    margin-right: 0;

    .el-dialog__title {
      font-weight: 600;
      color: #5a32a3;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid rgba(147, 112, 219, 0.15);
    padding: 16px 24px;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .btn-cancel {
      border-radius: 6px;
      border: 1px solid rgba(147, 112, 219, 0.4);
      color: #5a32a3;

      &:hover {
        background: #f8f7ff;
        border-color: #7b42f6;
      }
    }

    .btn-confirm {
      border-radius: 6px;
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
      }
    }
  }
}
</style>