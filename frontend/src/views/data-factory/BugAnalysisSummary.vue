<template>
  <div class="bug-analysis-container">
    <!-- 顶部筛选栏 -->
    <div class="filter-bar">
      <div class="filter-bar-left">
        <!-- 时间聚合维度 -->
        <div class="group-by-selector-top">
          <span class="label">时间聚合维度：</span>
          <el-radio-group v-model="groupBy" size="default">
            <el-radio-button label="week">按周</el-radio-button>
            <el-radio-button label="month">按月</el-radio-button>
            <el-radio-button label="quarter">按季度</el-radio-button>
            <el-radio-button label="half_year">按半年</el-radio-button>
            <el-radio-button label="year">按年</el-radio-button>
          </el-radio-group>
          <el-button
            v-if="currentStep === 1"
            type="primary"
            :disabled="selectedRecords.length === 0"
            :loading="analyzing"
            @click="generateSummary"
            class="generate-btn"
          >
            <el-icon><TrendCharts /></el-icon>
            生成汇总分析
          </el-button>
        </div>
      </div>
      <div class="filter-bar-spacer"></div>
      <div class="filter-bar-right">
        <div v-if="currentStep === 1" class="status-tag">
          <el-icon class="status-icon"><Checked /></el-icon>
          <span>已选择 {{ selectedRecords.length }} 个记录</span>
        </div>
        <div v-else class="status-tag success">
          <el-icon class="status-icon"><CircleCheck /></el-icon>
          <span>分析完成</span>
        </div>
      </div>
    </div>

    <!-- 步骤 1: 选择分析范围 -->
    <div v-show="currentStep === 1" class="step-content-area">
      <div class="card-container">
        <div class="card-header">
          <span class="header-title"><el-icon><Checked /></el-icon> 选择分析范围</span>
        </div>
        
        <!-- 记录列表 -->
        <div class="records-selector">
          <el-table
            ref="recordsTable"
            :data="availableRecords"
            style="width: 100%"
            stripe
            @selection-change="handleSelectionChange"
            v-loading="loadingRecords"
          >
            <el-table-column type="selection" width="55" header-align="center" align="center" />
            <el-table-column label="序号" width="80" header-align="center" align="center">
              <template #default="{ $index }">
                <span>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="file_name" label="文件名" min-width="180" show-overflow-tooltip header-align="center" align="left">
              <template #default="{ row }">
                <span>{{ row.file_name || '未命名' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_bugs" label="Bug数" width="100" header-align="center" align="center">
              <template #default="{ row }">
                <span class="count-badge">{{ row.total_bugs || 0 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="上传时间" width="160" header-align="center" align="center">
              <template #default="{ row }">
                <span class="time-text">{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 空状态提示 -->
        <div v-if="availableRecords.length === 0 && !loadingRecords" class="records-empty">
          <el-empty description="暂无历史记录">
            <template #image>
              <el-icon :size="60" color="#dcdfe6"><Document /></el-icon>
            </template>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 步骤 2: 汇总结果展示 -->
    <div v-if="currentStep === 2 && summaryData" class="step-content-area">
      <!-- 返回按钮 -->
      <div class="back-bar">
        <el-button @click="goBackToSelection" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回重新选择
        </el-button>
        <el-button type="primary" @click="refreshAnalysis" :loading="analyzing">
          <el-icon><Refresh /></el-icon>
          重新分析
        </el-button>
      </div>
      
      <!-- 核心指标卡片 -->
      <div class="summary-cards">
        <el-row :gutter="16">
          <el-col :span="4" :xs="12">
            <div class="summary-card">
              <div class="summary-icon" style="background: #e6f7ff; color: #1890ff;"><el-icon><Document /></el-icon></div>
              <div class="summary-info">
                <div class="summary-value">{{ summaryData.metrics.total_bugs }}</div>
                <div class="summary-label">总 Bug 数</div>
                <div class="summary-sub">全部缺陷汇总</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4" :xs="12">
            <div class="summary-card">
              <div class="summary-icon" style="background: #f6ffed; color: #52c41a;"><el-icon><Grid /></el-icon></div>
              <div class="summary-info">
                <div class="summary-value">{{ summaryData.metrics.total_modules }}</div>
                <div class="summary-label">涉及模块</div>
                <div class="summary-sub">跨模块统计</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4" :xs="12">
            <div class="summary-card">
              <div class="summary-icon" style="background: #fff7e6; color: #fa8c16;"><el-icon><Files /></el-icon></div>
              <div class="summary-info">
                <div class="summary-value">{{ summaryData.metrics.record_count }}</div>
                <div class="summary-label">分析记录</div>
                <div class="summary-sub">历史版本数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4" :xs="12">
            <div class="summary-card">
              <div class="summary-icon" style="background: #fff2f0; color: #ff4d4f;"><el-icon><Warning /></el-icon></div>
              <div class="summary-info">
                <div class="summary-value">{{ summaryData.metrics.online_bugs }}</div>
                <div class="summary-label">线上故障</div>
                <div class="summary-sub">生产环境问题</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4" :xs="12">
            <div class="summary-card">
              <div class="summary-icon" style="background: #f9f0ff; color: #722ed1;"><el-icon><CircleCheck /></el-icon></div>
              <div class="summary-info">
                <div class="summary-value">{{ summaryData.metrics.defect_bugs }}</div>
                <div class="summary-label">缺陷数量</div>
                <div class="summary-sub">功能/体验问题</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4" :xs="12">
            <div class="summary-card" :class="{ 'has-risk': summaryData?.risk_modules?.length > 0 }">
              <div class="summary-icon" style="background: #fff1f0; color: #cf1322;"><el-icon><Bell /></el-icon></div>
              <div class="summary-info">
                <div class="summary-value">{{ summaryData.risk_modules.length }}</div>
                <div class="summary-label">风险模块</div>
                <div class="summary-sub">需重点关注</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Tab 标签页导航 -->
      <div class="tab-navigation">
        <div class="tab-item active">
          <el-icon><TrendCharts /></el-icon>
          <span>趋势分析</span>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="16" class="chart-row">
          <!-- 趋势分析 -->
          <el-col :span="16">
            <div class="card-container chart-card">
              <div class="card-header">
                <span class="header-title"><el-icon><TrendCharts /></el-icon> Bug 趋势分析</span>
              </div>
              <div ref="trendChartRef" class="chart-container"></div>
            </div>
          </el-col>
          
          <!-- 热点模块排名 -->
          <el-col :span="8">
            <div class="card-container chart-card">
              <div class="card-header">
                <span class="header-title"><el-icon><Histogram /></el-icon> 热点模块 Top10</span>
              </div>
              <div ref="moduleChartRef" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 风险预警 -->
      <div class="risk-section" v-if="summaryData && summaryData.risk_modules && summaryData.risk_modules.length > 0">
        <div class="card-container">
          <div class="card-header">
            <span class="header-title"><el-icon><Warning /></el-icon> 风险预警</span>
            <el-tag type="danger" size="small">{{ summaryData.risk_modules.length }} 个高风险模块</el-tag>
          </div>
          <el-table :data="summaryData.risk_modules" style="width: 100%" stripe>
            <el-table-column type="index" width="50" align="center" />
            <el-table-column prop="module" label="模块名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="current" label="当前数量" width="100" align="center">
              <template #default="{ row }">
                <span class="p0-badge">{{ row.current }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="previous" label="历史基数" width="100" align="center">
              <template #default="{ row }">
                <span class="text-gray">{{ row.previous }}</span>
              </template>
            </el-table-column>
            <el-table-column label="增长率" width="120" align="center">
              <template #default="{ row }">
                <span class="growth-rate" :class="row.growth_rate > 1 ? 'high-risk' : 'medium-risk'">
                  +{{ (row.growth_rate * 100).toFixed(0) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="趋势" min-width="200">
              <template #default="{ row }">
                <div class="mini-trend">
                  <span
                    v-for="(point, idx) in row.trend_data"
                    :key="idx"
                    class="trend-point"
                    :style="{ height: `${(point.count / Math.max(...row.trend_data.map(t => t.count))) * 30}px` }"
                    :title="`${point.date}: ${point.count}`"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- AI 洞察 -->
      <div class="ai-section">
        <div class="card-container">
          <div class="card-header">
            <span class="header-title"><el-icon><Cpu /></el-icon> AI 智能洞察</span>
            <el-button
              type="primary"
              size="small"
              :loading="aiAnalyzing"
              :disabled="!!aiInsight"
              @click="generateAIInsight"
            >
              {{ aiInsight ? '已生成' : '生成洞察' }}
            </el-button>
          </div>
          
          <div v-if="aiInsight" class="ai-content">
            <div class="ai-insight" v-html="renderMarkdown(aiInsight)"></div>
          </div>
          <div v-else class="ai-placeholder">
            <el-empty description="点击上方按钮生成 AI 智能洞察">
              <template #image>
                <el-icon :size="60" color="#909399"><Cpu /></el-icon>
              </template>
            </el-empty>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { marked } from 'marked'
import api from '@/utils/api'
import {
  Document, Grid, Files, Warning, CircleCheck, Bell,
  TrendCharts, Histogram, Cpu, Checked, ArrowLeft, Refresh
} from '@element-plus/icons-vue'

// 路由
const router = useRouter()
const route = useRoute()

// 状态
const currentStep = ref(1) // 1: 选择文件, 2: 分析结果
const availableRecords = ref([])
const selectedRecords = ref([])
const groupBy = ref('month')
const loadingRecords = ref(false)
const analyzing = ref(false)
const summaryData = ref(null)
const aiAnalyzing = ref(false)
const aiInsight = ref('')

// 图表引用
const trendChartRef = ref(null)
const moduleChartRef = ref(null)
let trendChart = null
let moduleChart = null

// 初始化
onMounted(() => {
  fetchAvailableRecords()
})

// 获取可用记录列表
const fetchAvailableRecords = async () => {
  loadingRecords.value = true
  try {
    const response = await api.get('/data-factory/bug-analysis/records/', {
      params: { page_size: 1000 }
    })
    // 适配不同的响应结构: data.items / data.results / data
    availableRecords.value = response.data?.data?.items || response.data?.data?.results || response.data?.data || []
  } catch (error) {
    console.error('获取记录列表失败:', error)
    ElMessage.error('获取历史记录失败')
  } finally {
    loadingRecords.value = false
  }
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

// 生成汇总分析
const generateSummary = async () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请至少选择一个分析记录')
    return
  }

  analyzing.value = true
  try {
    const recordIds = selectedRecords.value.map(r => r.id)
    const response = await api.post('/data-factory/bug-analysis/summary/', {
      record_ids: recordIds,
      group_by: groupBy.value
    })

    if (response.data.success) {
      // 后端返回扁平结构，直接使用 response.data
      summaryData.value = {
        metrics: response.data.metrics,
        trends: response.data.trends,
        module_ranking: response.data.module_ranking,
        risk_modules: response.data.risk_modules
      }
      
      // 切换到步骤 2
      currentStep.value = 2
      ElMessage.success('汇总分析完成')
      
      // 等待 DOM 更新后渲染图表
      await nextTick()
      renderCharts()
    } else {
      ElMessage.error(response.data.message || '分析失败')
    }
  } catch (error) {
    console.error('汇总分析失败:', error)
    ElMessage.error('汇总分析失败: ' + (error.response?.data?.message || error.message))
  } finally {
    analyzing.value = false
  }
}

// 渲染图表
const renderCharts = () => {
  if (!summaryData.value) return
  
  renderTrendChart()
  renderModuleChart()
}

// 趋势图表
const renderTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartRef.value)
  
  const trends = summaryData.value.trends || []
  const dates = trends.map(t => t.date)
  const totals = trends.map(t => t.total)
  const onlines = trends.map(t => t.online)
  const defects = trends.map(t => t.defect)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['Bug总数', '线上故障', '缺陷'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: 'Bug数量'
    },
    series: [
      {
        name: 'Bug总数',
        type: 'line',
        smooth: true,
        data: totals,
        itemStyle: { color: '#1890ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24,144,255,0.3)' },
            { offset: 1, color: 'rgba(24,144,255,0.05)' }
          ])
        }
      },
      {
        name: '线上故障',
        type: 'line',
        smooth: true,
        data: onlines,
        itemStyle: { color: '#ff4d4f' }
      },
      {
        name: '缺陷',
        type: 'line',
        smooth: true,
        data: defects,
        itemStyle: { color: '#52c41a' }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 模块排名图表
const renderModuleChart = () => {
  if (!moduleChartRef.value) return
  
  if (moduleChart) {
    moduleChart.dispose()
  }
  
  moduleChart = echarts.init(moduleChartRef.value)
  
  const ranking = summaryData.value.module_ranking || []
  const names = ranking.map(r => r.module).reverse()
  const counts = ranking.map(r => r.count).reverse()
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'Bug数'
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        width: 90,
        overflow: 'truncate'
      }
    },
    series: [
      {
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#722ed1' },
            { offset: 1, color: '#b37feb' }
          ])
        },
        label: {
          show: true,
          position: 'right'
        }
      }
    ]
  }
  
  moduleChart.setOption(option)
}

