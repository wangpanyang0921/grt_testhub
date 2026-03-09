<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select v-model="projectId" :placeholder="$t('uiAutomation.common.selectProject')" style="width: 220px" @change="onProjectChange" class="project-select">
        <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
      </el-select>
      <el-input
        v-model="searchKeyword"
        :placeholder="$t('uiAutomation.testCase.searchPlaceholder')"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button class="reset-btn" @click="handleReset">{{ $t('uiAutomation.common.reset') }}</el-button>
      <el-button type="primary" class="query-btn" @click="handleSearch">
        <el-icon><Search /></el-icon>
        {{ $t('uiAutomation.common.search') }}
      </el-button>
      <div class="filter-bar-spacer"></div>
      <el-button type="primary" class="create-btn" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        {{ $t('uiAutomation.testCase.newTestCase') }}
      </el-button>
    </div>

    <div class="card-container test-case-layout">
      <!-- 用例列表 -->
      <div v-if="!selectedTestCase" class="list-panel">
        <el-table
          :data="paginatedTestCases"
          v-loading="loading"
          stripe
          style="width: 100%"
          class="test-case-table"
        >
          <el-table-column label="序号" width="80" header-align="center" align="center">
            <template #default="{ $index }">
              {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.testCase.caseName')" min-width="200" header-align="center" align="left">
            <template #default="{ row }">
              <div class="case-name-cell" @click="selectTestCase(row)">{{ row.name }}</div>
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.testCase.caseDescription')" min-width="250" header-align="center" align="center" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.description || '' }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.testCase.stepsCount')" width="120" header-align="center" align="center">
            <template #default="{ row }">
              <span class="step-count">{{ row.steps?.length || 0 }} {{ $t('uiAutomation.testCase.stepsCountUnit') }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.common.updateTime')" width="180" header-align="center" align="center">
            <template #default="{ row }">
              {{ formatTime(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.common.operation')" width="320" fixed="right" header-align="center" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="success" class="action-btn run-btn" @click.stop="runTestCase(row)">
                  <el-icon><CaretRight /></el-icon>
                  <span>{{ $t('uiAutomation.testCase.run') }}</span>
                </el-button>
                <el-button size="small" class="action-btn edit-btn" @click.stop="editTestCase(row)">
                  <el-icon><Edit /></el-icon>
                  <span>{{ $t('uiAutomation.common.edit') }}</span>
                </el-button>
                <el-button size="small" class="action-btn copy-btn" @click.stop="copyTestCase(row)">
                  <el-icon><CopyDocument /></el-icon>
                  <span>{{ $t('uiAutomation.common.copy') }}</span>
                </el-button>
                <el-button size="small" type="danger" class="action-btn delete-btn" @click.stop="deleteTestCase(row)">
                  <el-icon><Delete /></el-icon>
                  <span>{{ $t('uiAutomation.common.delete') }}</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredTestCases.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 测试用例详情和步骤编辑 -->
      <div v-if="selectedTestCase" class="detail-panel">
        <div class="test-case-detail">
          <div class="detail-header">
            <div class="detail-title-wrapper">
              <el-button size="small" class="back-btn" @click="backToList">
                <el-icon><ArrowLeft /></el-icon>
                {{ $t('uiAutomation.common.back') }}
              </el-button>
              <h3 class="detail-title">{{ selectedTestCase.name }}</h3>
            </div>
            <div class="detail-actions">
              <el-button size="small" class="btn-secondary" @click="addStep">
                <el-icon><Plus /></el-icon>
                {{ $t('uiAutomation.testCase.addStep') }}
              </el-button>
              <el-button size="small" type="primary" @click="saveTestCase">
                <el-icon><Check /></el-icon>
                {{ $t('uiAutomation.testCase.saveTestCase') }}
              </el-button>
              <el-select v-model="selectedEngine" :placeholder="$t('uiAutomation.testCase.selectEngine')" size="small" style="width: 130px; margin-right: 10px" class="config-select">
                <el-option label="Playwright" value="playwright" />
                <el-option label="Selenium" value="selenium" />
              </el-select>
              <el-select v-model="selectedBrowser" :placeholder="$t('uiAutomation.testCase.selectBrowser')" size="small" style="width: 120px; margin-right: 10px" class="config-select">
                <el-option label="Chrome" value="chrome" />
                <el-option label="Firefox" value="firefox" />
                <el-option label="Safari" value="safari" />
                <el-option label="Edge" value="edge" />
              </el-select>
              <el-select v-model="headlessMode" :placeholder="$t('uiAutomation.testCase.runMode')" size="small" style="width: 110px; margin-right: 10px" class="config-select">
                <el-option :label="$t('uiAutomation.testCase.headedMode')" :value="false" />
                <el-option :label="$t('uiAutomation.testCase.headlessMode')" :value="true" />
              </el-select>
              <el-button size="small" type="success" @click="runTestCase(selectedTestCase)" :loading="isRunning" class="run-btn">
                <el-icon v-if="!isRunning"><CaretRight /></el-icon>
                {{ isRunning ? $t('uiAutomation.testCase.running') : $t('uiAutomation.testCase.run') }}
              </el-button>
              <el-button size="small" class="btn-secondary" v-if="executionResult" @click="toggleView">
                <el-icon><component :is="showSteps ? 'View' : 'Edit'" /></el-icon>
                {{ showSteps ? $t('uiAutomation.testCase.viewResult') : $t('uiAutomation.testCase.editSteps') }}
              </el-button>
              <el-button
                size="small"
                v-if="executionResult && !showSteps"
                type="success"
                @click="runTestCase(selectedTestCase)"
                :loading="isRunning"
                class="run-btn"
              >
                <el-icon v-if="!isRunning"><Refresh /></el-icon>
                {{ $t('uiAutomation.testCase.rerun') }}
              </el-button>
            </div>
          </div>

          <!-- 测试步骤编辑 -->
          <div class="steps-container" v-show="showSteps">
            <div class="steps-header">
              <h4 class="steps-title">{{ $t('uiAutomation.testCase.testSteps') }}</h4>
              <el-button size="small" class="btn-text" @click="expandAllSteps">
                {{ allStepsExpanded ? $t('uiAutomation.testCase.foldAll') : $t('uiAutomation.testCase.expandAll') }}
              </el-button>
            </div>

            <div class="steps-scroll-container">
              <div class="steps-list">
                <draggable
                  v-model="currentSteps"
                  item-key="id"
                  handle=".drag-handle"
                  @change="onStepsReorder"
                >
                  <template #item="{ element, index }">
                    <div class="step-item" :class="{ expanded: element.expanded }">
                      <div class="step-header">
                        <div class="step-left">
                          <el-icon class="drag-handle"><Rank /></el-icon>
                          <span class="step-number">{{ index + 1 }}</span>
                          <el-select
                            v-model="element.action_type"
                            :placeholder="$t('uiAutomation.testCase.selectAction')"
                            size="small"
                            style="width: 120px"
                            @change="onActionTypeChange(element)"
                            class="action-select"
                          >
                            <el-option :label="$t('uiAutomation.testCase.actionClick')" value="click" />
                            <el-option :label="$t('uiAutomation.testCase.actionFill')" value="fill" />
                            <el-option :label="$t('uiAutomation.testCase.actionGetText')" value="getText" />
                            <el-option :label="$t('uiAutomation.testCase.actionWaitFor')" value="waitFor" />
                            <el-option :label="$t('uiAutomation.testCase.actionHover')" value="hover" />
                            <el-option :label="$t('uiAutomation.testCase.actionScroll')" value="scroll" />
                            <el-option :label="$t('uiAutomation.testCase.actionScreenshot')" value="screenshot" />
                            <el-option :label="$t('uiAutomation.testCase.actionAssert')" value="assert" />
                            <el-option :label="$t('uiAutomation.testCase.actionWait')" value="wait" />
                            <el-option :label="$t('uiAutomation.testCase.actionSwitchTab')" value="switchTab" />
                          </el-select>
                          <el-select
                            v-if="needsElement(element.action_type)"
                            v-model="element.element_id"
                            :placeholder="$t('uiAutomation.testCase.selectElement')"
                            size="small"
                            style="width: 200px"
                            filterable
                            @change="onElementChange(element)"
                            class="element-select"
                          >
                            <el-option
                              v-for="elem in availableElements"
                              :key="elem.id"
                              :label="`${elem.name} (${elem.locator_value})`"
                              :value="elem.id"
                            />
                          </el-select>
                        </div>
                        <div class="step-right">
                          <el-button
                            size="small"
                            class="btn-icon"
                            @click="element.expanded = !element.expanded"
                          >
                            <el-icon>
                              <component :is="element.expanded ? 'ArrowUp' : 'ArrowDown'" />
                            </el-icon>
                          </el-button>
                          <el-button size="small" class="btn-icon delete" @click="removeStep(index)">
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </div>
                      </div>

                      <div v-if="element.expanded" class="step-content">
                        <!-- 输入参数 -->
                        <div v-if="needsInputValue(element.action_type)" class="step-param">
                          <label>{{ $t('uiAutomation.testCase.inputValue') }}</label>
                          <div style="display: flex; gap: 5px; flex: 1">
                            <el-input
                              v-model="element.input_value"
                              :placeholder="element.action_type === 'switchTab' ? $t('uiAutomation.testCase.switchTabPlaceholder') : $t('uiAutomation.testCase.inputPlaceholder')"
                              size="small"
                              class="param-input"
                            >
                              <template #append>
                                <el-button
                                  size="small"
                                  :icon="MagicStick"
                                  @click="openDataFactorySelector(element, 'input_value')"
                                  title="引用数据工厂"
                                  class="data-factory-btn"
                                />
                              </template>
                            </el-input>
                            <el-tooltip content="插入动态变量" placement="top" v-if="element.action_type !== 'switchTab'">
                              <el-button size="small" @click="openVariableHelper(element, 'input_value')" class="variable-helper-btn">
                                <el-icon><MagicStick /></el-icon>
                              </el-button>
                            </el-tooltip>
                          </div>
                        </div>

                        <!-- 等待时间 -->
                        <div v-if="needsWaitTime(element.action_type)" class="step-param">
                          <label>{{ $t('uiAutomation.testCase.waitTime') }}</label>
                          <el-input-number
                            v-model="element.wait_time"
                            :min="100"
                            :max="30000"
                            :step="100"
                            size="small"
                            class="param-input"
                          />
                        </div>

                        <!-- 断言参数 -->
                        <div v-if="element.action_type === 'assert'" class="step-param">
                          <label>{{ $t('uiAutomation.testCase.assertType') }}</label>
                          <el-select v-model="element.assert_type" size="small" style="width: 150px" class="param-select">
                            <el-option :label="$t('uiAutomation.testCase.assertTextContains')" value="textContains" />
                            <el-option :label="$t('uiAutomation.testCase.assertTextEquals')" value="textEquals" />
                            <el-option :label="$t('uiAutomation.testCase.assertIsVisible')" value="isVisible" />
                            <el-option :label="$t('uiAutomation.testCase.assertExists')" value="exists" />
                            <el-option :label="$t('uiAutomation.testCase.assertHasAttribute')" value="hasAttribute" />
                          </el-select>
                          <div style="display: flex; align-items: center; margin-left: 10px; width: 240px">
                            <el-input
                              v-model="element.assert_value"
                              :placeholder="$t('uiAutomation.testCase.expectedValue')"
                              size="small"
                              style="flex: 1"
                              class="param-input"
                            >
                              <template #append>
                                <el-button
                                  size="small"
                                  :icon="MagicStick"
                                  @click="openDataFactorySelector(element, 'assert_value')"
                                  title="引用数据工厂"
                                  class="data-factory-btn"
                                />
                              </template>
                            </el-input>
                            <el-tooltip content="插入动态变量" placement="top">
                              <el-button size="small" style="margin-left: 5px" @click="openVariableHelper(element, 'assert_value')" class="variable-helper-btn">
                                <el-icon><MagicStick /></el-icon>
                              </el-button>
                            </el-tooltip>
                          </div>
                        </div>

                        <!-- 步骤描述 -->
                        <div class="step-param">
                          <label>{{ $t('uiAutomation.testCase.stepDescription') }}</label>
                          <el-input
                            v-model="element.description"
                            :placeholder="$t('uiAutomation.testCase.stepDescPlaceholder')"
                            size="small"
                            class="param-input"
                          />
                        </div>
                      </div>
                    </div>
                  </template>
                </draggable>
              </div>
            </div>
          </div>

          <!-- 执行结果 -->
          <div v-if="executionResult" class="execution-result" v-show="!showSteps">
            <div class="result-header">
              <h4 class="result-title">{{ $t('uiAutomation.testCase.executionResult') }}</h4>
              <el-tag :type="executionResult.success ? 'success' : 'danger'" class="result-tag">
                {{ executionResult.success ? $t('uiAutomation.testCase.executionSuccess') : $t('uiAutomation.testCase.executionFailed') }}
              </el-tag>
            </div>
            <div class="result-content">
              <el-tabs v-model="resultActiveTab" class="result-tabs">
                <el-tab-pane :label="$t('uiAutomation.testCase.executionLogs')" name="logs">
                  <div class="logs-container">
                    <div v-if="parsedExecutionLogs.length > 0">
                      <div v-for="(step, index) in parsedExecutionLogs" :key="index" class="log-item">
                        <div class="log-header">
                          <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                            {{ $t('uiAutomation.testCase.step') }} {{ step.step_number }}
                          </el-tag>
                          <span class="log-action">{{ getActionText(step.action_type) }}</span>
                          <span class="log-desc">{{ step.description }}</span>
                        </div>
                        <div v-if="step.error" class="log-error">
                          <el-icon><WarningFilled /></el-icon>
                          <pre class="error-message">{{ step.error }}</pre>
                        </div>
                      </div>
                    </div>
                    <el-empty v-else :description="$t('uiAutomation.testCase.noLogs')" />
                  </div>
                </el-tab-pane>
                <el-tab-pane :label="$t('uiAutomation.testCase.failedScreenshots')" name="screenshots" v-if="executionResult.screenshots && executionResult.screenshots.length > 0">
                  <div class="screenshots-container">
                    <div
                      v-for="(screenshot, index) in executionResult.screenshots"
                      :key="index"
                      class="screenshot-item"
                      @click="previewScreenshot(screenshot)"
                    >
                      <div class="screenshot-wrapper">
                        <img
                          :src="screenshot.url"
                          :alt="`${$t('uiAutomation.testCase.screenshot')} ${index + 1}`"
                          :data-index="index"
                          @error="handleImageError"
                          @load="handleImageLoad"
                        />
                        <div class="screenshot-placeholder" v-if="!screenshot.loaded">
                          <el-icon><Picture /></el-icon>
                          <span>{{ $t('uiAutomation.testCase.loadingImage') }}</span>
                        </div>
                        <div class="screenshot-error" v-if="screenshot.error">
                          <el-icon><Warning /></el-icon>
                          <span>{{ $t('uiAutomation.testCase.imageLoadFailed') }}</span>
                        </div>
                        <div class="screenshot-overlay">
                          <el-icon class="zoom-icon"><ZoomIn /></el-icon>
                        </div>
                      </div>
                      <div class="screenshot-info">
                        <p class="screenshot-description">{{ screenshot.description || `${$t('uiAutomation.testCase.screenshot')} ${index + 1}` }}</p>
                        <p class="screenshot-meta" v-if="screenshot.step_number">{{ $t('uiAutomation.testCase.step') }} {{ screenshot.step_number }}</p>
                        <p class="screenshot-time" v-if="screenshot.timestamp">{{ formatTime(screenshot.timestamp) }}</p>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane :label="$t('uiAutomation.testCase.errorInfo')" name="errors" v-if="executionResult.errors && executionResult.errors.length > 0">
                  <div class="errors-container">
                    <div
                      v-for="(error, index) in executionResult.errors"
                      :key="index"
                      class="error-item"
                    >
                      <div class="error-header">
                        <el-tag type="danger" size="large">
                          <el-icon><WarningFilled /></el-icon>
                          {{ error.message || error }}
                        </el-tag>
                        <span v-if="error.step_number" class="error-step">
                          {{ $t('uiAutomation.testCase.step') }} {{ error.step_number }}
                        </span>
                      </div>

                      <div v-if="error.action_type || error.element || error.description" class="error-meta">
                        <div v-if="error.action_type" class="meta-item">
                          <span class="meta-label">{{ $t('uiAutomation.testCase.operationType') }}</span>
                          <span class="meta-value">{{ error.action_type }}</span>
                        </div>
                        <div v-if="error.element" class="meta-item">
                          <span class="meta-label">{{ $t('uiAutomation.testCase.targetElement') }}</span>
                          <span class="meta-value">{{ error.element }}</span>
                        </div>
                        <div v-if="error.description" class="meta-item">
                          <span class="meta-label">{{ $t('uiAutomation.testCase.stepDesc') }}</span>
                          <span class="meta-value">{{ error.description }}</span>
                        </div>
                      </div>

                      <div v-if="error.details || error.stack" class="error-details">
                        <div class="details-header">{{ $t('uiAutomation.testCase.detailErrorInfo') }}</div>
                        <pre class="details-content">{{ error.details || error.stack }}</pre>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 新建/编辑测试用例对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTestCase ? $t('uiAutomation.testCase.editTestCase') : $t('uiAutomation.testCase.createTestCase')"
      width="500px"
      class="custom-dialog"
    >
      <el-form :model="testCaseForm" label-width="100px">
        <el-form-item :label="$t('uiAutomation.testCase.caseName')" required class="is-required">
          <el-input v-model="testCaseForm.name" :placeholder="$t('uiAutomation.testCase.caseNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.testCase.caseDescription')">
          <el-input
            v-model="testCaseForm.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('uiAutomation.testCase.caseDescPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.testCase.priority')">
          <el-select v-model="testCaseForm.priority" style="width: 100%" class="priority-select">
            <el-option :label="$t('uiAutomation.testCase.priorityHigh')" value="high" />
            <el-option :label="$t('uiAutomation.testCase.priorityMedium')" value="medium" />
            <el-option :label="$t('uiAutomation.testCase.priorityLow')" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false" class="btn-cancel">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="saveTestCaseForm" class="btn-confirm">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 截图预览对话框 -->
    <el-dialog
      v-model="showScreenshotPreview"
      :title="$t('uiAutomation.testCase.screenshotPreview')"
      width="80%"
      :close-on-click-modal="true"
      class="custom-dialog"
    >
      <div v-if="currentScreenshot" class="screenshot-preview">
        <div class="preview-info">
          <h4>{{ currentScreenshot.description }}</h4>
          <p v-if="currentScreenshot.step_number">{{ $t('uiAutomation.testCase.failedStep') }}: {{ $t('uiAutomation.testCase.step') }} {{ currentScreenshot.step_number }}</p>
          <p v-if="currentScreenshot.timestamp">{{ $t('uiAutomation.testCase.screenshotTime') }}: {{ formatTime(currentScreenshot.timestamp) }}</p>
        </div>
        <div class="preview-image">
          <img :src="currentScreenshot.url" :alt="currentScreenshot.description" />
        </div>
      </div>
    </el-dialog>

    <!-- 变量助手对话框 -->
    <el-dialog
      v-model="showVariableHelper"
      :title="$t('uiAutomation.testCase.variableHelper')"
      :close-on-click-modal="false"
      width="900px"
      class="custom-dialog"
    >
      <el-tabs tab-position="left" style="height: 450px" class="variable-tabs">
        <el-tab-pane
          v-for="(category, index) in variableCategoriesComputed"
          :key="index"
          :label="category.label"
        >
          <div style="height: 450px; overflow-y: auto; padding: 10px;">
            <el-table :data="category.variables" style="width: 100%" @row-click="insertVariable" highlight-current-row class="variable-table">
              <el-table-column prop="name" label="函数名" width="150" show-overflow-tooltip>
                <template #default="{ row }">
                  <el-tag size="small" class="function-tag">{{ row.name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="desc" label="描述" min-width="150" />
              <el-table-column prop="syntax" label="语法" min-width="200" show-overflow-tooltip />
              <el-table-column prop="example" label="示例" min-width="200" show-overflow-tooltip />
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" class="insert-btn">{{ $t('uiAutomation.testCase.insert') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <DataFactorySelector
      v-model="showDataFactorySelector"
      @select="handleDataFactorySelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, CaretRight, Edit, CopyDocument, Delete, Check,
  Rank, ArrowUp, ArrowDown, WarningFilled, Picture, Warning,
  ZoomIn, View, Refresh, MagicStick, ArrowLeft
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import {
  getTestCases,
  createTestCase,
  updateTestCase,
  deleteTestCase as deleteTestCaseApi,
  getTestCaseDetail,
  runTestCase as runTestCaseApi,
  getElements,
  getUiProjects
} from '@/api/ui_automation'
import DataFactorySelector from '@/components/DataFactorySelector.vue'

const { t } = useI18n()

// 项目选择
const projectId = ref(null)
const projects = ref([])

// 测试用例列表
const testCases = ref([])
const selectedTestCase = ref(null)
const searchKeyword = ref('')
const loading = ref(false)

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

// 当前步骤
const currentSteps = ref([])
const showSteps = ref(true)
const allStepsExpanded = ref(false)

// 执行相关
const isRunning = ref(false)
const executionResult = ref(null)
const resultActiveTab = ref('logs')
const selectedEngine = ref('playwright')
const selectedBrowser = ref('chrome')
const headlessMode = ref(false)

// 可用元素
const availableElements = ref([])

// 对话框
const showCreateDialog = ref(false)
const editingTestCase = ref(null)
const testCaseForm = reactive({
  name: '',
  description: '',
  priority: 'medium'
})

// 截图预览
const showScreenshotPreview = ref(false)
const currentScreenshot = ref(null)

// 变量助手
const showVariableHelper = ref(false)
const currentEditingStep = ref(null)
const currentEditingField = ref('')

// 数据工厂选择器
const showDataFactorySelector = ref(false)
const currentStepForDataFactory = ref(null)
const currentFieldForDataFactory = ref('')

// 过滤后的测试用例
const filteredTestCases = computed(() => {
  if (!searchKeyword.value) return testCases.value
  const keyword = searchKeyword.value.toLowerCase()
  return testCases.value.filter(tc =>
    tc.name.toLowerCase().includes(keyword) ||
    (tc.description && tc.description.toLowerCase().includes(keyword))
  )
})

// 分页后的测试用例
const paginatedTestCases = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filteredTestCases.value.slice(start, end)
})

// 解析执行日志
const parsedExecutionLogs = computed(() => {
  if (!executionResult.value?.logs) return []
  try {
    const logs = typeof executionResult.value.logs === 'string'
      ? JSON.parse(executionResult.value.logs)
      : executionResult.value.logs
    return Array.isArray(logs) ? logs : []
  } catch (e) {
    return []
  }
})

// 变量分类
const variableCategoriesComputed = computed(() => [
  {
    label: t('uiAutomation.testCase.variableCategories.string'),
    variables: [
      { name: 'random_string', syntax: '${random_string(length)}', desc: '生成随机字符串', example: '${random_string(10)}' },
      { name: 'random_number', syntax: '${random_number(min, max)}', desc: '生成随机数字', example: '${random_number(1, 100)}' },
      { name: 'random_uuid', syntax: '${random_uuid()}', desc: '生成UUID', example: '${random_uuid()}' },
      { name: 'word_count', syntax: '${word_count(text)}', desc: '字数统计', example: '${word_count("hello world")}' },
      { name: 'regex_test', syntax: '${regex_test(pattern, text, flags)}', desc: '正则测试', example: '${regex_test("^[a-z]+\\d+$", "hello123", "gi")}' },
      { name: 'case_convert', syntax: '${case_convert(text, convert_type)}', desc: '大小写转换', example: '${case_convert("hello", "upper")}' },
    ]
  },
  {
    label: t('uiAutomation.testCase.variableCategories.businessData'),
    variables: [
      { name: 'generate_chinese_name', syntax: '${generate_chinese_name(gender, count)}', desc: '生成中文姓名', example: '${generate_chinese_name("random", 1)}' },
      { name: 'generate_chinese_phone', syntax: '${generate_chinese_phone(count)}', desc: '生成手机号', example: '${generate_chinese_phone(1)}' },
      { name: 'generate_chinese_email', syntax: '${generate_chinese_email(count)}', desc: '生成邮箱', example: '${generate_chinese_email(1)}' },
      { name: 'generate_chinese_address', syntax: '${generate_chinese_address(full_address, count)}', desc: '生成地址', example: '${generate_chinese_address(true, 1)}' },
      { name: 'generate_id_card', syntax: '${generate_id_card(count)}', desc: '生成身份证号', example: '${generate_id_card(1)}' },
      { name: 'generate_company_name', syntax: '${generate_company_name(count)}', desc: '生成公司名称', example: '${generate_company_name(1)}' },
      { name: 'generate_bank_card', syntax: '${generate_bank_card(count)}', desc: '生成银行卡号', example: '${generate_bank_card(1)}' },
      { name: 'generate_hk_id_card', syntax: '${generate_hk_id_card(count)}', desc: '生成香港身份证号', example: '${generate_hk_id_card(1)}' },
      { name: 'generate_business_license', syntax: '${generate_business_license(count)}', desc: '生成营业执照号', example: '${generate_business_license(1)}' },
      { name: 'generate_user_profile', syntax: '${generate_user_profile(count)}', desc: '生成用户档案', example: '${generate_user_profile(1)}' },
      { name: 'generate_coordinates', syntax: '${generate_coordinates(count)}', desc: '生成经纬度', example: '${generate_coordinates(1)}' }
    ]
  },
  {
    label: t('uiAutomation.testCase.variableCategories.dateTime'),
    variables: [
      { name: 'timestamp_convert', syntax: '${timestamp_convert(timestamp, convert_type)}', desc: '时间戳转换', example: '${timestamp_convert(1234567890, "to_datetime")}' },
      { name: 'random_date', syntax: '${random_date(start_date, end_date, count, date_format)}', desc: '生成随机日期', example: '${random_date("2024-01-01", "2024-12-31", 1, "%Y-%m-%d")}' }
    ]
  },
  {
    label: '编码转换',
    variables: [
      { name: 'base64_encode', syntax: '${base64_encode(text, encoding)}', desc: 'Base64编码', example: '${base64_encode("123456", "utf-8")}' },
      { name: 'base64_decode', syntax: '${base64_decode(text, encoding)}', desc: 'Base64解码', example: '${base64_decode("MTIzNDU2", "utf-8")}' },
      { name: 'url_encode', syntax: '${url_encode(data, encoding)}', desc: 'URL编码', example: '${url_encode("hello world", "utf-8")}' },
      { name: 'url_decode', syntax: '${url_decode(data, encoding)}', desc: 'URL解码', example: '${url_decode("hello%20world", "utf-8")}' },
      { name: 'unicode_convert', syntax: '${unicode_convert(text, convert_type)}', desc: 'Unicode转换', example: '${unicode_convert("你好", "to_unicode")}' },
      { name: 'ascii_convert', syntax: '${ascii_convert(text, convert_type)}', desc: 'ASCII转换', example: '${ascii_convert("ABC", "to_ascii")}' },
      { name: 'color_convert', syntax: '${color_convert(color, from_type, to_type)}', desc: '颜色值转换', example: '${color_convert("#ff0000", "hex", "rgb")}' },
      { name: 'base_convert', syntax: '${base_convert(number, from_base, to_base)}', desc: '进制转换', example: '${base_convert(10, 10, 16)}' },
      { name: 'timestamp_convert', syntax: '${timestamp_convert(timestamp, convert_type)}', desc: '时间戳转换', example: '${timestamp_convert(1234567890, "to_datetime")}' },
      { name: 'generate_barcode', syntax: '${generate_barcode(data, format)}', desc: '生成条形码', example: '${generate_barcode("123456", "code128")}' },
      { name: 'generate_qrcode', syntax: '${generate_qrcode(data)}', desc: '生成二维码', example: '${generate_qrcode("https://example.com")}' },
      { name: 'decode_qrcode', syntax: '${decode_qrcode(data)}', desc: '二维码解析', example: '${decode_qrcode("/path/to/image.png")}' },
      { name: 'image_to_base64', syntax: '${image_to_base64(image_path)}', desc: '图片转Base64', example: '${image_to_base64("/path/to/image.png")}' },
      { name: 'base64_to_image', syntax: '${base64_to_image(base64_data, output_path)}', desc: 'Base64转图片', example: '${base64_to_image("data:image/png;base64,...", "/path/to/output.png")}' }
    ]
  },
  {
    label: '加密哈希',
    variables: [
      { name: 'md5_hash', syntax: '${md5_hash(text)}', desc: 'MD5加密', example: '${md5_hash("123456")}' },
      { name: 'sha1_hash', syntax: '${sha1_hash(text)}', desc: 'SHA1加密', example: '${sha1_hash("123456")}' },
      { name: 'sha256_hash', syntax: '${sha256_hash(text)}', desc: 'SHA256加密', example: '${sha256_hash("123456")}' },
      { name: 'sha512_hash', syntax: '${sha512_hash(text)}', desc: 'SHA512加密', example: '${sha512_hash("123456")}' },
      { name: 'hash_comparison', syntax: '${hash_comparison(hash1, hash2)}', desc: '哈希值比对', example: '${hash_comparison("hash1", "hash2")}' },
      { name: 'aes_encrypt', syntax: '${aes_encrypt(text, password, mode)}', desc: 'AES加密', example: '${aes_encrypt("hello", "password", "CBC")}' },
      { name: 'aes_decrypt', syntax: '${aes_decrypt(encrypted_text, password, mode)}', desc: 'AES解密', example: '${aes_decrypt("encrypted", "password", "CBC")}' }
    ]
  },
  {
    label: 'Crontab',
    variables: [
      { name: 'generate_expression', syntax: '${generate_expression(minute, hour, day, month, weekday)}', desc: '生成Crontab表达式', example: '${generate_expression("*", "*", "*", "*", "*")}' },
      { name: 'parse_expression', syntax: '${parse_expression(expression)}', desc: '解析Crontab表达式', example: '${parse_expression("0 0 * * *")}' },
      { name: 'get_next_runs', syntax: '${get_next_runs(expression, count)}', desc: '获取下次执行时间', example: '${get_next_runs("0 0 * * *", 5)}' },
      { name: 'validate_expression', syntax: '${validate_expression(expression)}', desc: '验证Crontab表达式', example: '${validate_expression("0 0 * * *")}' }
    ]
  },
  {
    label: t('uiAutomation.testCase.variableCategories.other'),
    variables: [
      { name: 'random_password', syntax: '${random_password(length, include_uppercase, include_lowercase, include_digits, include_special, count)}', desc: '生成随机密码', example: '${random_password(12, true, true, true, true, 1)}' },
      { name: 'random_color', syntax: '${random_color(format, count)}', desc: '生成随机颜色', example: '${random_color(hex, 1)}' },
      { name: 'jwt_decode', syntax: '${jwt_decode(token, verify, secret)}', desc: 'JWT解码', example: '${jwt_decode(token, false, secret)}' },
      { name: 'password_strength', syntax: '${password_strength(password)}', desc: '密码强度分析', example: '${password_strength(myPassword123)}' },
      { name: 'generate_salt', syntax: '${generate_salt(length)}', desc: '生成随机盐值', example: '${generate_salt(16)}' }
    ]
  }
])

const openVariableHelper = (step, field) => {
  currentEditingStep.value = step
  currentEditingField.value = field
  showVariableHelper.value = true
}

const openDataFactorySelector = (step, field) => {
  currentStepForDataFactory.value = step
  currentFieldForDataFactory.value = field
  showDataFactorySelector.value = true
}

const handleDataFactorySelect = (record) => {
  const step = currentStepForDataFactory.value
  const field = currentFieldForDataFactory.value

  if (record && record.output_data && step && field) {
    let valueToSet = ''

    if (typeof record.output_data === 'string') {
      valueToSet = record.output_data
    } else if (typeof record.output_data === 'object') {
      valueToSet = JSON.stringify(record.output_data)
    }

    step[field] = valueToSet
    ElMessage.success(`已引用数据: ${record.name}`)
  }
}

const insertVariable = (row) => {
  if (currentEditingStep.value && currentEditingField.value) {
    const currentValue = currentEditingStep.value[currentEditingField.value] || ''
    currentEditingStep.value[currentEditingField.value] = currentValue + row.syntax
    showVariableHelper.value = false
    ElMessage.success(`已插入变量: ${row.name}`)
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects()
    projects.value = response.data.results || response.data
    if (projects.value.length > 0 && !projectId.value) {
      projectId.value = projects.value[0].id
      await onProjectChange(projectId.value)
    }
  } catch (error) {
    console.error('加载项目失败:', error)
    ElMessage.error('加载项目失败')
  }
}

// 项目切换
const onProjectChange = async (id) => {
  projectId.value = id
  selectedTestCase.value = null
  executionResult.value = null
  await loadTestCases()
  await loadElements()
}

// 加载测试用例
const loadTestCases = async () => {
  if (!projectId.value) return
  loading.value = true
  try {
    const response = await getTestCases({ project: projectId.value })
    testCases.value = response.data.results || response.data
  } catch (error) {
    console.error('加载测试用例失败:', error)
    ElMessage.error('加载测试用例失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.currentPage = 1
}

// 重置
const handleReset = () => {
  searchKeyword.value = ''
  pagination.currentPage = 1
}

// 分页大小变化
const handleSizeChange = () => {
  pagination.currentPage = 1
}

// 页码变化
const handleCurrentChange = () => {
  // 页码变化时自动重新计算 paginatedTestCases
}

// 加载元素
const loadElements = async () => {
  if (!projectId.value) return
  try {
    const response = await getElements({ project: projectId.value })
    availableElements.value = response.data.results || response.data
  } catch (error) {
    console.error('加载元素失败:', error)
  }
}

// 选择测试用例
const selectTestCase = async (testCase) => {
  selectedTestCase.value = testCase
  executionResult.value = null
  showSteps.value = true
  try {
    const response = await getTestCaseDetail(testCase.id)
    currentSteps.value = (response.data.steps || []).map(step => ({
      ...step,
      expanded: false
    }))
  } catch (error) {
    console.error('加载测试用例详情失败:', error)
    ElMessage.error('加载测试用例详情失败')
  }
}

// 返回列表
const backToList = () => {
  selectedTestCase.value = null
  currentSteps.value = []
  executionResult.value = null
}

// 添加步骤
const addStep = () => {
  currentSteps.value.push({
    id: Date.now(),
    action_type: 'click',
    element_id: null,
    input_value: '',
    wait_time: 1000,
    description: '',
    expanded: true
  })
}

// 删除步骤
const removeStep = (index) => {
  currentSteps.value.splice(index, 1)
}

// 步骤重排
const onStepsReorder = () => {
  // 步骤顺序已在 v-model 中更新
}

// 展开/折叠所有步骤
const expandAllSteps = () => {
  allStepsExpanded.value = !allStepsExpanded.value
  currentSteps.value.forEach(step => {
    step.expanded = allStepsExpanded.value
  })
}

// 操作类型改变
const onActionTypeChange = (step) => {
  // 根据操作类型重置相关字段
  if (!needsElement(step.action_type)) {
    step.element_id = null
  }
  if (!needsInputValue(step.action_type)) {
    step.input_value = ''
  }
}

// 元素改变
const onElementChange = (step) => {
  const element = availableElements.value.find(e => e.id === step.element_id)
  if (element && !step.description) {
    step.description = `${element.name}`
  }
}

// 判断是否需要元素
const needsElement = (actionType) => {
  return ['click', 'fill', 'getText', 'waitFor', 'hover', 'assert'].includes(actionType)
}

// 判断是否需要输入值
const needsInputValue = (actionType) => {
  return ['fill', 'wait', 'switchTab'].includes(actionType)
}

// 判断是否需要等待时间
const needsWaitTime = (actionType) => {
  return actionType === 'wait'
}

// 保存测试用例
const saveTestCase = async () => {
  if (!selectedTestCase.value) return
  try {
    const data = {
      name: selectedTestCase.value.name,
      description: selectedTestCase.value.description,
      steps: currentSteps.value.map((step, index) => ({
        ...step,
        order: index
      }))
    }
    await updateTestCase(selectedTestCase.value.id, data)
    ElMessage.success('保存成功')
    await loadTestCases()
  } catch (error) {
    console.error('保存测试用例失败:', error)
    ElMessage.error('保存失败')
  }
}

// 运行测试用例
const runTestCase = async (testCase) => {
  isRunning.value = true
  executionResult.value = null
  try {
    const response = await runTestCaseApi(testCase.id, {
      engine: selectedEngine.value,
      browser: selectedBrowser.value,
      headless: headlessMode.value
    })
    executionResult.value = response.data
    showSteps.value = false
    ElMessage.success('执行完成')
  } catch (error) {
    console.error('运行测试用例失败:', error)
    ElMessage.error('运行失败')
  } finally {
    isRunning.value = false
  }
}

// 切换视图
const toggleView = () => {
  showSteps.value = !showSteps.value
}

// 编辑测试用例
const editTestCase = (testCase) => {
  editingTestCase.value = testCase
  testCaseForm.name = testCase.name
  testCaseForm.description = testCase.description
  testCaseForm.priority = testCase.priority || 'medium'
  showCreateDialog.value = true
}

// 复制测试用例
const copyTestCase = async (testCase) => {
  try {
    const response = await getTestCaseDetail(testCase.id)
    const detail = response.data
    const data = {
      name: `${detail.name} - 复制`,
      description: detail.description,
      priority: detail.priority,
      project_id: projectId.value,
      steps: detail.steps || []
    }
    await createTestCase(data)
    ElMessage.success('复制成功')
    await loadTestCases()
  } catch (error) {
    console.error('复制测试用例失败:', error)
    ElMessage.error('复制失败')
  }
}

// 删除测试用例
const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试用例吗？', '提示', {
      type: 'warning'
    })
    await deleteTestCaseApi(testCase.id)
    ElMessage.success('删除成功')
    if (selectedTestCase.value?.id === testCase.id) {
      selectedTestCase.value = null
      currentSteps.value = []
    }
    await loadTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试用例失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 保存测试用例表单
const saveTestCaseForm = async () => {
  if (!testCaseForm.name) {
    ElMessage.warning('请输入用例名称')
    return
  }
  if (!projectId.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  try {
    const data = {
      name: testCaseForm.name,
      description: testCaseForm.description,
      priority: testCaseForm.priority,
      project_id: projectId.value,
      steps: []
    }
    if (editingTestCase.value) {
      await updateTestCase(editingTestCase.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createTestCase(data)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingTestCase.value = null
    testCaseForm.name = ''
    testCaseForm.description = ''
    testCaseForm.priority = 'medium'
    await loadTestCases()
  } catch (error) {
    console.error('保存测试用例失败:', error)
    ElMessage.error('保存失败')
  }
}

// 预览截图
const previewScreenshot = (screenshot) => {
  currentScreenshot.value = screenshot
  showScreenshotPreview.value = true
}

// 处理图片加载错误
const handleImageError = (event) => {
  const index = event.target.dataset.index
  if (executionResult.value?.screenshots?.[index]) {
    executionResult.value.screenshots[index].error = true
  }
}

// 处理图片加载成功
const handleImageLoad = (event) => {
  const index = event.target.dataset.index
  if (executionResult.value?.screenshots?.[index]) {
    executionResult.value.screenshots[index].loaded = true
  }
}

// 获取操作文本
const getActionText = (actionType) => {
  const actionMap = {
    click: '点击',
    fill: '输入',
    getText: '获取文本',
    waitFor: '等待元素',
    hover: '悬停',
    scroll: '滚动',
    screenshot: '截图',
    assert: '断言',
    wait: '等待',
    switchTab: '切换标签'
  }
  return actionMap[actionType] || actionType
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

// 监听对话框关闭
watch(showCreateDialog, (val) => {
  if (!val) {
    editingTestCase.value = null
    testCaseForm.name = ''
    testCaseForm.description = ''
    testCaseForm.priority = 'medium'
  }
})

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);

  .project-select {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.3);
      box-shadow: none;

      &:hover, &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }

    :deep(.el-input__inner) {
      color: #5a32a3;
      font-weight: 500;
    }
  }

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.3);
    box-shadow: none;

    &:hover, &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }

  .filter-bar-spacer {
    flex: 1;
  }

  .reset-btn {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: #ffffff;
    border: 1px solid rgba(147, 112, 219, 0.4);
    color: #5a32a3;

    &:hover {
      background: #f8f7ff;
      border-color: #7b42f6;
      color: #7b42f6;
    }
  }

  .query-btn {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
    }

    .el-icon {
      margin-right: 6px;
    }
  }

  .create-btn {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
    }

    .el-icon {
      margin-right: 6px;
    }
  }
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: 16px;
}

