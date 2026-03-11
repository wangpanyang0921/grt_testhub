<template>
  <div class="page-container">
    <div class="filter-bar">
      <div class="status-tabs">
        <button
          class="status-tab"
          :class="{ active: selectedStatus === '' }"
          @click="selectedStatus = ''; loadTasks()">
          {{ $t('generatedTestCases.allStatus') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'pending' }"
          @click="selectedStatus = 'pending'; loadTasks()">
          {{ $t('generatedTestCases.statusPending') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'generating' }"
          @click="selectedStatus = 'generating'; loadTasks()">
          {{ $t('generatedTestCases.statusGenerating') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'reviewing' }"
          @click="selectedStatus = 'reviewing'; loadTasks()">
          {{ $t('generatedTestCases.statusReviewing') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'revising' }"
          @click="selectedStatus = 'revising'; loadTasks()">
          {{ $t('generatedTestCases.statusRevising') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'completed' }"
          @click="selectedStatus = 'completed'; loadTasks()">
          {{ $t('generatedTestCases.statusCompleted') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'cancelled' }"
          @click="selectedStatus = 'cancelled'; loadTasks()">
          {{ $t('generatedTestCases.statusCancelled') }}
        </button>
        <button
          class="status-tab"
          :class="{ active: selectedStatus === 'failed' }"
          @click="selectedStatus = 'failed'; loadTasks()">
          {{ $t('generatedTestCases.statusFailed') }}
        </button>
      </div>

      <div class="filter-bar-spacer"></div>

      <el-button
        type="danger"
        class="batch-delete-btn"
        :disabled="selectedTasks.length === 0"
        @click="batchDeleteTasks"
        :loading="isDeleting">
        <el-icon><Delete /></el-icon>
        {{ isDeleting ? $t('generatedTestCases.deleting') : '批量删除' }}
      </el-button>
    </div>

    <div class="card-container">
      <!-- 有数据时显示表格 -->
      <el-table v-if="tasks.length > 0" :data="tasks" v-loading="isLoading" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" header-align="center" align="center" />
        <el-table-column label="序号" width="80" header-align="center" align="center">
          <template #default="{ $index }">
            {{ (pagination.currentPage - 1) * pagination.pageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="title" :label="$t('generatedTestCases.requirement')" min-width="400" show-overflow-tooltip header-align="center" align="left">
          <template #default="{ row }">
            <span
              :class="['requirement-name', { 'clickable': !['completed', 'failed', 'cancelled'].includes(row.status) }]"
              @click="goToGenerationPage(row)"
              :title="['completed', 'failed', 'cancelled'].includes(row.status) ? '' : '点击返回生成页面'">
              {{ row.title }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('generatedTestCases.status')" width="140" header-align="center" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="row.status">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="执行人" width="120" header-align="center" align="center" show-overflow-tooltip />
        <el-table-column prop="created_at" :label="$t('generatedTestCases.generationTime')" width="180" header-align="center" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('generatedTestCases.actions')" width="120" fixed="right" header-align="center" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                v-if="row.status === 'completed'"
                type="primary"
                size="small"
                class="action-btn export-btn"
                @click="exportTestCasesMD(row)">
                <el-icon><Download /></el-icon>
                <span>{{ $t('generatedTestCases.exportMarkdown') }}</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 无数据时显示空状态 -->
      <div v-if="!isLoading && tasks.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon :size="32" color="#bfbfbf"><Document /></el-icon>
        </div>
        <h3>{{ selectedStatus ? '暂无符合条件的数据' : $t('generatedTestCases.noTasks') }}</h3>
        <p v-if="!selectedStatus">{{ $t('generatedTestCases.emptyHint') }}<router-link to="/ai-generation/requirement-analysis">{{ $t('generatedTestCases.aiGeneration') }}</router-link>{{ $t('generatedTestCases.createTask') }}</p>

      </div>

      <div v-if="tasks.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="onPageSizeChange"
          @current-change="goToPage"
        />
      </div>
    </div>

    <!-- 测试用例详情弹窗 -->
    <el-dialog v-model="showTestCaseDetailModal" :title="selectedTestCaseDetail?.title" width="800px">
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.caseNumber') }}</label>
        <span>{{ selectedTestCaseDetail?.case_id }}</span>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.relatedRequirement') }}</label>
        <span>{{ selectedTestCaseDetail?.requirement_name }} ({{ selectedTestCaseDetail?.requirement_id_display }})</span>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.priority') }}</label>
        <span class="priority-tag" :class="selectedTestCaseDetail?.priority?.toLowerCase()">
          {{ selectedTestCaseDetail?.priority_display }}
        </span>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.status') }}</label>
        <span class="status-tag" :class="selectedTestCaseDetail?.status">
          {{ selectedTestCaseDetail?.status_display }}
        </span>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.preconditions') }}</label>
        <p>{{ selectedTestCaseDetail?.precondition }}</p>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.testSteps') }}</label>
        <p class="test-steps" v-html="selectedTestCaseDetail?.test_steps"></p>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.expectedResult') }}</label>
        <p v-html="selectedTestCaseDetail?.expected_result"></p>
      </div>
      <div class="detail-item" v-if="selectedTestCaseDetail?.review_comments">
        <label>{{ $t('generatedTestCases.reviewComments') }}</label>
        <p>{{ selectedTestCaseDetail?.review_comments }}</p>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.generatedAI') }}</label>
        <span>{{ selectedTestCaseDetail?.generated_by_ai }}</span>
      </div>
      <div class="detail-item" v-if="selectedTestCaseDetail?.reviewed_by_ai">
        <label>{{ $t('generatedTestCases.reviewedAI') }}</label>
        <span>{{ selectedTestCaseDetail?.reviewed_by_ai }}</span>
      </div>
      <div class="detail-item">
        <label>{{ $t('generatedTestCases.generatedTime') }}</label>
        <span>{{ formatDateTime(selectedTestCaseDetail?.created_at) }}</span>
      </div>
    </el-dialog>

    <!-- 采纳用例编辑弹框 -->
    <el-dialog v-model="showAdoptModal" :title="$t('generatedTestCases.adoptModalTitle')" width="800px">
      <el-form :model="adoptForm" label-width="140px">
        <el-form-item :label="$t('generatedTestCases.caseTitle')">
          <el-input v-model="adoptForm.title" :placeholder="$t('generatedTestCases.caseTitlePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('generatedTestCases.caseDescription')">
          <el-input v-model="adoptForm.description" type="textarea" :rows="3" :placeholder="$t('generatedTestCases.caseDescriptionPlaceholder')"></el-input>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('generatedTestCases.belongsToProject')" required>
              <el-select v-model="adoptForm.project_id" @change="onAdoptProjectChange" placeholder="$t('generatedTestCases.selectProject')">
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('generatedTestCases.relatedVersion')" required>
              <el-select v-model="adoptForm.version_id" placeholder="$t('generatedTestCases.selectVersion')">
                <el-option v-for="version in availableVersions" :key="version.id" :label="version.name + (version.is_baseline ? $t('generatedTestCases.baseline') : '')" :value="version.id"></el-option>
              </el-select>
              <div class="form-hint">
                {{ adoptForm.project_id ?
                    $t('generatedTestCases.showingProjectVersions', { project: getProjectName(adoptForm.project_id) }) :
                    $t('generatedTestCases.showingAllVersions') }}
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('generatedTestCases.priority')">
              <el-select v-model="adoptForm.priority">
                <el-option label="$t('generatedTestCases.priorityLow')" value="low"></el-option>
                <el-option label="$t('generatedTestCases.priorityMedium')" value="medium"></el-option>
                <el-option label="$t('generatedTestCases.priorityHigh')" value="high"></el-option>
                <el-option label="$t('generatedTestCases.priorityCritical')" value="critical"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('generatedTestCases.testType')">
              <el-select v-model="adoptForm.test_type">
                <el-option label="$t('generatedTestCases.testTypeFunctional')" value="functional"></el-option>
                <el-option label="$t('generatedTestCases.testTypeIntegration')" value="integration"></el-option>
                <el-option label="$t('generatedTestCases.testTypeAPI')" value="api"></el-option>
                <el-option label="$t('generatedTestCases.testTypeUI')" value="ui"></el-option>
                <el-option label="$t('generatedTestCases.testTypePerformance')" value="performance"></el-option>
                <el-option label="$t('generatedTestCases.testTypeSecurity')" value="security"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="$t('generatedTestCases.status')">
          <el-select v-model="adoptForm.status">
            <el-option label="$t('generatedTestCases.statusDraft')" value="draft"></el-option>
            <el-option label="$t('generatedTestCases.statusActive')" value="active"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('generatedTestCases.preconditions')">
          <el-input v-model="adoptForm.preconditions" type="textarea" :rows="3" :placeholder="$t('generatedTestCases.preconditionsPlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('generatedTestCases.operationSteps')">
          <el-input v-model="adoptForm.steps" type="textarea" :rows="6" :placeholder="$t('generatedTestCases.operationStepsPlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('generatedTestCases.expectedResult')">
          <el-input v-model="adoptForm.expected_result" type="textarea" :rows="3" :placeholder="$t('generatedTestCases.expectedResultPlaceholder')"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeAdoptModal">{{ $t('generatedTestCases.cancel') }}</el-button>
          <el-button type="primary" @click="confirmAdopt" :loading="isAdopting">{{ isAdopting ? $t('generatedTestCases.adopting') : $t('generatedTestCases.confirmAdopt') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Document } from '@element-plus/icons-vue'

export default {
  components: {
    Download
  },
  name: 'GeneratedTestCaseList',
  data() {
    return {
      isLoading: false,
      tasks: [],
      selectedStatus: '',
      selectedTaskDetail: null,
      selectedTestCaseDetail: null,
      showTestCaseDetailModal: false,
      showAdoptModal: false,
      isAdopting: false,
      projects: [],
      projectVersions: [],
      allVersions: [],
      adoptForm: {
        title: '',
        description: '',
        project_id: null,
        priority: 'low',
        test_type: 'functional',
        status: 'draft',
        preconditions: '',
        steps: '',
        expected_result: '',
        version_id: null
      },
      currentAdoptingTask: null,
      selectedTasks: [],
      isDeleting: false,
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      allStats: {
        total: 0,
        completed: 0,
        running: 0,
        failed: 0
      }
    }
  },

  computed: {
    availableVersions() {
      if (this.adoptForm.project_id) {
        return this.projectVersions
      } else {
        return this.allVersions
      }
    }
  },
  
  mounted() {
    this.loadTasks()
    this.fetchProjects()
    this.fetchAllVersions()
  },
  
  methods: {
    async loadTasks() {
      this.isLoading = true
      try {
        let url = '/requirement-analysis/testcase-generation/'
        const params = new URLSearchParams()
        
        params.append('page', String(this.pagination.currentPage))
        params.append('page_size', String(this.pagination.pageSize))
        
        if (this.selectedStatus) {
          params.append('status', this.selectedStatus)
        }
        
        if (params.toString()) {
          url += '?' + params.toString()
        }
        
        const response = await api.get(url)
        
        if (response.data.results) {
          this.tasks = response.data.results
          this.pagination.total = response.data.count || 0
        } else {
          this.tasks = response.data || []
          this.pagination.total = this.tasks.length
        }
        
        this.updateStats()
        
      } catch (error) {
        console.error(this.$t('generatedTestCases.loadTasksFailed'), error)
        this.tasks = []
        this.pagination.total = 0
      } finally {
        this.isLoading = false
        this.selectedTasks = []
      }
    },

    handleSelectionChange(selection) {
      this.selectedTasks = selection.map(item => item.task_id)
    },

    isTaskSelected(taskId) {
      return this.selectedTasks.includes(taskId)
    },

    async batchDeleteTasks() {
      if (this.selectedTasks.length === 0) {
        ElMessage.warning(this.$t('generatedTestCases.selectTasksFirst'))
        return
      }

      try {
        await ElMessageBox.confirm(
          this.$t('generatedTestCases.batchDeleteConfirm', { count: this.selectedTasks.length }),
          this.$t('generatedTestCases.confirmTitle'),
          {
            confirmButtonText: this.$t('common.confirm'),
            cancelButtonText: this.$t('common.cancel'),
            type: 'warning'
          }
        )

        this.isDeleting = true
        let successCount = 0
        let failCount = 0

        for (const taskId of this.selectedTasks) {
          try {
            await api.delete(`/requirement-analysis/testcase-generation/${taskId}/`)
            successCount++
          } catch (error) {
            console.error(`删除任务 ${taskId} 失败:`, error)
            failCount++
          }
        }

        if (successCount > 0) {
          ElMessage.success(this.$t('generatedTestCases.deleteSuccess', { success: successCount, failed: failCount }))
        } else {
          ElMessage.error(this.$t('generatedTestCases.deleteFailed'))
        }

        this.selectedTasks = []
        this.loadTasks()

      } catch (error) {
        if (error !== 'cancel') {
          console.error(this.$t('generatedTestCases.batchDeleteFailed'), error)
          ElMessage.error(this.$t('generatedTestCases.batchDeleteFailed') + ': ' + (error.message || this.$t('generatedTestCases.unknownError')))
        }
      } finally {
        this.isDeleting = false
      }
    },

    updateStats() {
      this.loadAllStats()
    },

    async loadAllStats() {
      try {
        let url = '/requirement-analysis/testcase-generation/'
        const params = new URLSearchParams()
        
        params.append('page_size', '10000')
        params.append('page', '1')
        
        if (this.selectedStatus) {
          params.append('status', this.selectedStatus)
        }
        
        url += '?' + params.toString()
        
        const response = await api.get(url)
        const allTasks = response.data.results || response.data || []
        
        this.allStats.total = allTasks.length
        this.allStats.completed = allTasks.filter(t => t.status === 'completed').length
        this.allStats.running = allTasks.filter(t => ['pending', 'generating', 'reviewing'].includes(t.status)).length
        this.allStats.failed = allTasks.filter(t => t.status === 'failed').length
        
      } catch (error) {
        console.error(this.$t('generatedTestCases.loadStatsFailed'), error)
        this.allStats.total = this.pagination.total || 0
        this.allStats.completed = 0
        this.allStats.running = 0
        this.allStats.failed = 0
      }
    },

    getStatusText(status) {
      const statusMap = {
        'pending': this.$t('generatedTestCases.statusPending'),
        'generating': this.$t('generatedTestCases.statusGenerating'),
        'reviewing': this.$t('generatedTestCases.statusReviewing'),
        'revising': this.$t('generatedTestCases.statusRevising'),
        'completed': this.$t('generatedTestCases.statusCompleted'),
        'failed': this.$t('generatedTestCases.statusFailed'),
        'cancelled': this.$t('generatedTestCases.statusCancelled')
      }
      return statusMap[status] || status
    },

    getStatusType(status) {
      const typeMap = {
        'pending': 'info',
        'generating': 'warning',
        'reviewing': 'primary',
        'revising': 'warning',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'info'
      }
      return typeMap[status] || 'info'
    },

    getStatusIcon(status) {
      const iconMap = {
        'pending': 'icon-pending',
        'generating': 'icon-generating',
        'reviewing': 'icon-reviewing',
        'revising': 'icon-revising',
        'completed': 'icon-completed',
        'failed': 'icon-failed'
      }
      return iconMap[status] || ''
    },

    getTestCaseCount(task) {
      if (!task.final_test_cases) {
        return 0
      }

      const content = task.final_test_cases
      const lines = content.split('\n').filter(line => line.trim())

      let tableRows = 0
      let isFirstRow = true
      let isTableFormat = false

      for (let line of lines) {
        if (line.includes('|') && !line.includes('--------')) {
          const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell)
          if (cells.length > 1) {
            if (isFirstRow) {
              isFirstRow = false
              if (line.includes('测试用例编号') || line.includes('ID') || line.includes('用例ID') ||
                  line.includes('场景') || line.includes('步骤')) {
                isTableFormat = true
                continue
              }
            }

            tableRows++
            if (tableRows >= 1) {
              isTableFormat = true
            }
          }
        }
      }

      if (isTableFormat && tableRows > 0) {
        return tableRows
      }

      let caseCount = 0
      for (const line of lines) {
        if (line.includes('测试用例') || line.includes('Test Case') || line.match(/^(\d+\.|测试场景)/)) {
          caseCount++
        }
      }

      return caseCount || 0
    },

    exportTestCasesMD(task) {
      try {
        const exportUrl = `/api/requirement-analysis/testcase-generation/${task.task_id}/export_md/?filename=${encodeURIComponent(task.title || task.task_id)}`

        console.log('开始导出MD文件，URL:', exportUrl)

        fetch(exportUrl, {
          method: 'GET',
          credentials: 'include',
        })
        .then(response => {
          if (response.ok) {
            return response.blob();
          } else {
            throw new Error(`导出失败: ${response.status} ${response.statusText}`);
          }
        })
        .then(blob => {
          console.log('获取到文件blob，大小:', blob.size)
          
          const urlObject = URL.createObjectURL(blob)
          
          const link = document.createElement('a')
          link.href = urlObject
          link.download = `${task.title || task.task_id}.md`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          
          setTimeout(() => {
            URL.revokeObjectURL(urlObject)
          }, 100)

          console.log('文件下载已触发')
          ElMessage.success('MD格式测试用例导出成功！')
        })
        .catch(error => {
          console.error('导出失败:', error)
          ElMessage.error(`导出失败: ${error.message || '未知错误'}`)
        });
      } catch (error) {
        console.error('导出MD格式测试用例失败:', error)
        ElMessage.error(`导出失败: ${error.message || '未知错误'}`)
      }
    },

    goToGenerationPage(task) {
      // 只有正在生成中的任务（非completed、非failed、非cancelled）才可以点击跳转
      if (!['completed', 'failed', 'cancelled'].includes(task.status)) {
        this.$router.push({
          path: '/ai-generation/requirement-analysis',
          query: {
            taskId: task.task_id,
            outputMode: task.output_mode || 'stream'
          }
        })
      }
      // 已完成或失败的任务不执行任何操作
    },

    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    async fetchProjects() {
      try {
        const response = await api.get('/projects/list/')
        this.projects = response.data.results || []
      } catch (error) {
        console.error(this.$t('generatedTestCases.fetchProjectsFailed'), error)
      }
    },

    async fetchAllVersions() {
      try {
        const response = await api.get('/versions/')
        this.allVersions = response.data.results || response.data || []
      } catch (error) {
        console.error(this.$t('generatedTestCases.fetchVersionsFailed'), error)
        this.allVersions = []
      }
    },

    async fetchProjectVersions(projectId) {
      if (!projectId) {
        this.projectVersions = []
        return
      }

      try {
        const response = await api.get(`/versions/projects/${projectId}/versions/`)
        this.projectVersions = response.data || []
      } catch (error) {
        console.error(this.$t('generatedTestCases.fetchProjectVersionsFailed'), error)
        this.projectVersions = []
      }
    },

    async adoptTestCase(testCase) {
      this.currentAdoptingTask = testCase
      
      this.adoptForm = {
        title: testCase.title,
        description: testCase.title,
        project_id: null,
        priority: 'low',
        test_type: 'functional',
        status: 'draft',
        preconditions: testCase.precondition || '',
        steps: testCase.test_steps || '',
        expected_result: testCase.expected_result || '',
        version_id: null
      }
      
      this.showAdoptModal = true
    },

    async onAdoptProjectChange() {
      if (this.adoptForm.project_id) {
        await this.fetchProjectVersions(this.adoptForm.project_id)
        
        if (this.adoptForm.version_id) {
          const versionExists = this.projectVersions.some(v => v.id === this.adoptForm.version_id)
          if (!versionExists) {
            this.adoptForm.version_id = null
          }
        }
      } else {
        this.projectVersions = []
      }
    },

    async confirmAdopt() {
      if (!this.adoptForm.project_id) {
        ElMessage.warning(this.$t('generatedTestCases.selectProjectRequired'))
        return
      }

      if (!this.adoptForm.version_id) {
        ElMessage.warning(this.$t('generatedTestCases.selectVersionRequired'))
        return
      }

      if (!this.adoptForm.title.trim()) {
        ElMessage.warning(this.$t('generatedTestCases.enterCaseTitle'))
        return
      }

      if (!this.adoptForm.expected_result.trim()) {
        ElMessage.warning(this.$t('generatedTestCases.enterExpectedResult'))
        return
      }
      
      this.isAdopting = true
      
      try {
        const submitData = {
          title: this.adoptForm.title,
          description: this.adoptForm.description,
          project_id: this.adoptForm.project_id,
          priority: this.adoptForm.priority || 'low',
          test_type: this.adoptForm.test_type,
          status: this.adoptForm.status,
          preconditions: this.adoptForm.preconditions,
          steps: this.adoptForm.steps,
          expected_result: this.adoptForm.expected_result,
          version_ids: this.adoptForm.version_id ? [this.adoptForm.version_id] : []
        }
        
        if (!submitData.priority) {
          submitData.priority = 'low'
        }
        
        await api.post('/testcases/', submitData)
        
        try {
          await api.patch(`/requirement-analysis/test-cases/${this.currentAdoptingTask.id}/`, {
            status: 'adopted'
          })
        } catch (updateError) {
          console.warn(this.$t('generatedTestCases.updateStatusFailed'), updateError)
        }

        ElMessage.success(this.$t('generatedTestCases.adoptModalSuccess'))
        this.closeAdoptModal()
        this.loadTestCases()

      } catch (error) {
        console.error(this.$t('generatedTestCases.adoptCaseFailed'), error)
        ElMessage.error(this.$t('generatedTestCases.adoptCaseFailedRetry'))
      } finally {
        this.isAdopting = false
      }
    },

    closeAdoptModal() {
      this.showAdoptModal = false
      this.currentAdoptingTask = null
      this.projectVersions = []
    },

    closeTestCaseDetail() {
      this.showTestCaseDetailModal = false
      this.selectedTestCaseDetail = null
    },

    loadTestCases() {
      this.loadTasks()
    },

    getProjectName(projectId) {
      const project = this.projects.find(p => p.id === projectId)
      return project ? project.name : ''
    },

    onPageSizeChange() {
      this.pagination.currentPage = 1
      this.loadTasks()
    },

    goToPage(page) {
      this.pagination.currentPage = page
      this.loadTasks()
    }
  }
}
</script>

<style lang="scss" scoped>
:root {
  --primary-color: #667eea;
  --primary-dark: #764ba2;
  --primary-light: #f8f7ff;
  --primary-lighter: #fafbff;
  --border-color: #e8e8e8;
  --text-primary: #262626;
  --text-secondary: #595959;
  --text-tertiary: #8c8c8c;
  --bg-light: #ffffff;
  --bg-gray: #fafafa;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #ff4d4f;
  --info-color: #1890ff;
}

.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);

  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: #5a32a3;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .page-subtitle {
    color: #6d5d8f;
    font-size: 14px;
    opacity: 0.9;
    margin: 0;
  }
}

.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  .status-tabs {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .status-tab {
    padding: 6px 12px;
    border: none;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    background: rgba(147, 112, 219, 0.1);
    color: #6d5d8f;
    white-space: nowrap;
  }

  .status-tab:hover {
    background: rgba(147, 112, 219, 0.2);
    transform: translateY(-1px);
  }

  .status-tab.active {
    background: linear-gradient(135deg, #9370db 0%, #7b42f6 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(147, 112, 219, 0.3);
  }

  .filter-bar-spacer {
    flex: 1;
  }

  .stats-container {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: nowrap;
  }

  .stats-container .stat-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(147, 112, 219, 0.08);
    border-radius: 6px;
    min-width: auto;
    transition: all 0.3s ease;
    flex-shrink: 0;
  }

  .stats-container .stat-item:hover {
    background: rgba(147, 112, 219, 0.15);
  }

  .stats-container .stat-number {
    font-size: 1.2rem;
    font-weight: 700;
    color: #5a32a3;
    line-height: 1;
  }

  .stats-container .stat-label {
    font-size: 0.75rem;
    color: #6d5d8f;
    font-weight: 500;
    white-space: nowrap;
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

  .el-table {
    border: none;
    border-radius: 8px 8px 0 0;
    overflow: hidden;
    min-height: 200px;
    box-shadow: none;
    transition: all 0.3s ease;
    background-color: transparent !important;

    --el-color-primary: var(--primary-color);
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

    :deep(.el-table__header-wrapper) {
      background-color: #ffffff !important;

      :deep(.el-table__header) {
        background-color: #ffffff !important;

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
            background-color: #ffffff !important;
          }

          :deep(.cell) {
            background-color: #ffffff !important;
            color: #5a32a3 !important;
            font-weight: 600 !important;
          }
        }
      }
    }

    :deep(.el-table__body-wrapper) {
      background-color: #ffffff !important;

      :deep(.el-table__row) {
        transition: all 0.3s ease;
        background-color: #ffffff !important;
        line-height: 24px;

        &:hover {
          background-color: #f8f7ff !important;
        }

        &.el-table__row--striped {
          background-color: #fafaff !important;
        }

        :deep(td) {
          padding: 14px 16px;
          border-bottom: 1px solid #e9ecef;
          color: #333;
          font-size: 14px;
          font-weight: 400;
          line-height: 24px;
          transition: all 0.3s ease;
        }
      }
    }

    :deep(.el-table__empty-block) {
      padding: 60px 0;
      background: #ffffff !important;

      :deep(.el-table__empty-text) {
        color: #666;
        font-size: 14px;
        line-height: 24px;
      }
    }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 40px;
    min-height: 300px;

    .empty-icon {
      width: 64px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 16px;
      margin-bottom: 20px;
      transition: all 0.3s ease;

      .el-icon {
        opacity: 0.5;
      }
    }

    h3 {
      color: #8c8c8c;
      margin-bottom: 0;
      font-size: 14px;
      font-weight: 400;
    }

    p {
      font-size: 14px;
      line-height: 1.8;
      color: #8c8c8c;
      max-width: 400px;
      margin: 0 auto;
      text-align: center;
    }

    a {
      color: #7b42f6;
      text-decoration: none;
      font-weight: 500;
      transition: all 0.3s ease;
      padding: 4px 8px;
      border-radius: 4px;
      margin: 0 4px;

      &:hover {
        color: #5a32a3;
        background: rgba(147, 112, 219, 0.1);
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

// 操作按钮容器
.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  flex-wrap: nowrap;
}

// 操作按钮样式
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

  &.export-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

// 状态徽章样式 - 参考图2简洁风格
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

  // 需求分析中 - 蓝色
  &.pending {
    background: #e6f7ff;
    color: #1890ff;
  }

  // 用例编写中 - 橙色
  &.generating {
    background: #fff7e6;
    color: #fa8c16;
  }

  // 用例评审中 - 紫色
  &.reviewing {
    background: #f9f0ff;
    color: #722ed1;
  }

  // 用例修订中 - 黄色
  &.revising {
    background: #fffbe6;
    color: #faad14;
  }

  // 已完成 - 绿色
  &.completed {
    background: #f6ffed;
    color: #52c41a;
  }

  // 失败 - 红色
  &.failed {
    background: #fff1f0;
    color: #f5222d;
  }

  // 已取消 - 灰色
  &.cancelled {
    background: #f5f5f5;
    color: #8c8c8c;
  }
}

// 筛选标签样式优化
.filter-bar {
  .status-tabs {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding: 4px;
    background: #f8f7ff;
    border-radius: 8px;
  }

  .status-tab {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s ease;
    background: transparent;
    color: #6d5d8f;
    white-space: nowrap;
    position: relative;

    &:hover {
      background: rgba(147, 112, 219, 0.1);
      color: #5a32a3;
    }

    &.active {
      background: #ffffff;
      color: #7b42f6;
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
      font-weight: 600;
    }
  }

  // 批量删除按钮样式
  .batch-delete-btn {
    background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3) !important;

    .el-icon {
      margin-right: 6px;
    }

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #ff7875 0%, #ffa39e 100%) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 6px 20px rgba(255, 77, 79, 0.4) !important;
    }

    &:active:not(:disabled) {
      transform: translateY(0) !important;
    }

    &:disabled {
      background: linear-gradient(135deg, #d9d9d9 0%, #bfbfbf 100%) !important;
      box-shadow: none !important;
      cursor: not-allowed !important;
    }
  }
}

// 统计信息样式优化
.stats-container {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: nowrap;

  .stat-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #ffffff;
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.15);
    transition: all 0.3s ease;
    flex-shrink: 0;

    &:hover {
      border-color: rgba(147, 112, 219, 0.3);
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
    }

    .stat-number {
      font-size: 18px;
      font-weight: 700;
      color: #5a32a3;
      line-height: 1;
    }

    .stat-label {
      font-size: 12px;
      color: #8c8c8c;
      font-weight: 500;
      white-space: nowrap;
    }
  }
}

// 用例数量徽章
.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  background: linear-gradient(135deg, #f8f7ff 0%, #ede9fe 100%);
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 12px;
  color: #5a32a3;
  font-size: 12px;
  font-weight: 600;
}

// 需求名称样式
.requirement-name {
  color: #333;
  font-weight: 500;
  transition: all 0.3s ease;

  &:hover {
    color: #7b42f6;
  }

  &.clickable {
    cursor: pointer;
    color: #7b42f6;
    text-decoration: underline;
    text-decoration-color: transparent;
    transition: all 0.3s ease;

    &:hover {
      color: #6d28d9;
      text-decoration-color: #6d28d9;
    }
  }
}
</style>
