<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select v-model="selectedProject" :placeholder="$t('common.selectProject')" @change="onProjectChange" class="project-select" style="width: 200px;">
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="showCreatePageDialog = true">
        <el-icon><Folder /></el-icon>
        {{ $t('uiAutomation.element.createPage') }}
      </el-button>
      <el-button class="btn-secondary add-element-btn" @click="createEmptyElement">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.element.addElement') }}
      </el-button>
      <el-button class="btn-secondary import-btn" @click="showImportDialog = true">
        <el-icon><Upload /></el-icon>
        批量导入
      </el-button>
    </div>

    <div class="card-container element-layout">
      <!-- 左侧页面树 -->
      <div class="sidebar">
        <div class="page-tree">
          <el-tree
            ref="treeRef"
            :key="treeKey"
            :data="treeData"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :default-expanded-keys="expandedKeys"
            @node-click="onNodeClick"
            @node-contextmenu="onNodeRightClick"
            @node-expand="onNodeExpand"
            @node-collapse="onNodeCollapse"
            class="custom-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node" @mouseenter="hoveredNode = data" @mouseleave="hoveredNode = null">
                <el-icon v-if="data.type === 'page'" class="node-icon folder-icon">
                  <Folder />
                </el-icon>
                <el-icon v-else class="node-icon element-icon">
                  <Document />
                </el-icon>

                <!-- 页面名称编辑 -->
                <div v-if="data.type === 'page' && editingNodeId === data.id" class="node-edit">
                  <el-input
                    v-model="editingNodeName"
                    size="small"
                    @blur="savePageName"
                    @keyup.enter="savePageName"
                    @keyup.esc="cancelEdit"
                    ref="editInputRef"
                  />
                </div>

                <!-- 普通显示模式 -->
                <span v-else class="node-label">{{ node.label }}</span>



                <!-- 页面操作图标 -->
                <div v-if="data.type === 'page' && hoveredNode?.id === data.id && editingNodeId !== data.id" class="node-actions">
                  <el-tooltip :content="$t('uiAutomation.element.contextMenu.addElement')" placement="top">
                    <el-icon class="action-icon" @click.stop="addElementToPage(data)">
                      <Plus />
                    </el-icon>
                  </el-tooltip>
                  <el-tooltip :content="$t('uiAutomation.element.contextMenu.addSubPage')" placement="top">
                    <el-icon class="action-icon" @click.stop="addSubPageToNode(data)">
                      <FolderAdd />
                    </el-icon>
                  </el-tooltip>
                  <el-tooltip :content="$t('uiAutomation.element.contextMenu.edit')" placement="top">
                    <el-icon class="action-icon" @click.stop="editPageNode(data)">
                      <Edit />
                    </el-icon>
                  </el-tooltip>
                  <el-tooltip :content="$t('uiAutomation.element.contextMenu.delete')" placement="top">
                    <el-icon class="action-icon delete" @click.stop="deletePageNode(data)">
                      <Delete />
                    </el-icon>
                  </el-tooltip>
                </div>

                <!-- 元素操作图标 -->
                <div v-if="data.type === 'element' && hoveredNode?.id === data.id" class="node-actions">
                  <el-tooltip :content="$t('uiAutomation.common.edit')" placement="top">
                    <el-icon class="action-icon" @click.stop="editElementNode(data)">
                      <Edit />
                    </el-icon>
                  </el-tooltip>
                  <el-tooltip :content="$t('uiAutomation.common.delete')" placement="top">
                    <el-icon class="action-icon delete" @click.stop="deleteElementNode(data)">
                      <Delete />
                    </el-icon>
                  </el-tooltip>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧元素详情 -->
      <div class="main-content">
        <div v-if="!selectedElement" class="empty-state">
          <el-empty :description="$t('uiAutomation.element.emptyElementTip')" />
        </div>

        <div v-else class="element-detail">
          <!-- 元素基本信息 -->
          <div class="detail-header">
            <h3 class="detail-title">{{ $t('uiAutomation.element.elementDetail') }}</h3>
            <el-button size="default" type="primary" @click="saveElement" :loading="saving" ref="saveButtonRef">
              {{ $t('uiAutomation.common.save') }}
            </el-button>
          </div>

          <!-- 元素配置 -->
          <div class="element-form">
            <el-form :key="formKey" :model="selectedElement" label-width="120px" size="default">
              <el-form-item :label="$t('uiAutomation.element.page')" class="is-required">
                <el-select v-model="selectedElement.page" :placeholder="$t('uiAutomation.element.selectPage')" style="width: 100%;">
                  <el-option
                    v-for="page in pages"
                    :key="page.id"
                    :label="page.name"
                    :value="page.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.element.elementName')" class="is-required">
                <el-input v-model="selectedElement.name" :placeholder="$t('uiAutomation.element.elementNamePlaceholder')" />
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.element.elementType')" class="is-required">
                <el-select v-model="selectedElement.element_type" :placeholder="$t('uiAutomation.element.elementType')" style="width: 100%;">
                  <el-option :label="$t('uiAutomation.element.elementTypes.button')" value="BUTTON" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.input')" value="INPUT" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.link')" value="LINK" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.dropdown')" value="DROPDOWN" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.checkbox')" value="CHECKBOX" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.radio')" value="RADIO" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.text')" value="TEXT" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.image')" value="IMAGE" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.table')" value="TABLE" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.form')" value="FORM" />
                  <el-option :label="$t('uiAutomation.element.elementTypes.modal')" value="MODAL" />
                </el-select>
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.element.locatorStrategy')" prop="locator_strategy_id" class="is-required">
                <el-select
                  v-model="selectedElement.locator_strategy_id"
                  :key="`strategy-${formKey}-${selectedElement.locator_strategy_id || 'null'}`"
                  :placeholder="$t('uiAutomation.element.rules.strategyRequired')"
                  value-key="id"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="strategy in locatorStrategies"
                    :key="strategy.id"
                    :label="strategy.name"
                    :value="strategy.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item prop="locator_value" class="is-required">
                <template #label>
                  <span>{{ $t('uiAutomation.element.locatorExpression') }}</span>
                  <el-tooltip
              placement="top"
              :content="$t('uiAutomation.element.locatorTip.id') + '；' + $t('uiAutomation.element.locatorTip.css') + '；' + $t('uiAutomation.element.locatorTip.xpath') + '；' + $t('uiAutomation.element.locatorTip.other')"
              :show-after="200"
              popper-class="custom-tooltip"
            >
              <el-icon class="tooltip-icon"><Warning /></el-icon>
            </el-tooltip>
                </template>
                <el-input v-model="selectedElement.locator_value" :placeholder="$t('uiAutomation.element.locatorExpressionPlaceholder')" />
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.element.waitTimeout') + '(' + $t('uiAutomation.element.waitTimeoutUnit') + ')'">
                <el-input-number v-model="selectedElement.wait_timeout" :min="1" :max="60" style="width: 200px" />
              </el-form-item>

              <el-form-item>
                <template #label>
                  <span>{{ $t('uiAutomation.element.forceAction') }}</span>
                  <el-tooltip
                    placement="top"
                    :content="$t('uiAutomation.element.forceActionTip')"
                    :show-after="200"
                    popper-class="custom-tooltip"
                  >
                    <el-icon class="tooltip-icon"><Warning /></el-icon>
                  </el-tooltip>
                </template>
                <div class="force-action-row">
                  <el-switch
                    v-model="selectedElement.force_action"
                    :active-text="$t('uiAutomation.element.forceActionEnabled')"
                    :inactive-text="$t('uiAutomation.element.forceActionDisabled')"
                  />
                </div>
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.element.componentName')">
                <el-input v-model="selectedElement.component_name" :placeholder="$t('uiAutomation.element.componentNamePlaceholder')" />
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.common.description')">
                <el-input v-model="selectedElement.description" type="textarea" :rows="2" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建页面对话框 -->
    <el-dialog v-model="showCreatePageDialog" :title="$t('uiAutomation.element.createPageTitle')" width="500px">
      <el-form ref="pageFormRef" :model="pageForm" :rules="pageRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.element.pageName')" prop="name">
          <el-input v-model="pageForm.name" :placeholder="$t('uiAutomation.element.pageNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.parentPage')">
          <el-select v-model="pageForm.parent_page" :placeholder="$t('uiAutomation.element.selectParentPage')" clearable>
            <el-option
              v-for="page in getAllPages()"
              :key="page.id"
              :label="page.name"
              :value="page.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="pageForm.description" type="textarea" :rows="3" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreatePageDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="createPage">{{ $t('uiAutomation.common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <ul v-show="showContextMenu" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <li @click="addContextElement">{{ $t('uiAutomation.element.contextMenu.addElement') }}</li>
      <li @click="addSubPage">{{ $t('uiAutomation.element.contextMenu.addSubPage') }}</li>
      <li @click="editNode">{{ $t('uiAutomation.element.contextMenu.edit') }}</li>
      <li @click="deleteNode">{{ $t('uiAutomation.element.contextMenu.delete') }}</li>
    </ul>

    <!-- 编辑页面对话框 -->
    <el-dialog v-model="showEditPageDialog" :title="$t('uiAutomation.element.editPageTitle')" width="500px">
      <el-form ref="editPageFormRef" :model="editPageForm" :rules="pageRules" label-width="100px">
        <el-form-item :label="$t('uiAutomation.element.pageName')" prop="name">
          <el-input v-model="editPageForm.name" :placeholder="$t('uiAutomation.element.pageNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.element.parentPage')">
          <el-select v-model="editPageForm.parent_page" :placeholder="$t('uiAutomation.element.selectParentPage')" clearable>
            <el-option
              v-for="page in getAllPagesExceptCurrent(editPageForm.id)"
              :key="page.id"
              :label="page.name"
              :value="page.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="editPageForm.description" type="textarea" :rows="3" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditPageDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="updatePage">{{ $t('uiAutomation.common.save') }}</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showImportDialog" width="800px" @close="resetImportDialog">
      <template #header>
        <div class="dialog-header-with-tooltip">
          <span class="dialog-title">批量导入元素</span>
          <el-tooltip
            effect="dark"
            placement="bottom-start"
            :show-arrow="true"
            popper-class="import-tips-tooltip"
          >
            <template #content>
              <div class="tooltip-content">
                <div class="tooltip-title">导入说明</div>
                <div class="tooltip-item">
                  <span class="tooltip-dot">1.</span>
                  <span>支持 Excel 文件格式（.xlsx, .xls）</span>
                </div>
                <div class="tooltip-item">
                  <span class="tooltip-dot">2.</span>
                  <span><strong>必填字段</strong>：所属页面、元素名称、元素类型、定位策略、定位表达式</span>
                </div>
                <div class="tooltip-item">
                  <span class="tooltip-dot">3.</span>
                  <span>所属页面支持父子页面格式，用 <code>/</code> 分隔（如：首页/登录页）</span>
                </div>
                <div class="tooltip-item">
                  <span class="tooltip-dot">4.</span>
                  <span>如果页面不存在，系统会<strong>自动创建</strong></span>
                </div>
                <div class="tooltip-item">
                  <span class="tooltip-dot">5.</span>
                  <span>元素类型可选值：按钮、输入框、链接、下拉框、复选框、单选框、文本、图片、表格、表单、弹窗</span>
                </div>
              </div>
            </template>
            <el-icon class="header-info-icon"><Warning /></el-icon>
          </el-tooltip>
        </div>
      </template>
      <div class="import-dialog-content">
        <div class="import-actions">
          <el-button class="btn-secondary" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载模板
          </el-button>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
          >
            <el-button class="btn-secondary">
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
          </el-upload>
        </div>

        <div v-if="importFileName" class="import-file-info">
          <el-tag type="info" closable @close="clearImportFile">
            {{ importFileName }}
          </el-tag>
        </div>

        <div v-if="importData.length > 0" class="import-preview">
          <h4>数据预览（共 {{ importData.length }} 条）</h4>
          <el-table :data="importData.slice(0, 10)" border style="width: 100%;">
            <el-table-column prop="page" label="所属页面" width="150" show-overflow-tooltip />
            <el-table-column prop="name" label="元素名称" width="150" show-overflow-tooltip />
            <el-table-column prop="element_type" label="元素类型" width="100" />
            <el-table-column prop="locator_strategy" label="定位策略" width="120" show-overflow-tooltip />
            <el-table-column prop="locator_value" label="定位表达式" show-overflow-tooltip />
          </el-table>
          <div v-if="importData.length > 10" style="text-align: center; margin-top: 8px; color: #9370db; font-size: 13px;">
            仅显示前 10 条数据
          </div>
        </div>

        <div v-if="importErrors.length > 0" class="import-errors">
          <h4>数据验证错误</h4>
          <el-alert type="error">
            <ul>
              <li v-for="(error, index) in importErrors" :key="index">{{ error }}</li>
            </ul>
          </el-alert>
        </div>
      </div>

      <template #footer>
        <el-button class="btn-cancel" @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="executeImport" :loading="importing" :disabled="importData.length === 0 || importErrors.length > 0">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, FolderAdd, Document, Search, Edit, Delete,
  Folder, Document as DocumentIcon, Operation, DocumentCopy, ArrowDown, Warning,
  Upload, Download
} from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import {
  getUiProjects,
  getElements,
  createElement,
  getElementDetail,
  updateElement,
  deleteElement,
  getElementTree,
  getElementGroupTree,
  getElementGroups,
  createElementGroup,
  updateElementGroup,
  deleteElementGroup,
  getLocatorStrategies,
  validateElementLocator,
  generateElementSuggestions
} from '@/api/ui_automation'

