<template>
  <div class="request-tree-item">
    <div
      class="request-item"
      :class="{ 
        'is-disabled': !request.enabled,
        'is-group': request.step_type === 'group'
      }"
      :style="{ paddingLeft: `${currentLevel * 20 + 16}px` }"
    >
      <!-- 展开/折叠按钮 (仅group类型显示) -->
      <div v-if="request.step_type === 'group' && request.children && request.children.length > 0" 
           class="expand-btn"
           @click.stop="toggleExpand">
        <el-icon v-if="isExpanded"><ArrowDown /></el-icon>
        <el-icon v-else><ArrowRight /></el-icon>
      </div>
      <div v-else class="expand-placeholder"></div>
      
      <div class="request-number">{{ displayNumber }}</div>
      
      <div class="request-content">
        <div class="request-header">
          <div class="request-type-badge" :class="request.step_type || 'request'">
            {{ getTypeText(request.step_type) }}
          </div>
          <span class="request-name">{{ request.override_name || request.request?.name || request.name || '未命名' }}</span>
          <span v-if="request.children && request.children.length > 0" class="child-count">
            {{ request.children.length }} 个子项
          </span>
        </div>
        
        <div class="request-detail" v-if="request.step_type !== 'group' && request.request">
          <span class="method" :class="getMethodClass(request.override_method || request.request.method)">
            {{ request.override_method || request.request.method }}
          </span>
          <span class="url">{{ request.override_url || request.request.url }}</span>
        </div>
      </div>
      
      <div class="request-meta">
        <span class="assertion-count" v-if="request.assertions?.length > 0">
          <el-icon><Check /></el-icon>
          {{ request.assertions.length }} 个断言
        </span>
      </div>
      
      <div class="request-actions">
        <el-switch
          v-model="request.enabled"
          @change="$emit('toggleEnabled', request)"
          size="small"
          class="enable-switch"
        />
        <el-button 
          size="small" 
          class="action-btn edit-btn"
          @click="$emit('edit', request)"
        >
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button 
          size="small" 
          class="action-btn remove-btn" 
          @click="$emit('remove', request)"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 递归渲染子请求 -->
    <div v-if="isExpanded && request.children && request.children.length > 0" class="request-children">
      <suite-request-tree
        v-for="(childReq, childIndex) in request.children"
        :key="childReq.id"
        :request="childReq"
        :index="childIndex"
        :level="Number(level) + 1"
        :parent-number="displayNumber"
        @edit="$emit('edit', $event)"
        @remove="$emit('remove', $event)"
        @toggle-enabled="$emit('toggleEnabled', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowRight, ArrowDown, Edit, Delete, Check } from '@element-plus/icons-vue'

const props = defineProps({
  request: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: 0
  },
  level: {
    type: [Number, String],
    default: 0
  },
  parentNumber: {
    type: [String, Number],
    default: null
  }
})

defineEmits(['edit', 'remove', 'toggleEnabled'])

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

const getTypeText = (type) => {
  const typeMap = {
    'request': '接口',
    'group': '分组'
  }
  return typeMap[type] || '接口'
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
.request-tree-item {
  width: 100%;
}

.request-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.request-item:hover {
  background-color: #fafafa;
}

.request-item.is-disabled {
  opacity: 0.6;
  background-color: #f8f9fa;
}

.request-item.is-disabled .request-name,
.request-item.is-disabled .url {
  text-decoration: line-through;
  color: #bfbfbf;
}

.request-item.is-group {
  background: #f8f6ff;
  border-left: 3px solid #7b42f6;
}

.request-item.is-group:hover {
  background: #f0ecff;
}

.request-item.is-group .request-name {
  font-weight: 600;
  color: #5a32a3;
}

.expand-btn {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #7b42f6;
  margin-right: 10px;
  border-radius: 50%;
  border: 1px solid #d4c8f5;
  background: #ffffff;
  transition: all 0.2s ease;
  font-size: 12px;
}

.expand-btn:hover {
  background: #7b42f6;
  color: #ffffff;
  border-color: #7b42f6;
}

.expand-placeholder {
  width: 22px;
  margin-right: 10px;
}

.request-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f0ff;
  color: #7b42f6;
  border: 1.5px solid #7b42f6;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.request-content {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.request-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.request-type-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.request-type-badge.request {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.request-type-badge.group {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.request-name {
  font-weight: 500;
  color: #262626;
  font-size: 14px;
  line-height: 1.4;
}

.child-count {
  color: #8c8c8c;
  font-size: 12px;
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
}

.request-detail {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.method {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  min-width: 48px;
  text-align: center;
}

.method-get {
  background: #e6f4ff;
  color: #0958d9;
}

.method-post {
  background: #f6ffed;
  color: #389e0d;
}

.method-put {
  background: #fff7e6;
  color: #d46b08;
}

.method-delete {
  background: #fff2f0;
  color: #cf1322;
}

.method-patch {
  background: #f9f0ff;
  color: #531dab;
}

.url {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
  color: #595959;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
}

.request-meta {
  margin: 0 20px;
  flex-shrink: 0;
}

.assertion-count {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #52c41a;
  font-size: 12px;
  padding: 4px 10px;
  background: rgba(82, 196, 26, 0.08);
  border-radius: 12px;
  font-weight: 500;
}

.request-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  flex-shrink: 0;
  padding-left: 16px;
}

.enable-switch {
  flex-shrink: 0;
  margin-right: 12px;
}

.action-btn {
  width: 32px !important;
  height: 32px !important;
  padding: 0 !important;
  border-radius: 8px !important;
  border: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
}

.action-btn.edit-btn {
  background: rgba(123, 66, 246, 0.1) !important;
  color: #7b42f6 !important;
}

.action-btn.edit-btn:hover {
  background: #7b42f6 !important;
  color: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
}

.action-btn.remove-btn {
  background: rgba(255, 77, 79, 0.1) !important;
  color: #ff4d4f !important;
}

.action-btn.remove-btn:hover {
  background: #ff4d4f !important;
  color: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.4);
}

.request-children {
  width: 100%;
  background: #fafafa;
  position: relative;
}

.request-children::before {
  content: '';
  position: absolute;
  left: 26px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: #e0e0e0;
}

.request-children .request-item {
  position: relative;
}

.request-children .request-item::before {
  content: '';
  position: absolute;
  left: 26px;
  top: 50%;
  width: 12px;
  height: 1px;
  background: #e0e0e0;
}

/* 响应式适配 */
@media screen and (max-width: 992px) {
  .request-meta {
    display: none;
  }
}

@media screen and (max-width: 768px) {
  .request-item {
    padding: 12px 16px;
    flex-wrap: wrap;
  }

  .request-detail {
    width: 100%;
  }

  .request-actions {
    width: 100%;
    margin-left: 0;
    margin-top: 12px;
    justify-content: flex-end;
  }
}
</style>