.test-case-layout {
  display: flex;
  flex-direction: row;
}

.list-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  padding: 16px;

  .test-case-table {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);

    &::before {
      display: none;
    }

    // 表头包装器
    :deep(.el-table__header-wrapper) {
      background-color: #ffffff !important;

      // 表头
      :deep(.el-table__header) {
        background-color: #ffffff !important;

        // 表头单元格
        :deep(th) {
          background-color: #ffffff !important;
          color: #5a32a3;
          font-weight: 600;
          font-size: 14px;
          border-bottom: 1px solid #e9ecef;
          padding: 16px;
          text-align: center;
          line-height: 24px;
          transition: all 0.3s ease;

          &:hover {
            background-color: #f8f7ff !important;
          }

          .cell {
            background-color: #ffffff !important;
            color: #5a32a3;
            font-weight: 600;
          }
        }
      }
    }

    // 表格主体
    :deep(.el-table__body-wrapper) {
      background-color: #ffffff;

      :deep(.el-table__body) {
        background-color: #ffffff;

        :deep(tr) {
          background-color: #ffffff;
          transition: all 0.3s ease;

          &:hover {
            background-color: #f8f7ff !important;
          }

          // 斑马纹
          &.el-table__row--striped {
            background-color: #fafafa;

            &:hover {
              background-color: #f8f7ff !important;
            }
          }

          :deep(td) {
            background-color: transparent;
            border-bottom: 1px solid #f0f0f0;
            padding: 12px 16px;
            color: #595959;
            font-size: 14px;
            text-align: center;
          }
        }
      }
    }

    // 直接覆盖表头单元格样式
    :deep(.el-table__header th) {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600 !important;
    }

    // 覆盖表头单元格内容样式
    :deep(.el-table__header th .cell) {
      background-color: #ffffff !important;
      color: #5a32a3 !important;
      font-weight: 600 !important;
    }

    // 行悬停效果
    :deep(.el-table__row:hover) {
      background-color: #f8f7ff !important;
    }

    // 用例名称样式 - 与 AISuiteList.vue 保持一致
    .case-name-cell {
      padding: 4px 8px;
      line-height: 1.6;
      color: #595959;
      cursor: pointer;
      transition: color 0.3s ease;

      &:hover {
        color: #7b42f6;
      }
    }

    .step-count {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 16px;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.3s ease;
      white-space: nowrap;
      background: #f5f5f5;
      color: #8c8c8c;
    }

    .action-buttons {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 4px;
      flex-wrap: nowrap;

      .action-btn {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 10px !important;
        border-radius: 6px;
        transition: all 0.3s ease;

        .el-icon {
          font-size: 14px;
        }

        span {
          font-size: 12px;
        }

        &.run-btn {
          background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%) !important;
          border: none !important;
          color: #ffffff !important;
          font-weight: 600 !important;

          &:hover {
            background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
          }
        }

        &.edit-btn {
          background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
          border: none !important;
          color: #ffffff !important;
          font-weight: 600 !important;

          &:hover {
            background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
          }
        }

        &.copy-btn {
          background: linear-gradient(135deg, #909399 0%, #606266 100%) !important;
          border: none !important;
          color: #ffffff !important;
          font-weight: 600 !important;

          &:hover {
            background: linear-gradient(135deg, #a6a9ad 0%, #909399 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(144, 147, 153, 0.4);
          }
        }

        &.delete-btn {
          background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%) !important;
          border: none !important;
          color: #ffffff !important;
          font-weight: 600 !important;

          &:hover {
            background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 77, 79, 0.4);
          }
        }
      }
    }
  }

  .pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 16px 0;
    margin-top: 8px;
    background: transparent;
    border: none;
    transition: all 0.3s ease;

    /* 定义主题变量 - 浅紫色风格 */
    --primary-color: #a78bfa;
    --primary-dark: #8b5cf6;
    --primary-light: #f3f0ff;
    --text-primary: #262626;
    --text-secondary: #595959;
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

    :deep(.el-pagination) {
      display: flex;
      align-items: center;
      gap: 4px;
      font-weight: 500;

      // 总条数
      .el-pagination__total {
        color: #6b7280;
        font-size: 14px;
        font-weight: 500;
        margin-right: 12px;
      }

      // 每页条数选择器
      .el-pagination__sizes {
        margin-right: 12px;

        .el-select {
          .el-input__wrapper {
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            box-shadow: none;

            &:hover {
              border-color: #a78bfa;
              box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
            }

            &.is-focus {
              border-color: #a78bfa;
              box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15);
            }
          }

          .el-input__inner {
            color: #374151;
            font-weight: 500;
          }
        }
      }

      // 上一页/下一页按钮
      .btn-prev,
      .btn-next {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        color: #6b7280;
        transition: all 0.3s ease;

        &:hover:not(:disabled) {
          background: #f5f3ff;
          border-color: #a78bfa;
          color: #8b5cf6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2);
        }

        &:disabled {
          background: #f5f5f5;
          border-color: #e0e0e0;
          color: #c0c0c0;
        }

        .el-icon {
          font-size: 14px;
          font-weight: bold;
        }
      }

      // 页码按钮
      .el-pager {
        display: flex;
        gap: 8px;

        li {
          min-width: 32px;
          height: 32px;
          padding: 0 8px;
          border-radius: 8px;
          border: 1px solid #d1d5db;
          background: #ffffff;
          color: #6b7280;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;

          &:hover:not(.is-active) {
            background: #f5f3ff;
            border-color: #a78bfa;
            color: #8b5cf6;
            transform: translateY(-1px);
          }

          &.is-active {
            background: #f5f3ff;
            border-color: #a78bfa;
            color: #8b5cf6;
            box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2);
          }

          &.is-active:hover {
            background: #ede9fe;
            border-color: #8b5cf6;
          }
        }
      }

      // 跳转输入框
      .el-pagination__jump {
        color: #6b7280;
        font-weight: 500;
        margin-left: 12px;

        .el-input {
          width: 50px;
          margin: 0 4px;

          .el-input__wrapper {
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            box-shadow: none;

            &:hover {
              border-color: #a78bfa;
              box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
            }

            &.is-focus {
              border-color: #a78bfa;
              box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15);
            }
          }

          .el-input__inner {
            color: #374151;
            font-weight: 500;
            text-align: center;
          }
        }
      }
    }
  }
}

