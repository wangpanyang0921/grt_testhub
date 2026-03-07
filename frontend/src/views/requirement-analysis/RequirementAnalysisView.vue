<template>
  <div class="requirement-analysis">
    <!-- 配置引导弹出窗口 -->
    <div v-if="showConfigGuide && !checkingConfig" class="modal-overlay" @click.self="showConfigGuide = false" :key="modalKey">
      <div class="guide-config-modal">
      <div class="guide-header">
        <svg class="guide-icon" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
          <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z" fill="#f59e0b"/>
          <path d="M464 336a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z" fill="#f59e0b"/>
        </svg>
        <div class="guide-title">
          <h2>{{ $t('configGuide.title') }}</h2>
          <p>{{ $t('configGuide.subtitle') }}</p>
        </div>
      </div>

      <div class="config-groups">
        <!-- 模型配置行 -->
        <div class="config-group">
          <div class="group-label">{{ $t('configGuide.modelConfig') }}</div>
          <div class="config-items-row">
            <div class="config-item-inline" :class="getConfigItemClass('writer_model')">
              <span class="status-symbol" v-html="getStatusSymbol('writer_model')"></span>
              <span class="config-label">{{ $t('configGuide.caseWriter') }}</span>
              <span class="config-name" v-if="configStatus.writer_model.name">{{ configStatus.writer_model.name }}</span>
              <span class="status-text" v-if="!configStatus.writer_model.configured">{{ $t('configGuide.unconfigured') }}</span>
              <span class="status-text warning" v-else-if="!configStatus.writer_model.enabled">{{ $t('configGuide.disabled') }}</span>
            </div>

            <div class="config-item-inline" :class="getConfigItemClass('reviewer_model')">
              <span class="status-symbol" v-html="getStatusSymbol('reviewer_model')"></span>
              <span class="config-label">{{ $t('configGuide.caseReviewer') }}</span>
              <span class="config-name" v-if="configStatus.reviewer_model.name">{{ configStatus.reviewer_model.name }}</span>
              <span class="status-text" v-if="!configStatus.reviewer_model.configured">{{ $t('configGuide.unconfigured') }}</span>
              <span class="status-text warning" v-else-if="!configStatus.reviewer_model.enabled">{{ $t('configGuide.disabled') }}</span>
            </div>
          </div>
        </div>

        <!-- 提示词配置行 -->
        <div class="config-group">
          <div class="group-label">{{ $t('configGuide.promptConfig') }}</div>
          <div class="config-items-row">
            <div class="config-item-inline" :class="getConfigItemClass('writer_prompt')">
              <span class="status-symbol" v-html="getStatusSymbol('writer_prompt')"></span>
              <span class="config-label">{{ $t('configGuide.caseWriter') }}</span>
              <span class="config-name" v-if="configStatus.writer_prompt.name">{{ configStatus.writer_prompt.name }}</span>
              <span class="status-text" v-if="!configStatus.writer_prompt.configured">{{ $t('configGuide.unconfigured') }}</span>
              <span class="status-text warning" v-else-if="!configStatus.writer_prompt.enabled">{{ $t('configGuide.disabled') }}</span>
            </div>

            <div class="config-item-inline" :class="getConfigItemClass('reviewer_prompt')">
              <span class="status-symbol" v-html="getStatusSymbol('reviewer_prompt')"></span>
              <span class="config-label">{{ $t('configGuide.caseReviewer') }}</span>
              <span class="config-name" v-if="configStatus.reviewer_prompt.name">{{ configStatus.reviewer_prompt.name }}</span>
              <span class="status-text" v-if="!configStatus.reviewer_prompt.configured">{{ $t('configGuide.unconfigured') }}</span>
              <span class="status-text warning" v-else-if="!configStatus.reviewer_prompt.enabled">{{ $t('configGuide.disabled') }}</span>
            </div>
          </div>
        </div>

        <!-- 生成行为配置行 -->
        <div class="config-group">
          <div class="group-label">{{ $t('configGuide.generationConfig') }}</div>
          <div class="config-items-row">
            <div class="config-item-inline" :class="getConfigItemClass('generation_config')">
              <span class="status-symbol" v-html="getStatusSymbol('generation_config')"></span>
              <span class="config-label">{{ $t('configGuide.generationSettings') }}</span>
              <span class="config-name" v-if="configStatus.generation_config && configStatus.generation_config.name">{{ configStatus.generation_config.name }}</span>
              <span class="status-text" v-if="!configStatus.generation_config || !configStatus.generation_config.configured">{{ $t('configGuide.unconfigured') }}</span>
            </div>
          </div>
        </div>
      </div>

        <div class="guide-actions">
          <button class="generate-manual-btn" @click="goToConfig">
            {{ $t('configGuide.goToConfig') }}
          </button>
          <div class="skip-action" @click="showConfigGuide = false">
            {{ $t('configGuide.configureLater') }}
          </div>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 页面顶部步骤指示器 - 在所有步骤页面显示 -->
      <div v-if="!isGenerating && !showResults && currentStep >= 1 && currentStep <= 3" class="steps-indicator-top">
        <div class="step-indicator-item" :class="{ active: currentStep >= 1, clickable: currentStep > 1 }" @click="goToStep(1)">
          <span class="step-indicator-number">1</span>
          <span class="step-indicator-text">输出模式</span>
        </div>
        <div class="step-indicator-line-horizontal" :class="{ active: currentStep >= 2 }"></div>
        <div class="step-indicator-item" :class="{ active: currentStep >= 2, clickable: currentStep > 2 }" @click="goToStep(2)">
          <span class="step-indicator-number">2</span>
          <span class="step-indicator-text">输入方式</span>
        </div>
        <div class="step-indicator-line-horizontal" :class="{ active: currentStep >= 3 }"></div>
        <div class="step-indicator-item" :class="{ active: currentStep >= 3, clickable: currentStep > 3 }" @click="goToStep(3)">
          <span class="step-indicator-number">3</span>
          <span class="step-indicator-text">填写需求</span>
        </div>
      </div>

      <!-- 初始欢迎界面 -->
      <div v-if="!isGenerating && !showResults && currentStep === 0" class="welcome-section">
        <div class="welcome-card">
          <div class="welcome-icon">🚀</div>
          <h2>个性化生成测试用例</h2>
          <button class="start-btn" @click="startSetup">
            开始配置
          </button>
        </div>
      </div>

      <!-- 步骤1：选择输出模式 -->
      <div v-if="!isGenerating && !showResults && currentStep === 1" class="step-section">
        <div class="step-card">
          <div class="step-card-main">
            <div class="step-content-wrapper">
              <div class="output-mode-selector">
                <div class="mode-option" :class="{ active: globalOutputMode === 'stream' }" @click="selectOutputMode('stream')">
                  <div class="mode-content">
                    <div class="mode-title">
                      <span class="mode-icon stream-icon">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M3 12c0-1.1.9-2 2-2h2c1.1 0 2 .9 2 2s-.9 2-2 2H5c-1.1 0-2-.9-2-2z" fill="currentColor"/>
                          <path d="M11 12c0-1.1.9-2 2-2h2c1.1 0 2 .9 2 2s-.9 2-2 2h-2c-1.1 0-2-.9-2-2z" fill="currentColor" opacity="0.6"/>
                          <path d="M3 6c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2s-.9 2-2 2H5c-1.1 0-2-.9-2-2z" fill="currentColor" opacity="0.4"/>
                          <path d="M3 18c0-1.1.9-2 2-2h6c1.1 0 2 .9 2 2s-.9 2-2 2H5c-1.1 0-2-.9-2-2z" fill="currentColor" opacity="0.8"/>
                          <path d="M17 6c0-1.1.9-2 2-2h2c1.1 0 2 .9 2 2s-.9 2-2 2h-2c-1.1 0-2-.9-2-2z" fill="currentColor"/>
                          <path d="M17 18c0-1.1.9-2 2-2h2c1.1 0 2 .9 2 2s-.9 2-2 2h-2c-1.1 0-2-.9-2-2z" fill="currentColor" opacity="0.6"/>
                        </svg>
                      </span>
                      流式输出
                    </div>
                    <div class="mode-desc">生成过程内容可见</div>
                  </div>
                </div>
                <div class="mode-option" :class="{ active: globalOutputMode === 'complete' }" @click="selectOutputMode('complete')">
                  <div class="mode-content">
                    <div class="mode-title">
                      <span class="mode-icon complete-icon">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/>
                        </svg>
                      </span>
                      完整输出
                    </div>
                    <div class="mode-desc">生成过程内容不可见</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤2：选择输入方式 -->
      <div v-if="!isGenerating && !showResults && currentStep === 2" class="step-section">
        <div class="step-card">
          <div class="step-card-main">
            <div class="step-content-wrapper">
              <div class="input-method-selector">
                <div class="input-method-option" :class="{ active: selectedInputMethod === 'manual' }" @click="selectInputMethod('manual')">
                  <div class="input-method-icon">✏️</div>
                  <div class="input-method-title">手动输入</div>
                </div>
                <div class="input-method-option" :class="{ active: selectedInputMethod === 'upload' }" @click="selectInputMethod('upload')">
                  <div class="input-method-icon">📁</div>
                  <div class="input-method-title">文件上传</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3：填写需求 -->
      <div v-if="!isGenerating && !showResults && currentStep === 3" class="step-section">
        <!-- 手动输入需求描述区域 -->
        <div v-if="selectedInputMethod === 'manual'" class="step-card">
          <div class="step-card-main">
            <div class="step-content-wrapper">
              <div class="input-form">
                <div class="form-group">
                  <label><span class="required">*</span> {{ $t('requirementAnalysis.requirementTitle') }}</label>
                  <input
                    v-model="manualInput.title"
                    type="text"
                    class="form-input">
                </div>

                <div class="form-group textarea-with-count">
                  <label><span class="required">*</span> {{ $t('requirementAnalysis.requirementDescription') }}</label>
                  <div class="textarea-wrapper">
                    <textarea
                      v-model="manualInput.description"
                      class="form-textarea"
                      rows="8"></textarea>
                    <div class="char-count">{{ manualInput.description.length }}/2000</div>
                  </div>
                </div>



                <button
                  class="generate-manual-btn"
                  @click="generateFromManualInput"
                  :disabled="!canGenerateManual || isGenerating">
                  <span v-if="isGenerating">{{ $t('requirementAnalysis.generating') }}</span>
                  <span v-else>{{ $t('requirementAnalysis.generateButton') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 文档上传区域 -->
        <div v-if="selectedInputMethod === 'upload'" class="step-card">
          <div class="step-card-main">
            <div class="step-content-wrapper">
              <!-- 文档标题输入框 - 在文件选择上方 -->
              <div v-if="selectedFile" class="document-info">
                <div class="form-group">
                  <label>{{ $t('requirementAnalysis.documentTitle') }}</label>
                  <input
                    v-model="documentTitle"
                    type="text"
                    class="form-input"
                    :placeholder="$t('requirementAnalysis.documentPlaceholder')">
                </div>
              </div>

              <h3 v-if="selectedFile" class="upload-section-title">需求上传</h3>
              <div class="upload-area"
                   @dragover.prevent
                   @drop="handleDrop"
                   :class="{ 'drag-over': isDragOver }"
                   @dragenter="isDragOver = true"
                   @dragleave="isDragOver = false">
                <div v-if="!selectedFile" class="upload-placeholder">
                  <i class="upload-icon">📁</i>
                  <p class="upload-hint">{{ $t('requirementAnalysis.supportedFormats') }}</p>
                  <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileSelect"
                    accept=".pdf,.doc,.docx,.txt,.md"
                    style="display: none;">
                  <button class="select-file-btn" @click="$refs.fileInput.click()">
                    {{ $t('requirementAnalysis.selectFile') }}
                  </button>
                </div>

                <div v-else class="file-selected">
                  <div class="file-info">
                    <div class="file-icon-wrapper">
                      <svg class="file-icon-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="url(#fileGradient)" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M14 2V8H20" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M16 13H8" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round"/>
                        <path d="M16 17H8" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round"/>
                        <path d="M10 9H8" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round"/>
                        <defs>
                          <linearGradient id="fileGradient" x1="4" y1="2" x2="20" y2="22" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#f5f0ff"/>
                            <stop offset="1" stop-color="#ede9fe"/>
                          </linearGradient>
                        </defs>
                      </svg>
                    </div>
                    <div class="file-details">
                      <p class="file-name">{{ selectedFile.name }}</p>
                    </div>
                    <button class="remove-file" @click="removeFile" title="移除文件">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="selectedFile">
                <button
                  class="generate-btn"
                  @click="generateFromDocument"
                  :disabled="!documentTitle || isGenerating">
                  <span v-if="isGenerating">{{ $t('requirementAnalysis.generating') }}</span>
                  <span v-else>{{ $t('requirementAnalysis.generateButton') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 生成进度和结果 -->
      <div v-if="isGenerating || showResults" class="generation-progress">
        <div class="progress-card">
          <!-- 进度步骤指示器 -->
          <div class="progress-steps">
            <div class="step" :class="{ active: currentStep >= 1 }">
              <span class="step-number">1</span>
              <span class="step-text">{{ $t('requirementAnalysis.stepAnalysis') }}</span>
            </div>
            <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
            <div class="step" :class="{ active: currentStep >= 2 }">
              <span class="step-number">2</span>
              <span class="step-text">{{ $t('requirementAnalysis.stepWriting') }}</span>
            </div>
            <div class="step-line" :class="{ active: currentStep >= 3 }" v-if="showReviewStep"></div>
            <div v-if="showReviewStep" class="step" :class="{ active: currentStep >= 3 }">
              <span class="step-number">3</span>
              <span class="step-text">{{ $t('requirementAnalysis.stepReview') }}</span>
            </div>
            <div class="step-line" :class="{ active: currentStep >= (showReviewStep ? 4 : 3) }"></div>
            <div class="step" :class="{ active: currentStep >= (showReviewStep ? 4 : 3) }">
              <span class="step-number">{{ showReviewStep ? 4 : 3 }}</span>
              <span class="step-text">{{ $t('requirementAnalysis.stepComplete') }}</span>
            </div>
          </div>

          <!-- 进度信息区域 - 仅在流式输出模式下显示 -->
          <div v-if="globalOutputMode === 'stream'" class="progress-info">
            <div class="progress-item">
              <span class="label">{{ $t('requirementAnalysis.currentStatus') }}</span>
              <span class="value">{{ showResults ? $t('requirementAnalysis.generationComplete') : progressText }}</span>
            </div>
            <div class="progress-item mode-item">
              <span class="label">输出模式</span>
              <span class="value mode-value">
                {{ $t('requirementAnalysis.realtimeStream') }}
              </span>
            </div>
            <button v-if="!showResults" class="cancel-generation-btn-inline" @click="cancelGeneration">
              {{ $t('requirementAnalysis.cancelGeneration') }}
            </button>
          </div>

          <!-- 完整输出模式提示区域 -->
          <div v-if="globalOutputMode === 'complete' && isGenerating" class="complete-mode-notice">
            <div class="notice-desc">AI正在后台生成测试用例，生成过程内容不可见。请耐心等待，完成后将显示最终结果。</div>
          </div>

          <!-- 完整输出模式下的取消按钮 -->
          <div v-if="globalOutputMode === 'complete' && !showResults" class="complete-mode-cancel">
            <button class="cancel-generation-btn-inline" @click="cancelGeneration">
              {{ $t('requirementAnalysis.cancelGeneration') }}
            </button>
          </div>

          <!-- 流式内容实时显示区域 - 仅在流式输出模式下显示 -->
          <div v-if="streamedContent && globalOutputMode === 'stream'" class="stream-content-display">
            <div class="stream-header" @click="contentExpanded = !contentExpanded" style="cursor: pointer;">
              <div class="stream-header-left">
                <span class="expand-icon">{{ contentExpanded ? '▼' : '▶' }}</span>
                <span class="stream-title">{{ $t('requirementAnalysis.realtimeGeneratedContent') }}</span>
              </div>
              <span class="stream-status">{{ $t('requirementAnalysis.characters', { count: streamedContent.length }) }}</span>
            </div>
            <div v-show="contentExpanded" class="stream-content" v-html="formatMarkdown(streamedContent)"></div>
          </div>

          <!-- 评审内容显示区域 - 仅在流式输出模式下显示 -->
          <div v-if="streamedReviewContent && globalOutputMode === 'stream'" class="stream-content-display" style="margin-top: 15px;">
            <div class="stream-header" @click="reviewExpanded = !reviewExpanded" style="cursor: pointer;">
              <div class="stream-header-left">
                <span class="expand-icon">{{ reviewExpanded ? '▼' : '▶' }}</span>
                <span class="stream-title">{{ $t('requirementAnalysis.aiReviewComments') }}</span>
              </div>
              <span class="stream-status">{{ $t('requirementAnalysis.characters', { count: streamedReviewContent.length }) }}</span>
            </div>
            <div v-show="reviewExpanded" class="stream-content" v-html="formatMarkdown(streamedReviewContent)"></div>
          </div>

          <!-- 最终版用例显示区域 - 仅在流式输出模式下显示 -->
          <div v-if="finalTestCases && globalOutputMode === 'stream'" class="stream-content-display" style="margin-top: 15px;">
            <div class="stream-header" @click="finalExpanded = !finalExpanded" style="cursor: pointer;">
              <div class="stream-header-left">
                <span class="expand-icon">{{ finalExpanded ? '▼' : '▶' }}</span>
                <span class="stream-title">
                  {{ $t('requirementAnalysis.finalVersionTestCases') }}
                  <span v-if="isGenerating" class="streaming-indicator">{{ $t('requirementAnalysis.generating') }}</span>
                </span>
              </div>
              <span class="stream-status">{{ $t('requirementAnalysis.characters', { count: finalTestCases.length }) }}</span>
            </div>
            <div v-show="finalExpanded" class="stream-content final-testcases" v-html="formatMarkdown(finalTestCases)"></div>
          </div>

          <!-- 任务完成后的操作按钮 -->
          <div v-if="showResults" class="completion-actions">
            <button class="new-generation-btn" @click="resetGeneration">
              {{ $t('requirementAnalysis.newGeneration') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 旧的生成结果区域已废弃，保留用于兼容 -->
      <!-- 现在使用流式显示区域 + 最终版用例区域 -->
      <div v-if="false && showResults && generationResult" class="generation-result">
        <div class="result-header">
          <h2>{{ $t('requirementAnalysis.generationComplete') }}</h2>
          <div class="result-summary">
            <span class="summary-item">
              {{ $t('requirementAnalysis.summaryTaskId', { taskId: generationResult.task_id }) }}
            </span>
            <span class="summary-item">
              {{ $t('requirementAnalysis.summaryGenerationTime', { time: formatDateTime(generationResult.completed_at) }) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import { useUserStore } from '@/stores/user'

export default {
  name: 'RequirementAnalysisView',
  data() {
    return {
      // 步骤管理：0-初始，1-选择输出模式，2-选择输入方式，3-填写需求
      currentStep: 0,
      // 输入方式选择：'manual'-手动输入，'upload'-文件上传
      selectedInputMethod: null,
      // 全局输出模式设置
      globalOutputMode: 'stream',  // 默认使用流式输出

      // 手动输入需求
      manualInput: {
        title: '',
        description: '',
        selectedProject: ''
      },

      // 文件上传
      selectedFile: null,
      documentTitle: '',
      selectedProject: '',
      projects: [],
      isDragOver: false,

      // 生成状态
      isGenerating: false,
      currentTaskId: null,
      progressText: '',
      currentStep: 0,
      pollInterval: null,
      eventSource: null,  // SSE连接
      streamedContent: '',  // 流式接收的内容
      streamedReviewContent: '',  // 流式接收的评审内容
      finalTestCases: '',  // 最终版用例
      hasShownCompletionMessage: false,  // 是否已经显示过完成消息
      showReviewStep: true,  // 是否显示评审步骤（根据生成配置决定）

      // 展开/收起状态
      contentExpanded: true,  // 实时生成内容展开状态
      reviewExpanded: true,   // AI评审意见展开状态
      finalExpanded: true,    // 最终版用例展开状态

      // 生成结果
      showResults: false,
      generationResult: null,

      // AI配置状态
      configStatus: {
        overall_status: 'unknown',
        message: '',
        writer_model: {
          configured: false,
          enabled: false,
          name: null,
          provider: null,
          id: null,
          required: true
        },
        writer_prompt: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true
        },
        reviewer_model: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true
        },
        reviewer_prompt: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true
        },
        generation_config: {
          configured: false,
          enabled: false,
          name: null,
          id: null,
          required: true,
          default_output_mode: null
        }
      },
      showConfigGuide: false,
      checkingConfig: true,
      modalKey: 0  // 用于强制重新渲染弹窗
    }
  },

  computed: {
    canGenerateManual() {
      return this.manualInput.title.trim() &&
             this.manualInput.description.trim() &&
             this.manualInput.description.length <= 2000
    }
  },

  async mounted() {
    this.progressText = this.$t('requirementAnalysis.preparing')
    this.loadProjects()
    this.checkConfigStatus()

    // 检查是否有任务ID参数，如果有则加载该任务
    const taskId = this.$route.query.taskId
    if (taskId) {
      console.log('检测到任务ID参数:', taskId)
      await this.loadExistingTask(taskId)
    } else {
      // 没有任务ID时，直接进入输出模式选择页面（跳过欢迎页面）
      this.currentStep = 1
    }
  },

  activated() {
    // 当从其他页面返回时，重新检查配置状态
    // 立即隐藏弹窗和遮罩层，强制重新渲染
    this.showConfigGuide = false
    this.checkingConfig = true
    this.modalKey += 1  // 改变key值，强制重新渲染弹窗

    // 延迟检查配置，确保页面完全加载后再显示弹窗
    setTimeout(async () => {
      await this.checkConfigStatus()
    }, 200)
  },

  beforeUnmount() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
    }
    // 停止token自动刷新定时器
    const userStore = useUserStore()
    userStore.stopAutoRefresh()
  },

  methods: {
    // 步骤管理方法
    startSetup() {
      this.currentStep = 1
    },

    selectOutputMode(mode) {
      this.globalOutputMode = mode
      this.currentStep = 2
    },

    // 加载已有任务
    async loadExistingTask(taskId) {
      try {
        console.log('加载已有任务:', taskId)
        const response = await api.get(`/requirement-analysis/testcase-generation/${taskId}/`)
        const task = response.data

        console.log('获取到任务信息:', task)
        console.log('任务output_mode字段:', task.output_mode)
        console.log('任务output_mode_display字段:', task.output_mode_display)

        // 设置任务信息
        this.currentTaskId = task.task_id
        this.isGenerating = true
        this.showResults = false
        
        // 设置输出模式 - 优先使用URL参数中的outputMode，如果没有则使用任务数据中的output_mode
        const urlOutputMode = this.$route.query.outputMode
        if (urlOutputMode) {
          this.globalOutputMode = urlOutputMode
          console.log('从URL参数设置输出模式:', urlOutputMode)
        } else if (task.output_mode) {
          this.globalOutputMode = task.output_mode
          console.log('从任务数据设置输出模式:', task.output_mode)
        } else {
          console.log('没有可用的输出模式，使用默认值stream，当前globalOutputMode:', this.globalOutputMode)
        }

        // 根据任务状态设置当前步骤
        if (task.status === 'pending') {
          this.currentStep = 1
          this.progressText = this.$t('requirementAnalysis.statusPending')
        } else if (task.status === 'generating') {
          this.currentStep = 2
          this.progressText = this.$t('requirementAnalysis.statusGenerating')
        } else if (task.status === 'reviewing' || task.status === 'revising') {
          this.currentStep = 3
          this.progressText = task.status === 'reviewing' ? this.$t('requirementAnalysis.statusReviewing') : this.$t('requirementAnalysis.statusRevising')
        } else if (task.status === 'completed') {
          this.currentStep = 4
          this.showResults = true
          this.progressText = this.$t('requirementAnalysis.statusCompleted')
        }

        // 恢复已有内容
        if (task.generated_test_cases) {
          this.streamedContent = task.generated_test_cases
        }
        if (task.review_feedback) {
          this.streamedReviewContent = task.review_feedback
        }
        if (task.final_test_cases) {
          this.finalTestCases = task.final_test_cases
        }

        // 如果任务还在进行中，继续监听进度
        if (task.status !== 'completed' && task.status !== 'failed') {
          console.log('任务仍在进行中，启动进度监听')
          if (task.output_mode === 'stream') {
            this.startStreamingProgress()
          } else {
            this.startPolling()
          }
        }

        ElMessage.success(this.$t('requirementAnalysis.taskLoaded'))
      } catch (error) {
        console.error('加载任务失败:', error)
        ElMessage.error(this.$t('requirementAnalysis.loadTaskFailed'))
      }
    },
    
    selectInputMethod(method) {
      this.selectedInputMethod = method
      this.currentStep = 3
    },
    
    goBack() {
      if (this.currentStep > 0) {
        this.currentStep -= 1
      }
    },
    
    goToStep(step) {
      // 只允许返回到已经完成的步骤
      if (step < this.currentStep) {
        this.currentStep = step
      }
    },
    
    resetToStart() {
      this.currentStep = 0
      this.selectedInputMethod = null
      this.selectedFile = null
      this.documentTitle = ''
      this.manualInput = {
        title: '',
        description: '',
        selectedProject: ''
      }
    },
    
    async loadProjects() {
      try {
        const response = await api.get('/projects/')
        this.projects = response.data.results || response.data
      } catch (error) {
        console.error(this.$t('requirementAnalysis.loadProjectsFailed'), error)
      }
    },

    async checkConfigStatus() {
      try {
        this.checkingConfig = true
        const response = await api.get('/requirement-analysis/config/check/')
        this.configStatus = response.data

        // 判断逻辑：只有当"用例编写模型"、"用例评审模型"、"用例编写提示词"和"用例评审提示词"都配置且启用时，才不显示弹框
        const writerModelReady = response.data.writer_model &&
                                response.data.writer_model.configured &&
                                response.data.writer_model.enabled

        const reviewerModelReady = response.data.reviewer_model &&
                                  response.data.reviewer_model.configured &&
                                  response.data.reviewer_model.enabled

        const writerPromptReady = response.data.writer_prompt &&
                                 response.data.writer_prompt.configured &&
                                 response.data.writer_prompt.enabled

        const reviewerPromptReady = response.data.reviewer_prompt &&
                                   response.data.reviewer_prompt.configured &&
                                   response.data.reviewer_prompt.enabled

        // 检查生成行为配置
        const generationConfigReady = response.data.generation_config &&
                                      response.data.generation_config.configured

        // 只有五项都准备好时才不显示引导弹框
        if (writerModelReady && reviewerModelReady && writerPromptReady && reviewerPromptReady && generationConfigReady) {
          this.showConfigGuide = false

          // 如果生成配置允许用户修改，则使用配置的默认输出模式
          // 但只有在没有从URL加载任务的情况下才设置
          if (response.data.generation_config && response.data.generation_config.default_output_mode && !this.$route.query.taskId) {
            this.globalOutputMode = response.data.generation_config.default_output_mode
          }

          // 根据生成配置的enable_auto_review决定是否显示评审步骤
          if (response.data.generation_config && response.data.generation_config.enable_auto_review !== null) {
            this.showReviewStep = response.data.generation_config.enable_auto_review
          } else {
            this.showReviewStep = true  // 默认显示
          }
        } else {
          this.showConfigGuide = true
        }
      } catch (error) {
        console.error('Failed to check config status:', error)
        // 如果检查失败，默认不显示引导，避免影响正常使用
        this.showConfigGuide = false
        this.checkingConfig = false
      } finally {
        this.checkingConfig = false
      }
    },

    goToConfig() {
      // 智能判断跳转目标：优先跳转到未配置/未启用的页面
      // 优先级：必需配置 > 可选配置，提示词 > 模型

      // 0. 首先检查生成行为配置（generation_config）
      if (!this.configStatus.generation_config || !this.configStatus.generation_config.configured) {
        this.$router.push('/configuration/generation-config')
        return
      }

      // 1. 优先检查必需的提示词配置（writer_prompt）
      if (!this.configStatus.writer_prompt.configured || !this.configStatus.writer_prompt.enabled) {
        this.$router.push('/configuration/prompt-config')
        return
      }

      // 2. 检查必需的模型配置（writer_model）
      if (!this.configStatus.writer_model.configured || !this.configStatus.writer_model.enabled) {
        this.$router.push('/configuration/ai-model')
        return
      }

      // 3. 检查可选的评审提示词（reviewer_prompt）
      if (!this.configStatus.reviewer_prompt.configured || !this.configStatus.reviewer_prompt.enabled) {
        this.$router.push('/configuration/prompt-config')
        return
      }

      // 4. 检查可选的评审模型（reviewer_model）
      if (!this.configStatus.reviewer_model.configured || !this.configStatus.reviewer_model.enabled) {
        this.$router.push('/configuration/ai-model')
        return
      }

      // 默认跳转到生成行为配置
      this.$router.push('/configuration/generation-config')
    },

    goToPromptConfig() {
      this.$router.push('/configuration/prompt-config')
    },

    getConfigItemClass(configKey) {
      const config = this.configStatus[configKey]
      if (config.enabled) {
        return 'status-enabled'
      } else if (config.configured) {
        return 'status-disabled'
      } else {
        return 'status-unconfigured'
      }
    },

    getStatusIcon(configKey) {
      const config = this.configStatus[configKey]
      if (config.enabled) {
        // 绿色对号
        return '<path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292c-12.7 17.7-39 17.7-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 13.3l71.2 98.8 157.2-218c6-8.3 15.6-13.3 25.9-13.3H699c6.5 0 10.3 7.4 6.5 12.7z" fill="#27ae60"/>'
      } else if (config.configured) {
        // 禁用图标（灰色圆圈和斜线）
        return '<path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372zm128-412c0 4.4-3.6 8-8 8H392c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h240c4.4 0 8 3.6 8 8v48z" fill="#95a5a6"/>'
      } else {
        // 红色叉号
        return '<path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm165.4 618.2l-66-70.7c-10.6-10.1-28.1-10.1-38.8 0l-66.7 71.5-66.7-71.5c-10.6-10.1-28.1-10.1-38.8 0l-66 70.7c-9.9 10.6-9.9 27.4 0 38l66 70.7c10.6 10.1 28.1 10.1 38.8 0l66.7-71.5 66.7 71.5c10.6 10.1 28.1 10.1 38.8 0l66-70.7c9.9-10.6 9.9-27.4 0-38z" fill="#e74c3c"/>'
      }
    },

    getStatusSymbol(configKey) {
      const config = this.configStatus[configKey]
      if (config.enabled) {
        // 绿色对勾
        return '<span style="color: #27ae60; font-size: 18px;">✓</span>'
      } else if (config.configured) {
        // 禁用图标
        return '<span style="color: #95a5a6; font-size: 18px;">○</span>'
      } else {
        // 红色叉号
        return '<span style="color: #e74c3c; font-size: 18px;">✗</span>'
      }
    },

    handleDrop(event) {
      event.preventDefault()
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.handleFileSelect({ target: { files } })
      }
    },

    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        const allowedTypes = [
          'application/pdf',
          'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'text/plain',
          'text/markdown',
          'text/x-markdown'
        ]

        if (allowedTypes.includes(file.type) ||
            file.name.match(/\.(pdf|doc|docx|txt|md)$/i)) {
          this.selectedFile = file
          this.documentTitle = file.name.replace(/\.[^/.]+$/, "")
        } else {
          ElMessage.error(this.$t('requirementAnalysis.invalidFileFormatDetail'))
        }
      }
    },

    removeFile() {
      this.selectedFile = null
      this.documentTitle = ''
      this.$refs.fileInput.value = ''
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    async generateFromManualInput() {
      if (!this.canGenerateManual) {
        ElMessage.error(this.$t('requirementAnalysis.fillRequiredInfo'))
        return
      }

      const requirementText = `${this.$t('requirementAnalysis.requirementTitle')}: ${this.manualInput.title}\n\n${this.$t('requirementAnalysis.requirementDescription')}:\n${this.manualInput.description}`

      await this.startGeneration(
        this.manualInput.title,
        requirementText,
        this.manualInput.selectedProject,
        this.globalOutputMode  // 使用全局输出模式
      )
    },

    async generateFromDocument() {
      if (!this.selectedFile || !this.documentTitle) {
        ElMessage.error(this.$t('requirementAnalysis.selectFileAndTitle'))
        return
      }

      try {
        // 首先上传并提取文档内容
        const formData = new FormData()
        formData.append('title', this.documentTitle)
        formData.append('file', this.selectedFile)
        if (this.selectedProject) {
          formData.append('project', this.selectedProject)
        }

        ElMessage.info(this.$t('requirementAnalysis.extractingContent'))
        const uploadResponse = await api.post('/requirement-analysis/documents/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        // 提取文档内容
        const extractResponse = await api.get(`/requirement-analysis/documents/${uploadResponse.data.id}/extract_text/`)
        const extractedText = extractResponse.data.extracted_text

        if (!extractedText || extractedText.trim().length === 0) {
          ElMessage.error(this.$t('requirementAnalysis.extractionFailed'))
          return
        }

        const requirementText = `${this.$t('requirementAnalysis.documentTitle')}: ${this.documentTitle}\n\n${this.$t('requirementAnalysis.documentContent')}:\n${extractedText}`

        await this.startGeneration(
          this.documentTitle,
          requirementText,
          this.selectedProject,
          this.globalOutputMode  // 使用全局输出模式
        )

      } catch (error) {
        console.error(this.$t('requirementAnalysis.documentProcessingFailed'), error)
        ElMessage.error(this.$t('requirementAnalysis.documentProcessingFailed') + ': ' + (error.response?.data?.error || error.message))
      }
    },

    async startGeneration(title, requirementText, projectId, outputMode = 'stream') {
      // 在开始生成前，主动刷新token确保生成过程中不会过期
      try {
        const userStore = useUserStore()
        if (userStore.isTokenExpiringSoon && userStore.refreshToken) {
          console.log('Refreshing token before generation...')
          await userStore.refreshAccessToken()
          console.log('Token refreshed successfully, safe to start generation')
        } else if (userStore.accessToken) {
          console.log('Token status is good, no refresh needed')
        }
      } catch (error) {
        console.error('Token refresh failed:', error)
        ElMessage.error(this.$t('requirementAnalysis.tokenRefreshFailed'))
        return
      }

      this.isGenerating = true
      this.currentStep = 1
      // 根据输出模式设置初始提示
      console.log('🚀 startGeneration: outputMode =', outputMode, typeof outputMode)
      if (outputMode === 'stream') {
        console.log('✅ 设置流式模式提示')
        this.progressText = 'AI正在思考中，请稍候...'
      } else {
        console.log('❌ 设置非流式模式提示, outputMode:', outputMode)
        this.progressText = this.$t('requirementAnalysis.creatingTask')
      }
      console.log('📝 progressText 设置为:', this.progressText)
      // 强制Vue更新DOM
      this.$nextTick(() => {
        console.log('🔄 DOM已更新, progressText:', this.progressText)
      })
      this.streamedContent = ''  // 清空流式内容
      this.finalTestCases = ''  // 清空最终版用例
      this.streamedReviewContent = ''  // 清空评审内容
      this.hasShownCompletionMessage = false  // 重置完成消息标志位
      this.showResults = false  // 隐藏上一次的结果

      try {
        // 调用新的生成API
        const requestData = {
          title: title,
          requirement_text: requirementText,
          use_writer_model: true,
          use_reviewer_model: true,
          output_mode: outputMode  // 添加输出模式参数
        }

        // 如果选择了项目，添加到请求中
        if (projectId) {
          requestData.project = projectId
        }

        const response = await api.post('/requirement-analysis/testcase-generation/generate/', requestData)

        this.currentTaskId = response.data.task_id

        ElMessage.success(this.$t('requirementAnalysis.generateSuccess'))

        // 根据输出模式选择不同的进度获取方式
        console.log('🔄 输出模式:', outputMode, 'globalOutputMode:', this.globalOutputMode)
        if (outputMode === 'stream') {
          console.log('🚀 启动SSE流式输出')
          // 先设置等待AI的提示，让用户知道正在连接
          const waitingText = this.$t('requirementAnalysis.waitingForAI')
          console.log('📝 设置progressText为:', waitingText)
          this.progressText = waitingText
          console.log('✅ progressText已设置为:', this.progressText)
          this.startStreamingProgress()
        } else {
          console.log('🔄 启动轮询模式')
          this.progressText = this.$t('requirementAnalysis.taskCreated')
          this.startPolling()
        }

      } catch (error) {
        console.error(this.$t('requirementAnalysis.createTaskFailed'), error)
        ElMessage.error(this.$t('requirementAnalysis.createTaskFailed') + ': ' + (error.response?.data?.error || error.message))
        this.isGenerating = false
      }
    },

    startStreamingProgress(retryCount = 0) {
      // 使用SSE进行流式进度获取
      // 注意：EventSource不使用axios代理，需要直接指向后端服务器
      // 完整的URL路径: /api/requirement-analysis/testcase-generation/{task_id}/stream_progress/

      // 立即设置等待提示，让用户知道正在连接AI
      console.log('📝 startStreamingProgress: 设置waitingForAI提示')
      this.progressText = 'AI正在思考中，请稍候...'
      console.log('✅ startStreamingProgress: progressText已设置为:', this.progressText)

      // 动态获取后端URL：使用当前页面的协议和主机名，端口改为8000
      // 这样无论通过 localhost、127.0.0.1 还是 IP 地址访问，都能正确连接后端
      const currentOrigin = window.location.origin  // 如 http://192.168.10.107:3000
      const url = new URL(currentOrigin)
      // 将端口改为后端端口 8000
      const baseUrl = `${url.protocol}//${url.hostname}:8000`
      const apiUrl = `${baseUrl}/api/requirement-analysis/testcase-generation/${this.currentTaskId}/stream_progress/`

      console.log('SSE连接URL:', apiUrl, '重试次数:', retryCount)

      // 创建EventSource（不支持自定义headers，使用withCredentials发送cookie）
      this.eventSource = new EventSource(apiUrl, { withCredentials: true })

      // 监听连接打开事件
      this.eventSource.onopen = (event) => {
        console.log('✅ SSE连接已打开', event)
        // 连接成功，重置重试计数
        this.sseRetryCount = 0
      }

      this.eventSource.onmessage = (event) => {
        console.log('📨 收到SSE消息:', event.data)

        try {
          const data = JSON.parse(event.data)
          console.log('📦 解析后的数据:', data)

          if (data.type === 'connected') {
            // SSE连接已建立，更新状态提示用户
            console.log('✅ SSE连接已建立:', data.message)
            // 保持waitingForAI提示，不覆盖
          } else if (data.type === 'progress') {
            // Update progress status - 只更新步骤，不覆盖提示文本
            if (data.status === 'generating') {
              this.currentStep = 2
              // 只有在已经开始接收内容后才更新进度文本
              if (this.streamedContent) {
                this.progressText = `${this.$t('requirementAnalysis.statusGenerating')} ${data.progress}%`
              }
            } else if (data.status === 'reviewing') {
              this.currentStep = 3
              if (this.streamedReviewContent) {
                this.progressText = `${this.$t('requirementAnalysis.statusReviewing')} ${data.progress}%`
              }
            } else if (data.status === 'revising') {
              this.currentStep = 3
              if (this.finalTestCases) {
                this.progressText = `${this.$t('requirementAnalysis.statusRevising')} ${data.progress}%`
              }
            }
          } else if (data.type === 'content') {
            // Real-time streaming content (case generation)
            console.log('✍️ Received streaming content:', data.content.length, 'characters')
            this.streamedContent += data.content
            this.currentStep = 2
            this.progressText = this.$t('requirementAnalysis.statusGenerating')
          } else if (data.type === 'review_content') {
            // Real-time review content
            console.log('📝 Received review content:', data.content.length, 'characters', 'Total length:', this.streamedReviewContent.length + data.content.length)
            this.streamedReviewContent += data.content
            this.currentStep = 3
            this.progressText = this.$t('requirementAnalysis.statusReviewing')
          } else if (data.type === 'final_content') {
            // Real-time final test cases content
            console.log('🎯 Received final cases content:', data.content.length, 'characters', 'Total length:', this.finalTestCases.length + data.content.length)
            this.finalTestCases += data.content
            this.currentStep = 3
            this.progressText = '🎯 ' + this.$t('requirementAnalysis.statusRevising')
          } else if (data.type === 'status') {
            // Final status
            console.log('📊 Received status update:', data.status)
            if (data.status === 'completed') {
              this.progressText = this.$t('requirementAnalysis.statusCompleted')
              // Fetch final result
              this.fetchFinalResult()
            } else if (data.status === 'failed') {
              this.progressText = this.$t('requirementAnalysis.statusFailed')
              this.handleGenerationError()
            }
          } else if (data.type === 'done') {
            // 流式结束，立即关闭EventSource，获取最终结果
            console.log('✅ 流式传输完成')
            if (this.eventSource) {
              console.log('🔒 关闭SSE连接')
              this.eventSource.close()
              this.eventSource = null
            }
            this.fetchFinalResult()
          }
        } catch (e) {
          console.error('❌ 解析SSE数据失败:', e, '原始数据:', event.data)
        }
      }

      this.eventSource.onerror = (error) => {
        console.log('⚠️ SSE连接事件:', error)

        // 如果EventSource已经被关闭（在onmessage中关闭的），不做任何处理
        if (!this.eventSource) {
          console.log('ℹ️ EventSource已关闭，忽略错误事件')
          return
        }

        console.log('EventSource状态:', {
          readyState: this.eventSource.readyState,
          url: this.eventSource.url
        })

        // 如果任务已经完成或不在生成中，不要降级
        if (this.showResults || !this.isGenerating) {
          console.log('ℹ️ 任务已完成或不在生成中，不降级到轮询')
          // 清理EventSource
          if (this.eventSource) {
            this.eventSource.close()
            this.eventSource = null
          }
          return
        }

        // readyState=2表示连接已关闭，readyState=0表示连接中断
        // EventSource会自动重连（readyState=0），除非是致命错误（readyState=2）
        if (this.eventSource.readyState === 2) {
          console.error('❌ SSE连接永久关闭，降级到轮询模式')
          this.eventSource.close()
          this.eventSource = null
          ElMessage.warning(this.$t('requirementAnalysis.streamConnectionInterrupted'))
          this.startPolling()
        } else if (this.eventSource.readyState === 0) {
          // EventSource正在重连，等待一段时间后检查
          console.log('🔄 SSE正在重连...')
          setTimeout(() => {
            // 如果5秒后还是断开状态，降级到轮询
            if (this.eventSource && this.eventSource.readyState === 0) {
              console.error('❌ SSE重连失败，降级到轮询模式')
              this.eventSource.close()
              this.eventSource = null
              ElMessage.warning(this.$t('requirementAnalysis.streamConnectionInterrupted'))
              this.startPolling()
            }
          }, 5000)
        }
      }
    },

    async fetchFinalResult() {
      try {
        // 修复URL：去掉多余的/api/前缀（axios baseURL已经包含/api）
        const response = await api.get(`/requirement-analysis/testcase-generation/${this.currentTaskId}/progress/`)
        const task = response.data

        this.generationResult = task
        this.showResults = true
        this.isGenerating = false

        // 设置第4步为完成状态
        this.currentStep = 4

        // 设置最终版用例（如果还没有通过流式接收完整）
        if (task.final_test_cases) {
          console.log('📝 Getting final cases from task object')
          // 无论this.finalTestCases是否已有值，都用最新的final_test_cases覆盖
          // 这样确保完整输出模式下也能正确显示最终版用例
          this.finalTestCases = task.final_test_cases
        }

        // 如果评审内容为空，从task对象中获取
        if (!this.streamedReviewContent && task.review_feedback) {
          console.log('📝 Getting review content from task object')
          this.streamedReviewContent = task.review_feedback
        }

        // 如果生成内容为空，从task对象中获取
        if (!this.streamedContent && task.generated_test_cases) {
          console.log('✍️ Getting generated content from task object')
          this.streamedContent = task.generated_test_cases
        }

        if (this.eventSource) {
          this.eventSource.close()
          this.eventSource = null
        }

        // Only show completion message once
        if (!this.hasShownCompletionMessage) {
          ElMessage.success(this.$t('requirementAnalysis.generateCompleteSuccess'))
          this.hasShownCompletionMessage = true
        }
      } catch (error) {
        console.error('Failed to fetch final result:', error)
        ElMessage.error(this.$t('requirementAnalysis.fetchResultFailed'))
        this.isGenerating = false
      }
    },

    handleGenerationError() {
      this.isGenerating = false
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
      }
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },

    startPolling() {
      this.pollInterval = setInterval(async () => {
        try {
          // 修复URL：去掉多余的/api/前缀（axios baseURL已经包含/api）
          const response = await api.get(`/requirement-analysis/testcase-generation/${this.currentTaskId}/progress/`)
          const task = response.data

          console.log(`${this.$t('requirementAnalysis.taskStatus')}: ${task.status}, ${this.$t('requirementAnalysis.progress')}: ${task.progress}%`)

          // 更新进度显示
          if (task.status === 'generating') {
            this.currentStep = 2
            this.progressText = this.$t('requirementAnalysis.statusGenerating')
          } else if (task.status === 'reviewing') {
            this.currentStep = 3
            this.progressText = this.$t('requirementAnalysis.statusReviewing')
          } else if (task.status === 'completed') {
            this.currentStep = 4
            this.progressText = this.$t('requirementAnalysis.statusCompleted')

            // 任务完成，显示结果
            this.generationResult = task
            this.showResults = true
            this.isGenerating = false

            // 设置显示内容（完整输出模式下需要）
            if (task.generated_test_cases) {
              console.log('✍️ Polling mode - Setting generated content')
              this.streamedContent = task.generated_test_cases
            }
            if (task.review_feedback) {
              console.log('📝 Polling mode - Setting review content')
              this.streamedReviewContent = task.review_feedback
            }
            if (task.final_test_cases) {
              console.log('🎯 Polling mode - Setting final test cases')
              this.finalTestCases = task.final_test_cases
            }

            clearInterval(this.pollInterval)
            this.pollInterval = null

            // 只显示一次完成消息
            if (!this.hasShownCompletionMessage) {
              ElMessage.success(this.$t('requirementAnalysis.generateCompleteSuccess'))
              this.hasShownCompletionMessage = true
            }
            return
          } else if (task.status === 'failed') {
            this.progressText = this.$t('requirementAnalysis.statusFailed')
            this.isGenerating = false

            clearInterval(this.pollInterval)
            this.pollInterval = null

            ElMessage.error(this.$t('requirementAnalysis.generateFailed') + ': ' + (task.error_message || this.$t('requirementAnalysis.unknownError')))
            return
          }

        } catch (error) {
          console.error(this.$t('requirementAnalysis.checkProgressFailed'), error)
          // 继续轮询，不中断
        }
      }, 3000) // 每3秒检查一次
    },

    async cancelGeneration() {
      // 停止前端轮询
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }

      // 如果有任务ID，调用后端API取消任务
      if (this.currentTaskId) {
        try {
          await api.post(`/requirement-analysis/testcase-generation/${this.currentTaskId}/cancel/`)
          ElMessage.success(this.$t('requirementAnalysis.generationCancelled'))
        } catch (error) {
          console.error('取消任务失败:', error)
          ElMessage.error(error.response?.data?.error || '取消任务失败')
        }
      }

      // 重置前端状态
      this.isGenerating = false
      this.currentTaskId = null
      this.streamedContent = ''
      this.streamedReviewContent = ''
      this.finalTestCases = ''
    },

    // 下载测试用例为xlsx文件
    async downloadTestCases() {
      try {
        // 解析最终测试用例内容
        const finalTestCases = this.generationResult.final_test_cases;
        const taskId = this.generationResult.task_id;

        // 创建工作簿
        const workbook = XLSX.utils.book_new();

        // 过滤掉总结和建议部分，只保留测试用例内容
        const filteredContent = this.filterTestCasesOnly(finalTestCases);

        // 尝试解析表格格式的测试用例（参考AutoGenTestCase的做法）
        const tableFormat = this.parseTableFormat(filteredContent);

        let worksheetData = [];

        if (tableFormat.length > 0) {
          // 如果解析到表格格式，直接使用，但要确保表头正确
          worksheetData = tableFormat;

          // 检查并修正表头
          if (worksheetData.length > 0) {
            const header = worksheetData[0];
            for (let i = 0; i < header.length; i++) {
              if (header[i] && header[i].includes('测试步骤')) {
                header[i] = header[i].replace('测试步骤', '操作步骤');
              }
              if (header[i] && header[i].includes('Test Steps')) {
                header[i] = header[i].replace('Test Steps', '操作步骤');
              }
            }
          }
        } else {
          // 否则尝试解析结构化格式
          worksheetData = this.parseStructuredFormat(filteredContent);
        }

        // 将所有单元格中的<br>标签转换为换行符
        worksheetData = worksheetData.map(row =>
          row.map(cell => this.convertBrToNewline(cell))
        );

        // 创建工作表
        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

        // 设置列宽
        const colWidths = [
          { wch: 15 }, // 测试用例编号
          { wch: 30 }, // 测试场景
          { wch: 25 }, // 前置条件
          { wch: 40 }, // 操作步骤
          { wch: 30 }, // 预期结果
          { wch: 10 }  // 优先级
        ];
        worksheet['!cols'] = colWidths;

        // 设置表头样式（加粗）
        if (worksheetData.length > 1) {
          for (let col = 0; col < Math.min(6, worksheetData[0].length); col++) {
            const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col });
            if (!worksheet[cellAddress]) continue;
            worksheet[cellAddress].s = {
              font: { bold: true },
              alignment: { horizontal: 'center', vertical: 'center', wrapText: true }
            };
          }

          // 设置自动换行
          for (let row = 1; row < worksheetData.length; row++) {
            for (let col = 0; col < Math.min(6, worksheetData[row].length); col++) {
              const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
              if (worksheet[cellAddress]) {
                worksheet[cellAddress].s = {
                  alignment: { vertical: 'top', wrapText: true }
                };
              }
            }
          }
        }

        // 将工作表添加到工作簿
        XLSX.utils.book_append_sheet(workbook, worksheet, this.$t('requirementAnalysis.testCaseSheetName'));

        // 生成文件名（包含任务ID和日期）
        const fileName = this.$t('requirementAnalysis.excelFileName', { taskId: taskId, date: new Date().toISOString().slice(0, 10) });

        // 导出文件
        XLSX.writeFile(workbook, fileName);

        ElMessage.success(this.$t('requirementAnalysis.downloadSuccess'));
      } catch (error) {
        console.error(this.$t('requirementAnalysis.downloadFailed'), error);
        ElMessage.error(this.$t('requirementAnalysis.downloadFailed') + ': ' + (error.message || this.$t('requirementAnalysis.unknownError')));
      }
    },

    // 保存到用例记录
    async saveToTestCaseRecords() {
      try {
        // 调用后端API保存到记录
        const response = await api.post(`/requirement-analysis/testcase-generation/${this.generationResult.task_id}/save_to_records/`)

        if (response.data.already_saved) {
          ElMessage.info(this.$t('requirementAnalysis.alreadySaved'))
        } else {
          const importedCount = response.data.imported_count || 0
          ElMessage.success(`测试用例已保存！已导入 ${importedCount} 条测试用例到测试用例管理系统`)
        }

        // 不跳转，留在当前页面
        // this.$router.push('/generated-testcases')
      } catch (error) {
        console.error(this.$t('requirementAnalysis.saveFailed'), error)
        ElMessage.error(this.$t('requirementAnalysis.saveFailed') + ': ' + (error.response?.data?.error || error.message))
      }
    },

    resetGeneration() {
      // 重置生成状态
      this.isGenerating = false;
      this.currentTaskId = null;
      this.progressText = this.$t('requirementAnalysis.preparing');
      this.currentStep = 0;
      this.showResults = false;
      this.generationResult = null;

      // 重置步骤流程状态
      this.resetToStart();

      // 清空流式内容和最终版用例
      this.streamedContent = '';
      this.streamedReviewContent = '';
      this.finalTestCases = '';

      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    },

    // 格式化日期时间
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      const date = new Date(dateTimeString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },

    // 格式化Markdown为HTML（简化版）
    formatMarkdown(content) {
      if (!content) return '';

      // 先去除"新增"标记，在markdown转换之前处理
      // 这样可以避免markdown转换后无法匹配的问题
      let html = content
          .replace(/\*\*新增\*\*-/g, '')  // **新增**-xxx -> xxx (保留xxx的原有格式)
          .replace(/新增-/g, '');  // 新增-xxx -> xxx (保留xxx的原有格式)

      // 转义HTML特殊字符
      html = html
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;');

      // 转换Markdown语法
      // 标题 #
      html = html.replace(/^#{6}\s+(.+)$/gm, '<h6>$1</h6>');
      html = html.replace(/^#{5}\s+(.+)$/gm, '<h5>$1</h5>');
      html = html.replace(/^#{4}\s+(.+)$/gm, '<h4>$1</h4>');
      html = html.replace(/^#{3}\s+(.+)$/gm, '<h3>$1</h3>');
      html = html.replace(/^#{2}\s+(.+)$/gm, '<h2>$1</h2>');
      html = html.replace(/^#{1}\s+(.+)$/gm, '<h1>$1</h1>');

      // 粗体 **text** 或 __text__
      html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

      // 斜体 *text* 或 _text_
      html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
      html = html.replace(/_(.+?)_/g, '<em>$1</em>');

      // 代码块 ```code```
      html = html.replace(/```([\s\S]+?)```/g, '<pre><code>$1</code></pre>');

      // 行内代码 `code`
      html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

      // 换行符转换为<br>
      html = html.replace(/\n/g, '<br>');

      return html;
    },

    // 将HTML的<br>标签转换为换行符（用于Excel导出）
    convertBrToNewline(text) {
      if (!text) return '';
      return text.replace(/<br\s*\/?>/gi, '\n');
    },

    // 过滤掉总结和建议部分，只保留测试用例内容
    filterTestCasesOnly(content) {
      if (!content) return '';

      const lines = content.split('\n');
      const filteredLines = [];
      let inTestCaseSection = true;

      for (let line of lines) {
        const trimmedLine = line.trim();

        // 检查是否到了总结或建议部分
        if (trimmedLine.includes('总结') ||
            trimmedLine.includes('建议') ||
            trimmedLine.includes('Summary') ||
            trimmedLine.includes('Recommendation') ||
            trimmedLine.includes('最后') ||
            trimmedLine.includes('补充说明')) {
          inTestCaseSection = false;
          break;
        }

        if (inTestCaseSection) {
          filteredLines.push(line);
        }
      }

      return filteredLines.join('\n');
    },

    // 解析表格格式的测试用例（参考AutoGenTestCase的做法）
    parseTableFormat(content) {
      if (!content) return [];

      const lines = content.split('\n').filter(line => line.trim());
      const worksheetData = [];

      for (let line of lines) {
        const trimmedLine = line.trim();

        // 检查是否是表格行（包含|分隔符，且不是分隔线）
        if (trimmedLine.includes('|') && !trimmedLine.includes('--------')) {
          const cells = trimmedLine.split('|').map(cell => cell.trim()).filter(cell => cell);
          if (cells.length > 1) {
            worksheetData.push(cells);
          }
        }
      }

      return worksheetData;
    },

    // 解析结构化格式的测试用例
    parseStructuredFormat(content) {
      if (!content) return [];

      const lines = content.split('\n').filter(line => line.trim());
      const worksheetData = [];

      // 添加表头
      worksheetData.push([
        this.$t('requirementAnalysis.excelTestCaseNumber'),
        this.$t('requirementAnalysis.excelTestScenario'),
        this.$t('requirementAnalysis.excelPrecondition'),
        this.$t('requirementAnalysis.excelTestSteps'),
        this.$t('requirementAnalysis.excelExpectedResult'),
        this.$t('requirementAnalysis.excelPriority')
      ]);

      let currentTestCase = {};
      let testCaseNumber = 1;
      let i = 0;

      while (i < lines.length) {
        const line = lines[i].trim();

        // 识别测试用例开始标志
        if (line.includes('测试用例') || line.includes('Test Case') ||
            line.match(/^(\d+\.|\*|\-|\d+、)/)) {

          // 如果之前有测试用例数据，先保存
          if (Object.keys(currentTestCase).length > 0) {
            worksheetData.push([
              currentTestCase.number || `TC${testCaseNumber}`,
              currentTestCase.scenario || '',
              currentTestCase.precondition || '',
              currentTestCase.steps || '',
              currentTestCase.expected || '',
              currentTestCase.priority || '中'
            ]);
            testCaseNumber++;
          }

          // 开始新的测试用例
          currentTestCase = {
            number: `TC${testCaseNumber}`,
            scenario: line.replace(/^(\d+\.|\*|\-|\d+、)\s*/, '').replace(/测试用例\d*[:：]?\s*/, ''),
            precondition: '',
            steps: '',
            expected: '',
            priority: '中'
          };
          i++;
        }
        // 识别前置条件
        else if (line.includes('前置条件') || line.includes('前提') ||
            line.includes('Precondition')) {
          let precondition = line.replace(/.*?[:：]\s*/, '');
          // 收集后续的前置条件行
          i++;
          while (i < lines.length) {
            const nextLine = lines[i].trim();
            if (nextLine.includes('测试步骤') || nextLine.includes('操作步骤') ||
                nextLine.includes('Test Steps') || nextLine.includes('步骤') ||
                nextLine.includes('预期结果') || nextLine.includes('Expected') ||
                nextLine.includes('优先级') || nextLine.includes('Priority') ||
                nextLine.includes('测试用例') || nextLine.includes('Test Case') ||
                nextLine.match(/^(\d+\.|\*|\-|\d+、)/)) {
              break;
            }
            if (nextLine) {
              precondition += '\n' + nextLine;
            }
            i++;
          }
          currentTestCase.precondition = precondition;
        }
        // 识别测试步骤
        else if (line.includes('测试步骤') || line.includes('操作步骤') ||
            line.includes('Test Steps') || line.includes('步骤')) {
          let steps = line.replace(/.*?[:：]\s*/, '');
          // 收集后续的步骤行
          i++;
          while (i < lines.length) {
            const nextLine = lines[i].trim();
            if (nextLine.includes('预期结果') || nextLine.includes('Expected') ||
                nextLine.includes('优先级') || nextLine.includes('Priority') ||
                nextLine.includes('测试用例') || nextLine.includes('Test Case') ||
                nextLine.match(/^(\d+\.|\*|\-|\d+、)/)) {
              break;
            }
            if (nextLine) {
              steps += '\n' + nextLine;
            }
            i++;
          }
          currentTestCase.steps = steps;
        }
        // 识别预期结果
        else if (line.includes('预期结果') || line.includes('Expected') ||
            line.includes('期望')) {
          let expected = line.replace(/.*?[:：]\s*/, '');
          // 收集后续的结果行
          i++;
          while (i < lines.length) {
            const nextLine = lines[i].trim();
            if (nextLine.includes('优先级') || nextLine.includes('Priority') ||
                nextLine.includes('测试用例') || nextLine.includes('Test Case') ||
                nextLine.match(/^(\d+\.|\*|\-|\d+、)/)) {
              break;
            }
            if (nextLine) {
              expected += '\n' + nextLine;
            }
            i++;
          }
          currentTestCase.expected = expected;
        }
        // 识别优先级
        else if (line.includes('优先级') || line.includes('Priority')) {
          currentTestCase.priority = line.replace(/.*?[:：]\s*/, '');
          i++;
        }
        // 如果是没有明确标识的行，可能是场景描述的延续
        else if (Object.keys(currentTestCase).length > 0 &&
            !currentTestCase.steps && !currentTestCase.expected &&
            !currentTestCase.precondition) {
          if (currentTestCase.scenario && line.length > 5) {
            currentTestCase.scenario += '\n' + line;
          }
          i++;
        } else {
          i++;
        }
      }

      // 保存最后一个测试用例
      if (Object.keys(currentTestCase).length > 0) {
        worksheetData.push([
          currentTestCase.number || `TC${testCaseNumber}`,
          currentTestCase.scenario || '',
          currentTestCase.precondition || '',
          currentTestCase.steps || '',
          currentTestCase.expected || '',
          currentTestCase.priority || '中'
        ]);
      }

      // 如果没有解析到结构化数据，则按原格式输出
      if (worksheetData.length <= 1) {
        worksheetData.length = 0; // 清空
        worksheetData.push([this.$t('requirementAnalysis.testCaseContent')]);
        content.split('\n').forEach((line, index) => {
          if (line.trim()) {
            worksheetData.push([line.trim()]);
          }
        });
      }

      return worksheetData;
    }
  }
}
</script>

<style scoped>
.requirement-analysis {
  padding: 0;
  max-width: none;
  margin: 0;
  position: relative;
  min-height: calc(100vh - 80px);
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(123, 66, 246, 0.05) 0%, rgba(90, 50, 163, 0.08) 100%);
  border-radius: 16px;
  border: 1px solid rgba(147, 112, 219, 0.1);
}

.page-header h1 {
  font-size: 2rem;
  color: #4a249c;
  margin-bottom: 8px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-header h1::before {
  content: '🤖';
  font-size: 1.8rem;
}

.page-header p {
  color: #6d5d8f;
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
  line-height: 1.6;
}

/* 输出模式设置区域 - 全局 */
.output-mode-section {
  margin-bottom: 24px;
}

.output-mode-card {
  background: linear-gradient(135deg, #ffffff 0%, #faf9ff 100%);
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.12);
  transition: all 0.3s ease;
  margin: 0 auto;
  max-width: 1400px;
}

.output-mode-card:hover {
  box-shadow: 0 8px 24px rgba(147, 112, 219, 0.12);
  transform: translateY(-1px);
}

.output-mode-header {
  margin-bottom: 20px;
}

.output-mode-card h3 {
  font-size: 1.15rem;
  color: #4a249c;
  margin: 0 0 8px 0;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 0.3px;
}

.mode-section-desc {
  color: #6d5d8f;
  font-size: 0.95rem;
  margin: 0 0 20px 0;
  line-height: 1.5;
  font-weight: 400;
  opacity: 0.85;
  max-width: 800px;
}

/* 配置引导弹出窗口 */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(15, 23, 42, 0.6) !important;
  backdrop-filter: blur(4px);
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
  padding: 20px;
  margin: 0 !important;
  opacity: 1 !important;
}

.guide-config-modal {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
  border-radius: 24px;
  padding: 36px;
  max-width: 850px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.8);
  position: relative;
  flex-shrink: 0;
  margin: auto;
  opacity: 1 !important;
}

.guide-config-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px 24px 0 0;
}

.guide-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.guide-icon {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  filter: drop-shadow(0 4px 8px rgba(245, 158, 11, 0.2));
}

.guide-title h2 {
  font-size: 1.6rem;
  color: #4a249c;
  margin: 0 0 6px 0;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.guide-title p {
  color: #6d5d8f;
  font-size: 0.95rem;
  margin: 0;
  font-weight: 400;
}

.config-groups {
  margin-bottom: 24px;
}

.config-group {
  margin-bottom: 20px;
}

.group-label {
  font-size: 0.85rem;
  color: #6d5d8f;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.config-items-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.config-item-inline {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
  font-weight: 500;
}

.config-item-inline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 12px 0 0 12px;
}

.config-item-inline.optional {
  opacity: 0.75;
}

/* 根据状态设置背景色和样式 */
.config-item-inline.status-enabled {
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.9) 0%, rgba(220, 252, 231, 0.6) 100%);
  border-color: rgba(34, 197, 94, 0.2);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1);
}

