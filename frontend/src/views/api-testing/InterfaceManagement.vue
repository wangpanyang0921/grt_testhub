<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select v-model="selectedProject" :placeholder="$t('apiTesting.common.selectProject')" @change="onProjectChange" class="project-select" style="width: 200px;">
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="showCreateCollectionDialog = true">
        <el-icon><Folder /></el-icon>
        {{ $t('apiTesting.interface.createCollection') }}
      </el-button>
      <el-button class="btn-secondary add-element-btn" @click="createEmptyRequest">
        <el-icon><Plus /></el-icon>
        {{ $t('apiTesting.interface.addInterface') }}
      </el-button>
    </div>

    <div class="card-container interface-layout">
      <!-- 左侧接口列表 -->
      <div class="sidebar">
        <div class="interface-list">
          <el-table
            :data="interfaceList"
            style="width: 100%"
            height="100%"
            highlight-current-row
            @row-click="onInterfaceRowClick"
          >
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column label="接口名称" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="interface-name-cell">
                  <el-icon v-if="row.request_type === 'WEBSOCKET'"><Connection /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="请求方式" width="90" align="center">
              <template #default="{ row }">
                <el-tag 
                  v-if="row.request_type !== 'WEBSOCKET'" 
                  size="small" 
                  :class="row.method?.toLowerCase()"
                  class="method-tag"
                >
                  {{ row.method }}
                </el-tag>
                <el-tag v-else size="small" type="info">WS</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="所属合集" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="collection-cell">
                  <el-icon><Folder /></el-icon>
                  <span>{{ getCollectionName(row.collection) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="创建人" width="100" align="center">
              <template #default="{ row }">
                <span>{{ row.created_by?.username || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button-group>
                  <el-button size="small" @click.stop="editInterface(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button size="small" type="danger" @click.stop="deleteInterface(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
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
            <el-tab-pane label="参数" name="params">
              <KeyValueEditor
                v-model="selectedRequest.params"
                :placeholder-key="$t('apiTesting.interface.paramName')"
                :placeholder-value="$t('apiTesting.interface.paramValue')"
              />
            </el-tab-pane>

            <el-tab-pane label="请求头" name="headers">
              <KeyValueEditor
                ref="headersEditorRef"
                v-model="selectedRequest.headers"
                :placeholder-key="$t('apiTesting.interface.headerName')"
                :placeholder-value="$t('apiTesting.interface.headerValue')"
                @update:modelValue="onHeadersUpdate"
              />
            </el-tab-pane>

            <el-tab-pane label="请求体" name="body" v-if="hasBody">
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
              <el-tab-pane label="变量提取" name="variable-extractors">
                <div class="variable-extractors-editor">
                  <div class="extractors-header">
                    <el-button size="small" type="primary" @click="addVariableExtractor">
                      <el-icon><Plus /></el-icon>
                      添加提取规则
                    </el-button>
                  </div>
                  <div class="extractors-tips">
                    <el-alert type="info" :closable="false">
                      <template #title>
                        <div class="tips-content">
                          <p>从响应中提取数据并保存到环境变量，供后续接口使用</p>
                        </div>
                      </template>
                    </el-alert>
                  </div>
                  <div class="extractors-list" v-if="selectedRequest.variable_extractors && selectedRequest.variable_extractors.length > 0">
                    <div
                      v-for="(extractor, index) in selectedRequest.variable_extractors"
                      :key="index"
                      class="extractor-item"
                    >
                      <div class="extractor-header">
                        <el-input
                          v-model="extractor.name"
                          placeholder="提取规则名称"
                          size="small"
                          class="extractor-name"
                        />
                        <el-button
                          size="small"
                          type="danger"
                          @click="removeVariableExtractor(index)"
                          circle
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                      <div class="extractor-config">
                        <el-select
                          v-model="extractor.source"
                          placeholder="选择提取来源"
                          size="small"
                          style="width: 100%; margin-bottom: 8px;"
                        >
                          <el-option label="响应体 (JSON)" value="json_body" />
                          <el-option label="响应头" value="header" />
                        </el-select>
                        <el-input
                          v-if="extractor.source === 'json_body'"
                          v-model="extractor.json_path"
                          placeholder="JSON Path 表达式，如: $.data.token"
                          size="small"
                          style="margin-bottom: 8px;"
                        />
                        <el-input
                          v-if="extractor.source === 'header'"
                          v-model="extractor.header_name"
                          placeholder="响应头名称，如: X-Auth-Token"
                          size="small"
                          style="margin-bottom: 8px;"
                        />
                        <el-input
                          v-model="extractor.variable_name"
                          placeholder="环境变量名称，如: authToken"
                          size="small"
                        />
                      </div>
                    </div>
                  </div>
                  <div v-else class="no-extractors">
                    <p>暂无变量提取规则</p>
                    <el-button size="small" type="primary" @click="addVariableExtractor">
                      <el-icon><Plus /></el-icon>
                      添加第一个提取规则
                    </el-button>
                  </div>
                </div>
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
              <el-tab-pane label="响应体" name="body">
                <div class="response-body">
                  <div class="response-actions">
                    <el-button-group>
                      <el-button size="small" @click="formatResponse">格式化</el-button>
                      <el-button size="small" @click="copyResponse">复制</el-button>
                    </el-button-group>
                    <el-tag v-if="selectedJsonPath" type="success" size="small" closable @close="selectedJsonPath = ''" style="margin-left: 10px;">
                      已选择: {{ selectedJsonPath }}
                    </el-tag>
                  </div>
                  <div class="response-content-wrapper">
                    <pre class="response-content" @click="handleResponseClick">{{ responseBody }}</pre>
                    <div v-if="selectedJsonPath" class="json-path-actions">
                      <el-button size="small" type="primary" @click="useJsonPathForExtractor">
                        用于变量提取
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="响应头" name="headers">
                <div class="response-headers">
                  <div v-for="(value, key) in response.response_data?.headers" :key="key" class="header-row">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="提取变量" name="extracted-variables" v-if="response.extraction_results && response.extraction_results.length > 0">
                <div class="extraction-results">
                  <div
                    v-for="(result, index) in response.extraction_results"
                    :key="index"
                    class="extraction-result-item"
                    :class="{ 'success': result.success, 'failed': !result.success }"
                  >
                    <div class="extraction-result-header">
                      <el-tag :type="result.success ? 'success' : 'danger'" size="small">
                        {{ result.success ? '成功' : '失败' }}
                      </el-tag>
                      <span class="extraction-name">{{ result.name }}</span>
                    </div>
                    <div class="extraction-result-details">
                      <div class="result-row" v-if="result.variable_name">
                        <span class="label">变量名</span>
                        <span class="value">{{ result.variable_name }}</span>
                      </div>
                      <div class="result-row" v-if="result.json_path">
                        <span class="label">JSON Path</span>
                        <span class="value">{{ result.json_path }}</span>
                      </div>
                      <div class="result-row" v-if="result.header_name">
                        <span class="label">响应头</span>
                        <span class="value">{{ result.header_name }}</span>
                      </div>
                      <div class="result-row" v-if="result.success">
                        <span class="label">提取值</span>
                        <span class="value extraction-value">{{ result.value }}</span>
                      </div>
                      <div class="result-row" v-if="result.error">
                        <span class="label">错误</span>
                        <span class="value error">{{ result.error }}</span>
                      </div>
                    </div>
                  </div>
                  <div v-if="response.extracted_variables && Object.keys(response.extracted_variables).length > 0" class="extracted-variables-summary">
                    <h4>已保存到环境变量</h4>
                    <div class="variables-list">
                      <div v-for="(value, key) in response.extracted_variables" :key="key" class="variable-item">
                        <span class="variable-key">{{ key }}</span>
                        <span class="variable-value">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="断言结果" name="assertions" v-if="response.assertions_results && response.assertions_results.length > 0">
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
import { Plus, Folder, Document, Edit, Delete, Connection } from '@element-plus/icons-vue'
import api from '@/utils/api'
import KeyValueEditor from './components/KeyValueEditor.vue'

const { t } = useI18n()

const treeRef = ref(null)
const expandedKeys = ref([])
const projects = ref([])
const selectedProject = ref(null)
const collections = ref([])
const flatCollections = ref([])
const interfaceList = ref([])
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
const rawBodyInputRef = ref(null)
const currentHeaders = ref({})
const selectedJsonPath = ref('')

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
const variableCategories = ref([])
const loading = ref(false)

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

    // 填充接口列表（用于表格展示）
    interfaceList.value = requests

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

// 获取合集名称
const getCollectionName = (collectionId) => {
  if (!collectionId) return '未分类'
  const collection = flatCollections.value.find(c => c.id === collectionId)
  return collection ? collection.name : '未分类'
}

// 表格行点击事件
const onInterfaceRowClick = (row) => {
  editInterface(row)
}

// 编辑接口
const editInterface = (row) => {
  console.log('editInterface - original data.headers:', row.headers)
  const convertedHeaders = convertObjectToKeyValueArray(row.headers || {})
  console.log('editInterface - converted headers:', convertedHeaders)

  // 初始化currentHeaders
  currentHeaders.value = row.headers || {}
  console.log('editInterface - initialized currentHeaders:', currentHeaders.value)

  selectedRequest.value = {
    ...row,
    params: convertObjectToKeyValueArray(row.params || {}),
    headers: convertedHeaders,
    body: row.body || {},
    auth: row.auth || {}
  }

  console.log('editInterface - selectedRequest.value.headers:', selectedRequest.value.headers)

  // 解析body数据
  parseBodyData(row.body)
}

// 解析body数据
const parseBodyData = (body) => {
  if (!body || !body.type) {
    bodyType.value = 'none'
    return
  }

  bodyType.value = body.type

  if (body.type === 'json') {
    rawType.value = 'json'
    // 如果 data 已经是字符串，直接显示；否则序列化为 JSON
    if (typeof body.data === 'string') {
      rawBody.value = body.data
    } else {
      rawBody.value = body.data ? JSON.stringify(body.data, null, 2) : ''
    }
  } else if (body.type === 'raw') {
    rawType.value = 'text'
    rawBody.value = body.data || ''
  } else if (body.type === 'form-data') {
    formData.value = body.data || {}
  } else if (body.type === 'x-www-form-urlencoded') {
    formUrlEncoded.value = body.data || {}
  }
}

// 删除接口
const deleteInterface = async (row) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.messages.confirm.deleteInterface'),
      t('apiTesting.common.confirm'),
      { type: 'warning' }
    )
    await api.delete(`/api-testing/requests/${row.id}/`)
    ElMessage.success(t('apiTesting.messages.success.delete'))
    await loadRequests()
    if (selectedRequest.value?.id === row.id) {
      selectedRequest.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    }
  }
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
        // 如果 data 已经是字符串，直接显示；否则序列化为 JSON
        if (typeof data.body.data === 'string') {
          rawBody.value = data.body.data
        } else {
          rawBody.value = JSON.stringify(data.body.data, null, 2)
        }
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
        // 如果 data 已经是字符串，直接显示；否则序列化为 JSON
        if (typeof data.body.data === 'string') {
          rawBody.value = data.body.data
        } else {
          rawBody.value = JSON.stringify(data.body.data, null, 2)
        }
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

const addVariableExtractor = () => {
  if (!selectedRequest.value.variable_extractors) {
    selectedRequest.value.variable_extractors = []
  }

  selectedRequest.value.variable_extractors.push({
    name: `提取规则${selectedRequest.value.variable_extractors.length + 1}`,
    source: 'json_body',
    json_path: '',
    header_name: '',
    variable_name: ''
  })
}

const removeVariableExtractor = (index) => {
  if (selectedRequest.value.variable_extractors) {
    selectedRequest.value.variable_extractors.splice(index, 1)
  }
}

// 处理响应体点击事件，生成 JSON Path
const handleResponseClick = (event) => {
  const selection = window.getSelection()
  const selectedText = selection.toString().trim()

  if (!selectedText || !response.value?.response_data?.body) {
    return
  }

  try {
    const body = typeof response.value.response_data.body === 'string'
      ? JSON.parse(response.value.response_data.body)
      : response.value.response_data.body

    const jsonPath = findJsonPath(body, selectedText)
    if (jsonPath) {
      selectedJsonPath.value = jsonPath
      ElMessage.success(`已生成 JSON Path: ${jsonPath}`)
    }
  } catch (e) {
    console.error('Failed to parse response body:', e)
  }
}

// 递归查找 JSON Path
const findJsonPath = (obj, targetValue, currentPath = '$') => {
  if (obj === targetValue) {
    return currentPath
  }

  if (Array.isArray(obj)) {
    for (let i = 0; i < obj.length; i++) {
      const result = findJsonPath(obj[i], targetValue, `${currentPath}[${i}]`)
      if (result) return result
    }
  } else if (typeof obj === 'object' && obj !== null) {
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const result = findJsonPath(obj[key], targetValue, `${currentPath}.${key}`)
        if (result) return result
      }
    }
  }

  return null
}

// 将选中的 JSON Path 用于变量提取
const useJsonPathForExtractor = () => {
  if (!selectedJsonPath.value) return

  // 切换到变量提取标签
  activeTab.value = 'variable-extractors'

  // 如果没有提取规则，创建一个
  if (!selectedRequest.value.variable_extractors || selectedRequest.value.variable_extractors.length === 0) {
    addVariableExtractor()
  }

  // 填充到最后一个提取规则中
  const lastIndex = selectedRequest.value.variable_extractors.length - 1
  selectedRequest.value.variable_extractors[lastIndex].source = 'json_body'
  selectedRequest.value.variable_extractors[lastIndex].json_path = selectedJsonPath.value

  ElMessage.success('JSON Path 已填充到变量提取规则')
  selectedJsonPath.value = ''
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
      post_request_script: '',
      variable_extractors: []
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
      post_request_script: res.data.post_request_script || '',
      variable_extractors: res.data.variable_extractors || []
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

const saveRequest = async () => {
  if (!selectedRequest.value) return

  // 检查必填字段
  if (!selectedRequest.value.name) {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseInputRequestName'))
    return
  }

  if (!selectedRequest.value.url) {
    ElMessage.warning(t('apiTesting.messages.warning.pleaseInputUrl'))
    return
  }

  saving.value = true
  try {
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
      name: selectedRequest.value.name,
      method: selectedRequest.value.method,
      url: selectedRequest.value.url,
      description: selectedRequest.value.description || '',
      collection: selectedRequest.value.collection,
      project: selectedProject.value,
      request_type: selectedRequest.value.request_type || 'HTTP',
      params: convertKeyValueArrayToObject(selectedRequest.value.params || []),
      headers: convertKeyValueArrayToObject(selectedRequest.value.headers || []),
      body: bodyData,
      auth: selectedRequest.value.auth || {},
      pre_request_script: selectedRequest.value.pre_request_script || '',
      post_request_script: selectedRequest.value.post_request_script || '',
      variable_extractors: selectedRequest.value.variable_extractors || []
    }

    if (selectedRequest.value.id) {
      // 更新现有请求
      await api.put(`/api-testing/requests/${selectedRequest.value.id}/`, requestData)
      ElMessage.success(t('apiTesting.messages.success.update'))
    } else {
      // 创建新请求
      const res = await api.post('/api-testing/requests/', requestData)
      selectedRequest.value.id = res.data.id
      ElMessage.success(t('apiTesting.messages.success.create'))
    }
    // 重新加载集合和请求
    await Promise.all([loadCollections(), loadRequests()])
  } catch (error) {
    console.error('Save request error:', error)
    ElMessage.error(t('apiTesting.messages.error.saveFailed'))
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

// 获取变量函数（模拟API调用）
const getVariableFunctions = async () => {
  // 返回本地定义的变量函数数据
  return {
    data: {
      '随机数': [
        { name: '${random_int}', description: '随机整数', example: '${random_int(1, 100)}' },
        { name: '${random_float}', description: '随机浮点数', example: '${random_float(1.0, 100.0)}' },
      ],
      '字符串': [
        { name: '${random_string}', description: '随机字符串', example: '${random_string(10)}' },
        { name: '${uuid}', description: 'UUID', example: '${uuid()}' },
      ],
      '时间日期': [
        { name: '${timestamp}', description: '当前时间戳', example: '${timestamp()}' },
        { name: '${datetime}', description: '当前日期时间', example: '${datetime("YYYY-MM-DD HH:mm:ss")}' },
      ],
    }
  }
}

// 使用本地变量分类数据
const useLocalVariableCategories = () => {
  variableCategories.value = [
    {
      label: '随机数',
      variables: [
        { name: '${random_int}', description: '随机整数', example: '${random_int(1, 100)}' },
        { name: '${random_float}', description: '随机浮点数', example: '${random_float(1.0, 100.0)}' },
      ]
    },
    {
      label: '字符串',
      variables: [
        { name: '${random_string}', description: '随机字符串', example: '${random_string(10)}' },
        { name: '${uuid}', description: 'UUID', example: '${uuid()}' },
      ]
    },
    {
      label: '时间日期',
      variables: [
        { name: '${timestamp}', description: '当前时间戳', example: '${timestamp()}' },
        { name: '${datetime}', description: '当前日期时间', example: '${datetime("YYYY-MM-DD HH:mm:ss")}' },
      ]
    },
  ]
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
        
        groupedFunctions.forEach(func => {
          const category = func.category || '未分类'
          if (!grouped[category]) {
            grouped[category] = []
          }
          grouped[category].push(func)
        })
        
        // 定义固定的分类顺序
        const categoryOrder = [
          '随机数',
          '测试数据',
          '字符串',
          '编码转换',
          '加密',
          '时间日期',
          'Crontab',
          '未分类'
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
})

onBeforeUnmount(() => {
  // 清理WebSocket连接
  if (websocketConnection.value) {
    websocketConnection.value.close()
    websocketConnection.value = null
  }
})
</script>

<style lang="scss" scoped>
.page-container {
  --primary-color: #7b42f6;
  --primary-light: #a78bfa;
  --primary-lighter: #c4b5fd;
  --primary-lightest: #f5f3ff;
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
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

  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  padding: 20px 24px;

  .project-select {
    :deep(.el-input__wrapper) {
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      background: #ffffff;

      &:hover, &.is-focus {
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
        border-color: #7b42f6;
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  .filter-bar-spacer {
    flex: 1;
  }

  .create-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

    .el-icon {
      margin-right: 6px;
    }

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4) !important;
    }
  }

  .add-element-btn {
    background: #ffffff !important;
    border: 1px solid rgba(147, 112, 219, 0.4) !important;
    color: #5a32a3 !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;

    .el-icon {
      margin-right: 6px;
    }

    &:hover {
      background: #f8f7ff !important;
      border-color: #7b42f6 !important;
      color: #7b42f6 !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.2) !important;
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
}

.interface-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 700px;
  border-right: 1px solid rgba(147, 112, 219, 0.12);
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.interface-list {
  flex: 1;
  overflow: hidden;
  padding: 0;

  :deep(.el-table) {
    background: transparent;

    .el-table__header-wrapper {
      background: #f5f7fa;
    }

    .el-table__row {
      cursor: pointer;

      &:hover {
        background: #f0f9ff;
      }

      &.current-row {
        background: #e6f7ff;
      }
    }
  }

  .interface-name-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #909399;
    }
  }

  .collection-cell {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #606266;

    .el-icon {
      color: #e6a23c;
    }
  }

  .method-tag {
    font-weight: 600;

    &.get {
      background: #e1f3d8;
      color: #67c23a;
    }

    &.post {
      background: #d9ecff;
      color: #409eff;
    }

    &.put {
      background: #faecd8;
      color: #e6a23c;
    }

    &.delete {
      background: #fde2e2;
      color: #f56c6c;
    }

    &.patch {
      background: #f0e9ff;
      color: #a855f7;
    }
  }
}

.collection-tree {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;

  :deep(.el-tree) {
    background: transparent;

    .el-tree-node__content {
      height: 44px;
      border-radius: 10px;
      margin-bottom: 6px;
      padding-left: 8px !important;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        background: rgba(123, 66, 246, 0.06);
      }
    }

    .el-tree-node.is-current > .el-tree-node__content {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border-left: 3px solid #5a32a3;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.25);

      :deep(.tree-node) {
        .el-icon {
          color: white !important;
        }

        .node-label {
          color: white !important;
          font-weight: 600;
        }

        .method-tag {
          color: #5a32a3 !important;
          background: white !important;
        }
      }
    }
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 8px;

  .el-icon {
    font-size: 16px;
    color: #7b42f6;
  }

  .node-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #5a32a3;
    font-weight: 500;
  }

  .node-edit {
    flex: 1;

    .el-input {
      font-size: 14px;

      :deep(.el-input__wrapper) {
        border-radius: 6px;
        border: 1px solid rgba(147, 112, 219, 0.3);
        box-shadow: none;

        &:hover, &.is-focus {
          border-color: #7b42f6;
          box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
        }
      }
    }
  }

  .method-tag {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    color: white;
    font-weight: 600;

    &.get { background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%); }
    &.post { background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%); }
    &.put { background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%); }
    &.delete { background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%); }
    &.patch { background: linear-gradient(135deg, #909399 0%, #a6a9ad 100%); }
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f8f7ff;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;

  :deep(.el-empty__description) {
    color: #9370db;
  }

  .el-button {
    margin-top: 16px;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 8px;
    padding: 10px 24px;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
    }
  }
}

