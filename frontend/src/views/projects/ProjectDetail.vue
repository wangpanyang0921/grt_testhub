<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ project?.name }} - {{ $t('menu.aiProjectManagement') }}</h1>
      </div>
    </div>

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 菜单树平铺展示 -->
      <div class="menu-tree-fullwidth">
        <div class="sidebar-header">
          <h3 class="sidebar-title">{{ $t('project.menuList') }}</h3>
          <el-button type="primary" size="small" class="action-btn edit-btn" @click="openMenuDialog()">
            <el-icon><Plus /></el-icon>
            <span>{{ $t('project.addMenu') }}</span>
          </el-button>
        </div>
        <div class="menu-tree-container">
          <el-tree
            v-if="menuTree.length > 0"
            :data="menuTree"
            :props="treeProps"
            node-key="id"
            default-expand-all
            highlight-current
            class="menu-tree"
          >
            <template #default="{ node, data }">
              <div class="menu-tree-node">
                <span class="menu-name">{{ data.name }}</span>
                <div class="menu-actions">
                  <el-button
                    link
                    type="primary"
                    size="small"
                    @click.stop="openMenuDialog(data)"
                    :title="$t('project.addSubMenu')"
                  >
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button
                    link
                    type="primary"
                    size="small"
                    @click.stop="openMenuDialog(null, data)"
                    :title="$t('common.edit')"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button
                    link
                    type="danger"
                    size="small"
                    @click.stop="deleteMenu(data)"
                    :title="$t('common.delete')"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
          <el-empty v-else :description="$t('project.noMenu')" />
        </div>
      </div>
    </div>

    <!-- 菜单编辑对话框 -->
    <el-dialog
      v-model="showMenuDialog"
      :title="isEditMenu ? $t('project.editMenu') : $t('project.addMenu')"
      :close-on-click-modal="false"
      width="500px"
      class="project-dialog"
    >
      <el-form ref="menuFormRef" :model="menuForm" :rules="menuRules" label-width="100px" class="project-form">
        <el-form-item :label="$t('project.menuName')" prop="name">
          <el-input v-model="menuForm.name" :placeholder="$t('project.menuNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('project.menuDescription')" prop="description">
          <el-input
            v-model="menuForm.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('project.menuDescriptionPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="$t('project.parentMenu')" prop="parent">
          <el-tree-select
            v-model="menuForm.parent"
            :data="menuTreeForSelect"
            :props="treeProps"
            node-key="id"
            :placeholder="$t('project.selectParentMenu')"
            clearable
            check-strictly
            class="tree-select"
          />
        </el-form-item>
        <el-form-item :label="$t('project.sortOrder')" prop="sort_order">
          <el-input-number v-model="menuForm.sort_order" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showMenuDialog = false" class="action-btn cancel-btn">
            <span>{{ $t('common.cancel') }}</span>
          </el-button>
          <el-button type="primary" @click="saveMenu" :loading="submitting" class="action-btn edit-btn">
            <span>{{ $t('common.confirm') }}</span>
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const { t } = useI18n()

// 端信息
const project = ref(null)

// 菜单树数据
const menuTree = ref([])

// 树形配置
const treeProps = {
  label: 'name',
  children: 'children'
}

// 对话框相关
const showMenuDialog = ref(false)
const isEditMenu = ref(false)
const currentMenuId = ref(null)
const submitting = ref(false)
const menuFormRef = ref()

const menuForm = reactive({
  name: '',
  description: '',
  parent: null,
  sort_order: 0
})

const menuRules = {
  name: [
    { required: true, message: t('project.menuNameRequired'), trigger: 'blur' },
    { min: 1, max: 100, message: t('project.menuNameLength'), trigger: 'blur' }
  ]
}

// 用于下拉选择的菜单树（排除当前编辑的菜单及其子菜单）
const menuTreeForSelect = computed(() => {
  if (!isEditMenu.value || !currentMenuId.value) {
    return menuTree.value
  }
  // 过滤掉当前编辑的菜单及其子菜单
  return filterMenuTree(menuTree.value, currentMenuId.value)
})

// 递归过滤菜单树
const filterMenuTree = (menus, excludeId) => {
  return menus.filter(menu => {
    if (menu.id === excludeId) {
      return false
    }
    if (menu.children && menu.children.length > 0) {
      menu.children = filterMenuTree(menu.children, excludeId)
    }
    return true
  })
}

// 获取端信息
const fetchProject = async () => {
  try {
    const response = await api.get(`/projects/${route.params.id}/`)
    project.value = response.data
  } catch (error) {
    ElMessage.error(t('project.fetchDetailFailed'))
  }
}

// 获取菜单树
const fetchMenus = async () => {
  try {
    const response = await api.get(`/projects/${route.params.id}/menus/`)
    menuTree.value = response.data
  } catch (error) {
    ElMessage.error(t('project.fetchMenuFailed'))
  }
}

// 打开菜单对话框
const openMenuDialog = (parentMenu = null, menu = null) => {
  if (menu) {
    // 编辑模式
    isEditMenu.value = true
    currentMenuId.value = menu.id
    menuForm.name = menu.name
    menuForm.description = menu.description || ''
    menuForm.parent = menu.parent
    menuForm.sort_order = menu.sort_order || 0
  } else {
    // 新增模式
    isEditMenu.value = false
    currentMenuId.value = null
    menuForm.name = ''
    menuForm.description = ''
    menuForm.parent = parentMenu ? parentMenu.id : null
    menuForm.sort_order = 0
  }
  showMenuDialog.value = true
}