// 返回选择页面
const goBackToSelection = () => {
  currentStep.value = 1
  // 清空图表实例，下次重新渲染
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }
  if (moduleChart) {
    moduleChart.dispose()
    moduleChart = null
  }
}

// 重新分析
const refreshAnalysis = async () => {
  // 清空现有分析结果
  summaryData.value = null
  aiInsight.value = ''
  
  // 重新生成分析
  await generateSummary()
}

// 生成 AI 洞察
const generateAIInsight = async () => {
  if (!summaryData.value) return

  aiAnalyzing.value = true
  try {
    // 调用新的 AI 洞察生成接口（后端直接调用 AI，无需经过 Dify）
    const response = await api.post('/data-factory/bug-analysis/generate-insight/', {
      summary_data: summaryData.value
    })

    console.log('AI 响应:', response.data)

    // 提取洞察内容
    if (response.data.success) {
      aiInsight.value = response.data.data?.insight || 'AI 分析完成，但未返回有效内容'
    } else {
      ElMessage.error(response.data.message || 'AI 洞察生成失败')
    }
  } catch (error) {
    console.error('AI 洞察生成失败:', error)
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('AI 洞察生成超时，请稍后重试')
    } else {
      ElMessage.error(error.response?.data?.message || 'AI 洞察生成失败')
    }
  } finally {
    aiAnalyzing.value = false
  }
}

