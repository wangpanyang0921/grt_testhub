<template>
  <div class="interface-management">
    <div class="interface-layout">
      <!-- 左侧集合树 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <el-select v-model="selectedProject" :placeholder="$t('apiTesting.common.selectProject')" @change="onProjectChange">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="showCreateCollectionDialog = true" :title="$t('apiTesting.interface.createCollection')">
              <el-icon><Folder /></el-icon>
            </el-button>
            <el-button type="success" size="small" @click="createEmptyRequest" :title="$t('apiTesting.interface.addInterface')">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="collection-tree">
          <el-tree
            ref="treeRef"
            :data="collections"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :default-expanded-keys="expandedKeys"
            @node-click="onNodeClick"
            @node-contextmenu="onNodeRightClick"
            @node-expand="onNodeExpand"
            @node-collapse="onNodeCollapse"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.type === 'collection'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>
                
                <!-- 集合名称编辑 -->
                <div v-if="data.type === 'collection' && editingNodeId === data.id" class="node-edit">
                  <el-input
                    v-model="editingNodeName"
                    size="small"
                    @blur="saveCollectionName"
                    @keyup.enter="saveCollectionName"
                    @keyup.esc="cancelEdit"
                    ref="editInputRef"
                  />
                </div>
                
                <!-- 普通显示模式 -->
                <span v-else class="node-label">{{ node.label }}</span>
                
                <span v-if="data.type === 'request' && data.request_type !== 'WEBSOCKET'" class="method-tag" :class="data.method?.toLowerCase()">
                  {{ data.method }}
                </span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧请求详情 -->
      <div class="main-content">
        <div v-if="!selectedRequest" class="empty-state">
          <el-empty :description="$t('apiTesting.interface.selectInterface')">
            <el-button type="primary" @click="createEmptyRequest">{{ $t('apiTesting.interface.createNewInterface') }}</el-button>
          </el-empty>
        </div>
        
        <div v-else class="request-detail">
          <!-- 请求基本信息 -->
          <div class="request-header">
            <div class="request-line">
              <!-- HTTP接口显示方法选择器 -->
              <el-select 
                v-if="!selectedRequest || selectedRequest.request_type !== 'WEBSOCKET'" 
                v-model="selectedRequest.method" 
                style="width: 100px;"
              >
                <el-option v-for="method in availableMethods" :key="method" :label="method" :value="method" />
              </el-select>
              
              <el-input
                v-model="selectedRequest.url"
                :placeholder="$t('apiTesting.interface.inputRequestUrl')"
                class="url-input"
                :class="{ 'websocket-url': selectedRequest && selectedRequest.request_type === 'WEBSOCKET' }"
              >
                <template #prepend>
                  <el-select v-model="selectedEnvironment" :placeholder="$t('apiTesting.interface.environment')" style="width: 120px;">
                    <el-option :label="$t('apiTesting.common.noEnvironment')" :value="null" />
                    <el-option
                      v-for="env in environments"
                      :key="env.id"
                      :label="env.name"
                      :value="env.id"
                    />
                  </el-select>
                </template>
              </el-input>

              <!-- WebSocket连接按钮 -->
              <el-button
                v-if="selectedRequest && selectedRequest.request_type === 'WEBSOCKET'"
                :type="websocketConnectionStatus === 'disconnected' ? 'primary' : 'info'"
                :loading="websocketConnectionStatus === 'connecting'"
                @click="toggleWebSocketConnection"
              >
                <span v-if="websocketConnectionStatus === 'disconnected'">{{ $t('apiTesting.interface.connect') }}</span>
                <span v-else-if="websocketConnectionStatus === 'connecting'">{{ $t('apiTesting.interface.connecting') }}</span>
                <span v-else>{{ $t('apiTesting.interface.disconnect') }}</span>
              </el-button>

              <!-- HTTP发送按钮 -->
              <el-button
                v-else
                type="primary"
                @click="sendRequest"
                :loading="sending"
              >
                {{ $t('apiTesting.interface.send') }}
              </el-button>
            </div>

            <div class="request-name">
              <el-input
                v-model="selectedRequest.name"
                :placeholder="$t('apiTesting.interface.requestName')"
                size="small"
                style="width: 300px;"
              />
              <el-button size="small" @click="saveRequest" :loading="saving" ref="saveButtonRef">
                {{ $t('apiTesting.common.save') }}
              </el-button>
            </div>
          </div>

          <!-- 请求配置 -->
          <el-tabs v-model="activeTab" class="request-tabs">
            <el-tab-pane label="Params" name="params">
              <KeyValueEditor
                v-model="selectedRequest.params"
                :placeholder-key="$t('apiTesting.interface.paramName')"
                :placeholder-value="$t('apiTesting.interface.paramValue')"
              />
            </el-tab-pane>

            <el-tab-pane label="Headers" name="headers">
              <KeyValueEditor
                ref="headersEditorRef"
                v-model="selectedRequest.headers"
                :placeholder-key="$t('apiTesting.interface.headerName')"
                :placeholder-value="$t('apiTesting.interface.headerValue')"
                @update:modelValue="onHeadersUpdate"
              />
            </el-tab-pane>
            
            <el-tab-pane label="Body" name="body" v-if="hasBody">
              <div class="body-container">
                <el-radio-group v-model="bodyType" @change="onBodyTypeChange">
                  <el-radio value="none">none</el-radio>
                  <el-radio value="form-data">form-data</el-radio>
                  <el-radio value="x-www-form-urlencoded">x-www-form-urlencoded</el-radio>
                  <el-radio value="raw">raw</el-radio>
                  <el-radio value="binary">binary</el-radio>
                </el-radio-group>
                
                <div v-if="bodyType === 'form-data'" class="body-content">
                  <KeyValueEditor
                    v-model="formData"
                    :placeholder-key="$t('apiTesting.interface.key')"
                    :placeholder-value="$t('apiTesting.interface.value')"
                    :show-file="true"
                  />
                </div>

                <div v-else-if="bodyType === 'x-www-form-urlencoded'" class="body-content">
                  <KeyValueEditor
                    v-model="formUrlEncoded"
                    :placeholder-key="$t('apiTesting.interface.key')"
                    :placeholder-value="$t('apiTesting.interface.value')"
                  />
                </div>

                <div v-else-if="bodyType === 'raw'" class="body-content">
                  <div class="raw-options">
                    <el-select v-model="rawType" style="width: 150px;">
                      <el-option label="Text" value="text" />
                      <el-option label="JSON" value="json" />
                      <el-option label="HTML" value="html" />
                      <el-option label="XML" value="xml" />
                    </el-select>
                  </div>
                  <el-input
                    ref="rawBodyInputRef"
                    v-model="rawBody"
                    type="textarea"
                    :rows="10"
                    :placeholder="$t('apiTesting.interface.inputRequestBody')"
                    class="raw-body"
                  />
                </div>
              </div>
            </el-tab-pane>
            
            <!-- HTTP接口专用标签页 -->
            <template v-if="!selectedRequest || selectedRequest.request_type !== 'WEBSOCKET'">
              <el-tab-pane label="Pre-request Script" name="pre-script">
                <el-input
                  v-model="selectedRequest.pre_request_script"
                  type="textarea"
                  :rows="10"
                  :placeholder="$t('apiTesting.interface.preRequestScript')"
                />
              </el-tab-pane>

              <el-tab-pane label="Tests" name="tests">
                <el-input
                  v-model="selectedRequest.post_request_script"
                  type="textarea"
                  :rows="10"
                  :placeholder="$t('apiTesting.interface.postRequestScript')"
                />
              </el-tab-pane>

              <el-tab-pane :label="$t('apiTesting.interface.assertions')" name="assertions">
                <div class="assertions-editor">
                  <div class="assertions-header">
                    <el-button size="small" type="primary" @click="addAssertion">
                      <el-icon><Plus /></el-icon>
                      {{ $t('apiTesting.interface.addAssertion') }}
                    </el-button>
                  </div>
                  
                  <div class="assertions-list">
                    <div 
                      v-for="(assertion, index) in selectedRequest.assertions" 
                      :key="index" 
                      class="assertion-item"
                    >
                      <div class="assertion-header">
                        <el-input
                          v-model="assertion.name"
                          :placeholder="$t('apiTesting.interface.assertionName')"
                          size="small"
                          class="assertion-name"
                        />
                        <el-button
                          size="small"
                          type="danger"
                          @click="removeAssertion(index)"
                          circle
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>

                      <div class="assertion-config">
                        <el-select
                          v-model="assertion.type"
                          :placeholder="$t('apiTesting.interface.selectAssertionType')"
                          size="small"
                          @change="onAssertionTypeChange(assertion)"
                        >
                          <el-option :label="$t('apiTesting.interface.assertionTypes.statusCode')" value="status_code" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.responseTime')" value="response_time" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.contains')" value="contains" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.jsonPath')" value="json_path" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.header')" value="header" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.equals')" value="equals" />
                        </el-select>

                        <div class="assertion-params" v-if="assertion.type">
                          <!-- 状态码断言 -->
                          <div v-if="assertion.type === 'status_code'">
                            <el-input-number
                              v-model="assertion.expected"
                              :min="100"
                              :max="599"
                              size="small"
                              :placeholder="$t('apiTesting.interface.expectedStatusCode')"
                            />
                          </div>

                          <!-- 响应时间断言 -->
                          <div v-else-if="assertion.type === 'response_time'">
                            <el-input-number
                              v-model="assertion.expected"
                              :min="1"
                              size="small"
                              :placeholder="$t('apiTesting.interface.maxResponseTime')"
                            />
                          </div>
                          
                          <!-- 包含文本断言 -->
                          <div v-else-if="assertion.type === 'contains'">
                            <el-input
                              v-model="assertion.expected"
                              :placeholder="$t('apiTesting.interface.expectedContains')"
                              size="small"
                            />
                          </div>

                          <!-- JSON路径断言 -->
                          <div v-else-if="assertion.type === 'json_path'">
                            <el-input
                              v-model="assertion.json_path"
                              :placeholder="$t('apiTesting.interface.jsonPathExpression')"
                              size="small"
                              class="assertion-input"
                            />
                            <el-input
                              v-model="assertion.expected"
                              :placeholder="$t('apiTesting.interface.expectedValue')"
                              size="small"
                              class="assertion-input"
                            />
                          </div>

                          <!-- 响应头断言 -->
                          <div v-else-if="assertion.type === 'header'">
                            <el-input
                              v-model="assertion.header_name"
                              :placeholder="$t('apiTesting.interface.headerNameLabel')"
                              size="small"
                              class="assertion-input"
                            />
                            <el-input
                              v-model="assertion.expected_value"
                              :placeholder="$t('apiTesting.interface.expectedValue')"
                              size="small"
                              class="assertion-input"
                            />
                          </div>

                          <!-- 完全匹配断言 -->
                          <div v-else-if="assertion.type === 'equals'">
                            <el-input
                              v-model="assertion.expected"
                              :placeholder="$t('apiTesting.interface.expectedMatch')"
                              size="small"
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div v-if="!selectedRequest.assertions || selectedRequest.assertions.length === 0" class="no-assertions">
                      <p>{{ $t('apiTesting.interface.noAssertions') }}</p>
                      <el-button size="small" type="primary" @click="addAssertion">
                        <el-icon><Plus /></el-icon>
                        {{ $t('apiTesting.interface.addFirstAssertion') }}
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </template>
            
            <!-- WebSocket接口专用标签页 -->
            <template v-else-if="selectedRequest && selectedRequest.request_type === 'WEBSOCKET'">
              <el-tab-pane label="Message" name="message">
                <div class="message-container">
                  <div class="message-input-section">
                    <el-select
                      v-model="websocketMessageType"
                      :placeholder="$t('apiTesting.interface.messageType')"
                      style="width: 150px; margin-bottom: 15px;"
                    >
                      <el-option label="Text" value="text" />
                      <el-option label="JSON" value="json" />
                      <el-option label="Binary" value="binary" />
                    </el-select>

                    <div v-if="websocketMessageType === 'text' || websocketMessageType === 'json'">
                      <el-input
                        v-model="websocketMessageContent"
                        type="textarea"
                        :rows="6"
                        :placeholder="$t('apiTesting.interface.inputWebSocketMessage')"
                      />
                    </div>

                    <div v-else-if="websocketMessageType === 'binary'">
                      <el-upload
                        drag
                        action="#"
                        :auto-upload="false"
                        :show-file-list="false"
                        :on-change="handleWebSocketFileUpload"
                      >
                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                        <div class="el-upload__text">
                          {{ $t('apiTesting.interface.dragBinaryFile') }}<em>{{ $t('apiTesting.interface.clickUpload') }}</em>
                        </div>
                      </el-upload>
                      <div v-if="websocketBinaryFile" class="uploaded-file">
                        <span>{{ websocketBinaryFile.name }}</span>
                        <el-button size="small" type="danger" @click="clearWebSocketBinaryFile">{{ $t('apiTesting.interface.clear') }}</el-button>
                      </div>
                    </div>

                    <div class="message-actions" style="margin-top: 15px;">
                      <el-button type="primary" @click="sendWebSocketMessage">
                        {{ $t('apiTesting.interface.sendMessage') }}
                      </el-button>
                      <el-button @click="clearWebSocketMessage">
                        {{ $t('apiTesting.interface.clearMessage') }}
                      </el-button>
                    </div>
                  </div>

                  <!-- WebSocket消息历史记录 -->
                  <div class="websocket-response-section" v-if="websocketMessages.length > 0">
                    <h3>{{ $t('apiTesting.interface.messageHistory') }}</h3>
                    <div class="websocket-messages">
                      <div
                        v-for="(msg, index) in websocketMessages.slice().reverse()"
                        :key="index"
                        class="websocket-message-item"
                        :class="msg.type"
                      >
                        <div class="message-header">
                          <span class="message-type" :class="msg.type">
                            {{ msg.type === 'sent' ? $t('apiTesting.interface.messageSent') :
                               msg.type === 'connected' ? $t('apiTesting.interface.messageConnected') :
                               msg.type === 'info' ? $t('apiTesting.interface.messageInfo') :
                               msg.type === 'error' ? $t('apiTesting.interface.messageError') : $t('apiTesting.interface.messageReceived') }}
                          </span>
                          <span class="message-time">{{ msg.timestamp }}</span>
                        </div>
                        <div class="message-content">
                          <pre v-if="msg.type === 'received' && isJsonString(msg.content)">{{ formatJson(msg.content) }}</pre>
                          <pre v-else>{{ msg.content }}</pre>
                        </div>
                      </div>
                    </div>
                    <div class="message-actions">
                      <el-button size="small" @click="clearWebSocketMessages">{{ $t('apiTesting.interface.clearHistory') }}</el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </template>
          </el-tabs>

          <!-- 响应区域 -->
          <div v-if="response" class="response-section">
            <div class="response-header">
              <h3>{{ $t('apiTesting.interface.response') }}</h3>
              <div class="response-info">
                <el-tag :type="getStatusType(response.status_code)">
                  {{ response.status_code }}
                </el-tag>
                <span class="response-time">{{ response.response_time?.toFixed(0) }}ms</span>
              </div>
            </div>

            <el-tabs v-model="responseActiveTab">
              <el-tab-pane :label="$t('apiTesting.interface.responseBody')" name="body">
                <div class="response-body">
                  <div class="response-actions">
                    <el-button-group>
                      <el-button size="small" @click="formatResponse">{{ $t('apiTesting.interface.format') }}</el-button>
                      <el-button size="small" @click="copyResponse">{{ $t('apiTesting.common.copy') }}</el-button>
                    </el-button-group>
                  </div>
                  <pre class="response-content">{{ responseBody }}</pre>
                </div>
              </el-tab-pane>

              <el-tab-pane :label="$t('apiTesting.interface.responseHeaders')" name="headers">
                <div class="response-headers">
                  <div v-for="(value, key) in response.response_data?.headers" :key="key" class="header-row">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane :label="$t('apiTesting.interface.assertionResults')" name="assertions" v-if="response.assertions_results && response.assertions_results.length > 0">
                <div class="assertions-results">
                  <div
                    v-for="(result, index) in response.assertions_results"
                    :key="index"
                    class="assertion-result-item"
                    :class="{ 'passed': result.passed, 'failed': !result.passed }"
                  >
                    <div class="assertion-result-header">
                      <el-tag :type="result.passed ? 'success' : 'danger'" size="small">
                        {{ result.passed ? $t('apiTesting.interface.passed') : $t('apiTesting.interface.failed') }}
                      </el-tag>
                      <span class="assertion-name">{{ result.name }}</span>
                    </div>
                    <div class="assertion-result-details">
                      <div class="result-row">
                        <span class="label">{{ $t('apiTesting.interface.expected') }}</span>
                        <span class="value">{{ result.expected !== null && result.expected !== undefined ? result.expected : $t('apiTesting.interface.notSet') }}</span>
                      </div>
                      <div class="result-row">
                        <span class="label">{{ $t('apiTesting.interface.actual') }}</span>
                        <span class="value">{{ result.actual !== null && result.actual !== undefined ? result.actual : $t('apiTesting.interface.notObtained') }}</span>
                      </div>
                      <div class="result-row" v-if="result.error">
                        <span class="label">{{ $t('apiTesting.interface.error') }}</span>
                        <span class="value error">{{ result.error }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建集合对话框 -->
    <el-dialog v-model="showCreateCollectionDialog" :title="$t('apiTesting.interface.createCollection')" width="500px">
      <el-form ref="collectionFormRef" :model="collectionForm" :rules="collectionRules" label-width="80px">
        <el-form-item :label="$t('apiTesting.interface.collectionName')" prop="name">
          <el-input v-model="collectionForm.name" :placeholder="$t('apiTesting.interface.inputCollectionName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.common.description')" prop="description">
          <el-input v-model="collectionForm.description" type="textarea" :rows="3" :placeholder="$t('apiTesting.common.pleaseInput')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.interface.parentCollection')" prop="parent">
          <el-select v-model="collectionForm.parent" :placeholder="$t('apiTesting.interface.selectParentCollection')" clearable>
            <el-option
              v-for="collection in flatCollections"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateCollectionDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="createCollection">{{ $t('apiTesting.common.create') }}</el-button>
      </template>
    </el-dialog>

    <!-- 编辑集合对话框 -->
    <el-dialog v-model="showEditCollectionDialog" :title="$t('apiTesting.common.edit')" width="500px">
      <el-form ref="editCollectionFormRef" :model="editCollectionForm" :rules="collectionRules" label-width="80px">
        <el-form-item :label="$t('apiTesting.interface.collectionName')" prop="name">
          <el-input v-model="editCollectionForm.name" :placeholder="$t('apiTesting.interface.inputCollectionName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.common.description')" prop="description">
          <el-input v-model="editCollectionForm.description" type="textarea" :rows="3" :placeholder="$t('apiTesting.common.pleaseInput')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.interface.parentCollection')" prop="parent">
          <el-select v-model="editCollectionForm.parent" :placeholder="$t('apiTesting.interface.selectParentCollection')" clearable>
            <el-option
              v-for="collection in flatCollections.filter(c => c.id !== editCollectionForm.id)"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditCollectionDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="updateCollection">{{ $t('apiTesting.common.save') }}</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <ul v-show="showContextMenu" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <li @click="addRequest">{{ $t('apiTesting.interface.contextMenu.addRequest') }}</li>
      <li @click="addCollection">{{ $t('apiTesting.interface.contextMenu.addSubCollection') }}</li>
      <li @click="editNode">{{ $t('apiTesting.interface.contextMenu.edit') }}</li>
      <li @click="deleteNode">{{ $t('apiTesting.interface.contextMenu.delete') }}</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, Folder, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import KeyValueEditor from './components/KeyValueEditor.vue'

const { t } = useI18n()

const treeRef = ref(null)
const expandedKeys = ref([])
const projects = ref([])
const selectedProject = ref(null)
const collections = ref([])
const flatCollections = ref([])
const environments = ref([])
const selectedEnvironment = ref(null)
const selectedRequest = ref(null)
const response = ref(null)
const sending = ref(false)
const saving = ref(false)
const activeTab = ref('params')
const responseActiveTab = ref('body')
const showCreateCollectionDialog = ref(false)
const showEditCollectionDialog = ref(false)
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const rightClickedNode = ref(null)
const headersEditorRef = ref(null)
const editingNodeId = ref(null)
const editingNodeName = ref('')
const editInputRef = ref(null)
<<<<<<< HEAD
=======
const rawBodyInputRef = ref(null)
const currentHeaders = ref({})
>>>>>>> upstream/main

// 辅助函数：将对象或数组转换为键值对数组（用于KeyValueEditor组件）
const convertObjectToKeyValueArray = (obj) => {
  if (!obj) return []
  
  // 如果已经是数组格式（新的完整格式），直接返回
  if (Array.isArray(obj)) {
    console.log('Input is already array format:', obj)
    return obj.map(item => ({
      key: item.key || '',
      value: item.value || '',
      enabled: item.enabled !== false,
      description: item.description || ''
    }))
  }
  
  // 如果是对象格式（旧的简单key-value格式），转换为数组
  if (typeof obj === 'object') {
    console.log('Converting object to array:', obj)
    return Object.entries(obj).map(([key, value]) => ({
      key,
      value: String(value),
      enabled: true,
      description: ''
    }))
  }
  
  return []
}

// 辅助函数：将键值对数组转换为对象（保存时使用）
const convertKeyValueArrayToObject = (input) => {
  console.log('convertKeyValueArrayToObject input:', input)
  
  // 如果输入已经是普通对象，直接返回
  if (input && typeof input === 'object' && !Array.isArray(input)) {
    console.log('Input is already an object, returning as-is')
    return input
  }
  
  // 如果输入是数组，转换为对象
  if (!Array.isArray(input)) return {}
  
  const obj = {}
  input.forEach(item => {
    console.log('Processing item:', item, 'enabled:', item.enabled)
    if (item.enabled !== false && item.key) {
      obj[item.key] = item.value || ''
      console.log('Added to obj:', item.key, '=', item.value)
    }
  })
  console.log('convertKeyValueArrayToObject output:', obj)
  return obj
}

const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
const websocketMethods = ['CONNECT', 'SUBSCRIBE', 'UNSUBSCRIBE', 'SEND', 'PING', 'PONG']

const availableMethods = computed(() => {
  return selectedRequest.value && selectedRequest.value.request_type === 'WEBSOCKET' 
    ? websocketMethods 
    : httpMethods
})

// WebSocket消息相关数据
const websocketMessageType = ref('text')
const websocketMessageContent = ref('')
const websocketBinaryFile = ref(null)
const websocketConnectionStatus = ref('disconnected') // disconnected, connecting, connected
const websocketConnection = ref(null)
const websocketMessages = ref([]) // WebSocket消息历史记录
const bodyType = ref('none')
const rawType = ref('json')
const formData = ref({})
const formUrlEncoded = ref({})
const rawBody = ref('')

const treeProps = {
  children: 'children',
  label: 'name'
}

const collectionForm = reactive({
  name: '',
  description: '',
  parent: null
})

const editCollectionForm = reactive({
  id: null,
  name: '',
  description: '',
  parent: null
})

const collectionRules = computed(() => ({
  name: [{ required: true, message: t('apiTesting.interface.inputCollectionName'), trigger: 'blur' }]
}))

const hasBody = computed(() => {
  return selectedRequest.value && ['POST', 'PUT', 'PATCH'].includes(selectedRequest.value.method)
})

const responseBody = computed(() => {
  if (!response.value?.response_data) return ''
  
  try {
    if (response.value.response_data.json) {
      return JSON.stringify(response.value.response_data.json, null, 2)
    } else {
      return response.value.response_data.body || ''
    }
  } catch (e) {
    return response.value.response_data.body || ''
  }
})

const getStatusType = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'danger'
  return 'info'
}