.request-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow: auto;
  background: transparent;
}

.request-header {
  margin-bottom: 20px;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid rgba(147, 112, 219, 0.1);
  box-shadow: 0 2px 12px rgba(147, 112, 219, 0.06);
}

.request-line {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;

  .el-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }
  }
}

.url-input {
  flex: 1;

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    box-shadow: none;

    &:hover, &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }

  :deep(.el-input-group__prepend) {
    background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
    border-color: rgba(147, 112, 219, 0.2);

    .el-select {
      :deep(.el-input__wrapper) {
        border: none;
        box-shadow: none;
        background: transparent;
      }
    }
  }

  &.websocket-url {
    :deep(.el-input__wrapper) {
      border-color: rgba(147, 112, 219, 0.4);
    }
  }
}

.request-name {
  display: flex;
  gap: 12px;
  align-items: center;

  .el-input {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }
  }

  .el-button {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 8px;
    font-weight: 500;
    color: white;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
      color: white;
    }
  }
}

.request-tabs {
  margin-bottom: 16px;

  :deep(.el-tabs__header) {
    margin-bottom: 12px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    background: rgba(147, 112, 219, 0.1);
  }

  :deep(.el-tabs__nav) {
    display: flex;
    gap: 4px;
  }

  :deep(.el-tabs__item) {
    color: #666;
    font-weight: 500;
    font-size: 13px;
    padding: 0 16px;
    height: 36px;
    line-height: 36px;
    border-radius: 6px 6px 0 0;
    transition: all 0.3s ease;

    &:hover {
      color: #7b42f6;
      background: rgba(123, 66, 246, 0.05);
    }

    &.is-active {
      color: #7b42f6;
      background: linear-gradient(135deg, rgba(123, 66, 246, 0.1) 0%, rgba(90, 50, 163, 0.05) 100%);
    }
  }

  :deep(.el-tabs__active-bar) {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    height: 3px;
    border-radius: 2px;
  }
}

