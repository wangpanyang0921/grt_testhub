<template>
  <el-dialog
    v-model="visible"
    title="导入接口"
    width="1000px"
    :close-on-click-modal="false"
    custom-class="import-interface-dialog"
  >
    <div class="import-section">
      <div class="import-steps" style="display: flex; flex-direction: column; gap: 20px;">
        <!-- 步骤1：选择目标集合 -->
        <div class="step" style="margin-bottom: 0;">
          <div class="step-content">
            <el-select
              v-model="targetCollection"
              placeholder="请选择要导入的集合"
              style="width: 100%"
            >
              <el-option
                v-for="collection in collections"
                :key="collection.id"
                :label="collection.name"
                :value="collection.id"
              />
            </el-select>
          </div>
        </div>
        <!-- 步骤2：上传文件（上传成功后隐藏） -->
        <div v-if="!uploadedFile" class="step" style="margin-bottom: 0;">
          <div class="step-content">
            <el-upload
              class="upload-area"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".json"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 Apifox 导出的 OpenAPI 3.0 JSON 文件
                </div>
              </template>
            </el-upload>
          </div>
        </div>
      </div>

      <!-- 预览区域 -->
      <div v-if="previewData.length > 0" class="preview-section" style="margin-top: 20px; overflow-x: auto;">
        <!-- 列表表头 -->
        <div class="preview-list-header" style="display: flex !important; align-items: center; padding: 0 16px; height: 40px; box-sizing: border-box; min-width: 800px;">
          <div style="width: 40px; flex-shrink: 0;">
            <el-checkbox v-model="selectAll" @change="handleSelectAll" style="margin: 0;"></el-checkbox>
          </div>
          <span class="header-method" style="width: 100px; flex-shrink: 0; text-align: center;">方法</span>
          <span class="header-name" style="width: 250px; flex-shrink: 0; padding-left: 10px;">接口名称</span>
          <span class="header-path" style="width: 400px; flex-shrink: 0; padding-left: 10px;">接口路径</span>
        </div>
        <div class="preview-list" style="min-width: 800px;">
          <div
            v-for="item in previewData"
            :key="item.id"
            class="preview-item"
            style="height: 40px; display: flex; align-items: center; padding: 0 16px;"
          >
            <div style="width: 40px; flex-shrink: 0;">
              <el-checkbox v-model="selectedInterfaces" :label="item.id" style="margin: 0;">
                <span></span>
              </el-checkbox>
            </div>
            <div class="item-content" style="display: flex; align-items: center; flex: 1;">
              <span class="method-badge" :class="item.method?.toLowerCase()" style="width: 100px; flex-shrink: 0; text-align: center;">{{ item.method }}</span>
              <span class="interface-name" style="width: 250px; flex-shrink: 0; padding-left: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.name }}</span>
              <span class="interface-path" style="width: 400px; flex-shrink: 0; padding-left: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.path }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        class="import-btn"
        :loading="importing"
        :disabled="!canImport"
        @click="handleImport"
      >
        {{ importButtonText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'

const props = defineProps({
  modelValue: Boolean,
  collections: {
    type: Array,
    default: () => []
  },
  projectId: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'success', 'import-global-headers'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const importing = ref(false)

// 导入相关数据
const targetCollection = ref('')
const previewData = ref([])
const selectedInterfaces = ref([])
const uploadedFile = ref(null)

const selectAll = computed({
  get: () => previewData.value.length > 0 && selectedInterfaces.value.length === previewData.value.length,
  set: (val) => {
    selectedInterfaces.value = val ? previewData.value.map(item => item.id) : []
  }
})

const canImport = computed(() => {
  return selectedInterfaces.value.length > 0 && targetCollection.value
})

const importButtonText = computed(() => {
  return `导入 ${selectedInterfaces.value.length} 个接口`
})

// 处理全选
const handleSelectAll = (val) => {
  selectAll.value = val
}

// 处理文件上传
const handleFileChange = (file) => {
  uploadedFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      parseOpenApiData(data)
      ElMessage.success('文件解析成功')
    } catch (error) {
      ElMessage.error('文件解析失败：' + error.message)
    }
  }
  reader.readAsText(file.raw)
}

// 全局参数
const globalHeadersFromImport = ref([])
const globalParamsFromImport = ref([])

// 解析 OpenAPI 数据
const parseOpenApiData = (data) => {
  // 提取全局 headers（从 x-apifox-common-headers 或其他自定义字段）
  globalHeadersFromImport.value = []
  if (data['x-apifox-common-headers']) {
    globalHeadersFromImport.value = data['x-apifox-common-headers'].map(h => ({
      key: h.name,
      value: h.example || h.default || '',
      description: h.description || '',
      type: h.type || 'string',
      enabled: true
    }))
  }

  // 提取全局 params（从 x-apifox-common-params 或其他自定义字段）
  globalParamsFromImport.value = []
  if (data['x-apifox-common-params']) {
    globalParamsFromImport.value = data['x-apifox-common-params'].map(p => ({
      key: p.name,
      value: p.example || p.default || '',
      description: p.description || '',
      type: p.type || 'string',
      enabled: true
    }))
  }

  const interfaces = []
  let idCounter = 1

  // 遍历所有路径
  if (data.paths) {
    for (const [path, methods] of Object.entries(data.paths)) {
      for (const [method, details] of Object.entries(methods)) {
        if (typeof details === 'object' && details) {
          interfaces.push({
            id: idCounter++,
            name: details.summary || details.operationId || `${method.toUpperCase()} ${path}`,
            method: method.toUpperCase(),
            path: path,
            description: details.description || '',
            raw: {
              details: details,
              globalParams: {
                headers: globalHeadersFromImport.value,
                params: globalParamsFromImport.value
              }
            }
          })
        }
      }
    }
  }

  previewData.value = interfaces
  // 默认全选
  selectedInterfaces.value = interfaces.map(item => item.id)
}

// 处理导入
const handleImport = async () => {
  if (selectedInterfaces.value.length === 0) {
    ElMessage.warning('请至少选择一个接口')
    return
  }

  if (!targetCollection.value) {
    ElMessage.warning('请选择目标集合')
    return
  }

  importing.value = true

  try {
    // 获取选中的接口数据
    const selectedData = previewData.value.filter(item => selectedInterfaces.value.includes(item.id))

    // 收集所有 headers
    const allHeaders = []
    selectedData.forEach(item => {
      if (item.raw?.details?.parameters) {
        item.raw.details.parameters.forEach(p => {
          if (p.in === 'header' && p.name) {
            allHeaders.push({
              key: p.name,
              value: p.schema?.default || p.example || '',
              description: p.description || '',
              type: p.schema?.type || 'string',
              enabled: true,
              is_global: false
            })
          }
        })
      }
    })

    // 合并全局 headers（去重）
    const uniqueGlobalHeaders = []
    const headerKeySet = new Set()

    // 先从全局参数添加
    globalHeadersFromImport.value.forEach(header => {
      if (!headerKeySet.has(header.key)) {
        headerKeySet.add(header.key)
        uniqueGlobalHeaders.push({
          ...header,
          enabled: true
        })
      }
    })

    // 再从接口添加
    allHeaders.forEach(header => {
      if (!headerKeySet.has(header.key)) {
        headerKeySet.add(header.key)
        uniqueGlobalHeaders.push(header)
      }
    })

    // 提取全局 params（去重）
    const uniqueGlobalParams = []
    const paramKeySet = new Set()
    globalParamsFromImport.value.forEach(param => {
      if (!paramKeySet.has(param.key)) {
        paramKeySet.add(param.key)
        uniqueGlobalParams.push({
          ...param,
          enabled: true
        })
      }
    })

    console.log('最终的全局 headers:', uniqueGlobalHeaders)

    const importData = {
      format: 'openapi',
      project_id: props.projectId,
      collection_id: targetCollection.value,
      global_headers: uniqueGlobalHeaders,
      global_params: uniqueGlobalParams,
      interfaces: selectedData.map(item => {
        const details = extractRequestDetails(item.raw)
        // 不传递 headers 到接口，因为所有 headers 都作为全局 headers 传递了
        return {
          name: item.name,
          method: item.method,
          url: item.path,
          description: item.description,
          params: details.params,
          path_params: details.path_params,
          body: details.body,
          request_type: 'HTTP',
          variable_extractors: details.variable_extractors,
          assertions: details.assertions
        }
      })
    }

    const res = await api.post('/api-testing/import/', importData)
    const globalMsg = uniqueGlobalHeaders.length > 0
      ? `，${uniqueGlobalHeaders.length} 个全局 Header`
      : ''
    ElMessage.success(`成功导入 ${res.data.imported_count} 个接口${globalMsg}`)
    emit('success')
    emit('import-global-headers', uniqueGlobalHeaders)
    visible.value = false
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败: ' + (error.response?.data?.error || error.message || '未知错误'))
  } finally {
    importing.value = false
  }
}

// 提取请求详情
const extractRequestDetails = (raw) => {
  const details = {}
  const { details: apiDetails, globalParams = { headers: [], params: [] } } = raw

  // 全局 header 名称集合（用于判断是否是全局 header）- 使用小写进行不区分大小写的匹配
  const globalHeaderNames = new Set(globalParams.headers.map(h => h.key.toLowerCase()))
  const globalParamNames = new Set(globalParams.params.map(p => p.key.toLowerCase()))

  console.log('全局 header 名称集合:', Array.from(globalHeaderNames))
  console.log('接口 parameters:', apiDetails?.parameters)

  if (apiDetails) {
    // 提取 headers（包含直接定义的和引用的）
    // 注意：API Fox 导出的文件中，所有 in: 'header' 的 parameters 都是全局 headers
    if (apiDetails.parameters) {
      const headerParams = []
      const interfaceSpecificHeaders = []

      apiDetails.parameters.forEach(p => {
        // 处理 $ref 引用
        if (p.$ref) {
          const refName = p.$ref.split('/').pop()
          const globalHeader = globalParams.headers.find(h => h.key === refName || h.key === refName.replace(/-/g, '_'))
          if (globalHeader) {
            headerParams.push({
              ...globalHeader,
              is_global: true
            })
          }
        } else if (p.in === 'header') {
          // API Fox 导出时，所有 header 类型的参数都视为全局 header
          const headerInfo = {
            key: p.name,
            value: p.schema?.default || p.example || '',
            description: p.description || '',
            type: p.schema?.type || 'string',
            is_global: true  // 所有 header 都标记为全局
          }
          headerParams.push(headerInfo)
        }
      })

      // 合并：全局 headers 放在前面
      details.headers = [...headerParams, ...interfaceSpecificHeaders]

      console.log('提取的接口 headers:', details.headers)
      console.log('  - 全局 headers:', headerParams)
      console.log('  - 接口特定 headers:', interfaceSpecificHeaders)
    }

    // 提取 query 参数
    if (apiDetails.parameters) {
      const queryParams = []

      apiDetails.parameters.forEach(p => {
        // 处理 $ref 引用
        if (p.$ref) {
          const refName = p.$ref.split('/').pop()
          const globalParam = globalParams.params.find(param => param.key === refName)
          if (globalParam) {
            queryParams.push({
              ...globalParam,
              is_global: true
            })
          }
        } else if (p.in === 'query') {
          queryParams.push({
            key: p.name,
            value: p.default || p.example || '',
            type: p.schema?.type || p.type || 'string',
            description: p.description || '',
            is_global: globalParamNames.has(p.name.toLowerCase())
          })
        }
      })

      details.params = queryParams
    }

    // 提取 path 参数
    if (apiDetails.parameters) {
      const pathParams = []

      apiDetails.parameters.forEach(p => {
        if (p.in === 'path') {
          pathParams.push({
            key: p.name,
            value: '',
            type: p.schema?.type || p.type || 'string',
            description: p.description || ''
          })
        }
      })

      details.path_params = pathParams
    }

    // 提取 body
    if (apiDetails.requestBody?.content) {
      const content = apiDetails.requestBody.content

      // 尝试提取 application/json
      if (content['application/json']) {
        const jsonContent = content['application/json']
        let bodyData = null

        // 优先使用 example
        if (jsonContent.example !== undefined) {
          bodyData = jsonContent.example
          // 如果 example 是字符串，尝试解析为 JSON
          if (typeof bodyData === 'string') {
            try {
              bodyData = JSON.parse(bodyData)
              // 处理双重转义的情况：如果解析后还是字符串，再次解析
              if (typeof bodyData === 'string') {
                try {
                  bodyData = JSON.parse(bodyData)
                } catch {
                  // 第二次解析失败，保持第一次解析的结果
                }
              }
            } catch {
              // 解析失败，保持字符串原样，但仍然是 json 类型
              // 因为 content-type 是 application/json
            }
          }
        }
        // 如果没有 example，尝试从 schema 生成示例
        else if (jsonContent.schema) {
          bodyData = generateExampleFromSchema(jsonContent.schema)
        }

        details.body = bodyData
        details.request_type = 'json'
      }
      // 尝试提取其他类型
      else if (content['application/x-www-form-urlencoded']) {
        const formContent = content['application/x-www-form-urlencoded']
        if (formContent.schema?.properties) {
          const formData = {}
          for (const [key, prop] of Object.entries(formContent.schema.properties)) {
            formData[key] = prop.example || prop.default || ''
          }
          details.body = formData
          details.request_type = 'form'
        }
      }
      // text/plain
      else if (content['text/plain']) {
        details.body = content['text/plain'].example || ''
        details.request_type = 'raw'
      }
    }

    // 提取变量提取规则（从 x-apifox-extractors 或其他自定义字段）
    if (apiDetails['x-apifox-extractors']) {
      details.variable_extractors = apiDetails['x-apifox-extractors']
    }

    // 提取断言（从 x-apifox-assertions 或其他自定义字段）
    if (apiDetails['x-apifox-assertions']) {
      details.assertions = apiDetails['x-apifox-assertions']
    }
  }

  return details
}

// 从 schema 生成示例数据
const generateExampleFromSchema = (schema) => {
  if (!schema) return null

  // 如果有 example，直接使用
  if (schema.example !== undefined) {
    return schema.example
  }

  // 根据类型生成示例
  switch (schema.type) {
    case 'string':
      return schema.example || schema.default || ''
    case 'integer':
    case 'number':
      return schema.example || schema.default || 0
    case 'boolean':
      return schema.example || schema.default || false
    case 'array':
      if (schema.items) {
        return [generateExampleFromSchema(schema.items)]
      }
      return []
    case 'object':
      if (schema.properties) {
        const obj = {}
        for (const [key, prop] of Object.entries(schema.properties)) {
          obj[key] = generateExampleFromSchema(prop)
        }
        return obj
      }
      return {}
    default:
      return null
  }
}

// 重置数据
watch(visible, (val) => {
  if (!val) {
    targetCollection.value = ''
    previewData.value = []
    selectedInterfaces.value = []
    uploadedFile.value = null
  }
})
</script>

<style lang="scss" scoped>
// 导入对话框样式 - 使用 :deep() 覆盖 Element Plus 默认样式
:deep(.import-interface-dialog) {
  // 对话框整体样式
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);

  // 对话框头部
  .el-dialog__header {
    padding: 20px 24px;
    margin-right: 0;
    border-bottom: 1px solid #f3f4f6;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 800;
      color: #1f2937;
    }
  }

  // 对话框主体
  .el-dialog__body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }

  // 对话框底部
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #f3f4f6;
  }
}

