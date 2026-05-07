<template>
  <div class="document-selector">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索文档名称"
        clearable
        class="search-input"
        @input="filterDocuments"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

    </div>

    <!-- 文档列表 - 表格形式 -->
    <div class="document-table-wrapper">
      <el-table
        v-loading="loading"
        :data="paginatedDocuments"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
        :row-class-name="getRowClassName"
      >
        <el-table-column width="60" align="center">
          <template #default="{ row }">
            <el-checkbox
              :model-value="selectedDocuments.includes(row.id)"
              @click.stop
              @change="() => toggleDocument(row.id)"
            />
          </template>
        </el-table-column>

        <el-table-column label="文档名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="table-doc-name">{{ row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <span class="table-file-type">{{ row.file_type.toUpperCase() }}</span>
          </template>
        </el-table-column>

        <el-table-column label="大小" width="100" align="center">
          <template #default="{ row }">
            <span class="table-file-size">{{ formatFileSize(row.file_size) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="更新时间" width="120" align="center">
          <template #default="{ row }">
            <span class="table-date">{{ formatDate(row.updated_at) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="paginatedDocuments.length === 0" class="empty-state">
        <el-empty description="暂无文档" />
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="totalPages > 1">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredDocuments.length"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'selection-change'])

const documents = ref([])
const selectedDocuments = ref(props.modelValue)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const loading = ref(false)

const filteredDocuments = computed(() => {
  if (!searchQuery.value) return documents.value
  const query = searchQuery.value.toLowerCase()
  return documents.value.filter(doc =>
    doc.name.toLowerCase().includes(query)
  )
})

const paginatedDocuments = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredDocuments.value.slice(startIndex, endIndex)
})

const totalPages = computed(() => {
  return Math.ceil(filteredDocuments.value.length / pageSize.value)
})

onMounted(() => {
  loadIndexedDocuments()
})

const loadIndexedDocuments = async () => {
  try {
    const response = await api.get('/assistant/knowledge-base/documents/indexed_documents/')
    if (response.data.success) {
      documents.value = response.data.documents
    } else {
      ElMessage.error(response.data.error || '获取文档列表失败')
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  }
}

const filterDocuments = () => {
  currentPage.value = 1
}

const toggleDocument = (docId) => {
  const index = selectedDocuments.value.indexOf(docId)
  if (index > -1) {
    selectedDocuments.value.splice(index, 1)
  } else {
    selectedDocuments.value.push(docId)
  }
  handleSelectionChange(selectedDocuments.value)
}

const handleSelectionChange = (value) => {
  selectedDocuments.value = value
  emit('update:modelValue', value)
  emit('selection-change', value)
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const handleRowClick = (row) => {
  toggleDocument(row.id)
}

const getRowClassName = ({ row }) => {
  return selectedDocuments.value.includes(row.id) ? 'selected-row' : ''
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style lang="scss" scoped>
.document-selector {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}

// 搜索栏样式 - 参考 XMindConverter
.search-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 4px 0;

  .search-input {
    flex: 1;
    max-width: 400px;

    :deep(.el-input__wrapper) {
      box-shadow: 0 0 0 1px rgba(147, 112, 219, 0.25);
      border-radius: 10px;
      background: #ffffff;
      padding: 4px 12px;

      &:hover,
      &.is-focus {
        box-shadow: 0 0 0 1px #7b42f6;
      }
    }

    :deep(.el-input__inner) {
      color: #1e293b;
      font-weight: 500;
      font-size: 14px;

      &::placeholder {
        color: #94a3b8;
      }
    }

    :deep(.el-input__prefix) {
      color: #94a3b8;
      font-size: 16px;
    }
  }

}

// 文档表格样式 - 参考示例表格
.document-table-wrapper {
  flex: 1;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid rgba(147, 112, 219, 0.12);
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);

  :deep(.el-table) {
    border-radius: 12px;
    overflow: hidden;
    background: transparent;

    // 表头样式
    .el-table__header {
      th {
        background: #ffffff;
        color: #7b42f6;
        font-weight: 600;
        font-size: 14px;
        padding: 16px 0;
        border-bottom: 1px solid rgba(147, 112, 219, 0.15);

        .cell {
          font-weight: 600;
        }
      }
    }

    // 表体样式
    .el-table__body {
      tr {
        cursor: pointer;
        transition: all 0.2s ease;

        td {
          padding: 14px 0;
          border-bottom: 1px solid rgba(147, 112, 219, 0.08);
        }

        &:hover {
          background-color: rgba(123, 66, 246, 0.04);
        }

        &.selected-row {
          background: rgba(123, 66, 246, 0.08);

          td {
            background: transparent;
          }
        }

        &:last-child td {
          border-bottom: none;
        }
      }
    }

    // 复选框样式
    .el-checkbox__inner {
      width: 16px;
      height: 16px;
      border-color: rgba(123, 66, 246, 0.3);
      border-radius: 4px;

      &:hover {
        border-color: #7b42f6;
      }
    }

    .el-checkbox__input.is-checked .el-checkbox__inner {
      background-color: #7b42f6;
      border-color: #7b42f6;
    }
  }

  // 文档名称
  .table-doc-name {
    font-size: 14px;
    font-weight: 500;
    color: #1e293b;
  }

  // 文件类型标签
  .table-file-type {
    display: inline-block;
    font-size: 12px;
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 500;
  }

  // 文件大小
  .table-file-size {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
  }

  // 日期
  .table-date {
    font-size: 13px;
    color: #94a3b8;
    font-weight: 500;
  }
}

.empty-state {
  padding: 60px 0;

  :deep(.el-empty__description) {
    color: #94a3b8;
    font-size: 14px;
  }
}

// 分页样式优化
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 16px;

  :deep(.el-pagination) {
    .el-pager li {
      border-radius: 8px;
      font-weight: 500;

      &:hover {
        color: #7b42f6;
      }

      &.is-active {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);
      }
    }

    .btn-prev,
    .btn-next {
      border-radius: 8px;

      &:hover {
        color: #7b42f6;
      }
    }
  }
}
</style>