.detail-panel {
  flex: 1;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .test-case-detail {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 24px;
    overflow: hidden;
    height: 100%;

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid rgba(147, 112, 219, 0.15);
      gap: 12px;
      min-height: 40px;

      .detail-title-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-shrink: 0;

        .back-btn {
          display: inline-flex !important;
          align-items: center;
          gap: 4px;
          background: #f5f3ff !important;
          border: 1px solid #7b42f6 !important;
          color: #5a32a3 !important;
          border-radius: 6px;
          padding: 6px 12px;
          font-size: 13px;
          visibility: visible !important;
          opacity: 1 !important;

          &:hover {
            background: #e8e4ff !important;
            border-color: #5a32a3 !important;
            color: #5a32a3 !important;
          }
        }

        .detail-title {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #5a32a3;
        }
      }

      .detail-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
        margin-left: auto;
        flex-shrink: 0;

        .btn-secondary {
          background: #ffffff;
          border: 1px solid rgba(147, 112, 219, 0.4);
          color: #5a32a3;
          border-radius: 6px;

          &:hover {
            background: #f8f7ff;
            border-color: #7b42f6;
            color: #7b42f6;
          }
        }

        .run-btn {
          background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%);
          border: none;
          border-radius: 6px;

          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
          }
        }

        .config-select {
          :deep(.el-input__wrapper) {
            border-radius: 6px;
            border: 1px solid rgba(147, 112, 219, 0.3);
          }
        }
      }
    }

    .steps-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      margin-bottom: 20px;
      border: 1px solid rgba(147, 112, 219, 0.15);
      border-radius: 10px;
      background: linear-gradient(180deg, #faf8ff 0%, #f5f3ff 100%);
      overflow: hidden;

      .steps-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid rgba(147, 112, 219, 0.15);
        background: #ffffff;

        .steps-title {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #5a32a3;
        }

        .btn-text {
          color: #7b42f6;

          &:hover {
            color: #5a32a3;
          }
        }
      }

      .steps-scroll-container {
        overflow-y: auto;
        flex: 1;
        min-height: 0;
        padding: 16px;

        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: #f5f5f5;
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
          background: #ccc;
          border-radius: 3px;

          &:hover {
            background: #999;
          }
        }
      }

      .steps-list {
        .step-item {
          background: #ffffff;
          border: 1px solid rgba(147, 112, 219, 0.15);
          border-radius: 10px;
          margin-bottom: 12px;
          box-shadow: 0 2px 8px rgba(147, 112, 219, 0.05);
          transition: all 0.3s ease;

          &:hover {
            border-color: #7b42f6;
            box-shadow: 0 4px 12px rgba(123, 66, 246, 0.1);
          }

          .step-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
            border-radius: 10px 10px 0 0;

            .step-left {
              display: flex;
              align-items: center;
              gap: 10px;

              .drag-handle {
                cursor: move;
                color: #9370db;
              }

              .step-number {
                background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
                color: white;
                width: 26px;
                height: 26px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
              }

              .action-select,
              .element-select {
                :deep(.el-input__wrapper) {
                  border-radius: 6px;
                  border: 1px solid rgba(147, 112, 219, 0.3);
                }
              }
            }

            .step-right {
              display: flex;
              gap: 6px;

              .btn-icon {
                padding: 6px;
                border-radius: 6px;
                background: rgba(147, 112, 219, 0.1);
                border: 1px solid rgba(147, 112, 219, 0.2);
                color: #7b42f6;

                &:hover {
                  background: rgba(147, 112, 219, 0.2);
                }

                &.delete {
                  background: rgba(245, 108, 108, 0.1);
                  border-color: rgba(245, 108, 108, 0.2);
                  color: #f56c6c;

                  &:hover {
                    background: rgba(245, 108, 108, 0.2);
                  }
                }
              }
            }
          }

          .step-content {
            padding: 16px;
            border-top: 1px solid rgba(147, 112, 219, 0.1);

            .step-param {
              display: flex;
              align-items: center;
              margin-bottom: 12px;
              gap: 10px;

              &:last-child {
                margin-bottom: 0;
              }

              label {
                width: 100px;
                font-weight: 500;
                color: #5a32a3;
                font-size: 13px;
              }

              .param-input,
              .param-select {
                :deep(.el-input__wrapper) {
                  border-radius: 6px;
                  border: 1px solid rgba(147, 112, 219, 0.3);

                  &:hover, &.is-focus {
                    border-color: #7b42f6;
                    box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
                  }
                }
              }
            }
          }
        }
      }
    }

    .execution-result {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      border: 1px solid rgba(147, 112, 219, 0.15);
      border-radius: 10px;
      background: #ffffff;
      overflow: hidden;

      .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid rgba(147, 112, 219, 0.15);
        background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);

        .result-title {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #5a32a3;
        }

        .result-tag {
          font-weight: 600;
        }
      }

      .result-content {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;
        padding: 20px;

        .result-tabs {
          :deep(.el-tabs__header) {
            margin-bottom: 16px;
          }

          :deep(.el-tabs__item) {
            color: #666;

            &.is-active {
              color: #7b42f6;
            }

            &:hover {
              color: #5a32a3;
            }
          }
        }
      }
    }
  }
}