// 渲染 Markdown
const renderMarkdown = (text) => {
  return marked(text || '')
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 监听窗口大小变化，调整图表
window.addEventListener('resize', () => {
  trendChart?.resize()
  moduleChart?.resize()
})
</script>

<style scoped>
/* 页面容器 - 参考 XMindConverter.vue 紫色主题 */
.bug-analysis-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
}

/* 顶部筛选栏 - 紫色主题卡片样式 */
.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.filter-bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 顶部时间聚合维度选择器 */
.group-by-selector-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-by-selector-top .label {
  color: #5a32a3;
  font-size: 14px;
  font-weight: 500;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #5a32a3;
}

.page-subtitle {
  color: #9370db;
  font-size: 13px;
}

.filter-bar-spacer {
  flex: 1;
}

.filter-bar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 状态标签 */
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.2);
  border-radius: 6px;
  font-size: 13px;
  color: #7b42f6;
  font-weight: 500;
}

.status-tag.success {
  background: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

.status-icon {
  font-size: 14px;
}

/* 返回按钮栏 */
.back-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 步骤内容区域 */
.step-content-area {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 记录列表空状态 */
.records-empty {
  padding: 40px 0;
}

/* 卡片容器 - 参考 XMindConverter.vue 紫色主题 */
.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #5a32a3;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 10px;
  border-left: 4px solid #7b42f6;
}

.header-title .el-icon {
  font-size: 18px;
  color: #7b42f6;
}

/* 表格样式 - 与参考文件 XMindConverter.vue 一致 */
.records-selector {
  margin-bottom: 20px;

  /* 覆盖 Element Plus 默认主题变量 */
  --el-color-primary: #7b42f6;
  --el-border-color: #e9ecef;
  --el-border-color-light: #e9ecef;
  --el-border-color-lighter: #e9ecef;
  --el-fill-color-light: #ffffff;
  --el-fill-color-lighter: #ffffff;
  --el-fill-color-blank: #ffffff;
  --el-text-color-primary: #333;
  --el-text-color-regular: #333;
  --el-text-color-secondary: #666;
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;
  --el-table-stripe-bg-color: #fafaff;

  &::before {
    display: none;
  }

  /* 表头包装器 */
  :deep(.el-table__header-wrapper) {
    background-color: #ffffff !important;
  }

  :deep(.el-table__header) {
    background-color: #ffffff !important;
  }

  /* 表头单元格样式 */
  :deep(th) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600;
    font-size: 14px;
    border-bottom: 1px solid #e9ecef;
    padding: 0 !important;
    text-align: center;
    transition: all 0.3s ease;

    &:hover {
      background-color: #ffffff !important;
    }
  }

  :deep(th .cell) {
    background-color: #ffffff !important;
    color: #5a32a3 !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    line-height: 24px !important;
    padding: 16px !important;
  }

  /* 表格体样式 */
  :deep(.el-table__body-wrapper) {
    background-color: #ffffff !important;
  }

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
  }

  :deep(td) {
    padding: 14px 16px;
    border-bottom: 1px solid #e9ecef;
    color: #333;
    font-size: 14px;
    font-weight: 400;
    line-height: 24px;
    transition: all 0.3s ease;
    vertical-align: middle;
  }

  /* 空状态样式 */
  :deep(.el-table__empty-block) {
    padding: 60px 0;
    background: #ffffff !important;
  }

  :deep(.el-table__empty-text) {
    color: #666;
    font-size: 14px;
    line-height: 24px;
  }
}