// 保存菜单
const saveMenu = async () => {
  try {
    await menuFormRef.value.validate()
    submitting.value = true

    const data = {
      name: menuForm.name,
      description: menuForm.description,
      parent: menuForm.parent,
      sort_order: menuForm.sort_order
    }

    if (isEditMenu.value) {
      await api.put(`/projects/${route.params.id}/menus/${currentMenuId.value}/update/`, data)
      ElMessage.success(t('project.menuUpdateSuccess'))
    } else {
      await api.post(`/projects/${route.params.id}/menus/create/`, data)
      ElMessage.success(t('project.menuCreateSuccess'))
    }

    showMenuDialog.value = false
    await fetchMenus()
  } catch (error) {
    if (error !== 'validation') {
      ElMessage.error(isEditMenu.value ? t('project.menuUpdateFailed') : t('project.menuCreateFailed'))
    }
  } finally {
    submitting.value = false
  }
}

// 删除菜单
const deleteMenu = async (menu) => {
  try {
    await ElMessageBox.confirm(
      t('project.confirmDeleteMenu', { name: menu.name }),
      t('common.confirm'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    await api.delete(`/projects/${route.params.id}/menus/${menu.id}/delete/`)
    ElMessage.success(t('project.menuDeleteSuccess'))
    
    await fetchMenus()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('project.menuDeleteFailed'))
    }
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchProject()
  fetchMenus()
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
  gap: 20px;
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.12);

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #5a32a3;
    margin: 0;
    background: linear-gradient(135deg, #5a32a3 0%, #7b42f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

// 主体内容区
.main-content {
  flex: 1;
  min-height: 0;
}

// 全宽菜单树
.menu-tree-fullwidth {
  width: 100%;
  height: 100%;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.12);

    .sidebar-title {
      font-size: 16px;
      font-weight: 600;
      color: #5a32a3;
      margin: 0;
    }
  }

  .menu-tree-container {
    flex: 1;
    padding: 16px;
    overflow-y: auto;

    .menu-tree {
      :deep(.el-tree-node__content) {
        height: 40px;
        border-radius: 6px;
        margin-bottom: 4px;

        &:hover {
          background: rgba(123, 66, 246, 0.05);
        }
      }

      :deep(.el-tree-node.is-current > .el-tree-node__content) {
        background: rgba(123, 66, 246, 0.1);
      }

      .menu-tree-node {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex: 1;
        padding-right: 8px;

        .menu-name {
          font-size: 14px;
          color: #333;
          font-weight: 500;
        }

        .menu-actions {
          display: none;
          gap: 4px;
        }
      }

      :deep(.el-tree-node__content:hover) .menu-actions {
        display: flex;
      }
    }
  }
}



// 子菜单区域
.submenu-section {
  margin-top: 32px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #5a32a3;
    margin: 0 0 16px 0;
    padding-left: 10px;
    border-left: 4px solid #7b42f6;
  }
}

// 表格样式
:deep(.data-table) {
  border: none;
  border-radius: 8px;
  overflow: hidden;
  background-color: transparent !important;

  --el-color-primary: #7b42f6;
  --el-border-color: #e9ecef;
  --el-border-color-light: #e9ecef;
  --el-border-color-lighter: #e9ecef;
  --el-fill-color-light: #ffffff;
  --el-fill-color-lighter: #ffffff;
  --el-fill-color-blank: #ffffff;
  --el-text-color-primary: #333;
  --el-text-color-regular: #333;
  --el-text-color-secondary: #666;
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;
  --el-table-stripe-bg-color: #fafaff;

  &::before {
    display: none;
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
    padding: 0 !important;
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
    padding: 16px !important;
  }

  :deep(td) {
    border-bottom: 1px solid #e9ecef;
    padding: 0 !important;
    text-align: center;
    transition: all 0.3s ease;
  }

  :deep(td .cell) {
    color: #333;
    font-size: 14px;
    line-height: 24px !important;
    padding: 16px !important;
  }

  :deep(tr:hover > td) {
    background-color: #f8f7ff !important;
  }

  :deep(.el-table__body-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(.el-table__row) {
    background-color: #ffffff !important;

    &.el-table__row--striped {
      background-color: #fafaff !important;
    }
  }
}

// 按钮样式
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;

  &.edit-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    color: #ffffff;

    &:hover {
      background: linear-gradient(135deg, #6b35e8 0%, #4a2593 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    }
  }

  &.delete-btn {
    background: #ff4d4f;
    border: none;
    color: #ffffff;

    &:hover {
      background: #ff7875;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
    }
  }

  &.cancel-btn {
    background: #ffffff;
    border: 1px solid rgba(147, 112, 219, 0.3);
    color: #5a32a3;

    &:hover {
      border-color: #7b42f6;
      color: #7b42f6;
      background: rgba(123, 66, 246, 0.05);
    }
  }
}

// 对话框样式
:deep(.project-dialog) {
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.12);
    margin-right: 0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: #5a32a3;
    }
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid rgba(147, 112, 219, 0.12);
  }
}

// 表单样式
:deep(.project-form) {
  .el-form-item__label {
    color: #5a32a3;
    font-weight: 500;
  }

  .el-input__wrapper,
  .el-textarea__inner {
    box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.2) inset;

    &:hover {
      box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.4) inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 1px #7b42f6 inset;
    }
  }

  .tree-select {
    width: 100%;
  }
}

// 对话框底部按钮布局
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
