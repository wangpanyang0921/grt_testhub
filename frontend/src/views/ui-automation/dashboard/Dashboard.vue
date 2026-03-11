<template>
  <div class="dashboard-container">
    <!-- 数据概览 -->
    <div class="stats-section">
      <h2 class="section-title">{{ $t('uiAutomation.dashboard.dataOverview') }}</h2>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ projectCount }}</div>
                <div class="stat-label">{{ $t('uiAutomation.dashboard.uiTestProjects') }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ testCaseCount }}</div>
                <div class="stat-label">{{ $t('uiAutomation.dashboard.testCases') }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ suiteCount }}</div>
                <div class="stat-label">{{ $t('uiAutomation.dashboard.testSuites') }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <el-icon><RefreshRight /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ executionCount }}</div>
                <div class="stat-label">{{ $t('uiAutomation.dashboard.testExecutions') }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 最近活动和快速操作 - 暂时隐藏
    <el-row :gutter="20" class="content-section">
      <el-col :span="12">
        <el-card class="recent-activities" :title="$t('uiAutomation.dashboard.operationRecords')" shadow="hover">
          <div v-if="loading" class="loading-container">
            <el-empty :description="$t('uiAutomation.dashboard.loading')" />
          </div>
          <div v-else-if="operationRecords.length === 0" class="empty-container">
            <el-empty :description="$t('uiAutomation.dashboard.noRecords')" />
          </div>
          <div v-else class="activities-list">
            <div v-for="record in operationRecords" :key="record.id" class="activity-item">
              <div class="activity-icon" :class="getOperationIconClass(record.operation_type)">
                <el-icon><component :is="getOperationIcon(record.operation_type)" /></el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-text">
                  <span class="operation-user">{{ record.user_name }}</span>
                  <span class="operation-action">{{ record.operation_type_display }}</span>
                  <span class="operation-resource">{{ record.resource_type_display }}</span>
                  <span class="resource-name">「{{ record.resource_name }}」</span>
                </div>
                <div class="activity-time">{{ formatRelativeTime(record.created_at) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="quick-actions" :title="$t('uiAutomation.dashboard.quickActions')" shadow="hover">
          <div class="actions-grid">
            <div class="action-item" @click="goToProjects">
              <div class="action-icon bg-blue">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.projectManagement') }}</div>
            </div>
            <div class="action-item" @click="goToElements">
              <div class="action-icon bg-green">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.elementManagement') }}</div>
            </div>
            <div class="action-item" @click="goToTestCases">
              <div class="action-icon bg-cyan">
                <el-icon><Document /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.caseManagement') }}</div>
            </div>
            <div class="action-item" @click="goToScripts">
              <div class="action-icon bg-purple">
                <el-icon><Edit /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.scriptGeneration') }}</div>
            </div>
            <div class="action-item" @click="goToSuites">
              <div class="action-icon bg-orange">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.runTests') }}</div>
            </div>
            <div class="action-item" @click="goToExecutions">
              <div class="action-icon bg-red">
                <el-icon><VideoPlay /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.executionRecords') }}</div>
            </div>
            <div class="action-item" @click="goToReports">
              <div class="action-icon bg-indigo">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="action-label">{{ $t('uiAutomation.dashboard.testReports') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    -->

    <!-- 核心功能介绍 -->
    <div class="features-section">
      <h2 class="section-title">{{ $t('uiAutomation.dashboard.coreFeatures') }}</h2>
      <el-row :gutter="20" class="features-row">
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon><Cpu /></el-icon>
            </div>
            <h3 class="feature-title">{{ $t('uiAutomation.dashboard.elementLocation') }}</h3>
            <p class="feature-description">{{ $t('uiAutomation.dashboard.elementLocationDesc') }}</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <h3 class="feature-title">{{ $t('uiAutomation.dashboard.dualEngine') }}</h3>
            <p class="feature-description">{{ $t('uiAutomation.dashboard.dualEngineDesc') }}</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon><Platform /></el-icon>
            </div>
            <h3 class="feature-title">{{ $t('uiAutomation.dashboard.multiBrowser') }}</h3>
            <p class="feature-description">{{ $t('uiAutomation.dashboard.multiBrowserDesc') }}</p>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="20" class="features-row">
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <h3 class="feature-title">{{ $t('uiAutomation.dashboard.fullNotification') }}</h3>
            <p class="feature-description">{{ $t('uiAutomation.dashboard.fullNotificationDesc') }}</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon><Edit /></el-icon>
            </div>
            <h3 class="feature-title">{{ $t('uiAutomation.dashboard.scriptRecording') }}</h3>
            <p class="feature-description">{{ $t('uiAutomation.dashboard.scriptRecordingDesc') }}</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon><RefreshRight /></el-icon>
            </div>
            <h3 class="feature-title">{{ $t('uiAutomation.dashboard.autoExecution') }}</h3>
            <p class="feature-description">{{ $t('uiAutomation.dashboard.autoExecutionDesc') }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  Folder, Document, Collection, RefreshRight,
  Bell, Cpu, Monitor, Edit, Platform,
  Plus, Delete, CaretRight, Refresh, VideoPlay, DataAnalysis
} from '@element-plus/icons-vue'
import router from '@/router'
import {
  getDashboardStats,
  getOperationRecords
} from '@/api/ui_automation'

const { t } = useI18n()

// 统计数据
const projectCount = ref(0)
const testCaseCount = ref(0)
const suiteCount = ref(0)
const executionCount = ref(0)

// 操作记录
const operationRecords = ref([])
const loading = ref(false)

// 加载数据
const loadDashboardData = async () => {
  loading.value = true
  try {
    // 并行加载统计数据和操作记录
    const [statsRes, recordsRes] = await Promise.all([
      getDashboardStats(),
      getOperationRecords({ limit: 10 })
    ])

    // 更新统计数据
    const stats = statsRes.data
    projectCount.value = stats.project_count || 0
    testCaseCount.value = stats.test_case_count || 0
    suiteCount.value = stats.suite_count || 0
    executionCount.value = stats.execution_count || 0

    // 操作记录
    operationRecords.value = recordsRes.data.results || recordsRes.data || []
  } catch (error) {
    ElMessage.error(t('uiAutomation.dashboard.messages.loadFailed'))
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

// 获取操作类型图标
const getOperationIcon = (operationType) => {
  const iconMap = {
    'create': Plus,
    'edit': Edit,
    'delete': Delete,
    'run': CaretRight,
    'rerun': Refresh,
    'save': Document,
    'rename': Edit
  }
  return iconMap[operationType] || Bell
}

// 获取操作图标样式类
const getOperationIconClass = (operationType) => {
  const classMap = {
    'create': 'icon-create',
    'edit': 'icon-edit',
    'delete': 'icon-delete',
    'run': 'icon-run',
    'rerun': 'icon-rerun',
    'save': 'icon-save',
    'rename': 'icon-rename'
  }
  return classMap[operationType] || ''
}

// 格式化相对时间
const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMins < 1) {
    return t('uiAutomation.dashboard.justNow')
  } else if (diffMins < 60) {
    return t('uiAutomation.dashboard.minutesAgo', { n: diffMins })
  } else if (diffHours < 24) {
    return t('uiAutomation.dashboard.hoursAgo', { n: diffHours })
  } else {
    return t('uiAutomation.dashboard.daysAgo', { n: diffDays })
  }
}

// 导航到各功能页面
const goToProjects = () => {
  router.push('/ui-automation/projects')
}

const goToElements = () => {
  router.push('/ui-automation/elements-enhanced')
}

const goToTestCases = () => {
  router.push('/ui-automation/test-cases')
}

const goToScripts = () => {
  router.push('/ui-automation/scripts-enhanced')
}

const goToSuites = () => {
  router.push('/ui-automation/suites')
}

const goToExecutions = () => {
  router.push('/ui-automation/executions')
}

const goToReports = () => {
  router.push('/ui-automation/reports')
}

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData()
})
</script>

<style lang="scss" scoped>
// 页面容器
.dashboard-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
}

// 统计区域
.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(147, 112, 219, 0.15);
  }
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100px;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon.bg-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.bg-green {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
}

.stat-icon.bg-purple {
  background: linear-gradient(135deg, #722ed1 0%, #531dab 100%);
}

.stat-icon.bg-orange {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
}

.stat-icon.bg-red {
  background: linear-gradient(135deg, #f5222d 0%, #cf1322 100%);
}

.stat-icon.bg-cyan {
  background: linear-gradient(135deg, #13c2c2 0%, #08979c 100%);
}

.stat-icon.bg-indigo {
  background: linear-gradient(135deg, #597ef7 0%, #2f54eb 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #5a32a3;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

// 内容区域
.content-section {
  margin-bottom: 20px;
}

.recent-activities {
  height: 100%;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
}

.activities-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid rgba(147, 112, 219, 0.08);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(147, 112, 219, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: #7b42f6;
}

.activity-icon.icon-create {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #1890ff;
}

.activity-icon.icon-edit {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  color: #fa8c16;
}

.activity-icon.icon-delete {
  background: linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%);
  color: #f5222d;
}

.activity-icon.icon-run {
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  color: #52c41a;
}

.activity-icon.icon-rerun {
  background: linear-gradient(135deg, #f9f0ff 0%, #efdbff 100%);
  color: #722ed1;
}

.activity-icon.icon-save {
  background: linear-gradient(135deg, #e6fffb 0%, #b5f5ec 100%);
  color: #13c2c2;
}

.activity-icon.icon-rename {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  color: #fa8c16;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
}

.activity-text .operation-user {
  font-weight: 600;
  color: #7b42f6;
}

.activity-text .operation-action {
  margin: 0 4px;
  color: #666;
}

.activity-text .operation-resource {
  margin-right: 4px;
  color: #666;
}

.activity-text .resource-name {
  font-weight: 500;
  color: #333;
}

.activity-time {
  font-size: 12px;
  color: #999;
}

.quick-actions {
  height: 100%;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.action-item {
  text-align: center;
  padding: 15px 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(147, 112, 219, 0.05);
}

.action-item:hover {
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(147, 112, 219, 0.15);
  border-color: rgba(147, 112, 219, 0.2);
}

.action-item .action-icon {
  margin: 0 auto 15px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-icon.bg-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.action-icon.bg-green {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
}

.action-icon.bg-cyan {
  background: linear-gradient(135deg, #13c2c2 0%, #08979c 100%);
}

.action-icon.bg-purple {
  background: linear-gradient(135deg, #722ed1 0%, #531dab 100%);
}

.action-icon.bg-orange {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
}

.action-icon.bg-red {
  background: linear-gradient(135deg, #f5222d 0%, #cf1322 100%);
}

.action-icon.bg-indigo {
  background: linear-gradient(135deg, #597ef7 0%, #2f54eb 100%);
}

.action-label {
  font-size: 16px;
  color: #5a32a3;
  font-weight: 500;
}

// 功能区域
.features-section {
  margin-top: 16px;
  margin-bottom: 20px;
}

.features-section .features-row {
  margin-bottom: 16px;
}

.features-section .features-row:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #5a32a3;
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  padding-left: 12px;
  border-left: 4px solid #7b42f6;
}

.feature-card {
  height: 100%;
  padding: 36px 24px;
  text-align: center;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(147, 112, 219, 0.15);
  border-color: rgba(147, 112, 219, 0.2);
}

.feature-icon {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  font-size: 40px;
  color: #7b42f6;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(147, 112, 219, 0.15);
}

.feature-card:hover .feature-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  transform: scale(1.05);
}

.feature-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #5a32a3;
}

.feature-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 8px;
}

// 加载和空状态
.loading-container,
.empty-container {
  padding: 40px 0;
  background: transparent;
}

// 响应式适配
@media screen and (max-width: 1920px) {
  .stats-section {
    margin-bottom: 20px;
  }

  .stat-content {
    height: 90px;
  }

  .stat-icon {
    width: 55px;
    height: 55px;
    font-size: 22px;
  }

  .stat-value {
    font-size: 26px;
  }

  .content-section {
    margin-bottom: 20px;
  }

  .features-section {
    margin-bottom: 20px;
  }

  .feature-card {
    padding: 32px 20px;
  }

  .feature-icon {
    width: 80px;
    height: 80px;
    font-size: 36px;
  }
}

@media screen and (max-width: 1600px) {
  .stats-section {
    margin-bottom: 20px;
  }

  .stat-content {
    height: 85px;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }

  .stat-value {
    font-size: 24px;
  }

  .content-section {
    margin-bottom: 20px;
  }

  .features-section {
    margin-bottom: 20px;
  }

  .section-title {
    font-size: 22px;
  }
}

@media screen and (max-width: 1440px) {
  .stats-section {
    margin-bottom: 20px;
  }

  .stat-content {
    height: 80px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 18px;
  }

  .stat-value {
    font-size: 22px;
  }

  .content-section {
    margin-bottom: 20px;
  }
  
  .features-section {
    margin-bottom: 28px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .actions-grid {
    gap: 12px;
  }
  
  .action-item {
    padding: 12px 8px;
  }
  
  .action-icon {
    width: 45px;
    height: 45px;
    font-size: 22px;
  }
  
  .action-label {
    font-size: 15px;
  }
}

@media screen and (max-width: 1366px) {
  .stats-section {
    margin-bottom: 24px;
  }
  
  .stat-content {
    height: 75px;
  }
  
  .stat-icon {
    width: 45px;
    height: 45px;
    font-size: 18px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 13px;
  }
  
  .content-section {
    margin-bottom: 24px;
  }
  
  .features-section {
    margin-bottom: 24px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .activities-list {
    max-height: 350px;
  }
  
  .actions-grid {
    gap: 10px;
  }
  
  .action-item {
    padding: 10px 6px;
  }
  
  .action-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .action-label {
    font-size: 14px;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .feature-icon {
    width: 70px;
    height: 70px;
    font-size: 32px;
  }
  
  .feature-title {
    font-size: 16px;
  }
  
  .feature-description {
    font-size: 13px;
  }
}

@media screen and (max-width: 1280px) {
  .stats-section {
    margin-bottom: 20px;
  }
  
  .stat-content {
    height: 70px;
  }
  
  .stat-icon {
    width: 42px;
    height: 42px;
    font-size: 16px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .content-section {
    margin-bottom: 20px;
  }
  
  .features-section {
    margin-bottom: 20px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .activities-list {
    max-height: 300px;
  }
  
  .action-item {
    padding: 8px 5px;
  }
  
  .action-icon {
    width: 38px;
    height: 38px;
    font-size: 18px;
  }
  
  .action-label {
    font-size: 13px;
  }
  
  .feature-card {
    padding: 15px;
  }
  
  .feature-icon {
    width: 60px;
    height: 60px;
    font-size: 28px;
  }
}

@media screen and (max-width: 1024px) {
  .stats-section {
    margin-bottom: 18px;
  }
  
  .stat-content {
    height: 65px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .stat-value {
    font-size: 16px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .content-section {
    margin-bottom: 18px;
  }
  
  .features-section {
    margin-bottom: 18px;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  .activities-list {
    max-height: 280px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .action-item {
    padding: 10px 8px;
  }
  
  .action-label {
    font-size: 13px;
  }
  
  .feature-card {
    padding: 12px;
  }
  
  .feature-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .feature-title {
    font-size: 14px;
  }
  
  .feature-description {
    font-size: 12px;
  }
}

@media screen and (max-width: 768px) {
  .stats-section {
    margin-bottom: 15px;
  }
  
  .stat-content {
    height: 60px;
  }
  
  .stat-icon {
    width: 35px;
    height: 35px;
    font-size: 14px;
  }
  
  .stat-value {
    font-size: 14px;
  }
  
  .stat-label {
    font-size: 11px;
  }
  
  .content-section {
    margin-bottom: 15px;
  }
  
  .features-section {
    margin-bottom: 15px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 15px;
  }
  
  .activities-list {
    max-height: 250px;
  }
  
  .activity-item {
    padding: 10px 0;
  }
  
  .activity-icon {
    width: 28px;
    height: 28px;
  }
  
  .activity-text {
    font-size: 13px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .action-item {
    padding: 8px 5px;
  }
  
  .action-icon {
    width: 35px;
    height: 35px;
    font-size: 16px;
  }
  
  .action-label {
    font-size: 12px;
  }
  
  .feature-card {
    padding: 10px;
  }
  
  .feature-icon {
    width: 45px;
    height: 45px;
    font-size: 20px;
  }
  
  .feature-title {
    font-size: 13px;
  }
  
  .feature-description {
    font-size: 11px;
  }
}

@media screen and (max-width: 480px) {
  .stats-section {
    margin-bottom: 12px;
  }
  
  .stat-content {
    height: 55px;
  }
  
  .stat-icon {
    width: 30px;
    height: 30px;
    font-size: 12px;
  }
  
  .stat-value {
    font-size: 13px;
  }
  
  .stat-label {
    font-size: 10px;
  }
  
  .content-section {
    margin-bottom: 12px;
  }
  
  .features-section {
    margin-bottom: 12px;
  }
  
  .section-title {
    font-size: 14px;
    margin-bottom: 12px;
  }
  
  .activities-list {
    max-height: 200px;
  }
  
  .activity-item {
    padding: 8px 0;
  }
  
  .activity-icon {
    width: 24px;
    height: 24px;
  }
  
  .activity-text {
    font-size: 12px;
  }
  
  .activity-time {
    font-size: 11px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  
  .action-item {
    padding: 6px 3px;
  }
  
  .action-icon {
    width: 30px;
    height: 30px;
    font-size: 14px;
  }
  
  .action-label {
    font-size: 11px;
  }
  
  .feature-card {
    padding: 8px;
  }
  
  .feature-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
  
  .feature-title {
    font-size: 12px;
  }
  
  .feature-description {
    font-size: 10px;
  }
}
</style>