.body-container {
  padding: 10px 0;
}

.body-content {
  margin-top: 15px;
}

.raw-options {
  margin-bottom: 10px;

  .el-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }
  }
}

.raw-body {
  font-family: 'Courier New', monospace;

  :deep(.el-textarea__inner) {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    background: #fafafa;

    &:hover, &:focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }
}

.response-section {
  margin-top: 24px;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid rgba(147, 112, 219, 0.1);
  box-shadow: 0 2px 12px rgba(147, 112, 219, 0.06);

  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    background: rgba(147, 112, 219, 0.08);
    height: 1px;
  }

  :deep(.el-tabs__item) {
    color: #666;
    font-weight: 500;
    font-size: 14px;
    padding: 0 20px;
    height: 40px;
    line-height: 40px;
    transition: all 0.3s ease;

    &:hover {
      color: #7b42f6;
    }

    &.is-active {
      color: #7b42f6;
      font-weight: 600;
    }
  }

  :deep(.el-tabs__active-bar) {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    height: 3px;
    border-radius: 2px;
  }
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.08);
}

.response-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.response-time {
  color: #7b42f6;
  font-size: 13px;
  font-weight: 500;
  background: linear-gradient(135deg, rgba(123, 66, 246, 0.1) 0%, rgba(90, 50, 163, 0.05) 100%);
  padding: 4px 12px;
  border-radius: 20px;
}

