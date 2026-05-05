<template>
  <el-dialog
    v-model="visible"
    title="选择数据工厂数据"
    width="1000px"
    :close-on-click-modal="false"
    @close="handleClose"
    class="data-factory-dialog"
  >
    <div class="filter-bar">
      <el-input
        v-model="filterToolName"
        placeholder="请输入工具名称"
        clearable
        @clear="handleSearch"
        class="filter-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="filterCategory"
        placeholder="请选择工具分类"
        clearable
        class="filter-select"
        style="width: 200px"
      >
        <el-option
          v-for="cat in categories"
          :key="cat.value"
          :label="cat.label"
          :value="cat.value"
        />
      </el-select>
      <el-select
        v-model="filterTag"
        placeholder="请选择标签"
        filterable
        allow-create
        clearable
        class="filter-select"
      >
        <el-option
          v-for="tag in availableTags"
          :key="tag"
          :label="tag"
          :value="tag"
        />
      </el-select>
      <el-button type="primary" class="query-btn" @click="handleSearch">
        <el-icon><Search /></el-icon>
        查询
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="records"
      stripe
      @row-click="handleRowClick"
      @selection-change="handleSelectionChange"
      class="records-table"
      height="400"
    >
      <el-table-column type="index" label="序号" width="60" header-align="center" align="center">
        <template #default="{ $index }">
          {{ $index + 1 + (currentPage - 1) * pageSize }}
        </template>
      </el-table-column>
      <el-table-column prop="tool_name_display" label="工具名称" min-width="180" show-overflow-tooltip header-align="center" align="center" />
      <el-table-column prop="tool_category_display" label="分类" min-width="120" header-align="center" align="center">
        <template #default="{ row }">
          <span :class="['category-badge', row.tool_category || 'other']">{{ getCategoryDisplayName(row.tool_category) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" min-width="180" header-align="center" align="center">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="tags" label="标签" min-width="180" header-align="center" align="center">
        <template #default="{ row }">
          <el-tag
            v-for="tag in (row.tags || [])"
            :key="tag"
            size="small"
            class="tag-item"
          >
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right" header-align="center" align="center">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" class="action-btn view-btn" @click="previewRecord(row)">
              <el-icon><View /></el-icon>
              <span>预览</span>
            </el-button>
            <el-button size="small" type="primary" class="action-btn select-btn" @click="selectRecord(row)">
              <el-icon><Check /></el-icon>
              <span>选择</span>
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </el-dialog>

  <!-- 预览对话框 -->
  <el-dialog
    v-model="previewVisible"
    title="数据预览"
    width="600px"
    class="preview-dialog"
  >
    <div class="preview-content">
      <pre class="json-preview">{{ previewData }}</pre>
    </div>
    <template #footer>
      <el-button @click="previewVisible = false" class="btn-cancel">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElTag, ElButton, ElIcon, ElInput, ElSelect, ElOption, ElTable, ElTableColumn, ElDialog, ElPagination } from 'element-plus'
import { Search, View, Check } from '@element-plus/icons-vue'
import { getDataFactoryRecords, getDataFactoryTags, getDataFactoryCategories } from '@/api/data-factory'

// DataFactoryRecord 类型定义
interface DataFactoryRecord {
  id: number
  tool_name: string
  tool_name_display?: string
  tool_category?: string
  tool_category_display?: string
  input_params?: Record<string, any>
  output_data?: any
  created_at?: string
  tags?: string[]
  data?: any
}

// 分类中英文映射
const categoryMapping: Record<string, string> = {
  'random': '随机数',
  'string': '字符工具',
  'test_data': '测试数据',
  'datetime': '时间日期',
  'encode': '编码转换',
  'crypto': '加密哈希',
  'crontab': 'Crontab',
  'professional': '专业工具',
  'system': '系统工具',
  'entertainment': '娱乐工具',
  'mock': 'Mock图片',
  'other': '其他'
}

// 获取分类中文显示名
const getCategoryDisplayName = (category?: string): string => {
  if (!category) return '其他'
  return categoryMapping[category] || category
}

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'select', record: DataFactoryRecord): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 数据状态
const loading = ref(false)
const records = ref<DataFactoryRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedRecords = ref<DataFactoryRecord[]>([])

// 筛选条件
const filterToolName = ref('')
const filterCategory = ref('')
const filterTag = ref('')

// 可用标签和分类
const availableTags = ref<string[]>([])
const categories = ref<{label: string, value: string}[]>([])

// 预览相关
const previewVisible = ref(false)
const previewData = ref('')