const loadProjects = async () => {
  try {
    const res = await api.get('/api-testing/projects/')
    projects.value = res.data.results || res.data
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
      await onProjectChange()
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadProjects'))
  }
}

const loadCollections = async (preserveExpandState = true) => {
  if (!selectedProject.value) return

  try {
    const res = await api.get('/api-testing/collections/', {
      params: { project: selectedProject.value }
    })
    const collectionsData = res.data.results || res.data

    // 构建树形结构
    collections.value = buildTree(collectionsData)
    flatCollections.value = collectionsData

    // 加载每个集合的请求
    await loadRequests()

    // 如果不保留展开状态，清空展开键
    if (!preserveExpandState) {
      expandedKeys.value = []
    }

  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadCollections'))
  }
}

const loadRequests = async () => {
  if (!selectedProject.value) return

  try {
    const res = await api.get('/api-testing/requests/')
    const requests = res.data.results || res.data

    // 清空所有集合的子节点（请求）
    collections.value.forEach(collection => {
      clearCollectionChildren(collection)
    })

    // 过滤掉之前的未分类接口（type 为 request 且 id 为 null 的项）
    collections.value = collections.value.filter(item => item.type === 'collection')

    // 将请求添加到对应集合中或直接添加到根级别
    requests.forEach(request => {
      if (request.collection) {
        // 有关联集合的请求，添加到对应集合下
        const collection = findCollectionById(collections.value, request.collection)
        if (collection) {
          if (!collection.children) collection.children = []
          collection.children.push({
            ...request,
            type: 'request',
            name: request.name
          })
        }
      } else {
        // 未关联集合的请求，直接添加到集合列表的根级别
        collections.value.push({
          ...request,
          type: 'request',
          name: request.name
        })
      }
    })
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadRequests'))
  }
}