// 导入区域样式
.import-section {
  max-height: calc(70vh - 200px);
  min-height: 200px;
  overflow-y: auto;
  overflow-x: visible;
  padding: 0 16px 0 8px;
}

// 上传区域样式
.upload-area {
  :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    border: 2px dashed #e5e7eb;
    border-radius: 12px;
    background: #fafafa;
    transition: all 0.3s ease;

    &:hover {
      border-color: #7b42f6;
      background: #f5f3ff;
    }

    .el-icon--upload {
      font-size: 48px;
      color: #9ca3af;
      margin-bottom: 16px;
    }

    .el-upload__text {
      font-size: 14px;
      color: #6b7280;

      em {
        color: #7b42f6;
        font-style: normal;
        font-weight: 500;
      }
    }
  }

  :deep(.el-upload__tip) {
    text-align: center;
    color: #9ca3af;
    font-size: 12px;
    margin-top: 8px;
  }
}

// 导入按钮样式
.import-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #a855f7 100%);
  border: none;
  padding: 10px 24px;
  font-weight: 500;

  &:hover {
    background: linear-gradient(135deg, #6b35e8 0%, #9a46e8 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: #e5e7eb;
    color: #9ca3af;
    transform: none;
    box-shadow: none;
  }
}

// 步骤样式
.import-steps {
  .step {
    .step-content {
      margin-top: 0;
    }
  }
}