// 获取数据列表
const fetchRecords = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filterToolName.value) {
      params.tool_name = filterToolName.value
    }
    if (filterCategory.value) {
      params.tool_category = filterCategory.value
    }
    if (filterTag.value) {
      params.tag = filterTag.value
    }

    const res = await getDataFactoryRecords(params)
    // 处理两种响应格式：包装格式 {code, data, message} 和直接格式 {results, count}
    const responseData = res.data
    if (responseData.code === 200) {
      // 包装格式
      records.value = responseData.data?.results || []
      total.value = responseData.data?.count || 0
    } else if (responseData.results) {
      // 直接格式 (Django REST Framework 默认格式)
      records.value = responseData.results || []
      total.value = responseData.count || 0
    } else if (Array.isArray(responseData)) {
      // 纯数组格式
      records.value = responseData
      total.value = responseData.length
    } else {
      ElMessage.error(responseData.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取数据工厂记录失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 获取可用标签
const fetchTags = async () => {
  try {
    const res = await getDataFactoryTags()
    console.log('Tags API response:', res.data)
    const responseData = res.data
    
    let tags: string[] = []
    if (responseData.tags && Array.isArray(responseData.tags)) {
      // 后端格式 { tags: [...], count: N }
      tags = responseData.tags
    } else if (responseData.code === 200 && Array.isArray(responseData.data)) {
      // 包装格式 { code: 200, data: [...] }
      tags = responseData.data
    } else if (Array.isArray(responseData)) {
      // 直接数组格式
      tags = responseData
    } else if (responseData.results && Array.isArray(responseData.results)) {
      // DRF 分页格式
      tags = responseData.results
    }
    
    availableTags.value = tags.filter(tag => tag && typeof tag === 'string')
    console.log('Processed tags:', availableTags.value)
  } catch (error) {
    console.error('获取标签失败:', error)
    availableTags.value = []
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const res = await getDataFactoryCategories()
    console.log('Categories API response:', res.data)
    const responseData = res.data
    
    let cats: {label: string, value: string}[] = []
    
    if (responseData.categories && Array.isArray(responseData.categories)) {
      // 后端格式 { categories: [...], total_tools: N }
      cats = responseData.categories.map((item: any) => ({
        label: item.name || item.label || item.display_name || String(item),
        value: item.scenario || item.value || item.id || item.key || String(item)
      }))
    } else if (responseData.code === 200 && Array.isArray(responseData.data)) {
      // 包装格式 { code: 200, data: [...] }
      cats = responseData.data.map((item: any) => ({
        label: item.label || item.name || item.display_name || String(item),
        value: item.value || item.id || item.key || String(item)
      }))
    } else if (Array.isArray(responseData)) {
      // 直接数组格式
      cats = responseData.map((item: any) => {
        if (typeof item === 'string') {
          return { label: item, value: item }
        }
        return {
          label: item.label || item.name || item.display_name || String(item),
          value: item.value || item.id || item.key || String(item)
        }
      })
    } else if (responseData.results && Array.isArray(responseData.results)) {
      // DRF 分页格式
      cats = responseData.results.map((item: any) => ({
        label: item.label || item.name || item.display_name || String(item),
        value: item.value || item.id || item.key || String(item)
      }))
    }
    
    categories.value = cats.filter(cat => cat.label && cat.value)
    console.log('Processed categories:', categories.value)
  } catch (error) {
    console.error('获取分类失败:', error)
    categories.value = []
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchRecords()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchRecords()
}

// 页码变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchRecords()
}

// 行点击
const handleRowClick = (row: DataFactoryRecord) => {
  // 可以在这里添加行点击逻辑
}

// 选择变化
const handleSelectionChange = (selection: DataFactoryRecord[]) => {
  selectedRecords.value = selection
}

// 预览记录
const previewRecord = (record: DataFactoryRecord) => {
  // 优先使用 data 字段，如果不存在则使用 output_data 字段
  const dataToPreview = record.data !== undefined ? record.data : record.output_data
  previewData.value = JSON.stringify(dataToPreview, null, 2)
  previewVisible.value = true
}

// 选择记录
const selectRecord = (record: DataFactoryRecord) => {
  emit('select', record)
  visible.value = false
}

// 确认选择
const handleConfirm = () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请选择至少一条记录')
    return
  }
  emit('select', selectedRecords.value[0])
  visible.value = false
}

