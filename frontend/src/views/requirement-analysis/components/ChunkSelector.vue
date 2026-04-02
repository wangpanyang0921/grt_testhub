<template>
  <div class="chunk-selector">
    <!-- 已选文档标签 -->
    <div class="selected-docs-bar">
      <span class="label">已选文档</span>
      <div class="tags-wrapper">
        <el-tag
          v-for="docId in selectedDocumentIds"
          :key="docId"
          closable
          size="small"
          class="document-tag"
          @close="removeDocument(docId)"
        >
          {{ getDocumentName(docId) }}
        </el-tag>
        <span v-if="selectedDocumentIds.length === 0" class="empty-hint">暂无选择</span>
      </div>
    </div>

    <!-- 调试按钮 -->
    <div v-if="selectedDocumentIds.length > 0 && allChunks.length === 0" class="debug-actions">
      <el-button size="small" type="primary" plain @click="reloadChunks">
        <el-icon><Refresh /></el-icon>
        重新加载切片
      </el-button>
    </div>

    <!-- 切片列表 -->
    <div class="chunk-list">
      <div
        v-for="chunk in allChunks"
        :key="`${chunk.document_id}-${chunk.chunk_index}`"
        class="chunk-item"
        :class="{ selected: isSelected(chunk) }"
        @click="toggleChunk(chunk)"
      >
        <div class="chunk-checkbox">
          <el-checkbox
            :model-value="isSelected(chunk)"
            @click.stop
            @change="() => toggleChunk(chunk)"
          />
        </div>
        <div class="chunk-body">
          <div class="chunk-header">
            <div class="chunk-badges">
              <span class="badge doc-badge">{{ getDocumentName(chunk.document_id) }}</span>
              <span class="badge index-badge">#{{ chunk.chunk_index + 1 }}</span>
            </div>
            <el-button
              link
              type="primary"
              size="small"
              @click.stop="previewChunk(chunk)"
            >
              预览
            </el-button>
          </div>
          <div class="chunk-preview-text" @click.stop="previewChunk(chunk)">
            {{ truncateContent(chunk.content) }}
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="allChunks.length === 0" class="empty-state">
        <el-empty description="请先选择文档" />
      </div>
    </div>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="切片预览"
      width="700px"
      class="chunk-preview-dialog"
    >
      <div class="preview-header">
        <span class="preview-doc">{{ previewChunkData.docName }}</span>
        <el-tag size="small" type="info">切片 {{ previewChunkData.chunkIndex + 1 }}</el-tag>
      </div>
      <div class="preview-body">
        <pre class="preview-text">{{ previewChunkData.content }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

const props = defineProps({
  selectedDocumentIds: {
    type: Array,
    default: () => []
  },
  documents: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'selection-change', 'remove-document'])

const allChunks = ref([])
const selectedChunks = ref(props.modelValue)
const previewVisible = ref(false)
const previewChunkData = ref({
  docName: '',
  chunkIndex: 0,
  content: ''
})

// 监听选中文档变化，加载对应切片
watch(
  () => props.selectedDocumentIds,
  async (newVal) => {
    console.log('选中文档变化:', newVal)
    // 确保 newVal 是数组
    const docIds = Array.isArray(newVal) ? newVal : []
    if (docIds.length > 0) {
      await loadChunksForDocuments(docIds)
    } else {
      allChunks.value = []
      selectedChunks.value = []
    }
  },
  { immediate: true }
)

// 监听选中切片变化
watch(
  () => selectedChunks.value,
  (newVal) => {
    emit('update:modelValue', newVal)
    emit('selection-change', newVal)
  }
)

const loadChunksForDocuments = async (documentIds) => {
  try {
    allChunks.value = []
    const promises = documentIds.map(async (docId) => {
      try {
        const response = await api.get(`/assistant/knowledge-base/documents/${docId}/chunks/`)
        console.log(`加载文档 ${docId} 的切片响应:`, response.data)
        if (response.data.success && response.data.chunks && response.data.chunks.length > 0) {
          return response.data.chunks.map((chunk) => ({
            ...chunk,
            document_id: parseInt(docId),
            // 使用后端返回的 index 作为 chunk_index
            chunk_index: parseInt(chunk.index)
          }))
        }
        return []
      } catch (error) {
        console.error(`加载文档 ${docId} 的切片失败:`, error)
        ElMessage.error(`加载文档 ${getDocumentName(docId)} 的切片失败`)
        return []
      }
    })

    const results = await Promise.all(promises)
    console.log('所有切片结果:', results)
    allChunks.value = results.flat()
    console.log('合并后的切片:', allChunks.value)
  } catch (error) {
    console.error('加载切片失败:', error)
    ElMessage.error('加载切片失败')
  }
}

const getDocumentName = (docId) => {
  const doc = props.documents.find(d => d && d.id === docId)
  return doc ? doc.name : `文档${docId}`
}

const isSelected = (chunk) => {
  return selectedChunks.value.some(item =>
    item.document_id === chunk.document_id &&
    item.chunk_index === chunk.chunk_index
  )
}

const toggleChunk = (chunk) => {
  const index = selectedChunks.value.findIndex(item =>
    item.document_id === chunk.document_id &&
    item.chunk_index === chunk.chunk_index
  )
  if (index > -1) {
    selectedChunks.value.splice(index, 1)
  } else {
    selectedChunks.value.push({
      document_id: chunk.document_id,
      chunk_index: chunk.chunk_index,
      content: chunk.content
    })
  }
  emit('update:modelValue', selectedChunks.value)
  emit('selection-change', selectedChunks.value)
}

const removeDocument = (docId) => {
  selectedChunks.value = selectedChunks.value.filter(chunk => chunk.document_id !== docId)
  emit('remove-document', docId)
}

const reloadChunks = () => {
  if (props.selectedDocumentIds && props.selectedDocumentIds.length > 0) {
    loadChunksForDocuments(props.selectedDocumentIds)
  }
}

// 暴露方法给父组件调用
defineExpose({
  reloadChunks
})

const previewChunk = (chunk) => {
  previewChunkData.value = {
    docName: getDocumentName(chunk.document_id),
    chunkIndex: chunk.chunk_index,
    content: chunk.content
  }
  previewVisible.value = true
}

const truncateContent = (content, maxLength = 180) => {
  if (!content) return ''
  return content.length > maxLength ? content.substring(0, maxLength) + '...' : content
}
</script>

<style scoped>
.chunk-selector {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}

/* 已选文档栏 - 现代卡片风格 */
.selected-docs-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f7ff 0%, #f0ecff 100%);
  border-radius: 12px;
  border: 1px solid rgba(123, 66, 246, 0.1);
  box-shadow: 0 2px 8px rgba(123, 66, 246, 0.05);
}