.response-body {
  position: relative;
}

.response-actions {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;

  .el-button {
    border-radius: 6px;
    font-weight: 500;

    &:hover {
      transform: translateY(-1px);
    }
  }
}

.response-content {
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
  padding: 15px;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid rgba(147, 112, 219, 0.1);
  cursor: text;
  user-select: text;
}

.response-content-wrapper {
  position: relative;
}

.json-path-actions {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  .el-button {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 6px;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    }
  }
}

.response-headers {
  padding: 15px;
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
  border-radius: 8px;
  border: 1px solid rgba(147, 112, 219, 0.1);
}

.header-row {
  margin-bottom: 5px;
  font-size: 12px;
  color: #5a32a3;
}

/* 断言样式 */
.assertions-editor {
  padding: 10px;
}

.assertions-header {
  margin-bottom: 15px;

  .el-button {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 6px;
    font-weight: 500;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    }
  }
}

.assertion-item {
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 8px;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #faf9ff 0%, #f5f3ff 100%);
  overflow: hidden;
}

.assertion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.15);
  background: white;
}

.assertion-name {
  flex: 1;
  margin-right: 10px;

  :deep(.el-input__wrapper) {
    border-radius: 6px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    box-shadow: none;

    &:hover, &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
    }
  }
}

.assertion-config {
  padding: 12px;

  .el-select {
    width: 100%;
    margin-bottom: 10px;

    :deep(.el-input__wrapper) {
      border-radius: 6px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
      }
    }
  }
}