.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

// 对话框样式
.custom-dialog {
  :deep(.el-dialog__header) {
    background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);
    padding: 20px 24px;
    margin-right: 0;

    .el-dialog__title {
      font-weight: 600;
      color: #5a32a3;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid rgba(147, 112, 219, 0.15);
    padding: 16px 24px;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .btn-cancel {
      border-radius: 6px;
      border: 1px solid rgba(147, 112, 219, 0.4);
      color: #5a32a3;

      &:hover {
        background: #f8f7ff;
        border-color: #7b42f6;
      }
    }

    .btn-confirm {
      border-radius: 6px;
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
      }
    }
  }
}

// 截图预览样式
.screenshot-preview {
  .preview-info {
    margin-bottom: 20px;
    padding: 16px;
    background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.15);

    h4 {
      margin: 0 0 8px 0;
      color: #5a32a3;
      font-weight: 600;
    }

    p {
      margin: 4px 0;
      color: #666;
      font-size: 14px;
    }
  }

  .preview-image {
    text-align: center;

    img {
      max-width: 100%;
      max-height: 70vh;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
  }
}

// 日志容器样式
.logs-container {
  .log-item {
    margin-bottom: 12px;
    padding: 12px;
    background: #f8f7ff;
    border-radius: 8px;
    border-left: 3px solid #7b42f6;

    .log-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      .log-action {
        font-weight: 500;
        color: #5a32a3;
      }

      .log-desc {
        color: #666;
        font-size: 13px;
      }
    }

    .log-error {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      padding: 8px;
      background: rgba(245, 108, 108, 0.1);
      border-radius: 6px;
      color: #f56c6c;

      .el-icon {
        margin-top: 2px;
      }

      .error-message {
        margin: 0;
        font-size: 12px;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  }
}

// 截图容器样式
.screenshots-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;

  .screenshot-item {
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);

      .screenshot-wrapper {
        box-shadow: 0 8px 24px rgba(123, 66, 246, 0.2);
      }
    }

    .screenshot-wrapper {
      position: relative;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid rgba(147, 112, 219, 0.2);
      aspect-ratio: 16/10;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .screenshot-placeholder,
      .screenshot-error {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        color: #999;
        gap: 8px;
      }

      .screenshot-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;

        .zoom-icon {
          font-size: 32px;
          color: white;
        }
      }

      &:hover .screenshot-overlay {
        opacity: 1;
      }
    }

    .screenshot-info {
      padding: 8px 0;

      .screenshot-description {
        margin: 0 0 4px 0;
        font-size: 13px;
        font-weight: 500;
        color: #5a32a3;
      }

      .screenshot-meta,
      .screenshot-time {
        margin: 0;
        font-size: 11px;
        color: #999;
      }
    }
  }
}

