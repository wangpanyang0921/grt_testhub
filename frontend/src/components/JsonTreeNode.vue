<template>
  <div class="json-tree-node">
    <template v-if="isObject">
      <div class="json-item object-item">
        <span class="json-bracket">{</span>
        <el-button
          size="small"
          type="primary"
          link
          class="copy-path-btn"
          @click="$emit('copy-path', path)"
        >
          <el-icon><CopyDocument /></el-icon>
        </el-button>
      </div>
      <div class="json-children">
        <div
          v-for="(value, key) in data"
          :key="key"
          class="json-property"
        >
          <span class="json-key">"{{ key }}":</span>
          <template v-if="isSimpleValue(value)">
            <span :class="getValueClass(value)">{{ formatValue(value) }}</span>
            <el-button
              size="small"
              type="primary"
              link
              class="copy-path-btn"
              @click="$emit('copy-path', `${path}.${key}`)"
            >
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
          <template v-else>
            <JsonTreeNode
              :data="value"
              :path="`${path}.${key}`"
              @copy-path="$emit('copy-path', $event)"
            />
          </template>
        </div>
      </div>
      <div class="json-bracket">}</div>
    </template>
    <template v-else-if="isArray">
      <div class="json-item array-item">
        <span class="json-bracket">[</span>
        <span v-if="arrayLength === 0" class="json-empty">/* empty array */</span>
        <el-button
          v-else
          size="small"
          type="primary"
          link
          class="copy-path-btn"
          @click="$emit('copy-path', path)"
        >
          <el-icon><CopyDocument /></el-icon>
        </el-button>
      </div>
      <div v-if="arrayLength > 0" class="json-children">
        <div
          v-for="(item, index) in data"
          :key="index"
          class="json-array-item"
        >
          <template v-if="isSimpleValue(item)">
            <span :class="getValueClass(item)">{{ formatValue(item) }}</span>
            <el-button
              size="small"
              type="primary"
              link
              class="copy-path-btn"
              @click="$emit('copy-path', `${path}[${index}]`)"
            >
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
          <template v-else>
            <JsonTreeNode
              :data="item"
              :path="`${path}[${index}]`"
              @copy-path="$emit('copy-path', $event)"
            />
          </template>
        </div>
      </div>
      <div class="json-bracket">]</div>
    </template>
    <template v-else>
      <span :class="getValueClass(data)">{{ formatValue(data) }}</span>
    </template>
  </div>
</template>

<script>
// 使用 options API 定义组件名，支持递归
export default {
  name: 'JsonTreeNode'
}
</script>

<script setup>
import { computed } from 'vue'
import { CopyDocument } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: [Object, Array, String, Number, Boolean, null],
    required: true
  },
  path: {
    type: String,
    default: '$'
  }
})

defineEmits(['copy-path'])

const isObject = computed(() => {
  return props.data !== null && typeof props.data === 'object' && !Array.isArray(props.data)
})

const isArray = computed(() => {
  return Array.isArray(props.data)
})

const arrayLength = computed(() => {
  if (isArray.value && Array.isArray(props.data) && props.data) {
    return props.data.length
  }
  return 0
})

const isSimpleValue = (value) => {
  return value === null || typeof value !== 'object'
}

const getValueClass = (value) => {
  if (value === null) return 'json-null'
  if (typeof value === 'string') return 'json-string'
  if (typeof value === 'number') return 'json-number'
  if (typeof value === 'boolean') return 'json-boolean'
  return ''
}

const formatValue = (value) => {
  if (value === null) return 'null'
  if (typeof value === 'string') return `"${value}"`
  return String(value)
}
</script>

<style scoped>
.json-tree-node {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.json-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.json-bracket {
  color: #333;
}

.json-children {
  padding-left: 20px;
}

.json-property {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 2px 0;
  flex-wrap: wrap;
}

.json-array-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 2px 0;
  flex-wrap: wrap;
}

.json-key {
  color: #881391;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.json-string {
  color: #0d7377;
  word-break: break-all;
  white-space: pre-wrap;
}

.json-number {
  color: #1c00cf;
  word-break: break-all;
}

.json-boolean {
  color: #d73a49;
}

.json-null {
  color: #6f42c1;
}

.json-empty {
  color: #999;
  font-style: italic;
  font-size: 12px;
}

.copy-path-btn {
  /* 复制按钮始终显示（不需要 hover） */
  opacity: 1;
  padding: 2px 6px;
  height: 24px;
  min-height: 24px;
}
</style>