.assertion-params {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .el-input,
  .el-input-number {
    :deep(.el-input__wrapper) {
      border-radius: 6px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
      }
    }
  }
}

.assertion-input {
  margin-bottom: 5px;
}

.no-assertions {
  text-align: center;
  padding: 30px;
  color: #9370db;

  .el-button {
    margin-top: 12px;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 6px;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    }
  }
}

/* 变量提取器样式 */
.variable-extractors-editor {
  padding: 10px;
}

.extractors-header {
  margin-bottom: 15px;

  .el-button {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 6px;
    font-weight: 500;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    }
  }
}

.extractors-tips {
  margin-bottom: 15px;

  .el-alert {
    background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
    border: 1px solid rgba(147, 112, 219, 0.2);

    .tips-content {
      p {
        margin: 0;
        color: #5a32a3;
        font-size: 13px;
      }
    }
  }
}

.extractors-list {
  .extractor-item {
    border: 1px solid rgba(147, 112, 219, 0.2);
    border-radius: 8px;
    margin-bottom: 15px;
    background: linear-gradient(135deg, #faf9ff 0%, #f5f3ff 100%);
    overflow: hidden;
  }
}

.extractor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.15);
  background: white;
}

.extractor-name {
  flex: 1;
  margin-right: 10px;

  :deep(.el-input__wrapper) {
    border-radius: 6px;
    border: 1px solid rgba(147, 112, 219, 0.2);
    box-shadow: none;

    &:hover, &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
    }
  }
}

