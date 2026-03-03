<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('uiAutomation.element.title') }}</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreatePageDialog = true">
          <el-icon><Folder /></el-icon>
          {{ $t('uiAutomation.element.createPage') }}
        </el-button>
        <el-button class="btn-secondary" @click="createEmptyElement">
          <el-icon><Plus /></el-icon>
          {{ $t('uiAutomation.element.addElement') }}
        </el-button>
      </div>
    </div>

    <div class="card-container element-layout">
      <!-- 左侧页面树 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <el-select v-model="selectedProject" :placeholder="$t('common.selectProject')" @change="onProjectChange" class="project-select">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </div>

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
              <div class="tree-node">
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

                <span v-if="data.type === 'element'" class="element-type-tag" :class="data.element_type?.toLowerCase()">
                  {{ getElementTypeLabel(data.element_type) }}
                </span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧元素详情 -->
      <div class="main-content">
        <div v-if="!selectedElement" class="empty-state">
          <el-empty :description="$t('uiAutomation.element.emptyElementTip')">
            <el-button type="primary" @click="createEmptyElement">{{ $t('uiAutomation.element.createNewElement') }}</el-button>
          </el-empty>
        </div>

        <div v-else class="element-detail">
          <!-- 元素基本信息 -->
          <div class="detail-header">
            <h3 class="detail-title">{{ $t('uiAutomation.element.elementDetail') }}</h3>
            <div class="element-info">
              <div class="required-field-wrapper">
                <span class="required-star">*</span>
                <el-input
                  v-model="selectedElement.name"
                  :placeholder="$t('uiAutomation.element.elementNamePlaceholder')"
                  size="small"
                  style="width: 300px; margin-right: 10px"
                />
              </div>
              <div class="required-field-wrapper">
                <span class="required-star">*</span>
                <el-select v-model="selectedElement.element_type" :placeholder="$t('uiAutomation.element.elementType')" size="small" style="width: 120px;">
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
              </div>
              <el-button size="small" type="primary" @click="saveElement" :loading="saving" ref="saveButtonRef">
                {{ $t('uiAutomation.common.save') }}
              </el-button>
            </div>
          </div>

          <!-- 元素配置 -->
          <div class="element-form">
            <el-form :key="formKey" :model="selectedElement" label-width="100px" size="small">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.page')" class="is-required">
                    <el-select v-model="selectedElement.page" :placeholder="$t('uiAutomation.element.selectPage')">
                      <el-option
                        v-for="page in pages"
                        :key="page.id"
                        :label="page.name"
                        :value="page.name"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.componentName')">
                    <el-input v-model="selectedElement.component_name" :placeholder="$t('uiAutomation.element.componentNamePlaceholder')" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.locatorStrategy')" prop="locator_strategy_id" class="is-required">
                    <el-select
                      v-model="selectedElement.locator_strategy_id"
                      :key="`strategy-${formKey}-${selectedElement.locator_strategy_id || 'null'}`"
                      :placeholder="$t('uiAutomation.element.rules.strategyRequired')"
                      value-key="id"
                    >
                      <el-option
                        v-for="strategy in locatorStrategies"
                        :key="strategy.id"
                        :label="strategy.name"
                        :value="strategy.id"
                      />
                    </el-select>
                    <!-- 调试信息 -->
                    <div style="font-size: 10px; color: #666; margin-top: 2px;">
                      {{ $t('uiAutomation.element.debugInfo') }}: {{ $t('uiAutomation.element.currentValue') }}={{selectedElement.locator_strategy_id}} ({{typeof selectedElement.locator_strategy_id}})
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.waitTimeout') + '(' + $t('uiAutomation.element.waitTimeoutUnit') + ')'">
                    <el-input-number v-model="selectedElement.wait_timeout" :min="1" :max="60" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="$t('uiAutomation.element.forceAction')">
                    <el-switch
                      v-model="selectedElement.force_action"
                      :active-text="$t('uiAutomation.element.forceActionEnabled')"
                      :inactive-text="$t('uiAutomation.element.forceActionDisabled')"
                    />
                    <div class="form-help-text" style="margin-top: 5px;">
                      {{ $t('uiAutomation.element.forceActionTip') }}
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item :label="$t('uiAutomation.element.locatorExpression')" prop="locator_value" class="is-required">
                <el-input v-model="selectedElement.locator_value" :placeholder="$t('uiAutomation.element.locatorExpressionPlaceholder')" />
                <div class="form-help-text">
                  {{ $t('uiAutomation.element.locatorTip.title') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.id') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.css') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.xpath') }}<br>
                  - {{ $t('uiAutomation.element.locatorTip.other') }}
                </div>
              </el-form-item>

              <el-form-item :label="$t('uiAutomation.common.description')">
                <el-input v-model="selectedElement.description" type="textarea" :rows="3" :placeholder="$t('uiAutomation.element.descriptionPlaceholder')" />
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, FolderAdd, Document, Search, Edit, Delete,
  Folder, Document as DocumentIcon, Operation, DocumentCopy, ArrowDown
} from '@element-plus/icons-vue'
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

// 右键菜单
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const rightClickedNode = ref(null)

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

.page-header {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(147, 112, 219, 0.1);

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #5a32a3;
    margin: 0;
    background: linear-gradient(135deg, #5a32a3 0%, #7b42f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .header-actions {
    display: flex;
    gap: 12px;

    .el-button {
      border-radius: 8px;
      padding: 10px 20px;
      font-weight: 500;
      transition: all 0.3s ease;

      &.el-button--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
        }

        .el-icon {
          margin-right: 6px;
        }
      }

      &.btn-secondary {
        background: #ffffff;
        border: 1px solid rgba(147, 112, 219, 0.4);
        color: #5a32a3;

        &:hover {
          background: #f8f7ff;
          border-color: #7b42f6;
          color: #7b42f6;
          transform: translateY(-1px);
        }

        .el-icon {
          margin-right: 6px;
        }
      }
    }
  }
}

.card-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
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
  width: 320px;
  border-right: 1px solid rgba(147, 112, 219, 0.15);
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #faf8ff 0%, #f5f3ff 100%);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.15);
  background: #ffffff;

  .project-select {
    width: 100%;

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
}

.page-tree {
  flex: 1;
  overflow-y: auto;
  padding: 16px;

  .custom-tree {
    background: transparent;

    :deep(.el-tree-node__content) {
      height: 40px;
      border-radius: 8px;
      margin-bottom: 4px;
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
  padding: 24px;
  background: #ffffff;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
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
  .detail-header {
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);

    .detail-title {
      font-size: 18px;
      font-weight: 600;
      color: #5a32a3;
      margin: 0 0 16px 0;
    }

    .element-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .required-field-wrapper {
        display: flex;
        align-items: center;
        gap: 4px;

        .required-star {
          color: #f56c6c;
          font-weight: bold;
          font-size: 14px;
        }
      }

      .el-input, .el-select {
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

      .el-button {
        border-radius: 8px;
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border: none;
        padding: 8px 20px;

        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
        }
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
          box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
          border-radius: 8px;

          &:hover, &:focus {
            box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
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