// 国际化
const { t } = useI18n()

// 响应式数据
const projects = ref([])
const selectedProject = ref('')
const pages = ref([])
const locatorStrategies = ref([])
const treeData = ref([])
const selectedElement = ref(null)
const expandedKeys = ref([])
const treeKey = ref(0) // 用于强制重新渲染树组件
const formKey = ref(0) // 用于强制重新渲染表单组件

// 表单引用
const treeRef = ref(null)
const pageFormRef = ref(null)
const editPageFormRef = ref(null)

// 对话框控制
const showCreatePageDialog = ref(false)
const showEditPageDialog = ref(false)
const showImportDialog = ref(false)

// 批量导入相关
const uploadRef = ref(null)
const importFileName = ref('')
const importData = ref([])
const importErrors = ref([])
const importing = ref(false)

// 右键菜单
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const rightClickedNode = ref(null)

// 悬停节点
const hoveredNode = ref(null)

// 表单数据
const pageForm = reactive({
  name: '',
  description: '',
  parent_page: null
})

const editPageForm = reactive({
  id: null,
  name: '',
  description: '',
  parent_page: null
})

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'name'
}

// 表单验证规则
const pageRules = computed(() => ({
  name: [
    { required: true, message: t('uiAutomation.element.rules.pageNameRequired'), trigger: 'blur' }
  ]
}))