// 输入框样式
.input-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

// 预览区域样式
.preview-section {
  margin-top: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

// 列表表头样式
.preview-list-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f3f4f6;
  border-radius: 6px;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 13px;
  color: #6b7280;

  .el-checkbox {
    margin-right: 12px;
  }

  .header-method {
    width: 70px;
    text-align: center;
    flex-shrink: 0;
  }

  .header-name {
    width: 200px;
    flex-shrink: 0;
    padding-left: 10px;
  }

  .header-path {
    flex: 1;
    padding-left: 10px;
  }
}

// 列表项样式
.preview-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: #f3f4f6;
  }

  :deep(.el-checkbox) {
    margin-right: 0;
    width: 100%;

    .el-checkbox__label {
      padding-left: 0;
      width: 100%;
    }
  }

  .item-content {
    display: flex;
    align-items: center;
    width: 100%;
  }

  .method-badge {
    width: 70px;
    flex-shrink: 0;
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;

    &.get {
      background: #dcfce7;
      color: #16a34a;
    }

    &.post {
      background: #dbeafe;
      color: #2563eb;
    }

    &.put {
      background: #fef3c7;
      color: #d97706;
    }

    &.delete {
      background: #fee2e2;
      color: #dc2626;
    }

    &.patch {
      background: #f3e8ff;
      color: #7c3aed;
    }
  }

  .interface-name {
    width: 200px;
    flex-shrink: 0;
    padding-left: 10px;
    font-size: 14px;
    color: #374151;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .interface-path {
    flex: 1;
    padding-left: 10px;
    font-size: 13px;
    color: #6b7280;
    font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

// 复选框样式
:deep(.el-checkbox__inner) {
  border-radius: 4px;
  border-color: #d1d5db;

  &:hover {
    border-color: #7b42f6;
  }
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #7b42f6;
  border-color: #7b42f6;
}

// 选择框样式
:deep(.el-select) {
  .el-input__wrapper {
    border-radius: 8px;
    box-shadow: 0 0 0 1px #e5e7eb;

    &:hover {
      box-shadow: 0 0 0 1px #7b42f6;
    }

    &.is-focus {
      box-shadow: 0 0 0 1px #7b42f6;
    }
  }
}

// 滚动条样式
.import-section {
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #9ca3af;
  }
}
</style>