.config-item-inline.status-enabled::before {
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
}

.config-item-inline.status-disabled {
  background: linear-gradient(135deg, rgba(254, 249, 195, 0.9) 0%, rgba(254, 240, 138, 0.6) 100%);
  border-color: rgba(234, 179, 8, 0.2);
  box-shadow: 0 4px 12px rgba(234, 179, 8, 0.1);
}

.config-item-inline.status-disabled::before {
  background: linear-gradient(180deg, #eab308 0%, #ca8a04 100%);
}

.config-item-inline.status-unconfigured {
  background: linear-gradient(135deg, rgba(254, 242, 242, 0.9) 0%, rgba(254, 226, 226, 0.6) 100%);
  border-color: rgba(239, 68, 68, 0.2);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
}

.config-item-inline.status-unconfigured::before {
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
}

.status-symbol {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  font-size: 20px;
}

.config-label {
  font-size: 0.95rem;
  color: #4a249c;
  font-weight: 600;
  flex-shrink: 0;
}

.config-name {
  font-size: 0.85rem;
  color: #6d5d8f;
  margin-left: 4px;
  font-weight: 500;
}

.status-text {
  margin-left: auto;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  background: #ef4444;
  color: white;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.2);
}

.status-text.warning {
  background: #eab308;
  box-shadow: 0 2px 6px rgba(234, 179, 8, 0.2);
}