const clearCollectionChildren = (collection) => {
  if (collection.children) {
    collection.children = collection.children.filter(child => child.type === 'collection')
    collection.children.forEach(child => clearCollectionChildren(child))
  }
}

const loadEnvironments = async () => {
  try {
    // 获取全局环境 + 当前项目环境，不传递project参数
    const res = await api.get('/api-testing/environments/')
    const allEnvironments = res.data.results || res.data

    // 过滤全局环境和当前项目环境
    environments.value = allEnvironments.filter(env =>
      env.scope === 'GLOBAL' ||
      (env.scope === 'LOCAL' && (!selectedProject.value || env.project === selectedProject.value))
    )
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadEnvironments'))
  }
}

const buildTree = (items) => {
  const map = {}
  const roots = []
  
  items.forEach(item => {
    map[item.id] = { ...item, type: 'collection', children: [] }
  })
  
  items.forEach(item => {
    if (item.parent) {
      if (map[item.parent]) {
        map[item.parent].children.push(map[item.id])
      }
    } else {
      roots.push(map[item.id])
    }
  })
  
  return roots
}

const findCollectionById = (collections, id) => {
  for (const collection of collections) {
    if (collection.id === id) return collection
    if (collection.children) {
      const found = findCollectionById(collection.children, id)
      if (found) return found
    }
  }
  return null
}

const onProjectChange = async () => {
  await Promise.all([loadCollections(false), loadEnvironments()])
}

const onNodeClick = (data) => {
  if (data.type === 'request') {
    console.log('onNodeClick - original data.headers:', data.headers)
    const convertedHeaders = convertObjectToKeyValueArray(data.headers || {})
    console.log('onNodeClick - converted headers:', convertedHeaders)
    
    // 初始化currentHeaders
    currentHeaders.value = data.headers || {}
    console.log('onNodeClick - initialized currentHeaders:', currentHeaders.value)
    
    selectedRequest.value = {
      ...data,
      params: convertObjectToKeyValueArray(data.params || {}),
      headers: convertedHeaders,
      body: data.body || {},
      auth: data.auth || {}
    }
    
    console.log('onNodeClick - selectedRequest.value.headers:', selectedRequest.value.headers)

    // 解析body数据
    if (data.body && data.body.type) {
      if (data.body.type === 'json' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'json'
        rawBody.value = JSON.stringify(data.body.data, null, 2)
      } else if (data.body.type === 'raw' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'text'
        rawBody.value = data.body.data
      } else if (data.body.type === 'form-data') {
        bodyType.value = 'form-data'
        formData.value = data.body.data || {}
      } else if (data.body.type === 'x-www-form-urlencoded') {
        bodyType.value = 'x-www-form-urlencoded'
        formUrlEncoded.value = data.body.data || {}
      } else if (data.body.type === 'binary') {
        bodyType.value = 'binary'
      } else {
        bodyType.value = 'none'
        rawBody.value = ''
      }
    } else {
      bodyType.value = 'none'
      rawBody.value = ''
    }
    
    response.value = null
  }
}

const onNodeRightClick = (event, data) => {
  event.preventDefault()
  rightClickedNode.value = data
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  showContextMenu.value = true
  
  nextTick(() => {
    document.addEventListener('click', hideContextMenu)
  })
}

const hideContextMenu = () => {
  showContextMenu.value = false
  document.removeEventListener('click', hideContextMenu)
}

const startEditCollection = (collection) => {
  editingNodeId.value = collection.id
  editingNodeName.value = collection.name
  nextTick(() => {
    if (editInputRef.value) {
      editInputRef.value.focus()
    }
  })
}

const saveCollectionName = async () => {
  if (!editingNodeId.value || !editingNodeName.value.trim()) {
    cancelEdit()
    return
  }

  try {
    const collection = flatCollections.value.find(c => c.id === editingNodeId.value)
    if (!collection) {
      ElMessage.error(t('apiTesting.messages.error.operationFailed'))
      cancelEdit()
      return
    }

    const data = {
      name: editingNodeName.value.trim(),
      description: collection.description,
      parent: collection.parent,
      project: selectedProject.value
    }

    await api.put(`/api-testing/collections/${editingNodeId.value}/`, data)
    
    // 直接更新本地数据，避免重新加载
    const updateCollectionName = (collections, id, newName) => {
      for (const collection of collections) {
        // 只更新集合类型的节点，跳过接口类型的节点
        if (collection.type === 'collection' && collection.id === id) {
          collection.name = newName
          return true
        }
        if (collection.children && updateCollectionName(collection.children, id, newName)) {
          return true
        }
      }
      return false
    }
    
    // 更新树中的集合名称
    updateCollectionName(collections.value, editingNodeId.value, editingNodeName.value.trim())
    
    // 更新平均集合列表
    const flatCollection = flatCollections.value.find(c => c.id === editingNodeId.value)
    if (flatCollection) {
      flatCollection.name = editingNodeName.value.trim()
    }
    
    ElMessage.success(t('apiTesting.messages.success.collectionNameUpdated'))
    cancelEdit()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.updateFailed'))
    cancelEdit()
  }
}