.extractor-config {
  padding: 12px;

  .el-select {
    :deep(.el-input__wrapper) {
      border-radius: 6px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
      }
    }
  }

  .el-input {
    :deep(.el-input__wrapper) {
      border-radius: 6px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 2px rgba(123, 66, 246, 0.1);
      }
    }
  }
}

.no-extractors {
  text-align: center;
  padding: 30px;
  color: #9370db;

  .el-button {
    margin-top: 12px;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    border-radius: 6px;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
    }
  }
}

/* WebSocket信息样式 */
.websocket-info-section {
  padding: 20px;
}

.websocket-tips {
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
  border-radius: 8px;
  border: 1px solid rgba(147, 112, 219, 0.15);
}

.websocket-tips h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #5a32a3;
}

.websocket-tips ul {
  margin: 0;
  padding-left: 20px;
}

.websocket-tips li {
  margin-bottom: 5px;
  color: #5a32a3;
}

/* WebSocket消息样式 */
.message-container {
  padding: 15px;
}

.message-input-section {
  margin-bottom: 20px;

  .el-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }
  }

  .el-textarea {
    :deep(.el-textarea__inner) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.2);

      &:hover, &:focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }
  }
}

.uploaded-file {
  margin-top: 10px;
  padding: 10px;
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(147, 112, 219, 0.15);
}