.guide-actions {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 12px;
  margin-top: 30px;
  width: 100%;
}

.guide-actions button {
  flex: none !important;
  width: 240px !important;
  height: 50px !important;
  padding: 0 24px !important;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center;
  white-space: nowrap;
  opacity: 1 !important;
  cursor: pointer;
  box-sizing: border-box !important;
}

.guide-actions .generate-manual-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: 2px solid transparent !important;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.guide-actions .skip-action {
  font-size: 0.85rem;
  color: #6d5d8f;
  cursor: pointer;
  text-decoration: none;
  padding: 4px 8px;
  transition: color 0.3s;
}

.guide-actions .skip-action:hover {
  color: #4a249c;
  text-decoration: underline;
}


.manual-input-card, .upload-card {
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.06);
  border: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.25s ease;
  margin: 0 auto 24px;
  max-width: 1400px;
}

.manual-input-card:hover, .upload-card:hover {
  box-shadow: 0 6px 20px rgba(147, 112, 219, 0.1);
  transform: translateY(-1px);
}

.manual-input-card h2, .upload-card h2 {
  color: #4a249c;
  margin-bottom: 20px;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 0.3px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #475569;
  font-size: 0.9rem;
  letter-spacing: 0.2px;
}

.mode-option {
  position: relative;
  cursor: pointer;
  display: flex;
}

