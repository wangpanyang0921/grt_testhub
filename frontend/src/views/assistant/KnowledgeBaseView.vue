<template>
  <div class="page-container">
    <!-- 筛选栏 - 包含搜索和上传按钮 -->
    <div class="filter-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索文档名称"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="upload-btn" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传文档
      </el-button>
    </div>

    <!-- 文档列表 -->
    <div class="card-container">
      <el-table :data="filteredDocuments" v-loading="loading" v-if="filteredDocuments.length > 0" stripe style="width: 100%">
        <el-table-column label="序号" width="70" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (currentPage - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="文档名称" min-width="250" show-overflow-tooltip header-align="center" align="left">
          <template #default="{ row }">
            <span>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <span class="file-size-text">{{ formatFileSize(row.file_size) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="110" header-align="center" align="center">
          <template #default="{ row }">
            <span class="file-type-badge" :class="row.file_type?.toLowerCase()">{{ row.file_type?.toUpperCase() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="索引状态" width="120" header-align="center" align="center">
          <template #default="{ row }">
            <div class="status-cell">
              <span class="status-badge" :class="row.status">
                {{ getStatusText(row.status) }}
              </span>
              <!-- 索引中时显示进度条 -->
              <el-progress 
                v-if="row.status === 'indexing'" 
                :percentage="row.indexProgress || 0" 
                :stroke-width="4"
                :show-text="false"
                class="index-progress"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="创建人" width="100" header-align="center" align="center">
          <template #default="{ row }">
            <span v-if="row.created_by">{{ row.created_by.username || row.created_by }}</span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="200" header-align="center" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                size="small" 
                type="primary" 
                class="action-btn edit-btn"
                @click="viewDocument(row)"
                :disabled="row.status !== 'indexed'"
              >
                <el-icon><View /></el-icon>
                <span>查看</span>
              </el-button>
              <el-button 
                size="small" 
                type="success" 
                class="action-btn run-btn"
                @click="chatWithDocument(row)"
                :disabled="row.status !== 'indexed'"
              >
                <el-icon><ChatDotRound /></el-icon>
                <span>问答</span>
              </el-button>
              <!-- 索引失败时显示重试按钮 -->
              <el-button 
                v-if="row.status === 'failed'"
                size="small" 
                type="warning" 
                class="action-btn retry-btn"
                @click="retryIndex(row)"
                :loading="row.retrying"
              >
                <el-icon><RefreshRight /></el-icon>
                <span>重试</span>
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                class="action-btn delete-btn"
                @click="deleteDocument(row)"
              >
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="filteredDocuments.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalDocuments"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredDocuments.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><DocumentDelete /></el-icon>
        </div>
        <div class="empty-title">暂无文档</div>
        <div class="empty-desc">知识库空空如也，上传文档开始构建您的智能知识库</div>
        <el-button type="primary" size="large" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="文档名称">
          <el-input v-model="uploadForm.name" placeholder="请输入文档名称（可选）" />
        </el-form-item>
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept=".pdf,.md,.txt,.doc,.docx"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Markdown、TXT、Word 格式，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpload" :loading="uploading">
            确认上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 文档问答对话框 -->
    <el-dialog
      v-model="showChatDialog"
      :title="`文档问答 - ${currentDoc?.name}`"
      width="800px"
      :close-on-click-modal="false"
      class="chat-dialog"
    >
      <div class="chat-container">
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(msg, index) in chatMessages" :key="index" :class="['message', msg.role]">
            <div class="message-content">
              <div v-if="msg.thinking" class="thinking-status">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>{{ msg.thinking }}</span>
              </div>
              <div v-else>{{ msg.content }}</div>
            </div>
          </div>
        </div>
        <div class="chat-input-area">
          <el-input
            v-model="chatInput"
            type="textarea"
            :rows="2"
            placeholder="输入您的问题，按回车发送..."
            @keydown.enter.exact.prevent="sendQuestion"
          />
          <el-button 
            type="primary" 
            @click="sendQuestion" 
            :loading="chatLoading"
            :disabled="chatLoading"
            class="send-btn"
          >
            <el-icon v-if="!chatLoading"><Promotion /></el-icon>
            <span v-else class="loading-dots"></span>
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 文档详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`文档详情 - ${currentDoc?.name}`"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="currentDoc" class="document-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档名称">{{ currentDoc.name }}</el-descriptions-item>
          <el-descriptions-item label="文档类型">{{ currentDoc.file_type?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(currentDoc.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="索引状态">
            <span class="status-badge" :class="currentDoc.status">
              {{ getStatusText(currentDoc.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间" :span="2">{{ formatDate(currentDoc.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">{{ formatDate(currentDoc.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="currentDoc.index_data">
          <h4>文档索引结构</h4>
          <el-tree
            :data="[currentDoc.index_data]"
            :props="{ label: 'title', children: 'children' }"
            default-expand-all
          />
        </div>

        <div class="detail-section" v-if="currentDoc.index_error">
          <h4>索引错误信息</h4>
          <el-alert
            :title="currentDoc.index_error"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button
            v-if="currentDoc?.status === 'failed'"
            type="primary"
            @click="reindexDocument(currentDoc)"
          >
            重新索引
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Collection, Upload, Document, View, ChatDotRound, Delete,
  UploadFilled, Loading, Promotion, DocumentDelete, Search
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// 数据
const documents = ref([])
const loading = ref(false)
const showUploadDialog = ref(false)
const showChatDialog = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const currentDoc = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessagesRef = ref(null)
const showDetailDialog = ref(false)

const uploadForm = reactive({
  name: '',
  file: null
})

// 搜索
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const totalDocuments = computed(() => documents.value.length)

// 计算属性
const documentCount = computed(() => {
  return documents.value?.length || 0
})

const indexedCount = computed(() => {
  return documents.value?.filter(d => d.status === 'indexed').length || 0
})

const pendingCount = computed(() => {
  return documents.value?.filter(d => d.status === 'pending').length || 0
})

// 搜索过滤后的数据
const filteredDocuments = computed(() => {
  let result = documents.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = documents.value.filter(doc =>
      doc.name?.toLowerCase().includes(query)
    )
  }
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 方法
const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/assistant/knowledge-base/documents/')
    console.log('文档列表响应:', response.data)
    // 确保数据是数组
    const data = response.data
    if (Array.isArray(data)) {
      documents.value = data
    } else if (data && Array.isArray(data.results)) {
      // 处理分页格式
      documents.value = data.results
    } else if (data && typeof data === 'object') {
      // 如果是单个对象，转换为数组
      documents.value = [data]
    } else {
      documents.value = []
    }
    console.log('文档列表数据:', documents.value)
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
    documents.value = []
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  uploadForm.file = file.raw
  if (!uploadForm.name) {
    uploadForm.name = file.name.replace(/\.[^/.]+$/, '')
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const handleFileRemove = () => {
  uploadForm.file = null
}

const handleUpload = async () => {
  if (!uploadForm.file) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('name', uploadForm.name)

    await api.post('/assistant/knowledge-base/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success('文档上传成功，正在生成索引...')
    showUploadDialog.value = false
    // 重置表单
    uploadForm.name = ''
    uploadForm.file = null
    uploadRef.value?.clearFiles()
    // 延迟刷新列表，确保数据已保存
    setTimeout(() => {
      loadDocuments()
    }, 500)
  } catch (error) {
    console.error('上传失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || '上传失败'
    ElMessage.error(`上传失败: ${errorMsg}`)
  } finally {
    uploading.value = false
  }
}

const deleteDocument = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该文档吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/assistant/knowledge-base/documents/${row.id}/`)

    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const viewDocument = (row) => {
  currentDoc.value = row
  showDetailDialog.value = true
}

const reindexDocument = async (row) => {
  try {
    await api.post(`/assistant/knowledge-base/documents/${row.id}/reindex/`)
    ElMessage.success('重新索引任务已提交')
    showDetailDialog.value = false
    loadDocuments()
  } catch (error) {
    console.error('重新索引失败:', error)
    ElMessage.error('重新索引失败')
  }
}

// 重试索引（用于列表中的重试按钮）
const retryIndex = async (row) => {
  row.retrying = true
  try {
    await api.post(`/assistant/knowledge-base/documents/${row.id}/reindex/`)
    ElMessage.success('重新索引任务已提交')
    // 立即更新状态为索引中
    row.status = 'indexing'
    row.indexProgress = 0
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (row.indexProgress < 90) {
        row.indexProgress += Math.random() * 15
      }
    }, 2000)
    
    // 5秒后刷新列表获取真实状态
    setTimeout(() => {
      clearInterval(progressInterval)
      loadDocuments()
    }, 5000)
  } catch (error) {
    console.error('重新索引失败:', error)
    ElMessage.error('重新索引失败')
  } finally {
    row.retrying = false
  }
}

const chatWithDocument = (row) => {
  currentDoc.value = row
  chatMessages.value = []
  chatInput.value = ''
  showChatDialog.value = true
}

const sendQuestion = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return

  const question = chatInput.value.trim()
  chatMessages.value.push({ role: 'user', content: question })
  chatInput.value = ''
  chatLoading.value = true

  // 添加一个空的助手消息用于流式显示
  const assistantMessageIndex = chatMessages.value.length
  chatMessages.value.push({
    role: 'assistant',
    content: '',
    thinking: '正在思考...'
  })

  // 滚动到底部
  nextTick(() => {
    chatMessagesRef.value?.scrollTo(0, chatMessagesRef.value.scrollHeight)
  })

  try {
    // 使用流式接口
    const response = await fetch('/api/assistant/knowledge-base/chat/stream-chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        document: currentDoc.value.id,
        question: question
      })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let answerContent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            switch (data.type) {
              case 'start':
                chatMessages.value[assistantMessageIndex].thinking = '正在检索相关文档内容...'
                break
              case 'thinking':
                chatMessages.value[assistantMessageIndex].thinking = data.content
                break
              case 'chunk':
                chatMessages.value[assistantMessageIndex].thinking = ''
                answerContent += data.content
                chatMessages.value[assistantMessageIndex].content = answerContent
                // 实时滚动到底部
                nextTick(() => {
                  chatMessagesRef.value?.scrollTo(0, chatMessagesRef.value.scrollHeight)
                })
                break
              case 'end':
                chatMessages.value[assistantMessageIndex].thinking = ''
                chatMessages.value[assistantMessageIndex].content = data.answer || answerContent
                break
              case 'error':
                throw new Error(data.error)
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e)
          }
        }
      }
    }
  } catch (error) {
    console.error('问答失败:', error)
    const errorMsg = error.message || '问答失败'
    chatMessages.value[assistantMessageIndex].content = `抱歉，回答生成失败：${errorMsg}`
    chatMessages.value[assistantMessageIndex].thinking = ''
    ElMessage.error('问答失败')
  } finally {
    chatLoading.value = false
    nextTick(() => {
      chatMessagesRef.value?.scrollTo(0, chatMessagesRef.value.scrollHeight)
    })
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const handleSearch = () => {
  // 搜索通过 computed 属性 filteredDocuments 实时过滤
}

const getFileTypeTag = (type) => {
  const typeMap = {
    'pdf': 'danger',
    'md': 'success',
    'txt': 'info',
    'doc': 'primary',
    'docx': 'primary'
  }
  return typeMap[type] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待索引',
    'indexing': '索引中',
    'indexed': '已索引',
    'failed': '失败'
  }
  return statusMap[status] || status
}

onMounted(() => {
  loadDocuments()
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

// 筛选栏样式 - 参考 XMindConverter
.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;

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

  .filter-bar-spacer {
    flex: 1;
  }

  .upload-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 20px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover,
    &:focus {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-2px);
      box-shadow: 0 4px 14px rgba(123, 66, 246, 0.35);
    }

    &:active {
      transform: translateY(0);
      background: linear-gradient(135deg, #5a32a3 0%, #3d1f7a 100%);
    }
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

  // 表格样式 - 参考 XMindConverter
  .el-table {
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

    // 表头样式
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
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    text-align: center;

    .empty-icon {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 24px;

      .el-icon {
        font-size: 56px;
        color: #a78bfa;
      }
    }

    .empty-title {
      font-size: 20px;
      font-weight: 600;
      color: #374151;
      margin-bottom: 12px;
    }

    .empty-desc {
      font-size: 14px;
      color: #9ca3af;
      margin-bottom: 32px;
      max-width: 400px;
      line-height: 1.6;
    }

    .el-button--primary {
      padding: 12px 32px;
      font-size: 15px;
      border-radius: 8px;
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;

      &:hover,
      &:focus {
        background: linear-gradient(135deg, #8b5cf6 0%, #6b21a8 100%);
      }

      &:active {
        background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
      }

      .el-icon {
        margin-right: 8px;
      }
    }
  }
}

.doc-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;

  .doc-icon {
    color: #7b42f6;
    font-size: 18px;
  }
}

.status-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;

  .index-progress {
    width: 80px;

    :deep(.el-progress-bar__outer) {
      background-color: #e6e6e6;
      border-radius: 2px;
    }

    :deep(.el-progress-bar__inner) {
      background: linear-gradient(90deg, #7b42f6 0%, #a855f7 100%);
      border-radius: 2px;
      transition: width 0.3s ease;
    }
  }
}

// 文件类型徽章样式 - 参考索引状态样式
.file-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  // PDF - 红色
  &.pdf {
    background: #fff1f0;
    color: #f5222d;
  }

  // DOC/DOCX - 蓝色
  &.doc,
  &.docx {
    background: #e6f7ff;
    color: #1890ff;
  }

  // TXT - 灰色
  &.txt {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  // 其他类型 - 紫色
  &.default {
    background: #f9f0ff;
    color: #722ed1;
  }
}

// 文件大小文本样式
.file-size-text {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

// 时间文本样式
.time-text {
  color: #666;
  font-size: 14px;
  white-space: nowrap;
}

// 状态徽章样式 - 参考 XMindConverter
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.pending {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  &.indexing {
    background: #fff7e6;
    color: #fa8c16;
  }

  &.indexed {
    background: #f6ffed;
    color: #52c41a;
  }

  &.failed {
    background: #fff1f0;
    color: #f5222d;
  }
}

// 灰色文本样式
.text-gray {
  color: #8c8c8c;
}

// 操作按钮样式 - 在历史记录卡片外部定义
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
    color: #ffffff !important;
  }

  span {
    font-size: 12px;
    color: #ffffff !important;
  }

  // 查看按钮 - 紫色
  &.edit-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
    }

    &:disabled {
      background: linear-gradient(135deg, #d1c4e9 0%, #b39ddb 100%) !important;
      opacity: 0.6;
    }
  }

  // 问答按钮 - 绿色
  &.run-btn {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
    }

    &:disabled {
      background: linear-gradient(135deg, #c6e9a8 0%, #a8d889 100%) !important;
      opacity: 0.6;
    }
  }

  // 重试按钮 - 橙色
  &.retry-btn {
    background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #ffa940 0%, #fa8c16 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(250, 140, 22, 0.4);
    }
  }

  // 删除按钮 - 红色
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

.upload-area {
  width: 100%;

  :deep(.el-upload-dragger) {
    width: 100%;
    padding: 40px 20px;
    border-color: rgba(147, 112, 219, 0.3);
    background: rgba(147, 112, 219, 0.02);

    &:hover {
      border-color: #7b42f6;
    }
  }
}

.chat-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
  }
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 500px;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    background: linear-gradient(180deg, #fafbfc 0%, #f5f7fa 100%);

    .message {
      margin-bottom: 20px;
      animation: fadeInUp 0.3s ease;

      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      &.user {
        text-align: right;

        .message-content {
          background: linear-gradient(135deg, #7b42f6 0%, #6b21a8 100%);
          color: #fff;
          display: inline-block;
          padding: 14px 20px;
          border-radius: 20px 20px 4px 20px;
          max-width: 75%;
          text-align: left;
          font-size: 14px;
          line-height: 1.6;
          box-shadow: 0 4px 12px rgba(123, 66, 246, 0.25);
          word-break: break-word;
        }
      }

      &.assistant {
        .message-content {
          background: #ffffff;
          color: #1f2937;
          display: inline-block;
          padding: 14px 20px;
          border-radius: 20px 20px 20px 4px;
          max-width: 75%;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          white-space: pre-wrap;
          font-size: 14px;
          line-height: 1.7;
          border: 1px solid #f0f0f0;
          word-break: break-word;

          .thinking-status {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #7b42f6;
            font-size: 14px;
            padding: 8px 0;

            .el-icon {
              font-size: 18px;
              color: #a78bfa;
            }
          }
        }
      }
    }
  }

  .chat-input-area {
    display: flex;
    gap: 12px;
    padding: 20px 24px;
    background: #ffffff;
    border-top: 1px solid #f0f0f0;

    .el-textarea {
      flex: 1;

      :deep(.el-textarea__inner) {
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background: #fafbfc;
        padding: 12px 16px;
        font-size: 14px;
        line-height: 1.6;
        transition: all 0.3s ease;
        resize: none;

        &:hover {
          border-color: #d1d5db;
          background: #ffffff;
        }

        &:focus {
          border-color: #a78bfa;
          background: #ffffff;
          box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
        }

        &::placeholder {
          color: #9ca3af;
        }
      }
    }

    .send-btn {
      align-self: flex-end;
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, #7b42f6 0%, #6b21a8 100%);
      border: none;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      margin: 0;

      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.35);
      }

      &:active:not(:disabled) {
        background: linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%);
        transform: translateY(0);
      }

      &:disabled {
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
        opacity: 0.9;
        cursor: not-allowed;
      }

      // 移除 Element Plus 默认的 loading 样式
      .el-loading-spinner {
        display: none;
      }

      .el-icon {
        font-size: 18px;
        margin: 0;
      }

      .loading-dots {
        display: flex;
        gap: 3px;
        align-items: center;
        justify-content: center;

        &::before,
        &::after {
          content: '';
          width: 4px;
          height: 4px;
          background: #fff;
          border-radius: 50%;
          animation: dots 1.4s infinite ease-in-out both;
        }

        &::before {
          animation-delay: -0.32s;
        }

        &::after {
          animation-delay: -0.16s;
        }
      }

      @keyframes dots {
        0%, 80%, 100% {
          transform: scale(0);
          opacity: 0.5;
        }
        40% {
          transform: scale(1);
          opacity: 1;
        }
      }
    }
  }
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 分页样式 - 完全参考 XMindConverter
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
    }

    // 每页条数选择器
    .el-pagination__sizes {
      .el-select {
        .el-input__wrapper {
          border-radius: 6px;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
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
        }
      }
    }
  }
}

.document-detail {
  .detail-section {
    margin-top: 24px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid #e5e7eb;
    }

    .el-tree {
      background: #fafafa;
      padding: 16px;
      border-radius: 8px;
    }
  }
}
</style>