/* WebSocket响应区域样式 */
.websocket-response-section {
  border-top: 1px solid rgba(147, 112, 219, 0.15);
  padding-top: 20px;
}

.websocket-response-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #5a32a3;
}

.websocket-messages {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 15px;
}

.websocket-message-item {
  border: 1px solid rgba(147, 112, 219, 0.15);
  border-radius: 8px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #faf9ff 0%, #f5f3ff 100%);
  overflow: hidden;
}

.websocket-message-item.sent {
  border-left: 3px solid #7b42f6;
}

.websocket-message-item.received {
  border-left: 3px solid #67c23a;
}

.websocket-message-item.info {
  border-left: 3px solid #9370db;
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
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%);
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
  font-size: 12px;
}

.message-type.sent {
  color: #7b42f6;
  font-weight: bold;
}

.message-type.received {
  color: #67c23a;
  font-weight: bold;
}

.message-type.info {
  color: #9370db;
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
  color: #9370db;
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
  color: #5a32a3;
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
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 12px;
  background: linear-gradient(135deg, #faf9ff 0%, #f5f3ff 100%);
}

.assertion-result-item.passed {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f8e8 100%);
}

.assertion-result-item.failed {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
}

.assertion-result-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.assertion-name {
  margin-left: 8px;
  font-weight: 500;
  color: #5a32a3;
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
  color: #9370db;
}

