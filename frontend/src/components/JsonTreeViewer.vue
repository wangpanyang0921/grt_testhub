<template>
  <div class="json-tree-viewer">
    <json-tree-node
      :data="parsedData"
      :path="rootPath"
      @copy-path="handleCopyPath"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import JsonTreeNode from './JsonTreeNode.vue'

const props = defineProps({
  data: {
    type: [Object, Array, String, Number, Boolean, null],
    required: true
  },
  rootPath: {
    type: String,
    default: '$'
  }
})

const emit = defineEmits(['copy-path'])

const parsedData = computed(() => {
  if (typeof props.data === 'string') {
    try {
      return JSON.parse(props.data)
    } catch {
      return props.data
    }
  }
  return props.data
})

const handleCopyPath = (path) => {
  emit('copy-path', path)
}
</script>

<style scoped>
.json-tree-viewer {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>