// 错误容器样式
.errors-container {
  .error-item {
    margin-bottom: 16px;
    padding: 16px;
    background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
    border-radius: 8px;
    border: 1px solid rgba(245, 108, 108, 0.2);

    .error-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .error-step {
        font-size: 13px;
        color: #f56c6c;
        font-weight: 500;
      }
    }

    .error-meta {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 8px;
      margin-bottom: 12px;
      padding: 12px;
      background: rgba(255, 255, 255, 0.5);
      border-radius: 6px;

      .meta-item {
        display: flex;
        gap: 8px;
        font-size: 13px;

        .meta-label {
          color: #999;
        }

        .meta-value {
          color: #5a32a3;
          font-weight: 500;
        }
      }
    }

    .error-details {
      .details-header {
        font-size: 13px;
        font-weight: 600;
        color: #f56c6c;
        margin-bottom: 8px;
      }

      .details-content {
        margin: 0;
        padding: 12px;
        background: rgba(245, 108, 108, 0.05);
        border-radius: 6px;
        font-size: 12px;
        color: #666;
        white-space: pre-wrap;
        word-break: break-all;
        max-height: 200px;
        overflow-y: auto;
      }
    }
  }
}

// 变量表格样式
.variable-table {
  :deep(.el-table__header) {
    th {
      background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
      color: #5a32a3;
      font-weight: 600;
    }
  }

  :deep(.el-table__row) {
    cursor: pointer;

    &:hover {
      background: #f8f7ff;
    }

    &.current-row {
      background: linear-gradient(135deg, #f0edff 0%, #e8e4ff 100%);
    }
  }

  .function-tag {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    color: white;
    border: none;
  }

  .insert-btn {
    color: #7b42f6;

    &:hover {
      color: #5a32a3;
    }
  }
}

// 优先级选择器样式
.priority-select {
  :deep(.el-input__wrapper) {
    border-radius: 6px;
    border: 1px solid rgba(147, 112, 219, 0.3);

    &:hover, &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }
}

// 数据工厂按钮样式
.data-factory-btn,
.variable-helper-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border: none;
  color: white;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);
  }
}