// 获取元素类型标签
const getElementTypeLabel = (type) => {
  const typeKey = type?.toLowerCase()
  const typeMap = {
    'button': t('uiAutomation.element.elementTypes.button'),
    'input': t('uiAutomation.element.elementTypes.input'),
    'link': t('uiAutomation.element.elementTypes.link'),
    'dropdown': t('uiAutomation.element.elementTypes.dropdown'),
    'checkbox': t('uiAutomation.element.elementTypes.checkbox'),
    'radio': t('uiAutomation.element.elementTypes.radio'),
    'text': t('uiAutomation.element.elementTypes.text'),
    'image': t('uiAutomation.element.elementTypes.image'),
    'table': t('uiAutomation.element.elementTypes.table'),
    'form': t('uiAutomation.element.elementTypes.form'),
    'modal': t('uiAutomation.element.elementTypes.modal')
  }
  return typeMap[typeKey] || type
}

// 获取所有页面
const getAllPages = () => {
  const allPages = []

  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'page') {
        allPages.push({
          id: node.id,
          name: node.name
        })
      }
      if (node.children) {
        traverse(node.children)
      }
    })
  }

  traverse(treeData.value)
  return allPages
}

// 获取所有页面（除了指定ID的页面）
const getAllPagesExceptCurrent = (currentId) => {
  const allPages = []

  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'page' && node.id !== currentId) {
        allPages.push({
          id: node.id,
          name: node.name
        })
      }
      if (node.children) {
        traverse(node.children)
      }
    })
  }

  traverse(treeData.value)
  return allPages
}

// 页面名称编辑相关
const editingNodeId = ref(null)
const editingNodeName = ref('')
const editInputRef = ref(null)

// 状态
const saving = ref(false)
const validating = ref(false)
const generating = ref(false)
const suggestions = ref([])


// 将关键变量暴露到window对象，方便在控制台调试
const exposeToWindow = () => {
  if (typeof window !== 'undefined') {
    window.ELEMENTS_DEBUG = {
      treeData,
      projects,
      selectedElement,
      loadElementTree,
      treeRef: typeof treeRef !== 'undefined' ? treeRef : null,
      expandedKeys,
      pages,
      $vm: { // 当前组件实例
        treeData: treeData.value,
        projects: projects.value,
        pages: pages.value,
        expandedKeys: expandedKeys.value
      }
    }
    console.log('=== Vue组件调试信息已暴露 ===')
    console.log('Window可用调试变量已设置')
    console.log('控制台可直接访问:')
    console.log('  window.ELEMENTS_DEBUG.treeData')
    console.log('  window.ELEMENTS_DEBUG.projects')
    console.log('  window.ELEMENTS_DEBUG.selectedElement')
    console.log('==============================')
  }
}

