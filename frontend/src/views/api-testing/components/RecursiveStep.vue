<template>
  <div class="step-tree-item">
    <div
      class="step-item"
      :class="{ 
        'is-disabled': !step.override_enabled,
        'is-group': step.step_type === 'group',
        [`level-${level}`]: true
      }"
      :style="{ paddingLeft: `${currentLevel * 24}px` }"
    >
      <!-- 展开/折叠按钮 (仅group类型显示) -->
      <div v-if="step.step_type === 'group' && step.children && step.children.length > 0" 
           class="expand-btn"
           @click.stop="toggleExpand">
        <el-icon v-if="isExpanded"><ArrowDown /></el-icon>
        <el-icon v-else><ArrowRight /></el-icon>
      </div>
      <div v-else class="expand-placeholder"></div>
      
      <div class="step-number">{{ displayNumber }}</div>
      
      <div class="step-content">
        <div class="step-header">
          <div class="step-type-badge" :class="step.step_type">
            {{ getStepTypeText(step.step_type) }}
          </div>
          <span class="step-name">{{ step.name }}</span>
          <span class="step-alias" v-if="step.step_alias">({{ step.step_alias }})</span>
          <span v-if="step.children && step.children.length > 0" class="child-count">
            ({{ step.children.length }} 个子项)
          </span>
        </div>
        
        <div class="step-detail" v-if="step.step_type === 'request' && step.api_request">
          <span class="method" :class="getMethodClass(step.override_method || step.api_request?.method)">
            {{ step.override_method || step.api_request?.method }}
          </span>
          <span class="url">{{ step.override_url || step.api_request?.url }}</span>
        </div>
        
        <div class="step-detail" v-else-if="step.step_type === 'scenario_ref'">
          <el-icon><Link /></el-icon>
          <span>引用场景: {{ step.referenced_scenario_name }}</span>
        </div>
      </div>
      
      <div class="step-actions">
        <el-switch
          v-model="step.override_enabled"
          @change="$emit('toggle', step)"
          size="small"
        />
        <el-button size="small" type="primary" @click="$emit('edit', step)">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button size="small" type="danger" @click="$emit('delete', step)">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 递归渲染子步骤 -->
    <div v-if="isExpanded && step.children && step.children.length > 0" class="step-children">
      <recursive-step
        v-for="(childStep, childIndex) in step.children"
        :key="childStep.id"
        :step="childStep"
        :index="childIndex"
        :level="Number(level) + 1"
        :parent-number="displayNumber"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowRight, ArrowDown, Edit, Delete, Link } from '@element-plus/icons-vue'

const props = defineProps({
  step: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: 0
  },
  level: {
    type: [Number, String],
    default: 0,
    validator: (val) => !isNaN(Number(val))
  },
  parentNumber: {
    type: [String, Number],
    default: null
  }
})

defineEmits(['edit', 'delete', 'toggle'])

const isExpanded = ref(true)

const currentLevel = computed(() => Number(props.level))

const displayNumber = computed(() => {
  if (props.parentNumber) {
    return `${props.parentNumber}.${props.index + 1}`
  }
  return String(props.index + 1)
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const getChildLevel = () => {
  return Number(props.level) + 1
}

const getStepTypeText = (type) => {
  const typeMap = {
    'request': '接口',
    'group': '分组',
    'condition': '条件',
    'loop': '循环',
    'wait': '等待',
    'script': '脚本',
    'scenario_ref': '引用'
  }
  return typeMap[type] || type
}

const getMethodClass = (method) => {
  if (!method) return ''
  const methodClasses = {
    'GET': 'method-get',
    'POST': 'method-post',
    'PUT': 'method-put',
    'DELETE': 'method-delete',
    'PATCH': 'method-patch'
  }
  return methodClasses[method.toUpperCase()] || ''
}
</script>

<style scoped>
.step-tree-item {
  width: 100%;
}

.step-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  transition: background-color 0.2s;
}

.step-item:hover {
  background-color: #f5f7fa;
}

.step-item.is-disabled {
  opacity: 0.6;
  background-color: #f5f7fa;
}

.step-item.is-group {
  background-color: #f0f9ff;
  font-weight: 500;
}

.step-item.is-group:hover {
  background-color: #e0f2fe;
}

.expand-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #606266;
  margin-right: 8px;
  border-radius: 4px;
}

.expand-btn:hover {
  background-color: #dcdfe6;
}

.expand-placeholder {
  width: 24px;
  margin-right: 8px;
}

.step-number {
  width: 36px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #409eff;
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 12px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.step-type-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.step-type-badge.request {
  background-color: #e6f7ff;
  color: #1890ff;
}

.step-type-badge.group {
  background-color: #f6ffed;
  color: #52c41a;
}

.step-type-badge.scenario_ref {
  background-color: #fff7e6;
  color: #fa8c16;
}

.step-type-badge.condition {
  background-color: #f9f0ff;
  color: #722ed1;
}

.step-type-badge.loop {
  background-color: #fff0f6;
  color: #eb2f96;
}

.step-name {
  font-weight: 500;
  color: #303133;
}

.step-alias {
  color: #909399;
  font-size: 12px;
}

.child-count {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.step-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.method {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.method-get {
  background-color: #e6f7ff;
  color: #1890ff;
}

.method-post {
  background-color: #f6ffed;
  color: #52c41a;
}

.method-put {
  background-color: #fff7e6;
  color: #fa8c16;
}

.method-delete {
  background-color: #fff1f0;
  color: #f5222d;
}

.method-patch {
  background-color: #f9f0ff;
  color: #722ed1;
}

.url {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

.step-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
}

.step-children {
  width: 100%;
}

/* 层级缩进样式 */
.level-0 {
  /* 顶层不额外缩进 */
}

.level-1 {
  /* 通过 padding-left 控制缩进 */
}

.level-2 {
  /* 通过 padding-left 控制缩进 */
}
</style>