/* 数据单元格内容样式 */
.file-name {
  color: #5a32a3;
  font-weight: 500;
}

.index-number {
  display: inline-block;
  min-width: 24px;
  padding: 2px 6px;
  background: rgba(147, 112, 219, 0.1);
  color: #7b42f6;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

.count-badge {
  display: inline-block;
  min-width: 28px;
  padding: 2px 8px;
  background: rgba(147, 112, 219, 0.1);
  color: #7b42f6;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}

.p0-badge {
  display: inline-block;
  min-width: 28px;
  padding: 2px 8px;
  background: #fef0f0;
  color: #f56c6c;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}

.text-gray {
  color: #909399;
}

.time-text {
  color: #606266;
  font-size: 13px;
}

.generate-btn {
  margin-left: 8px;
}

/* Tab 导航 - 紫色主题 */
.tab-navigation {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 4px;
  background: rgba(147, 112, 219, 0.08);
  border-radius: 6px;
  width: fit-content;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #7b42f6;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #5a32a3;
  background: rgba(147, 112, 219, 0.15);
}

.tab-item.active {
  background: #fff;
  color: #5a32a3;
  font-weight: 500;
  box-shadow: 0 1px 4px rgba(147, 112, 219, 0.2);
}

.tab-item .el-icon {
  font-size: 16px;
}

/* 汇总统计卡片 - 紫色主题 */
.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(147, 112, 219, 0.12);
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  transition: all 0.3s;
  height: 100%;
}

.summary-card:hover {
  box-shadow: 0 6px 20px rgba(147, 112, 219, 0.15);
  transform: translateY(-2px);
}

.summary-card.has-risk {
  border-color: #ff4d4f;
  background: #fff1f0;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.summary-info {
  flex: 1;
  min-width: 0;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #5a32a3;
  line-height: 1.2;
}

.summary-label {
  font-size: 13px;
  color: #7b42f6;
  margin-top: 4px;
  font-weight: 500;
}

.summary-sub {
  font-size: 12px;
  color: #9370db;
  margin-top: 2px;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 20px;
}

.chart-row {
  margin-bottom: 16px;
}

.chart-card {
  height: 100%;
}

.chart-container {
  height: 320px;
  width: 100%;
}

/* 风险预警 */
.risk-section {
  margin-bottom: 20px;
}

.growth-rate {
  font-weight: 600;
  font-size: 14px;
}

.growth-rate.high-risk {
  color: #cf1322;
}

.growth-rate.medium-risk {
  color: #fa8c16;
}

.mini-trend {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 30px;
}

.trend-point {
  width: 8px;
  background: #7b42f6;
  border-radius: 2px;
  min-height: 4px;
}

/* AI 洞察 - 紫色主题 */
.ai-section {
  margin-bottom: 20px;
}

.ai-content {
  padding: 20px;
  background: linear-gradient(135deg, #f5f3ff 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid rgba(147, 112, 219, 0.2);
  box-shadow: 0 2px 8px rgba(147, 112, 219, 0.1);
}

.ai-insight {
  line-height: 1.8;
  color: #262626;
  font-size: 14px;
}

.ai-insight :deep(h1), .ai-insight :deep(h2), .ai-insight :deep(h3) {
  color: #7b42f6;
  font-weight: 600;
  margin: 20px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(147, 112, 219, 0.2);
}

.ai-insight :deep(h1:first-child), .ai-insight :deep(h2:first-child), .ai-insight :deep(h3:first-child) {
  margin-top: 0;
}

.ai-insight :deep(ul) {
  padding-left: 0;
  list-style: none;
}

.ai-insight :deep(li) {
  margin: 8px 0;
  padding-left: 20px;
  position: relative;
}

.ai-insight :deep(li::before) {
  content: '';
  position: absolute;
  left: 6px;
  top: 10px;
  width: 6px;
  height: 6px;
  background: #7b42f6;
  border-radius: 50%;
}

.ai-insight :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(147, 112, 219, 0.1);
}

.ai-insight :deep(th) {
  background: rgba(147, 112, 219, 0.1);
  color: #5a32a3;
  font-weight: 600;
  padding: 12px 16px;
  text-align: left;
  font-size: 13px;
  border-bottom: 2px solid rgba(147, 112, 219, 0.2);
}

.ai-insight :deep(td) {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
  vertical-align: top;
}

.ai-insight :deep(tr:last-child td) {
  border-bottom: none;
}

.ai-insight :deep(tr:hover td) {
  background: rgba(147, 112, 219, 0.05);
}

.ai-insight :deep(strong) {
  color: #5a32a3;
  font-weight: 600;
}

.ai-insight :deep(p) {
  margin: 12px 0;
}

.ai-insight :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(147, 112, 219, 0.3), transparent);
  margin: 20px 0;
}

.ai-placeholder {
  padding: 40px 0;
}
</style>