.selected-docs-bar .label {
  font-size: 14px;
  color: #5a32a3;
  font-weight: 600;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.selected-docs-bar .label::before {
  content: '';
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, #7b42f6 0%, #5a32a3 100%);
  border-radius: 2px;
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  flex: 1;
}

.document-tag {
  margin: 0;
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border: none;
  color: #fff;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  transition: all 0.3s ease;
}

.document-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
}

.empty-hint {
  font-size: 13px;
  color: #9ca3af;
  font-style: italic;
  padding: 6px 0;
}

/* 切片列表 */
.chunk-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 4px;
}

/* 自定义滚动条 */
.chunk-list::-webkit-scrollbar {
  width: 6px;
}

.chunk-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chunk-list::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #c4b5fd 0%, #a78bfa 100%);
  border-radius: 3px;
}

.chunk-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #a78bfa 0%, #8b5cf6 100%);
}

/* 切片卡片 - 现代设计 */
.chunk-item {
  display: flex;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.chunk-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background 0.3s ease;
}

.chunk-item:hover {
  border-color: #c4b5fd;
  box-shadow: 0 8px 24px rgba(123, 66, 246, 0.12);
  transform: translateY(-2px);
}

.chunk-item:hover::before {
  background: linear-gradient(180deg, #7b42f6 0%, #5a32a3 100%);
}

.chunk-item.selected {
  border-color: #7b42f6;
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
  box-shadow: 0 4px 16px rgba(123, 66, 246, 0.15);
}

.chunk-item.selected::before {
  background: linear-gradient(180deg, #7b42f6 0%, #5a32a3 100%);
}

.chunk-checkbox {
  flex-shrink: 0;
  padding-top: 2px;
}

.chunk-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border-color: #7b42f6;
}

.chunk-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 预览按钮样式 */
.chunk-header .el-button {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff !important;
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  padding: 6px 16px;
  border-radius: 8px;
  border: none !important;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);
}

.chunk-header .el-button:hover {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
  transform: translateY(-1px);
}

.chunk-badges {
  display: flex;
  gap: 10px;
}

.badge {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.doc-badge {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #5a32a3;
  border: 1px solid rgba(123, 66, 246, 0.15);
}

.index-badge {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #4b5563;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chunk-preview-text {
  font-size: 14px;
  line-height: 1.7;
  color: #4b5563;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  cursor: pointer;
  transition: color 0.3s ease;
}

.chunk-preview-text:hover {
  color: #7b42f6;
}

.empty-state {
  padding: 60px 0;
}

.empty-state :deep(.el-empty__description) {
  color: #9ca3af;
  font-size: 14px;
}

/* 预览弹窗优化 */
.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.preview-doc {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.preview-body {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.preview-text {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.8;
  color: #374151;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 调试按钮区域 */
.debug-actions {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.debug-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
}

.preview-doc {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.preview-body {
  max-height: 500px;
  overflow-y: auto;
}

.preview-text {
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