.value {
  flex: 1;
  word-break: break-all;
  color: #5a32a3;
}

.value.error {
  color: #f56c6c;
}

/* 变量提取结果样式 */
.extraction-results {
  padding: 0;
}

.extraction-result-item {
  border-radius: 10px;
  margin-bottom: 12px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.extraction-result-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.extraction-result-item.success {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f6fef6 0%, #f0f9f0 100%);
}

.extraction-result-item.failed {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fff8f8 0%, #fff0f0 100%);
}

.extraction-result-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.06);
}

.extraction-name {
  margin-left: 10px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.extraction-result-details {
  font-size: 13px;
}

.extraction-result-details .result-row {
  display: flex;
  margin-bottom: 8px;
  align-items: flex-start;
}

.extraction-result-details .label {
  width: 80px;
  font-weight: 500;
  color: #666;
  flex-shrink: 0;
}

.extraction-result-details .value {
  flex: 1;
  word-break: break-all;
  color: #333;
  font-family: 'Courier New', monospace;
  background: rgba(0, 0, 0, 0.02);
  padding: 4px 8px;
  border-radius: 4px;
}

.extraction-result-details .value.extraction-value {
  color: #67c23a;
  font-weight: 600;
  background: rgba(103, 194, 58, 0.08);
}

.extraction-result-details .value.error {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.08);
}

.extracted-variables-summary {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f6fef6 0%, #f0f9f0 100%);
  border-radius: 10px;
  border: 1px solid #67c23a;

  h4 {
    margin: 0 0 16px 0;
    color: #67c23a;
    font-size: 15px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;

    &::before {
      content: '';
      width: 4px;
      height: 16px;
      background: #67c23a;
      border-radius: 2px;
    }
  }
}

.variables-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.variable-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid rgba(103, 194, 58, 0.2);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);

  .variable-key {
    font-weight: 600;
    color: #67c23a;
    margin-right: 16px;
    min-width: 120px;
    font-size: 14px;
  }

  .variable-value {
    flex: 1;
    color: #333;
    word-break: break-all;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    background: rgba(103, 194, 58, 0.05);
    padding: 6px 10px;
    border-radius: 4px;
  }
}

.context-menu {
  position: fixed;
  z-index: 9999;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.2);
  padding: 8px 0;
  margin: 0;
  list-style: none;
  min-width: 140px;
}

.context-menu li {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #5a32a3;
  transition: all 0.3s ease;
}

.context-menu li:hover {
  background: linear-gradient(135deg, rgba(123, 66, 246, 0.1) 0%, rgba(90, 50, 163, 0.05) 100%);
  color: #7b42f6;
}
</style>

<style>
.page-container {
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%) !important;
}
</style>