// 响应式布局适配
@media screen and (max-width: 1440px) {
  .page-container {
    padding: 16px;
    gap: 16px;
  }

  .page-header {
    padding: 16px 20px;

    .page-title {
      font-size: 20px;
    }
  }

  .list-panel {
    width: 320px;
    min-width: 320px;

    .panel-header {
      padding: 14px 16px;
    }

    .test-case-list {
      padding: 12px;

      .test-case-item {
        padding: 12px;
        margin-bottom: 10px;
      }
    }
  }

  .detail-panel {
    .test-case-detail {
      padding: 16px;

      .detail-header {
        margin-bottom: 16px;
        padding-bottom: 12px;

        .detail-title {
          font-size: 16px;
        }
      }
    }
  }
}

@media screen and (max-width: 1280px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }

  .page-header {
    padding: 14px 16px;
    flex-wrap: wrap;

    .page-title {
      font-size: 18px;
    }

    .header-actions {
      gap: 8px;

      .project-select {
        width: 180px !important;
      }
    }
  }

  .test-case-layout {
    flex-direction: column;
  }

  .list-panel {
    width: 100%;
    min-width: auto;
    border-right: none;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);
    max-height: 300px;

    .panel-header {
      padding: 12px 16px;

      .panel-title {
        font-size: 14px;
      }
    }

    .test-case-list {
      padding: 12px;

      .test-case-item {
        padding: 12px;
        margin-bottom: 8px;

        .case-header {
          .case-info {
            .case-name {
              font-size: 14px;
            }

            .case-description {
              font-size: 12px;
            }
          }

          .case-actions {
            .action-icon-btn {
              padding: 4px;
            }
          }
        }
      }
    }
  }

  .detail-panel {
    .test-case-detail {
      padding: 16px;

      .detail-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;

        .detail-actions {
          width: 100%;
          flex-wrap: wrap;

          .config-select {
            width: 100px !important;
          }
        }
      }

      .steps-container {
        .steps-header {
          padding: 12px 16px;

          .steps-title {
            font-size: 14px;
          }
        }

        .steps-scroll-container {
          padding: 12px;
        }
      }
    }
  }
}

