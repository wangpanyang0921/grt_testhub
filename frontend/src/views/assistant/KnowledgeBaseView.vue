<template>
  <div class="page-container">
    <!-- 文档列表视图 -->
    <div v-if="!isChatMode" class="document-list-view">
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
              <el-link type="primary" @click="showDocumentChunks(row)" :underline="false" class="doc-name-link">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="处理状态" width="120" header-align="center" align="center">
            <template #default="{ row }">
              <div class="status-cell">
                <span class="status-badge" :class="row.status">
                  {{ getStatusText(row.status) }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="split_type" label="切片方式" width="120" header-align="center" align="center">
            <template #default="{ row }">
              <span class="split-type-badge" :class="row.split_type">
                {{ getSplitTypeText(row.split_type) }}
              </span>
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
                  @click="enterChatMode(row)"
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
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="empty-title">暂无文档</div>
          <div class="empty-desc">知识库空空如也，上传文档开始构建您的智能知识库</div>
          <el-button type="primary" size="large" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
        </div>
      </div>
    </div>

    <!-- 文档问答视图 - 参考 AssistantView.vue 样式 -->
    <div v-else class="chat-view">
      <!-- 左侧问答历史侧边栏 -->
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-title">问答历史</div>
          <el-button type="primary" class="new-chat-btn" @click="startNewChat" :icon="Plus" circle size="small" />
        </div>

        <div class="history-list">
          <div class="session-scroll-area">
            <div
              v-for="(session, index) in chatSessions"
              :key="index"
              :class="['session-item', { active: currentChatSessionIndex === index }]"
              @click="switchChatSession(index)"
            >
              <div class="session-title-wrapper">
                <el-icon class="chat-icon"><ChatDotRound /></el-icon>
                <span class="session-title" :title="session.title">{{ session.title || '新问答' }}</span>
              </div>
              <div class="session-actions" @click.stop>
                <span class="delete-text" @click.stop="deleteChatSession(index)">删除</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧问答主内容区 -->
      <div class="chat-main-content">
        <!-- 新问答欢迎页 -->
        <div v-if="isNewChatSession" class="welcome-screen">
          <div class="welcome-content">
            <div class="logo-area">
              <div class="logo-circle">
                <el-icon><Collection /></el-icon>
              </div>
              <h1>{{ currentDoc?.name }}</h1>
            </div>

            <div class="center-input-wrapper">
              <el-input
                v-model="chatInput"
                type="textarea"
                :rows="3"
                placeholder="输入您的问题，按回车发送"
                class="center-input"
                resize="none"
                @keydown.enter.exact.prevent="sendQuestion"
              />
              <div class="input-actions">
                <el-button
                  type="primary"
                  circle
                  :icon="Promotion"
                  :disabled="!chatInput.trim() || chatLoading"
                  @click="sendQuestion"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 问答对话界面 -->
        <div v-else class="chat-screen">
          <div class="chat-header">
            <el-icon class="back-icon" @click="exitChatMode"><ArrowLeft /></el-icon>
            <span class="doc-name">{{ currentDoc?.name }}</span>
          </div>
          <div class="messages-container" ref="chatMessagesRef">
            <div
              v-for="(msg, index) in currentChatSession?.messages || []"
              :key="index"
              :class="['message-row', msg.role]"
            >
              <div class="avatar">
                <el-avatar v-if="msg.role === 'user'" :size="36" :src="userAvatarUrl" :icon="UserFilled" class="user-avatar" />
                <el-avatar v-else :size="36" :icon="Collection" class="ai-avatar" />
              </div>
              <div class="message-wrapper">
                <div class="message-sender">
                  <span class="sender-name">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</span>
                  <span v-if="msg.timestamp" class="message-time">{{ formatMessageTime(msg.timestamp) }}</span>
                </div>
                <div class="message-content">
                  <div v-if="msg.thinking" class="thinking-status">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>{{ msg.thinking }}</span>
                  </div>
                  <div v-else class="message-text markdown-body" v-html="renderMarkdown(msg.content)"></div>
                </div>
              </div>
            </div>
            <div style="height: 20px;"></div>
          </div>

          <div class="chat-footer">
            <div class="input-box">
              <el-input
                v-model="chatInput"
                type="textarea"
                :rows="1"
                :autosize="{ minRows: 1, maxRows: 5 }"
                placeholder="输入您的问题，按回车发送"
                resize="none"
                @keydown.enter.exact.prevent="sendQuestion"
              />
              <el-button
                type="primary"
                class="send-btn"
                :disabled="!chatInput.trim() || chatLoading"
                @click="sendQuestion"
              >
                <el-icon><Promotion /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="uploadForm" label-width="100px" class="upload-form">
        <el-form-item label="文档名称" class="form-item-left">
          <el-input v-model="uploadForm.name" placeholder="请输入文档名称" />
        </el-form-item>
        <el-form-item class="form-item-left split-type-item">
          <template #label>
            <span class="split-type-label">切分方式</span>
            <el-tooltip
              content="语义切分按段落和句子切分，适合需求文档；固定长度按字数切分，适合通用文档"
              placement="top"
              :show-after="200"
            >
              <span class="split-type-info-wrapper">
                <el-icon class="split-type-info-icon"><InfoFilled /></el-icon>
              </span>
            </el-tooltip>
          </template>
          <el-radio-group v-model="uploadForm.splitType">
            <el-radio label="semantic">语义切分（推荐）</el-radio>
            <el-radio label="fixed">固定长度</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选择文件" class="form-item-left">
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
                支持 PDF、Markdown、TXT、Word 格式，单个文件不超过 10MB
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
            <div class="message-avatar">
              <img v-if="msg.role === 'user' && userAvatarUrl" :src="userAvatarUrl" alt="用户头像" class="avatar-img" />
              <el-icon v-else-if="msg.role === 'user'"><UserFilled /></el-icon>
              <el-icon v-else><Collection /></el-icon>
            </div>
            <div class="message-wrapper">
              <div class="message-sender">
                <span class="sender-name">{{ msg.role === 'user' ? '我' : 'AI助手' }}</span>
                <span v-if="msg.timestamp" class="message-time">{{ formatMessageTime(msg.timestamp) }}</span>
              </div>
              <div class="message-content">
                <div v-if="msg.thinking" class="thinking-status">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  <span>{{ msg.thinking }}</span>
                </div>
                <div v-else class="message-text markdown-body" v-html="renderMarkdown(msg.content)"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="chat-input-area">
          <div class="input-wrapper">
            <el-input
              v-model="chatInput"
              type="textarea"
              :rows="2"
              placeholder="输入您的问题，按回车发送..."
              @keydown.enter.exact.prevent="sendQuestion"
              resize="none"
            />
            <el-button
              type="primary"
              @click="sendQuestion"
              :disabled="chatLoading || !chatInput.trim()"
              class="send-btn"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 文档详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="文档详情"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="currentDoc" class="document-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档名称">{{ currentDoc.name }}</el-descriptions-item>
          <el-descriptions-item label="文档类型">{{ currentDoc.file_type?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(currentDoc.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <span v-if="currentDoc.status === 'indexed'" class="text-success">{{ getStatusText(currentDoc.status) }}</span>
            <span v-else class="status-badge" :class="currentDoc.status">
              {{ getStatusText(currentDoc.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ formatDate(currentDoc.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentDoc.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="文本长度" v-if="currentDoc.index_data?.text_length !== undefined">{{ currentDoc.index_data.text_length }} 字符</el-descriptions-item>
          <el-descriptions-item label="分块数量" v-if="currentDoc.index_data?.chunks_count !== undefined">{{ currentDoc.index_data.chunks_count }} 块</el-descriptions-item>
          <el-descriptions-item label="文件路径" :span="2" v-if="currentDoc.index_data?.file_path">{{ formatFilePath(currentDoc.index_data.file_path) }}</el-descriptions-item>
          <el-descriptions-item label="向量ID" :span="2">
            <span v-if="currentDoc.vector_storage_uuid">{{ currentDoc.vector_storage_uuid }}</span>
            <span v-else class="text-gray">-</span>
          </el-descriptions-item>
        </el-descriptions>

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

    <!-- 文档切块内容弹窗 -->
    <el-dialog
      v-model="showChunksDialog"
      :title="`文档切块 - ${chunksData.documentName}`"
      width="900px"
      class="chunks-dialog"
      destroy-on-close
      top="5vh"
    >
      <div v-loading="chunksLoading" class="chunks-container">
        <div v-if="chunksData.total === 0" class="empty-chunks">
          <el-empty description="暂无切块内容" />
        </div>
        <div v-else class="chunks-list">
          <div
            v-for="(chunk, index) in chunksData.chunks"
            :key="index"
            :class="['chunk-item', { expanded: expandedChunks.has(chunk.index) }]"
          >
            <div class="chunk-header" @click="toggleChunk(chunk.index)">
              <div class="chunk-header-left">
                <el-icon class="expand-icon"><ArrowRight /></el-icon>
                <span class="chunk-index">
                  <span class="chunk-label">切块</span>
                  <span class="chunk-number">#{{ chunk.index + 1 }}</span>
                </span>
              </div>
              <span class="chunk-size">{{ chunk.content.length }} 字符</span>
            </div>
            <div v-show="expandedChunks.has(chunk.index)" class="chunk-content">
              <div class="formatted-content" v-html="formatChunkContent(chunk.content)"></div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showChunksDialog = false">关闭</el-button>
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
  UploadFilled, Loading, Promotion, DocumentDelete, Search,
  FolderOpened, UserFilled, Cpu, ArrowRight, InfoFilled,
  Plus, ArrowLeft
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 计算用户头像URL
const userAvatarUrl = computed(() => {
  if (userStore.user?.avatar) {
    if (userStore.user.avatar.startsWith('http')) {
      return userStore.user.avatar
    }
    return `/api${userStore.user.avatar}`
  }
  return ''
})

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
const showChunksDialog = ref(false)
const chunksData = ref({
  documentName: '',
  chunks: [],
  total: 0
})
const chunksLoading = ref(false)
const expandedChunks = ref(new Set())

const uploadForm = reactive({
  name: '',
  file: null,
  splitType: 'semantic'
})

// 搜索
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const totalDocuments = computed(() => documents.value.length)

// 新的页面内嵌式问答状态
const isChatMode = ref(false)
const chatSessions = ref([])
const currentChatSessionIndex = ref(-1)

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

// 当前问答会话
const currentChatSession = computed(() => {
  if (currentChatSessionIndex.value >= 0 && currentChatSessionIndex.value < chatSessions.value.length) {
    return chatSessions.value[currentChatSessionIndex.value]
  }
  return null
})

// 是否为新问答会话（没有消息）
const isNewChatSession = computed(() => {
  return !currentChatSession.value || currentChatSession.value.messages.length === 0
})

// 进入问答模式
const enterChatMode = async (row) => {
  currentDoc.value = row
  isChatMode.value = true
  chatSessions.value = []
  currentChatSessionIndex.value = -1
  chatInput.value = ''

  // 加载历史问答记录
  await loadChatHistory(row.id)
}

// 退出问答模式
const exitChatMode = () => {
  isChatMode.value = false
  currentDoc.value = null
  chatSessions.value = []
  currentChatSessionIndex.value = -1
  chatInput.value = ''
}

// 开始新问答
const startNewChat = () => {
  const newSession = {
    title: '新问答',
    messages: [],
    createdAt: new Date()
  }
  chatSessions.value.unshift(newSession)
  currentChatSessionIndex.value = 0
  chatInput.value = ''
}

// 切换问答会话
const switchChatSession = (index) => {
  currentChatSessionIndex.value = index
  chatInput.value = ''
  scrollToBottom()
}

// 删除问答会话 - 调用后端API真正删除
const deleteChatSession = async (index) => {
  const session = chatSessions.value[index]
  if (!session) return

  try {
    await ElMessageBox.confirm('确定要删除该问答记录吗？删除后将无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 如果有后端ID，调用API删除
    if (session.id) {
      await api.delete(`/assistant/knowledge-base/chat/${session.id}/`)
    }

    // 从前端数组中移除
    chatSessions.value.splice(index, 1)
    if (currentChatSessionIndex.value === index) {
      currentChatSessionIndex.value = -1
    } else if (currentChatSessionIndex.value > index) {
      currentChatSessionIndex.value--
    }
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除问答记录失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

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

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const handleFileChange = (file) => {
  // 检查文件大小
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
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
    formData.append('split_type', uploadForm.splitType)

    const response = await api.post('/assistant/knowledge-base/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success('文档上传成功，正在生成索引...')
    showUploadDialog.value = false
    // 重置表单
    uploadForm.name = ''
    uploadForm.file = null
    uploadRef.value?.clearFiles()
    
    // 获取新上传文档的ID
    const newDoc = response.data
    if (newDoc && newDoc.id) {
      // 添加到列表并设置初始状态
      documents.value.unshift({
        ...newDoc,
        status: 'indexing'
      })

      // 定期轮询获取真实状态
      const pollInterval = setInterval(async () => {
        try {
          const pollResponse = await api.get(`/assistant/knowledge-base/documents/${newDoc.id}/`)
          const updatedDoc = pollResponse.data
          const docIndex = documents.value.findIndex(d => d.id === newDoc.id)
          if (docIndex !== -1) {
            documents.value[docIndex] = {
              ...documents.value[docIndex],
              ...updatedDoc
            }
            // 如果索引完成或失败，停止轮询并刷新列表
            if (updatedDoc.status === 'indexed' || updatedDoc.status === 'failed') {
              clearInterval(pollInterval)
              loadDocuments() // 刷新列表显示最终状态
            }
          }
        } catch (error) {
          console.error('轮询文档状态失败:', error)
        }
      }, 3000)

      // 5分钟后停止轮询（防止无限轮询）
      setTimeout(() => {
        clearInterval(pollInterval)
      }, 300000)
    } else {
      // 如果没有获取到文档ID，则刷新整个列表
      loadDocuments()
    }
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

const toggleChunk = (index) => {
  if (expandedChunks.value.has(index)) {
    expandedChunks.value.delete(index)
  } else {
    expandedChunks.value.add(index)
  }
}

// 格式化切块内容，支持表格、图片、段落样式
const formatChunkContent = (content) => {
  if (!content) return ''

  let formatted = content

  // 0. 预处理：将连续空格中的特定模式转换为换行
  // 处理标题：将 "  ## " 转换为 "\n## "
  formatted = formatted.replace(/\s+##\s+/g, '\n\n## ')
  // 处理数字列表：将 " 1. " 转换为 "\n1. "
  formatted = formatted.replace(/\s+(\d+)\.\s+/g, '\n\n$1. ')
  // 处理段落分隔：将多个空格转换为段落分隔
  formatted = formatted.replace(/\s{3,}/g, '\n\n')

  // 1. 处理图片标记 【图片内容识别】和图片编号
  formatted = formatted.replace(/(【图片[^】]*】)/g, '<div class="content-section-title image-section">$1</div>')
  formatted = formatted.replace(/(图片\d+[:：])/g, '<div class="image-title">$1</div>')

  // 2. 处理表格标记 【表格内容】
  formatted = formatted.replace(/(【表格内容】)/g, '<div class="content-section-title table-section">$1</div>')

  // 3. 处理文档包含图片标记
  formatted = formatted.replace(/(【文档包含 \d+ 张图片】)/g, '<div class="content-section-title info-section">$1</div>')

  // 4. 将表格格式转换为 HTML 表格
  // 匹配包含 | 的表格行（支持 内容 | 内容 格式）
  const tableRegex = /(^[^\n]*\|[^\n]*$\n?)+/gm
  formatted = formatted.replace(tableRegex, (match) => {
    const rows = match.trim().split('\n').filter(row => row.trim() && row.includes('|'))
    if (rows.length < 1) return match

    let tableHtml = '<table class="content-table">'
    rows.forEach((row, index) => {
      const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell)
      if (cells.length > 0) {
        tableHtml += '<tr>'
        cells.forEach((cell, cellIndex) => {
          const firstColClass = cellIndex === 0 ? ' class="table-first-col"' : ''
          if (index === 0) {
            tableHtml += `<th${firstColClass}>${cell}</th>`
          } else {
            tableHtml += `<td${firstColClass}>${cell}</td>`
          }
        })
        tableHtml += '</tr>'
      }
    })
    tableHtml += '</table>'
    return tableHtml
  })

  // 5. 使用 marked 解析 Markdown
  // 先保存我们已经转换的 HTML 标签
  const htmlPlaceholders = []
  formatted = formatted.replace(/<[^>]+>/g, (match) => {
    htmlPlaceholders.push(match)
    return `\u0000${htmlPlaceholders.length - 1}\u0000`
  })

  // 使用 marked 解析 Markdown
  formatted = marked.parse(formatted, { breaks: true })

  // 恢复 HTML 标签
  formatted = formatted.replace(/\u0000(\d+)\u0000/g, (match, index) => {
    return htmlPlaceholders[parseInt(index)]
  })

  return formatted
}

const showDocumentChunks = async (row) => {
  if (row.status !== 'indexed') {
    ElMessage.warning('文档尚未完成索引，无法查看切块内容')
    return
  }

  // 重置展开状态
  expandedChunks.value.clear()
  chunksLoading.value = true
  showChunksDialog.value = true

  try {
    const response = await api.get(`/assistant/knowledge-base/documents/${row.id}/chunks/`)
    chunksData.value = {
      documentName: response.data.document_name,
      chunks: response.data.chunks,
      total: response.data.total
    }
  } catch (error) {
    console.error('获取文档切块失败:', error)
    ElMessage.error(error.response?.data?.error || '获取文档切块失败')
    showChunksDialog.value = false
  } finally {
    chunksLoading.value = false
  }
}

const viewDocument = async (row) => {
  try {
    const response = await api.get(`/assistant/knowledge-base/documents/${row.id}/`)
    currentDoc.value = response.data
    showDetailDialog.value = true
  } catch (error) {
    console.error('获取文档详情失败:', error)
    ElMessage.error('获取文档详情失败')
  }
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

    // 定期轮询获取真实状态
    const pollInterval = setInterval(async () => {
      try {
        const pollResponse = await api.get(`/assistant/knowledge-base/documents/${row.id}/`)
        const updatedDoc = pollResponse.data
        // 更新当前行状态
        row.status = updatedDoc.status
        // 如果索引完成或失败，停止轮询并刷新列表
        if (updatedDoc.status === 'indexed' || updatedDoc.status === 'failed') {
          clearInterval(pollInterval)
          loadDocuments() // 刷新列表显示最终状态
        }
      } catch (error) {
        console.error('轮询文档状态失败:', error)
      }
    }, 3000)

    // 5分钟后停止轮询
    setTimeout(() => {
      clearInterval(pollInterval)
    }, 300000)
  } catch (error) {
    console.error('重新索引失败:', error)
    ElMessage.error('重新索引失败')
  } finally {
    row.retrying = false
  }
}

const loadChatHistory = async (documentId) => {
  try {
    console.log('正在加载历史记录，文档ID:', documentId)
    const response = await api.get(`/assistant/knowledge-base/chat/`, {
      params: { document: documentId }
    })

    console.log('历史记录响应:', response.data)

    // 处理分页格式
    let history = response.data
    if (history && Array.isArray(history.results)) {
      history = history.results
    }

    if (Array.isArray(history) && history.length > 0) {
      console.log('找到历史记录数量:', history.length)

      // 每个问答对作为一个独立的会话，不合并
      history.reverse().forEach(chat => {
        const session = {
          id: chat.id,  // 保存后端ID用于删除
          title: chat.question?.substring(0, 20) || '问答',
          messages: [
            { role: 'user', content: chat.question, timestamp: chat.created_at },
            { role: 'assistant', content: chat.answer, timestamp: chat.created_at }
          ],
          createdAt: chat.created_at
        }
        chatSessions.value.push(session)
      })

      // 默认选中第一个会话
      currentChatSessionIndex.value = 0

      // 滚动到底部
      nextTick(() => {
        scrollToBottom()
      })
    } else {
      console.log('没有找到历史记录')
      // 自动创建一个新会话
      startNewChat()
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.warning('加载历史记录失败')
    // 自动创建一个新会话
    startNewChat()
  }
}

const sendQuestion = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return

  // 如果没有当前会话，自动创建一个新会话
  if (!currentChatSession.value) {
    startNewChat()
  }

  const question = chatInput.value.trim()
  const currentTime = new Date()

  // 如果是第一条消息，更新会话标题
  if (currentChatSession.value.messages.length === 0) {
    currentChatSession.value.title = question.substring(0, 20) + (question.length > 20 ? '...' : '')
  }

  currentChatSession.value.messages.push({ role: 'user', content: question, timestamp: currentTime })
  chatInput.value = ''
  chatLoading.value = true

  // 添加一个空的助手消息用于流式显示
  const assistantMessageIndex = currentChatSession.value.messages.length
  currentChatSession.value.messages.push({
    role: 'assistant',
    content: '',
    thinking: '正在思考...'
  })

  // 滚动到底部
  scrollToBottom()

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
                currentChatSession.value.messages[assistantMessageIndex].thinking = '正在检索相关文档内容...'
                break
              case 'thinking':
                currentChatSession.value.messages[assistantMessageIndex].thinking = data.content
                break
              case 'chunk':
                currentChatSession.value.messages[assistantMessageIndex].thinking = ''
                answerContent += data.content
                currentChatSession.value.messages[assistantMessageIndex].content = answerContent
                // 实时滚动到底部
                scrollToBottom()
                break
              case 'end':
                currentChatSession.value.messages[assistantMessageIndex].thinking = ''
                currentChatSession.value.messages[assistantMessageIndex].content = data.answer || answerContent
                currentChatSession.value.messages[assistantMessageIndex].timestamp = new Date()
                // 保存后端返回的chat_id到会话，用于删除
                if (data.chat_id) {
                  currentChatSession.value.id = data.chat_id
                }
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
    currentChatSession.value.messages[assistantMessageIndex].content = `抱歉，回答生成失败：${errorMsg}`
    currentChatSession.value.messages[assistantMessageIndex].thinking = ''
    ElMessage.error('问答失败')
  } finally {
    chatLoading.value = false
    scrollToBottom()
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

const formatMessageTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const formatFilePath = (path) => {
  if (!path) return ''
  const prefix = '/Users/jinshaomin/Documents/jinsm/test_hub'
  if (path.startsWith(prefix)) {
    return path.substring(prefix.length)
  }
  return path
}

const renderMarkdown = (content) => {
  if (!content) return ''
  return marked.parse(content, { breaks: true })
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
    'pending': '待处理',
    'indexing': '处理中',
    'indexed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

const getSplitTypeText = (splitType) => {
  const splitTypeMap = {
    'semantic': '语义切分',
    'fixed': '固定长度'
  }
  // 历史数据默认为固定长度切分
  if (!splitType) {
    return '固定长度'
  }
  return splitTypeMap[splitType] || splitType
}

onMounted(() => {
  loadDocuments().then(() => {
    // 页面加载完成后，为正在索引的文档恢复进度条
    restoreIndexingProgress()
  })
})

// 恢复索引中的状态轮询
const restoreIndexingProgress = () => {
  documents.value.forEach(doc => {
    if (doc.status === 'indexing') {
      // 启动状态轮询
      const pollInterval = setInterval(async () => {
        try {
          const response = await api.get(`/assistant/knowledge-base/documents/${doc.id}/`)
          const updatedDoc = response.data

          // 更新文档状态
          const targetDoc = documents.value.find(d => d.id === doc.id)
          if (targetDoc) {
            targetDoc.status = updatedDoc.status
          }

          // 如果索引完成或失败，停止轮询并刷新列表
          if (updatedDoc.status === 'indexed' || updatedDoc.status === 'failed') {
            clearInterval(pollInterval)
            loadDocuments() // 刷新列表显示最终状态
          }
        } catch (error) {
          console.error('轮询文档状态失败:', error)
        }
      }, 3000)

      // 5分钟后停止轮询
      setTimeout(() => {
        clearInterval(pollInterval)
      }, 300000)
    }
  })
}
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

// 文档列表视图
.document-list-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 问答视图 - 参考 AssistantView.vue 样式
.chat-view {
  display: flex;
  height: calc(100vh - 108px);
  gap: 20px;
  overflow: hidden;
}

// 左侧问答历史侧边栏
.chat-sidebar {
  width: 280px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);
    background: transparent;

    .sidebar-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 15px;
      font-weight: 600;
      color: #1f2937;

      .back-icon {
        font-size: 18px;
        color: #7b42f6;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          transform: translateX(-2px);
          color: #6b35e0;
        }
      }

      span {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
      }
    }

    .new-chat-btn {
      background: #7b42f6;
      border: none;
      transition: all 0.3s ease;

      &:hover {
        background: #6b35e0;
        transform: scale(1.05);
      }
    }
  }

  .history-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 16px;

    .history-label {
      padding: 0 8px 12px;
      font-size: 12px;
      color: #8c8c8c;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .session-scroll-area {
      flex: 1;
      overflow-y: auto;
      padding: 0;

      &::-webkit-scrollbar {
        width: 4px;
      }
      &::-webkit-scrollbar-thumb {
        background: rgba(147, 112, 219, 0.2);
        border-radius: 2px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
      }
    }

    .session-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      margin: 6px 0;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s ease;
      color: #595959;
      background: transparent;
      border: 1px solid transparent;

      &:hover {
        background: rgba(147, 112, 219, 0.08);
        color: #7b42f6;
        border-color: rgba(147, 112, 219, 0.15);

        .session-actions {
          opacity: 1;
        }
      }

      &.active {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        color: #7b42f6;
        font-weight: 500;
        border-color: rgba(147, 112, 219, 0.2);
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.1);

        .chat-icon {
          color: #7b42f6;
        }
      }

      .session-title-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
        flex: 1;
        overflow: hidden;

        .chat-icon {
          font-size: 16px;
          color: #d1d5db;
          flex-shrink: 0;
        }

        .session-title {
          font-size: 14px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }

      .session-actions {
        opacity: 0;
        transition: opacity 0.2s;
        flex-shrink: 0;

        .delete-text {
          font-size: 12px;
          color: #9ca3af;
          padding: 4px 8px;
          border-radius: 4px;
          transition: all 0.2s;
          cursor: pointer;

          &:hover {
            color: #f56c6c;
            background: #fef0f0;
          }
        }
      }
    }
  }
}

// 右侧问答主内容区
.chat-main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  overflow: hidden;

  // 欢迎页样式
  .welcome-screen {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0;
    background: transparent;
    min-height: 0;

    .welcome-content {
      width: 100%;
      max-width: 720px;
      padding: 0 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: -40px;
    }

    .logo-area {
      text-align: center;
      margin-bottom: 36px;

      .logo-circle {
        width: 72px;
        height: 72px;
        background: #7b42f6;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px;
        box-shadow: 0 8px 24px rgba(123, 66, 246, 0.25);

        .el-icon {
          font-size: 36px;
          color: #ffffff;
        }
      }

      h1 {
        font-size: 28px;
        color: #1f2937;
        margin: 0 0 12px;
        font-weight: 600;
        letter-spacing: -0.5px;
      }

      p {
        color: #6b7280;
        font-size: 15px;
        margin: 0;
        font-weight: 400;
      }
    }

    .center-input-wrapper {
      width: 100%;
      max-width: 640px;
      position: relative;
      background: #ffffff;
      border-radius: 16px;
      padding: 8px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      border: 1px solid rgba(147, 112, 219, 0.15);
      transition: all 0.3s ease;

      &:focus-within {
        box-shadow: 0 4px 24px rgba(123, 66, 246, 0.15);
        border-color: #7b42f6;
      }

      .center-input {
        :deep(.el-textarea__inner) {
          border-radius: 12px;
          padding: 12px 48px 12px 16px;
          font-size: 15px;
          border: none !important;
          background: transparent;
          box-shadow: none !important;
          outline: none !important;
          min-height: 52px !important;

          &::placeholder {
            color: #9ca3af;
          }

          &:focus {
            box-shadow: none !important;
            border: none !important;
            outline: none !important;
          }
        }
      }

      .input-actions {
        position: absolute;
        right: 14px;
        bottom: 14px;

        .el-button {
          width: 36px;
          height: 36px;
          background: #7b42f6;
          border: none;
          transition: all 0.3s ease;
          border-radius: 10px;

          &:hover {
            transform: translateY(-2px);
            background: #6b35e0;
          }

          &:active {
            transform: translateY(0);
          }

          &.is-disabled {
            background: #e5e7eb;
          }

          .el-icon {
            font-size: 18px;
            color: white;
          }
        }
      }
    }
  }

  // 问答对话界面样式
  .chat-screen {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .chat-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 20px 24px;
      background: #ffffff;
      border-bottom: 1px solid rgba(147, 112, 219, 0.1);

      .back-icon {
        font-size: 20px;
        color: #7b42f6;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          transform: translateX(-2px);
          color: #6b35e0;
        }
      }

      .doc-name {
        font-size: 16px;
        font-weight: 600;
        color: #1f2937;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      background: #ffffff;

      .message-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        align-items: flex-start;
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

        .avatar {
          flex-shrink: 0;
          margin-top: 2px;

          .user-avatar {
            background: #e5e7eb;
            border: 2px solid #fff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
          }

          .ai-avatar {
            background: #7b42f6;
            color: #fff;
            border-radius: 10px;
            border: 2px solid #fff;
            box-shadow: 0 1px 3px rgba(123, 66, 246, 0.2);
          }
        }

        .message-wrapper {
          flex: 1;
          max-width: calc(100% - 48px);

          .message-sender {
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 6px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;

            .message-time {
              font-size: 12px;
              color: #9ca3af;
              font-weight: normal;
            }
          }

          .message-content {
            .message-text {
              font-size: 14px;
              line-height: 1.5;
              word-break: break-word;
            }

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

        &.user {
          flex-direction: row-reverse;

          .message-wrapper {
            display: flex;
            flex-direction: column;
            align-items: flex-end;

            .message-sender {
              text-align: right;
            }

            .message-content {
              display: flex;
              justify-content: flex-end;
              max-width: 85%;

              .message-text {
                background: #7b42f6;
                color: #fff;
                padding: 10px 14px;
                border-radius: 16px 16px 4px 16px;
                display: inline-block;
                line-height: 1.5;
              }
            }
          }
        }

        &.assistant {
          .message-content {
            max-width: 85%;

            .message-text {
              background: #fff;
              color: #374151;
              padding: 10px 14px;
              border-radius: 16px 16px 16px 4px;
              display: inline-block;
              line-height: 1.5;
              border: 1px solid rgba(147, 112, 219, 0.15);
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

              &.markdown-body {
                p {
                  margin: 0 0 8px 0;
                  &:last-child {
                    margin-bottom: 0;
                  }
                }

                strong {
                  font-weight: 600;
                }

                em {
                  font-style: italic;
                }

                code {
                  background: #e5e7eb;
                  padding: 2px 6px;
                  border-radius: 4px;
                  font-family: monospace;
                  font-size: 13px;
                }

                pre {
                  background: #1f2937;
                  color: #f3f4f6;
                  padding: 12px;
                  border-radius: 8px;
                  overflow-x: auto;
                  margin: 8px 0;

                  code {
                    background: transparent;
                    padding: 0;
                    color: inherit;
                  }
                }

                ul, ol {
                  margin: 8px 0;
                  padding-left: 20px;
                }

                li {
                  margin: 4px 0;
                }

                a {
                  color: #7b42f6;
                  text-decoration: none;
                  &:hover {
                    text-decoration: underline;
                  }
                }

                blockquote {
                  border-left: 4px solid #7b42f6;
                  margin: 8px 0;
                  padding-left: 12px;
                  color: #6b7280;
                }
              }
            }
          }
        }
      }
    }

    .chat-footer {
      padding: 16px 24px;
      background: #ffffff;

      .input-box {
        display: flex;
        gap: 12px;
        align-items: flex-end;
        background: #ffffff;
        border-radius: 20px;
        padding: 12px 16px;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;

        &:focus-within {
          border-color: #a78bfa;
        }

        .el-textarea {
          flex: 1;
          border: none !important;
          box-shadow: none !important;
          outline: none !important;

          :deep(.el-textarea__inner) {
            border: none !important;
            background: transparent !important;
            padding: 8px 0;
            font-size: 14px;
            line-height: 1.6;
            resize: none !important;
            box-shadow: none !important;
            min-height: 24px !important;
            outline: none !important;

            &::placeholder {
              color: #9ca3af;
            }

            &:focus {
              box-shadow: none !important;
              outline: none !important;
              border-color: transparent !important;
            }
          }

          &:focus,
          &:focus-within {
            outline: none !important;
            box-shadow: none !important;
          }
        }

        .send-btn {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: linear-gradient(135deg, #7b42f6 0%, #6b21a8 100%);
          border: none;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          margin: 0;
          flex-shrink: 0;

          &:hover:not(:disabled) {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            transform: scale(1.05);
          }

          &:active:not(:disabled) {
            transform: scale(0.95);
          }

          &:disabled {
            background: #d1d5db;
            cursor: not-allowed;
          }

          .el-icon {
            font-size: 16px;
            color: #fff;
          }
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

    .el-icon {
      margin-right: 6px;
    }

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
  flex-direction: row;
  align-items: center;
  justify-content: center;
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

// 切片方式徽章样式
.split-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
  text-align: center;
  min-width: 64px;

  &.semantic {
    background: #e6f7ff;
    color: #1890ff;
  }

  &.fixed {
    background: #fff7e6;
    color: #fa8c16;
  }
}

// 灰色文本样式
.text-gray {
  color: #8c8c8c;
}

.text-success {
  color: #52c41a;
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

.upload-form {
  .form-item-left {
    :deep(.el-form-item__label) {
      justify-content: flex-start;
      padding-left: 0;
    }

    :deep(.el-form-item__content) {
      margin-left: 0 !important;
    }
  }

  .split-type-item {
    :deep(.el-form-item__label) {
      display: flex;
      align-items: center;

      .split-type-label {
        line-height: 1;
      }

      .el-tooltip__trigger {
        display: inline-flex;
        align-items: center;
        margin-left: 4px;
        line-height: 1;
        padding: 0;
        border-radius: 0;
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        border: none !important;

        &:hover,
        &:focus,
        &:active {
          background: transparent !important;
          background-color: transparent !important;
          box-shadow: none !important;
          outline: none !important;
          border: none !important;
        }

        .split-type-info-icon {
          font-size: 14px;
          color: #909399;
          cursor: pointer;
          transition: color 0.2s;
          background: transparent !important;
          background-color: transparent !important;

          &:hover {
            color: #409eff;
          }
        }
      }
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

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    background: #ffffff;

    .message {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
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

      .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7b42f6 0%, #6b21a8 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        overflow: hidden;

        .avatar-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .el-icon {
          color: #fff;
          font-size: 18px;
        }
      }

      .message-wrapper {
        flex: 1;
        max-width: calc(100% - 48px);

        .message-sender {
          font-size: 13px;
          color: #6b7280;
          margin-bottom: 6px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;

          .message-time {
            font-size: 12px;
            color: #9ca3af;
            font-weight: normal;
          }
        }

        .message-content {
          .message-text {
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
          }

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

      &.user {
        flex-direction: row-reverse;

        .message-avatar {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .message-wrapper {
          display: flex;
          flex-direction: column;
          align-items: flex-end;

          .message-sender {
            text-align: right;
          }

          .message-content {
            display: flex;
            justify-content: flex-end;
            max-width: 85%;

            .message-text {
              background: #7b42f6;
              color: #fff;
              padding: 10px 14px;
              border-radius: 16px 16px 4px 16px;
              display: inline-block;
              line-height: 1.5;
            }
          }
        }
      }

      &.assistant {
        .message-content {
          max-width: 85%;

          .message-text {
            background: #f3f4f6;
            color: #1f2937;
            padding: 10px 14px;
            border-radius: 16px 16px 16px 4px;
            display: inline-block;
            line-height: 1.5;

            &.markdown-body {
              p {
                margin: 0 0 8px 0;
                &:last-child {
                  margin-bottom: 0;
                }
              }

              strong {
                font-weight: 600;
              }

              em {
                font-style: italic;
              }

              code {
                background: #e5e7eb;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 13px;
              }

              pre {
                background: #1f2937;
                color: #f3f4f6;
                padding: 12px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 8px 0;

                code {
                  background: transparent;
                  padding: 0;
                  color: inherit;
                }
              }

              ul, ol {
                margin: 8px 0;
                padding-left: 20px;
              }

              li {
                margin: 4px 0;
              }

              a {
                color: #7b42f6;
                text-decoration: none;
                &:hover {
                  text-decoration: underline;
                }
              }

              blockquote {
                border-left: 4px solid #7b42f6;
                margin: 8px 0;
                padding-left: 12px;
                color: #6b7280;
              }
            }
          }
        }
      }
    }
  }

  .chat-input-area {
    padding: 16px 24px;
    background: #ffffff;

    .input-wrapper {
      display: flex;
      gap: 12px;
      align-items: flex-end;
      background: #ffffff;
      border-radius: 20px;
      padding: 12px 16px;
      border: 1px solid #e5e7eb;
      transition: all 0.3s ease;
      margin: 0 -8px;

      &:focus-within {
        border-color: #a78bfa;
      }

      .el-textarea {
        flex: 1;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;

        :deep(.el-textarea__inner) {
          border: none !important;
          background: transparent !important;
          padding: 8px 0;
          font-size: 14px;
          line-height: 1.6;
          resize: none !important;
          box-shadow: none !important;
          min-height: 24px !important;
          outline: none !important;

          &::placeholder {
            color: #9ca3af;
          }

          &:focus {
            box-shadow: none !important;
            outline: none !important;
            border-color: transparent !important;
          }
        }

        &:focus,
        &:focus-within {
          outline: none !important;
          box-shadow: none !important;
        }
      }

      .send-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7b42f6 0%, #6b21a8 100%);
        border: none;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        margin: 0;
        flex-shrink: 0;

        &:hover:not(:disabled) {
          background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
          transform: scale(1.05);
        }

        &:active:not(:disabled) {
          transform: scale(0.95);
        }

        &:disabled {
          background: #d1d5db;
          cursor: not-allowed;
        }

        .el-icon {
          font-size: 16px;
          color: #fff;
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
  .el-descriptions {
    .el-descriptions__label {
      white-space: nowrap !important;
      width: 100px;
      min-width: 100px;
    }
    .el-descriptions__content {
      word-break: break-all;
    }
  }

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

// 文档切块弹窗样式
.chunks-dialog {
  max-height: 90vh;
  display: flex;
  flex-direction: column;

  :deep(.el-dialog__body) {
    flex: 1;
    overflow: hidden;
    padding: 20px;
  }

  .chunks-container {
    max-height: calc(90vh - 150px);
    overflow-y: auto;

    .empty-chunks {
      padding: 40px 0;
    }

    .chunks-list {
      display: flex;
      flex-direction: column;
      gap: 16px;

      .chunk-item {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;

        &.expanded {
          .chunk-header {
            .chunk-header-left {
              .expand-icon {
                transform: rotate(90deg);
              }
            }
          }
        }

        .chunk-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          background: #f1f5f9;
          border-bottom: 1px solid transparent;
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            background: #e2e8f0;
          }

          .chunk-header-left {
            display: flex;
            align-items: center;
            gap: 10px;

            .expand-icon {
              font-size: 14px;
              color: #64748b;
              transition: transform 0.2s ease;
              font-weight: bold;
            }

            .chunk-index {
              display: flex;
              align-items: center;
              gap: 6px;
              line-height: 1.4;

              .chunk-label {
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
              }

              .chunk-number {
                font-size: 14px;
                font-weight: 700;
                color: #7b42f6;
              }
            }
          }

          .chunk-size {
            font-size: 11px;
            color: #94a3b8;
            background: #e2e8f0;
            padding: 3px 8px;
            border-radius: 10px;
          }
        }

        &.expanded .chunk-header {
          border-bottom-color: #e2e8f0;
        }

        .chunk-content {
          padding: 16px;
          font-size: 14px;
          line-height: 1.6;
          color: #334155;
          word-break: break-word;

          .formatted-content {
            // marked 生成的段落样式
            p {
              margin: 0 0 12px 0;
              line-height: 1.8;
              color: #334155;

              &:last-child {
                margin-bottom: 0;
              }
            }

            // marked 生成的标题样式
            h1, h2, h3, h4, h5, h6 {
              margin: 16px 0 10px 0;
              color: #1e293b;
              font-weight: 600;

              &:first-child {
                margin-top: 0;
              }
            }

            h1 { font-size: 18px; }
            h2 { font-size: 16px; }
            h3 { font-size: 15px; }
            h4, h5, h6 { font-size: 14px; }

            // 章节标题样式 - 使用更具体的选择器
            div.content-section-title {
              margin: 16px 0 10px 0;
              padding: 8px 12px;
              border-radius: 6px;
              font-weight: 600;
              font-size: 13px;

              &.image-section {
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
                color: #92400e !important;
                border-left: 3px solid #f59e0b !important;
              }

              &.table-section {
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
                color: #1e40af !important;
                border-left: 3px solid #3b82f6 !important;
              }

              &.info-section {
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
                color: #065f46 !important;
                border-left: 3px solid #10b981 !important;
              }
            }

            // 图片标题样式
            div.image-title {
              margin: 12px 0 8px 0;
              padding: 6px 10px;
              background: #fffbeb !important;
              border-radius: 4px;
              color: #b45309 !important;
              font-weight: 600;
              font-size: 13px;
              display: inline-block;
            }

            // 表格样式
            table.content-table {
              width: 100%;
              border-collapse: collapse;
              margin: 12px 0;
              font-size: 13px;
              box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
              border-radius: 6px;
              overflow: hidden;
              table-layout: fixed; // 固定列宽分配

              th, td {
                padding: 10px 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
                word-wrap: break-word;
                overflow-wrap: break-word;
                white-space: normal;
                vertical-align: top;
              }

              // 第一列（使用明确的类名，更可靠）
              th.table-first-col,
              td.table-first-col {
                width: 150px !important;
                min-width: 150px !important;
                max-width: 150px !important;
                font-weight: 500;
                white-space: normal !important;
                word-break: normal !important;
                overflow-wrap: normal !important;
                text-align: left;
              }

              th {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                font-weight: 600;
                color: #475569;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 0.5px;
                white-space: nowrap;
              }

              td {
                color: #334155;
                background: #ffffff;
                line-height: 1.6;
              }

              tr:last-child {
                th, td {
                  border-bottom: none;
                }
              }

              tr:hover td {
                background: #f8fafc;
              }
            }

            // marked 生成的列表样式
            ul, ol {
              margin: 12px 0;
              padding-left: 24px;

              li {
                margin: 8px 0;
                line-height: 1.6;
                color: #334155;
              }
            }

            ul {
              list-style-type: disc;
            }

            ol {
              list-style-type: decimal;
            }

            // 加粗文字
            strong {
              color: #1e293b;
              font-weight: 600;
            }
          }
        }
      }
    }
  }
}

// 文档名称链接样式
.doc-name-link {
  font-weight: 500;
  cursor: pointer;

  &:hover {
    color: #5a32a3;
  }
}
</style>