// 关闭对话框
const handleClose = () => {
  filterToolName.value = ''
  filterCategory.value = ''
  filterTag.value = ''
  currentPage.value = 1
  selectedRecords.value = []
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 监听对话框显示状态
watch(() => props.modelValue, (val) => {
  if (val) {
    fetchRecords()
    fetchTags()
    fetchCategories()
  }
})

onMounted(() => {
  fetchTags()
  fetchCategories()
})
</script>

<style scoped lang="scss">
.data-factory-dialog {
  :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);
    padding: 20px 24px;
    margin-right: 0;

    .el-dialog__title {
      color: #5a32a3;
      font-weight: 600;
      font-size: 18px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, #7b42f6 0%, #5a32a3 100%);
        border-radius: 2px;
      }
    }

    .el-dialog__headerbtn {
      top: 20px;
      right: 20px;

      .el-dialog__close {
        color: #9ca3af;
        font-size: 20px;
        transition: all 0.3s ease;

        &:hover {
          color: #7b42f6;
          transform: rotate(90deg);
        }
      }
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
    background: #ffffff;
    max-height: 70vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(147, 112, 219, 0.3);
      border-radius: 3px;

      &:hover {
        background: rgba(147, 112, 219, 0.5);
      }
    }
  }

  :deep(.el-dialog__footer) {
    background: #ffffff;
    border-top: 1px solid rgba(147, 112, 219, 0.1);
    padding: 16px 24px;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0;
  background: none;
  border-radius: 0;
  box-shadow: none;
  border: none;
  margin-bottom: 16px;

  .filter-input {
    flex: 1;
    min-width: 200px;
  }

  .filter-select {
    flex: 1;
    min-width: 180px;
  }

  .filter-input,
  .filter-select {
    :deep(.el-input__wrapper),
    :deep(.el-select__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.3);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: none;
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
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
}

.records-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
  border-top: none !important;

  &::before {
    display: none;
  }

  :deep(.el-table__inner-wrapper::before) {
    display: none !important;
  }

  :deep(.el-table__header-wrapper) {
    background-color: #ffffff !important;

    :deep(.el-table__header) {
      background-color: #ffffff !important;

      :deep(th) {
        background-color: #ffffff !important;
        color: #5a32a3;
        font-weight: 600;
        font-size: 14px;
        border-bottom: none;
        border-top: none;
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

  :deep(.el-table__header th) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600 !important;
  }

  :deep(.el-table__header th .cell) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600 !important;
  }

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

  :deep(.el-table__row:hover) {
    background-color: #f8f7ff !important;
  }

  .category-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    white-space: nowrap;

    &.random {
      background: rgba(64, 158, 255, 0.15);
      color: #409eff;
    }

    &.string {
      background: rgba(103, 194, 58, 0.15);
      color: #67c23a;
    }

    &.test_data {
      background: rgba(230, 162, 60, 0.15);
      color: #e6a23c;
    }

    &.datetime {
      background: rgba(144, 147, 153, 0.15);
      color: #909399;
    }

    &.encode {
      background: rgba(64, 158, 255, 0.15);
      color: #409eff;
    }

    &.crypto {
      background: rgba(245, 108, 108, 0.15);
      color: #f56c6c;
    }

    &.crontab {
      background: rgba(155, 105, 245, 0.15);
      color: #9b69f5;
    }

    &.professional {
      background: rgba(131, 85, 210, 0.15);
      color: #8355d2;
    }

    &.system {
      background: rgba(96, 98, 102, 0.15);
      color: #606266;
    }

    &.entertainment {
      background: rgba(255, 193, 7, 0.15);
      color: #ffc107;
    }

    &.mock {
      background: rgba(121, 85, 72, 0.15);
      color: #795548;
    }

    &.other {
      background: rgba(144, 147, 153, 0.15);
      color: #909399;
    }
  }

  .tag-item {
    border-radius: 6px;
    padding: 4px 10px;
    font-weight: 500;
    border: none;
    background: linear-gradient(135deg, rgba(123, 66, 246, 0.1) 0%, rgba(90, 50, 163, 0.1) 100%);
    color: #7b42f6;
    margin-right: 6px;
    margin-bottom: 4px;
  }

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

      &.select-btn {
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

  :deep(.el-pagination) {
    display: flex;
    align-items: center;
    gap: 4px;
    font-weight: 500;

    .el-pagination__total {
      color: #6b7280;
      font-size: 14px;
      font-weight: 500;
      margin-right: 12px;
    }

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

.preview-content {
  .json-preview {
    max-height: 300px;
    overflow: auto;
    overflow-x: auto;
    overflow-y: auto;
    background: #f5f7fa;
    padding: 10px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    word-break: break-all;
  }
}

:global(.btn-cancel) {
  border: 1px solid rgba(147, 112, 219, 0.3) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  color: #7b42f6 !important;
  background: #ffffff !important;
  transition: all 0.3s ease !important;

  &:hover {
    border-color: #7b42f6 !important;
    background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%) !important;
    color: #5a32a3 !important;
    transform: translateY(-2px) !important;
  }

  &:active {
    transform: translateY(0) !important;
  }
}

:global(.btn-confirm) {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  border-radius: 8px !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;
  transition: all 0.3s ease !important;

  &:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4) !important;
    color: #ffffff !important;
  }

  &:active, &:focus {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    color: #ffffff !important;
    border: none !important;
    outline: none !important;
  }

  &:disabled,
  &.is-disabled {
    background: #e0e0e0 !important;
    color: #999999 !important;
    cursor: not-allowed !important;
    opacity: 0.6 !important;
    box-shadow: none !important;
    transform: none !important;
  }
}
</style>
