<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title || '切片预览'"
    width="60%"
    class="chunk-preview-dialog"
  >
    <div class="preview-content">
      <div class="preview-header">
        <span class="doc-name">{{ chunkData.docName }}</span>
        <span class="chunk-index">切片 {{ chunkData.chunkIndex + 1 }}</span>
      </div>
      <div class="preview-body">
        <pre class="chunk-full-content">{{ chunkData.content }}</pre>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="closePreview">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  chunkData: {
    type: Object,
    default: () => ({
      docName: '',
      chunkIndex: 0,
      content: ''
    })
  },
  title: {
    type: String,
    default: '切片预览'
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const dialogVisible = ref(props.modelValue)

// 监听外部 modelValue 变化
watch(
  () => props.modelValue,
  (newVal) => {
    dialogVisible.value = newVal
  }
)

// 监听内部 dialogVisible 变化
watch(
  () => dialogVisible.value,
  (newVal) => {
    emit('update:modelValue', newVal)
    if (!newVal) {
      emit('close')
    }
  }
)

const closePreview = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.preview-content {
  max-height: 60vh;
  overflow-y: auto;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.doc-name {
  background-color: #f0f9ff;
  color: #409eff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.chunk-index {
  background-color: #f4f4f5;
  color: #909399;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.preview-body {
  padding: 10px 0;
}

.chunk-full-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  color: #606266;
}
</style>