@media screen and (max-width: 1024px) {
  .page-header {
    .header-actions {
      .project-select {
        width: 160px !important;
      }

      .el-button {
        padding: 8px 14px;
        font-size: 13px;
      }
    }
  }

  .list-panel {
    max-height: 250px;
  }

  .detail-panel {
    .test-case-detail {
      .detail-header {
        .detail-actions {
          .config-select {
            width: 90px !important;

            :deep(.el-input__inner) {
              font-size: 12px;
            }
          }

          .el-button {
            padding: 6px 10px;
            font-size: 12px;
          }
        }
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .page-container {
    padding: 8px;
    gap: 8px;
  }

  .page-header {
    padding: 12px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .page-title {
      font-size: 16px;
    }

    .header-actions {
      width: 100%;
      flex-wrap: wrap;

      .project-select {
        width: 100% !important;
        margin-right: 0;
        margin-bottom: 8px;
      }

      .el-button {
        flex: 1;
        min-width: 120px;
      }
    }
  }

  .card-container {
    padding: 12px;
    border-radius: 8px;
  }

  .list-panel {
    max-height: 200px;

    .panel-header {
      padding: 10px 12px;

      .panel-title {
        font-size: 13px;
      }
    }

    .test-case-list {
      padding: 8px;

      .test-case-item {
        padding: 10px;

        .case-header {
          flex-wrap: wrap;
          gap: 8px;

          .case-actions {
            width: 100%;
            justify-content: flex-end;
          }
        }
      }
    }
  }

  .detail-panel {
    .test-case-detail {
      padding: 12px;

      .detail-header {
        .detail-title {
          font-size: 15px;
        }

        .detail-actions {
          .config-select {
            width: calc(50% - 4px) !important;
            margin-right: 0 !important;
            margin-bottom: 8px;
          }

          .el-button {
            flex: 1;
            min-width: auto;
          }
        }
      }

      .steps-container {
        .steps-list {
          .step-item {
            .step-header {
              flex-wrap: wrap;
              gap: 8px;
              padding: 10px 12px;

              .step-left {
                flex-wrap: wrap;
                gap: 8px;

                .action-select,
                .element-select {
                  width: calc(50% - 4px) !important;
                }
              }
            }

            .step-content {
              padding: 12px;

              .step-param {
                flex-wrap: wrap;

                label {
                  width: 100%;
                  margin-bottom: 4px;
                }

                .param-input,
                .param-select {
                  width: 100% !important;
                }
              }
            }
          }
        }
      }
    }
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    .page-title {
      font-size: 15px;
    }
  }

  .list-panel {
    max-height: 180px;

    .test-case-list {
      .test-case-item {
        .case-header {
          .case-info {
            .case-name {
              font-size: 13px;
            }
          }
        }
      }
    }
  }

  .detail-panel {
    .test-case-detail {
      .detail-header {
        .detail-title {
          font-size: 14px;
        }
      }
    }
  }
}
</style>
