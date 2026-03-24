import request from '@/utils/api'

// 获取工具分类
export function getCategories() {
  return request({
    url: '/data-factory/categories/',
    method: 'get'
  })
}

// 获取数据工厂记录列表
export function getDataFactoryRecords(params) {
  return request({
    url: '/data-factory/',
    method: 'get',
    params
  })
}

// 获取数据工厂标签列表
export function getDataFactoryTags() {
  return request({
    url: '/data-factory/tags/',
    method: 'get'
  })
}

// 获取数据工厂分类列表
export function getDataFactoryCategories() {
  return request({
    url: '/data-factory/categories/',
    method: 'get'
  })
}

// 执行工具
export function executeTool(data) {
  return request({
    url: '/data-factory/',
    method: 'post',
    data
  })
}

// 获取历史记录
export function getHistory(params) {
  return request({
    url: '/data-factory/',
    method: 'get',
    params
  })
}

// 获取统计信息
export function getStatistics() {
  return request({
    url: '/data-factory/statistics/',
    method: 'get'
  })
}

// 删除记录
export function deleteRecord(id) {
  return request({
    url: `/data-factory/${id}/`,
    method: 'delete'
  })
}

// 批量生成
export function batchGenerate(data) {
  return request({
    url: '/data-factory/batch_generate/',
    method: 'post',
    data
  })
}

// DataFactoryRecord 类型定义
/**
 * @typedef {Object} DataFactoryRecord
 * @property {number} id - 记录ID
 * @property {string} tool_name - 工具名称
 * @property {string} tool_name_display - 工具显示名称
 * @property {string} tool_category - 工具分类
 * @property {string} tool_category_display - 分类显示名称
 * @property {Object} input_params - 输入参数
 * @property {Object} output_data - 输出数据
 * @property {string} created_at - 创建时间
 * @property {string[]} tags - 标签列表
 */

// Excel智能填充 - 分析模板
export function analyzeExcelTemplate(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/data-factory/excel-filler/analyze/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// Excel智能填充 - 预览数据
export function previewFilledData(file, rowCount = 5, customFields = {}) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('row_count', String(rowCount))
  if (Object.keys(customFields).length > 0) {
    formData.append('custom_fields', JSON.stringify(customFields))
  }
  return request({
    url: '/data-factory/excel-filler/preview/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// Excel智能填充 - 生成并下载文件
export function fillExcelData(file, rowCount = 10, customFields = {}) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('row_count', String(rowCount))
  if (Object.keys(customFields).length > 0) {
    formData.append('custom_fields', JSON.stringify(customFields))
  }
  return request({
    url: '/data-factory/excel-filler/fill/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    responseType: 'blob'
  })
}

export {}