// 组件挂载
onMounted(async () => {
  console.log('=== 组件挂载开始 ===')

  await loadProjects()
  await loadLocatorStrategies()

  console.log('项目数量:', projects.value.length)
  console.log('定位策略:', locatorStrategies.value.length)

  if (projects.value.length > 0) {
    console.log('设置初始项目为:', projects.value[0].id)
    selectedProject.value = projects.value[0].id
    await onProjectChange()
    console.log('onProjectChange完成')
  }

  // 暴露调试信息
  exposeToWindow()

  console.log('=== 组件挂载完成 ===')
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects()
    projects.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 提供控制台调试帮助函数
const debugTree = () => {
  if (typeof window !== 'undefined') {
    console.log('=== 树数据调试 ===')
    console.log('treeData:', treeData.value)
    console.log('页面对象:',
      treeData.value.map(p => ({
        id: p.id,
        name: p.name,
        type: p.type,
        children: p.children?.length || 0,
        elementChildren: p.children?.filter(c => c.type === 'element').map(e => e.name) || []
      }))
    )

    // 找出所有元素
    const allElements = []
    const findElements = (nodes, parent) => {
      nodes.forEach(node => {
        if (node.type === 'element') {
          allElements.push({
            name: node.name,
            id: node.id,
            parent: parent
          })
        } else if (node.type === 'page' && node.children) {
          findElements(node.children, node.name)
        }
      })
    }
    findElements(treeData.value, null)
    console.log('所有元素:', allElements)

    // 暴露到window
    window.debugTreeData = debugTree
    console.log('调试函数已挂载到 window.debugTreeData()')
    console.log('===============================')
  }
}

// 加载定位策略
const loadLocatorStrategies = async () => {
  try {
    const response = await getLocatorStrategies()
    locatorStrategies.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('获取定位策略失败:', error)
  }
}

// 加载页面（分组）
const loadPages = async () => {
  if (!selectedProject.value) return

  try {
    const response = await getElementGroups({ project: selectedProject.value })
    pages.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('获取页面失败:', error)
  }
}

// 加载页面树结构
const loadPageTree = async () => {
  if (!selectedProject.value) return

  try {
    const response = await getElementGroupTree({ project: selectedProject.value })
    // 构建完整的树形结构
    const buildTree = (groups) => {
      return groups.map(group => ({
        ...group,
        type: 'page',
        children: group.children ? buildTree(group.children) : []
      }))
    }

    const tree = buildTree(response.data || [])
    console.log('页面树结构:', tree)
    treeData.value = tree

    // 加载每个页面下的元素
    await loadElementsForTree()

    // 恢复展开状态
    if (expandedKeys.value.length === 0 && tree.length > 0) {
      expandedKeys.value = tree.map(node => node.id)
    }
  } catch (error) {
    console.error('获取页面树失败:', error)
    treeData.value = []
  }
}

// 为树加载元素数据
const loadElementsForTree = async () => {
  if (!selectedProject.value) return

  try {
    const response = await getElements({ project: selectedProject.value, page_size: 1000 })
    const elements = response.data?.results || response.data || []

    console.log('获取到元素数量:', elements.length)

    // 将元素添加到对应的页面下
    elements.forEach(element => {
      const pageNode = findPageNode(treeData.value, element.page)
      if (pageNode) {
        if (!pageNode.children) {
          pageNode.children = []
        }
        // 检查是否已存在
        const exists = pageNode.children.some(child => child.id === element.id && child.type === 'element')
        if (!exists) {
          pageNode.children.push({
            ...element,
            type: 'element',
            name: element.name
          })
        }
      }
    })

    // 强制刷新树组件
    treeKey.value++

    console.log('元素加载完成，treeData:', treeData.value)
  } catch (error) {
    console.error('获取元素失败:', error)
  }
}

// 在树中查找页面节点
const findPageNode = (nodes, pageName) => {
  for (const node of nodes) {
    if (node.type === 'page' && node.name === pageName) {
      return node
    }
    if (node.children) {
      const found = findPageNode(node.children, pageName)
      if (found) return found
    }
  }
  return null
}

// 加载元素树
const loadElementTree = async () => {
  if (!selectedProject.value) return

  try {
    const response = await getElementTree({ project: selectedProject.value })
    const tree = response.data || []

    // 将元素树合并到页面树中
    tree.forEach(item => {
      if (item.elements && item.elements.length > 0) {
        const pageNode = findPageNode(treeData.value, item.page_name)
        if (pageNode) {
          if (!pageNode.children) {
            pageNode.children = []
          }
          item.elements.forEach(element => {
            const exists = pageNode.children.some(child => child.id === element.id && child.type === 'element')
            if (!exists) {
              pageNode.children.push({
                ...element,
                type: 'element',
                name: element.name
              })
            }
          })
        }
      }
    })

    // 强制刷新树组件
    treeKey.value++
  } catch (error) {
    console.error('获取元素树失败:', error)
  }
}

// 项目切换
const onProjectChange = async () => {
  console.log('项目切换:', selectedProject.value)
  if (!selectedProject.value) {
    treeData.value = []
    selectedElement.value = null
    return
  }

  // 重置展开状态
  expandedKeys.value = []

  await loadPages()
  await loadPageTree()

  // 默认展开所有页面
  const getAllPageIds = (nodes) => {
    const ids = []
    nodes.forEach(node => {
      if (node.type === 'page') {
        ids.push(node.id)
        if (node.children) {
          ids.push(...getAllPageIds(node.children))
        }
      }
    })
    return ids
  }
  expandedKeys.value = getAllPageIds(treeData.value)
  console.log('展开节点:', expandedKeys.value)

  selectedElement.value = null
}

// 节点点击
const onNodeClick = async (data) => {
  if (data.type === 'element') {
    try {
      const response = await getElementDetail(data.id)
      selectedElement.value = response.data
      formKey.value++ // 强制刷新表单
    } catch (error) {
      console.error('获取元素详情失败:', error)
      ElMessage.error('获取元素详情失败')
    }
  }
}

// 节点展开
const onNodeExpand = (data) => {
  if (!expandedKeys.value.includes(data.id)) {
    expandedKeys.value.push(data.id)
  }
}

// 节点折叠
const onNodeCollapse = (data) => {
  const index = expandedKeys.value.indexOf(data.id)
  if (index > -1) {
    expandedKeys.value.splice(index, 1)
  }
}

// 创建空元素
const createEmptyElement = () => {
  selectedElement.value = {
    id: null,
    name: '',
    element_type: 'BUTTON',
    page: pages.value.length > 0 ? pages.value[0].name : '',
    component_name: '',
    locator_value: '',
    locator_strategy_id: null,
    wait_timeout: 10,
    force_action: false,
    description: '',
    project: selectedProject.value
  }
  formKey.value++ // 强制刷新表单
}

// 保存元素
const saveElement = async () => {
  if (!selectedElement.value.name) {
    ElMessage.warning('请输入元素名称')
    return
  }

  if (!selectedElement.value.locator_strategy_id) {
    ElMessage.warning('请选择定位策略')
    return
  }

  if (!selectedElement.value.locator_value) {
    ElMessage.warning('请输入定位表达式')
    return
  }

  saving.value = true
  try {
    // 构建符合后端要求的数据格式
    const elementData = {
      name: selectedElement.value.name,
      element_type: selectedElement.value.element_type,
      page: selectedElement.value.page,
      component_name: selectedElement.value.component_name || '',
      locator_value: selectedElement.value.locator_value,
      locator_strategy_id: selectedElement.value.locator_strategy_id,
      wait_timeout: selectedElement.value.wait_timeout || 10,
      force_action: selectedElement.value.force_action || false,
      description: selectedElement.value.description || '',
      project_id: selectedProject.value
    }

    if (selectedElement.value.id) {
      await updateElement(selectedElement.value.id, elementData)
      ElMessage.success('更新成功')
    } else {
      const response = await createElement(elementData)
      selectedElement.value.id = response.data.id
      ElMessage.success('创建成功')
    }

    // 刷新树
    await loadPageTree()
  } catch (error) {
    console.error('保存元素失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || '保存失败'
    ElMessage.error(`保存失败: ${errorMsg}`)
  } finally {
    saving.value = false
  }
}

// 节点右键点击
const onNodeRightClick = (event, data) => {
  rightClickedNode.value = data
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  showContextMenu.value = true
}

// 添加元素（从右键菜单）
const addContextElement = () => {
  showContextMenu.value = false
  if (rightClickedNode.value) {
    createEmptyElement()
    if (rightClickedNode.value.type === 'page') {
      selectedElement.value.page = rightClickedNode.value.name
    } else if (rightClickedNode.value.type === 'element') {
      // 找到父页面
      const findParentPage = (nodes, targetId) => {
        for (const node of nodes) {
          if (node.children) {
            for (const child of node.children) {
              if (child.id === targetId && child.type === 'element') {
                return node.name
              }
            }
            const result = findParentPage(node.children, targetId)
            if (result) return result
          }
        }
        return null
      }
      const parentPage = findParentPage(treeData.value, rightClickedNode.value.id)
      if (parentPage) {
        selectedElement.value.page = parentPage
      }
    }
  }
}

// 添加子页面
const addSubPage = () => {
  showContextMenu.value = false
  if (rightClickedNode.value && rightClickedNode.value.type === 'page') {
    pageForm.parent_page = rightClickedNode.value.id
    showCreatePageDialog.value = true
  }
}

// 编辑节点
const editNode = () => {
  showContextMenu.value = false
  if (rightClickedNode.value) {
    if (rightClickedNode.value.type === 'page') {
      // 编辑页面
      editPageForm.id = rightClickedNode.value.id
      editPageForm.name = rightClickedNode.value.name
      editPageForm.description = rightClickedNode.value.description || ''
      editPageForm.parent_page = rightClickedNode.value.parent_page
      showEditPageDialog.value = true
    } else {
      // 编辑元素 - 直接加载
      onNodeClick(rightClickedNode.value)
    }
  }
}

// 删除节点
const deleteNode = async () => {
  showContextMenu.value = false
  if (!rightClickedNode.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除${rightClickedNode.value.type === 'page' ? '页面' : '元素'} "${rightClickedNode.value.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )

    if (rightClickedNode.value.type === 'page') {
      await deleteElementGroup(rightClickedNode.value.id)
    } else {
      await deleteElement(rightClickedNode.value.id)
    }

    ElMessage.success('删除成功')
    await loadPageTree()

    // 如果删除的是当前选中的元素，清空选中状态
    if (selectedElement.value && selectedElement.value.id === rightClickedNode.value.id) {
      selectedElement.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 添加元素到指定页面
const addElementToPage = (node) => {
  rightClickedNode.value = node
  addContextElement()
}

// 添加子页面到指定节点
const addSubPageToNode = (node) => {
  rightClickedNode.value = node
  addSubPage()
}

// 编辑页面节点
const editPageNode = (node) => {
  rightClickedNode.value = node
  editNode()
}

// 删除页面节点
const deletePageNode = (node) => {
  rightClickedNode.value = node
  deleteNode()
}

// 编辑元素节点
const editElementNode = (node) => {
  rightClickedNode.value = node
  onNodeClick(node)
}

// 删除元素节点
const deleteElementNode = (node) => {
  rightClickedNode.value = node
  deleteNode()
}

// 创建页面
const createPage = async () => {
  if (!pageForm.name) {
    ElMessage.warning('请输入页面名称')
    return
  }

  try {
    await createElementGroup({
      name: pageForm.name,
      description: pageForm.description,
      parent_group: pageForm.parent_page,
      project: selectedProject.value
    })

    ElMessage.success('创建成功')
    showCreatePageDialog.value = false
    pageForm.name = ''
    pageForm.description = ''
    pageForm.parent_page = null

    await loadPageTree()
  } catch (error) {
    console.error('创建页面失败:', error)
    ElMessage.error('创建失败')
  }
}

// 更新页面
const updatePage = async () => {
  if (!editPageForm.name) {
    ElMessage.warning('请输入页面名称')
    return
  }

  try {
    await updateElementGroup(editPageForm.id, {
      name: editPageForm.name,
      description: editPageForm.description,
      parent_group: editPageForm.parent_page,
      project: selectedProject.value
    })

    ElMessage.success('更新成功')
    showEditPageDialog.value = false

    await loadPageTree()
  } catch (error) {
    console.error('更新页面失败:', error)
    ElMessage.error('更新失败')
  }
}

// 保存页面名称（树内编辑）
const savePageName = async () => {
  if (!editingNodeName.value.trim()) {
    cancelEdit()
    return
  }

  try {
    await updateElementGroup(editingNodeId.value, {
      name: editingNodeName.value,
      project: selectedProject.value
    })

    // 更新本地数据
    const updateNodeName = (nodes) => {
      for (const node of nodes) {
        if (node.id === editingNodeId.value) {
          node.name = editingNodeName.value
          return true
        }
        if (node.children && updateNodeName(node.children)) {
          return true
        }
      }
      return false
    }
    updateNodeName(treeData.value)

    ElMessage.success('更新成功')
  } catch (error) {
    console.error('更新页面名称失败:', error)
    ElMessage.error('更新失败')
  } finally {
    editingNodeId.value = null
    editingNodeName.value = ''
  }
}

// 取消编辑
const cancelEdit = () => {
  editingNodeId.value = null
  editingNodeName.value = ''
}

// 批量导入相关函数
const resetImportDialog = () => {
  importFileName.value = ''
  importData.value = []
  importErrors.value = []
  importing.value = false
}

const clearImportFile = () => {
  importFileName.value = ''
  importData.value = []
  importErrors.value = []
}

const downloadTemplate = () => {
  const templateData = [
    {
      '所属页面': '首页/登录页',
      '元素名称': '登录按钮',
      '元素类型': '按钮',
      '定位策略': 'ID',
      '定位表达式': 'login-btn',
      '等待超时(秒)': 10,
      '强制操作': false,
      '组件名称': '',
      '描述': '登录页面的登录按钮'
    },
    {
      '所属页面': '首页',
      '元素名称': '用户名输入框',
      '元素类型': '输入框',
      '定位策略': 'CSS',
      '定位表达式': '#username',
      '等待超时(秒)': 10,
      '强制操作': false,
      '组件名称': '',
      '描述': ''
    }
  ]

  const ws = XLSX.utils.json_to_sheet(templateData)

  // 设置列宽为原来的3倍（默认约10字符，设置为30字符）
  const colWidths = [
    { wch: 30 },  // 所属页面
    { wch: 30 },  // 元素名称
    { wch: 15 },  // 元素类型
    { wch: 18 },  // 定位策略
    { wch: 36 },  // 定位表达式
    { wch: 18 },  // 等待超时(秒)
    { wch: 15 },  // 强制操作
    { wch: 24 },  // 组件名称
    { wch: 45 }   // 描述
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '元素导入模板')
  XLSX.writeFile(wb, '元素导入模板.xlsx')
}

const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(/** @type {ArrayBuffer} */ (e.target.result))
      const workbook = XLSX.read(data, { type: 'array' })
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
      const jsonData = XLSX.utils.sheet_to_json(firstSheet)

      importFileName.value = file.name
      parseImportData(jsonData)
    } catch (error) {
      console.error('解析Excel文件失败:', error)
      ElMessage.error('解析Excel文件失败，请检查文件格式')
    }
  }
  reader.readAsArrayBuffer(file.raw)
}

const parseImportData = (jsonData) => {
  importData.value = []
  importErrors.value = []

  const validElementTypes = ['BUTTON', 'INPUT', 'LINK', 'DROPDOWN', 'CHECKBOX', 'RADIO', 'TEXT', 'IMAGE', 'TABLE', 'FORM', 'MODAL']

  // 中文元素类型映射到英文
  const elementTypeMapping = {
    '按钮': 'BUTTON',
    '输入框': 'INPUT',
    '链接': 'LINK',
    '下拉框': 'DROPDOWN',
    '复选框': 'CHECKBOX',
    '单选框': 'RADIO',
    '文本': 'TEXT',
    '图片': 'IMAGE',
    '表格': 'TABLE',
    '表单': 'FORM',
    '弹窗': 'MODAL'
  }

  jsonData.forEach((row, index) => {
    const rowNum = index + 2

    const page = row['所属页面'] || row['page'] || ''
    const name = row['元素名称'] || row['name'] || ''
    let elementType = (row['元素类型'] || row['element_type'] || '').toUpperCase()
    const locatorStrategy = row['定位策略'] || row['locator_strategy'] || ''
    const locatorValue = row['定位表达式'] || row['locator_value'] || ''
    const waitTimeout = row['等待超时(秒)'] || row['wait_timeout'] || 10
    const forceAction = row['强制操作'] || row['force_action'] || false
    const componentName = row['组件名称'] || row['component_name'] || ''
    const description = row['描述'] || row['description'] || ''

    // 如果是中文元素类型，转换为英文
    const originalElementType = elementType
    if (elementTypeMapping[elementType]) {
      elementType = elementTypeMapping[elementType]
    }

    if (!page) {
      importErrors.value.push(`第 ${rowNum} 行：所属页面不能为空`)
    }
    if (!name) {
      importErrors.value.push(`第 ${rowNum} 行：元素名称不能为空`)
    }
    if (!elementType) {
      importErrors.value.push(`第 ${rowNum} 行：元素类型不能为空`)
    } else if (!validElementTypes.includes(elementType)) {
      importErrors.value.push(`第 ${rowNum} 行：元素类型 "${originalElementType}" 无效，有效值为：${validElementTypes.join(', ')} 或中文：${Object.keys(elementTypeMapping).join(', ')}`)
    }
    if (!locatorStrategy) {
      importErrors.value.push(`第 ${rowNum} 行：定位策略不能为空`)
    }
    if (!locatorValue) {
      importErrors.value.push(`第 ${rowNum} 行：定位表达式不能为空`)
    }

    importData.value.push({
      page,
      name,
      element_type: elementType,
      locator_strategy: locatorStrategy,
      locator_value: locatorValue,
      wait_timeout: parseInt(waitTimeout) || 10,
      force_action: !!forceAction,
      component_name: componentName,
      description: description
    })
  })
}

const findOrCreatePage = async (pagePath) => {
  const pageNames = pagePath.split('/').filter(p => p.trim())
  let parentId = null
  let currentFullPageName = ''

  for (let i = 0; i < pageNames.length; i++) {
    const pageName = pageNames[i]
    currentFullPageName = pageNames.slice(0, i + 1).join('/')

    let existingPage = null
    
    const findPageByParentAndName = (nodes, targetParentId, targetName) => {
      for (const node of nodes) {
        if (node.type === 'page' && node.name === targetName) {
          const nodeParent = node.parent_group || null
          if (nodeParent === targetParentId) {
            return node
          }
        }
        if (node.children) {
          const found = findPageByParentAndName(node.children, targetParentId, targetName)
          if (found) return found
        }
      }
      return null
    }

    existingPage = findPageByParentAndName(treeData.value, parentId, pageName)

    if (existingPage) {
      parentId = existingPage.id
    } else {
      const response = await createElementGroup({
        name: pageName,
        description: '',
        parent_group: parentId,
        project: selectedProject.value
      })
      parentId = response.data.id
      await loadPageTree()
    }
  }

  return currentFullPageName
}

const executeImport = async () => {
  if (importData.value.length === 0 || importErrors.value.length > 0) {
    return
  }

  importing.value = true
  let successCount = 0
  let failCount = 0

  try {
    for (const item of importData.value) {
      try {
        const pageName = await findOrCreatePage(item.page)

        let strategyId = null
        for (const strategy of locatorStrategies.value) {
          if (strategy.name === item.locator_strategy) {
            strategyId = strategy.id
            break
          }
        }

        if (!strategyId) {
          importErrors.value.push(`元素 "${item.name}"：定位策略 "${item.locator_strategy}" 不存在`)
          failCount++
          continue
        }

        await createElement({
          name: item.name,
          element_type: item.element_type,
          page: pageName,
          component_name: item.component_name || '',
          locator_value: item.locator_value,
          locator_strategy_id: strategyId,
          wait_timeout: item.wait_timeout || 10,
          force_action: item.force_action || false,
          description: item.description || '',
          project_id: selectedProject.value
        })

        successCount++
      } catch (error) {
        console.error('导入元素失败:', error)
        importErrors.value.push(`元素 "${item.name}"：导入失败 - ${error.response?.data?.detail || error.message}`)
        failCount++
      }
    }

    await loadPageTree()

    if (failCount > 0) {
      ElMessage.warning(`导入完成：成功 ${successCount} 条，失败 ${failCount} 条`)
    } else {
      ElMessage.success(`导入成功：共 ${successCount} 条`)
      showImportDialog.value = false
      resetImportDialog()
    }
  } catch (error) {
    console.error('批量导入失败:', error)
    ElMessage.error('批量导入失败')
  } finally {
    importing.value = false
  }
}

// 点击其他地方关闭右键菜单
onMounted(() => {
  document.addEventListener('click', () => {
    showContextMenu.value = false
  })
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
  padding: 16px 20px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 2px;

  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
    box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.25);
    border-radius: 8px;
    background: #ffffff;

    &:hover,
    &:focus {
      box-shadow: 0 0 0 1px #7b42f6;
    }
  }

  :deep(.el-input__inner) {
    color: #5a32a3;
    font-weight: 500;
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

  .add-element-btn,
  .import-btn {
    background: #ffffff !important;
    border: 1px solid rgba(147, 112, 219, 0.4) !important;
    color: #5a32a3 !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;

    .el-icon {
      margin-right: 6px;
    }

    &:hover {
      background: #f8f7ff !important;
      border-color: #7b42f6 !important;
      color: #7b42f6 !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.2) !important;
    }
  }
}

// 对话框标题带提示图标样式
.dialog-header-with-tooltip {
  display: flex;
  align-items: center;
  gap: 12px;

  .dialog-title {
    font-size: 18px;
    font-weight: 600;
    color: #5a32a3;
  }

  .header-info-icon {
    font-size: 20px;
    color: #7b42f6;
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(123, 66, 246, 0.1);
      transform: scale(1.1);
    }
  }
}

// Tooltip 样式 - 紫色渐变风格
:deep(.import-tips-tooltip) {
  background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 20px 24px !important;
  max-width: 520px !important;
  box-shadow: 0 12px 32px rgba(109, 40, 217, 0.4) !important;

  .el-popper__arrow::before {
    background: #8B5CF6 !important;
    border-color: #8B5CF6 !important;
  }

  .tooltip-content {
    color: #ffffff;

    .tooltip-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.25);
      color: #ffffff;
    }

    .tooltip-item {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      margin-bottom: 12px;
      font-size: 14px;
      line-height: 1.7;
      color: rgba(255, 255, 255, 0.95);

      &:last-child {
        margin-bottom: 0;
      }

      .tooltip-dot {
        color: #FCD34D;
        font-weight: 700;
        flex-shrink: 0;
        font-size: 14px;
      }

      strong {
        font-weight: 600;
        color: #FCD34D;
      }

      code {
        background: rgba(255, 255, 255, 0.25);
        color: #FCD34D;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'Monaco', monospace;
        font-size: 13px;
        font-weight: 500;
      }
    }
  }
}