const cancelEdit = () => {
  editingNodeId.value = null
  editingNodeName.value = ''
}

const onNodeExpand = (data) => {
  if (!expandedKeys.value.includes(data.id)) {
    expandedKeys.value.push(data.id)
  }
}

const onNodeCollapse = (data) => {
  const index = expandedKeys.value.indexOf(data.id)
  if (index > -1) {
    expandedKeys.value.splice(index, 1)
  }
}

const addRequest = () => {
  // 创建新请求
  const newRequest = {
    name: t('apiTesting.interface.newRequest'),
    method: 'GET',
    url: '',
    headers: {},
    params: {},
    body: {},
    collection: rightClickedNode.value.type === 'collection' ? rightClickedNode.value.id : rightClickedNode.value.collection,
    type: 'request'
  }
  selectedRequest.value = newRequest
  hideContextMenu()
}

const addCollection = () => {
  collectionForm.parent = rightClickedNode.value.type === 'collection' ? rightClickedNode.value.id : null
  showCreateCollectionDialog.value = true
  hideContextMenu()
}

const editNode = () => {
  if (rightClickedNode.value.type === 'request') {
    // 使用与onNodeClick相同的逻辑来正确设置selectedRequest
    const data = rightClickedNode.value
    console.log('editNode - original data.headers:', data.headers)
    const convertedHeaders = convertObjectToKeyValueArray(data.headers || {})
    console.log('editNode - converted headers:', convertedHeaders)
    
    // 初始化currentHeaders
    currentHeaders.value = data.headers || {}
    console.log('editNode - initialized currentHeaders:', currentHeaders.value)
    
    selectedRequest.value = {
      ...data,
      params: convertObjectToKeyValueArray(data.params || {}),
      headers: convertedHeaders,
      body: data.body || {},
      auth: data.auth || {}
    }
    
    console.log('editNode - selectedRequest.value.headers:', selectedRequest.value.headers)

    // 解析body数据
    if (data.body && data.body.type) {
      if (data.body.type === 'json' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'json'
        rawBody.value = JSON.stringify(data.body.data, null, 2)
      } else if (data.body.type === 'raw' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'text'
        rawBody.value = data.body.data
      } else if (data.body.type === 'form-data') {
        bodyType.value = 'form-data'
        formData.value = data.body.data || {}
      } else if (data.body.type === 'x-www-form-urlencoded') {
        bodyType.value = 'x-www-form-urlencoded'
        formUrlEncoded.value = data.body.data || {}
      } else if (data.body.type === 'binary') {
        bodyType.value = 'binary'
      } else {
        bodyType.value = 'none'
        rawBody.value = ''
      }
    } else {
      bodyType.value = 'none'
      rawBody.value = ''
    }
    
    response.value = null
  } else if (rightClickedNode.value.type === 'collection') {
    // 打开集合编辑对话框
    const collection = rightClickedNode.value
    editCollectionForm.id = collection.id
    editCollectionForm.name = collection.name
    editCollectionForm.description = collection.description
    editCollectionForm.parent = collection.parent
    showEditCollectionDialog.value = true
  }
  hideContextMenu()
}

