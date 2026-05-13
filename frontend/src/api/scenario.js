import request from '@/utils/api'

// ==================== 自动化场景 API ====================

// 获取场景列表
export function getScenarios(params) {
  return request({
    url: '/api-testing/scenarios/',
    method: 'get',
    params
  })
}

// 创建场景
export function createScenario(data) {
  return request({
    url: '/api-testing/scenarios/',
    method: 'post',
    data
  })
}

// 获取场景详情
export function getScenario(id) {
  return request({
    url: `/api-testing/scenarios/${id}/`,
    method: 'get'
  })
}

// 更新场景
export function updateScenario(id, data) {
  return request({
    url: `/api-testing/scenarios/${id}/`,
    method: 'put',
    data
  })
}

// 删除场景
export function deleteScenario(id) {
  return request({
    url: `/api-testing/scenarios/${id}/`,
    method: 'delete'
  })
}

// 执行场景
export function executeScenario(id) {
  return request({
    url: `/api-testing/scenarios/${id}/execute/`,
    method: 'post'
  })
}

// 获取场景执行历史
export function getScenarioExecutions(id, params = {}) {
  return request({
    url: `/api-testing/scenarios/${id}/executions/`,
    method: 'get',
    params
  })
}

// 获取可引用的场景列表（用于场景引用）
export function getAvailableReferences(id) {
  return request({
    url: `/api-testing/scenarios/${id}/available_references/`,
    method: 'get'
  })
}

// ==================== 场景步骤 API ====================

// 获取步骤列表
export function getScenarioSteps(scenarioId) {
  return request({
    url: '/api-testing/scenario-steps/',
    method: 'get',
    params: { scenario_id: scenarioId }
  })
}

// 创建步骤
export function createScenarioStep(data) {
  return request({
    url: '/api-testing/scenario-steps/',
    method: 'post',
    data
  })
}

// 获取步骤详情
export function getScenarioStep(id) {
  return request({
    url: `/api-testing/scenario-steps/${id}/`,
    method: 'get'
  })
}

// 更新步骤
export function updateScenarioStep(id, data) {
  return request({
    url: `/api-testing/scenario-steps/${id}/`,
    method: 'put',
    data
  })
}

// 删除步骤
export function deleteScenarioStep(id) {
  return request({
    url: `/api-testing/scenario-steps/${id}/`,
    method: 'delete'
  })
}

// 重新排序步骤
export function reorderScenarioStep(id, data) {
  return request({
    url: `/api-testing/scenario-steps/${id}/reorder/`,
    method: 'post',
    data
  })
}

// ==================== 执行记录 API ====================

// 获取执行记录列表
export function getExecutions(params = {}) {
  return request({
    url: '/api-testing/scenario-executions/',
    method: 'get',
    params
  })
}

// 获取执行详情
export function getExecution(id) {
  return request({
    url: `/api-testing/scenario-executions/${id}/`,
    method: 'get'
  })
}

// ==================== Apifox 导入 API ====================

// 验证导入文件
export function validateApifoxImport(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/api-testing/apifox/import-v2/validate/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 执行导入
export function importApifox(data) {
  return request({
    url: '/api-testing/apifox/import-v2/',
    method: 'post',
    data
  })
}