.import-dialog-content {
  .import-tips-collapse {
    margin-bottom: 20px;
    border: none;
    background: transparent;

    :deep(.el-collapse-item__header) {
      background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
      border: 1px solid rgba(147, 112, 219, 0.15);
      border-radius: 12px;
      padding: 16px 20px;
      height: auto;
      line-height: normal;

      &.is-active {
        border-radius: 12px 12px 0 0;
        border-bottom: none;
      }

      .el-collapse-item__arrow {
        color: #7b42f6;
        font-size: 16px;
        font-weight: bold;
      }
    }

    :deep(.el-collapse-item__wrap) {
      background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
      border: 1px solid rgba(147, 112, 219, 0.15);
      border-top: none;
      border-radius: 0 0 12px 12px;
      overflow: hidden;
    }

    :deep(.el-collapse-item__content) {
      padding: 0 20px 20px;
      background: transparent;
    }

    .tips-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(147, 112, 219, 0.1);

      .tips-icon {
        font-size: 20px;
        color: #7b42f6;
      }

      .tips-title {
        font-size: 16px;
        font-weight: 600;
        color: #5a32a3;
      }
    }

    .tips-content {
      .tip-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 10px;

        .tip-dot {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
          color: white;
          font-size: 11px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          margin-top: 1px;
        }

        .tip-text {
          font-size: 13px;
          color: #5a32a3;
          line-height: 1.6;

          strong {
            color: #7b42f6;
            font-weight: 600;
          }

          code {
            background: rgba(123, 66, 246, 0.1);
            color: #7b42f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', monospace;
            font-size: 12px;
          }
        }
      }

      .element-types {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-left: 30px;
        margin-top: 8px;

        .type-tag {
          background: linear-gradient(135deg, #f0edff 0%, #e8e4ff 100%);
          border: 1px solid rgba(123, 66, 246, 0.2);
          color: #5a32a3;
          font-weight: 500;
          transition: all 0.2s ease;

          &:hover {
            background: linear-gradient(135deg, #e8e4ff 0%, #ddd8ff 100%);
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(123, 66, 246, 0.15);
          }
        }
      }
    }
  }

  .import-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;

    .btn-secondary,
    .btn-cancel {
      background: #ffffff !important;
      border: 1px solid rgba(147, 112, 219, 0.4) !important;
      color: #5a32a3 !important;
      font-weight: 500 !important;
      padding: 10px 20px !important;
      border-radius: 8px !important;
      transition: all 0.3s ease !important;

      .el-icon {
        margin-right: 8px;
        font-size: 16px;
      }

      &:hover {
        background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%) !important;
        border-color: #7b42f6 !important;
        color: #7b42f6 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.2) !important;
      }
    }
  }

  .import-file-info {
    margin-bottom: 16px;
  }

  .import-preview {
    margin-top: 20px;

    h4 {
      color: #5a32a3;
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 12px;
    }

    :deep(.el-table) {
      font-size: 13px;

      th {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        color: #5a32a3;
        font-weight: 600;
      }
    }
  }

  .import-errors {
    margin-top: 20px;

    h4 {
      color: #f56c6c;
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 12px;
    }

    ul {
      margin: 0;
      padding-left: 20px;
    }

    li {
      margin-bottom: 6px;
      color: #f56c6c;
    }
  }
}

