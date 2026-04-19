<template>
  <div class="bug-analysis-container">
    <!-- ==================== 列表视图 ==================== -->
    <template v-if="viewMode === 'list'">
      <!-- 顶部筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名或版本标签"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <div class="filter-bar-spacer"></div>
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传分析
        </el-button>
      </div>

      <!-- 历史记录列表 -->
      <div class="card-container history-card">
        <el-table
          ref="tableRef"
          v-loading="loadingHistory"
          :data="historyRecords"
          stripe
          style="width: 100%"
        >
          <el-table-column label="序号" width="80" header-align="center" align="center">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>

          <el-table-column label="文件名" min-width="120" show-overflow-tooltip header-align="center" align="left">
            <template #default="{ row }">
              <span class="file-name">{{ row.file_name || '未命名' }}</span>
            </template>
          </el-table-column>

          <el-table-column label="版本标签" width="160" header-align="center" align="center">
            <template #default="{ row }">
              <span v-if="row.version_tag" class="version-badge">{{ row.version_tag }}</span>
              <span v-else class="text-gray">-</span>
            </template>
          </el-table-column>

          <el-table-column label="Bug 数量" width="120" header-align="center" align="center">
            <template #default="{ row }">
              <span class="count-badge">{{ row.total_bugs || 0 }}</span>
            </template>
          </el-table-column>

          <el-table-column label="P0 风险" width="110" header-align="center" align="center">
            <template #default="{ row }">
              <span v-if="row.meta_data?.p0_count > 0" class="p0-badge">
                {{ row.meta_data.p0_count }}
              </span>
              <span v-else class="text-gray">0</span>
            </template>
          </el-table-column>



          <el-table-column label="上传时间" width="180" header-align="center" align="center">
            <template #default="{ row }">
              <span class="time-text">{{ formatDateTime(row.created_at) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right" header-align="center" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" @click="viewAnalysisDetail(row)">
                  <el-icon><View /></el-icon>
                  <span>查看</span>
                </el-button>
                <el-button size="small" type="danger" @click="handleDeleteRecord(row)">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container" v-if="!loadingHistory && historyRecords.length > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>

        <!-- 空状态 -->
        <el-empty v-if="!loadingHistory && historyRecords.length === 0" description="暂无分析记录">
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传文件开始分析
          </el-button>
        </el-empty>
      </div>
    </template>

    <!-- ==================== 分析结果详情视图 ==================== -->
    <template v-else-if="viewMode === 'detail'">
      <!-- 页面标题 -->
      <div class="detail-header">
        <div class="detail-header-left">
          <!-- 返回列表按钮已隐藏 -->
          <div class="detail-title">
            <h2>{{ currentRecord?.file_name || 'Bug 分析报告' }}</h2>
            <el-tag v-if="currentRecord?.version_tag" size="small" type="info">{{ currentRecord.version_tag }}</el-tag>
          </div>
        </div>
        <div class="detail-header-actions">
          <!-- 重新上传按钮已隐藏 -->
          <el-button type="primary" @click="showExportDialog = true">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </div>
      </div>

      <!-- 分析结果内容 -->
      <!-- 操作栏已隐藏 - 功能合并到顶部导航栏 -->

      <!-- 历史记录侧栏 (V2新增) -->
      <transition name="slide-fade">
        <div v-if="showHistory" class="history-sidebar">
          <div class="history-header">
            <span class="history-title"><el-icon><Clock /></el-icon> 分析历史</span>
            <el-button text @click="showHistory = false"><el-icon><Close /></el-icon></el-button>
          </div>
          <div class="history-list" v-loading="loadingHistory">
            <div v-for="rec in historyRecords" :key="rec.id" class="history-item" :class="{ active: rec.id === currentRecordId }" @click="loadHistoryRecord(rec)">
              <div class="history-item-main">
                <span class="history-item-name">{{ rec.file_name || rec.version_tag || `#${rec.id}` }}</span>
                <el-tag size="small" :type="rec.meta_data?.p0_count > 0 ? 'danger' : 'info'" v-if="rec.meta_data">P0:{{ rec.meta_data.p0_count }}</el-tag>
              </div>
              <div class="history-item-meta">
                <span>{{ rec.total_bugs }}条</span><span>{{ rec.created_at }}</span>
                <span class="top-mod">{{ rec.meta_data?.top_module || '' }}</span>
              </div>
            </div>
            <el-empty v-if="!loadingHistory && historyRecords.length === 0" description="暂无历史记录" :image-size="60" />
          </div>
        </div>
      </transition>

      <!-- 主内容区 -->
      <div class="main-content" :class="{ 'with-sidebar': showHistory }">

        <!-- 汇总统计卡片 -->
        <div class="summary-cards">
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="summary-card">
                <div class="summary-icon" style="background: #fef0f0; color: #e94560;"><el-icon><Document /></el-icon></div>
                <div class="summary-info">
                  <div class="summary-value">{{ (metaData && metaData.total_bugs) || 0 }}</div>
                  <div class="summary-label">Bug 总数</div>
                  <div class="summary-sub">{{ workTypesText }}</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card">
                <div class="summary-icon" style="background: #e6f7ff; color: #1890ff;"><el-icon><Grid /></el-icon></div>
                <div class="summary-info">
                  <div class="summary-value">{{ Object.keys(modulesData).length }}</div>
                  <div class="summary-label">功能模块</div>
                  <div class="summary-sub">{{ (metaData && metaData.tag_count) || 0 }} 种标签归类</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card">
                <div class="summary-icon" style="background: #f6ffed; color: #52c41a;"><el-icon><TrendCharts /></el-icon></div>
                <div class="summary-info">
                  <div class="summary-value">{{ clusterData.length }}</div>
                  <div class="summary-label">缺陷聚集点</div>
                  <div class="summary-sub">>=5条的功能聚簇</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card">
                <div class="summary-icon" style="background: #fff7e6; color: #fa8c16;"><el-icon><User /></el-icon></div>
                <div class="summary-info">
                  <div class="summary-value">{{ (metaData && metaData.creators) || 0 }}</div>
                  <div class="summary-label">参与人员</div>
                  <div class="summary-sub">Bug 提交者</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- AI 总结摘要 (V2新增) - 只在启用AI时显示 -->
        <el-card class="section-card" v-if="aiSummary || aiLoading">
          <template #header>
            <div class="card-header">
              <span class="header-title"><el-icon><MagicStick /></el-icon> AI 智能摘要</span>
              <el-tag v-if="!aiLoading" type="success" size="small" effect="dark" class="ai-status-tag success">
                AI 已生成
              </el-tag>
              <el-tag v-else size="small" effect="plain" class="ai-status-tag loading">
                AI 分析中...
              </el-tag>
            </div>
          </template>
          <!-- AI 加载状态 - 现代骨架屏 -->
          <div v-if="aiLoading && !aiSummary" class="ai-loading-container">
            <div class="ai-loading-header">
              <div class="ai-loading-pulse">
                <el-icon class="is-loading"><Loading /></el-icon>
              </div>
              <div class="ai-loading-info">
                <div class="ai-loading-title">AI 正在分析数据...</div>
                <div class="ai-loading-desc">{{ aiLoadingText }}</div>
              </div>
            </div>
            <div class="ai-skeleton">
              <div class="ai-skeleton-line"></div>
              <div class="ai-skeleton-line"></div>
              <div class="ai-skeleton-line"></div>
              <div class="ai-skeleton-line"></div>
            </div>
            <div class="ai-loading-status">
              <div class="ai-loading-dot"></div>
              <div class="ai-loading-dot"></div>
              <div class="ai-loading-dot"></div>
              <span class="ai-loading-text-new">智能分析中</span>
            </div>
          </div>
          <!-- AI 结果展示 -->
          <div v-else class="ai-summary-content" v-html="formatAiSummary(aiSummary)"></div>
        </el-card>

        <!-- 结论摘要 (原有逻辑, 无AI总结或非AI加载状态时显示) -->
        <el-card class="section-card" v-else>
          <template #header>
            <div class="card-header">
              <span class="header-title"><el-icon><InfoFilled /></el-icon> 结论摘要</span>
              <el-tag type="danger" v-if="riskData && riskData.P0 && riskData.P0.total > 0">P0 风险 {{ riskData.P0.total }} 条</el-tag>
            </div>
          </template>
          <div class="summary-content">
            <div class="summary-section danger" v-if="summaryLines.length > 0">
              <div class="summary-title">关键发现</div>
              <div class="summary-list"><div v-for="(line, index) in summaryLines" :key="index" class="summary-item" v-html="line"></div></div>
            </div>
            <div class="summary-section warning" v-if="actionLines.length > 0">
              <div class="summary-title">行动建议</div>
              <div class="summary-list"><div v-for="(line, index) in actionLines" :key="index" class="summary-item" v-html="line"></div></div>
            </div>
          </div>
        </el-card>

        <!-- 模块分布图表 -->
        <el-row :gutter="16" class="chart-row">
          <el-col :span="24">
            <el-card class="chart-card">
              <template #header>
                <span class="chart-title">模块分布
                  <el-text type="info" size="small" style="margin-left: 8px;">(点击柱状图可定位到下方测试重点卡片)</el-text>
                </span>
              </template>
              <div ref="moduleChartRef" class="chart-container clickable-chart" @click="onModuleChartClick"></div>
              <!-- 未归类提示已移除，所有内容都在柱状图中显示 -->
            </el-card>
          </el-col>
        </el-row>

        <!-- 严重度交叉分析 -->
        <el-row :gutter="16" class="chart-row">
          <el-col :span="12">
            <el-card class="chart-card"><template #header><span class="chart-title">原始严重度 → 推断严重度 交叉对照</span></template>
              <div ref="severityCrossChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card"><template #header><span class="chart-title">推断严重度分布</span></template>
              <div ref="severityPieChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 状态与优先级 -->
        <el-row :gutter="16" class="chart-row">
          <el-col :span="12">
            <el-card class="chart-card"><template #header><span class="chart-title">Bug 状态分布</span></template>
              <div ref="statusChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card"><template #header><span class="chart-title">优先级分布</span></template>
              <div ref="priorityChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 关键词词频 -->
        <el-row :gutter="16" class="chart-row">
          <el-col :span="24">
            <el-card class="chart-card"><template #header><span class="chart-title">关键词词频 Top 20</span></template>
              <div ref="keywordChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 创建者分布 -->
        <el-row :gutter="16" class="chart-row">
          <el-col :span="24">
            <el-card class="chart-card"><template #header><span class="chart-title">创建者 × 模块分布</span></template>
              <div ref="creatorChartRef" class="chart-container" style="height: 400px;"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 时间趋势 -->
        <el-row :gutter="16" class="chart-row">
          <el-col :span="24">
            <el-card class="chart-card">
              <template #header>
                <span class="chart-title">Bug 创建时间趋势
                  <el-tag v-if="metaData && metaData.import_count > 0" size="small" type="info">已排除 {{ metaData.import_count }} 条平台导入数据</el-tag>
                </span>
              </template>
              <div ref="timelineChartRef" class="chart-container" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 风险分析表格 -->
        <el-card class="section-card">
          <template #header><div class="card-header"><span class="header-title"><el-icon><Warning /></el-icon>回归风险分析</span></div></template>
          <div class="risk-section">
            <h4 class="risk-title p0">P0 — 必须回归 (服务中断/应用崩溃)</h4>
            <el-table :data="p0RiskData" border style="width: 100%">
              <el-table-column prop="type" label="风险类型" min-width="180"><template #default="{ row }"><el-tag :type="row.tagType" effect="dark">{{ row.type }}</el-tag></template></el-table-column>
              <el-table-column prop="count" label="Bug数量" width="100" align="center" /><el-table-column prop="percentage" label="占比" width="100" align="center" />
              <el-table-column prop="rule" label="计算规则" min-width="180" /><el-table-column prop="desc" label="说明" />
            </el-table>
          </div>
          <div class="risk-section">
            <h4 class="risk-title p1">P1 — 应该回归 (功能阻塞/修复质量存疑)</h4>
            <el-table :data="p1RiskData" border style="width: 100%">
              <el-table-column prop="type" label="风险类型" min-width="180"><template #default="{ row }"><el-tag :type="row.tagType" effect="dark">{{ row.type }}</el-tag></template></el-table-column>
              <el-table-column prop="count" label="Bug数量" width="100" align="center" /><el-table-column prop="percentage" label="占比" width="100" align="center" />
              <el-table-column prop="rule" label="计算规则" min-width="180" /><el-table-column prop="desc" label="说明" />
            </el-table>
          </div>
          <div class="risk-section">
            <h4 class="risk-title p2">P2 — 按需回归 (影响较轻/边界场景)</h4>
            <el-table :data="p2RiskData" border style="width: 100%">
              <el-table-column prop="type" label="风险类型" min-width="180"><template #default="{ row }"><el-tag :type="row.tagType">{{ row.type }}</el-tag></template></el-table-column>
              <el-table-column prop="count" label="Bug数量" width="100" align="center" /><el-table-column prop="percentage" label="占比" width="100" align="center" />
              <el-table-column prop="rule" label="计算规则" min-width="180" /><el-table-column prop="desc" label="说明" />
            </el-table>
          </div>
        </el-card>

        <!-- 模块测试重点 - AI智能分析版 -->
        <el-card class="section-card" v-if="Object.keys(testFocusData).length > 0">
          <template #header>
            <div class="card-header">
              <span class="header-title"><el-icon><List /></el-icon>模块迭代测试重点</span>
              <div class="header-actions">
                <el-text type="info" size="small">(基于AI三层架构智能分析)</el-text>
                <el-button
                  type="primary"
                  size="small"
                  :loading="isAnalyzingAllModules"
                  :disabled="isAllModulesAnalyzed"
                  @click="analyzeAllModules"
                  class="ai-analyze-btn"
                >
                  <el-icon><MagicStick /></el-icon>
                  {{ isAllModulesAnalyzed ? 'AI分析完成' : 'AI智能分析' }}
                </el-button>
              </div>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :span="12" v-for="(info, module) in testFocusData" :key="module">
              <div :ref="el => setModuleCardRef(el, module)" 
                   :id="`module-card-${module}`"
                   class="focus-card" 
                   @click="openModuleDetail(module)" 
                   :class="{ clickable: currentRecordId, highlighted: highlightedModule === module }">
                <!-- AI分析结果展示 -->
                <div v-if="aiModuleFocus[module]" class="ai-focus-card">
                  <div class="focus-header">
                    <span class="focus-name">{{ module }}</span>
                    <div class="focus-badges">
                      <el-tag v-if="aiModuleFocus[module].risk_level === 'high'" type="danger" size="small" effect="light">高风险</el-tag>
                      <el-tag v-else-if="aiModuleFocus[module].risk_level === 'medium'" type="warning" size="small" effect="light">中风险</el-tag>
                      <el-tag v-else type="success" size="small" effect="light">低风险</el-tag>
                      <el-tag type="info" size="small" effect="plain" style="margin-left: 4px;">{{ aiModuleFocus[module].total_count }}条</el-tag>
                    </div>
                  </div>
                  <div class="focus-body ai-body">
                    <!-- AI智能分析点 -->
                    <div class="ai-section-title">智能分析</div>
                    <div v-for="(point, idx) in aiModuleFocus[module].focus_points?.slice(0, 3)" :key="idx" 
                         class="ai-point-item" :class="point.level">
                      <div class="ai-point-type">
                        <el-tag :type="point.level==='high'?'danger':point.level==='medium'?'warning':'info'" size="small" effect="light">
                          {{ point.type }}
                        </el-tag>
                      </div>
                      <div class="ai-point-desc">{{ point.description }}</div>
                    </div>
                    <div v-if="aiModuleFocus[module].focus_points?.length > 3" class="more-points-hint">
                      +{{ aiModuleFocus[module].focus_points.length - 3 }} 更多...
                    </div>
                    <!-- 基础测试关注点 -->
                    <div class="base-section-title">基础关注点</div>
                    <ul class="focus-points base-focus-points">
                      <li v-for="(point, idx) in info.focus_points?.slice(0, 3)" :key="idx">{{ point }}</li>
                    </ul>
                    <div v-if="info.focus_points?.length > 3" class="more-points-hint">
                      +{{ info.focus_points.length - 3 }} 更多...
                    </div>
                  </div>
                </div>
                <!-- AI分析加载中 -->
                <div v-else-if="moduleFocusLoading[module]" class="ai-loading-card">
                  <div class="focus-header">
                    <span class="focus-name">{{ module }}</span>
                  </div>
                  <div class="ai-loading-body">
                    <el-skeleton :rows="2" animated />
                    <div class="ai-loading-text">AI分析中...</div>
                  </div>
                </div>
                <!-- 基础统计（降级显示） -->
                <div v-else>
                  <div class="focus-header">
                    <span class="focus-name">{{ module }}</span>
                    <div class="focus-badges">
                      <el-tag v-if="info.online >= 20" type="danger" size="small">线上故障多({{ info.online }}条)</el-tag>
                      <el-tag v-else-if="info.online >= 5" type="warning" size="small">有线上故障({{ info.online }}条)</el-tag>
                      <el-tag v-if="info.reopened > 0" type="danger" size="small" style="margin-left: 8px;">二次回归({{ info.reopened }}条)</el-tag>
                    </div>
                  </div>
                  <div class="focus-body">
                    <div class="focus-stats"><span>总计: {{ info.total }} 条</span><span>Top缺陷: {{ info.top_types.map(t => t[0]).slice(0, 2).join(', ') }}</span></div>
                    <ul class="focus-points"><li v-for="(point, idx) in info.focus_points" :key="idx">{{ point }}</li></ul>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div><!-- end main-content -->

      <!-- ===== 模块详情抽屉 (V2新增) ===== -->
      <el-drawer v-model="moduleDrawerVisible" :title="'模块详情: ' + selectedModule" direction="rtl" size="50%" destroy-on-close>
        <template #header>
          <div class="drawer-header">
            <span>{{ selectedModule }}</span>
            <el-space>
              <el-tag v-if="selectedModuleStats.online > 0" type="danger" size="small">线上故障 {{ selectedModuleStats.online }}</el-tag>
              <el-tag v-if="selectedModuleStats.reopened > 0" type="warning" size="small">二次打开 {{ selectedModuleStats.reopened }}</el-tag>
            </el-space>
          </div>
        </template>
        <div v-loading="loadingModuleDetail">
          <el-descriptions :column="3" border size="small" class="module-stats-desc">
            <el-descriptions-item label="总Bug数">{{ selectedModuleStats.total || '-' }}</el-descriptions-item>
            <el-descriptions-item label="线上故障">{{ selectedModuleStats.online || 0 }}</el-descriptions-item>
            <el-descriptions-item label="二次打开">{{ selectedModuleStats.reopened || 0 }}</el-descriptions-item>
          </el-descriptions>
          <!-- 缺陷类型分布 -->
          <div class="detail-section" v-if="selectedModuleStats.dtype_dist">
            <h4 class="detail-section-title">缺陷类型分布</h4>
            <div class="dtype-tags"><el-tag v-for="(count, dtype) in selectedModuleStats.dtype_dist" :key="dtype" :type="dtypeTagType(dtype)" effect="plain" round style="margin: 4px;">{{ dtype }} ({{ count }})</el-tag></div>
          </div>
          <!-- 智能模块测试重点 (三层架构) -->
          <div class="detail-section ai-section intelligent-focus" v-if="aiModuleFocus[selectedModule]||moduleFocusLoading[selectedModule]">
            <h4 class="detail-section-title ai-title">
              <el-icon><MagicStick /></el-icon> 智能测试重点
              <el-tag v-if="aiModuleFocus[selectedModule]?.risk_level==='high'" type="danger" size="small" effect="light" style="margin-left: 8px;">高风险</el-tag>
              <el-tag v-else-if="aiModuleFocus[selectedModule]?.risk_level==='medium'" type="warning" size="small" effect="light" style="margin-left: 8px;">中风险</el-tag>
              <el-tag v-else-if="aiModuleFocus[selectedModule]?.risk_level==='low'" type="success" size="small" effect="light" style="margin-left: 8px;">低风险</el-tag>
              <el-tag v-if="aiModuleFocus[selectedModule]?.cached" type="info" size="small" effect="plain" style="margin-left: 8px;">缓存</el-tag>
            </h4>
            <div v-loading="moduleFocusLoading[selectedModule]" class="intelligent-focus-content">
              <div v-if="aiModuleFocus[selectedModule]" class="focus-points-intelligent">
                <div v-for="(point, idx) in aiModuleFocus[selectedModule].focus_points" :key="idx" 
                     class="focus-point-item" :class="point.level">
                  <div class="point-header">
                    <el-tag :type="point.level==='high'?'danger':point.level==='medium'?'warning':'info'" size="small" effect="light">
                      {{ point.type }}
                    </el-tag>
                    <span v-if="point.source==='layer1'" class="point-source">统计</span>
                    <span v-else-if="point.source==='layer2'" class="point-source ai">AI洞察</span>
                    <span v-else-if="point.source==='layer3'" class="point-source">关联</span>
                  </div>
                  <div class="point-desc">{{ point.description }}</div>
                  <div class="point-suggestion" v-if="point.test_suggestion">
                    <el-icon><Check /></el-icon> {{ point.test_suggestion }}
                  </div>
                  <div class="point-root-cause" v-if="point.root_cause">
                    <el-text type="info" size="small">根因: {{ point.root_cause }}</el-text>
                  </div>
                </div>
              </div>
              <div v-else class="focus-loading-hint">AI 正在分析模块特征...</div>
            </div>
            <!-- 技术洞察 -->
            <div v-if="aiModuleFocus[selectedModule]?.layer2_insights?.technical_insights" class="technical-insights">
              <el-divider content-position="left">技术洞察</el-divider>
              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item label="主要问题域">{{ aiModuleFocus[selectedModule].layer2_insights.technical_insights.primary_domain }}</el-descriptions-item>
                <el-descriptions-item label="架构关注点" v-if="aiModuleFocus[selectedModule].layer2_insights.technical_insights.architecture_concern">
                  {{ aiModuleFocus[selectedModule].layer2_insights.technical_insights.architecture_concern }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          <!-- AI 测试建议 (旧版兼容) -->
          <div class="detail-section ai-section" v-if="getAiTestFocus(selectedModule)">
            <h4 class="detail-section-title ai-title"><el-icon><MagicStick /></el-icon> AI 测试建议</h4>
            <div class="ai-content" v-html="formatAiFocus(getAiTestFocus(selectedModule))"></div>
          </div>
          <!-- AI 根因假设 -->
          <div class="detail-section ai-section" v-if="getAiRootCause(selectedModule)">
            <h4 class="detail-section-title ai-title"><el-icon><Search /></el-icon> AI 根因假设</h4>
            <div class="ai-content cause-content">{{ getAiRootCause(selectedModule) }}</div>
          </div>
          <!-- 基础测试关注点 -->
          <div class="detail-section" v-if="selectedModuleStats.focus_points">
            <h4 class="detail-section-title">基础测试关注点</h4>
            <ul class="focus-points-list"><li v-for="(point, idx) in selectedModuleStats.focus_points" :key="idx">{{ point }}</li></ul>
          </div>
          <!-- Bug 明细表格 -->
          <div class="detail-section bug-list-section">
            <h4 class="detail-section-title">Bug 明细列表 <el-text type="info" size="small">({{ filteredModuleBugs.length }} 条)</el-text></h4>
            <div class="bug-filter-bar">
              <el-input v-model="bugFilter.keyword" placeholder="搜索标题..." clearable size="small" style="width: 200px;" prefix-icon="Search" />
              <el-select v-model="bugFilter.severity" placeholder="严重度" clearable size="small" style="width: 130px;"><el-option label="P0" value="P0"/><el-option label="P1" value="P1"/><el-option label="P2" value="P2"/></el-select>
              <el-select v-model="bugFilter.defectType" placeholder="缺陷类型" clearable size="small" style="width: 140px;"><el-option v-for="dt in Object.keys(selectedModuleStats.dtype_dist || {})" :key="dt" :label="dt" :value="dt"/></el-select>
            </div>
            <el-table :data="filteredModuleBugs" border size="small" max-height="400" stripe>
              <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
              <el-table-column prop="inferred_sev" label="推断严重度" width="90" align="center"><template #default="{ row }"><el-tag :type="sevTagType(row.inferred_sev)" size="small">{{ row.inferred_sev }}</el-tag></template></el-table-column>
              <el-table-column prop="defect_type" label="缺陷类型" width="100" align="center" />
              <el-table-column prop="status" label="状态" width="90" align="center" />
              <el-table-column prop="creator" label="创建者" width="90" align="center" />
              <el-table-column prop="created" label="创建时间" width="120" align="center" sortable />
            </el-table>
          </div>
        </div>
      </el-drawer>

      <!-- ===== 回归导出对话框 (V2新增) ===== -->
      <el-dialog v-model="showExportDialog" title="导出回归清单" width="560px" destroy-on-close>
        <div class="export-options">
          <el-form label-width="120px">
            <el-form-item label="导出格式:"><el-radio-group v-model="exportFormat"><el-radio value="markdown">Markdown</el-radio><el-radio value="excel">Excel</el-radio></el-radio-group></el-form-item>
            <el-form-item label="导出范围:"><el-radio-group v-model="exportScope"><el-radio value="all">全部模块</el-radio><el-radio value="top5">Top5 模块</el-radio><el-radio value="custom">自定义</el-radio></el-radio-group></el-form-item>
            <el-form-item v-if="exportScope === 'custom'" label="选择模块:">
              <el-select v-model="exportCustomModules" multiple collapse-tags placeholder="选择要导出的模块">
                <el-option v-for="(cnt, mod) in modulesData" :key="mod" :label="`${mod} (${cnt})`" :value="mod" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
        <template #footer><el-button @click="showExportDialog = false">取消</el-button><el-button type="primary" @click="doExport" :loading="exporting"><el-icon><Download /></el-icon> 导出</el-button></template>
      </el-dialog>

    </template>
    <!-- end detail view -->

    <!-- ==================== 上传对话框 ==================== -->
    <el-dialog v-model="showUploadDialog" title="上传 Bug 文件分析" width="600px" destroy-on-close>
      <el-upload
        class="upload-area"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
        :disabled="analyzing"
      >
        <el-icon class="upload-icon" :class="{ 'is-loading': analyzing }">
          <component :is="analyzing ? 'Loading' : 'UploadFilled'" />
        </el-icon>
        <div class="upload-text">
          <p v-if="!analyzing">拖拽 Excel 文件到此处，或 <em>点击上传</em></p>
          <p v-else class="analyzing-text"><el-icon class="is-loading"><Loading /></el-icon>正在分析中，请稍候...</p>
          <p class="upload-tip">支持从云效导出的 .xlsx/.xls 格式 Bug 清单</p>
        </div>
      </el-upload>

      <!-- 版本标签配置 - 紫色调 -->
      <div class="version-config" style="margin-top: 24px; padding: 20px; background: linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%); border-radius: 8px; border: 1px solid rgba(147,112,219,0.2);">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
          <el-icon style="color: #7b42f6; font-size: 18px;"><InfoFilled /></el-icon>
          <span style="font-weight: 600; color: #5a32a3;">版本信息</span>
          <el-tag size="small" type="info" effect="plain" style="background: rgba(147,112,219,0.1); color: #7b42f6; border-color: rgba(147,112,219,0.3);">必填</el-tag>
        </div>
        <el-form label-width="0">
          <el-form-item style="margin-bottom: 0;">
            <el-input 
              v-model="versionTag" 
              placeholder="请输入版本标签，如：v6.0.0-release" 
              style="width: 100%;" 
              clearable
              :prefix-icon="Grid"
            >
              <template #append>
                <el-tooltip content="用于标识本次分析的版本/迭代，便于后续检索和对比" placement="top">
                  <el-icon style="color: #94a3b8;"><InfoFilled /></el-icon>
                </el-tooltip>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
        <div style="margin-top: 12px; font-size: 12px; color: #7b42f6; display: flex; align-items: center; gap: 6px;">
          <el-icon style="font-size: 14px; color: #7b42f6;"><Clock /></el-icon>
          <span>分析记录将自动保存到历史记录，可通过版本标签快速检索</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="startAnalysis" :loading="analyzing" :disabled="!fileName">
          开始分析
        </el-button>
      </template>
    </el-dialog>
  </div><!-- end bug-analysis-container -->
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { DataAnalysis, UploadFilled, Loading, RefreshLeft, Document, Grid, TrendCharts, User,
  InfoFilled, Warning, List, Clock, Close, Download, MagicStick, Search, Check, View, Delete, ArrowLeft, Upload, CircleCheck } from '@element-plus/icons-vue'
import { analyzeBugExcel, enhanceWithAI, getBugAnalysisRecords, getBugAnalysisRecordDetail, getModuleDetail, deleteBugAnalysisRecord, analyzeModuleFocusIntelligent } from '@/api/data-factory'

const route = useRoute()
const router = useRouter()

// ==================== 视图控制 ====================
const viewMode = ref(route.query.view === 'detail' ? 'detail' : 'list') // 'list' | 'detail'
const showUploadDialog = ref(false)
const searchQuery = ref('')

// ==================== 状态 ====================
const analyzing = ref(false)
const analysisResult = ref(false)
const fileName = ref('')
const currentRecordId = ref(null)
const currentRecord = ref(null)

// AI 配置 (V2)
const aiProvider = ref('qwen')
const versionTag = ref('')
const saveRecord = ref(true)

// AI 加载状态 (渐进式加载)
const aiLoading = ref(false)
const aiLoadingText = ref('AI 分析中...')

// 历史记录 (V2)
const historyRecords = ref([])
const loadingHistory = ref(false)
const tableRef = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 模块详情 (V2)
const moduleDrawerVisible = ref(false)
const selectedModule = ref('')
const selectedModuleStats = ref({})
const moduleBugs = ref([])
const loadingModuleDetail = ref(false)
const bugFilter = ref({ keyword: '', severity: '', defectType: '' })
const bugPage = ref(1)

// 导出 (V2)
const showExportDialog = ref(false)
const exportFormat = ref('markdown')
const exportScope = ref('top5')
const exportCustomModules = ref([])
const exporting = ref(false)

// 图表引用
const moduleChartRef = ref(null), severityCrossChartRef = ref(null), severityPieChartRef = ref(null)
const statusChartRef = ref(null), priorityChartRef = ref(null), keywordChartRef = ref(null)
const creatorChartRef = ref(null), timelineChartRef = ref(null)

// 数据
const modulesData = ref({}), featureDetailData = ref([]), severityCrossData = ref({})
const sevInfData = ref({}), sevData = ref({}), statusData = ref({}), priorityData = ref({})
const kwData = ref([]), timelineCleanData = ref({}), timelineData = ref({})
const creatorModuleData = ref([]), riskData = ref({ P0:{total:0,detail:{}}, P1:{total:0,detail:{}}, P2:{total:0,detail:{}} })
const clusterData = ref([]), rootCauseData = ref([]), testFocusData = ref({}), metaData = ref({})
const aiSummary = ref(''), aiTestFocus = ref({}), aiRootCause = ref([]), aiRisks = ref({}), aiKeywords = ref([])
const summaryLines = ref([]), actionLines = ref([])
// 智能模块分析结果 (三层架构)
const aiModuleFocus = ref({})
const moduleFocusLoading = ref({})
const isAnalyzingAllModules = ref(false)
const isAllModulesAnalyzed = computed(() => {
  const modules = Object.keys(testFocusData.value)
  if (modules.length === 0) return false
  return modules.every(m => aiModuleFocus.value[m])
})

// 模块卡片联动相关
const highlightedModule = ref('')
const moduleCardRefs = ref({})

// 设置模块卡片ref
const setModuleCardRef = (el, moduleName) => {
  if (el) {
    moduleCardRefs.value[moduleName] = el
  }
}

let _rawAnalysisResult = null

// ==================== 计算属性 ====================
const workTypesText = computed(() => {
  const types = metaData.value?.work_types || {}
  return Object.entries(types).map(([k, v]) => `${k}${v}`).join('+') || '缺陷+线上故障'
})
const hasAiData = computed(() => !!aiSummary.value || Object.keys(aiTestFocus.value).length > 0)
const filteredModuleBugs = computed(() => {
  let list = moduleBugs.value
  if (bugFilter.value.keyword) {
    const kw = bugFilter.value.keyword.toLowerCase()
    list = list.filter(b => b.title.toLowerCase().includes(kw))
  }
  if (bugFilter.value.severity) list = list.filter(b => b.inferred_sev === bugFilter.value.severity)
  if (bugFilter.value.defectType) list = list.filter(b => b.defect_type === bugFilter.value.defectType)
  return list
})

const p0RiskData = computed(() => {
  // 只使用 AI 生成的风险类型，没有则返回空数组
  if (aiRisks.value?.P0?.length > 0) {
    const total = metaData.value?.total_bugs || 1
    return aiRisks.value.P0.map(item => ({
      ...item,
      percentage: item.percentage || `${((item.count || 0) / total * 100).toFixed(1)}%`
    }))
  }
  // AI分析完成前显示为空
  return []
})
const p1RiskData = computed(() => {
  // 只使用 AI 生成的风险类型，没有则返回空数组
  if (aiRisks.value?.P1?.length > 0) {
    const total = metaData.value?.total_bugs || 1
    return aiRisks.value.P1.map(item => ({
      ...item,
      percentage: item.percentage || `${((item.count || 0) / total * 100).toFixed(1)}%`
    }))
  }
  // AI分析完成前显示为空
  return []
})
const p2RiskData = computed(() => {
  // 只使用 AI 生成的风险类型，没有则返回空数组
  if (aiRisks.value?.P2?.length > 0) {
    const total = metaData.value?.total_bugs || 1
    return aiRisks.value.P2.map(item => ({
      ...item,
      percentage: item.percentage || `${((item.count || 0) / total * 100).toFixed(1)}%`
    }))
  }
  // AI分析完成前显示为空
  return []
})

// ==================== 工具方法 ====================
function getAiTestFocus(m) { return aiTestFocus.value[m] || '' }
function getAiRootCause(m) { return (aiRootCause.value.find(r=>r.module===m)||{}).cause||'' }
function sevTagType(sev){return{'P0':'danger','P1':'warning','P2':'info'}[sev]||''}
function dtypeTagType(dt){return{'UI显示':'','功能逻辑':'warning','数据内容':'danger','交互操作':'','性能稳定':'danger','跨端兼容':'warning'}[dt]||'info'}
function formatAiSummary(t){
  if(!t)return''
  
  // 保留空行用于判断列表边界
  const lines = t.split('\n')
  let html = ''
  let inRiskList = false
  let inActionList = false
  let riskCounter = 0
  let actionCounter = 0
  let lastNum = 0
  
  // SVG 图标 - 设置固定尺寸
  const warningIcon = `<svg class="ai-icon" width="16" height="16" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="#ef4444" d="M512 64a448 448 0 1 1 0 896 448 448 0 0 1 0-896zm0 192a58.432 58.432 0 0 0-58.24 63.744l23.36 256.384a35.072 35.072 0 0 0 69.76 0l23.36-256.384A58.432 58.432 0 0 0 512 256zm0 512a64 64 0 1 0 0-128 64 64 0 0 0 0 128z"/></svg>`
  const checkIcon = `<svg class="ai-icon" width="16" height="16" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="#10b981" d="M512 64a448 448 0 1 1 0 896 448 448 0 0 1 0-896zm-6.656 545.024l-131.2-131.2a32 32 0 0 0-45.248 45.248l153.6 153.6a32 32 0 0 0 45.248 0l307.2-307.2a32 32 0 0 0-45.248-45.248l-284.352 284.8z"/></svg>`
  
  // 先找到第一个非空行作为概述
  let firstNonEmptyIdx = -1
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() && !/^\d+[\.\、]/.test(lines[i].trim())) {
      firstNonEmptyIdx = i
      break
    }
  }
  
  if (firstNonEmptyIdx >= 0) {
    html += `<div class="ai-summary-overview">${lines[firstNonEmptyIdx].trim().replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>`
  }
  
  for (let i = firstNonEmptyIdx + 1; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()
    
    // 跳过空行，但用空行来判断列表边界
    if (!trimmed) {
      // 如果当前在风险列表中，且遇到了空行，后面又是1.开头，则关闭风险列表
      if (inRiskList && i + 1 < lines.length) {
        let nextNonEmptyIdx = i + 1
        while (nextNonEmptyIdx < lines.length && !lines[nextNonEmptyIdx].trim()) {
          nextNonEmptyIdx++
        }
        if (nextNonEmptyIdx < lines.length && /^1[\.\、]/.test(lines[nextNonEmptyIdx].trim())) {
          inRiskList = false
          html += '</div></div>'
        }
      }
      continue
    }
    
    // 检测列表项
    const listItemMatch = trimmed.match(/^(\d+)[\.\、]\s*(.+)$/)
    if (listItemMatch) {
      const num = parseInt(listItemMatch[1])
      const content = listItemMatch[2].replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // 检测是否是第一个列表的开始（以1开头，且之前没有在列表中）
      if (num === 1 && !inRiskList && !inActionList) {
        inRiskList = true
        lastNum = 1
        riskCounter = 0
        html += `<div class="ai-summary-section"><div class="ai-summary-section-title">${warningIcon}关键风险点</div><div class="ai-summary-list risk-list">`
      }
      // 检测是否是第二个列表的开始（以1开头，但已经在风险列表中，且数字变小）
      else if (num === 1 && inRiskList && num < lastNum) {
        inRiskList = false
        html += '</div></div>'
        inActionList = true
        lastNum = 1
        actionCounter = 0
        html += `<div class="ai-summary-section"><div class="ai-summary-section-title">${checkIcon}行动建议</div><div class="ai-summary-list action-list">`
      }
      
      // 添加列表项
      if (inRiskList) {
        riskCounter++
        html += `<div class="ai-summary-item risk-item"><span class="ai-summary-num risk-num">${riskCounter}</span><span class="ai-summary-text">${content}</span></div>`
      } else if (inActionList) {
        actionCounter++
        html += `<div class="ai-summary-item action-item"><span class="ai-summary-num action-num">${actionCounter}</span><span class="ai-summary-text">${content}</span></div>`
      }
      
      lastNum = num
    }
  }
  
  // 关闭未关闭的标签
  if (inRiskList || inActionList) {
    html += '</div></div>'
  }
  
  return html
}
function formatAiFocus(t){if(!t)return'';return t.split('\n').filter(l=>l.trim()).map(l=>`<div class="ai-focus-item">${l}</div>`).join('')}

// ==================== 核心方法 ====================
// ==================== 列表视图方法 ====================

// 处理文件选择（只保存文件，不上传）
let selectedFile = null
const handleFileChange = async(file)=>{
  if(!file||!file.raw){
    fileName.value = ''
    selectedFile = null
    return
  }
  const rawFile=file.raw
  if(!['.xlsx','.xls'].includes(rawFile.name.substring(rawFile.name.lastIndexOf('.')).toLowerCase())){
    ElMessage.error('请上传 .xlsx 或 .xls 格式的 Excel 文件')
    fileName.value = ''
    selectedFile = null
    return
  }
  fileName.value=rawFile.name
  selectedFile=rawFile
}

// 开始分析（从对话框触发）
const startAnalysis = async()=>{
  if(!selectedFile){
    ElMessage.warning('请先选择文件')
    return
  }
  
  // 校验版本标签（必填）
  if(!versionTag.value || versionTag.value.trim() === ''){
    ElMessage.warning('请输入版本标签')
    return
  }

  analyzing.value=true
  showUploadDialog.value=false

  try{
    // 第一步：上传并获取基础分析结果（快速返回）
    const res=await analyzeBugExcel(selectedFile,{
      save:true,  // 默认保存到历史记录
      aiProvider:aiProvider.value,
      versionTag:versionTag.value,
      skip_ai: false
    })
    console.log('基础分析API响应:', res)
    const result=res.data||res

    if(result?.success){
      _rawAnalysisResult=result
      try{
        applyAnalysisResult(result)
        console.log('applyAnalysisResult完成')
      }catch(e){console.error('applyAnalysisResult错误:', e)}
      try{
        generateSummary()
        console.log('generateSummary完成')
      }catch(e){console.error('generateSummary错误:', e)}

      // 立即显示基础分析结果
      analysisResult.value=true
      viewMode.value='detail'
      currentRecordId.value=result.record_id
      // 更新URL，添加view和record_id参数
      router.replace({ query: { ...route.query, view: 'detail', record_id: result.record_id } })
      console.log('基础分析结果已显示')
      ElMessage.success(result.message||'基础分析完成')

      // 渲染图表
      nextTick(()=>{
        try{
          renderCharts()
          console.log('renderCharts完成')
        }catch(e){console.error('renderCharts错误:', e)}
      })

      // 加载历史记录（始终保存，自动刷新列表）
      if(result.record_id){
        try{await loadHistoryRecords()}catch(e){console.error('loadHistoryRecords错误:', e)}
      }

      // 第二步：如果后端标记需要AI增强，处理AI分析
      console.log('检查AI条件:', { ai_pending: result.ai_pending, record_id: result.record_id, aiProvider: aiProvider.value })
      aiLoading.value = true
      aiLoadingText.value = 'AI 正在分析中，请稍候...'
      
      if(result.ai_pending && aiProvider.value !== 'none'){
        if(result.record_id){
          console.log('开始AI增强分析(渐进式)...')
          setTimeout(() => {
            fetchAIEnhancement(result.record_id)
          }, 100)
        }else{
          console.log('无法启用AI分析: 无record_id')
          aiLoading.value = false
          if(result.ai_error){
            ElMessage.warning(result.ai_error)
          }else{
            ElMessage.warning('数据库模型不可用，请执行: python manage.py migrate')
          }
        }
      }else{
        console.log('AI未启用:', { ai_pending: result.ai_pending, aiProvider: aiProvider.value })
        aiLoading.value = false
      }
    }else{
      console.error('分析失败:', result)
      ElMessage.error(result?.error||'分析失败')
    }
  }catch(e){
    console.error('上传分析错误:', e)
    ElMessage.error(e.response?.data?.error||e.message||'分析失败，请检查文件格式')
  }
  finally{
    analyzing.value=false
    selectedFile=null
  }
}

// 查看分析详情
const viewAnalysisDetail = async(record)=>{
  if(!record)return
  
  // 设置当前记录
  currentRecord.value = record
  currentRecordId.value = record.id
  fileName.value = record.file_name || '未命名'
  versionTag.value = record.version_tag || ''
  
  // 加载详情数据
  try{
    analyzing.value = true
    const res = await getBugAnalysisRecordDetail(record.id)
    const result = res.data||res
    
    if(result?.analysis_result){
      _rawAnalysisResult = result.analysis_result
      try{
        applyAnalysisResult(result.analysis_result)
        console.log('applyAnalysisResult完成')
      }catch(e){console.error('applyAnalysisResult错误:', e)}
      try{
        generateSummary()
        console.log('generateSummary完成')
      }catch(e){console.error('generateSummary错误:', e)}
      
      // 恢复已缓存的AI模块分析结果 (从analysis_result中读取)
      const cachedAiModuleFocus = result.analysis_result?.aiModuleFocus
      console.log('[viewAnalysisDetail] 检查aiModuleFocus缓存:', {
        hasCached: !!cachedAiModuleFocus,
        keys: cachedAiModuleFocus ? Object.keys(cachedAiModuleFocus) : []
      })
      if(cachedAiModuleFocus && Object.keys(cachedAiModuleFocus).length > 0){
        aiModuleFocus.value = cachedAiModuleFocus
        console.log('[viewAnalysisDetail] ✅ 已恢复AI模块分析缓存:', Object.keys(cachedAiModuleFocus))
      } else {
        console.log('[viewAnalysisDetail] ⚠️ 没有可用的AI模块分析缓存')
      }
      
      // 切换到详情视图
      analysisResult.value = true
      viewMode.value = 'detail'
      currentRecordId.value = record.id
      
      // 更新URL，添加view和record_id参数
      router.replace({ query: { ...route.query, view: 'detail', record_id: record.id } })
      
      // 渲染图表
      nextTick(()=>{
        try{
          renderCharts()
          console.log('renderCharts完成')
        }catch(e){console.error('renderCharts错误:', e)}
      })
    }
    
    // 如果AI还在加载中，启动轮询
    if(result?.ai_pending && result.record_id){
      aiLoading.value = true
      aiLoadingText.value = 'AI 正在分析中，请稍候...'
      setTimeout(() => {
        fetchAIEnhancement(result.record_id)
      }, 100)
    }
  }catch(e){
    console.error('加载详情失败:', e)
    ElMessage.error('加载分析详情失败')
  }finally{
    analyzing.value = false
  }
}

// 删除记录
const handleDeleteRecord = async(record)=>{
  if(!record?.id)return
  
  try{
    await ElMessageBox.confirm(
      `确定要删除分析记录 "${record.file_name || '未命名'}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteBugAnalysisRecord(record.id)
    ElMessage.success('删除成功')
    
    // 刷新列表
    await loadHistoryRecords()
  }catch(error){
    if(error !== 'cancel'){
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

// 返回列表
const backToList = ()=>{
  viewMode.value = 'list'
  // 重置当前记录
  currentRecord.value = null
  currentRecordId.value = null
  analysisResult.value = false
  resetAnalysisData()
  // 清除URL中的view参数
  const { view, ...otherQuery } = route.query
  router.replace({ query: otherQuery })
}

// 搜索
const handleSearch = ()=>{
  loadHistoryRecords()
}

// 格式化日期时间
const formatDateTime = (datetime)=>{
  if(!datetime)return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// AI 增强分析（异步）- 注意：aiLoading已在调用前设置
const fetchAIEnhancement = async(recordId)=>{
  try{
    const res=await enhanceWithAI(recordId,{
      aiProvider:aiProvider.value,
      aiConfigId:null
    })
    console.log('AI增强API响应:', res)
    const result=res.data||res

    if(result?.success){
      // 应用AI增强结果
      if(result.aiSummary) aiSummary.value=result.aiSummary
      if(result.aiTestFocus) aiTestFocus.value=result.aiTestFocus
      if(result.aiRootCause) aiRootCause.value=result.aiRootCause
      if(result.aiRisks) aiRisks.value=result.aiRisks
      if(result.aiKeywords) aiKeywords.value=result.aiKeywords

      // 更新原始结果
      if(_rawAnalysisResult){
        _rawAnalysisResult.aiSummary=result.aiSummary
        _rawAnalysisResult.aiTestFocus=result.aiTestFocus
        _rawAnalysisResult.aiRootCause=result.aiRootCause
      }

      // AI关键词更新后，重新渲染关键词图表
      renderKeywordChart()

      // 自动为所有模块生成智能分析 (新功能)
      await fetchAllModulesIntelligentFocus(recordId)

      ElMessage.success(`AI 分析完成 (耗时${result.elapsed_ms||0}ms)`)
      console.log('AI增强结果已应用')
    }else{
      console.error('AI增强失败:', result)
      ElMessage.warning(result?.error||'AI 分析失败')
    }
  }catch(e){
    console.error('AI增强错误:', e)
    ElMessage.error(e.response?.data?.error||e.message||'AI 分析请求失败')
  }finally{
    aiLoading.value=false
  }
}

function applyAnalysisResult(result){
  modulesData.value=result.modulesData||{}; featureDetailData.value=result.featureDetailData||[]; severityCrossData.value=result.severityCrossData||{}
  sevInfData.value=result.sevInfData||{}; sevData.value=result.sevData||{}; statusData.value=result.statusData||{}; priorityData.value=result.priorityData||{}
  kwData.value=result.kwData||[]; timelineCleanData.value=result.timelineCleanData||{}; timelineData.value=result.timelineData||{}
  creatorModuleData.value=result.creatorModuleData||[]; riskData.value=result.riskData||{P0:{total:0,detail:{}},P1:{total:0,detail:{}},P2:{total:0,detail:{}}}
  clusterData.value=result.clusterData||[]; rootCauseData.value=result.rootCauseData||[]; testFocusData.value=result.testFocusData||{}; metaData.value=result.metaData||{}
  aiSummary.value=result.aiSummary||''; aiTestFocus.value=result.aiTestFocus||{}; aiRootCause.value=result.aiRootCause||[]; aiRisks.value=result.aiRisks||{}; aiKeywords.value=result.aiKeywords||[]
  // 恢复AI模块分析缓存
  if(result.aiModuleFocus && Object.keys(result.aiModuleFocus).length > 0){
    aiModuleFocus.value = result.aiModuleFocus
    console.log('[applyAnalysisResult] 已恢复aiModuleFocus:', Object.keys(result.aiModuleFocus))
  }
  // 只在 record_id 存在时才更新，避免覆盖已设置的值
  if(result.record_id){
    currentRecordId.value=result.record_id
  }
}

async function loadHistoryRecords(){
  loadingHistory.value=true
  try{
    const params = { 
      page: currentPage.value,
      page_size: pageSize.value 
    }
    if(searchQuery.value){
      params.search = searchQuery.value
    }
    const r=await getBugAnalysisRecords(params)
    historyRecords.value=(r.data?.data?.items||r.data?.results||[])
    total.value = r.data?.data?.total || r.data?.total || 0
  }
  catch(e){console.warn('加载历史记录失败:',e)}
  finally{loadingHistory.value=false}
}

// 分页事件处理
const handleSizeChange = (val) => {
  pageSize.value = val
  loadHistoryRecords()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadHistoryRecords()
}

async function loadHistoryRecord(rec){
  loadingModuleDetail.value=true
  try{
    const r=await getBugAnalysisRecordDetail(rec.id); const result=r.data||r
    console.log('[加载历史记录] API原始响应:', r)
    console.log('[加载历史记录] result对象:', result)
    console.log('[加载历史记录] result.analysis_result:', result?.analysis_result)
    if(result.analysis_result){
      _rawAnalysisResult=result.analysis_result
      console.log('[加载历史记录] analysis_result:', result.analysis_result)
      console.log('[加载历史记录] aiKeywords:', result.analysis_result?.aiKeywords)
      // 先设置 currentRecordId，再 applyAnalysisResult
      currentRecordId.value=rec.id
      applyAnalysisResult(result.analysis_result)
      generateSummary()
      analysisResult.value=true
      
      // 恢复已缓存的AI模块分析结果 (从analysis_result中读取)
      const cachedAiModuleFocus = result.analysis_result?.aiModuleFocus
      console.log('[加载历史记录] 检查aiModuleFocus缓存:', {
        hasCached: !!cachedAiModuleFocus,
        keys: cachedAiModuleFocus ? Object.keys(cachedAiModuleFocus) : [],
        fullData: cachedAiModuleFocus
      })
      if(cachedAiModuleFocus && Object.keys(cachedAiModuleFocus).length > 0){
        aiModuleFocus.value = cachedAiModuleFocus
        console.log('[加载历史记录] ✅ 已恢复AI模块分析缓存:', Object.keys(cachedAiModuleFocus))
      } else {
        console.log('[加载历史记录] ⚠️ 没有可用的AI模块分析缓存')
      }
      
      nextTick(()=>{
        renderCharts()
        console.log('[加载历史记录] 图表渲染完成，当前 aiKeywords:', aiKeywords.value)
      })
      ElMessage.success(`已加载: ${rec.file_name||rec.version_tag}`)
    }
  }catch(e){ElMessage.error('加载历史记录失败')} finally{loadingModuleDetail.value=false}
}

async function openModuleDetail(modName){
  if(!currentRecordId.value){ElMessage.info('仅支持查看已保存记录的模块详情');return}
  selectedModule.value=modName; moduleDrawerVisible.value=true; loadingModuleDetail.value=true
  bugFilter.value={keyword:'',severity:'',defectType:''}; bugPage.value=1
  const localInfo=testFocusData.value[modName]; selectedModuleStats.value=localInfo||{}
  try{
    const r=await getModuleDetail(currentRecordId.value,modName,{page_size:100}); const data=r.data||r
    selectedModuleStats.value=data.stats||localInfo||{}; moduleBugs.value=data.bugs||[]
    if(data.ai_test_focus&&!aiTestFocus.value[modName])aiTestFocus.value[modName]=data.ai_test_focus
    if(data.ai_root_cause&&!aiRootCause.value.find(r=>r.module===modName))aiRootCause.value.push({module:modName,cause:data.ai_root_cause})
    // 异步获取智能模块分析 (不阻塞主流程)
    loadIntelligentModuleFocus(modName)
  }catch(e){console.warn('获取模块详情API失败:',e); moduleBugs.value=[]}finally{loadingModuleDetail.value=false}
}

// 加载智能模块分析 (三层架构)
async function loadIntelligentModuleFocus(modName){
  if(!currentRecordId.value||!modName)return
  // 检查缓存
  if(aiModuleFocus.value[modName])return
  
  moduleFocusLoading.value[modName]=true
  try{
    const res=await analyzeModuleFocusIntelligent(currentRecordId.value,modName)
    const data=res.data||res
    if(data&&data.focus_points){
      aiModuleFocus.value[modName]=data
      console.log(`[AI] 模块 ${modName} 智能分析完成:`, data.risk_level)
    }
  }catch(e){
    console.warn(`[AI] 模块 ${modName} 智能分析失败:`,e)
  }finally{
    moduleFocusLoading.value[modName]=false
  }
}

// 为所有模块批量生成智能分析
async function fetchAllModulesIntelligentFocus(recordId){
  const modules = Object.keys(testFocusData.value)
  if(!modules.length || !recordId){
    console.log('[AI] 没有需要分析的模块')
    return
  }
  
  console.log(`[AI] 开始批量分析 ${modules.length} 个模块...`)
  
  // 过滤掉已有缓存的模块
  const modulesToAnalyze = modules.filter(m => !aiModuleFocus.value[m])
  
  if(!modulesToAnalyze.length){
    console.log('[AI] 所有模块已有缓存')
    return
  }
  
  // 限制并发数量，避免同时请求过多
  const batchSize = 3
  const batches = []
  
  for(let i = 0; i < modulesToAnalyze.length; i += batchSize){
    batches.push(modulesToAnalyze.slice(i, i + batchSize))
  }
  
  // 串行处理 - 避免并发导致数据覆盖
  for(const batch of batches){
    for(const modName of batch){
      moduleFocusLoading.value[modName] = true
      try{
        const res = await analyzeModuleFocusIntelligent(recordId, modName)
        const data = res.data || res
        if(data && data.focus_points){
          aiModuleFocus.value[modName] = data
          console.log(`[AI] 模块 ${modName} 智能分析完成`)
        }
      }catch(e){
        console.warn(`[AI] 模块 ${modName} 智能分析失败:`, e)
      }finally{
        moduleFocusLoading.value[modName] = false
      }
    }
  }
  
  console.log(`[AI] 批量分析完成`)
}

// 用户手动触发AI分析所有模块
async function analyzeAllModules(){
  if(!currentRecordId.value){
    ElMessage.warning('请先选择一个分析记录')
    return
  }
  
  const modules = Object.keys(testFocusData.value)
  if(!modules.length){
    ElMessage.info('暂无可分析的模块')
    return
  }
  
  // 检查是否已全部分析完成
  const pendingModules = modules.filter(m => !aiModuleFocus.value[m])
  if(!pendingModules.length){
    ElMessage.success('所有模块已完成AI分析')
    return
  }
  
  isAnalyzingAllModules.value = true
  ElMessage.info(`开始AI分析 ${pendingModules.length} 个模块，请稍候...`)
  
  try{
    await fetchAllModulesIntelligentFocus(currentRecordId.value)
    ElMessage.success('AI分析完成')
  }catch(e){
    console.error('[AI] 批量分析失败:', e)
    ElMessage.error('AI分析过程中出现错误')
  }finally{
    isAnalyzingAllModules.value = false
  }
}

function onModuleChartClick(event){
  const names=Object.keys(modulesData.value)
  if(event.event&&event.target&&event.data!==undefined){
    const idx=event.dataIndex!==undefined?event.dataIndex:event.data
    if(idx>=0&&idx<names.length){
      const moduleName = names[idx]
      // 滚动到对应的模块卡片
      scrollToModuleCard(moduleName)
    }
  }
}

// 滚动到指定模块卡片
function scrollToModuleCard(moduleName){
  const cardEl = moduleCardRefs.value[moduleName]
  if(!cardEl){
    console.warn('[联动] 未找到模块卡片:', moduleName)
    return
  }
  
  // 设置高亮
  highlightedModule.value = moduleName
  
  // 滚动到卡片位置
  cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
  
  // 3秒后移除高亮
  setTimeout(() => {
    if(highlightedModule.value === moduleName){
      highlightedModule.value = ''
    }
  }, 3000)
  
  console.log('[联动] 已定位到模块:', moduleName)
}

async function doExport(){
  exporting.value=true
  try{
    let c='# Bug 回归测试清单\n\n> 生成时间:'+new Date().toLocaleString()+' | 来源:'+(metaData.value.input_file||'-')+'\n\n## 总览\n- 总Bug数:'+metaData.value.total_bugs+'- P0/P1/P2:'+(sevInfData.value['推断P0']||0)+'/'+(sevInfData.value['推断P1']||0)+'/'+(sevInfData.value['推断P2']||0)+'\n\n'
    let targetMods=[]
    if(exportScope.value==='all')targetMods=Object.keys(modulesData.value)
    else if(exportScope.value==='top5')targetMods=Object.entries(modulesData.value).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([m])=>m)
    else targetMods=exportCustomMods.value
    for(const mod of targetMods){
      const info=testFocusData.value[mod]; if(!info)continue
      c+=`### ${mod} (${info.total}条)\n\n`
      c+=`- **总数**: ${info.total} | **线上**: ${info.online} | **二次打开**: ${info.reopened}\n`
      if(info.focus_points){for(const fp of info.focus_points)c+=`- ${fp}\n`}
      const af=getAiTestFocus(mod); if(af)c+=`\n**AI 建议:**\n${af}\n`
      c+='\n---\n\n'
    }
    const blob=new Blob([c],{type:'text/markdown;charset=utf-8'}); const url=URL.createObjectURL(blob); const a=document.createElement('a')
    a.href=url; a.download=`回归清单_${metaData.value.input_file?.replace('.xlsx','')||'bug'}_${Date.now()}.md`; a.click(); URL.revokeObjectURL(url)
    showExportDialog.value=false; ElMessage.success('导出成功!')
  }catch(e){ElMessage.error('导出失败: '+e.message)} finally{exporting.value=false}
}

// ==================== 摘要生成 ====================
const generateSummary=()=>{
  const lines=[],actions=[]
  const total=metaData.value?.total_bugs||0
  const sevGen=severityCrossData.value['3-一般']||{}, sP0=sevGen['P0']||0, sP1=sevGen['P1']||0
  if(sP0>0||sP1>0)lines.push(`<b>1) 严重度标注偏低：</b>"3-一般"中${sP0}条应为P0(白屏/504)、${sP1}条应为P1(无法/报错)，实际风险远高于标注。建议重新评审P0/P1候选Bug。`)
  const top3=Object.entries(modulesData.value).sort((a,b)=>b[1]-a[1]).slice(0,4).filter(([_,c])=>c>0)
  if(top3.length>0)lines.push(`<b>2) Bug聚集集中在${top3.map(([m,c])=>`${m}(${c})`).join('、')}：</b>这些模块是质量攻坚的重点方向。`)
  if((metaData.value?.uncategorized_pct||0)>20)lines.push(`<b>3) 标签规范待改善：</b>${metaData.value.uncategorized}条Bug归"其他"(${metaData.value.uncategorized_pct}%)，建议强制要求提Bug必须带【功能标签】+【端标签】。`)
  if(metaData.value?.import_count>0)lines.push(`<b style="color:#999;font-size:13px">数据说明：</b>本看板分析${total}条全量Bug。时间趋势图额外排除了${metaData.value.import_count}条平台迁移导入Bug。`)
  const p0T=riskData.value.P0?.total||0, p0D=riskData.value.P0?.detail||{}, p1O=riskData.value.P1?.detail?.['线上故障P1']||0, p1R=riskData.value.P1?.detail?.['二次回归']||0, p2O=riskData.value.P2?.detail?.['线上故障P2']||0
  if(p0T>0)actions.push(`<b>立即：</b>复核${p0T}条P0候选Bug(含白屏${p0D['白屏']||0}+504超时${p0D['504超时']||0}+闪退${p0D['闪退/崩溃']||0})，确认是否升级严重度。`)
  if((metaData.value?.uncategorized_pct||0)>20)actions.push('<b>本周：</b>强制推行Bug标签规范——提Bug必须带【功能标签】+【端标签】，消灭"其他"垃圾桶。')
  if(p1O>0||p2O>0)actions.push(`<b>持续：</b>重点模块安排专项回归测试——优先覆盖P1级线上故障${p1O}条+二次回归${p1R}条，P2级线上故障${p2O}条按需覆盖。`)
  summaryLines.value=lines; actionLines.value=actions
}

// ==================== 图表渲染 ====================
const renderCharts=()=>{renderModuleChart();renderSeverityCrossChart();renderSeverityPieChart();renderStatusChart();renderPriorityChart();renderKeywordChart();renderCreatorChart();renderTimelineChart()}

const renderModuleChart=()=>{
  if(!moduleChartRef.value)return; const chart=echarts.init(moduleChartRef.value)
  const d=modulesData.value
  // 按Bug数量从高到低排序
  const sortedEntries=Object.entries(d).sort((a,b)=>b[1]-a[1])
  const names=sortedEntries.map(([k])=>k), values=sortedEntries.map(([,v])=>v)
  chart.setOption({
    backgroundColor:'#fff',title:{text:'Bug模块分布(核心模块)',textStyle:{color:'#e94560',fontSize:14}},tooltip:{trigger:'axis'},
    xAxis:{type:'category',data:names,axisLabel:{color:'#333',rotate:35,fontSize:11},axisLine:{lineStyle:{color:'#ccc'}}},
    yAxis:{type:'value',axisLabel:{color:'#333'},axisLine:{lineStyle:{color:'#ccc'}},splitLine:{lineStyle:{color:'#e0e0e0'}}},
    series:[{type:'bar',data:values,itemStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#e94560'},{offset:1,color:'#e0e0e0'}])},label:{show:true,position:'top',color:'#333',fontSize:11}}],
    grid:{left:'10%',bottom:'22%',top:'15%'}
  })
  // 绑定点击事件 - 联动到测试重点卡片
  chart.off('click')
  chart.on('click', (params) => {
    if(params && params.name){
      scrollToModuleCard(params.name)
    }
  })
}
const renderSeverityCrossChart=()=>{
  if(!severityCrossChartRef.value)return; const chart=echarts.init(severityCrossChartRef.value)
  const d=severityCrossData.value, labels=Object.keys(d).sort()
  // P0/P1/P2 对应中文严重度
  const typeMap={'P0':'致命','P1':'严重','P2':'一般'}
  const types=['P0','P1','P2'], typeLabels=['致命','严重','一般'], colors=['#e74c3c','#e94560','#3498db']
  const series=types.map((t,i)=>({name:typeLabels[i],type:'bar',stack:'total',data:labels.map(s=>d[s][t]||0),itemStyle:{color:colors[i]},label:{show:false}}))
  chart.setOption({backgroundColor:'#fff',tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},legend:{data:typeLabels,textStyle:{color:'#333'},top:10},xAxis:{type:'category',data:labels,axisLabel:{color:'#333',fontSize:12},axisLine:{lineStyle:{color:'#ccc'}}},yAxis:{type:'value',axisLabel:{color:'#333'},axisLine:{lineStyle:{color:'#ccc'}},splitLine:{lineStyle:{color:'#e0e0e0'}}},series,grid:{left:'15%',right:'5%',top:'20%',bottom:'10%'}})
}
const renderSeverityPieChart=()=>{
  if(!severityPieChartRef.value)return; const chart=echarts.init(severityPieChartRef.value)
  const data=Object.entries(sevInfData.value).map(([k,v])=>({name:k,value:v}))
  chart.setOption({backgroundColor:'#fff',tooltip:{trigger:'item',formatter:'{b}: {c}条 ({d}%)'},series:[{type:'pie',radius:['40%','60%'],center:['50%','50%'],avoidLabelOverlap:true,data,label:{show:true,position:'outside',color:'#333',fontSize:11,formatter:'{b}: {c}条 ({d}%)',minMargin:5,edgeDistance:10},labelLine:{show:true,length:15,length2:20,smooth:true},itemStyle:{borderColor:'#fff',borderWidth:2},color:['#e74c3c','#e94560','#f39c12','#3498db']}]})}
const renderStatusChart=()=>{
  if(!statusChartRef.value)return; const chart=echarts.init(statusChartRef.value)
  const data=Object.entries(statusData.value).sort((a,b)=>b[1]-a[1]).map(([k,v])=>({name:k,value:v}))
  chart.setOption({backgroundColor:'#fff',tooltip:{trigger:'item',formatter:'{b}: {c}条 ({d}%)'},series:[{type:'pie',radius:['40%','60%'],center:['50%','50%'],avoidLabelOverlap:true,data,label:{show:true,position:'outside',color:'#333',fontSize:11,formatter:'{b}: {c}条 ({d}%)',minMargin:5,edgeDistance:10},labelLine:{show:true,length:15,length2:20,smooth:true},itemStyle:{borderColor:'#fff',borderWidth:2},color:['#27ae60','#95a5a6','#f39c12','#3498db','#e94560','#9b59b6','#e74c3c','#1abc9c','#34495e']}]})}
const renderPriorityChart=()=>{
  if(!priorityChartRef.value)return; const chart=echarts.init(priorityChartRef.value)
  const colors=['#e74c3c','#e94560','#f39c12','#3498db','#9b59b6','#95a5a6']
  const data=Object.entries(priorityData.value).sort((a,b)=>b[1]-a[1]).filter(([_,v])=>v>0).map(([k,v],i)=>({name:k,value:v,itemStyle:{color:colors[i%6]}}))
  chart.setOption({backgroundColor:'#fff',tooltip:{trigger:'item',formatter:'{b}: {c}条 ({d}%)'},series:[{type:'pie',radius:['40%','60%'],center:['50%','50%'],avoidLabelOverlap:true,data,label:{show:true,position:'outside',color:'#333',fontSize:11,formatter:'{b}: {c}条 ({d}%)',minMargin:5,edgeDistance:10},labelLine:{show:true,length:15,length2:20,smooth:true},itemStyle:{borderColor:'#fff',borderWidth:2}}]})}
const renderKeywordChart=()=>{
  if(!keywordChartRef.value)return
  // 获取或创建图表实例
  let chart = echarts.getInstanceByDom(keywordChartRef.value)
  if(!chart){
    chart = echarts.init(keywordChartRef.value)
  }
  // 优先使用 AI 生成的关键词，没有则显示空
  const data = aiKeywords.value && aiKeywords.value.length > 0 ? aiKeywords.value : []
  console.log('[关键词图表] 数据:', data, 'aiKeywords:', aiKeywords.value)
  const names=data.map(e=>e[0]), values=data.map(e=>e[1])
  const titleText = data.length > 0 ? '关键词词频 Top 20(AI 语义提取)' : '关键词词频 (等待 AI 分析...)'
  chart.setOption({backgroundColor:'#fff',title:{text:titleText,textStyle:{color:'#e94560',fontSize:14}},tooltip:{formatter:p=>`${p.name}: ${p.value}条相关Bug`},xAxis:{type:'value',axisLabel:{color:'#333'},axisLine:{lineStyle:{color:'#ccc'}},splitLine:{lineStyle:{color:'#e0e0e0'}}},yAxis:{type:'category',data:names,inverse:true,axisLabel:{color:'#333',fontSize:12},axisLine:{lineStyle:{color:'#ccc'}}},series:[{type:'bar',data:values,itemStyle:{color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#e0e0e0'},{offset:1,color:'#e94560'}])},label:{show:true,position:'right',color:'#333'}}],grid:{left:'15%',right:'10%'}})
}
const renderCreatorChart=()=>{
  if(!creatorChartRef.value)return; const chart=echarts.init(creatorChartRef.value)
  const data=creatorModuleData.value, modules=Object.keys(modulesData.value)
  const colors=['#e94560','#3498db','#f39c12','#9b59b6','#27ae60','#FF69B4','#1abc9c','#e74c3c','#34495e','#2ecc71','#e67e22','#8e44ad']
  const series=modules.map((mod,i)=>({name:mod,type:'bar',stack:'module',data:data.map(d=>(d.modules&&d.modules[mod])||0),itemStyle:{color:colors[i%colors.length],borderColor:'#fff',borderWidth:1}}))
  series.push({name:'其他(低频/无标签)',type:'bar',stack:'module',data:data.map(d=>(d.modules&&d.modules['其他'])||0),itemStyle:{color:'#d5d8dc',borderColor:'#fff',borderWidth:1}})
  chart.setOption({backgroundColor:'#fff',title:{text:'创建者×模块分布(堆叠)',textStyle:{color:'#e94560',fontSize:14},left:'center'},tooltip:{trigger:'axis',axisPointer:{type:'shadow'},formatter:params=>{const d=data[params[0].dataIndex];let l=`${d.creator}(总${d.total}条,线上${d.online}条/${d.online_pct}%)<br/>`;params.forEach(p=>{if(p.value>0)l+=`${p.seriesName}:${p.value}条<br/>`});return l}},legend:{data:[...modules,'其他(低频/无标签)'],textStyle:{color:'#333'},top:30,type:'scroll'},xAxis:{type:'value',axisLabel:{color:'#333'},axisLine:{lineStyle:{color:'#ccc'}},splitLine:{lineStyle:{color:'#e0e0e0'}}},yAxis:{type:'category',data:data.map(d=>`${d.creator}(${d.total}条,线上${d.online_pct}%)`),inverse:true,axisLabel:{color:'#333',fontSize:11},axisLine:{lineStyle:{color:'#ccc'}}},series,grid:{left:'25%',right:'5%',top:80}})
}
const renderTimelineChart=()=>{
  if(!timelineChartRef.value)return; const chart=echarts.init(timelineChartRef.value)
  const d=timelineCleanData.value, hasImport=metaData.value?.import_count>0
  chart.setOption({backgroundColor:'#fff',title:{text:`Bug创建时间趋势${hasImport?'(已排除平台迁移导入)':''}`,textStyle:{color:'#e94560',fontSize:14},left:'center'},tooltip:{trigger:'axis',formatter:p=>`${p[0].name}<br/>新增Bug:${p[0].value}条`},xAxis:{type:'category',data:Object.keys(d),axisLabel:{color:'#333',rotate:30},axisLine:{lineStyle:{color:'#ccc'}}},yAxis:{type:'value',axisLabel:{color:'#333'},axisLine:{lineStyle:{color:'#ccc'}},splitLine:{lineStyle:{color:'#e0e0e0'}}},series:[{type:'line',data:Object.values(d),smooth:true,itemStyle:{color:'#e94560'},lineStyle:{color:'#e94560',width:3},areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(233,69,96,0.15)'},{offset:1,color:'rgba(233,69,96,0.02)'}])},markPoint:{data:[{type:'max',name:'峰值',label:{color:'#333'}}],itemStyle:{color:'#e94560'}}}],grid:{left:'10%',bottom:'18%',top:50}})
}

// 重置分析数据（保留在详情视图）
const resetAnalysisData = () => {
  fileName.value = ''
  currentRecordId.value = null
  aiSummary.value = ''
  aiTestFocus.value = {}
  aiRootCause.value = []
  aiRisks.value = {}
  aiKeywords.value = []
  aiModuleFocus.value = {}  // 重置AI模块分析缓存
  moduleCardRefs.value = {}  // 重置模块卡片引用
  _rawAnalysisResult = null
  ;[moduleChartRef.value, severityCrossChartRef.value, severityPieChartRef.value, statusChartRef.value, priorityChartRef.value, keywordChartRef.value, creatorChartRef.value, timelineChartRef.value].forEach(ref => { if (ref) { const c = echarts.getInstanceByDom(ref); if (c) c.dispose() } })
}

// 重置分析（返回列表并清空所有数据）
const resetAnalysis = () => {
  viewMode.value = 'list'
  analysisResult.value = false
  currentRecord.value = null
  currentRecordId.value = null
  resetAnalysisData()
  // 重置版本标签
  versionTag.value = ''
  showUploadDialog.value = true
}

// 监听 URL 参数变化，自动切换视图
watch(() => route.query.view, (newView) => {
  if (newView === 'detail') {
    viewMode.value = 'detail'
  } else {
    viewMode.value = 'list'
    // 如果是从详情页返回列表页，清理详情页数据
    if (!newView && currentRecordId.value) {
      currentRecord.value = null
      currentRecordId.value = null
      analysisResult.value = false
      resetAnalysisData()
    }
  }
}, { immediate: true })

// 详情页刷新时恢复数据
const restoreDetailView = async () => {
  console.log('[restoreDetailView] 开始恢复, 状态:', {
    viewMode: viewMode.value,
    analysisResult: analysisResult.value,
    historyRecordsLength: historyRecords.value.length,
    recordIdFromUrl: route.query.record_id,
    query: route.query
  })
  // 如果当前是详情视图但没有数据，尝试从历史记录中恢复
  if (viewMode.value === 'detail' && !analysisResult.value && historyRecords.value.length > 0) {
    // 尝试从URL获取记录ID
    const recordIdFromUrl = route.query.record_id
    if (recordIdFromUrl) {
      const record = historyRecords.value.find(r => r.id === parseInt(recordIdFromUrl))
      if (record) {
        console.log('[恢复详情页] 从URL加载记录:', recordIdFromUrl)
        await loadHistoryRecord(record)
        return
      } else {
        console.warn('[恢复详情页] 找不到记录:', recordIdFromUrl, '可用记录:', historyRecords.value.map(r => r.id))
      }
    }
    // 如果没有URL参数或找不到记录，加载第一条历史记录
    console.log('[恢复详情页] 加载第一条历史记录')
    await loadHistoryRecord(historyRecords.value[0])
  } else {
    console.log('[restoreDetailView] 条件不满足, 跳过恢复:', {
      isDetail: viewMode.value === 'detail',
      noAnalysis: !analysisResult.value,
      hasHistory: historyRecords.value.length > 0
    })
  }
}

onMounted(() => {
  loadHistoryRecords().then(() => {
    // 历史记录加载完成后，如果是详情视图则恢复数据
    restoreDetailView()
  })
})
</script>

<style scoped>
/* ==================== 设计系统变量 - 紫色主题 ==================== */
.bug-analysis-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ==================== 筛选栏 - 参考XMindConverter风格 ==================== */
.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-bar :deep(.el-input__wrapper) {
  box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
  border-radius: 8px;
  border: 1px solid rgba(147, 112, 219, 0.2);
  background: #ffffff;
}

.filter-bar :deep(.el-input__wrapper:hover),
.filter-bar :deep(.el-input__wrapper:focus) {
  box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
  border-color: #7b42f6;
}

.filter-bar-spacer {
  flex: 1;
}

/* ==================== 卡片容器 - 统一风格 ==================== */
.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
}

/* ==================== 页面标题 ==================== */
.page-header{text-align:center;margin-bottom:28px;padding:12px 0}
.page-title{font-size:26px;font-weight:600;color:#5a32a3;display:flex;align-items:center;justify-content:center;gap:10px;margin:0;letter-spacing:-0.02em}
.page-title .el-icon{color:#7b42f6;font-size:28px}
.page-subtitle{color:#7b6db3;font-size:14px;margin-top:10px;font-weight:400}

/* ==================== 上传区域 - 紫色主题 ==================== */
.upload-card{max-width:720px;margin:48px auto;border-radius:12px;background:#fff;border:1px solid rgba(147,112,219,0.12);box-shadow:0 4px 16px rgba(147,112,219,0.08);transition:all 0.3s ease}
.upload-card:hover{box-shadow:0 8px 24px rgba(147,112,219,0.12);border-color:rgba(147,112,219,0.2)}
.upload-area{width:100%;padding:48px 0;background:linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%);border:2px dashed rgba(147,112,219,0.3);border-radius:8px;transition:all 0.3s ease}
.upload-area:hover{border-color:#7b42f6;background:linear-gradient(135deg, #f0edff 0%, #e8e4ff 100%)}
.upload-icon{font-size:52px;color:#a888e0;margin-bottom:16px;transition:all 0.3s ease}
.upload-area:hover .upload-icon{color:#7b42f6;transform:scale(1.05)}
.upload-icon.is-loading{animation:spin 1.2s linear infinite;color:#7b42f6}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

.upload-text{text-align:center}.upload-text p{margin:10px 0}
.upload-text em{color:#7b42f6;font-style:normal;font-weight:600;cursor:pointer;position:relative}
.upload-text em::after{content:'';position:absolute;bottom:-2px;left:0;width:100%;height:2px;background:#7b42f6;transform:scaleX(0);transition:transform 0.3s ease}
.upload-text em:hover::after{transform:scaleX(1)}

.analyzing-text{color:#7b42f6;display:flex;align-items:center;justify-content:center;gap:8px;font-weight:500}
.upload-tip{font-size:12px;color:#94a3b8;margin-top:4px}

.ai-options{margin-top:24px;padding:0 24px}
.ai-options :deep(.el-divider__text){background:#fff;color:#64748b;font-size:13px;padding:0 16px}
.template-tips{margin-top:20px;padding:0 24px 16px}
.template-tips :deep(.el-alert){border-radius:8px;border:none}

/* ==================== 操作栏 - 紫色主题 ==================== */
.analysis-result{position:relative}.result-actions{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap;align-items:center}
.result-actions .el-button{border-radius:8px;font-weight:500;padding:10px 20px;transition:all 0.3s ease}
.result-actions .el-button--primary{
  background:linear-gradient(135deg,#7b42f6 0%,#5a32a3 100%);
  border-color:#7b42f6;
  box-shadow:0 4px 12px rgba(123,66,246,0.3)
}
.result-actions .el-button--primary:hover{
  background:linear-gradient(135deg,#6d33e6 0%,#4a249c 100%);
  border-color:#6d33e6;
  transform:translateY(-1px);
  box-shadow:0 6px 16px rgba(123,66,246,0.4)
}
.history-badge{margin-left:6px}

/* ==================== 历史侧边栏 - 紫色主题 ==================== */
.history-sidebar {
  position: absolute;
  right: 0;
  top: 50px;
  width: 300px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.12);
  border: 1px solid rgba(147, 112, 219, 0.12);
  z-index: 10;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
  background: linear-gradient(90deg, #f8f7ff 0%, #fff 100%);
}
.history-title {
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5a32a3;
}
.history-list {
  padding: 10px;
}
.history-item {
  padding: 12px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  margin-bottom: 6px;
}
.history-item:hover {
  background: #f8f7ff;
  transform: translateX(2px);
  border-color: rgba(147, 112, 219, 0.15);
}
.history-item.active {
  border-color: #7b42f6;
  background: #f0edff;
  box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
}
.history-item-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.history-item-name {
  font-weight: 500;
  font-size: 13px;
  color: #5a32a3;
}
.history-item-meta {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  font-size: 11px;
  color: #7b6db3;
}
.top-mod {
  color: #ef4444;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.main-content{transition:margin-right 0.3s ease}.main-content.with-sidebar{margin-right:320px}

/* ==================== 统计卡片 - 紫色主题 ==================== */
.summary-cards{margin-bottom:24px}
.summary-card{
  background:#fff;
  border-radius:12px;
  padding:20px 24px;
  display:flex;
  gap:16px;
  align-items:center;
  border:1px solid rgba(147,112,219,0.12);
  box-shadow:0 4px 16px rgba(147,112,219,0.08);
  transition:all 0.3s ease
}
.summary-card:hover{
  box-shadow:0 8px 24px rgba(147,112,219,0.12);
  transform:translateY(-2px);
  border-color:rgba(147,112,219,0.2)
}
.summary-icon{
  width:52px;
  height:52px;
  border-radius:14px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:24px;
  flex-shrink:0;
  transition:all 0.3s ease;
  background:linear-gradient(135deg,#f5f3ff 0%,#ede9fe 100%);
  color:#7b42f6
}
.summary-card:hover .summary-icon{
  transform:scale(1.05);
  background:linear-gradient(135deg,#ede9fe 0%,#ddd6fe 100%)
}
.summary-info{flex:1}
.summary-value{font-size:28px;font-weight:700;color:#5a32a3;line-height:1.2}
.summary-label{font-size:14px;color:#7b6db3;margin-top:4px;font-weight:500}
.summary-sub{font-size:12px;color:#a898d8;margin-top:4px}

/* ==================== 卡片组件 - 紫色主题 ==================== */
.section-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.12);
  background: #fff;
  transition: all 0.3s ease;
}
.section-card:hover {
  box-shadow: 0 8px 24px rgba(147, 112, 219, 0.12);
  border-color: rgba(147, 112, 219, 0.2);
}
.section-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
  background: linear-gradient(90deg, #f8f7ff 0%, #fff 100%);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-title {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5a32a3;
  font-size: 15px;
}
.header-title .el-icon {
  color: #7b42f6;
  font-size: 18px;
}

/* 头部操作区域 - AI分析按钮 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-analyze-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border-color: #7b42f6;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.ai-analyze-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
  border-color: #6d33e6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
}

.ai-analyze-btn:disabled {
  background: #c0c0c0;
  border-color: #c0c0c0;
  cursor: not-allowed;
}

/* ==================== 图表卡片 - 紫色主题 ==================== */
.chart-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.12);
  background: #fff;
  transition: all 0.3s ease;
}
.chart-card:hover {
  box-shadow: 0 8px 24px rgba(147, 112, 219, 0.12);
  border-color: rgba(147, 112, 219, 0.2);
}
.chart-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(147, 112, 219, 0.1);
  background: linear-gradient(90deg, #f8f7ff 0%, #fff 100%);
}
.chart-title {
  font-weight: 600;
  color: #5a32a3;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ==================== AI 智能摘要样式 - 现代简约风格 ==================== */
:deep(.ai-summary-content) {
  padding: 8px 4px;
}

:deep(.ai-summary-overview) {
  font-size: 15px;
  line-height: 1.9;
  color: #4b5563;
  padding: 20px 24px;
  background: linear-gradient(135deg, #fef9e7 0%, #fdf3d2 100%);
  border-radius: 12px;
  border-left: 4px solid #f59e0b;
  margin-bottom: 28px;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.08);
}

:deep(.ai-summary-overview strong) {
  color: #b45309;
  font-weight: 600;
}

:deep(.ai-summary-section) {
  margin-bottom: 28px;
}

:deep(.ai-summary-section-title) {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
  padding: 0 4px 12px 4px;
  border-bottom: 1px solid #e5e7eb;
  letter-spacing: 0.3px;
}

:deep(.ai-summary-section-title .ai-icon) {
  font-size: 18px;
  width: 18px;
  height: 18px;
}

:deep(.ai-summary-list) {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 4px;
}

:deep(.ai-summary-item) {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 18px 22px;
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
  transition: all 0.25s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

:deep(.ai-summary-item:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

:deep(.ai-summary-item.risk-item) {
  background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
  border-color: #fecaca;
}

:deep(.ai-summary-item.risk-item:hover) {
  background: linear-gradient(135deg, #fef2f2 0%, #fee8e8 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
}

:deep(.ai-summary-item.action-item) {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-color: #bbf7d0;
}

:deep(.ai-summary-item.action-item:hover) {
  background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
}

:deep(.ai-summary-num) {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  position: relative;
}

:deep(.ai-summary-num.risk-num) {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.3);
}

:deep(.ai-summary-num.action-num) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
}

:deep(.ai-summary-text) {
  flex: 1;
  font-size: 14.5px;
  line-height: 1.75;
  color: #4b5563;
  padding-top: 2px;
}

:deep(.ai-summary-text strong) {
  color: #1f2937;
  font-weight: 600;
}

/* ==================== AI 状态标签样式 ==================== */
.ai-status-tag {
  border-radius: 12px;
  padding: 4px 12px;
  font-weight: 500;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.ai-status-tag.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.ai-status-tag.loading {
  background: linear-gradient(135deg, #f8f7ff 0%, #f0edff 100%) !important;
  color: #7b42f6 !important;
  border: 1px solid rgba(147, 112, 219, 0.3) !important;
}

.ai-status-tag .el-icon {
  font-size: 12px;
}

/* ==================== AI 加载状态 - 现代骨架屏风格 ==================== */
.ai-loading-container {
  padding: 32px 24px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.ai-loading-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #2563eb, transparent);
  animation: loading-bar 2s ease-in-out infinite;
}

@keyframes loading-bar {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0%); }
  100% { transform: translateX(100%); }
}

.ai-loading-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.ai-loading-pulse {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #dbeafe 0%, #2563eb 100%);
  animation: pulse 2s ease-in-out infinite;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-loading-pulse .el-icon {
  color: white;
  font-size: 20px;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
}

.ai-loading-info {
  flex: 1;
}

.ai-loading-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.ai-loading-desc {
  font-size: 13px;
  color: #64748b;
}

.ai-skeleton {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.5s ease-in-out infinite;
}

.ai-skeleton-line:nth-child(1) { width: 100%; }
.ai-skeleton-line:nth-child(2) { width: 85%; }
.ai-skeleton-line:nth-child(3) { width: 70%; }
.ai-skeleton-line:nth-child(4) { width: 90%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.ai-loading-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.ai-loading-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2563eb;
  animation: bounce 1.4s ease-in-out infinite both;
}

.ai-loading-dot:nth-child(1) { animation-delay: -0.32s; }
.ai-loading-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@keyframes pulse-highlight {
  0%, 100% { box-shadow: 0 0 0 3px rgba(245,158,11,0.3), 0 8px 16px -4px rgba(245,158,11,0.2); }
  50% { box-shadow: 0 0 0 6px rgba(245,158,11,0.15), 0 12px 24px -4px rgba(245,158,11,0.3); }
}

/* AI卡片样式 */.ai-loading-text-new {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.summary-content{padding:4px 0}.summary-section{margin-bottom:16px}.summary-section:last-child{margin-bottom:0}
.summary-title{font-weight:600;font-size:14px;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.summary-title.danger{color:#ef4444}.summary-title.warning{color:#f59e0b}
.summary-list{padding-left:4px}.summary-item{font-size:13px;line-height:1.8;color:#64748b;padding:2px 0}

.chart-row{margin-bottom:24px}
.chart-container{height:350px;width:100%}.clickable-chart{cursor:pointer}.chart-note{margin-top:8px}

.risk-section{margin-bottom:20px}.risk-section:last-child{margin-bottom:0}.risk-title{font-size:15px;margin-bottom:10px;padding-left:4px}
.risk-title.p0{color:#ef4444;border-left:3px solid #ef4444}.risk-title.p1{color:#f59e0b;border-left:3px solid #f59e0b}.risk-title.p2{color:#3b82f6;border-left:3px solid #3b82f6}

.focus-card{border:1px solid rgba(147,112,219,0.15);border-radius:12px;padding:16px;cursor:pointer;transition:all 0.25s ease;margin-bottom:16px;background:#fff;height:280px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 2px 8px rgba(147,112,219,0.06)}
.focus-card:hover{border-color:#7b42f6;box-shadow:0 8px 24px rgba(147,112,219,0.15);transform:translateY(-2px)}.focus-card.clickable{cursor:pointer}
.focus-card.highlighted{border-color:#f59e0b;box-shadow:0 0 0 3px rgba(245,158,11,0.3),0 8px 16px -4px rgba(245,158,11,0.2);transform:translateY(-2px);animation:pulse-highlight 1.5s ease-in-out}
.focus-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-shrink:0}
.focus-name{font-weight:600;font-size:15px;color:#5a32a3}.focus-badges{display:flex;gap:4px;flex-wrap:wrap}
.focus-body{font-size:13px;color:#64748b;flex:1;overflow-y:auto;padding-right:4px}.focus-body::-webkit-scrollbar{width:4px}.focus-body::-webkit-scrollbar-track{background:transparent}.focus-body::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:2px}.focus-stats{display:flex;gap:16px;margin-bottom:8px;font-size:12px;color:#94a3b8;flex-shrink:0}
.focus-points{padding-left:18px;margin:6px 0}.focus-points li{line-height:1.7}
.base-focus-points{margin-top:4px}
.ai-section-title{font-size:12px;font-weight:600;color:#7b42f6;margin:8px 0 6px;padding-bottom:4px;border-bottom:1px dashed rgba(147,112,219,0.2)}
.base-section-title{font-size:12px;font-weight:600;color:#64748b;margin:12px 0 6px;padding-bottom:4px;border-bottom:1px dashed #e2e8f0}
.ai-focus-preview{margin-top:8px;padding:8px 12px;background:#f0fdf4;border-radius:6px;border:1px solid #bbf7d0}
.ai-focus-label{font-size:12px;color:#16a34a;font-weight:600;display:flex;align-items:center;gap:4px}
.ai-focus-text{font-size:12px;color:#15803d;margin-top:4px;line-height:1.6}

.detail-section{margin-bottom:20px}.detail-section-title{font-size:14px;font-weight:600;color:#5a32a3;margin-bottom:10px;display:flex;align-items:center;gap:6px}
.module-stats-desc{margin-bottom:16px}
.dtype-tags{display:flex;flex-wrap:wrap;gap:4px}
.ai-section{background:#f8f7ff;border-radius:8px;padding:12px;border:1px solid rgba(147,112,219,0.15)}
.ai-title{color:#7b42f6!important}.ai-content{font-size:13px;line-height:1.8;color:#64748b}.cause-content{font-style:italic;color:#94a3b8}
.focus-points-list{padding-left:18px}.focus-points-list li{line-height:1.7;font-size:13px}
.bug-filter-bar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.bug-list-section{margin-top:8px}

/* 智能模块分析样式 */
.intelligent-focus{background:linear-gradient(135deg,#f8fafc 0%,#f1f5f9 100%);border:1px solid #cbd5e1}
.intelligent-focus-content{min-height:80px}
.focus-points-intelligent{display:flex;flex-direction:column;gap:12px}
.focus-point-item{padding:12px;background:#fff;border-radius:8px;border-left:3px solid #cbd5e1;transition:all 0.2s ease}
.focus-point-item.high{border-left-color:#ef4444;background:#fef2f2}
.focus-point-item.medium{border-left-color:#f59e0b;background:#fffbeb}
.focus-point-item.low{border-left-color:#3b82f6;background:#eff6ff}
.point-header{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.point-source{font-size:11px;color:#94a3b8;background:#f1f5f9;padding:2px 6px;border-radius:4px}
.point-source.ai{color:#7c3aed;background:#ede9fe;font-weight:500}
.point-desc{font-size:13px;color:#334155;line-height:1.6;margin-bottom:6px}
.point-suggestion{font-size:12px;color:#059669;display:flex;align-items:flex-start;gap:4px;line-height:1.5}
.point-root-cause{margin-top:4px}
.focus-loading-hint{text-align:center;color:#94a3b8;font-size:13px;padding:20px}
.technical-insights{margin-top:12px}

/* AI卡片样式 */
.ai-focus-card{height:100%;display:flex;flex-direction:column}
.ai-body{flex:1;display:flex;flex-direction:column;gap:8px}
.ai-point-item{padding:8px 10px;background:#f8fafc;border-radius:6px;border-left:3px solid #cbd5e1}
.ai-point-item.high{border-left-color:#ef4444;background:#fef2f2}
.ai-point-item.medium{border-left-color:#f59e0b;background:#fffbeb}
.ai-point-item.low{border-left-color:#3b82f6;background:#eff6ff}
.ai-point-type{margin-bottom:4px}
.ai-point-desc{font-size:12px;color:#475569;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.more-points-hint{text-align:center;font-size:12px;color:#94a3b8;padding:4px}
.ai-loading-card{height:100%}
.ai-loading-body{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:20px}
.ai-loading-text{font-size:12px;color:#94a3b8;margin-top:8px}

.slide-fade-enter-active,.slide-fade-leave-active{transition:all 0.3s ease}
.slide-fade-enter-from{transform:translateX(30px);opacity:0}.slide-fade-leave-to{transform:translateX(30px);opacity:0}

.export-options{padding:8px 0}
.drawer-header{display:flex;justify-content:space-between;align-items:center;width:100%}

/* ==================== 列表视图样式 - 紫色主题 ==================== */
.filter-bar {
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.filter-bar :deep(.el-input__wrapper) {
  box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
  border-radius: 8px;
  border: 1px solid rgba(147, 112, 219, 0.2);
  background: #ffffff;
}

.filter-bar :deep(.el-input__wrapper:hover),
.filter-bar :deep(.el-input__wrapper:focus) {
  box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
  border-color: #7b42f6;
}

.filter-bar-spacer {
  flex: 1;
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  overflow: hidden;
}

.history-card {
  flex: 1;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: 16px;
}

.history-card :deep(.el-table) {
  --el-table-border-color: rgba(147, 112, 219, 0.1);
  --el-table-header-bg-color: #ffffff;
  --el-table-row-hover-bg-color: #f8f7ff;
  border: none;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  min-height: 200px;
  box-shadow: none;
  transition: all 0.3s ease;
  background-color: transparent !important;
}

.history-card :deep(.el-table__header-wrapper) {
  background-color: #ffffff !important;
}

.history-card :deep(.el-table__header) {
  background-color: #ffffff !important;
}

.history-card :deep(th) {
  background-color: #ffffff !important;
  color: #5a32a3 !important;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid #e9ecef;
  padding: 0 !important;
  text-align: center;
  transition: all 0.3s ease;
}

.history-card :deep(th:hover) {
  background-color: #ffffff !important;
}

.history-card :deep(th .cell) {
  background-color: #ffffff !important;
  color: #5a32a3 !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
  line-height: 24px !important;
  padding: 16px !important;
}

.history-card :deep(.el-table__body-wrapper) {
  background-color: #ffffff !important;
}

.history-card :deep(.el-table__row) {
  transition: all 0.3s ease;
  background-color: #ffffff !important;
  line-height: 24px;
}

.history-card :deep(.el-table__row:hover) {
  background-color: #f8f7ff !important;
}

.history-card :deep(.el-table__row.el-table__row--striped) {
  background-color: #fafaff !important;
}

.history-card :deep(td) {
  padding: 14px 16px;
  border-bottom: 1px solid #e9ecef;
  color: #333;
  font-size: 14px;
  font-weight: 400;
  line-height: 24px;
  transition: all 0.3s ease;
  vertical-align: middle;
}


.history-card :deep(.el-table__empty-block) {
  padding: 60px 0;
  background: #ffffff !important;
}

.history-card :deep(.el-table__empty-text) {
  color: #666;
  font-size: 14px;
  line-height: 24px;
}

.file-name {
  font-weight: 500;
  color: #333;
}

/* 徽章样式 - 参考 XMindConverter 风格 */
.count-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  background: #e6f7ff;
  color: #1890ff;
  white-space: nowrap;
  min-width: 24px;
}

.version-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  background: #f5f3ff;
  color: #7b42f6;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.p0-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  background: #fff1f0;
  color: #f5222d;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.top-module-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  background: #f6ffed;
  color: #52c41a;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.time-text {
  color: #333;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
}

.action-buttons .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px !important;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.action-buttons .el-button--primary {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}

.action-buttons .el-button--primary:hover {
  background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
}

.action-buttons .el-button--danger {
  background: linear-gradient(135deg, #ff4d4f 0%, #f5222d 100%) !important;
  border: none !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}

.action-buttons .el-button--danger:hover {
  background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 34, 45, 0.4);
}

.text-gray {
  color: #a898d8;
}

/* ==================== 详情页头部 - 紫色主题 ==================== */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  margin-bottom: 20px;
}

.detail-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #5a32a3;
}

.detail-header-actions {
  display: flex;
  gap: 12px;
}

.detail-header-actions .el-button--primary {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border-color: #7b42f6;
}

.detail-header-actions .el-button--primary:hover {
  background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
  border-color: #6d33e6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
}

/* ==================== 上传对话框样式 ==================== */
.upload-dialog .upload-area {
  width: 100%;
  padding: 40px 0;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

/* ==================== 上传弹窗紫色主题 ==================== */
:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%);
  border-bottom: 1px solid rgba(147,112,219,0.15);
  padding: 16px 20px;
  margin-right: 0;
}

:deep(.el-dialog__title) {
  color: #5a32a3;
  font-weight: 600;
  font-size: 16px;
}

:deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #7b42f6;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid rgba(147,112,219,0.1);
  padding: 16px 20px;
}

/* 弹窗内按钮紫色主题 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
  border-color: #7b42f6;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
  border-color: #6d33e6;
}

/* 输入框紫色聚焦效果 */
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #7b42f6 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(147,112,219,0.5) inset;
}

/* ==================== 分页组件 - 紫色主题 ==================== */
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
}

.pagination-container :deep(.el-pagination) {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

/* 总条数 */
.pagination-container :deep(.el-pagination__total) {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  margin-right: 12px;
}

/* 每页条数选择器 */
.pagination-container :deep(.el-pagination__sizes) {
  margin-right: 12px;
}

.pagination-container :deep(.el-pagination__sizes .el-select .el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  box-shadow: none;
}

.pagination-container :deep(.el-pagination__sizes .el-select .el-input__wrapper:hover) {
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

.pagination-container :deep(.el-pagination__sizes .el-select .el-input__wrapper.is-focus) {
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15);
}

.pagination-container :deep(.el-pagination__sizes .el-select .el-input__inner) {
  color: #374151;
  font-weight: 500;
}

/* 上一页/下一页按钮 */
.pagination-container :deep(.el-pagination .btn-prev),
.pagination-container :deep(.el-pagination .btn-next) {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #6b7280;
  transition: all 0.3s ease;
}

.pagination-container :deep(.el-pagination .btn-prev:hover:not(:disabled)),
.pagination-container :deep(.el-pagination .btn-next:hover:not(:disabled)) {
  background: #f5f3ff;
  border-color: #a78bfa;
  color: #8b5cf6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2);
}

.pagination-container :deep(.el-pagination .btn-prev:disabled),
.pagination-container :deep(.el-pagination .btn-next:disabled) {
  background: #f5f5f5;
  border-color: #e0e0e0;
  color: #c0c0c0;
}

.pagination-container :deep(.el-pagination .btn-prev .el-icon),
.pagination-container :deep(.el-pagination .btn-next .el-icon) {
  font-size: 14px;
  font-weight: bold;
}

/* 页码按钮 */
.pagination-container :deep(.el-pager) {
  display: flex;
  gap: 8px;
}

.pagination-container :deep(.el-pager li) {
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
}

.pagination-container :deep(.el-pager li:hover:not(.is-active)) {
  background: #f5f3ff;
  border-color: #a78bfa;
  color: #8b5cf6;
  transform: translateY(-1px);
}

.pagination-container :deep(.el-pager li.is-active) {
  background: #f5f3ff;
  border-color: #a78bfa;
  color: #8b5cf6;
  box-shadow: 0 2px 8px rgba(167, 139, 250, 0.2);
}

.pagination-container :deep(.el-pager li.is-active:hover) {
  background: #ede9fe;
  border-color: #8b5cf6;
}

/* 跳转输入框 */
.pagination-container :deep(.el-pagination__jump) {
  color: #6b7280;
  font-weight: 500;
  margin-left: 12px;
}

.pagination-container :deep(.el-pagination__jump .el-input) {
  width: 50px;
  margin: 0 4px;
}

.pagination-container :deep(.el-pagination__jump .el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  box-shadow: none;
}

.pagination-container :deep(.el-pagination__jump .el-input__wrapper:hover) {
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

.pagination-container :deep(.el-pagination__jump .el-input__wrapper.is-focus) {
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.15);
}

.pagination-container :deep(.el-pagination__jump .el-input__inner) {
  color: #374151;
  font-weight: 500;
  text-align: center;
}
</style>