.mode-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.mode-content {
  border: 2px solid rgba(123, 66, 246, 0.15);
  border-radius: 20px;
  padding: 60px 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 4px 20px rgba(123, 66, 246, 0.08);
  min-height: 200px;
}

.mode-option:hover .mode-content {
  border-color: rgba(123, 66, 246, 0.4);
  background: linear-gradient(145deg, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.98) 100%);
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(123, 66, 246, 0.15);
}

.mode-option.active .mode-content {
  border-color: #7b42f6;
  background: linear-gradient(145deg, rgba(123, 66, 246, 0.08) 0%, rgba(123, 66, 246, 0.04) 100%);
  box-shadow: 0 4px 24px rgba(123, 66, 246, 0.2);
}

.mode-title {
  font-size: 1.35rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.mode-desc {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.6;
  text-align: center;
}

.mode-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.mode-icon svg {
  width: 20px;
  height: 20px;
}

.stream-icon {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.08) 100%);
  color: #8b5cf6;
}

.complete-icon {
  background: linear-gradient(135deg, rgba(123, 66, 246, 0.15) 0%, rgba(123, 66, 246, 0.08) 100%);
  color: #7b42f6;
}

.mode-option.active .stream-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.mode-option.active .complete-icon {
  background: linear-gradient(135deg, #7b42f6 0%, #6d28d9 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
}

.mode-option.active .mode-title {
  color: #7b42f6;
}

.mode-option.active .mode-desc {
  color: #475569;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.25s ease;
  background: #ffffff;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #7b42f6;
  box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
  background: #ffffff;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
  min-height: 180px;
  line-height: 1.6;
  padding: 14px;
}

.textarea-wrapper {
  position: relative;
}

.textarea-wrapper .form-textarea {
  padding-bottom: 40px;
}

.char-count {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 0.75rem;
  color: #94a3b8;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  transition: all 0.2s ease;
  pointer-events: none;
  backdrop-filter: blur(4px);
}

.char-count:hover {
  color: #64748b;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.generate-manual-btn, .generate-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #6d28d9 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.25s ease;
  width: 100%;
  margin-top: 16px;
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.3px;
}

.generate-manual-btn:hover:not(:disabled), .generate-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #8b5cf6 0%, #7b42f6 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(109, 40, 217, 0.35);
}