.card-container {
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid rgba(147, 112, 219, 0.12);
  flex: 1;
  overflow: hidden;
  display: flex;
}

.element-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  border-right: 1px solid rgba(147, 112, 219, 0.15);
  display: flex;
  flex-direction: column;
  background: transparent;
}

.page-tree {
  flex: 1;
  overflow-y: auto;
  padding: 16px 4px;

  .custom-tree {
    background: transparent;

    :deep(.el-tree-node__content) {
      height: 40px;
      border-radius: 8px;
      margin-bottom: 4px;
      padding-left: 4px !important;
      transition: all 0.3s ease;

      &:hover {
        background: rgba(123, 66, 246, 0.08);
      }
    }

    :deep(.el-tree-node.is-current > .el-tree-node__content) {
      background: linear-gradient(135deg, rgba(123, 66, 246, 0.15) 0%, rgba(90, 50, 163, 0.1) 100%);
      border-left: 3px solid #7b42f6;
    }
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 8px;

  .node-icon {
    font-size: 16px;

    &.folder-icon {
      color: #7b42f6;
    }

    &.element-icon {
      color: #9370db;
    }
  }

  .node-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #5a32a3;
    font-weight: 500;
  }

  .node-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;

    .action-icon {
      font-size: 25px;
      padding: 6px;
      border-radius: 6px;
      color: #9370db;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(123, 66, 246, 0.1);
        color: #7b42f6;
        transform: scale(1.1);
      }

      &.delete:hover {
        background: rgba(255, 77, 79, 0.1);
        color: #ff4d4f;
      }
    }
  }
}

