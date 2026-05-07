<template>
  <div class="team-statistics-container">
    <!-- 数据概览 -->
    <div class="stats-section">
      <div class="section-header">
        <h3 class="section-title">
          <el-icon><Odometer /></el-icon>
          数据概览
        </h3>
        <div class="filter-section">
          <el-date-picker
            v-model="selectedMonth"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            :clearable="false"
            @change="handleMonthChange"
          />
          <!-- 导出按钮暂时隐藏
          <el-button type="primary" @click="exportData" :loading="exportLoading">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
          -->
        </div>
      </div>
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value green">{{ overviewStats.interface_count || 0 }}</div>
            <div class="stat-label">接口数量</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value orange">{{ overviewStats.suite_count || 0 }}</div>
            <div class="stat-label">测试场景</div>
          </el-card>
        </el-col>
        <el-col :span="4" v-for="(item, index) in teamSummaryStats" :key="index">
          <el-card shadow="hover" class="stat-card highlight">
            <div class="stat-value" :class="item.class">{{ item.value }}</div>
            <div class="stat-label">{{ item.label }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 团队统计 -->
    <div class="team-stats">

      <!-- 排行榜 -->
      <div class="stats-section rank-section">
        <h3 class="section-title">
          <el-icon><Stamp /></el-icon>
          维护场景
        </h3>
        <el-table
          :data="reviewRank"
          style="width: 100%"
          v-loading="loading"
          empty-text="暂无数据"
          class="rank-table"
        >
          <el-table-column type="index" label="排名" width="80" align="center">
            <template #default="{ $index }">
              <div class="rank-badge" :class="{ 'has-medal': $index < 3, 'no-medal': $index >= 3 }">
                <span v-if="$index < 3" class="rank-icon">{{ ['🥇', '🥈', '🥉'][$index] }}</span>
                <span v-else class="rank-number">{{ $index + 1 }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="姓名" min-width="80" align="center" />
          <el-table-column prop="total_count" label="总创建" min-width="80" align="center" />
          <el-table-column prop="approved_count" label="已通过" min-width="80" align="center" />
          <el-table-column prop="pending_count" label="待评审" min-width="80" align="center" />
          <el-table-column prop="rejected_count" label="已拒绝" min-width="80" align="center" />
          <el-table-column prop="pass_rate" label="通过率" min-width="80" align="center">
            <template #default="{ row }">
              <span class="pass-rate-badge" :class="getPassRateClass(row.pass_rate)">
                {{ Number(row.pass_rate).toFixed(1) }}%
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 趋势图表 -->
    <div class="stats-section trend-section">
      <h3 class="section-title">
        <el-icon><TrendCharts /></el-icon>
        近6个月趋势
      </h3>
      <el-card shadow="hover" class="chart-card">
        <div ref="trendChart" class="chart-container" v-loading="chartLoading"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, OfficeBuilding,
  Stamp, TrendCharts, Download, Odometer
} from '@element-plus/icons-vue'
import { getTeamStats, getMonthlyTrend, getDashboardStats } from '@/api/api-testing'
import * as echarts from 'echarts'

// 数据加载状态
const loading = ref(false)
const chartLoading = ref(false)
const exportLoading = ref(false)

// 筛选条件
const selectedMonth = ref(getCurrentMonth())

// 统计数据
const teamStats = ref({
  team_summary: {},
  execution_rank: [],
  review_rank: []
})
const trendData = ref([])
const overviewStats = ref({
  project_count: 0,
  interface_count: 0,
  suite_count: 0,
  history_count: 0
})

// 图表实例
const trendChart = ref(null)
let chartInstance = null

// 获取当前月份
function getCurrentMonth() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

// 团队总体统计数据
const teamSummaryStats = computed(() => {
  const summary = teamStats.value.team_summary || {}
  return [
    { label: '总执行次数', value: summary.total_execution_count || 0, class: 'pink' },
    { label: '总通过用例', value: summary.total_passed_cases || 0, class: 'green' },
    { label: '总失败用例', value: summary.total_failed_cases || 0, class: 'danger' },
    { label: '平均通过率', value: `${summary.total_pass_rate || 0}%`, class: 'gold' }
  ]
})

// 排行榜数据
const reviewRank = computed(() => {
  return teamStats.value.review_rank || []
})

// 获取通过率样式
function getPassRateClass(rate) {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'danger'
}

// 获取通过率标签类型
function getPassRateType(rate) {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'danger'
}

// 加载团队统计数据
async function loadTeamStats() {
  loading.value = true
  try {
    const res = await getTeamStats({ month: selectedMonth.value })
    teamStats.value = res.data
  } catch (error) {
    console.error('加载团队统计失败:', error)
    ElMessage.error('加载团队统计失败')
  } finally {
    loading.value = false
  }
}

// 加载数据概览
async function loadOverviewStats() {
  try {
    const res = await getDashboardStats()
    overviewStats.value = res.data
  } catch (error) {
    console.error('加载数据概览失败:', error)
  }
}

// 加载趋势数据
async function loadTrendData() {
  chartLoading.value = true
  try {
    const res = await getMonthlyTrend({ months: 6 })
    trendData.value = res.data.trends || []
    nextTick(() => {
      initTrendChart()
    })
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  } finally {
    chartLoading.value = false
  }
}

// 初始化趋势图表
function initTrendChart() {
  if (!trendChart.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(trendChart.value)

  const months = trendData.value.map(item => item.month)
  const executionCounts = trendData.value.map(item => item.execution_count)
  const passRates = trendData.value.map(item => item.pass_rate)
  const reviewCounts = trendData.value.map(item => item.review_count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['执行次数', '通过率(%)', '评审次数'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: {
        rotate: 0,
        color: '#4b5563'
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '次数',
        position: 'left',
        nameTextStyle: {
          color: '#4b5563'
        },
        axisLine: {
          show: true,
          lineStyle: {
            color: 'rgba(147, 112, 219, 0.3)'
          }
        },
        axisLabel: {
          color: '#4b5563'
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: 'rgba(147, 112, 219, 0.06)',
            type: 'dashed'
          }
        }
      },
      {
        type: 'value',
        name: '百分比(%)',
        position: 'right',
        max: 100,
        nameTextStyle: {
          color: '#4b5563'
        },
        axisLine: {
          show: true,
          lineStyle: {
            color: 'rgba(147, 112, 219, 0.3)'
          }
        },
        axisLabel: {
          formatter: '{value}%',
          color: '#4b5563'
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '执行次数',
        type: 'bar',
        data: executionCounts,
        itemStyle: {
          color: '#7b42f6'
        }
      },
      {
        name: '通过率(%)',
        type: 'line',
        yAxisIndex: 1,
        data: passRates,
        itemStyle: {
          color: '#52c41a'
        },
        lineStyle: {
          width: 3
        }
      },
      {
        name: '评审次数',
        type: 'bar',
        data: reviewCounts,
        itemStyle: {
          color: '#faad14'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 月份切换
function handleMonthChange() {
  loadTeamStats()
}

// 导出数据
function exportData() {
  exportLoading.value = true

  const data = [
    ['团队统计', '数值'],
    ['统计月份', selectedMonth.value],
    ['总执行次数', teamStats.value.team_summary?.total_execution_count || 0],
    ['总通过用例', teamStats.value.team_summary?.total_passed_cases || 0],
    ['总失败用例', teamStats.value.team_summary?.total_failed_cases || 0],
    ['平均通过率', `${teamStats.value.team_summary?.total_pass_rate || 0}%`]
  ]

  // 添加已通过排行
  data.push(['', ''])
  data.push(['已通过排行', ''])
  data.push(['排名', '成员', '总创建', '已通过', '待评审', '已拒绝', '通过率'])
  reviewRank.value.forEach((item, index) => {
    data.push([index + 1, item.username, item.total_count, item.approved_count, item.pending_count, item.rejected_count, `${item.pass_rate}%`])
  })

  const filename = `团队统计_${selectedMonth.value}.csv`

  // 转换为CSV
  const csvContent = data.map(row => row.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()

  exportLoading.value = false
  ElMessage.success('导出成功')
}

// 初始化
onMounted(() => {
  loadOverviewStats()
  loadTeamStats()
  loadTrendData()

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})
</script>

<style lang="scss" scoped>
.team-statistics-container {
  padding: 20px 24px 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #6d28d9;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;

  .el-icon {
    font-size: 26px;
    color: #7b42f6;
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    padding: 8px;
    border-radius: 10px;
  }
}

.stats-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #6d28d9;
  margin-bottom: 0;
  display: flex;
  align-items: center;
  gap: 8px;

  .el-icon {
    color: #7c3aed;
    font-size: 18px;
  }
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;

  .el-button {
    .el-icon {
      margin-right: 6px;
    }

    &.el-button--primary {
      background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
      border: none;

      &:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
      }
    }
  }
}

.stat-card {
  text-align: center;
  padding: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.3s ease;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(147, 112, 219, 0.15);
  }

  &.highlight {
    background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);

    .stat-label {
      color: #6b7280;
    }

    &.stat-card:hover {
      box-shadow: 0 8px 24px rgba(147, 112, 219, 0.15);
    }
  }
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 6px;
  color: #6d28d9;

  &.primary {
    color: #6d28d9;
  }

  &.success {
    color: #7c3aed;
  }

  &.warning {
    color: #8b5cf6;
  }

  &.danger {
    color: #ef4444;
  }

  &.info {
    color: #a78bfa;
  }

  &.pink {
    color: #db2777;
  }

  &.green {
    color: #16a34a;
  }

  &.orange {
    color: #ea580c;
  }

  &.purple {
    color: #7c3aed;
  }

  &.gold {
    color: #d97706;
  }
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.stat-sub {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 4px;
}

// 概览卡片样式
.overview-card {
  padding: 0;
  overflow: hidden;

  :deep(.el-card__body) {
    padding: 0;
  }

  .stat-content {
    display: flex;
    align-items: center;
    padding: 20px;
  }

  .stat-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    flex-shrink: 0;

    .el-icon {
      font-size: 26px;
      color: white;
    }

    &.bg-blue {
      background: linear-gradient(135deg, #5b8ff9 0%, #4472d4 100%);
      box-shadow: 0 4px 12px rgba(91, 143, 249, 0.35);
    }

    &.bg-green {
      background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
      box-shadow: 0 4px 12px rgba(82, 196, 26, 0.35);
    }

    &.bg-purple {
      background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
      box-shadow: 0 4px 12px rgba(124, 58, 237, 0.35);
    }

    &.bg-orange {
      background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
      box-shadow: 0 4px 12px rgba(250, 173, 20, 0.35);
    }
  }

  .stat-info {
    flex: 1;
    text-align: left;

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 4px;
      line-height: 1.2;
    }

    .stat-label {
      font-size: 13px;
      color: #6b7280;
      font-weight: 500;
    }
  }
}

.rank-section {
  margin-top: 20px;

  .section-title {
    margin-bottom: 14px;
  }

  .rank-table {
    border-radius: 16px;
    background: #ffffff;
    border: none;
    overflow: hidden;

    :deep(.el-table__header-wrapper) {
      background: #f8f7ff;
    }

    :deep(.el-table__header) {
      background: transparent;

      th.el-table__cell {
        background: transparent;
        color: #6d28d9;
        font-weight: 600;
        font-size: 14px;
        border-bottom: 1px solid #e8e0ff;
        padding: 16px 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
    }

    :deep(.el-table__body) {
      background: transparent;

      tr {
        transition: all 0.2s ease;

        &:nth-child(even) {
          background: #fafaff;
        }

        &:hover {
          background: #f0edff !important;
          transform: translateX(2px);
        }

        &.hover-row {
          background: #f0edff !important;
        }
      }

      td.el-table__cell {
        border-bottom: 1px solid #f0edff;
        padding: 14px 8px;
        color: #374151;
        font-size: 14px;
      }
    }

    :deep(.el-table__empty-block) {
      background: transparent;
      padding: 60px 0;
    }

    :deep(.el-table__inner-wrapper::before) {
      display: none;
    }
  }
}

.rank-badge {
  width: 32px;
  height: 32px;
  line-height: 32px;
  font-size: 16px;
  margin: 0 auto;
  color: #6b7280;
  font-weight: 600;

  .rank-icon {
    font-size: 22px;
    line-height: 1;
  }

  .rank-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
  }

  // 4名以后显示圆形灰色背景
  &.no-medal {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    border: 1px solid #e5e7eb;
    font-size: 12px;
    color: #6b7280;
    box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.8);
    line-height: 1;
  }
}

// 通过率徽章样式
.pass-rate-badge {
  font-size: 13px;
  font-weight: 600;

  &.success {
    color: #16a34a;
  }

  &.warning {
    color: #ea580c;
  }

  &.danger {
    color: #dc2626;
  }
}

.trend-section {
  .section-title {
    margin-bottom: 14px;
  }
}

.chart-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border: 1px solid rgba(147, 112, 219, 0.08);
}

.chart-container {
  height: 320px;
  width: 100%;
}

:deep(.el-table) {
  border-radius: 8px;
  background: transparent;
  min-height: 200px;

  th {
    font-weight: 600;
    color: #374151;
    background: #f9fafb;
    padding: 12px 4px;
    height: 44px;

    .cell {
      white-space: nowrap;
      line-height: 1.4;
      font-size: 12px;
    }
  }

  td {
    padding: 10px 8px;
    height: 48px;
  }

  .cell {
    font-size: 13px;
  }

  .el-empty {
    padding: 60px 0;
  }

  .el-empty__description {
    margin-top: 12px;
    color: #9ca3af;
  }
}

// 表格 body 最小高度
:deep(.el-table__body-wrapper) {
  min-height: 120px;
}

:deep(.el-radio-group) {
  .el-radio-button__inner {
    font-weight: 500;
  }
}

// 响应式优化
@media screen and (max-width: 1200px) {
  .rank-section {
    .el-col-12 {
      width: 100%;
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .team-statistics-container {
    padding: 16px;
  }

  .page-title {
    font-size: 18px;

    .el-icon {
      font-size: 22px;
      padding: 6px;
    }
  }

  .stat-content {
    padding: 16px;
  }

  .stat-icon {
    width: 44px;
    height: 44px;

    .el-icon {
      font-size: 22px;
    }
  }

  .stat-info .stat-value {
    font-size: 22px;
  }
}
</style>