.generate-manual-btn:active:not(:disabled), .generate-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(109, 40, 217, 0.2);
}

.generate-manual-btn:disabled, .generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(109, 40, 217, 0.15);
}

.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 24px 0;
  position: relative;
  height: 32px;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e2e8f0 50%, transparent 100%);
}

.divider span {
  background: white;
  padding: 6px 18px;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  position: relative;
  z-index: 1;
  transition: all 0.2s ease;
}

.divider span:hover {
  border-color: #cbd5e1;
  color: #475569;
}

.upload-section-title {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #475569;
  font-size: 0.9rem;
  letter-spacing: 0.2px;
  text-align: left;
}

.upload-area {
  border: none;
  border-radius: 0;
  padding: 0;
  text-align: center;
  transition: all 0.25s ease;
  margin-bottom: 24px;
  background: transparent;
}

.upload-area.drag-over {
  border: 2px dashed #7b42f6;
  background: rgba(123, 66, 246, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.upload-placeholder {
  color: #64748b;
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  display: block;
  opacity: 0.7;
}

.upload-hint {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-top: 4px;
}

.select-file-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #6d28d9 100%);
  color: white;
  border: none;
  padding: 10px 22px;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 14px;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(109, 40, 217, 0.2);
  font-size: 0.95rem;
  font-weight: 500;
}

.select-file-btn:hover {
  background: linear-gradient(135deg, #8b5cf6 0%, #7b42f6 100%);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3);
  transform: translateY(-1px);
}

.file-selected {
  padding: 24px 28px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
  border-radius: 16px;
  border: 2px solid rgba(123, 66, 246, 0.15);
  box-shadow: 0 4px 20px rgba(123, 66, 246, 0.08);
  transition: all 0.3s ease;
}

.file-selected:hover {
  border-color: rgba(123, 66, 246, 0.25);
  box-shadow: 0 6px 24px rgba(123, 66, 246, 0.12);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(123, 66, 246, 0.08) 100%);
  border-radius: 12px;
  flex-shrink: 0;
}

.file-icon-svg {
  width: 28px;
  height: 28px;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  margin: 0;
  font-size: 0.95rem;
  color: #1a1a2e;
  line-height: 1.4;
  text-align: left;
}

.file-size {
  color: #8b5cf6;
  font-size: 0.875rem;
  margin: 6px 0 0 0;
  font-weight: 500;
}

.remove-file {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.25s ease;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 0;
}

.remove-file svg {
  width: 18px;
  height: 18px;
}

.remove-file:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  transform: rotate(90deg);
}