.element-type-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f7ff 100%);
  color: #7b42f6;
  border: 1px solid rgba(123, 66, 246, 0.2);
  font-weight: 500;

  &.button { background: linear-gradient(135deg, #e6f7ff 0%, #f0faff 100%); color: #1890ff; }
  &.input { background: linear-gradient(135deg, #f6ffed 0%, #f0ffe6 100%); color: #52c41a; }
  &.link { background: linear-gradient(135deg, #fff7e6 0%, #fffbf0 100%); color: #fa8c16; }
  &.dropdown { background: linear-gradient(135deg, #f9f0ff 0%, #fcf5ff 100%); color: #722ed1; }
  &.checkbox { background: linear-gradient(135deg, #fff0f6 0%, #fff5f8 100%); color: #eb2f96; }
  &.radio { background: linear-gradient(135deg, #f0f5ff 0%, #f5f8ff 100%); color: #2f54eb; }
  &.text { background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%); color: #595959; }
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: transparent;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #ffffff;
  border-radius: 12px;

  :deep(.el-empty__description) {
    color: #9370db;
  }

  .el-button {
    margin-top: 16px;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 8px;
    padding: 10px 24px;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
    }
  }
}

.element-detail {
  background: transparent;
  border-radius: 0;
  padding: 20px;
  border: none;

  .detail-header {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;

    .detail-title {
      font-size: 16px;
      font-weight: 600;
      color: #5a32a3;
      margin: 0;
    }

    .el-button--primary {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
      }
    }
  }
}

.element-form {
  .el-form-item {
    :deep(.el-form-item__label) {
      color: #5a32a3;
      font-weight: 500;
    }

    .el-input, .el-select, .el-input-number {
      :deep(.el-input__wrapper) {
        border-radius: 8px;
        border: 1px solid rgba(147, 112, 219, 0.2);
        box-shadow: none;

        &:hover, &.is-focus {
          border-color: #7b42f6;
          box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
        }
      }
    }

    .el-textarea {
      :deep(.el-textarea__inner) {
        border-radius: 8px;
        border: 1px solid rgba(147, 112, 219, 0.2);

        &:hover, &:focus {
          border-color: #7b42f6;
          box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
        }
      }
    }
  }
}

.form-help-text {
  font-size: 12px;
  color: #9370db;
  margin-top: 8px;
  line-height: 1.6;

  &.compact {
    margin-top: 4px;
    line-height: 1.4;
  }
}

.element-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(.el-form-item__label) {
    color: #5a32a3;
    font-weight: 500;
    padding-right: 8px;
    display: flex;
    align-items: center;
    gap: 6px;

    .tooltip-icon {
      color: #9370db;
      font-size: 14px;
      cursor: help;
      transition: color 0.3s ease;

      &:hover {
        color: #7b42f6;
      }
    }
  }

  // Tooltip 样式覆盖
  :deep(.el-tooltip__popper) {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 16px rgba(123, 66, 246, 0.3) !important;

    .el-tooltip__content {
      color: #ffffff !important;
      font-size: 13px !important;
      line-height: 1.6 !important;
      max-width: 400px;
      word-break: break-all;
    }

    // 箭头样式
    &[data-popper-placement^="top"] .el-popper__arrow::before {
      background: #7b42f6 !important;
      border-color: #7b42f6 !important;
    }

    &[data-popper-placement^="bottom"] .el-popper__arrow::before {
      background: #5a32a3 !important;
      border-color: #5a32a3 !important;
    }
  }

  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    box-shadow: none;

    &:hover,
    &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }

  :deep(.el-textarea__inner) {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);

    &:hover,
    &:focus {
      border-color: #7b42f6;
    }
  }
}

.force-action-row {
  display: flex;
  align-items: center;
  gap: 12px;

  .force-action-tip {
    font-size: 12px;
    color: #9370db;
    white-space: nowrap;
  }
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  z-index: 9999;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.2);
  padding: 8px 0;
  margin: 0;
  list-style: none;
  min-width: 140px;

  li {
    padding: 10px 16px;
    cursor: pointer;
    font-size: 14px;
    color: #5a32a3;
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(135deg, rgba(123, 66, 246, 0.1) 0%, rgba(90, 50, 163, 0.05) 100%);
      color: #7b42f6;
    }
  }
}

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(147, 112, 219, 0.2);

  .el-dialog__header {
    padding: 24px 24px 0;

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
        .el-select .el-input__wrapper {
          box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.25);
          border-radius: 8px;

          &:hover, &:focus {
            box-shadow: 0 0 0 1px #7b42f6;
          }
        }
      }
    }
  }

  .el-dialog__footer {
    padding: 0 24px 24px;

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
          transform: translateY(-1px);
        }
      }
    }
  }
}
</style>
