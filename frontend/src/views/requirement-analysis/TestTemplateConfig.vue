<template>
  <div class="test-template-config">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>测试模板配置</h2>
        <p class="subtitle">配置测试用例生成的模板，让系统更好地理解您的业务需求</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd" :icon="Plus">
          新建模板
        </el-button>
        <el-button @click="handleInitEducationTemplates" :icon="Collection" :loading="initLoading">
          初始化职业教育模板
        </el-button>
        <el-button @click="handleTestMatch" :icon="Search">
          测试匹配
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">模板总数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-number">{{ stats.active }}</div>
          <div class="stat-label">已启用</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-number">{{ stats.testPoint }}</div>
          <div class="stat-label">测试点模板</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-number">{{ stats.moduleCategories }}</div>
          <div class="stat-label">业务模块</div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索模板名称、关键词或模块"
        class="search-input"
        clearable
        @clear="loadTemplates"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="filterType" placeholder="模板类型" clearable @change="loadTemplates" class="filter-select">
        <el-option
          v-for="type in templateTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
      <el-select v-model="filterModule" placeholder="业务模块" clearable @change="loadTemplates" class="filter-select">
        <el-option
          v-for="module in moduleCategories"
          :key="module"
          :label="module"
          :value="module"
        />
      </el-select>
      <el-select v-model="filterActive" placeholder="启用状态" clearable @change="loadTemplates" class="filter-select">
        <el-option label="已启用" :value="true" />
        <el-option label="已禁用" :value="false" />
      </el-select>
    </div>

    <!-- 模板列表 -->
    <div class="card-container history-card">
      <el-table :data="templates" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="84" header-align="center" align="center" />
        <el-table-column prop="name" label="模板名称" min-width="150" show-overflow-tooltip header-align="center" />
        <el-table-column prop="template_type_display" label="类型" width="140" header-align="center" align="center" />
        <el-table-column prop="module_category" label="业务模块" width="115" header-align="center" align="center" />
        <el-table-column prop="keywords_list" label="匹配关键词" width="240" header-align="center">
          <template #default="{ row }">
            <el-tooltip
              :content="row.keywords_list.join(', ')"
              placement="top"
              :disabled="row.keywords_list.length <= 3"
            >
              <div class="keywords-cell">
                <el-tag
                  v-for="(keyword, index) in row.keywords_list.slice(0, 3)"
                  :key="keyword"
                  size="small"
                  class="keyword-tag"
                >
                  {{ keyword }}
                </el-tag>
                <el-tag
                  v-if="row.keywords_list.length > 3"
                  size="small"
                  class="keyword-tag more-tag"
                >
                  +{{ row.keywords_list.length - 3 }}
                </el-tag>
              </div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="success" class="action-btn detail-btn" @click="handleViewDetail(row)">
                <el-icon><View /></el-icon>
                <span>详情</span>
              </el-button>
              <el-button size="small" type="primary" class="action-btn edit-btn" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
              </el-button>
              <el-button size="small" type="danger" class="action-btn delete-btn" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTemplates"
          @current-change="loadTemplates"
        />
      </div>
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模板' : '新建模板'"
      width="900px"
      destroy-on-close
      :close-on-click-modal="false"
      class="template-dialog"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="115px"
        class="template-form"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" placeholder="如：课程管理测试点" />
        </el-form-item>

        <el-form-item label="模板类型" prop="template_type">
          <el-select v-model="form.template_type" placeholder="选择模板类型" style="width: 100%;">
            <el-option
              v-for="type in templateTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            >
              <div style="display: flex; flex-direction: column;">
                <span>{{ type.label }}</span>
                <span style="font-size: 12px; color: #999;">{{ type.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="业务模块" prop="module_category">
          <el-select
            v-model="form.module_category"
            placeholder="选择或输入业务模块"
            filterable
            allow-create
            style="width: 100%;"
          >
            <el-option
              v-for="module in moduleCategories"
              :key="module"
              :label="module"
              :value="module"
            />
          </el-select>
        </el-form-item>

        <el-form-item prop="keywords">
          <template #label>
            <div class="custom-label">
              <span>匹配关键词</span>
              <el-tooltip
                content="关键词用逗号分隔，系统会匹配需求文档中的内容"
                placement="top"
                effect="light"
                :show-after="100"
              >
                <span class="label-tip-icon">
                  <el-icon><Info-Filled /></el-icon>
                </span>
              </el-tooltip>
            </div>
          </template>
          <el-input
            v-model="form.keywords"
            type="textarea"
            :rows="2"
            placeholder="用逗号分隔关键词，如：课程,课时,章节,课件&#10;需求文档中包含这些词时会匹配此模板"
          />
        </el-form-item>

        <el-form-item prop="content" class="content-form-item">
          <template #label>
            <div class="custom-label">
              <span>模板内容</span>
              <el-tooltip
                :content="getContentTip()"
                placement="top"
                effect="light"
                :show-after="100"
              >
                <span class="label-tip-icon">
                  <el-icon><Info-Filled /></el-icon>
                </span>
              </el-tooltip>
            </div>
          </template>
          <div class="content-wrapper">
            <!-- 未选择模板类型时显示提示 -->
            <div v-if="!form.template_type" class="content-empty-tip">
              <el-icon><Info-Filled /></el-icon>
              <span>请先选择模板类型</span>
            </div>

            <!-- 测试点/场景类型 - 使用标签式输入 -->
            <div v-else-if="form.template_type === 'test_point' || form.template_type === 'test_scenario'" class="content-tags-wrapper">
              <div class="content-tags-header">
                <span class="content-tags-title">已添加 {{ contentList.length }} 项</span>
                <el-button type="primary" link size="small" class="add-item-btn" @click="addContentItem">
                  <el-icon><Plus /></el-icon>
                  添加一项
                </el-button>
              </div>
              <div class="content-tags-list" ref="contentTagsListRef">
                <div
                  v-for="(item, index) in contentList"
                  :key="index"
                  class="content-tag-item"
                  :ref="el => { if (el) contentTagRefs[index] = el }"
                >
                  <span class="content-tag-index">{{ index + 1 }}</span>
                  <el-input
                    v-model="contentList[index]"
                    :placeholder="getPlaceholder(index)"
                    size="small"
                    class="content-tag-input"
                  />
                  <el-button
                    type="danger"
                    link
                    size="small"
                    class="content-tag-delete"
                    @click="removeContentItem(index)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 前置条件类型 -->
            <div v-else-if="form.template_type === 'precondition'" class="content-textarea-wrapper">
              <el-input
                v-model="preconditionText"
                type="textarea"
                :rows="8"
                placeholder="输入前置条件，使用 {module} 作为模块变量&#10;例如：&#10;1. 系统正常运行&#10;2. 教师账号已登录&#10;3. {module}模块可访问"
                class="content-textarea"
              />
            </div>

            <!-- 其他类型 -->
            <div v-else class="content-textarea-wrapper">
              <el-input
                v-model="form.content"
                type="textarea"
                :rows="8"
                placeholder="输入模板内容（JSON格式）"
                class="content-textarea"
              />
            </div>
          </div>
        </el-form-item>

        <el-form-item label="优先级" prop="priority" class="priority-form-item">
          <div class="priority-wrapper">
            <el-slider v-model="form.priority" :min="1" :max="999" class="priority-slider" />
            <el-input-number v-model="form.priority" :min="1" :max="999" :controls="false" class="priority-number" />
            <div class="form-tip priority-tip">
              <el-icon><Info-Filled /></el-icon>
              <span>数字越小优先级越高，范围1-999</span>
            </div>
          </div>
        </el-form-item>

      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试匹配对话框 -->
    <el-dialog
      v-model="testMatchVisible"
      title="测试模板匹配"
      width="600px"
    >
      <el-form label-width="100px">
        <el-form-item label="测试文本">
          <el-input
            v-model="testMatchText"
            type="textarea"
            :rows="4"
            placeholder="输入需求描述文本，测试会匹配哪些模板"
          />
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="testMatchType" placeholder="全部类型" clearable>
            <el-option
              v-for="type in templateTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <div v-if="testMatchResult" class="test-match-result">
        <div class="match-result-header">
          <span class="match-count">匹配结果</span>
          <el-tag type="primary" effect="light" size="small">{{ testMatchResult.matched_count }} 个模板</el-tag>
        </div>
        <div class="match-cards">
          <div
            v-for="template in testMatchResult.matched_templates"
            :key="template.id"
            class="match-card"
          >
            <div class="card-header">
              <div class="card-title">{{ template.name }}</div>
              <div class="card-badges">
                <el-tag :type="getMatchTypeColor(template.type)" effect="light" size="small">
                  {{ getTypeLabel(template.type) }}
                </el-tag>
              </div>
            </div>
            <div class="card-meta">
              <span class="meta-item">
                <el-icon><Folder /></el-icon>
                {{ template.module_category }}
              </span>
            </div>
            <div class="card-keywords">
              <span class="keywords-label">匹配命中：</span>
              <div class="keywords-list">
                <span
                  v-for="kw in template.keywords"
                  :key="kw"
                  class="keyword-item"
                >
                  {{ kw }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="testMatchVisible = false">关闭</el-button>
        <el-button type="primary" @click="executeTestMatch" :loading="testMatchLoading">
          测试匹配
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="模板详情"
      width="700px"
      :close-on-click-modal="false"
      class="detail-dialog"
    >
      <el-descriptions :column="2" border v-if="detailData.id">
        <el-descriptions-item label="模板名称">{{ detailData.name }}</el-descriptions-item>
        <el-descriptions-item label="模板类型">
          <el-tag :type="getTypeColor(detailData.template_type) || 'info'" size="small">
            {{ detailData.template_type_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="业务模块">{{ detailData.module_category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="优先级">{{ detailData.priority }}</el-descriptions-item>
        <el-descriptions-item label="启用状态">
          <el-tag :type="detailData.is_active ? 'success' : 'info'" size="small">
            {{ detailData.is_active ? '已启用' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(detailData.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="匹配关键词" :span="2">
          <div class="detail-keywords">
            <el-tag
              v-for="keyword in (detailData.keywords_list || [])"
              :key="keyword"
              size="small"
              class="detail-keyword-tag"
            >
              {{ keyword }}
            </el-tag>
            <span v-if="!(detailData.keywords_list && detailData.keywords_list.length)" class="detail-empty">-</span>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="模板内容" :span="2">
          <div class="detail-content">
            <template v-if="detailData.template_type === 'precondition' && detailData.content">
              <pre>{{ detailData.content.precondition || detailData.content }}</pre>
            </template>
            <template v-else-if="Array.isArray(detailData.content)">
              <div v-for="(item, index) in detailData.content" :key="index" class="detail-content-item">
                {{ index + 1 }}. {{ item }}
              </div>
            </template>
            <template v-else>
              <pre>{{ JSON.stringify(detailData.content, null, 2) }}</pre>
            </template>
          </div>
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Collection, Search, Edit, Delete, InfoFilled, View, Folder
} from '@element-plus/icons-vue'
import axios from 'axios'

// 状态
const loading = ref(false)
const initLoading = ref(false)
const submitLoading = ref(false)
const testMatchLoading = ref(false)
const dialogVisible = ref(false)
const testMatchVisible = ref(false)
const isEdit = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const filterType = ref('')
const filterModule = ref('')
const filterActive = ref(null)

// 数据
const templates = ref([])
const templateTypes = ref([])
const moduleCategories = ref([])
const stats = reactive({
  total: 0,
  active: 0,
  testPoint: 0,
  moduleCategories: 0
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 表单
const formRef = ref(null)
const form = reactive({
  id: null,
  name: '',
  template_type: '',
  keywords: '',
  content: /** @type {any[] | {precondition: string}} */ ([]),
  priority: 100,
  module_category: '',
  is_active: true
})

// 内容列表（用于测试点和测试场景）
const contentList = ref([''])
const preconditionText = ref('')
const contentTagsListRef = ref(null)
const contentTagRefs = ref([])

// 测试匹配
const testMatchText = ref('')
const testMatchType = ref('')
const testMatchResult = ref(null)

// 表单规则
const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  template_type: [{ required: true, message: '请选择模板类型', trigger: 'change' }],
  keywords: [{ required: true, message: '请输入匹配关键词', trigger: 'blur' }],
  module_category: [{ required: true, message: '请输入业务模块', trigger: 'blur' }]
}

// 监听模板类型变化
watch(() => form.template_type, (newType) => {
  if (newType === 'test_point' || newType === 'test_scenario') {
    if (!Array.isArray(form.content) || form.content.length === 0) {
      contentList.value = ['']
    } else {
      contentList.value = [...form.content]
    }
  } else if (newType === 'precondition') {
    const content = form.content
    if (typeof content === 'object' && content !== null && !Array.isArray(content)) {
      const contentObj = content
      if ('precondition' in contentObj) {
        preconditionText.value = contentObj['precondition']
      } else {
        preconditionText.value = ''
      }
    } else {
      preconditionText.value = ''
    }
  }
})

// 获取类型标签
const getTypeLabel = (type) => {
  const found = templateTypes.value.find(t => t.value === type)
  return found ? found.label : type
}

// 获取匹配类型颜色
const getMatchTypeColor = (type) => {
  const colors = {
    'test_point': 'primary',
    'test_scenario': 'success',
    'test_step': 'warning',
    'precondition': 'info'
  }
  return colors[type] || ''
}

// 获取类型颜色（用于详情弹窗）
const getTypeColor = (type) => {
  const colors = {
    'test_point': 'primary',
    'test_scenario': 'success',
    'test_step': 'warning',
    'precondition': 'info'
  }
  return colors[type] || 'info'
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 获取内容提示
const getContentTip = () => {
  const tips = {
    'test_point': '测试点：输入具体的验证项，如"课程发布流程验证"',
    'test_scenario': '测试场景：输入业务场景描述，如"学员选课报名场景"',
    'test_step': '测试步骤：JSON格式，如 {"step1": "步骤1", "step2": "步骤2"}',
    'precondition': '前置条件：输入测试前置条件，使用 {module} 作为模块变量'
  }
  return tips[form.template_type] || '请输入模板内容'
}

// 获取输入框占位符
const getPlaceholder = (index) => {
  const placeholders = {
    'test_point': `测试点 ${index + 1}：如"课程发布流程验证"`,
    'test_scenario': `测试场景 ${index + 1}：如"学员选课报名场景"`
  }
  return placeholders[form.template_type] || `第 ${index + 1} 项`
}

// 加载模板列表
const loadTemplates = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterType.value) params.template_type = filterType.value
    if (filterModule.value) params.module_category = filterModule.value
    if (filterActive.value !== null) params.is_active = filterActive.value

    const response = await axios.get('/api/requirement-analysis/test-templates/', { params })
    templates.value = response.data.results || response.data
    pagination.total = response.data.count || templates.value.length

    // 更新统计
    updateStats()
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

// 更新统计
const updateStats = () => {
  stats.total = templates.value.length
  stats.active = templates.value.filter(t => t.is_active).length
  stats.testPoint = templates.value.filter(t => t.template_type === 'test_point').length
  stats.moduleCategories = new Set(templates.value.map(t => t.module_category).filter(Boolean)).size
}

// 加载模板类型
const loadTemplateTypes = async () => {
  try {
    const response = await axios.get('/api/requirement-analysis/test-templates/template_types/')
    templateTypes.value = response.data
  } catch (error) {
    console.error('加载模板类型失败:', error)
  }
}

// 加载业务模块
const loadModuleCategories = async () => {
  try {
    const response = await axios.get('/api/requirement-analysis/test-templates/module_categories/')
    moduleCategories.value = response.data
  } catch (error) {
    console.error('加载业务模块失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadTemplates()
}

// 新建
const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  form.keywords = row.keywords_list ? row.keywords_list.join(',') : row.keywords

  if (row.template_type === 'test_point' || row.template_type === 'test_scenario') {
    contentList.value = Array.isArray(row.content) ? [...row.content] : ['']
  } else if (row.template_type === 'precondition') {
    preconditionText.value = row.content?.precondition || ''
  }

  dialogVisible.value = true
}

// 查看详情
const detailVisible = ref(false)
const detailData = ref(/** @type {any} */ ({}))

const handleViewDetail = (row) => {
  detailData.value = { ...row }
  detailVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${row.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )

    await axios.delete(`/api/requirement-analysis/test-templates/${row.id}/`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 状态变更
const handleStatusChange = async (row) => {
  try {
    await axios.patch(`/api/requirement-analysis/test-templates/${row.id}/`, {
      is_active: row.is_active
    })
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
  } catch (error) {
    console.error('状态变更失败:', error)
    ElMessage.error('状态变更失败')
    row.is_active = !row.is_active
  }
}

// 初始化职业教育模板
const handleInitEducationTemplates = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要初始化职业教育SaaS默认模板吗？这将创建20+个常用模板。',
      '确认初始化',
      { type: 'info' }
    )

    initLoading.value = true
    const response = await axios.post('/api/requirement-analysis/test-templates/init_education_templates/')
    ElMessage.success(response.data.message || '初始化成功')
    loadTemplates()
    loadModuleCategories()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('初始化失败:', error)
      ElMessage.error('初始化失败')
    }
  } finally {
    initLoading.value = false
  }
}

// 测试匹配
const handleTestMatch = () => {
  testMatchText.value = ''
  testMatchType.value = ''
  testMatchResult.value = null
  testMatchVisible.value = true
}

// 执行测试匹配
const executeTestMatch = async () => {
  if (!testMatchText.value.trim()) {
    ElMessage.warning('请输入测试文本')
    return
  }

  testMatchLoading.value = true
  try {
    const response = await axios.post('/api/requirement-analysis/test-templates/test_match/', {
      text: testMatchText.value,
      template_type: testMatchType.value
    })
    testMatchResult.value = response.data
  } catch (error) {
    console.error('测试匹配失败:', error)
    ElMessage.error('测试匹配失败')
  } finally {
    testMatchLoading.value = false
  }
}

// 添加内容项
const addContentItem = () => {
  contentList.value.push('')
  // 等待 DOM 更新后滚动到新添加的项
  nextTick(() => {
    const newIndex = contentList.value.length - 1
    const newElement = contentTagRefs.value[newIndex]
    if (newElement && contentTagsListRef.value) {
      newElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // 聚焦到新添加项的输入框
      const input = newElement.querySelector('input')
      if (input) {
        input.focus()
      }
    }
  })
}

// 移除内容项
const removeContentItem = (index) => {
  contentList.value.splice(index, 1)
  if (contentList.value.length === 0) {
    contentList.value.push('')
  }
}

// 重置表单
const resetForm = () => {
  form.id = null
  form.name = ''
  form.template_type = ''
  form.keywords = ''
  form.content = []
  form.priority = 100
  form.module_category = ''
  form.is_active = true
  contentList.value = ['']
  preconditionText.value = ''
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 根据模板类型处理内容
  if (form.template_type === 'test_point' || form.template_type === 'test_scenario') {
    form.content = contentList.value.filter(item => item.trim())
    if (form.content.length === 0) {
      ElMessage.warning('请至少添加一项内容')
      return
    }
  } else if (form.template_type === 'precondition') {
    if (!preconditionText.value.trim()) {
      ElMessage.warning('请输入前置条件')
      return
    }
    form.content = { precondition: preconditionText.value }
  }

  submitLoading.value = true
  try {
    const data = {
      name: form.name,
      template_type: form.template_type,
      keywords: form.keywords,
      content: form.content,
      priority: form.priority,
      module_category: form.module_category,
      is_active: form.is_active
    }

    if (isEdit.value) {
      await axios.put(`/api/requirement-analysis/test-templates/${form.id}/`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/requirement-analysis/test-templates/', data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadTemplates()
    loadModuleCategories()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitLoading.value = false
  }
}

// 初始化
onMounted(() => {
  loadTemplates()
  loadTemplateTypes()
  loadModuleCategories()
})
</script>

<style lang="scss" scoped>
.test-template-config {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  padding: 20px 24px;
  margin-bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-left {
    h2 {
      margin: 0 0 8px 0;
      font-size: 20px;
      font-weight: 600;
      color: #5a32a3;
    }

    .subtitle {
      color: #666;
      font-size: 14px;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;

    .el-button {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 36px;
      padding: 0 16px;
      border-radius: 8px;
      font-weight: 500;
      font-size: 14px;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      border: 1px solid transparent;

      &--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border-color: transparent;
        color: #ffffff;

        &:hover:not(:disabled) {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
          transform: translateY(-2px);
          box-shadow: 0 4px 14px rgba(123, 66, 246, 0.35);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
        }
      }

      &:not(.el-button--primary) {
        background: #ffffff;
        border-color: rgba(123, 66, 246, 0.3);
        color: #5a32a3;

        &:hover {
          background: #f8f7ff;
          border-color: #7b42f6;
          color: #7b42f6;
        }
      }

      .el-icon {
        margin-right: 6px;
      }
    }
  }
}

.stats-row {
  .el-col {
    margin-bottom: 0;
  }
}

.stat-card {
  text-align: center;
  padding: 24px 20px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(147, 112, 219, 0.12);
  }
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #7b42f6;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.filter-bar {
  padding: 16px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 0;

  .search-input {
    flex: 2;
    min-width: 350px;

    :deep(.el-input__wrapper) {
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff;

      &:hover,
      &:focus {
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
        border-color: #7b42f6;
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  .filter-select {
    flex: 1;
    min-width: 140px;

    :deep(.el-input__wrapper) {
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff;

      &:hover,
      &:focus {
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
        border-color: #7b42f6;
      }
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
  padding: 20px;
}

.history-card {
  flex: 1;
}

.el-table {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  overflow: hidden;

  /* 覆盖 Element Plus 默认主题变量 */
  --el-color-primary: #7b42f6;
  --el-color-primary-light-3: #9370db;
  --el-border-color: #e9ecef;
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;
  --el-table-stripe-bg-color: #fafaff;

  :deep(.el-table__header-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(th) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600;
    font-size: 14px;
    border-bottom: 1px solid #e9ecef;
    padding: 16px !important;
  }

  :deep(th .cell) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600 !important;
  }

  :deep(.el-table__row) {
    transition: all 0.3s ease;
    background-color: #ffffff !important;

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
    vertical-align: middle;
  }

  :deep(.el-table__empty-block) {
    padding: 60px 0;
    background: #ffffff !important;
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
  min-width: auto !important;
  width: auto !important;

  .el-icon {
    font-size: 14px;
    margin: 0;
  }

  span {
    margin: 0;
    line-height: 1;
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

  &.detail-btn {
    background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #85ce61 0%, #6eb34d 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
    }
  }
}

// 详情对话框样式
.detail-dialog {
  .el-descriptions {
    margin-bottom: 0;
  }

  .detail-keywords {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .detail-keyword-tag {
      margin: 0;
    }

    .detail-empty {
      color: #909399;
    }
  }

  .detail-content {
    max-height: 300px;
    overflow-y: auto;

    pre {
      margin: 0;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 4px;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .detail-content-item {
      padding: 4px 0;
      line-height: 1.6;
    }
  }
}

.keywords-cell {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-height: 24px;

  .keyword-tag {
    margin: 0;
    border-radius: 4px;
    font-weight: 500;
  }

  .more-tag {
    background: rgba(123, 66, 246, 0.1);
    border-color: rgba(123, 66, 246, 0.2);
    color: #7b42f6;
    cursor: pointer;

    &:hover {
      background: rgba(123, 66, 246, 0.2);
    }
  }
}

.form-tip {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

// 优先级表单项样式
.priority-form-item {
  :deep(.el-form-item__content) {
    display: flex;
    align-items: center;
  }
}

.priority-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.priority-slider {
  flex: 1;
  min-width: 200px;

  :deep(.el-slider__runway) {
    background-color: #e5e7eb;
    height: 6px;
    border-radius: 3px;
  }

  :deep(.el-slider__bar) {
    background: linear-gradient(90deg, #7b42f6 0%, #a78bfa 100%);
    border-radius: 3px;
  }

  :deep(.el-slider__button) {
    width: 18px;
    height: 18px;
    border: 2px solid #7b42f6;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);

    &:hover {
      transform: scale(1.1);
    }
  }
}

.priority-number {
  width: 80px;
  flex-shrink: 0;

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    text-align: center;
  }

  :deep(.el-input__inner) {
    text-align: center;
    font-weight: 600;
    color: #7b42f6;
  }
}

.priority-tip {
  margin-top: 0;
  flex-shrink: 0;
  color: #8c8c8c;
  white-space: nowrap;

  .el-icon {
    color: #a78bfa;
    font-size: 14px;
  }
}

.content-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

// 模板内容区域样式
.content-form-item {
  :deep(.el-form-item__content) {
    display: block;
  }
}

.content-wrapper {
  width: 100%;
}

// 标签式内容输入
.content-tags-wrapper {
  background: #f8f7ff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(147, 112, 219, 0.15);
}

.content-tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
}

.add-item-btn {
  &:hover {
    color: #7b42f6 !important;

    .el-icon {
      color: #7b42f6 !important;
    }
  }
}

.content-tags-title {
  font-size: 14px;
  font-weight: 500;
  color: #5a32a3;
}

.content-tags-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

.content-tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(147, 112, 219, 0.3);
    box-shadow: 0 2px 8px rgba(147, 112, 219, 0.1);
  }
}

.content-tag-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  flex-shrink: 0;
}

.content-tag-input {
  flex: 1;

  :deep(.el-input__wrapper) {
    border-radius: 6px;
    box-shadow: none;
    background: transparent;

    &:hover,
    &.is-focus {
      box-shadow: 0 0 0 1px #7b42f6;
    }
  }
}

.content-tag-delete {
  flex-shrink: 0;
  padding: 4px !important;

  &:hover {
    transform: scale(1.1);
  }
}

// 文本域内容输入
.content-textarea-wrapper {
  background: #f8f7ff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(147, 112, 219, 0.15);
}

.content-textarea {
  :deep(.el-textarea__inner) {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    background: #ffffff;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 13px;
    line-height: 1.6;

    &:hover,
    &:focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }
}

// 内容提示
// 空状态提示
.content-empty-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 24px;
  background: #f8f7ff;
  border-radius: 12px;
  border: 1px dashed rgba(147, 112, 219, 0.3);
  color: #8c8c8c;
  font-size: 14px;

  .el-icon {
    color: #a78bfa;
    font-size: 16px;
  }
}

// 提示信息样式
.content-tip-wrapper {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.content-tip-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(167, 139, 250, 0.15);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;

  .el-icon {
    color: #a78bfa;
    font-size: 14px;
  }

  &:hover {
    background: rgba(167, 139, 250, 0.3);
    transform: scale(1.1);

    .el-icon {
      color: #7b42f6;
    }
  }
}

// 自定义标签样式
.custom-label {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 100%;
}

// Label 中的提示图标
.label-tip-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: rgba(167, 139, 250, 0.15);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;

  .el-icon {
    color: #a78bfa;
    font-size: 12px;
  }

  &:hover {
    background: rgba(167, 139, 250, 0.3);
    transform: scale(1.1);

    .el-icon {
      color: #7b42f6;
    }
  }
}

// 弹窗样式
.template-dialog {
  :deep(.el-dialog__body) {
    padding: 24px 32px;
  }
}

.template-form {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

// 测试匹配结果样式 - 现代卡片设计
.test-match-result {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
  border: 1px solid rgba(147, 112, 219, 0.15);
  border-radius: 16px;

  .match-result-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);

    .match-count {
      font-size: 16px;
      font-weight: 600;
      color: #5a32a3;
    }
  }

  .match-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .match-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
    border: 1px solid rgba(147, 112, 219, 0.08);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 16px rgba(147, 112, 219, 0.12);
      transform: translateY(-2px);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 10px;

      .card-title {
        font-size: 15px;
        font-weight: 600;
        color: #2d1b69;
        flex: 1;
        margin-right: 12px;
      }

      .card-badges {
        flex-shrink: 0;
      }
    }

    .card-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #606266;

        .el-icon {
          font-size: 14px;
          color: #9b7ee8;
        }
      }
    }

    .card-keywords {
      display: flex;
      align-items: flex-start;
      gap: 8px;

      .keywords-label {
        font-size: 12px;
        color: #909399;
        flex-shrink: 0;
        padding-top: 4px;
      }

      .keywords-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;

        .keyword-item {
          display: inline-flex;
          align-items: center;
          padding: 3px 10px;
          background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
          color: #2e7d32;
          font-size: 12px;
          font-weight: 500;
          border-radius: 20px;
          border: 1px solid rgba(46, 125, 50, 0.15);
        }
      }
    }
  }
}

// 对话框样式优化
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;

  .el-dialog__header {
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid rgba(147, 112, 219, 0.12);

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
    border-top: 1px solid rgba(147, 112, 219, 0.12);

    .el-button {
      height: 36px;
      padding: 0 20px;
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

      // 默认按钮（取消按钮）
      &:not(.el-button--primary) {
        background: #ffffff;
        border: 1px solid rgba(123, 66, 246, 0.3);
        color: #5a32a3;

        &:hover {
          background: #f8f7ff;
          border-color: #7b42f6;
          color: #7b42f6;
        }

        &:active {
          background: #ede9fe;
        }
      }

      // 主要按钮（确定按钮）
      &--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border: none;
        color: #ffffff;

        &:hover:not(:disabled) {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(123, 66, 246, 0.35);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
        }
      }
    }
  }
}

// 标签样式优化
:deep(.el-tag) {
  border-radius: 4px;
  font-weight: 500;
}

// Switch 样式优化
:deep(.el-switch) {
  &.is-checked .el-switch__core {
    background-color: #7b42f6;
    border-color: #7b42f6;
  }
}
</style>