.remove-file:hover {
  color: #ef4444;
  background: #fef2f2;
}

.generation-progress {
  margin: 0;
  padding: 16px 24px;
  background: #f5f0ff;
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.progress-card {
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
  border-radius: 16px;
  padding: 32px 40px;
  box-shadow: 0 4px 20px rgba(123, 66, 246, 0.08);
  border: 1px solid rgba(123, 66, 246, 0.08);
  text-align: center;
  margin: 0 auto;
  max-width: 1400px;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 96px);
  justify-content: center;
  align-items: center;
}

.progress-card h3 {
  color: #1a1a2e;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 1.5rem;
  font-weight: 600;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.progress-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  padding: 16px 28px;
  background: #faf8ff;
  border-radius: 12px;
  border: 1px solid rgba(123, 66, 246, 0.1);
  min-width: 280px;
}

.progress-item.mode-item {
  background: rgba(123, 66, 246, 0.06);
  border: 1px solid rgba(123, 66, 246, 0.12);
}

.progress-item .label {
  font-size: 0.85rem;
  color: #8b7aa0;
  font-weight: 500;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.progress-item .value {
  font-weight: 600;
  color: #7b42f6;
  font-size: 1rem;
}

.progress-item .value.mode-value {
  font-size: 0.95rem;
}

/* 流式内容显示区域 */
.stream-content-display {
  margin: 18px -40px;
  border: none;
  border-radius: 0;
  overflow: hidden;
  background: #f5f3ff;
  width: calc(100% + 80px);
}

.stream-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: linear-gradient(135deg, #ede9fe 0%, #f5f3ff 100%);
  border-bottom: 1px solid #ddd6fe;
  transition: background 0.2s ease;
}

.stream-header:hover {
  background: linear-gradient(135deg, #ddd6fe 0%, #ede9fe 100%);
}

.stream-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.expand-icon {
  font-size: 0.8rem;
  color: #7c3aed;
  transition: transform 0.2s ease;
  user-select: none;
}

.stream-title {
  font-weight: 600;
  color: #5b21b6;
  font-size: 0.95rem;
}

.stream-status {
  font-size: 0.8rem;
  color: #7c3aed;
  background: #ede9fe;
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid #ddd6fe;
}

.stream-content {
  max-height: none;
  overflow-y: visible;
  padding: 20px 24px;
  text-align: left;
  background: #f5f3ff;
  font-size: 0.95rem;
  line-height: 1.7;
  color: #334155;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.stream-content::-webkit-scrollbar {
  width: 6px;
}

.stream-content::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.stream-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.stream-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 最终版用例特殊样式 */
.stream-content.final-testcases {
  background: #f5f3ff;
  border: none;
  border-radius: 0;
  margin: 0;
  padding: 20px 24px;
}

/* 流式输出指示器 */
.streaming-indicator {
  font-size: 0.85em;
  margin-left: 8px;
  color: #4CAF50;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.stream-content h1,
.stream-content h2,
.stream-content h3,
.stream-content h4,
.stream-content h5,
.stream-content h6 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #4a249c;
  font-weight: 600;
}

.stream-content code {
  background: #f1f3f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.85em;
}

.stream-content pre {
  background: #f1f3f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 10px 0;
}

.stream-content pre code {
  background: none;
  padding: 0;
}

.progress-steps {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 0;
  margin-top: 60px;
  margin-bottom: 48px;
  flex-wrap: nowrap;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  opacity: 0.4;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  width: 100px;
}

.step.active {
  opacity: 1;
}

.step-number {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  color: #94a3b8;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.step.active .step-number {
  background: linear-gradient(135deg, #7b42f6 0%, #6d28d9 100%);
  border-color: #7b42f6;
  color: white;
  box-shadow: 0 4px 16px rgba(123, 66, 246, 0.35);
}

.step-text {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: center;
}

.step.active .step-text {
  color: #7b42f6;
  font-weight: 600;
}

/* 步骤之间的连接线 */
.step-line {
  width: 60px;
  height: 2px;
  background: #e2e8f0;
  margin-top: 22px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.step-line.active {
  background: linear-gradient(90deg, #7b42f6 0%, #9f7aea 100%);
}

.cancel-generation-btn-inline {
  background: white;
  color: #ef4444;
  border: 1.5px solid #ef4444;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.25s ease;
  margin-left: 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.cancel-generation-btn-inline::before {
  content: '✕';
  font-size: 0.75rem;
}

.cancel-generation-btn-inline:hover {
  background: #ef4444;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* 完整输出模式提示区域 */
.complete-mode-notice {
  padding: 16px 0;
  margin: 16px 0;
  text-align: center;
}

/* 完整输出模式下的取消按钮容器 */
.complete-mode-cancel {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.notice-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #7b42f6;
  margin-bottom: 8px;
}

.notice-desc {
  font-size: 0.95rem;
  color: #6b5b7a;
  line-height: 1.6;
}

.completion-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.completion-actions .new-generation-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #6d28d9 100%);
  color: white;
  border: none;
  padding: 14px 40px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(123, 66, 246, 0.25);
}

.completion-actions .new-generation-btn:hover {
  background: linear-gradient(135deg, #9f7aea 0%, #7b42f6 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(123, 66, 246, 0.35);
}

.generation-result {
  margin: 40px 0;
}

.result-header {
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(123, 66, 246, 0.08);
  border: 1px solid rgba(123, 66, 246, 0.1);
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.result-header h2 {
  color: #27ae60;
  margin: 0;
}

.result-summary {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.summary-item {
  color: #6d5d8f;
  font-size: 0.9rem;
}

.new-generation-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.generated-testcases-section, .review-feedback-section, .final-testcases-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
  margin-bottom: 20px;
}

.generated-testcases-section h3, .review-feedback-section h3, .final-testcases-section h3 {
  color: #4a249c;
  margin-bottom: 20px;
}

.testcase-content, .review-content {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
  border-left: 4px solid #3498db;
}

.testcase-content pre, .review-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .progress-info, .result-summary {
    flex-direction: column;
    gap: 10px;
  }

  .progress-steps {
    gap: 0;
    flex-wrap: wrap;
  }

  .step {
    width: 80px;
  }

  .step-line {
    width: 30px;
  }
}

.actions-section {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
  flex-wrap: wrap;
}

.download-btn, .save-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.download-btn {
  background-color: #1abc9c;
  color: white;
}

.download-btn:hover {
  background-color: #16a085;
}

.save-btn {
  background-color: #3498db;
  color: white;
}

.save-btn:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .actions-section {
    flex-direction: column;
    align-items: center;
  }

  .download-btn, .save-btn {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
}

/* 纵向步骤指示器样式 */
.steps-indicator-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
  min-width: 100px;
  align-self: center;
}

.steps-indicator-vertical .step-indicator-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.steps-indicator-vertical .step-indicator-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 1rem;
  color: #8c8c8c;
  transition: all 0.3s ease;
}

.steps-indicator-vertical .step-indicator-item.active .step-indicator-number {
  background: #7b42f6;
  color: white;
}

.steps-indicator-vertical .step-indicator-text {
  font-size: 0.875rem;
  color: #8c8c8c;
  font-weight: 400;
  transition: all 0.3s ease;
}

.steps-indicator-vertical .step-indicator-item.active .step-indicator-text {
  color: #7b42f6;
  font-weight: 500;
}

.step-indicator-line-vertical {
  width: 2px;
  height: 28px;
  background: rgba(123, 66, 246, 0.2);
  transition: all 0.3s ease;
}

.step-indicator-line-vertical.active {
  background: #7b42f6;
}

/* 顶部步骤指示器样式 - 与页面融为一体 */
.steps-indicator-top {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
  margin: 0;
  padding: 32px 0 24px 0;
  background: #f5f0ff;
  border: none;
  box-shadow: none;
  width: 100%;
}

.steps-indicator-top .step-indicator-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: default;
  width: 120px;
}

.steps-indicator-top .step-indicator-item.clickable {
  cursor: pointer;
}

.steps-indicator-top .step-indicator-item.clickable:hover .step-indicator-number {
  background: rgba(123, 66, 246, 0.1);
  transform: scale(1.08);
}

.steps-indicator-top .step-indicator-number {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: transparent;
  border: 2px solid rgba(123, 66, 246, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  color: #9ca3af;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.steps-indicator-top .step-indicator-item.active .step-indicator-number {
  background: #7b42f6;
  border-color: #7b42f6;
  color: white;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
}

.steps-indicator-top .step-indicator-text {
  font-size: 0.85rem;
  color: #9ca3af;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: center;
}

.steps-indicator-top .step-indicator-item.active .step-indicator-text {
  color: #7b42f6;
  font-weight: 600;
}

.step-indicator-line-horizontal {
  width: 80px;
  height: 2px;
  background: rgba(123, 66, 246, 0.15);
  transition: all 0.3s ease;
  margin-top: 22px;
  flex-shrink: 0;
}

.step-indicator-line-horizontal.active {
  background: linear-gradient(90deg, #7b42f6 0%, rgba(123, 66, 246, 0.3) 100%);
}

/* 欢迎界面样式 */
.welcome-section {
  margin: 0;
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: 0;
  background: #f5f0ff;
}

.welcome-card {
  background: transparent;
  border-radius: 0;
  padding: 60px 60px;
  text-align: center;
  box-shadow: none;
  border: none;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

.welcome-icon {
  font-size: 4rem;
  opacity: 0.9;
}

.welcome-card h2 {
  color: #1a1a2e;
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
}

.welcome-card p {
  color: #8c8c8c;
  font-size: 0.875rem;
  margin-bottom: 32px;
  line-height: 1.6;
  max-width: none;
  margin-left: auto;
  margin-right: auto;
  white-space: nowrap;
}

.start-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #6938d4 100%);
  color: white;
  border: none;
  padding: 14px 48px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(123, 66, 246, 0.3);
}

.start-btn:hover {
  background: linear-gradient(135deg, #6938d4 0%, #5a2eb8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
}

.start-btn:active {
  background: linear-gradient(135deg, #5a2eb8 0%, #4a249c 100%);
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);
}

/* 步骤卡片样式 */
.step-section {
  margin: 0;
  min-height: calc(100vh - 80px - 96px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: #f5f0ff;
}

.step-card {
  background: transparent;
  border-radius: 0;
  padding: 40px 60px;
  box-shadow: none;
  border: none;
  margin: 0;
  width: 100%;
  max-width: none;
  display: flex;
  gap: 48px;
}

.step-card-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 0;
}

.step-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.step-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.step-footer {
  display: flex;
  justify-content: center;
  margin-top: 48px;
}

/* 输出模式选择器 */
.output-mode-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.back-btn {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.95) 100%);
  border: 1px solid rgba(123, 66, 246, 0.25);
  color: #7b42f6;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  padding: 12px 28px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(123, 66, 246, 0.1);
}

.back-btn:hover {
  background: linear-gradient(135deg, rgba(123, 66, 246, 0.08) 0%, rgba(123, 66, 246, 0.15) 100%);
  border-color: rgba(123, 66, 246, 0.6);
  color: #6938d4;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.2);
}

.step-header h3 {
  color: #1a1a2e;
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.3px;
}

.step-description {
  color: #8c8c8c;
  font-size: 1rem;
  margin-bottom: 48px;
  text-align: center;
}

/* 输入方式选择器样式 */
.input-method-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.input-method-option {
  padding: 60px 48px;
  border: 2px solid rgba(123, 66, 246, 0.15);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
  text-align: center;
  box-shadow: 0 4px 20px rgba(123, 66, 246, 0.08);
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.input-method-option:hover {
  border-color: rgba(123, 66, 246, 0.4);
  background: linear-gradient(145deg, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.98) 100%);
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(123, 66, 246, 0.15);
}

.input-method-option.active {
  border-color: #7b42f6;
  background: linear-gradient(145deg, rgba(123, 66, 246, 0.08) 0%, rgba(123, 66, 246, 0.04) 100%);
  box-shadow: 0 4px 24px rgba(123, 66, 246, 0.2);
}

.input-method-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
}

.input-method-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.input-method-desc {
  font-size: 0.8rem;
  color: #8c8c8c;
  line-height: 1.5;
}

/* 步骤3的卡片样式调整 */
.manual-input-section,
.upload-section {
  width: 100%;
  display: contents;
}

/* 隐藏之前的输出模式选择器 */
.output-mode-section {
  display: none;
}

/* 隐藏分隔线 */
.divider {
  display: none;
}
</style>

<style>
/* 全局样式：确保弹窗不受任何容器限制 */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  max-height: none !important;
  background: rgba(15, 23, 42, 0.6) !important;
  backdrop-filter: blur(4px);
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
  padding: 20px;
  margin: 0 !important;
  opacity: 1 !important;
  box-sizing: border-box !important;
}

.guide-config-modal {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
  border-radius: 24px;
  padding: 36px;
  max-width: 850px !important;
  width: 100% !important;
  min-width: 300px !important;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.8);
  position: relative;
  flex-shrink: 0;
  margin: auto;
  opacity: 1 !important;
  box-sizing: border-box !important;
}

/* 全局按钮样式 */
.guide-actions {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 12px;
  margin-top: 30px;
  width: 100%;
}

.guide-actions button {
  flex: none !important;
  width: 240px !important;
  height: 50px !important;
  padding: 0 24px !important;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center;
  white-space: nowrap;
  opacity: 1 !important;
  box-sizing: border-box !important;
  cursor: pointer;
}

.guide-actions .generate-manual-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: 2px solid transparent !important;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.guide-actions .skip-action {
  font-size: 0.85rem;
  color: #6d5d8f;
  cursor: pointer;
  text-decoration: none;
  padding: 4px 8px;
  transition: color 0.3s;
}

.guide-actions .skip-action:hover {
  color: #4a249c;
  text-decoration: underline;
}
</style>