const deleteNode = async () => {
  if (!rightClickedNode.value) {
    hideContextMenu()
    return
  }

  const nodeType = rightClickedNode.value.type
  const nodeName = rightClickedNode.value.name

  // 显示确认对话框
  try {
    const typeText = nodeType === 'collection' ? t('apiTesting.interface.collection') : t('apiTesting.interface.request')
    const extra = nodeType === 'collection' ? t('apiTesting.interface.deleteCollectionExtra') : ''
    await ElMessageBox.confirm(
      t('apiTesting.interface.confirmDeleteNode', { type: typeText, name: nodeName, extra: extra }),
      t('apiTesting.messages.confirm.deleteTitle'),
      {
        confirmButtonText: t('apiTesting.interface.confirmDeleteBtn'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 用户确认删除，执行删除操作
    if (nodeType === 'collection') {
      await deleteCollection(rightClickedNode.value.id)
    } else if (nodeType === 'request') {
      await deleteRequest(rightClickedNode.value.id)
    }
  } catch (error) {
    // 用户取消删除或删除失败，不做任何处理
    console.log('删除操作被取消或失败:', error)
  }
  
  hideContextMenu()
}

const deleteCollection = async (collectionId) => {
  try {
    await api.delete(`/api-testing/collections/${collectionId}/`)
    ElMessage.success(t('apiTesting.messages.success.collectionDeleted'))
    
    // 如果当前选中的请求属于被删除的集合，清空选中状态
    if (selectedRequest.value && selectedRequest.value.collection === collectionId) {
      selectedRequest.value = null
      response.value = null
    }
    
    // 直接从树中移除集合，而不是重新加载
    const removeCollectionFromTree = (collections, id) => {
      for (let i = 0; i < collections.length; i++) {
        if (collections[i].id === id) {
          collections.splice(i, 1)
          return true
        }
        if (collections[i].children && removeCollectionFromTree(collections[i].children, id)) {
          return true
        }
      }
      return false
    }
    
    removeCollectionFromTree(collections.value, collectionId)
    
    // 从平集合列表中移除
    const index = flatCollections.value.findIndex(c => c.id === collectionId)
    if (index > -1) {
      flatCollections.value.splice(index, 1)
    }
    
    // 从展开键中移除
    const expandedIndex = expandedKeys.value.indexOf(collectionId)
    if (expandedIndex > -1) {
      expandedKeys.value.splice(expandedIndex, 1)
    }
    
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    console.error('Delete collection error:', error)
  }
}

const deleteRequest = async (requestId) => {
  try {
    await api.delete(`/api-testing/requests/${requestId}/`)
    ElMessage.success(t('apiTesting.messages.success.interfaceDeleted'))
    
    // 如果当前选中的是被删除的请求，清空选中状态
    if (selectedRequest.value && selectedRequest.value.id === requestId) {
      selectedRequest.value = null
      response.value = null
    }
    
    // 直接从树中移除请求，而不是重新加载
    const removeRequestFromTree = (collections, requestId) => {
      for (const collection of collections) {
        if (collection.children) {
          const requestIndex = collection.children.findIndex(child => child.type === 'request' && child.id === requestId)
          if (requestIndex > -1) {
            collection.children.splice(requestIndex, 1)
            return true
          }
        }
        if (collection.children && removeRequestFromTree(collection.children, requestId)) {
          return true
        }
      }
      return false
    }
    
    removeRequestFromTree(collections.value, requestId)
    
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    console.error('Delete request error:', error)
  }
}

const createCollection = async () => {
  try {
    const data = {
      ...collectionForm,
      project: selectedProject.value
    }
    const res = await api.post('/api-testing/collections/', data)
    const newCollection = res.data

    ElMessage.success(t('apiTesting.messages.success.collectionCreated'))
    showCreateCollectionDialog.value = false
    Object.assign(collectionForm, { name: '', description: '', parent: null })
    
    // 直接添加到本地数据，避免重新加载
    const newTreeNode = {
      ...newCollection,
      type: 'collection',
      children: []
    }
    
    // 添加到平集合列表
    flatCollections.value.push(newCollection)
    
    // 添加到树结构
    if (newCollection.parent) {
      // 找到父节点并添加
      const findAndAddToParent = (collections, parentId, newNode) => {
        for (const collection of collections) {
          if (collection.id === parentId) {
            if (!collection.children) collection.children = []
            collection.children.push(newNode)
            return true
          }
          if (collection.children && findAndAddToParent(collection.children, parentId, newNode)) {
            return true
          }
        }
        return false
      }
      
      findAndAddToParent(collections.value, newCollection.parent, newTreeNode)
      
      // 自动展开父节点
      if (!expandedKeys.value.includes(newCollection.parent)) {
        expandedKeys.value.push(newCollection.parent)
      }
    } else {
      // 添加到根级
      collections.value.push(newTreeNode)
    }
    
    // 自动展开新创建的集合
    if (!expandedKeys.value.includes(newCollection.id)) {
      expandedKeys.value.push(newCollection.id)
    }
    
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.createFailed'))
  }
}

const updateCollection = async () => {
  try {
    const data = {
      name: editCollectionForm.name,
      description: editCollectionForm.description,
      parent: editCollectionForm.parent,
      project: selectedProject.value
    }
    await api.put(`/api-testing/collections/${editCollectionForm.id}/`, data)
    
    ElMessage.success(t('apiTesting.messages.success.collectionUpdated'))
    showEditCollectionDialog.value = false
    
    // 更新本地树数据
    const updateCollectionInTree = (collections, id, newData) => {
      for (const collection of collections) {
        if (collection.id === id) {
          collection.name = newData.name
          collection.description = newData.description
          collection.parent = newData.parent
          return true
        }
        if (collection.children && updateCollectionInTree(collection.children, id, newData)) {
          return true
        }
      }
      return false
    }
    
    updateCollectionInTree(collections.value, editCollectionForm.id, data)
    
    // 更新平集合列表
    const flatCollection = flatCollections.value.find(c => c.id === editCollectionForm.id)
    if (flatCollection) {
      flatCollection.name = editCollectionForm.name
      flatCollection.description = editCollectionForm.description
      flatCollection.parent = editCollectionForm.parent
    }
    
    // 重置表单
    Object.assign(editCollectionForm, { id: null, name: '', description: '', parent: null })
    
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.updateFailed'))
  }
}

// 断言相关方法
const addAssertion = () => {
  if (!selectedRequest.value.assertions) {
    selectedRequest.value.assertions = []
  }

  selectedRequest.value.assertions.push({
    name: `${t('apiTesting.interface.assertion')}${selectedRequest.value.assertions.length + 1}`,
    type: '',
    expected: null,
    json_path: '',
    header_name: ''
  })
}

const removeAssertion = (index) => {
  if (selectedRequest.value.assertions) {
    selectedRequest.value.assertions.splice(index, 1)
  }
}

const onAssertionTypeChange = (assertion) => {
  // 重置断言参数
  assertion.expected = null
  assertion.json_path = ''
  assertion.header_name = ''
}

// WebSocket消息处理函数
const handleWebSocketFileUpload = (file) => {
  websocketBinaryFile.value = file.raw
  return false
}

const clearWebSocketBinaryFile = () => {
  websocketBinaryFile.value = null
}

const sendWebSocketMessage = () => {
  if (websocketConnectionStatus.value !== 'connected') {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseConnect'))
    return
  }

  if (!websocketConnection.value) {
    ElMessage.error(t('apiTesting.messages.error.connectFailed'))
    return
  }

  try {
    let messageToSend = ''

    if (websocketMessageType.value === 'text' || websocketMessageType.value === 'json') {
      messageToSend = websocketMessageContent.value
    } else if (websocketMessageType.value === 'binary' && websocketBinaryFile.value) {
      // 对于二进制文件，需要读取文件内容
      const reader = new FileReader()
      reader.onload = (e) => {
        websocketConnection.value.send(e.target.result)
        addWebSocketMessage('sent', '[Binary Data]')
        ElMessage.success(t('apiTesting.messages.success.binaryMessageSent'))
      }
      reader.onerror = () => {
        ElMessage.error(t('apiTesting.messages.error.readFileFailed'))
      }
      reader.readAsArrayBuffer(websocketBinaryFile.value)
      return
    } else {
      ElMessage.warning(t('apiTesting.messages.warning.pleaseInputContent'))
      return
    }

    websocketConnection.value.send(messageToSend)
    addWebSocketMessage('sent', messageToSend)
    ElMessage.success(t('apiTesting.messages.success.messageSent'))

  } catch (error) {
    const errorMsg = t('apiTesting.messages.error.sendFailed') + ': ' + error.message
    addWebSocketMessage('error', errorMsg)
    ElMessage.error(errorMsg)
  }
}

const clearWebSocketMessage = () => {
  websocketMessageContent.value = ''
  websocketBinaryFile.value = null
  websocketMessageType.value = 'text'
}

// WebSocket消息历史记录相关方法
const addWebSocketMessage = (type, content) => {
  const timestamp = new Date().toLocaleTimeString()
  websocketMessages.value.push({
    type,
    content,
    timestamp
  })
}

const clearWebSocketMessages = () => {
  websocketMessages.value = []
}

const isJsonString = (str) => {
  try {
    JSON.parse(str)
    return true
  } catch (e) {
    return false
  }
}

const formatJson = (str) => {
  try {
    return JSON.stringify(JSON.parse(str), null, 2)
  } catch (e) {
    return str
  }
}

// WebSocket连接管理函数
const toggleWebSocketConnection = () => {
  if (websocketConnectionStatus.value === 'disconnected') {
    connectWebSocket()
  } else {
    disconnectWebSocket()
  }
}

const connectWebSocket = () => {
  if (!selectedRequest.value || !selectedRequest.value.url) {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseInputUrl'))
    return
  }

  websocketConnectionStatus.value = 'connecting'

  try {
    // 替换环境变量
    let url = selectedRequest.value.url
    if (selectedEnvironment.value) {
      const env = environments.value.find(e => e.id === selectedEnvironment.value)
      if (env && env.variables) {
        Object.entries(env.variables).forEach(([key, value]) => {
          url = url.replace(`{{${key}}}`, value.currentValue || value.initialValue || '')
        })
      }
    }

    // 创建WebSocket连接
    websocketConnection.value = new WebSocket(url)

    websocketConnection.value.onopen = () => {
      websocketConnectionStatus.value = 'connected'
      // 添加连接成功的特殊消息
      addWebSocketMessage('connected', t('apiTesting.messages.info.websocketConnectedTo', { url }))
      ElMessage.success(t('apiTesting.messages.success.connect'))
    }

    websocketConnection.value.onmessage = (event) => {
      // 处理接收到的消息
      console.log('WebSocket message received:', event.data)
      addWebSocketMessage('received', event.data)
      ElMessage.info(t('apiTesting.messages.info.websocketMessageReceived'))
    }

    websocketConnection.value.onclose = () => {
      websocketConnectionStatus.value = 'disconnected'
      addWebSocketMessage('info', t('apiTesting.messages.info.websocketClosed'))
      ElMessage.info(t('apiTesting.messages.info.websocketClosed'))
    }

    websocketConnection.value.onerror = (error) => {
      websocketConnectionStatus.value = 'disconnected'
      const errorMsg = t('apiTesting.messages.error.websocketError') + ': ' + (error.message || '')
      addWebSocketMessage('error', errorMsg)
      ElMessage.error(errorMsg)
    }

  } catch (error) {
    websocketConnectionStatus.value = 'disconnected'
    const errorMsg = t('apiTesting.messages.error.connectFailed') + ': ' + error.message
    addWebSocketMessage('error', errorMsg)
    ElMessage.error(errorMsg)
  }
}

const disconnectWebSocket = () => {
  if (websocketConnection.value) {
    websocketConnection.value.close()
    websocketConnection.value = null
  }
  websocketConnectionStatus.value = 'disconnected'
  // 清空消息历史
  clearWebSocketMessages()
}

const createEmptyRequest = async () => {
  // 检查是否有选中的项目
  if (!selectedProject.value) {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseSelectProject'))
    return
  }

  // 检查是否有可用的集合
  if (!flatCollections.value || flatCollections.value.length === 0) {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseCreateCollection'))
    return
  }
  
  // 使用第一个集合作为默认集合
  const defaultCollection = flatCollections.value[0]
  
  // 获取当前项目信息
  const currentProject = projects.value.find(p => p.id === selectedProject.value)
  const isWebSocketProject = currentProject && currentProject.project_type === 'WEBSOCKET'
  
  saving.value = true
  try {
    // 创建一个空的接口，参照"获取宠物列表"的样式
    const data = {
      name: '新建接口',
      method: isWebSocketProject ? 'CONNECT' : 'GET',
      url: isWebSocketProject ? 'ws://{{host}}/websocket' : '{{base_url}}/api/new-endpoint',
      description: '',
      collection: defaultCollection.id,
      project: selectedProject.value,
      request_type: isWebSocketProject ? 'WEBSOCKET' : 'HTTP',
      params: {},
      headers: isWebSocketProject ? {} : {
        'Content-Type': 'application/json'
      },
      body: {},
      auth: {},
      pre_request_script: '',
      post_request_script: ''
    }
    
    const res = await api.post('/api-testing/requests/', data)
    ElMessage.success(t('apiTesting.messages.success.create'))

    // 重新加载集合和请求
    await Promise.all([loadCollections(), loadRequests()])
    
    // 自动选中新创建的请求并进入编辑状态
    selectedRequest.value = {
      id: res.data.id,
      name: res.data.name,
      method: res.data.method,
      url: res.data.url,
      description: res.data.description || '',
      collection: res.data.collection,
      project: res.data.project,
      request_type: res.data.request_type,
      params: convertObjectToKeyValueArray(res.data.params || {}),
      headers: convertObjectToKeyValueArray(res.data.headers || {}),
      body: res.data.body || {},
      auth: res.data.auth || {},
      pre_request_script: res.data.pre_request_script || '',
      post_request_script: res.data.post_request_script || ''
    }
    
    // 默认进入params标签页
    activeTab.value = 'params'
    
    // 初始化body相关变量
    bodyType.value = 'none'
    rawType.value = 'json'
    formData.value = {}
    formUrlEncoded.value = {}
    rawBody.value = ''
    
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.createFailed'))
    console.error('Create request error:', error)
  } finally {
    saving.value = false
  }
}

const sendRequest = async () => {
  if (!selectedRequest.value) return

  // 检查是否为WebSocket接口
  if (selectedRequest.value.request_type === 'WEBSOCKET') {
    ElMessage.warning(t('apiTesting.messages.warning.websocketNotSupported'))
    return
  }

  // 检查是否选择了环境
  if (!selectedEnvironment.value) {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseSelectEnvironment'))
    return
  }
  
  sending.value = true
  try {
    // 发送请求前先自动保存当前的修改
    await saveRequest()

    // 准备请求体数据
    let bodyData = {}
    if (hasBody.value) {
      if (bodyType.value === 'none') {
        bodyData = {}
      } else if (bodyType.value === 'raw' && rawBody.value) {
        if (rawType.value === 'json') {
          try {
            bodyData = {
              type: 'json',
              data: JSON.parse(rawBody.value)
            }
          } catch (e) {
            bodyData = {
              type: 'raw',
              data: rawBody.value
            }
          }
        } else {
          bodyData = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else if (bodyType.value === 'form-data') {
        bodyData = {
          type: 'form-data',
          data: formData.value || {}
        }
      } else if (bodyType.value === 'x-www-form-urlencoded') {
        bodyData = {
          type: 'x-www-form-urlencoded',
          data: formUrlEncoded.value || {}
        }
      } else if (bodyType.value === 'binary') {
        bodyData = {
          type: 'binary',
          data: null
        }
      }
    }
    
    const requestData = {
      ...selectedRequest.value,
      params: convertKeyValueArrayToObject(selectedRequest.value.params || []),
      headers: selectedRequest.value.headers,  // 现在直接使用数组格式
      body: bodyData,
      environment_id: selectedEnvironment.value
    }
    
    const res = await api.post(`/api-testing/requests/${selectedRequest.value.id}/execute/`, requestData)
    response.value = res.data
    ElMessage.success(t('apiTesting.messages.success.requestSent'))
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.requestFailed'))
    if (error.response?.data) {
      response.value = error.response.data
    }
  } finally {
    sending.value = false
  }
}

// 存储最新的headers数据
const currentHeaders = ref({})

const onHeadersUpdate = (newHeaders) => {
  console.log('Headers updated:', newHeaders)
  currentHeaders.value = newHeaders
  if (selectedRequest.value) {
    // 强制更新整个selectedRequest对象以触发响应式更新
    selectedRequest.value = {
      ...selectedRequest.value,
      headers: newHeaders
    }
    console.log('Updated selectedRequest.headers:', selectedRequest.value.headers)
  }
}

const saveRequest = async () => {
  if (!selectedRequest.value) return

  saving.value = true
  try {
    // 准备保存的数据
    let bodyData = {}

    if (hasBody.value) {
      if (bodyType.value === 'none') {
        bodyData = {}
      } else if (bodyType.value === 'raw' && rawBody.value) {
        if (rawType.value === 'json') {
          try {
            bodyData = {
              type: 'json',
              data: JSON.parse(rawBody.value)
            }
          } catch (e) {
            bodyData = {
              type: 'raw',
              data: rawBody.value
            }
          }
        } else {
          bodyData = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else if (bodyType.value === 'form-data') {
        // 处理 form-data 类型
        bodyData = {
          type: 'form-data',
          data: formData.value || {}
        }
      } else if (bodyType.value === 'x-www-form-urlencoded') {
        // 处理 x-www-form-urlencoded 类型
        bodyData = {
          type: 'x-www-form-urlencoded',
          data: formUrlEncoded.value || {}
        }
      } else if (bodyType.value === 'binary') {
        // 处理 binary 类型
        bodyData = {
          type: 'binary',
          data: null
        }
      }
    }
    
    // 直接从KeyValueEditor组件获取当前headers（完整数组格式）
    let finalHeaders = []
    console.log('headersEditorRef.value:', headersEditorRef.value)
    if (headersEditorRef.value) {
      // 直接访问KeyValueEditor的rows数据，保持完整的数组格式
      const rows = headersEditorRef.value.rows || []
      console.log('Direct access to headers rows:', rows)
      finalHeaders = rows
        .filter(row => row.enabled && row.key && row.key.trim())
        .map(row => ({
          key: row.key.trim(),
          value: row.value || '',
          description: row.description || '',
          enabled: row.enabled !== false
        }))
      console.log('Final headers array format:', finalHeaders)
    } else {
      console.log('headersEditorRef.value is null or undefined')
      // 如果无法获取，使用selectedRequest中的headers
      if (selectedRequest.value.headers && Array.isArray(selectedRequest.value.headers)) {
        finalHeaders = selectedRequest.value.headers.filter(item => item.enabled && item.key)
      }
    }
    
    console.log('Final headers to save:', finalHeaders)
    console.log('selectedRequest.value.params:', selectedRequest.value.params)
    
    const data = {
      ...selectedRequest.value,
      params: convertKeyValueArrayToObject(selectedRequest.value.params || []),
      headers: finalHeaders,  // 保存完整的数组格式，包含description
      body: bodyData
    }
    
    console.log('Data being sent to backend:', data)
    
    console.log('Final save data:', data)
    console.log('Headers being saved:', data.headers)
    
    if (selectedRequest.value.id) {
      await api.put(`/api-testing/requests/${selectedRequest.value.id}/`, data)
      
      // 更新树中的请求名称，避免重新加载
      const updateRequestName = (collections, requestId, newName) => {
        for (const collection of collections) {
          if (collection.children) {
            const request = collection.children.find(child => child.type === 'request' && child.id === requestId)
            if (request) {
              request.name = newName
              return true
            }
          }
          if (collection.children && updateRequestName(collection.children, requestId, newName)) {
            return true
          }
        }
        return false
      }
      
      updateRequestName(collections.value, selectedRequest.value.id, selectedRequest.value.name)
    } else {
      const res = await api.post('/api-testing/requests/', data)
      selectedRequest.value.id = res.data.id
      // 新建的请求需要重新加载树以显示新请求
      await loadCollections()
    }

    ElMessage.success(t('apiTesting.messages.success.save'))
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.saveFailed'))
  } finally {
    saving.value = false
  }
}

const onBodyTypeChange = () => {
  if (bodyType.value === 'raw') {
    rawType.value = 'json'
    rawBody.value = ''
  }
}

const formatResponse = () => {
  // 格式化响应内容
  try {
    if (response.value?.response_data?.json) {
      response.value.response_data.body = JSON.stringify(response.value.response_data.json, null, 2)
    }
  } catch (e) {
    ElMessage.error(t('apiTesting.messages.error.formatFailed'))
  }
}

const copyResponse = () => {
  if (responseBody.value) {
    navigator.clipboard.writeText(responseBody.value)
    ElMessage.success(t('apiTesting.messages.success.copiedToClipboard'))
  }
}

<<<<<<< HEAD
onMounted(() => {
  loadProjects()
=======
const evaluateJsonPath = () => {
  if (!response.value || !response.value.response_data || !response.value.response_data.json || !jsonPathExpression.value) {
    jsonPathResult.value = null
    return
  }

  try {
    // 简单的JSONPath实现
    const json = response.value.response_data.json
    let result = json

    // 解析JSONPath表达式
    const parts = jsonPathExpression.value.split('.').filter(p => p)

    for (const part of parts) {
      if (part === '$') {
        result = json
      } else if (part.includes('[')) {
        // 处理数组索引
        const [arrayName, indexStr] = part.split('[')
        const index = parseInt(indexStr.replace(']', ''))
        result = result[arrayName][index]
      } else {
        result = result[part]
      }
    }

    jsonPathResult.value = JSON.stringify(result, null, 2)
  } catch (e) {
    jsonPathResult.value = 'JSONPath表达式错误'
  }
}

const copyJsonPathResult = () => {
  if (jsonPathResult.value) {
    navigator.clipboard.writeText(jsonPathResult.value)
    ElMessage.success('已复制到剪贴板')
  }
}

const formatAssertionValue = (value) => {
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2)
  }
  return value
}

const createCollection = async () => {
  if (!collectionForm.name.trim()) {
    ElMessage.warning('请输入集合名称')
    return
  }

  try {
    const response = await api.post('/api-testing/collections/', {
      ...collectionForm,
      project: selectedProject.value
    })
    ElMessage.success('创建成功')
    await loadCollections(selectedProject.value)
    showCreateCollectionDialog.value = false
    collectionForm.name = ''
    collectionForm.description = ''
    collectionForm.parent = null
  } catch (error) {
    ElMessage.error('创建失败')
    console.error('创建失败:', error)
  }
}

const updateCollection = async () => {
  if (!editCollectionForm.name.trim()) {
    ElMessage.warning('请输入集合名称')
    return
  }

  try {
    await api.put(`/api-testing/collections/${editCollectionForm.id}/`, editCollectionForm)
    ElMessage.success('更新成功')
    await loadCollections(selectedProject.value)
    showEditCollectionDialog.value = false
  } catch (error) {
    ElMessage.error('更新失败')
    console.error('更新失败:', error)
  }
}

const importCurl = () => {
  // 清空上次的 curl 命令
  curlCommand.value = ''
  showCurlImportDialog.value = true
}

const parseAndImportCurl = async () => {
  if (!curlCommand.value.trim()) {
    ElMessage.warning('请输入CURL命令')
    return
  }

  try {
    const requestModel = await RequestModelParser.parseCurl(curlCommand.value)

    if (!selectedRequest.value) {
      createEmptyRequest()
    }

    // 回填基本字段
    selectedRequest.value.method = requestModel.method
    selectedRequest.value.url = requestModel.baseURL + requestModel.path
    selectedRequest.value.headers = requestModel.headers
    selectedRequest.value.params = requestModel.query

    // 回填 body 相关字段
    if (requestModel.body.mode !== 'none') {
      if (requestModel.body.mode === 'json') {
        bodyType.value = 'raw'
        rawType.value = 'json'
        rawBody.value = requestModel.body.json || ''
      } else if (requestModel.body.mode === 'raw') {
        bodyType.value = 'raw'
        rawType.value = 'text'
        rawBody.value = requestModel.body.raw || ''
      } else if (requestModel.body.mode === 'formdata') {
        bodyType.value = 'form-data'
        formData.value = requestModel.body.formdata || []
      } else if (requestModel.body.mode === 'urlencoded') {
        bodyType.value = 'x-www-form-urlencoded'
        formUrlEncoded.value = requestModel.body.urlencoded || []
      }
    }

    showCurlImportDialog.value = false
    ElMessage.success('导入成功')
  } catch (error) {
    ElMessage.error('解析CURL命令失败')
    console.error('解析CURL命令失败:', error)
  }
}

// 辅助函数：将对象格式转换为数组格式
const convertToArrayFormat = (data) => {
  if (!data) return []
  // 如果已经是数组格式，直接返回
  if (Array.isArray(data)) return data
  // 如果是对象格式，转换为数组格式
  if (typeof data === 'object') {
    return Object.entries(data).map(([key, value]) => ({
      key,
      value: typeof value === 'object' ? JSON.stringify(value) : String(value),
      enabled: true
    }))
  }
  return []
}

const exportRequest = () => {
  if (!selectedRequest.value) return

  try {
    let baseURL = ''
    let path = ''

    if (selectedRequest.value.url) {
      try {
        const url = new URL(selectedRequest.value.url)
        baseURL = `${url.protocol}//${url.host}`
        path = url.pathname
      } catch (error) {
        baseURL = selectedRequest.value.url
        path = ''
      }
    }

    const requestModel = {
      method: selectedRequest.value?.method || 'GET',
      baseURL: baseURL,
      path: path,
      query: convertToArrayFormat(selectedRequest.value?.params),
      headers: convertToArrayFormat(selectedRequest.value?.headers),
      body: {
        mode: 'none',
        raw: rawBody.value || ''
      },
      timeout: 30000
    }

    const curlCommand = RequestModelParser.toCurl(requestModel)
    navigator.clipboard.writeText(curlCommand)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出失败:', error)
  }
}

const generateCode = async (language) => {
  if (!selectedRequest.value) return

  if (!selectedRequest.value.url) {
    ElMessage.warning('请求URL不能为空')
    return
  }

  try {
    // 更新语言选择器的值
    codeLanguage.value = language

    // 构建完整的 requestModel 对象
    let bodyMode = 'none'

    if (bodyType.value === 'raw') {
      bodyMode = rawType.value === 'json' ? 'json' : 'raw'
    } else if (bodyType.value === 'form-data') {
      bodyMode = 'formdata'
    } else if (bodyType.value === 'x-www-form-urlencoded') {
      bodyMode = 'urlencoded'
    } else if (bodyType.value === 'binary') {
      bodyMode = 'binary'
    }

    // 解析 URL 获取 baseURL 和 path
    let baseURL = ''
    let path = ''
    try {
      const url = new URL(selectedRequest.value.url)
      baseURL = `${url.protocol}//${url.host}`
      path = url.pathname
    } catch (error) {
      // 如果 URL 解析失败，使用整个 URL 作为 path
      path = selectedRequest.value.url
    }

    // 构建完整的 requestModel 对象
    const requestModel = {
      method: selectedRequest.value.method || 'GET',
      baseURL: baseURL,
      path: path,
      query: Array.isArray(selectedRequest.value.params) ? selectedRequest.value.params : [],
      headers: Array.isArray(selectedRequest.value.headers) ? selectedRequest.value.headers : [],
      body: {
        mode: bodyMode,
        raw: rawBody.value,
        json: rawBody.value,
        formdata: formData.value,
        urlencoded: formUrlEncoded.value
      },
      timeout: 30000
    }

    const code = await CodeGenerator.generateCode(requestModel, language)
    generatedCode.value = code
    showCodeGenerateDialog.value = true
  } catch (error) {
    ElMessage.error('生成代码失败')
    console.error('生成代码失败:', error)
  }
}

const copyGeneratedCode = () => {
  if (generatedCode.value) {
    navigator.clipboard.writeText(generatedCode.value)
    ElMessage.success('已复制到剪贴板')
  }
}

const toggleWebSocketConnection = async () => {
  if (!selectedRequest.value || !selectedRequest.value.url) {
    ElMessage.warning('请填写WebSocket URL')
    return
  }

  if (websocketConnectionStatus.value === 'connected') {
    // 关闭连接
    if (websocketConnection.value) {
      websocketConnection.value.close()
      websocketConnection.value = null
    }
    websocketConnectionStatus.value = 'disconnected'
    ElMessage.success('WebSocket连接已关闭')
  } else {
    // 建立连接
    try {
      websocketConnectionStatus.value = 'connecting'
      const wsUrl = selectedRequest.value.url.replace('http://', 'ws://').replace('https://', 'wss://')

      websocketConnection.value = new WebSocket(wsUrl)

      websocketConnection.value.onopen = () => {
        websocketConnectionStatus.value = 'connected'
        ElMessage.success('WebSocket连接成功')
        websocketMessages.value.push({
          type: 'connected',
          content: 'WebSocket连接成功',
          timestamp: new Date().toLocaleString()
        })
      }

      websocketConnection.value.onmessage = (event) => {
        websocketMessages.value.push({
          type: 'received',
          content: event.data,
          timestamp: new Date().toLocaleString()
        })
      }

      websocketConnection.value.onclose = () => {
        websocketConnectionStatus.value = 'disconnected'
        websocketConnection.value = null
        websocketMessages.value.push({
          type: 'info',
          content: 'WebSocket连接已关闭',
          timestamp: new Date().toLocaleString()
        })
      }

      websocketConnection.value.onerror = (error) => {
        websocketConnectionStatus.value = 'disconnected'
        websocketConnection.value = null
        ElMessage.error('WebSocket连接失败')
        websocketMessages.value.push({
          type: 'error',
          content: `WebSocket连接失败: ${error.message}`,
          timestamp: new Date().toLocaleString()
        })
      }
    } catch (error) {
      websocketConnectionStatus.value = 'disconnected'
      ElMessage.error('WebSocket连接失败')
      console.error('WebSocket连接失败:', error)
    }
  }
}

const sendWebSocketMessage = () => {
  if (!websocketConnection.value || websocketConnectionStatus.value !== 'connected') {
    ElMessage.warning('请先建立WebSocket连接')
    return
  }

  if (websocketMessageType.value === 'binary' && !websocketBinaryFile.value) {
    ElMessage.warning('请选择要发送的二进制文件')
    return
  }

  try {
    let message = websocketMessageContent.value
    if (websocketMessageType.value === 'json') {

      message = JSON.parse(message)
    }

    websocketConnection.value.send(message)
    websocketMessages.value.push({
      type: 'sent',
      content: websocketMessageContent.value,
      timestamp: new Date().toLocaleString()
    })

    if (websocketMessageType.value !== 'binary') {
      websocketMessageContent.value = ''
    }
  } catch (error) {
    ElMessage.error('发送消息失败')
    console.error('发送消息失败:', error)
  }
}

const clearWebSocketMessage = () => {
  websocketMessageContent.value = ''
  websocketBinaryFile.value = null
}

const clearWebSocketMessages = () => {
  websocketMessages.value = []
}

const handleWebSocketFileUpload = (file) => {
  websocketBinaryFile.value = file.raw
}

const clearWebSocketBinaryFile = () => {
  websocketBinaryFile.value = null
}

const isJsonString = (str) => {
  try {
    JSON.parse(str)
    return true
  } catch (e) {
    return false
  }
}

const formatJson = (str) => {
  try {
    const obj = JSON.parse(str)
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return str
  }
}

const openDataFactorySelectorForBody = (field) => {
  currentBodyField.value = field
  currentAssertion.value = null
  currentAssertionField.value = ''
  currentAssertionIndex.value = -1
  currentScriptField.value = ''
  showDataFactorySelector.value = true
}

const openDataFactorySelectorForScript = (field) => {
  currentScriptField.value = field
  currentAssertion.value = null
  currentAssertionField.value = ''
  currentAssertionIndex.value = -1
  showDataFactorySelector.value = true
}

const openDataFactorySelector = (assertion, field, index) => {
  currentAssertion.value = assertion
  currentAssertionField.value = field
  currentAssertionIndex.value = index
  currentScriptField.value = ''
  showDataFactorySelector.value = true
}

const openVariableHelper = (field) => {
  currentEditingField.value = field
  currentAssertion.value = null
  currentAssertionField.value = ''
  currentAssertionIndex.value = -1
  showVariableHelper.value = true
}

const openVariableHelperForAssertion = (assertion, field, index) => {
  currentAssertion.value = assertion
  currentAssertionField.value = field
  currentAssertionIndex.value = index
  currentEditingField.value = ''
  showVariableHelper.value = true
}

const insertVariable = (variable) => {
  // 确保variable是对象（处理行点击事件）
  if (typeof variable === 'object' && variable !== null) {
    if (currentEditingField.value && selectedRequest.value) {
      const example = variable.example

      if (currentEditingField.value === 'rawBody') {
        // 在光标位置插入变量
        insertTextAtCursor(rawBodyInputRef, example)
      } else if (currentEditingField.value === 'pre_request_script') {
        // 对于脚本字段，暂时保持追加到末尾的行为
        // （如果需要光标插入，需要为脚本编辑器添加ref并实现类似逻辑）
        const currentValue = selectedRequest.value.pre_request_script || ''
        selectedRequest.value.pre_request_script = currentValue + example
      } else if (currentEditingField.value === 'post_request_script') {
        const currentValue = selectedRequest.value.post_request_script || ''
        selectedRequest.value.post_request_script = currentValue + example
      }

      ElMessage.success(`已插入变量: ${variable.name}`)
      showVariableHelper.value = false
    } else if (currentAssertion.value && currentAssertionField.value) {
      const example = variable.example
      const field = currentAssertionField.value

      const currentValue = currentAssertion.value[field] || ''
      if (!currentValue) {
        currentAssertion.value[field] = example
      } else {
        currentAssertion.value[field] = currentValue + example
      }

      ElMessage.success(`已插入变量: ${variable.name}`)
      showVariableHelper.value = false
    }
  }
}

const handleDataFactorySelect = (record) => {
  if (!record || !record.output_data) return

  let valueToSet = ''

  if (typeof record.output_data === 'string') {
    valueToSet = record.output_data
  } else if (record.output_data.result) {
    valueToSet = record.output_data.result
  } else if (record.output_data.output_data) {
    valueToSet = record.output_data.output_data
  } else if (typeof record.output_data === 'object') {

    const possibleResultFields = ['result', 'value', 'data', 'output', 'content']
    let foundResult = false
    for (const field of possibleResultFields) {
      if (record.output_data[field] !== undefined) {
        valueToSet = record.output_data[field]
        foundResult = true
        break
      }
    }
    // 如果没有找到可能的结果字段，将整个对象转为JSON字符串
    if (!foundResult) {
      valueToSet = JSON.stringify(record.output_data)
    }
  } else {
    valueToSet = JSON.stringify(record.output_data)
  }

  // 确保valueToSet是字符串类型
  if (typeof valueToSet !== 'string') {
    valueToSet = JSON.stringify(valueToSet)
  }

  // 如果是断言字段
  if (currentAssertion.value) {
    currentAssertion.value[currentAssertionField.value] = valueToSet
    ElMessage.success(`${t('apiTesting.interface.referencedToAssertion')}: ${record.tool_name}`)
  }
  // 如果是Body字段
  else if (currentBodyField.value) {
    if (currentBodyField.value === 'rawBody') {
      // 在光标位置插入文本
      insertTextAtCursor(rawBodyInputRef, valueToSet)
    }
    ElMessage.success(`已引用数据工厂数据到Body: ${record.tool_name}`)
  }
  // 如果是脚本字段
  else if (currentScriptField.value && selectedRequest.value) {
    // 将值插入到脚本中
    const insertText = `\n// 来自数据工厂: ${record.tool_name}\nconst ${record.tool_name.replace(/\s+/g, '_')} = ${JSON.stringify(valueToSet)}\n`
    const currentValue = selectedRequest.value[currentScriptField.value] || ''
    selectedRequest.value[currentScriptField.value] = currentValue + insertText
    ElMessage.success(`已引用数据工厂数据到脚本: ${record.tool_name}`)
  }

  showDataFactorySelector.value = false
}

// 在光标位置插入文本的辅助函数
const insertTextAtCursor = (inputRef, textToInsert) => {
  if (!inputRef.value) {
    // 如果没有找到ref，直接追加到末尾
    rawBody.value = rawBody.value + textToInsert
    return
  }

  // 获取textarea DOM元素
  const textarea = inputRef.value.$el?.querySelector('textarea')
  if (!textarea) {
    // 如果找不到textarea元素，直接追加到末尾
    rawBody.value = rawBody.value + textToInsert
    return
  }

  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  const currentValue = rawBody.value

  // 在光标位置插入新文本
  const newValue =
    currentValue.substring(0, startPos) +
    textToInsert +
    currentValue.substring(endPos)

  rawBody.value = newValue

  // 恢复光标位置到插入文本的末尾
  nextTick(() => {
    const newCursorPos = startPos + textToInsert.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    textarea.focus()
  })
}

// 加载变量函数
const loadVariableFunctions = async () => {
  try {
    loading.value = true
    console.log('开始加载变量函数...')
    const apiResponse = await getVariableFunctions()
    console.log('变量函数响应:', apiResponse)
    console.log('变量函数响应.data:', apiResponse.data)
    
    // 更灵活地处理响应数据结构
    let functionsData = null
    
    // 检查不同可能的数据结构
    if (apiResponse && apiResponse.data) {
      if (Array.isArray(apiResponse.data)) {
        // 后端返回的是数组，直接使用
        functionsData = apiResponse.data
      } else if (apiResponse.data.functions) {
        // 如果data中有functions字段，使用它
        functionsData = apiResponse.data.functions
      } else if (typeof apiResponse.data === 'object') {
        // 如果data是对象但没有functions字段，假设整个对象就是按分类组织的函数
        functionsData = apiResponse.data
      }
    }
    
    if (functionsData) {
      const groupedFunctions = functionsData
      console.log('处理后的 groupedFunctions:', groupedFunctions)

      // 后端已经按分类分组了，直接转换为标签页所需的格式
      if (typeof groupedFunctions === 'object' && !Array.isArray(groupedFunctions)) {
        variableCategories.value = Object.entries(groupedFunctions).map(([label, variables]) => ({
          label,
          variables
        }))
      } else if (Array.isArray(groupedFunctions)) {
        // 如果是数组，按分类分组
        const grouped = {}
        
        // 创建分类名称映射表
        const categoryMapping = {
          '随机数': t('apiTesting.component.keyValueEditor.categories.randomNumber'),
          '测试数据': t('apiTesting.component.keyValueEditor.categories.testData'),
          '字符串': t('apiTesting.component.keyValueEditor.categories.string'),
          '编码转换': t('apiTesting.component.keyValueEditor.categories.encodingConversion'),
          '加密': t('apiTesting.component.keyValueEditor.categories.encryption'),
          '时间日期': t('apiTesting.component.keyValueEditor.categories.datetime'),
          'Crontab': t('apiTesting.component.keyValueEditor.categories.crontab'),
          '未分类': t('apiTesting.component.keyValueEditor.categories.uncategorized')
        }
        
        groupedFunctions.forEach(func => {
          const rawCategory = func.category || '未分类'
          // 使用映射表获取正确的分类名称
          const category = categoryMapping[rawCategory] || rawCategory
          if (!grouped[category]) {
            grouped[category] = []
          }
          grouped[category].push(func)
        })
        
        // 定义固定的分类顺序 ['随机数', '测试数据', '字符串', '编码转换', '加密', '时间日期', 'Crontab', '未分类']
        const categoryOrder = [
          t('apiTesting.component.keyValueEditor.categories.randomNumber'),
          t('apiTesting.component.keyValueEditor.categories.testData'),
          t('apiTesting.component.keyValueEditor.categories.string'),
          t('apiTesting.component.keyValueEditor.categories.encodingConversion'),
          t('apiTesting.component.keyValueEditor.categories.encryption'),
          t('apiTesting.component.keyValueEditor.categories.datetime'),
          t('apiTesting.component.keyValueEditor.categories.crontab'),
          t('apiTesting.component.keyValueEditor.categories.uncategorized')
        ]
        
        // 按固定顺序构建分类列表
        const orderedCategories = []
        categoryOrder.forEach(category => {
          if (grouped[category]) {
            orderedCategories.push({
              label: category,
              variables: grouped[category]
            })
            delete grouped[category]
          }
        })
        
        // 添加剩余的分类（如果有）
        Object.entries(grouped).forEach(([label, variables]) => {
          orderedCategories.push({
            label,
            variables
          })
        })
        
        variableCategories.value = orderedCategories
      }

      console.log('最终变量分类:', variableCategories.value)
    } else {
      console.error('响应数据格式错误，无法找到函数数据')
      console.error('完整响应:', apiResponse)
    }
  } catch (error) {
    console.error('加载变量函数失败:', error)
    ElMessage.error('加载变量函数失败，使用本地数据')
    // 加载失败时使用本地变量分类数据
    useLocalVariableCategories()
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(async () => {
  await loadProjects()
  await loadVariableFunctions()

  // 添加全局点击事件监听器，用于隐藏右键菜单
  document.addEventListener('click', handleGlobalClick)
  document.addEventListener('contextmenu', handleGlobalClick)
>>>>>>> upstream/main
})

onBeforeUnmount(() => {
  // 清理WebSocket连接
  if (websocketConnection.value) {
    websocketConnection.value.close()
    websocketConnection.value = null
  }
})
</script>

<style scoped>
.interface-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.interface-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  background: #f8f9fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.collection-tree {
  flex: 1;
  overflow: auto;
  padding: 10px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
}

.node-label {
  flex: 1;
}

.node-edit {
  flex: 1;
}

.node-edit .el-input {
  font-size: 14px;
}

.method-tag {
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
  color: white;
  font-weight: bold;
}

.method-tag.get { background: #67c23a; }
.method-tag.post { background: #409eff; }
.method-tag.put { background: #e6a23c; }
.method-tag.delete { background: #f56c6c; }
.method-tag.patch { background: #909399; }

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.request-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: auto;
}

.request-header {
  margin-bottom: 20px;
}

.request-line {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.url-input {
  flex: 1;
}

.request-name {
  display: flex;
  gap: 10px;
  align-items: center;
}

.request-tabs {
  margin-bottom: 20px;
}

.body-container {
  padding: 10px 0;
}

.body-content {
  margin-top: 15px;
}

.raw-options {
  margin-bottom: 10px;
}

.raw-body {
  font-family: 'Courier New', monospace;
}

.response-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.response-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.response-time {
  color: #909399;
  font-size: 12px;
}

.response-body {
  position: relative;
}

.response-actions {
  margin-bottom: 10px;
}

.response-content {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.response-headers {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.header-row {
  margin-bottom: 5px;
  font-size: 12px;
}

/* 断言样式 */
.assertions-editor {
  padding: 10px;
}

.assertions-header {
  margin-bottom: 15px;
}

.assertion-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 15px;
  background: #fafafa;
}

.assertion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

.assertion-name {
  flex: 1;
  margin-right: 10px;
}

.assertion-config {
  padding: 10px;
}

.assertion-config .el-select {
  width: 100%;
  margin-bottom: 10px;
}

.assertion-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.assertion-input {
  margin-bottom: 5px;
}

.no-assertions {
  text-align: center;
  padding: 30px;
  color: #909399;
}

/* WebSocket信息样式 */
.websocket-info-section {
  padding: 20px;
}

.websocket-tips {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.websocket-tips h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.websocket-tips ul {
  margin: 0;
  padding-left: 20px;
}

.websocket-tips li {
  margin-bottom: 5px;
}

/* WebSocket消息样式 */
.message-container {
  padding: 15px;
}

.message-input-section {
  margin-bottom: 20px;
}

.uploaded-file {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* WebSocket响应区域样式 */
.websocket-response-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.websocket-response-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
}

.websocket-messages {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 15px;
}

.websocket-message-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #fafafa;
}

.websocket-message-item.sent {
  border-left: 3px solid #409eff;
}

.websocket-message-item.received {
  border-left: 3px solid #67c23a;
}

.websocket-message-item.info {
  border-left: 3px solid #909399;
}

.websocket-message-item.error {
  border-left: 3px solid #f56c6c;
}

.websocket-message-item.connected {
  border-left: 3px solid #67c23a;
}

.message-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 12px;
}

.message-type.sent {
  color: #409eff;
  font-weight: bold;
}

.message-type.received {
  color: #67c23a;
  font-weight: bold;
}

.message-type.info {
  color: #909399;
  font-weight: bold;
}

.message-type.error {
  color: #f56c6c;
  font-weight: bold;
}

.message-type.connected {
  color: #67c23a;
  font-weight: bold;
}

.message-time {
  color: #909399;
}

.message-content {
  padding: 10px 12px;
}

.message-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
}

/* WebSocket URL样式 */
.websocket-url {
  flex: 1;
}

/* 断言结果样式 */
.assertions-results {
  padding: 15px;
}

.assertion-result-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  padding: 10px;
}

.assertion-result-item.passed {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.assertion-result-item.failed {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.assertion-result-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.assertion-name {
  margin-left: 8px;
  font-weight: 500;
}

.assertion-result-details {
  padding-left: 24px;
  font-size: 12px;
}

.result-row {
  display: flex;
  margin-bottom: 4px;
}

.label {
  width: 50px;
  font-weight: 500;
}

.value {
  flex: 1;
  word-break: break-all;
}

.value.error {
  color: #f56c6c;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 5px 0;
  margin: 0;
  list-style: none;
  z-index: 9999;
}

.context-menu li {
  padding: 8px 15px;
  cursor: pointer;
  font-size: 14px;
}

.context-menu li:hover {
  background: #f5f7fa;
}
</style>