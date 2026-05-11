<template>
  <div class="automation-suite-detail">
    <div class="content" v-loading="loading">
      <!-- 套件信息卡片 - 放在最上面 -->
      <div class="suite-info-section" v-if="suite">
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">{{ $t('apiTesting.automation.executionEnvironment') }}</div>
            <div class="info-value">{{ getEnvironmentName(suite.environment) }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ $t('apiTesting.automation.requestCount') }}</div>
            <div class="info-value">{{ suite.suite_requests?.length || 0 }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ $t('apiTesting.automation.creator') }}</div>
            <div class="info-value">{{ suite.created_by?.username }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ $t('apiTesting.automation.createTime') }}</div>
            <div class="info-value">{{ formatDate(suite.created_at) }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ $t('apiTesting.automation.updateTime') }}</div>
            <div class="info-value">{{ formatDate(suite.updated_at) }}</div>
          </div>
        </div>
      </div>

      <!-- 标题和操作按钮 - 放在卡片下面 -->
      <div class="header">
        <div class="header-left">
          <span class="page-title">{{ suite?.name || $t('apiTesting.automation.suiteDetail') }}</span>
          <!-- 评审状态徽章 -->
          <span v-if="reviewSummary" class="review-status-badge" :class="reviewSummary?.overall_status">
            {{ getReviewStatusText(reviewSummary?.overall_status) }}
          </span>
        </div>
        <div class="header-actions" v-if="suite">
          <el-button type="success" @click="runTestSuite" :loading="running">
            <el-icon><VideoPlay /></el-icon>
            {{ $t('apiTesting.automation.runTest') }}
          </el-button>
          <el-button type="warning" @click="showAddRequest">
            <el-icon><Plus /></el-icon>
            {{ $t('apiTesting.automation.addRequest') }}
          </el-button>
          <!-- 评审按钮 - 只有未评审且不是创建者时显示 -->
          <template v-if="reviewSummary && !userHasReviewed && !isCreator">
            <el-button type="success" @click="submitReview('approved')">
              <el-icon><Check /></el-icon>
              通过
            </el-button>
            <el-button type="danger" @click="showRejectDialog = true">
              <el-icon><Close /></el-icon>
              拒绝
            </el-button>
          </template>
          <el-button type="primary" @click="editSuite">
            <el-icon><Edit /></el-icon>
            {{ $t('apiTesting.common.edit') }}
          </el-button>
        </div>
      </div>

      <!-- 场景编排 -->
      <div class="requests-section" v-if="suite">
        <div class="section-header">
          <h4>场景编排</h4>
        </div>
        
        <div class="requests-tree" v-if="suite.suite_requests?.length > 0">
          <suite-request-tree
            v-for="(req, index) in suite.suite_requests"
            :key="req.id"
            :request="req"
            :index="index"
            :level="0"
            @edit="editRequest"
            @remove="removeRequest"
            @toggle-enabled="updateRequestEnabled"
          />
        </div>
        
        <el-empty v-else :description="$t('apiTesting.automation.noRequests')" class="requests-empty" />
      </div>

      <!-- 评审区域 - 有评审记录且(未通过或非创建人)时显示 -->
      <div class="review-section" v-if="suite && reviewRecords.length > 0 && (reviewSummary?.overall_status !== 'approved' || !isCreator)">
        <div class="section-header">
          <div class="header-left">
            <h4>场景评审</h4>
          </div>
        </div>

        <el-table :data="reviewRecords" v-loading="reviewLoading" size="small">
          <el-table-column type="index" :label="$t('apiTesting.common.sequence')" width="60" align="center">
            <template #default="scope">
              {{ scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="scope">
              <span class="status-badge" :class="scope.row.status">
                {{ getReviewStatusText(scope.row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="意见" min-width="200" align="center">
            <template #default="scope">
              <span style="display: inline-block; width: 100%; text-align: center;">
                {{ scope.row.status === 'approved' ? '-' : (scope.row.comment || '-') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="reviewer.username" label="评审人" width="120" align="center" />
          <el-table-column prop="reviewed_at" label="评审时间" width="200" align="center">
            <template #default="scope">
              {{ formatDate(scope.row.reviewed_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="scope">
              <!-- 重新发起评审按钮 - 只有创建者且状态为拒绝时显示 -->
              <el-button
                v-if="isCreator && scope.row.status === 'rejected'"
                size="small"
                class="action-btn reset-btn"
                @click="resetReviews"
              >
                重新发起评审
              </el-button>
              <!-- 评审人操作按钮 -->
              <div v-else-if="scope.row.reviewer?.id === currentUser?.id" class="review-actions">
                <template v-if="scope.row.status === 'pending'">
                  <el-button
                    size="small"
                    class="action-btn approve-btn"
                    @click="submitReview('approved')"
                  >
                    通过
                  </el-button>
                  <el-button
                    size="small"
                    class="action-btn reject-btn"
                    @click="showRejectDialog = true"
                  >
                    拒绝
                  </el-button>
                </template>
                <template v-else>
                  <el-button
                    size="small"
                    class="action-btn edit-review-btn"
                    @click="editReview(scope.row)"
                  >
                    修改评审
                  </el-button>
                </template>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 拒绝原因对话框 -->
      <el-dialog v-model="showRejectDialog" title="拒绝原因" width="500px">
        <el-input
          v-model="rejectComment"
          type="textarea"
          :rows="4"
          placeholder="请输入拒绝原因（可选）"
        />
        <template #footer>
          <el-button @click="showRejectDialog = false">取消</el-button>
          <el-button type="primary" @click="submitReview('rejected')">确认</el-button>
        </template>
      </el-dialog>

      <!-- 执行历史 -->
      <div class="executions-section" v-if="suite">
        <div class="section-header">
          <h4>{{ $t('apiTesting.automation.executionHistory') }}</h4>
        </div>

        <el-table :data="executions" v-loading="executionsLoading" v-if="executions.length > 0">
          <el-table-column type="index" :label="$t('apiTesting.common.sequence')" width="60" align="center" />
          <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="100" align="center">
            <template #default="scope">
              <span class="status-badge" :class="scope.row.status?.toLowerCase()">
                {{ getStatusText(scope.row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="total_requests" :label="$t('apiTesting.automation.totalRequests')" min-width="110" align="center" />
          <el-table-column prop="passed_requests" :label="$t('apiTesting.automation.passedCount')" min-width="90" align="center">
            <template #default="scope">
              <span style="color: #67c23a">{{ scope.row.passed_requests }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="failed_requests" :label="$t('apiTesting.automation.failedCount')" min-width="90" align="center">
            <template #default="scope">
              <span style="color: #f56c6c">{{ scope.row.failed_requests }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="$t('apiTesting.automation.averageTime')" min-width="100" align="center">
            <template #default="scope">
              {{ getAverageExecutionTime(scope.row) }}
            </template>
          </el-table-column>
          <el-table-column prop="executed_by.username" :label="$t('apiTesting.automation.executor')" width="120" align="center" />
          <el-table-column prop="created_at" :label="$t('apiTesting.automation.executionTime')" width="200" align="center">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('apiTesting.common.operation')" width="120" align="center">
            <template #default="scope">
              <el-button size="small" class="action-btn view-detail-btn" @click="viewExecutionDetail(scope.row)">
                {{ $t('apiTesting.automation.viewDetails') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty v-else :description="$t('apiTesting.automation.noExecutions')" />
      </div>
    </div>

    <!-- 创建/编辑测试套件对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="$t('apiTesting.automation.editSuite')"
      width="600px"
      @close="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item :label="$t('apiTesting.automation.suiteName')" prop="name">
          <el-input v-model="editForm.name" :placeholder="$t('apiTesting.automation.inputSuiteName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.automation.suiteDescription')" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('apiTesting.automation.inputSuiteDescription')"
            class="suite-textarea"
          />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.automation.executionEnvironment')" prop="environment">
          <el-select v-model="editForm.environment" :placeholder="$t('apiTesting.automation.selectEnvironment')" clearable class="env-select">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitEditForm" :loading="submitting">
          {{ $t('apiTesting.common.update') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加请求对话框 -->
    <el-dialog
      v-model="showAddRequestDialog"
      :title="$t('apiTesting.automation.addRequestToSuite')"
      width="800px"
    >
      <div class="add-request-content">
        <div class="request-selector">
          <el-tree
            ref="requestTreeRef"
            :data="requestTree"
            :props="requestTreeProps"
            show-checkbox
            node-key="id"
            :check-on-click-node="false"
            @check="onRequestCheck"
          >
            <template #default="{ node, data }">
              <div class="request-tree-node">
                <el-icon v-if="data.type === 'collection'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>
                <span>{{ data.name }}</span>
                <span v-if="data.type === 'request'" class="method-tag" :class="data.method?.toLowerCase()">
                  {{ data.method }}
                </span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showAddRequestDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="addSelectedRequests" :loading="addingRequests">
          {{ $t('apiTesting.automation.addSelectedRequests') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行结果抽屉 -->
    <el-drawer
      v-model="showExecutionDialog"
      :title="$t('apiTesting.automation.testExecutionResult')"
      size="70%"
      direction="rtl"
      :destroy-on-close="true"
      class="result-drawer"
    >
      <div v-if="currentExecution" class="execution-detail-drawer">
        <!-- 统计概览卡片 -->
        <div class="summary-cards">
          <el-row :gutter="16">
            <el-col :xs="12" :sm="12" :md="6" :lg="6">
              <div class="summary-card">
                <div class="card-icon total">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="card-content">
                  <div class="card-label">{{ $t('apiTesting.automation.totalRequests') }}</div>
                  <div class="card-value">{{ currentExecution.total_requests }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="12" :md="6" :lg="6">
              <div class="summary-card success">
                <div class="card-icon">
                  <el-icon><CircleCheck /></el-icon>
                </div>
                <div class="card-content">
                  <div class="card-label">{{ $t('apiTesting.automation.passedCount') }}</div>
                  <div class="card-value">{{ currentExecution.passed_requests }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="12" :md="6" :lg="6">
              <div class="summary-card failed">
                <div class="card-icon">
                  <el-icon><CircleClose /></el-icon>
                </div>
                <div class="card-content">
                  <div class="card-label">{{ $t('apiTesting.automation.failedCount') }}</div>
                  <div class="card-value">{{ currentExecution.failed_requests }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="12" :md="6" :lg="6">
              <div class="summary-card primary">
                <div class="card-icon">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="card-content">
                  <div class="card-label">{{ $t('apiTesting.automation.passRate') }}</div>
                  <div class="card-value">{{ getPassRate(currentExecution) }}%</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 详细结果表格 -->
        <div class="result-table-section">
          <div class="section-header">
            <h4 class="section-title">
              <el-icon><List /></el-icon>
              {{ $t('apiTesting.automation.detailedResults') }}
            </h4>
          </div>
          <div class="table-wrapper">
            <el-table :data="formatExecutionResults(currentExecution.results)" class="custom-table">
              <el-table-column type="index" label="序号" width="70" header-align="center" align="center" />
              <el-table-column prop="name" :label="$t('apiTesting.automation.requestName')" min-width="150" header-align="center" align="center" />
              <el-table-column prop="method" :label="$t('apiTesting.automation.method')" width="100" header-align="center" align="center">
                <template #default="scope">
                  <span class="method-badge" :class="scope.row.method?.toLowerCase()">
                    {{ scope.row.method }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="status" :label="$t('apiTesting.automation.result')" width="100" header-align="center" align="center">
                <template #default="scope">
                  <span class="status-badge" :class="scope.row.passed ? 'success' : 'failed'">
                    {{ scope.row.passed ? $t('apiTesting.automation.testStatus.passed') : $t('apiTesting.automation.testStatus.failed') }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="status_code" :label="$t('apiTesting.automation.statusCode')" width="100" header-align="center" align="center" />
              <el-table-column prop="response_time" :label="$t('apiTesting.automation.responseTime')" width="100" header-align="center" align="center">
                <template #default="scope">
                  {{ scope.row.response_time?.toFixed(0) }}ms
                </template>
              </el-table-column>

              <el-table-column :label="$t('apiTesting.common.operation')" width="100" fixed="right" header-align="center" align="center">
                <template #default="scope">
                  <el-button link type="primary" size="small" @click="viewRequestDetail(scope.row)">
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 请求详情抽屉 -->
    <el-drawer
      v-model="showRequestDetailDialog"
      title="请求执行详情"
      size="50%"
      direction="rtl"
      :destroy-on-close="true"
      class="detail-drawer"
    >
      <div v-if="currentRequestDetail" class="request-detail-drawer">
        <!-- 顶部状态栏 -->
        <div class="request-header">
          <div class="request-title-row">
            <span class="request-name">{{ currentRequestDetail.name }}</span>
            <span class="method-tag" :class="currentRequestDetail.method?.toLowerCase()">{{ currentRequestDetail.method }}</span>
            <span class="status-tag" :class="currentRequestDetail.passed ? 'success' : 'failed'">
              {{ currentRequestDetail.passed ? '通过' : '失败' }}
            </span>
            <span class="meta-tag time-tag">{{ currentRequestDetail.response_time?.toFixed(0) }}ms</span>
            <span class="meta-tag code-tag">{{ currentRequestDetail.status_code }}</span>
          </div>
          <div class="request-url">{{ currentRequestDetail.url }}</div>
        </div>

        <!-- 错误信息 -->
        <div v-if="currentRequestDetail.error" class="error-banner">
          <el-icon><WarningFilled /></el-icon>
          <span>{{ currentRequestDetail.error }}</span>
        </div>

        <!-- 数据交换区域 -->
        <div class="data-section" v-if="currentRequestDetail.request_data || currentRequestDetail.response_data">
          <!-- 主标签切换 -->
          <div class="main-tabs">
            <button 
              class="main-tab-btn" 
              :class="{ active: activeDataTab === 'request' }"
              @click="activeDataTab = 'request'"
            >
              请求
            </button>
            <button 
              class="main-tab-btn" 
              :class="{ active: activeDataTab === 'response' }"
              @click="activeDataTab = 'response'"
            >
              响应
            </button>
          </div>
          
          <!-- 请求内容 -->
          <div v-if="activeDataTab === 'request' && currentRequestDetail.request_data" class="data-panel">
            <div class="panel-header">
              <div class="sub-tabs">
                <button 
                  v-for="tab in ['body', 'headers', 'params']" 
                  :key="tab"
                  class="sub-tab-btn"
                  :class="{ active: activeRequestTab === tab }"
                  @click="activeRequestTab = tab"
                >
                  {{ tab.toUpperCase() }}
                </button>
              </div>
              <span class="data-badge">{{ activeRequestTab.toUpperCase() }}</span>
            </div>
            <div class="code-container">
              <json-tree-viewer 
                :data="getRequestDataRaw()" 
                :root-path="getRequestJsonPathRoot()"
              />
            </div>
          </div>
          
          <!-- 响应内容 -->
          <div v-if="activeDataTab === 'response' && currentRequestDetail.response_data" class="data-panel">
            <div class="panel-header">
              <div class="sub-tabs">
                <button 
                  v-for="tab in responseTabs" 
                  :key="tab.key"
                  class="sub-tab-btn"
                  :class="{ active: activeResponseTab === tab.key }"
                  @click="activeResponseTab = tab.key"
                >
                  {{ tab.label }}
                </button>
              </div>
              <span class="data-badge">{{ activeResponseTab.toUpperCase() }}</span>
            </div>
            <div class="code-container" v-if="activeResponseTab !== 'assertions'">
              <json-tree-viewer 
                :data="getResponseDataRaw()" 
                :root-path="getJsonPathRoot()"
              />
            </div>
            <div class="assertions-container" v-else>
              <div class="assertion-list">
                <div v-for="(item, idx) in currentRequestDetail.assertions_results" :key="idx" class="assertion-item" :class="item.passed ? 'passed' : 'failed'">
                  <el-icon><CircleCheck v-if="item.passed" /><CircleClose v-else /></el-icon>
                  <span class="assertion-name">{{ item.name }}</span>
                  <span class="assertion-detail">
                    <span class="detail-item expected">
                      <span class="label">期望</span>
                      <span class="value" :class="{ null: item.expected === null && !item.expected_desc, object: typeof item.expected === 'object' }">
                        {{ item.expected_desc || (item.expected === null ? 'null' : (typeof item.expected === 'object' ? JSON.stringify(item.expected).substring(0, 30) + '...' : item.expected)) }}
                      </span>
                    </span>
                    <span class="separator">|</span>
                    <span class="detail-item actual" :class="{ mismatch: !item.passed && item.actual !== item.expected }">
                      <span class="label">实际</span>
                      <span class="value" :class="{ null: item.actual === null, object: typeof item.actual === 'object' }">
                        {{ item.actual === null ? 'null' : (typeof item.actual === 'object' ? JSON.stringify(item.actual).substring(0, 30) + '...' : item.actual) }}
                      </span>
                    </span>
                  </span>
                  <span v-if="item.error" class="assertion-error">{{ item.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 变量提取 -->
        <div v-if="currentRequestDetail.variable_results && Object.keys(currentRequestDetail.variable_results).length > 0" class="variables-section">
          <div class="section-title-compact">
            <el-icon><Collection /></el-icon>
            <span>变量提取</span>
          </div>
          <div class="variables-grid">
            <div v-for="(value, key) in currentRequestDetail.variable_results" :key="key" class="variable-item">
              <span class="var-key">{{ key }}</span>
              <span class="var-value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 接口编辑抽屉 -->
    <el-drawer
      v-model="showEditRequestDialog"
      title="编辑接口"
      size="900px"
      destroy-on-close
      class="edit-request-drawer"
    >
      <el-tabs v-model="editDrawerActiveTab" class="drawer-tabs">
        <!-- 基础信息 -->
        <el-tab-pane label="基础信息" name="basic">
          <el-form :model="editingRequestData" label-width="100px">
            <el-form-item label="接口名称">
              <el-input v-model="editingRequestData.name" placeholder="输入接口名称" />
            </el-form-item>
            <el-form-item label="请求方法">
              <el-select v-model="editingRequestData.method" style="width: 120px">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
                <el-option label="HEAD" value="HEAD" />
                <el-option label="OPTIONS" value="OPTIONS" />
              </el-select>
            </el-form-item>
            <el-form-item label="请求URL">
              <el-input ref="urlInputRef" v-model="editingRequestData.url" placeholder="输入完整的请求URL">
                <template #append>
                  <el-button @click="openVariablePicker('url')" title="插入变量">
                    <el-icon><MagicStick /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 请求头 -->
        <el-tab-pane label="请求头" name="headers">
          <div class="key-value-editor">
            <div class="editor-header">
              <el-button size="small" @click="addEditingHeader">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
            <div class="kv-list">
              <div v-for="(item, index) in editingHeadersList" :key="index" class="kv-item">
                <el-input v-model="item.key" placeholder="Header 名称" class="kv-key" />
                <el-input v-model="item.value" placeholder="Header 值" class="kv-value">
                  <template #append>
                    <el-button @click="openVariablePicker('header', index)" title="插入变量">
                      <el-icon><MagicStick /></el-icon>
                    </el-button>
                  </template>
                </el-input>
                <el-button type="danger" size="small" circle @click="removeEditingHeader(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 请求参数 -->
        <el-tab-pane label="请求参数" name="params">
          <div class="key-value-editor">
            <div class="editor-header">
              <el-button size="small" @click="addEditingParam">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
            <div class="kv-list">
              <div v-for="(item, index) in editingParamsList" :key="index" class="kv-item">
                <el-input v-model="item.key" placeholder="参数名" class="kv-key" />
                <el-input v-model="item.value" placeholder="参数值" class="kv-value">
                  <template #append>
                    <el-button @click="openVariablePicker('param', index)" title="插入变量">
                      <el-icon><MagicStick /></el-icon>
                    </el-button>
                  </template>
                </el-input>
                <el-button type="danger" size="small" circle @click="removeEditingParam(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 请求体 -->
        <el-tab-pane label="请求体" name="body" v-if="['POST', 'PUT', 'PATCH'].includes(editingRequestData.method)">
          <div class="body-editor">
            <div class="body-toolbar">
              <el-radio-group v-model="editingRequestData.bodyType" size="small">
                <el-radio-button label="json">JSON</el-radio-button>
                <el-radio-button label="raw">Raw</el-radio-button>
              </el-radio-group>
              <el-button 
                size="small"
                @click="openVariablePicker('body')"
                title="插入变量"
              >
                <el-icon><MagicStick /></el-icon>
                插入变量
              </el-button>
            </div>
            <div class="body-input-wrapper">
              <el-input
                ref="bodyInputRef"
                v-model="editingRequestData.bodyContent"
                type="textarea"
                :rows="15"
                placeholder="输入请求体内容，支持 {{$env.variable}} 语法引用环境变量"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 提取变量 -->
        <el-tab-pane label="提取变量" name="extractors">
          <div class="variable-extractors-editor">
            <div class="extractors-header" style="margin-bottom: 16px;">
              <el-button size="small" type="primary" @click="addEditingExtractor">
                <el-icon><Plus /></el-icon> 添加提取规则
              </el-button>
              <span class="extractors-hint" style="margin-left: 12px; color: #909399; font-size: 12px;">从响应中提取变量供后续接口使用</span>
            </div>
            <div class="extractors-table" v-if="editingExtractorsList && editingExtractorsList.length > 0">
              <div class="extractors-table-header" style="display: flex; padding: 8px; background: #f5f7fa; font-weight: 500; font-size: 13px;">
                <div style="flex: 1.5;">规则名称</div>
                <div style="flex: 1;">提取来源</div>
                <div style="flex: 2;">提取路径/Header名</div>
                <div style="flex: 1;">变量名</div>
                <div style="width: 50px;">操作</div>
              </div>
              <div class="extractors-table-body">
                <div
                  v-for="(extractor, index) in editingExtractorsList"
                  :key="index"
                  style="display: flex; padding: 8px; align-items: center; border-bottom: 1px solid #ebeef5;"
                >
                  <div style="flex: 1.5; padding-right: 8px;">
                    <el-input
                      v-model="extractor.name"
                      placeholder="规则名称"
                      size="small"
                    />
                  </div>
                  <div style="flex: 1; padding-right: 8px;">
                    <el-select
                      v-model="extractor.source"
                      placeholder="选择来源"
                      size="small"
                    >
                      <el-option label="JSON Body" value="json_body" />
                      <el-option label="Response Header" value="header" />
                    </el-select>
                  </div>
                  <div style="flex: 2; padding-right: 8px;">
                    <el-input
                      v-if="extractor.source === 'json_body'"
                      v-model="extractor.json_path"
                      placeholder="JSON Path 表达式"
                      size="small"
                    >
                      <template #append>
                        <el-button @click="openVariablePicker('extractor_json_path', index)" title="插入变量">
                          <el-icon><MagicStick /></el-icon>
                        </el-button>
                      </template>
                    </el-input>
                    <el-input
                      v-else-if="extractor.source === 'header'"
                      v-model="extractor.header_name"
                      placeholder="Header 名称"
                      size="small"
                    >
                      <template #append>
                        <el-button @click="openVariablePicker('extractor_header_name', index)" title="插入变量">
                          <el-icon><MagicStick /></el-icon>
                        </el-button>
                      </template>
                    </el-input>
                    <el-input
                      v-else
                      placeholder="请先选择提取来源"
                      size="small"
                      disabled
                    />
                  </div>
                  <div style="flex: 1; padding-right: 8px;">
                    <el-input
                      v-model="extractor.variable_name"
                      placeholder="变量名"
                      size="small"
                    />
                  </div>
                  <div style="width: 50px;">
                    <el-button
                      size="small"
                      type="danger"
                      @click="removeEditingExtractor(index)"
                      circle
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else style="text-align: center; padding: 40px; color: #909399;">
              <p>暂无提取规则</p>
              <el-button size="small" type="primary" @click="addEditingExtractor">
                <el-icon><Plus /></el-icon> 添加第一条规则
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 断言 -->
        <el-tab-pane label="断言" name="assertions">
          <div class="assertions-editor">
            <div class="assertions-header" style="margin-bottom: 16px; display: flex; gap: 12px;">
              <el-button size="small" type="primary" @click="addEditingAssertion">
                <el-icon><Plus /></el-icon> 添加断言
              </el-button>
            </div>
            <div class="assertions-table" v-if="editingAssertionsList && editingAssertionsList.length > 0">
              <div class="assertions-table-header" style="display: flex; padding: 8px; background: #f5f7fa; font-weight: 500; font-size: 13px;">
                <div style="flex: 1.5;">断言名称</div>
                <div style="flex: 1;">断言类型</div>
                <div style="flex: 2.5;">参数</div>
                <div style="width: 50px;">操作</div>
              </div>
              <div class="assertions-table-body">
                <div
                  v-for="(assertion, index) in editingAssertionsList"
                  :key="index"
                  style="display: flex; padding: 8px; align-items: center; border-bottom: 1px solid #ebeef5;"
                >
                  <div style="flex: 1.5; padding-right: 8px;">
                    <el-input
                      v-model="assertion.name"
                      placeholder="断言名称"
                      size="small"
                    />
                  </div>
                  <div style="flex: 1; padding-right: 8px;">
                    <el-select
                      v-model="assertion.type"
                      placeholder="选择类型"
                      size="small"
                      @change="onEditingAssertionTypeChange(assertion)"
                    >
                      <el-option label="状态码" value="status_code" />
                      <el-option label="响应时间" value="response_time" />
                      <el-option label="包含文本" value="contains" />
                      <el-option label="JSON Path" value="json_path" />
                      <el-option label="Header" value="header" />
                      <el-option label="完全匹配" value="equals" />
                    </el-select>
                  </div>
                  <div style="flex: 2.5; padding-right: 8px;">
                    <el-input-number
                      v-if="assertion.type === 'status_code'"
                      v-model="assertion.expected"
                      :min="100"
                      :max="599"
                      size="small"
                      placeholder="预期状态码"
                    />
                    <el-input-number
                      v-else-if="assertion.type === 'response_time'"
                      v-model="assertion.expected"
                      :min="1"
                      size="small"
                      placeholder="最大响应时间(ms)"
                    />
                    <el-input
                      v-else-if="assertion.type === 'contains'"
                      v-model="assertion.expected"
                      placeholder="预期包含的文本"
                      size="small"
                    >
                      <template #append>
                        <el-button @click="openVariablePicker('assertion_contains', index)" title="插入变量">
                          <el-icon><MagicStick /></el-icon>
                        </el-button>
                      </template>
                    </el-input>
                    <div v-else-if="assertion.type === 'json_path'" style="display: flex; gap: 8px;">
                      <el-input
                        v-model="assertion.json_path"
                        placeholder="JSON Path"
                        size="small"
                        style="flex: 1;"
                      >
                        <template #append>
                          <el-button @click="openVariablePicker('assertion_json_path', index)" title="插入变量">
                            <el-icon><MagicStick /></el-icon>
                          </el-button>
                        </template>
                      </el-input>
                      <el-input
                        v-model="assertion.expected"
                        :placeholder="getExpectedPlaceholder(assertion)"
                        size="small"
                        style="flex: 1;"
                      >
                        <template #append>
                          <el-button @click="openVariablePicker('assertion_json_expected', index)" title="插入变量">
                            <el-icon><MagicStick /></el-icon>
                          </el-button>
                        </template>
                      </el-input>
                    </div>
                    <div v-else-if="assertion.type === 'header'" style="display: flex; gap: 8px;">
                      <el-input
                        v-model="assertion.header_name"
                        placeholder="Header名称"
                        size="small"
                        style="flex: 1;"
                      >
                        <template #append>
                          <el-button @click="openVariablePicker('assertion_header_name', index)" title="插入变量">
                            <el-icon><MagicStick /></el-icon>
                          </el-button>
                        </template>
                      </el-input>
                      <el-input
                        v-model="assertion.expected_value"
                        placeholder="预期值"
                        size="small"
                        style="flex: 1;"
                      >
                        <template #append>
                          <el-button @click="openVariablePicker('assertion_header_expected', index)" title="插入变量">
                            <el-icon><MagicStick /></el-icon>
                          </el-button>
                        </template>
                      </el-input>
                    </div>
                    <el-input
                      v-else-if="assertion.type === 'equals'"
                      v-model="assertion.expected"
                      placeholder="预期匹配内容"
                      size="small"
                    >
                      <template #append>
                        <el-button @click="openVariablePicker('assertion_equals', index)" title="插入变量">
                          <el-icon><MagicStick /></el-icon>
                        </el-button>
                      </template>
                    </el-input>
                    <el-input
                      v-else
                      placeholder="请先选择断言类型"
                      size="small"
                      disabled
                    />
                  </div>
                  <div style="width: 50px;">
                    <el-button
                      size="small"
                      type="danger"
                      @click="removeEditingAssertion(index)"
                      circle
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else style="text-align: center; padding: 40px; color: #909399;">
              <p>暂无断言</p>
              <el-button size="small" type="primary" @click="addEditingAssertion">
                <el-icon><Plus /></el-icon> 添加第一条断言
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="drawer-footer">
          <el-button @click="showEditRequestDialog = false">取消</el-button>
          <el-button type="primary" @click="saveRequestEdit" :loading="savingRequestEdit">保存</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 变量选择器抽屉 -->
    <el-drawer
      v-model="showVariablePickerDialog"
      title="插入动态值"
      size="450px"
      direction="rtl"
      :close-on-click-modal="false"
      append-to-body
    >
      <div class="variable-picker-content">
        <div class="picker-section">
          <div class="section-title">选择变量类型</div>
          <el-radio-group v-model="selectedVarCategory" size="small">
            <el-radio-button label="prev">前置接口</el-radio-button>
            <el-radio-button label="env">环境变量</el-radio-button>
            <el-radio-button label="global">全局变量</el-radio-button>
            <el-radio-button label="dynamic">动态函数</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 前置接口变量 -->
        <div v-if="selectedVarCategory === 'prev'" class="picker-section">
          <div v-if="previousRequests.length === 0" class="no-prev-requests">
            <el-alert
              title="没有可用的前置接口"
              type="warning"
              :closable="false"
              description="当前接口是集合中的第一个接口，或集合中没有其他接口。"
            />
          </div>
          <div v-else>
            <div class="section-title">选择前置接口</div>
            <el-select v-model="selectedPrevRequestId" placeholder="选择要引用的接口" style="width: 100%" @change="onPrevRequestChange">
              <el-option
                v-for="req in previousRequests"
                :key="req.id"
                :label="`${req.displayOrder}. ${req.alias || req.request?.name || '未命名接口'}`"
                :value="req.id"
              >
                <div class="request-option">
                  <span class="request-order">{{ req.displayOrder }}</span>
                  <span class="request-name">{{ req.alias || req.request?.name || '未命名接口' }}</span>
                  <el-tag v-if="req.alias" size="small" type="info">别名: {{ req.alias }}</el-tag>
                </div>
              </el-option>
            </el-select>

            <div v-if="selectedPrevRequest" class="var-type-section">
              <div class="section-title">选择变量类型</div>
              <el-radio-group v-model="selectedVarType" size="small" @change="onVarTypeChange">
                <el-radio-button label="request.body">请求体</el-radio-button>
                <el-radio-button label="response.body">响应体</el-radio-button>
                <el-radio-button label="response.headers">响应头</el-radio-button>
                <el-radio-button label="response.status_code">状态码</el-radio-button>
                <el-radio-button label="response.response_time">响应时间</el-radio-button>
              </el-radio-group>
            </div>

            <!-- 执行结果展示区域 -->
            <div v-if="selectedPrevRequest && selectedVarType && previewData" class="execution-preview-section">
              <div class="section-title">
                点击字段复制路径
                <el-tag v-if="selectedPrevRequestExecution" size="small" :type="selectedPrevRequestExecution.passed ? 'success' : 'danger'">
                  {{ selectedPrevRequestExecution.passed ? '通过' : '失败' }}
                </el-tag>
              </div>
              <div class="preview-data-container">
                <json-tree-viewer
                  :data="previewData"
                  :root-path="getVariablePreviewRoot()"
                  @copy-path="onJsonPathCopy"
                />
              </div>
            </div>

            <div v-if="selectedPrevRequest && loadingExecution" class="execution-loading">
              <el-skeleton :rows="3" animated />
            </div>

            <div v-if="selectedPrevRequest && executionError" class="execution-error">
              <el-alert
                :title="executionError"
                type="warning"
                :closable="false"
                show-icon
              />
            </div>

            <div v-if="selectedPrevRequest && needsJsonPath" class="json-path-section">
              <div class="section-title">
                JSON Path（已自动填充，可手动修改）
                <el-tooltip content="例如: $.data.id 或 $.list[0].name">
                  <el-icon><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-input
                v-model="jsonPath"
                placeholder="点击上方字段自动生成"
                clearable
              />
            </div>
          </div>
        </div>

        <!-- 环境变量 -->
        <div v-if="selectedVarCategory === 'env'" class="picker-section">
          <div class="section-title">环境变量名</div>
          <el-input
            v-model="varName"
            placeholder="如: base_url, api_key"
          />
          <div class="var-hint" v-pre>用法: {{$env.变量名}}</div>
        </div>

        <!-- 全局变量 -->
        <div v-if="selectedVarCategory === 'global'" class="picker-section">
          <div class="section-title">全局变量名</div>
          <el-input
            v-model="varName"
            placeholder="如: token, user_id"
          />
          <div class="var-hint" v-pre>用法: {{$global.变量名}}</div>
        </div>

        <!-- 动态函数 -->
        <div v-if="selectedVarCategory === 'dynamic'" class="picker-section">
          <div class="section-title">选择函数</div>
          <el-select v-model="selectedFunction" style="width: 100%">
            <el-option label="随机字符串" value="random_string" />
            <el-option label="随机数字" value="random_int" />
            <el-option label="UUID" value="uuid" />
            <el-option label="时间戳" value="timestamp" />
          </el-select>
          <div v-if="selectedFunction === 'random_string' || selectedFunction === 'random_int'" class="function-params">
            <div class="section-title">参数</div>
            <el-input-number v-model="funcParam1" :min="1" :max="100" style="width: 120px" />
            <span class="param-hint">长度/范围</span>
          </div>
          <div class="var-hint" v-pre>用法: {{$函数名(参数)}}</div>
        </div>

        <div class="preview-section">
          <div class="section-title">预览</div>
          <el-input v-model="variablePreview" readonly class="preview-input">
            <template #append>
              <el-button @click="copyVariableToClipboard">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </div>

      <template #footer>
        <el-button @click="closeVariablePicker">取消</el-button>
        <el-button type="primary" @click="confirmVariableInsertion">插入</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import Sortable from 'sortablejs'
import api from '@/utils/api'
import { updateTestSuiteRequest } from '@/api/api-testing'
import SuiteRequestTree from './components/SuiteRequestTree.vue'
import JsonTreeViewer from '@/components/JsonTreeViewer.vue'
import { VideoPlay, Plus, Refresh, Folder, Document, Check, Close, RefreshLeft, Edit, Delete, Rank, CircleCheck, CircleClose, TrendCharts, List, InfoFilled, WarningFilled, Upload, Download, Collection, Timer, DocumentChecked, MagicStick, CopyDocument } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()

// 数据
const suite = ref(null)
const environments = ref([])
const executions = ref([])
const loading = ref(false)
const executionsLoading = ref(false)
const running = ref(false)
const requestTree = ref([])

// 评审相关
const reviewRecords = ref([])
const reviewSummary = ref(null)
const showRejectDialog = ref(false)
const reviewLoading = ref(false)
const rejectComment = ref('')
const userHasReviewed = computed(() => {
  return reviewRecords.value.some(r => r.reviewer?.id === currentUser.value?.id && r.status !== 'pending')
})
const currentUser = ref(null)
const isCreator = computed(() => {
  return suite.value?.created_by?.id === currentUser.value?.id
})

// 对话框状态
const showEditDialog = ref(false)
const showAddRequestDialog = ref(false)
const showExecutionDialog = ref(false)
const showRequestDetailDialog = ref(false)
const submitting = ref(false)
const addingRequests = ref(false)
const currentExecution = ref(null)
const currentRequestDetail = ref(null)

// 请求详情抽屉状态
const activeDataTab = ref('request')
const activeRequestTab = ref('body')
const activeResponseTab = ref('body')

// 响应 Tab 列表（动态包含断言 Tab）
const responseTabs = computed(() => {
  const tabs = [
    { key: 'body', label: 'BODY' },
    { key: 'headers', label: 'HEADERS' },
    { key: 'json', label: 'JSON' }
  ]
  if (currentRequestDetail.value?.assertions_results?.length > 0) {
    tabs.push({ key: 'assertions', label: `断言(${currentRequestDetail.value.assertions_results.length})` })
  }
  return tabs
})

// 接口编辑相关
const showEditRequestDialog = ref(false)
const editDrawerActiveTab = ref('body')
const savingRequestEdit = ref(false)
const editingRequestData = ref({
  id: null,
  name: '',
  method: 'GET',
  url: '',
  headers: {},
  params: {},
  body: {},
  bodyType: 'json',
  bodyContent: ''
})
const editingHeadersList = ref([])
const editingParamsList = ref([])
const editingExtractorsList = ref([])
const editingAssertionsList = ref([])

// ========== 变量选择器相关 ==========
const showVariablePickerDialog = ref(false)
const selectedVarCategory = ref('env')
const varName = ref('')
const selectedFunction = ref('random_string')
const funcParam1 = ref(8)
const variablePickerTarget = ref({ type: '', index: -1 })

// 输入框 refs（用于光标位置插入）
const urlInputRef = ref(null)
const bodyInputRef = ref(null)

// 光标位置状态
const cursorPosition = ref({ type: '', index: -1, start: 0, end: 0 })

// 跨接口变量选择
const selectedPrevRequestId = ref(null)
const selectedVarType = ref('response.body')
const jsonPath = ref('')
const currentEditingRequestId = ref(null)

// 前置接口执行记录（用于变量选择器展示）
const selectedPrevRequestExecution = ref(null)
const loadingExecution = ref(false)
const executionError = ref('')

// 获取预览数据（用于 JSON 树形展示）
const previewData = computed(() => {
  if (!selectedPrevRequestExecution.value) return null

  const dataType = selectedVarType.value
  const requestData = selectedPrevRequestExecution.value.request_data || {}
  const responseData = selectedPrevRequestExecution.value.response_data || {}

  switch (dataType) {
    case 'request.body':
      return requestData.body || {}
    case 'request.headers':
      return requestData.headers || {}
    case 'request.params':
      return requestData.params || {}
    case 'response.body':
      return responseData.body || responseData.json || {}
    case 'response.headers':
      return responseData.headers || {}
    case 'response.status_code':
      return responseData.status_code
    case 'response.response_time':
      return selectedPrevRequestExecution.value.response_time
    default:
      return null
  }
})

// 获取所有实际请求（排除分组/文件夹节点）的扁平列表
const getAllRequestsFlat = (requests) => {
  const result = []
  const traverse = (items) => {
    items.forEach((item) => {
      // 如果有 request 对象，说明是实际请求
      if (item.request) {
        result.push({
          ...item,
          // 使用数据库的 order 字段，而不是列表索引
          displayOrder: item.order
        })
      }
      // 如果有子节点，递归遍历
      if (item.children && item.children.length > 0) {
        traverse(item.children)
      }
    })
  }
  traverse(requests)
  return result
}

// 获取前置接口列表（在同集合中，排在当前接口之前的接口）
const previousRequests = computed(() => {
  if (!suite.value || !suite.value.suite_requests || !currentEditingRequestId.value) return []
  
  // 获取扁平化的所有请求列表
  const flatRequests = getAllRequestsFlat(suite.value.suite_requests)
  const currentIndex = flatRequests.findIndex(r => r.id === currentEditingRequestId.value)
  if (currentIndex === -1) return []
  
  // 返回当前接口之前的所有接口
  return flatRequests.slice(0, currentIndex)
})

// 选中的前置接口
const selectedPrevRequest = computed(() => {
  return previousRequests.value.find(r => r.id === selectedPrevRequestId.value)
})

// 是否需要 JSON Path
const needsJsonPath = computed(() => {
  return selectedVarType.value.includes('body') || selectedVarType.value.includes('headers')
})

// 变量预览
const variablePreview = computed(() => {
  // 前置接口变量
  if (selectedVarCategory.value === 'prev') {
    if (!selectedPrevRequest.value) return '{{$.接口名.变量类型}}'
    const requestRef = selectedPrevRequest.value.alias || selectedPrevRequest.value.displayOrder
    if (needsJsonPath.value && jsonPath.value) {
      return `{{$.${requestRef}.${selectedVarType.value}.${jsonPath.value}}}`
    }
    return `{{$.${requestRef}.${selectedVarType.value}}}`
  }
  
  // 环境变量
  if (selectedVarCategory.value === 'env') {
    return varName.value ? `{{$env.${varName.value}}}` : '{{$env.变量名}}'
  } else if (selectedVarCategory.value === 'global') {
    return varName.value ? `{{$global.${varName.value}}}` : '{{$global.变量名}}'
  } else if (selectedVarCategory.value === 'dynamic') {
    if (selectedFunction.value === 'random_string' || selectedFunction.value === 'random_int') {
      return `{{$${selectedFunction.value}(${funcParam1.value})}}`
    }
    return `{{$${selectedFunction.value}()}}`
  }
  return ''
})

// 打开变量选择器
const openVariablePicker = (type, index = -1) => {
  variablePickerTarget.value = { type, index }

  // 记录光标位置
  let inputEl = null
  switch (type) {
    case 'url':
      inputEl = urlInputRef.value?.$el?.querySelector('input')
      break
    case 'header':
      // 对于 header 和 param，通过 document.querySelector 获取当前活动的输入框
      inputEl = document.activeElement
      break
    case 'param':
      inputEl = document.activeElement
      break
    case 'body':
      inputEl = bodyInputRef.value?.$el?.querySelector('textarea')
      break
  }

  if (inputEl && (inputEl.tagName === 'INPUT' || inputEl.tagName === 'TEXTAREA')) {
    cursorPosition.value = {
      type,
      index,
      start: inputEl.selectionStart || 0,
      end: inputEl.selectionEnd || 0
    }
  } else {
    // 如果无法获取光标位置，则默认在末尾插入
    let currentValue = ''
    switch (type) {
      case 'url':
        currentValue = editingRequestData.value.url || ''
        break
      case 'header':
        currentValue = index >= 0 ? (editingHeadersList.value[index]?.value || '') : ''
        break
      case 'param':
        currentValue = index >= 0 ? (editingParamsList.value[index]?.value || '') : ''
        break
      case 'body':
        currentValue = editingRequestData.value.bodyContent || ''
        break
    }
    cursorPosition.value = {
      type,
      index,
      start: currentValue.length,
      end: currentValue.length
    }
  }

  // 记录当前正在编辑的接口ID（用于获取前置接口）
  currentEditingRequestId.value = editingRequestData.value.id
  // 重置跨接口变量选择状态
  selectedPrevRequestId.value = null
  selectedVarType.value = 'response.body'
  jsonPath.value = ''
  // 默认选中"前置接口"（如果有前置接口），否则选中"环境变量"
  if (previousRequests.value.length > 0) {
    selectedVarCategory.value = 'prev'
  } else {
    selectedVarCategory.value = 'env'
    varName.value = ''
    selectedFunction.value = 'random_string'
    funcParam1.value = 8
  }
  showVariablePickerDialog.value = true
}

// 关闭变量选择器
const closeVariablePicker = () => {
  showVariablePickerDialog.value = false
  variablePickerTarget.value = { type: '', index: -1 }
  // 清空执行记录
  selectedPrevRequestExecution.value = null
  executionError.value = ''
}

// 前置接口变更时加载执行记录
const onPrevRequestChange = async () => {
  if (!selectedPrevRequest.value) return

  loadingExecution.value = true
  executionError.value = ''
  selectedPrevRequestExecution.value = null

  try {
    // request 可能是对象 {id: xxx, ...} 或直接的 ID
    let requestId = null
    const request = selectedPrevRequest.value?.request

    if (request) {
      if (typeof request === 'object') {
        requestId = request.id
      } else if (typeof request === 'number') {
        requestId = request
      } else if (typeof request === 'string') {
        requestId = parseInt(request, 10)
      }
    }

    if (!requestId) {
      executionError.value = '该接口没有关联的请求ID'
      return
    }

    // 确保 requestId 是数字
    const numericRequestId = Number(requestId)

    const response = await api.get('/api-testing/histories/latest/', {
      params: { request_id: numericRequestId }
    })

    selectedPrevRequestExecution.value = response.data
  } catch (error) {
    console.error('加载执行记录失败:', error)
    executionError.value = error.response?.data?.error || '加载执行记录失败，请确保该接口已执行过'
  } finally {
    loadingExecution.value = false
  }
}

// 变量类型变更时清空 JSON Path
const onVarTypeChange = () => {
  jsonPath.value = ''
}

// 获取变量预览的根路径
const getVariablePreviewRoot = () => {
  if (!selectedPrevRequest.value) return '$'
  const requestRef = selectedPrevRequest.value.alias || selectedPrevRequest.value.displayOrder
  return `$.${requestRef}.${selectedVarType.value}`
}

// 点击 JSON 字段复制路径
const onJsonPathCopy = (fullPath) => {
  // 从完整路径中提取 JSON Path 部分
  // 例如: $.2.response.body.data.id -> data.id
  const match = fullPath.match(/\$\.\w+\.(request|response)\.(body|headers|params)\.?(.+)?/)
  if (match && match[3]) {
    jsonPath.value = match[3]
  } else if (match) {
    jsonPath.value = ''
  }
}

// 确认插入变量
const confirmVariableInsertion = () => {
  const variable = variablePreview.value
  const { type, index } = variablePickerTarget.value
  const { start, end } = cursorPosition.value

  switch (type) {
    case 'url': {
      const currentUrl = editingRequestData.value.url || ''
      editingRequestData.value.url = currentUrl.substring(0, start) + variable + currentUrl.substring(end)
      break
    }
    case 'header':
      if (index >= 0 && editingHeadersList.value[index]) {
        const currentValue = editingHeadersList.value[index].value || ''
        editingHeadersList.value[index].value = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'param':
      if (index >= 0 && editingParamsList.value[index]) {
        const currentValue = editingParamsList.value[index].value || ''
        editingParamsList.value[index].value = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'body': {
      const currentBody = editingRequestData.value.bodyContent || ''
      editingRequestData.value.bodyContent = currentBody.substring(0, start) + variable + currentBody.substring(end)
      break
    }
    case 'extractor_json_path':
      if (index >= 0 && editingExtractorsList.value[index]) {
        const currentValue = editingExtractorsList.value[index].json_path || ''
        editingExtractorsList.value[index].json_path = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'extractor_header_name':
      if (index >= 0 && editingExtractorsList.value[index]) {
        const currentValue = editingExtractorsList.value[index].header_name || ''
        editingExtractorsList.value[index].header_name = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'assertion_contains':
      if (index >= 0 && editingAssertionsList.value[index]) {
        const currentValue = editingAssertionsList.value[index].expected || ''
        editingAssertionsList.value[index].expected = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'assertion_json_path':
      if (index >= 0 && editingAssertionsList.value[index]) {
        const currentValue = editingAssertionsList.value[index].json_path || ''
        editingAssertionsList.value[index].json_path = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'assertion_json_expected':
      if (index >= 0 && editingAssertionsList.value[index]) {
        const currentValue = editingAssertionsList.value[index].expected || ''
        editingAssertionsList.value[index].expected = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'assertion_header_name':
      if (index >= 0 && editingAssertionsList.value[index]) {
        const currentValue = editingAssertionsList.value[index].header_name || ''
        editingAssertionsList.value[index].header_name = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'assertion_header_expected':
      if (index >= 0 && editingAssertionsList.value[index]) {
        const currentValue = editingAssertionsList.value[index].expected_value || ''
        editingAssertionsList.value[index].expected_value = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
    case 'assertion_equals':
      if (index >= 0 && editingAssertionsList.value[index]) {
        const currentValue = editingAssertionsList.value[index].expected || ''
        editingAssertionsList.value[index].expected = currentValue.substring(0, start) + variable + currentValue.substring(end)
      }
      break
  }

  closeVariablePicker()
}

// 复制变量到剪贴板
const copyVariableToClipboard = () => {
  navigator.clipboard.writeText(variablePreview.value).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 编辑接口请求表单
const editFormRef = ref(null)
const editForm = ref({
  name: '',
  description: '',
  environment: null
})

const editRules = {
  name: [{ required: true, message: t('apiTesting.automation.inputSuiteName'), trigger: 'blur' }]
}

// 树形选择
const requestTreeRef = ref(null)

// 表格引用
const requestTableRef = ref(null)
let sortableInstance = null
const requestTreeProps = {
  children: 'children',
  label: 'name'
}

// 方法
const getMethodType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'info',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return types[method?.toUpperCase()] || 'info'
}

const getStatusType = (status) => {
  const types = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'PENDING': t('apiTesting.automation.status.pending'),
    'RUNNING': t('apiTesting.automation.status.running'),
    'COMPLETED': t('apiTesting.automation.status.completed'),
    'FAILED': t('apiTesting.automation.status.failed')
  }
  return texts[status] || status
}

const getPassRate = (execution) => {
  if (!execution || execution.total_requests === 0) return 0
  return Math.round((execution.passed_requests / execution.total_requests) * 100)
}

const getAverageExecutionTime = (execution) => {
  if (!execution || execution.total_requests === 0) return '0ms'
  // 使用 start_time 和 end_time 计算总耗时
  const startTime = new Date(execution.start_time).getTime()
  const endTime = new Date(execution.end_time).getTime()
  const totalTime = endTime - startTime
  const avg = totalTime / execution.total_requests
  return `${avg.toFixed(0)}ms`
}

const getEnvironmentName = (environment) => {
  if (!environment) return t('apiTesting.automation.noEnvironment')
  if (typeof environment === 'object' && environment.name) {
    return environment.name
  }
  const env = environments.value.find(e => e.id === environment)
  return env ? env.name : t('apiTesting.automation.noEnvironment')
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const getReviewStatusType = (status) => {
  switch (status) {
    case 'approved':
      return 'success'
    case 'rejected':
      return 'danger'
    case 'partial':
      return 'warning'
    default:
      return 'info'
  }
}

const getReviewStatusText = (status) => {
  switch (status) {
    case 'approved':
      return '已通过'
    case 'rejected':
      return '不通过'
    case 'partial':
      return '部分通过'
    default:
      return '待评审'
  }
}

const loadReviewData = async () => {
  const suiteId = suite.value?.id
  if (!suiteId) return

  reviewLoading.value = true
  try {
    const summaryResponse = await api.get(`/api-testing/test-suites/${suiteId}/review_summary/`)
    reviewSummary.value = summaryResponse.data
    reviewRecords.value = summaryResponse.data.records || []
  } catch (error) {
    console.error('加载评审数据失败:', error)
  } finally {
    reviewLoading.value = false
  }
}

const submitReview = async (status) => {
  const suiteId = suite.value?.id
  if (!suiteId) return

  try {
    await api.post(`/api-testing/test-suites/${suiteId}/review/`, {
      status: status,
      comment: status === 'rejected' ? rejectComment.value : ''
    })
    ElMessage.success(status === 'approved' ? '已通过评审' : '已拒绝')
    showRejectDialog.value = false
    rejectComment.value = ''
    await loadReviewData()
  } catch (error) {
    ElMessage.error('提交评审失败')
  }
}

const editReview = async (record) => {
  const suiteId = suite.value?.id
  if (!suiteId) return

  try {
    // 简单的方式：先问用户要修改成什么
    await ElMessageBox.confirm(
      '请选择新的评审结果',
      '修改评审',
      {
        confirmButtonText: '通过',
        cancelButtonText: '拒绝',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    )
    // 用户点击"通过"
    await api.post(`/api-testing/test-suites/${suiteId}/review/`, {
      status: 'approved',
      comment: ''
    })
    ElMessage.success('已修改为通过')
    await loadReviewData()
  } catch (action) {
    // distinguishCancelAndClose: true 时，点击取消按钮会 reject 并返回 'cancel'
    if (action === 'cancel') {
      // 用户点击"拒绝"，弹出拒绝原因对话框
      rejectComment.value = record.comment || ''
      showRejectDialog.value = true
    }
    // 点击关闭按钮或按 ESC 时不执行任何操作
  }
}

const resetReviews = async () => {
  const suiteId = suite.value?.id
  if (!suiteId) return

  try {
    await ElMessageBox.confirm(
      '确定要重置评审状态吗？这将清除所有评审记录，需要所有人重新评审。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.post(`/api-testing/test-suites/${suiteId}/reset_reviews/`)
    ElMessage.success('评审状态已重置')
    await loadReviewData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置评审失败')
    }
  }
}

const formatExecutionResults = (results) => {
  if (!results || !Array.isArray(results)) return []
  return results
}

const formatJson = (data) => {
  if (!data) return ''
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

const getRequestData = () => {
  if (!currentRequestDetail.value?.request_data) return ''
  const data = currentRequestDetail.value.request_data
  switch (activeRequestTab.value) {
    case 'body':
      return formatJson(data.body)
    case 'headers':
      return formatJson(data.headers)
    case 'params':
      return formatJson(data.params)
    default:
      return ''
  }
}

// 获取请求数据（原始格式，用于 JSON 树形展示）
const getRequestDataRaw = () => {
  if (!currentRequestDetail.value?.request_data) return ''
  const data = currentRequestDetail.value.request_data
  switch (activeRequestTab.value) {
    case 'body':
      return data.body || ''
    case 'headers':
      return data.headers || {}
    case 'params':
      return data.params || {}
    default:
      return ''
  }
}

// 获取请求 JSONPath 根路径（用于跨步骤引用）
const getRequestJsonPathRoot = () => {
  // 获取当前接口的别名或序号
  if (!currentRequestDetail.value) return '$.request.body'

  // 尝试从 suite_requests 中找到当前接口的别名
  const flatRequests = getAllRequestsFlat(suite.value?.suite_requests || [])
  const currentRequest = flatRequests.find(r => r.id === currentRequestDetail.value.request_id)
  const requestRef = currentRequest?.alias || currentRequest?.displayOrder || 'current'

  switch (activeRequestTab.value) {
    case 'body':
      return `$.${requestRef}.request.body`
    case 'headers':
      return `$.${requestRef}.request.headers`
    case 'params':
      return `$.${requestRef}.request.params`
    default:
      return `$.${requestRef}.request.body`
  }
}

const getResponseData = () => {
  if (!currentRequestDetail.value?.response_data) return ''
  const data = currentRequestDetail.value.response_data
  switch (activeResponseTab.value) {
    case 'body':
      return data.body || ''
    case 'headers':
      return formatJson(data.headers)
    case 'json':
      return formatJson(data.json)
    default:
      return ''
  }
}

// 获取响应数据（原始格式，用于 JSON 树形展示）
const getResponseDataRaw = () => {
  if (!currentRequestDetail.value?.response_data) return ''
  const data = currentRequestDetail.value.response_data
  switch (activeResponseTab.value) {
    case 'body':
      return data.body || ''
    case 'headers':
      return data.headers || {}
    case 'json':
      return data.json || {}
    default:
      return ''
  }
}

// 获取 JSONPath 根路径（用于跨步骤引用）
const getJsonPathRoot = () => {
  // 获取当前接口的别名或序号
  if (!currentRequestDetail.value) return '$.response.body'
  
  // 尝试从 suite_requests 中找到当前接口的别名
  const flatRequests = getAllRequestsFlat(suite.value?.suite_requests || [])
  const currentRequest = flatRequests.find(r => r.id === currentRequestDetail.value.request_id)
  const requestRef = currentRequest?.alias || currentRequest?.displayOrder || 'current'
  
  switch (activeResponseTab.value) {
    case 'body':
      return `$.${requestRef}.response.body`
    case 'headers':
      return `$.${requestRef}.response.headers`
    case 'json':
      return `$.${requestRef}.response.json`
    default:
      return `$.${requestRef}.response.body`
  }
}

const goBack = () => {
  router.push('/api-testing/automation')
}

const loadSuiteDetail = async () => {
  const suiteId = route.params.id
  if (!suiteId) return

  loading.value = true
  try {
    const response = await api.get(`/api-testing/test-suites/${suiteId}/`)
    suite.value = response.data
    // 更新路由 query，添加测试套件名称，用于面包屑显示
    if (suite.value.name) {
      router.replace({
        query: { ...route.query, name: suite.value.name }
      })
    }
    await Promise.all([
      loadExecutions(),
      loadEnvironments(),
      loadReviewData()
    ])
    // 数据加载完成后初始化拖拽
    nextTick(() => {
      initSortable()
    })
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadSuiteDetail'))
  } finally {
    loading.value = false
  }
}

const loadEnvironments = async () => {
  try {
    const response = await api.get('/api-testing/environments/')
    const allEnvironments = response.data.results || response.data
    environments.value = allEnvironments.filter(env =>
      env.scope === 'GLOBAL' ||
      (env.scope === 'LOCAL' && (!suite.value?.project || env.project === suite.value.project))
    )
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadEnvironments'))
  }
}

const loadExecutions = async () => {
  if (!suite.value) return
  
  executionsLoading.value = true
  try {
    const response = await api.get('/api-testing/test-executions/', {
      params: { test_suite: suite.value.id }
    })
    executions.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadExecutionHistory'))
  } finally {
    executionsLoading.value = false
  }
}

const loadRequestTree = async () => {
  if (!suite.value?.project) return

  try {
    const collectionsRes = await api.get('/api-testing/collections/', {
      params: { project: suite.value.project }
    })
    const collections = collectionsRes.data.results || collectionsRes.data

    const requestsRes = await api.get('/api-testing/requests/')
    const requests = requestsRes.data.results || requestsRes.data

    requestTree.value = buildRequestTree(collections, requests)
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadRequestTree'))
  }
}

const buildRequestTree = (collections, requests) => {
  const map = {}
  const roots = []
  
  collections.forEach(collection => {
    map[collection.id] = {
      ...collection,
      type: 'collection',
      children: []
    }
  })
  
  collections.forEach(collection => {
    if (collection.parent && map[collection.parent]) {
      map[collection.parent].children.push(map[collection.id])
    } else {
      roots.push(map[collection.id])
    }
  })
  
  requests.forEach(request => {
    if (map[request.collection]) {
      map[request.collection].children.push({
        ...request,
        type: 'request',
        id: `request_${request.id}`
      })
    }
  })
  
  return roots
}

const runTestSuite = async () => {
  if (!suite.value) return
  
  running.value = true
  try {
    const response = await api.post(`/api-testing/test-suites/${suite.value.id}/execute/`)
    currentExecution.value = response.data
    showExecutionDialog.value = true
    await loadExecutions()
    ElMessage.success(t('apiTesting.messages.success.suiteExecuted'))
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.executeSuite'))
  } finally {
    running.value = false
  }
}

const editSuite = () => {
  if (!suite.value) return
  
  editForm.value.name = suite.value.name
  editForm.value.description = suite.value.description
  editForm.value.environment = suite.value.environment?.id || null
  showEditDialog.value = true
}

const duplicateSuite = async () => {
  if (!suite.value) return
  
  try {
    const newSuite = {
      name: `${suite.value.name} - ${t('apiTesting.common.copyText')}`,
      description: suite.value.description,
      project: suite.value.project,
      environment_id: suite.value.environment?.id || null
    }
    await api.post('/api-testing/test-suites/', newSuite)
    ElMessage.success(t('apiTesting.messages.success.copy'))
    goBack()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.copyFailed'))
  }
}

const submitEditForm = async () => {
  if (!editFormRef.value || !suite.value) return

  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const submitData = {
      name: editForm.value.name,
      description: editForm.value.description,
      project: suite.value.project,
      environment_id: editForm.value.environment
    }

    await api.put(`/api-testing/test-suites/${suite.value.id}/`, submitData)
    ElMessage.success(t('apiTesting.messages.success.suiteUpdated'))
    showEditDialog.value = false
    await loadSuiteDetail()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.updateFailed'))
  } finally {
    submitting.value = false
  }
}

const resetEditForm = () => {
  editForm.value = {
    name: '',
    description: '',
    environment: null
  }
  editFormRef.value?.resetFields()
}

const showAddRequest = async () => {
  await loadRequestTree()
  showAddRequestDialog.value = true
  
  nextTick(() => {
    setTimeout(() => {
      if (requestTreeRef.value && suite.value) {
        const existingRequestIds = suite.value.suite_requests?.map(sr => 
          `request_${sr.request.id}`
        ) || []
        requestTreeRef.value.setCheckedKeys(existingRequestIds, false)
      }
    }, 200)
  })
}

const onRequestCheck = () => {
  // 请求选择变化处理
}

const addSelectedRequests = async () => {
  if (!suite.value) return
  
  const checkedNodes = requestTreeRef.value.getCheckedNodes()
  const requestIds = checkedNodes
    .filter(node => node.type === 'request')
    .map(node => node.id.replace('request_', ''))

  if (requestIds.length === 0) {
    ElMessage.warning(t('apiTesting.messages.warning.selectAtLeastOneRequest'))
    return
  }

  addingRequests.value = true
  try {
    const response = await api.post(`/api-testing/test-suites/${suite.value.id}/add-requests/`, {
      request_ids: requestIds
    })

    // 直接使用返回的套件数据更新列表
    if (response.data && response.data.suite) {
      suite.value = response.data.suite
      // 重新初始化拖拽
      nextTick(() => {
        initSortable()
      })
    }

    ElMessage.success(response.data.message || t('apiTesting.messages.success.addSuccess'))
    showAddRequestDialog.value = false
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.addFailed'))
  } finally {
    addingRequests.value = false
  }
}

const updateRequestEnabled = async (suiteRequest) => {
  try {
    await api.put(`/api-testing/test-suite-requests/${suiteRequest.id}/`, {
      enabled: suiteRequest.enabled
    })
    // 重新加载套件详情以更新时间戳
    await loadSuiteDetail()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.updateFailed'))
    suiteRequest.enabled = !suiteRequest.enabled
  }
}

// 编辑接口请求
const editRequest = (suiteRequest) => {
  const request = suiteRequest.request || {}
  
  // 合并原始接口参数和覆盖参数（覆盖参数优先）
  const mergedHeaders = { ...(request.headers || {}), ...(suiteRequest.override_headers || {}) }
  const mergedParams = { ...(request.params || {}), ...(suiteRequest.override_params || {}) }
  
  // 确定使用哪个 body：优先使用覆盖的 body，否则使用原始接口的 body
  let mergedBody = suiteRequest.override_body
  if (!mergedBody || Object.keys(mergedBody).length === 0) {
    mergedBody = request.body || {}
  }
  
  // 初始化编辑数据
  editingRequestData.value = {
    id: suiteRequest.id,
    name: suiteRequest.override_name || request.name || '',
    method: suiteRequest.override_method || request.method || 'GET',
    url: suiteRequest.override_url || request.url || '',
    headers: mergedHeaders,
    params: mergedParams,
    body: mergedBody,
    bodyType: 'json',
    bodyContent: ''
  }
  
  // 初始化 body 内容
  const body = editingRequestData.value.body
  if (body && typeof body === 'object') {
    const bodyType = body['type']
    const bodyData = body['data']
    if (bodyType === 'json' || bodyType === 'raw') {
      editingRequestData.value.bodyType = bodyType
      editingRequestData.value.bodyContent = typeof bodyData === 'string' ? bodyData : JSON.stringify(bodyData, null, 2)
    } else {
      editingRequestData.value.bodyType = 'json'
      editingRequestData.value.bodyContent = JSON.stringify(body, null, 2)
    }
  } else if (body) {
    editingRequestData.value.bodyType = 'raw'
    editingRequestData.value.bodyContent = String(body)
  }
  
  // 初始化 headers 列表
  editingHeadersList.value = Object.entries(editingRequestData.value.headers || {}).map(([key, value]) => ({ key, value }))
  if (editingHeadersList.value.length === 0) {
    editingHeadersList.value.push({ key: '', value: '' })
  }
  
  // 初始化 params 列表
  editingParamsList.value = Object.entries(editingRequestData.value.params || {}).map(([key, value]) => ({ key, value }))
  if (editingParamsList.value.length === 0) {
    editingParamsList.value.push({ key: '', value: '' })
  }
  
  // 初始化提取变量列表 - 优先使用 suite_request 的 extracted_variables，否则使用 request 的 variable_extractors
  let extractors = suiteRequest.extracted_variables
  // 如果为空对象或空数组，则使用 request 的 variable_extractors
  if (!extractors || (Array.isArray(extractors) && extractors.length === 0) || (typeof extractors === 'object' && Object.keys(extractors).length === 0)) {
    extractors = request.variable_extractors
  }
  // 确保是数组类型
  if (!Array.isArray(extractors)) {
    extractors = []
  }
  editingExtractorsList.value = extractors.map(extractor => ({ ...extractor }))
  
  // 初始化断言列表 - 优先使用 suite_request 的 assertions，否则使用 request 的 assertions
  let assertions = suiteRequest.assertions
  // 如果为空数组，则使用 request 的 assertions
  if (!assertions || (Array.isArray(assertions) && assertions.length === 0)) {
    assertions = request.assertions
  }
  // 确保是数组类型
  if (!Array.isArray(assertions)) {
    assertions = []
  }
  editingAssertionsList.value = assertions.map(assertion => ({ ...assertion }))
  
  const method = suiteRequest.override_method || request.method || 'GET'
  editDrawerActiveTab.value = ['POST', 'PUT', 'PATCH'].includes(method) ? 'body' : 'basic'
  
  showEditRequestDialog.value = true
}

// Headers 操作
const addEditingHeader = () => editingHeadersList.value.push({ key: '', value: '' })
const removeEditingHeader = (index) => {
  editingHeadersList.value.splice(index, 1)
  if (editingHeadersList.value.length === 0) {
    editingHeadersList.value.push({ key: '', value: '' })
  }
}

// Params 操作
const addEditingParam = () => editingParamsList.value.push({ key: '', value: '' })
const removeEditingParam = (index) => {
  editingParamsList.value.splice(index, 1)
  if (editingParamsList.value.length === 0) {
    editingParamsList.value.push({ key: '', value: '' })
  }
}

// 提取变量操作
const addEditingExtractor = () => {
  editingExtractorsList.value.push({
    name: '',
    source: 'json_body',
    json_path: '',
    header_name: '',
    variable_name: ''
  })
}
const removeEditingExtractor = (index) => {
  editingExtractorsList.value.splice(index, 1)
}

// 断言操作
const addEditingAssertion = () => {
  editingAssertionsList.value.push({
    name: '',
    type: 'status_code',
    expected: 200,
    json_path: '',
    header_name: '',
    expected_value: ''
  })
}
const removeEditingAssertion = (index) => {
  editingAssertionsList.value.splice(index, 1)
}
const onEditingAssertionTypeChange = (assertion) => {
  assertion.expected = null
  assertion.json_path = ''
  assertion.header_name = ''
  assertion.expected_value = ''
  // 设置默认值
  if (assertion.type === 'status_code') {
    assertion.expected = 200
  } else if (assertion.type === 'response_time') {
    assertion.expected = 1000
  }
}

// 获取预期值的占位符
const getExpectedPlaceholder = (assertion) => {
  if (assertion.expected === 'not_null') {
    return '不为空'
  } else if (assertion.expected === 'not_undefined') {
    return '不为undefined'
  } else if (assertion.expected === 'not_empty') {
    return '不为空'
  }
  return assertion.expected_display || '预期值'
}

// 保存接口编辑
const saveRequestEdit = async () => {
  if (!editingRequestData.value.id) return
  
  savingRequestEdit.value = true
  try {
    // 转换 headers
    const headers = {}
    editingHeadersList.value.forEach(item => {
      if (item.key.trim()) headers[item.key.trim()] = item.value
    })
    
    // 转换 params
    const params = {}
    editingParamsList.value.forEach(item => {
      if (item.key.trim()) params[item.key.trim()] = item.value
    })
    
    // 转换 body
    let body = {}
    if (['POST', 'PUT', 'PATCH'].includes(editingRequestData.value.method)) {
      if (editingRequestData.value.bodyType === 'json') {
        try {
          body = { type: 'json', data: JSON.parse(editingRequestData.value.bodyContent) }
        } catch {
          body = { type: 'raw', data: editingRequestData.value.bodyContent }
        }
      } else {
        body = { type: 'raw', data: editingRequestData.value.bodyContent }
      }
    }
    
    // 转换提取变量 - 过滤掉空名称的规则
    const extractors = editingExtractorsList.value.filter(item => item.name.trim()).map(item => ({
      name: item.name.trim(),
      source: item.source,
      json_path: item.json_path,
      header_name: item.header_name,
      variable_name: item.variable_name
    }))
    
    // 转换断言 - 过滤掉空名称的断言
    const assertions = editingAssertionsList.value.filter(item => item.name.trim()).map(item => ({
      name: item.name.trim(),
      type: item.type,
      expected: item.expected,
      json_path: item.json_path,
      header_name: item.header_name,
      expected_value: item.expected_value
    }))
    
    const updateData = {
      override_name: editingRequestData.value.name,
      override_method: editingRequestData.value.method,
      override_url: editingRequestData.value.url,
      override_headers: headers,
      override_params: params,
      override_body: body,
      extracted_variables: extractors,
      assertions: assertions
    }
    
    await updateTestSuiteRequest(editingRequestData.value.id, updateData)
    ElMessage.success('保存成功')
    showEditRequestDialog.value = false
    // 重新加载套件详情
    await loadSuiteDetail()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingRequestEdit.value = false
  }
}

// 拖拽排序相关
const initSortable = () => {
  if (sortableInstance) return

  const tbody = requestTableRef.value?.$el.querySelector('.el-table__body tbody')
  if (!tbody) return

  sortableInstance = new Sortable(tbody, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'dragging',
    onEnd: async (evt) => {
      const { oldIndex, newIndex } = evt
      if (oldIndex === newIndex) return

      const requests = suite.value.suite_requests
      const draggedItem = requests[oldIndex]

      try {
        // 计算新的 order 值
        let newOrder
        if (newIndex === 0) {
          // 移动到第一位
          newOrder = requests[0].order - 1
        } else if (newIndex >= requests.length - 1) {
          // 移动到最后一位
          newOrder = requests[requests.length - 1].order + 1
        } else {
          // 移动到中间位置，取前后两个 order 的平均值
          const prevOrder = requests[newIndex - 1].order
          const nextOrder = requests[newIndex].order
          newOrder = (prevOrder + nextOrder) / 2
        }

        // 更新后端
        await api.patch(`/api-testing/test-suite-requests/${draggedItem.id}/`, {
          order: newOrder
        })

        // 前端重新排序
        requests.splice(oldIndex, 1)
        requests.splice(newIndex, 0, draggedItem)

        ElMessage.success(t('apiTesting.messages.success.orderUpdated'))
      } catch (error) {
        console.error('拖拽排序失败:', error)
        ElMessage.error(t('apiTesting.messages.error.orderUpdateFailed'))
        // 恢复原顺序
        await loadSuiteDetail()
      }
    }
  })
}

const removeRequest = async (suiteRequest) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.automation.confirmRemoveRequest'),
      t('apiTesting.automation.confirmRemove'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    await api.delete(`/api-testing/test-suite-requests/${suiteRequest.id}/`)
    ElMessage.success(t('apiTesting.messages.success.removeSuccess'))
    await loadSuiteDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.removeFailed'))
    }
  }
}

const viewExecutionDetail = (execution) => {
  currentExecution.value = execution
  showExecutionDialog.value = true
}

const viewRequestDetail = (requestResult) => {
  currentRequestDetail.value = requestResult
  showRequestDetailDialog.value = true
}

onMounted(async () => {
  // 获取当前用户信息
  try {
    const response = await api.get('/users/me/')
    currentUser.value = response.data
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
  loadSuiteDetail()
})
</script>

<style scoped lang="scss">
.automation-suite-detail {
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
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  padding: 20px 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #5a32a3;
}

.header-actions {
  display: flex;
  gap: 10px;

  .el-button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

    .el-icon {
      margin-right: 6px;
    }

    &.el-button--primary {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
      border: none !important;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
      }
    }

    &.el-button--success {
      background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;
      border: none !important;
      box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);

      &:hover {
        background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(82, 196, 26, 0.4);
      }
    }

    &.el-button--danger {
      background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%) !important;
      border: none !important;
      box-shadow: 0 4px 12px rgba(245, 34, 45, 0.3);

      &:hover {
        background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(245, 34, 45, 0.4);
      }
    }
  }
}

// 顶部评审状态徽章样式
.review-status-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-left: 10px;

  &.approved {
    background: rgba(82, 196, 26, 0.1);
    color: #52c41a;
  }

  &.rejected {
    background: rgba(245, 34, 45, 0.06);
    color: #ff4d4f;
  }

  &.pending {
    background: rgba(250, 140, 22, 0.1);
    color: #fa8c16;
  }
}

.content {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.suite-info-section {
  .info-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 24px;
  }

  .info-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    border-radius: 8px;
    transition: all 0.3s ease;

    background: #ffffff;
    border: 1px solid rgba(147, 112, 219, 0.15);
    border-left: 4px solid #7b42f6;

    &:nth-child(1) .info-label {
      color: #7b42f6;
    }

    &:nth-child(2) .info-label {
      color: #9370db;
    }

    &:nth-child(3) .info-label {
      color: #a888e0;
    }

    &:nth-child(4) .info-label {
      color: #b8a0e5;
    }

    &:nth-child(5) .info-label {
      color: #c8b8ea;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }

  .info-label {
    font-size: 13px;
    color: #8c8c8c;
    font-weight: 400;
  }

  .info-value {
    font-size: 15px;
    color: #333;
    font-weight: 500;
    word-break: break-all;
  }
}

.requests-section,
.executions-section,
.review-section {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.06),
              0 1px 3px rgba(0, 0, 0, 0.04);
  padding: 24px;
  transition: box-shadow 0.3s ease;

  &:hover {
    box-shadow: 0 8px 30px rgba(147, 112, 219, 0.1),
                0 2px 8px rgba(0, 0, 0, 0.04);
  }

  // Section header 优化
  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 8px;

      &::before {
        content: '';
        width: 4px;
        height: 18px;
        background: linear-gradient(180deg, #7b42f6 0%, #5a32a3 100%);
        border-radius: 2px;
      }
    }
  }

  // 树形结构容器
  .requests-tree {
    border: 1px solid #f0f0f0;
    border-radius: 12px;
    overflow: hidden;
    background: #fafafa;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.02);
  }

  // 空状态样式
  .requests-empty {
    padding: 60px 20px;
    background: #fafafa;
    border-radius: 12px;
    border: 2px dashed #e0e0e0;

    :deep(.el-empty__description) {
      color: #8c8c8c;
      font-size: 14px;
      margin-top: 16px;
    }

    :deep(.el-empty__image) {
      opacity: 0.6;
    }
  }

  // 操作按钮容器
  .operation-btns,
  .review-actions {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
  }

  // 操作按钮样式 - 与列表页保持一致
  .action-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 12px !important;
    border-radius: 6px;
    transition: all 0.3s ease;
    border: none !important;
    color: #ffffff !important;
    height: 28px;
    line-height: 1;

    // 编辑断言按钮 - 紫色
    &.edit-assertion-btn {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
      }
    }

    // 移除按钮 - 红色
    &.remove-btn {
      background: linear-gradient(135deg, #ff4d4f 0%, #f5222d 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(245, 34, 45, 0.4);
      }
    }

    // 通过按钮 - 绿色
    &.approve-btn {
      background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
      }
    }

    // 拒绝按钮 - 红色
    &.reject-btn {
      background: linear-gradient(135deg, #ff4d4f 0%, #f5222d 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(245, 34, 45, 0.4);
      }
    }

    // 修改评审按钮 - 紫色
    &.edit-review-btn {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
      }
    }

    // 重新发起评审按钮 - 蓝色
    &.reset-btn {
      background: linear-gradient(135deg, #409eff 0%, #1890ff 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #69b1ff 0%, #40a9ff 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
      }
    }

    // 查看详情按钮 - 紫色
    &.view-detail-btn {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
      }
    }
  }
}

.review-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      h4 {
        margin: 0;
        color: #5a32a3;
        font-size: 16px;
        font-weight: 600;
      }
    }

    .reset-review-btn {
      color: #e6a23c;

      &:hover {
        color: #cf9236;
        background: rgba(230, 162, 60, 0.1);
      }
    }
  }

  .review-status {
    display: flex;
    align-items: center;
    gap: 8px;

    .review-count {
      font-size: 13px;
      color: #666;
    }
  }

  .pending-text {
    color: #909399;
    font-size: 13px;
  }

  .reviewed-text {
    color: #67c23a;
    font-size: 13px;
  }

}

// 拖拽手柄样式
.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: grab;
  user-select: none;

  .drag-icon {
    font-size: 14px;
    color: #909399;
    transition: color 0.2s;
  }

  &:hover .drag-icon {
    color: #7b42f6;
  }

  span {
    font-size: 13px;
    color: #606266;
  }
}

.dragging {
  opacity: 0.7;
  background: #f5f3ff !important;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h4 {
    margin: 0;
    color: #5a32a3;
    font-size: 16px;
    font-weight: 600;
  }

  .el-button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.25s ease;

    &.el-button--primary {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
      border: none !important;

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
      }
    }
  }
}

// 表格样式
:deep(.el-table) {
  border: none;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: none;
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

  .el-table__header-wrapper {
    background-color: #ffffff !important;
  }

  .el-table__header {
    background-color: #ffffff !important;

    th {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600;
      font-size: 14px;
      border-bottom: 1px solid #e9ecef;
      padding: 16px !important;
      vertical-align: middle !important;

      .cell {
        color: #5a32a3 !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-align: center !important;
      }
    }
  }

  // 序号列特殊样式 - 确保表头和内容都居中对齐
  th.el-table__cell:first-child,
  td.el-table__cell:first-child {
    text-align: center !important;

    .cell {
      text-align: center !important;
      justify-content: center !important;
      padding-left: 0 !important;
      padding-right: 0 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
    }
  }

  // 序号列内容显示 - 使用更高的优先级
  :deep(.el-table__body) td.el-table__cell:first-child .cell {
    color: #333 !important;
    font-size: 14px !important;
    font-weight: normal !important;
  }

  // 序号列表头 - 使用更高的优先级
  :deep(.el-table__header) th.el-table__cell:first-child .cell {
    color: #5a32a3 !important;
    font-weight: 600 !important;
  }



  .el-table__row {
    transition: all 0.3s ease;
    background-color: #ffffff !important;

    &:hover {
      background-color: #f8f7ff !important;
    }

    &.el-table__row--striped {
      background-color: #fafaff !important;
    }
  }

  td {
    padding: 14px 16px;
    border-bottom: 1px solid #e9ecef;
    color: #333;
    font-size: 14px;
    font-weight: 400;
    vertical-align: middle !important;

    .cell {
      overflow: visible !important;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 40px;
    }
  }

  .el-table__empty-block {
    background: #ffffff !important;
  }

  // 方法标签样式 - 确保显示完整
  .method-tag {
    white-space: nowrap;
    overflow: visible;
  }

  // 方法徽章样式 - 参考 ProjectManagement.vue
  .method-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    white-space: nowrap;
    overflow: visible;
    line-height: 1.5;
    height: 24px;

    &.get {
      background: #f6ffed;
      color: #52c41a;
    }

    &.post {
      background: #f5f3ff;
      color: #7b42f6;
    }

    &.put {
      background: #fff7e6;
      color: #fa8c16;
    }

    &.delete {
      background: #fff1f0;
      color: #f5222d;
    }

    &.patch {
      background: #f5f5f5;
      color: #8c8c8c;
    }
  }

  // 状态徽章样式 - 用于评审状态和执行状态
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
    vertical-align: middle;

    // 评审状态
    &.approved {
      background: #f6ffed;
      color: #52c41a;
    }

    &.rejected {
      background: #fff2f0;
      color: #f5222d;
    }

    &.pending {
      background: #fff7e6;
      color: #fa8c16;
    }

    // 执行状态（小写）
    &.success,
    &.completed {
      background: #f6ffed;
      color: #52c41a;
    }

    &.failed {
      background: #fff2f0;
      color: #f5222d;
    }

    &.running,
    &.processing {
      background: #e6f4ff;
      color: #409eff;
    }

    // 执行状态（大写 - 执行历史用）
    &.completed {
      background: #f6ffed;
      color: #52c41a;
    }

    &.failed {
      background: #fff2f0;
      color: #f5222d;
    }

    &.running {
      background: #e6f4ff;
      color: #409eff;
    }

    &.pending {
      background: #fff7e6;
      color: #fa8c16;
    }
  }
}

.add-request-content {
  max-height: 400px;
  overflow-y: auto;
}

.request-tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 4px 0;

  .el-icon {
    color: #7b42f6;
  }
}

.method-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-weight: bold;
  margin-left: auto;

  &.get { background: linear-gradient(135deg, #67c23a 0%, #52c41a 100%); }
  &.post { background: linear-gradient(135deg, #409eff 0%, #7b42f6 100%); }
  &.put { background: linear-gradient(135deg, #e6a23c 0%, #fa8c16 100%); }
  &.delete { background: linear-gradient(135deg, #f56c6c 0%, #f5222d 100%); }
  &.patch { background: linear-gradient(135deg, #909399 0%, #595959 100%); }
}

.execution-detail {
  max-height: 70vh;
  overflow-y: auto;
}

/* 执行结果抽屉样式 - 参考 AutomationSuiteList.vue */
.execution-detail-drawer {
  padding: 0;

  /* 统计概览卡片 */
  .summary-cards {
    margin-bottom: 20px;

    .summary-card {
      display: flex;
      align-items: center;
      padding: 16px 20px;
      background: #ffffff;
      border: 1px solid rgba(147, 112, 219, 0.12);
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(147, 112, 219, 0.12);
      }

      .card-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 10px;
        margin-right: 16px;
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);

        .el-icon {
          font-size: 24px;
          color: #7b42f6;
        }

        &.total {
          background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
          .el-icon { color: #7b42f6; }
        }
      }

      .card-content {
        flex: 1;

        .card-label {
          color: #8c8c8c;
          font-size: 13px;
          margin-bottom: 4px;
        }

        .card-value {
          color: #1f2937;
          font-size: 24px;
          font-weight: 600;
        }
      }

      &.success {
        .card-icon {
          background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
          .el-icon { color: #52c41a; }
        }
        .card-value { color: #52c41a; }
      }

      &.failed {
        .card-icon {
          background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
          .el-icon { color: #f5222d; }
        }
        .card-value { color: #f5222d; }
      }

      &.primary {
        .card-icon {
          background: linear-gradient(135deg, #f9f0ff 0%, #efdbff 100%);
          .el-icon { color: #722ed1; }
        }
        .card-value { color: #722ed1; }
      }
    }
  }

  /* 结果表格区域 */
  .result-table-section {
    background: #ffffff;
    border: 1px solid rgba(147, 112, 219, 0.12);
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
    overflow: hidden;

    .section-header {
      padding: 16px 20px;
      background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
      border-bottom: 1px solid rgba(147, 112, 219, 0.12);

      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
        color: #5a32a3;
        font-size: 15px;
        font-weight: 600;

        .el-icon {
          font-size: 18px;
          color: #7b42f6;
        }
      }
    }

    .table-wrapper {
      padding: 16px;
    }
  }
}

/* 执行结果旧样式兼容 */
.execution-summary {
  margin-bottom: 30px;
  padding: 24px;
  background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;

  :deep(.el-statistic) {
    .el-statistic__head {
      color: #5a32a3;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .el-statistic__number {
      color: #7b42f6;
      font-weight: 600;
      font-size: 24px;
    }
  }
}

.execution-results h4 {
  margin: 0 0 15px 0;
  color: #5a32a3;
  font-weight: 600;
}

/* 请求详情对话框样式 */
.request-detail-dialog {
  max-height: 70vh;
  overflow-y: auto;
}

/* 请求详情抽屉样式 - 现代简洁设计 */
.request-detail-drawer {
  padding: 24px;
  min-height: 100%;

  /* 顶部状态栏 - 无边框设计 */
  .request-header {
    padding: 0 0 20px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);

    .request-title-row {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      flex-wrap: wrap;

      .request-name {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a2e;
      }

      .method-tag {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;

        &.get {
          background: #e6f7ff;
          color: #1890ff;
        }

        &.post {
          background: #f6ffed;
          color: #52c41a;
        }

        &.put {
          background: #fff7e6;
          color: #fa8c16;
        }

        &.delete {
          background: #fff1f0;
          color: #f5222d;
        }

        &.patch {
          background: #e6fffb;
          color: #13c2c2;
        }
      }

      .status-tag {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;

        &.success {
          background: #f6ffed;
          color: #52c41a;
        }

        &.failed {
          background: #fff1f0;
          color: #f5222d;
        }
      }

      .meta-tag {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;

        &.time-tag {
          background: #f0f5ff;
          color: #2f54eb;
        }

        &.code-tag {
          background: #f6ffed;
          color: #389e0d;
        }
      }
    }

    .request-url {
      font-size: 13px;
      color: #666;
      font-family: 'Courier New', Consolas, Monaco, monospace;
      word-break: break-all;
      padding: 8px 0;
    }
  }

  /* 错误横幅 - 简洁设计 */
  .error-banner {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #ffccc7;

    .el-icon {
      font-size: 16px;
      color: #f5222d;
      margin-top: 2px;
      flex-shrink: 0;
    }

    span {
      font-size: 13px;
      color: #cf1322;
      line-height: 1.5;
      word-break: break-all;
      white-space: pre-wrap;
      overflow-wrap: break-word;
    }
  }

  /* 数据区域 - 现代卡片式设计 */
  .data-section {
    margin-bottom: 24px;

    /* 主标签 - 简洁文字切换 */
    .main-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;

      .main-tab-btn {
        display: flex;
        align-items: center;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        background: transparent;
        color: #666;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
          color: #333;
          background: #f5f5f5;
        }

        &.active {
          background: #7b42f6;
          color: #fff;
        }
      }
    }

    /* 数据面板 - 无边框直接展示 */
    .data-panel {
      .panel-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;

        .sub-tabs {
          display: flex;
          gap: 4px;

          .sub-tab-btn {
            padding: 6px 14px;
            border: none;
            border-radius: 6px;
            background: transparent;
            color: #666;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;

            &:hover {
              color: #333;
              background: #f0f0f0;
            }

            &.active {
              background: #f0e6ff;
              color: #7b42f6;
            }
          }
        }

        .data-badge {
          display: none;
        }
      }

      .code-container {
        background: transparent !important;
        border: none !important;

        .json-path-hint {
          margin-bottom: 12px;

          .el-alert {
            padding: 8px 12px;

            .el-alert__title {
              font-size: 12px;
            }
          }
        }

        .code-block {
          margin: 0;
          padding: 0;
          font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', Consolas, Monaco, monospace;
          font-size: 13px;
          line-height: 1.7;
          color: #333;
          white-space: pre-wrap;
          word-wrap: break-word;
          background: transparent !important;
          border: none !important;
        }
      }
    }
  }

  /* 断言容器 - 在响应 Tab 内 */
  .assertions-container {
    .assertion-list {
      padding: 8px 0;

      .assertion-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 13px;

        &:last-child {
          border-bottom: none;
          margin-bottom: 0;
        }

        .el-icon {
          font-size: 16px;
          flex-shrink: 0;
        }

        .assertion-name {
          flex-shrink: 0;
          color: #333;
          max-width: 150px;
          word-break: break-all;
        }

        .assertion-detail {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          flex-wrap: wrap;

          .detail-item {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 8px;
            border-radius: 4px;
            background: #f5f5f5;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;

            .label {
              color: #999;
              font-size: 11px;
            }

            .value {
              color: #333;
              font-weight: 500;

              &.null {
                color: #999;
                font-style: italic;
              }

              &.object {
                color: #1890ff;
              }
            }

            &.expected {
              background: #e6f7ff;
              .label { color: #1890ff; }
            }

            &.actual {
              background: #f6ffed;
              .label { color: #52c41a; }

              &.mismatch {
                background: #fff2f0;
                .label { color: #f5222d; }
                .value { color: #f5222d; }
              }
            }
          }

          .separator {
            color: #d9d9d9;
            font-size: 11px;
          }
        }

        .assertion-error {
          color: #f5222d;
          font-size: 12px;
          flex: 1;
          word-break: break-all;
          white-space: pre-wrap;
          overflow-wrap: break-word;
          line-height: 1.4;
        }

        &.passed {
          .el-icon {
            color: #52c41a;
          }
        }

        &.failed {
          .el-icon {
            color: #f5222d;
          }
        }
      }
    }
  }

  /* 变量区域 - 简洁列表设计 */
  .variables-section {
    .section-title-compact {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: #5a32a3;
      border-bottom: 1px solid rgba(147, 112, 219, 0.1);

      .el-icon {
        font-size: 16px;
        color: #7b42f6;
      }
    }

    .variables-grid {
      padding: 12px 0;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 12px;

      .variable-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;

        .var-key {
          font-size: 12px;
          color: #7b42f6;
          font-weight: 500;
        }

        .var-value {
          font-size: 13px;
          color: #333;
          word-break: break-all;
          font-family: 'Courier New', Consolas, Monaco, monospace;
        }
      }
    }
  }
}

.detail-section {
  margin-bottom: 20px;

  h4 {
    margin: 0 0 10px 0;
    color: #5a32a3;
    font-size: 14px;
    font-weight: 600;
    border-left: 3px solid #7b42f6;
    padding-left: 10px;
  }
}

.code-block {
  background: #f8f7ff;
  border: 1px solid rgba(147, 112, 219, 0.15);
  border-radius: 8px;
  padding: 12px;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #4a4a4a;
}

// 对话框样式
:deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(147, 112, 219, 0.2);

  .el-dialog__header {
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
    margin: 0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: #5a32a3;
    }
  }

  .el-dialog__body {
    padding: 24px;

    .el-form {
      .el-form-item {
        margin-bottom: 20px;

        .el-form-item__label {
          color: #5a32a3;
          font-weight: 500;
        }

        .el-input__wrapper,
        .el-select .el-input__wrapper {
          box-shadow: none;
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);
          background-color: transparent;

          &:hover,
          &.is-focus {
            border-color: #7b42f6;
          }
        }

        .el-textarea__inner {
          box-shadow: none;
          border-radius: 8px;
          border: 1px solid rgba(147, 112, 219, 0.2);
          background-color: transparent;
          padding: 8px 12px;
          line-height: 1.5;

          &:hover,
          &:focus {
            border-color: #7b42f6;
          }
        }
      }
    }
  }

  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid #ebeef5;
    background: #fafafa;

    .el-button {
      font-weight: 500;
      padding: 8px 20px;
      border-radius: 8px;

      &.el-button--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;

        &:hover {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
        }
      }
    }
  }
}

// 状态徽章样式 - 参考 AutomationSuiteList.vue
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;

  &.success {
    background: #f6ffed;
    color: #52c41a;
  }

  &.failed {
    background: #fff2f0;
    color: #f5222d;
  }

  &.pending {
    background: #f5f5f5;
    color: #8c8c8c;
  }

  &.processing {
    background: #fff7e6;
    color: #fa8c16;
  }
}

// 自定义表格样式 - 参考 AutomationSuiteList.vue
.custom-table {
  border: none;
  border-radius: 8px;
  overflow: hidden;
  background-color: transparent !important;

  --el-color-primary: #7b42f6;
  --el-border-color: #e9ecef;
  --el-border-color-light: #e9ecef;
  --el-fill-color-light: #f8f7ff;
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;

  &::before {
    display: none;
  }

  :deep(th) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600;
    font-size: 13px;
    border-bottom: 1px solid #e9ecef;
    padding: 0 !important;
    height: 48px !important;
    text-align: center;
    vertical-align: middle !important;

    .cell {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      line-height: 1.4;
      white-space: normal;
      word-break: break-word;
    }
  }

  :deep(.el-table__row) {
    transition: all 0.3s ease;
    background-color: #ffffff !important;

    &:hover {
      background-color: #f8f7ff !important;
    }
  }

  :deep(td) {
    padding: 0 12px !important;
    border-bottom: 1px solid #e9ecef;
    color: #333;
    font-size: 13px;
    vertical-align: middle !important;
    height: 48px;

    .cell {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }
  }

  :deep(.el-table__empty-block) {
    padding: 40px 0;
  }
}

// 数据标签页样式
.data-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 0;
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
    border-bottom: 1px solid rgba(147, 112, 219, 0.12);
  }

  :deep(.el-tabs__item) {
    color: #595959;
    font-weight: 500;

    &.is-active {
      color: #7b42f6;
      background: #ffffff;
    }
  }

  :deep(.el-tabs__active-bar) {
    background-color: #7b42f6;
  }

  :deep(.el-tabs__content) {
    padding: 16px;
    background: #fafbfc;
  }
}

// 抽屉样式
:deep(.el-drawer) {
  .el-drawer__header {
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
    margin: 0;

    .el-drawer__title {
      font-size: 18px;
      font-weight: 600;
      color: #5a32a3;
    }

    .el-drawer__close-btn {
      color: #7b42f6;
      font-size: 18px;

      &:hover {
        color: #5a32a3;
      }
    }
  }

  .el-drawer__body {
    padding: 20px;
    background: #fafbfc;
    height: 100%;
    overflow-y: auto;
  }
}

// 详情抽屉特定样式
:deep(.detail-drawer) {
  .el-drawer__body {
    padding: 0;
    height: calc(100vh - 60px);
    overflow-y: auto;
  }
}

// 树形组件样式
:deep(.el-tree) {
  background: transparent;

  .el-tree-node__content {
    border-radius: 6px;
    margin: 2px 0;

    &:hover {
      background-color: #f8f7ff;
    }
  }

  .el-tree-node.is-current {
    > .el-tree-node__content {
      background-color: #f5f3ff;
      color: #7b42f6;
    }
  }
}

// Tab样式
:deep(.el-tabs) {
  .el-tabs__header {
    margin-bottom: 15px;
  }

  .el-tabs__item {
    color: #595959;
    font-weight: 500;

    &.is-active {
      color: #7b42f6;
    }
  }

  .el-tabs__active-bar {
    background-color: #7b42f6;
  }

  &.el-tabs--border-card {
    border: 1px solid rgba(147, 112, 219, 0.15);
    border-radius: 8px;

    .el-tabs__header {
      background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
      border-bottom: 1px solid rgba(147, 112, 219, 0.15);

      .el-tabs__item {
        &.is-active {
          background-color: #ffffff;
          border-bottom-color: #ffffff;
        }
      }
    }
  }
}

// Alert样式
:deep(.el-alert) {
  border-radius: 8px;

  &.el-alert--error {
    background: #fff1f0;
    border: 1px solid rgba(245, 34, 45, 0.2);
  }
}

// 断言编辑器样式
.assertions-editor {
  .assertions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .request-name {
      font-size: 14px;
      font-weight: 600;
      color: #5a32a3;
    }

    .el-button--primary {
      --el-button-bg-color: #7c3aed;
      --el-button-border-color: #7c3aed;
      --el-button-hover-bg-color: #6d28d9;
      --el-button-hover-border-color: #6d28d9;
    }
  }

  .assertions-table {
    border: 1px solid rgba(147, 112, 219, 0.15);
    border-radius: 8px;
    overflow: hidden;
  }

  .assertions-table-header {
    display: flex;
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
    padding: 12px 16px;
    font-weight: 600;
    font-size: 13px;
    color: #5a32a3;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);

    .col-name {
      width: 140px;
      padding-right: 12px;
    }

    .col-type {
      width: 140px;
      padding-right: 12px;
    }

    .col-params {
      flex: 1;
      padding-right: 12px;
    }

    .col-action {
      width: 50px;
      text-align: center;
    }
  }

  .assertions-table-body {
    .assertion-row {
      display: flex;
      padding: 12px 16px;
      border-bottom: 1px solid rgba(147, 112, 219, 0.1);
      align-items: center;
      background: #ffffff;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background: #faf8ff;
      }

      .col-name {
        width: 140px;
        padding-right: 12px;
      }

      .col-type {
        width: 140px;
        padding-right: 12px;
      }

      .col-params {
        flex: 1;
        padding-right: 12px;

        .el-input,
        .el-input-number,
        .params-row {
          width: 100%;
        }

        .params-row {
          display: flex;
          gap: 8px;

          .el-input {
            flex: 1;
          }
        }
      }

      .col-action {
        width: 50px;
        text-align: center;
      }

      .el-input,
      .el-select,
      .el-input-number {
        width: 100%;
      }
    }
  }
}

// 响应式适配
@media screen and (max-width: 768px) {
  .automation-suite-detail {
    padding: 16px;
  }

  .header {
    flex-direction: column;
    gap: 16px;
    padding: 16px 20px;

    .header-left {
      width: 100%;
    }

    .header-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .page-title {
    font-size: 18px;
  }

  .suite-info-section,
  .requests-section,
  .executions-section,
  .review-section {
    padding: 16px;
  }

  :deep(.el-descriptions) {
    .el-descriptions__label {
      width: 100px !important;
    }
  }

  .assertions-editor {
    .assertions-table-header,
    .assertion-row {
      .col-name {
        width: 100px;
      }

      .col-type {
        width: 120px;
      }
    }
  }
}

@media screen and (max-width: 480px) {
  .automation-suite-detail {
    padding: 12px;
  }

  .header {
    padding: 14px 16px;
  }

  .page-title {
    font-size: 16px;
  }
}

// 执行环境下拉框白色背景
.env-select {
  :deep(.el-select__wrapper) {
    background-color: #ffffff !important;
  }
}

// 场景描述 textarea 样式与场景名称 input 一致
.suite-textarea {
  :deep(.el-textarea__inner) {
    box-shadow: none !important;
    border-radius: 8px !important;
    border: 1px solid rgba(147, 112, 219, 0.2) !important;
    background-color: transparent !important;
    padding: 8px 12px !important;
    line-height: 1.5 !important;

    &:hover,
    &:focus {
      border-color: #7b42f6 !important;
    }
  }
}

// 接口编辑抽屉样式
.edit-request-drawer {
  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;

    .el-drawer__title {
      font-size: 18px;
      font-weight: 600;
      color: #1a1a2e;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, #7b42f6 0%, #5a32a3 100%);
        border-radius: 2px;
      }
    }

    .el-drawer__close-btn {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      transition: all 0.2s ease;

      &:hover {
        background: #f5f5f5;
        color: #7b42f6;
      }
    }
  }

  :deep(.el-drawer__body) {
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background: #fafafa;
  }

  :deep(.el-drawer__footer) {
    padding: 16px 24px;
    border-top: 1px solid #f0f0f0;
    background: #ffffff;
  }

  .drawer-tabs {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    :deep(.el-tabs__header) {
      margin: 0;
      background: #ffffff;
      border-bottom: 1px solid #f0f0f0;
      padding: 0 24px;

      .el-tabs__nav {
        border: none;
      }

      .el-tabs__item {
        height: 48px;
        line-height: 48px;
        font-size: 14px;
        color: #595959;
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
        padding: 0 20px;
        margin-right: 8px;

        &:hover {
          color: #7b42f6;
        }

        &.is-active {
          color: #7b42f6;
          border-bottom-color: #7b42f6;
          font-weight: 500;
        }
      }

      .el-tabs__active-bar {
        background: #7b42f6;
      }
    }

    :deep(.el-tabs__content) {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
    }

    :deep(.el-tab-pane) {
      height: 100%;
    }
  }

  .drawer-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .el-button {
      border-radius: 8px;
      padding: 10px 24px;
      font-weight: 500;
      transition: all 0.25s ease;

      &.el-button--default {
        border-color: #d9d9d9;
        color: #595959;

        &:hover {
          border-color: #7b42f6;
          color: #7b42f6;
        }
      }

      &.el-button--primary {
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

        &:hover {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
          transform: translateY(-1px);
          box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
        }
      }
    }
  }

  .key-value-editor {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #f0f0f0;

    .editor-header {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f5f5f5;

      .el-button {
        border-radius: 6px;
      }
    }

    .kv-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .kv-item {
      display: flex;
      gap: 12px;
      align-items: center;
      padding: 12px;
      background: #fafafa;
      border-radius: 8px;
      transition: all 0.2s ease;

      &:hover {
        background: #f5f0ff;
      }

      .kv-key {
        width: 200px;
      }

      .kv-value {
        flex: 1;
      }

      .el-button--danger {
        border-radius: 6px;
      }
    }
  }

  .body-editor {
    background: transparent;
    padding: 0;

    .body-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;

      .el-radio-group {
        .el-radio-button__inner {
          border-radius: 6px;
        }
      }
    }

    .body-input-wrapper {
      position: relative;
      background: #ffffff;
      border-radius: 8px;

      :deep(.el-textarea) {
        background: #ffffff;

        .el-textarea__inner {
          border-radius: 8px;
          font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
          font-size: 13px;
          line-height: 1.6;
          background: #ffffff;
          border: none;
          box-shadow: inset 0 0 0 1px #e8e8e8;
          padding: 16px;

          &:focus {
            box-shadow: inset 0 0 0 1px #7b42f6, 0 0 0 2px rgba(123, 66, 246, 0.1);
          }
        }
      }
    }
  }

  .el-form {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #f0f0f0;

    .el-form-item {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .el-form-item__label {
        color: #262626;
        font-weight: 500;
      }

      .el-input__wrapper,
      .el-select .el-input__wrapper {
        border-radius: 8px;
        box-shadow: 0 0 0 1px #e4e7ed inset;

        &:hover,
        &.is-focus {
          box-shadow: 0 0 0 1px #7b42f6 inset;
        }
      }
    }
  }

  // 断言编辑器样式
  .assertions-editor {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #f0f0f0;

    .assertions-header {
      margin-bottom: 16px;
      display: flex;
      gap: 12px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f5f5f5;

      .el-button {
        border-radius: 6px;
      }
    }

    .assertions-table {
      .assertions-table-header {
        display: flex;
        padding: 12px 16px;
        background: #fafafa;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        font-size: 13px;
        color: #595959;
        border-bottom: 1px solid #f0f0f0;
      }

      .assertions-table-body {
        > div {
          display: flex;
          padding: 12px 16px;
          align-items: center;
          border-bottom: 1px solid #f5f5f5;
          background: #ffffff;
          transition: all 0.2s ease;

          &:hover {
            background: #fafafa;
          }

          &:last-child {
            border-bottom: none;
            border-radius: 0 0 8px 8px;
          }

          > div {
            padding-right: 12px;

            &:last-child {
              padding-right: 0;
            }
          }

          .el-input__wrapper,
          .el-select .el-input__wrapper {
            border-radius: 6px;
          }

          .el-button--danger {
            border-radius: 6px;
          }
        }
      }
    }

    .el-empty {
      padding: 40px;
      color: #8c8c8c;

      .el-button {
        margin-top: 16px;
        border-radius: 6px;
      }
    }
  }

  // 提取规则编辑器样式
  .variable-extractors-editor {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #f0f0f0;

    .extractors-header {
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f5f5f5;

      .el-button {
        border-radius: 6px;
      }
    }

    .extractors-table {
      .extractors-table-header {
        display: flex;
        padding: 12px 16px;
        background: #fafafa;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        font-size: 13px;
        color: #595959;
        border-bottom: 1px solid #f0f0f0;
      }

      .extractors-table-body {
        > div {
          display: flex;
          padding: 12px 16px;
          align-items: center;
          border-bottom: 1px solid #f5f5f5;
          background: #ffffff;
          transition: all 0.2s ease;

          &:hover {
            background: #fafafa;
          }

          &:last-child {
            border-bottom: none;
            border-radius: 0 0 8px 8px;
          }

          > div {
            padding-right: 12px;

            &:last-child {
              padding-right: 0;
            }
          }

          .el-input__wrapper,
          .el-select .el-input__wrapper {
            border-radius: 6px;
          }

          .el-button--danger {
            border-radius: 6px;
          }
        }
      }
    }

    .el-empty {
      padding: 40px;
      color: #8c8c8c;

      .el-button {
        margin-top: 16px;
        border-radius: 6px;
      }
    }
  }
}

// 变量选择器样式
.variable-picker-content {
  .picker-section {
    margin-bottom: 20px;

    .section-title {
      font-weight: 600;
      margin-bottom: 10px;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 6px;

      .el-icon {
        color: #909399;
        cursor: help;
      }
    }

    .var-hint {
      margin-top: 8px;
      color: #909399;
      font-size: 12px;
      font-family: monospace;
    }

    .function-params {
      margin-top: 12px;

      .param-hint {
        margin-left: 8px;
        color: #909399;
        font-size: 12px;
      }
    }

    // 前置接口选择样式
    .no-prev-requests {
      margin-top: 16px;
    }

    .var-type-section,
    .json-path-section {
      margin-top: 16px;
    }

    // 执行结果预览区域
    .execution-preview-section {
      margin-top: 16px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      overflow: hidden;

      .section-title {
        padding: 12px 16px;
        background: #f5f7fa;
        border-bottom: 1px solid #e4e7ed;
        margin-bottom: 0;
      }

      .preview-data-container {
        max-height: 300px;
        overflow-y: auto;
        padding: 12px;
        background: #fff;
      }
    }

    .execution-loading,
    .execution-error {
      margin-top: 16px;
    }

    .request-option {
      display: flex;
      align-items: center;
      gap: 8px;

      .request-order {
        display: inline-block;
        width: 22px;
        height: 22px;
        line-height: 22px;
        text-align: center;
        background: #409eff;
        color: #fff;
        border-radius: 50%;
        font-size: 12px;
        font-weight: 600;
      }

      .request-name {
        flex: 1;
      }
    }
  }

  .preview-section {
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-top: 20px;

    .preview-input {
      :deep(.el-input__inner) {
        font-family: monospace;
        color: #409eff;
      }
    }
  }
}
</style>
