<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('project.projectDetail') }}</h1>
      <el-button type="primary" @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        {{ $t('common.back') }}
      </el-button>
    </div>

    <div class="card-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="$t('project.projectInfo')" name="info">
          <div v-if="project">
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="$t('project.projectName')">{{ project.name }}</el-descriptions-item>
              <el-descriptions-item :label="$t('project.status')">
                <el-tag :type="getStatusType(project.status)">{{ getStatusText(project.status) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('project.owner')">{{ project.owner?.username }}</el-descriptions-item>
              <el-descriptions-item :label="$t('project.createdAt')">{{ formatDate(project.created_at) }}</el-descriptions-item>
              <el-descriptions-item :label="$t('project.projectDescription')" :span="2">{{ project.description || $t('project.noDescription') }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="$t('project.projectMembers')" name="members">
          <div class="members-section">
            <el-button type="primary" @click="showAddMemberDialog = true">{{ $t('project.addMember') }}</el-button>
            <el-table :data="project?.members || []" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="user.username" :label="$t('project.username')" />
              <el-table-column prop="user.email" :label="$t('project.email')" />
              <el-table-column prop="role" :label="$t('project.role')" />
              <el-table-column prop="joined_at" :label="$t('project.joinedAt')">
                <template #default="{ row }">
                  {{ row.user?.username || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="邮箱">
                <template #default="{ row }">
                  {{ row.user?.email || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="角色">
                <template #default="{ row }">
                  {{ row.role || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="加入时间">
                <template #default="{ row }">
                  {{ formatDate(row.joined_at) || '-' }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('project.actions')" width="100">
                <template #default="{ row }">
                  <el-button size="small" type="danger" @click="removeMember(row)">{{ $t('common.delete') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="$t('project.environments')" name="environments">
          <div class="environments-section">
            <el-button type="primary" @click="showAddEnvDialog = true">{{ $t('project.addEnvironment') }}</el-button>
            <el-table :data="project?.environments || []" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="name" :label="$t('project.environmentName')" />
              <el-table-column prop="base_url" :label="$t('project.baseUrl')" />
              <el-table-column prop="description" :label="$t('project.description')" />
              <el-table-column prop="is_default" :label="$t('project.defaultEnvironment')">
                <template #default="{ row }">
                  <el-tag v-if="row.is_default" type="success">{{ $t('project.yes') }}</el-tag>
                  <span v-else>{{ $t('project.no') }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 添加成员对话框 -->
    <el-dialog v-model="showAddMemberDialog" title="添加项目成员" :close-on-click-modal="false" width="500px">
      <el-form ref="addMemberFormRef" :model="addMemberForm" :rules="addMemberRules" label-width="80px">
        <el-form-item label="用户" prop="user_id">
          <el-select v-model="addMemberForm.user_id" placeholder="请选择用户" filterable>
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="addMemberForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="开发者" value="developer" />
            <el-option label="测试者" value="tester" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddMemberDialog = false">取消</el-button>
          <el-button type="primary" @click="addMember">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const route = useRoute()
const { t } = useI18n()
const project = ref(null)
const activeTab = ref('info')
const showAddMemberDialog = ref(false)
const showAddEnvDialog = ref(false)
const users = ref([])
const addMemberFormRef = ref()

const addMemberForm = ref({
  user_id: '',
  role: 'tester'
})

const addMemberRules = {
  user_id: [
    { required: true, message: '请选择用户', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'blur' }
  ]
}

const fetchProject = async () => {
  try {
    const response = await api.get(`/projects/${route.params.id}/`)
    project.value = response.data
  } catch (error) {
    ElMessage.error(t('project.fetchDetailFailed'))
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/api-testing/users/')
    users.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

const getStatusType = (status) => {
  const typeMap = {
    active: 'success',
    paused: 'warning',
    completed: 'info',
    archived: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    active: t('project.active'),
    paused: t('project.paused'),
    completed: t('project.completed'),
    archived: t('project.archived')
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const addMember = async () => {
  try {
    const response = await api.post(`/projects/${route.params.id}/members/add/`, addMemberForm.value)
    ElMessage.success('成员添加成功')
    showAddMemberDialog.value = false
    // 重置表单
    addMemberForm.value.user_id = ''
    addMemberForm.value.role = 'tester'
    // 重新获取项目信息
    fetchProject()
  } catch (error) {
    ElMessage.error('添加成员失败')
  }
}

const removeMember = async (member) => {
  try {
    await api.delete(`/projects/${route.params.id}/members/${member.id}/`)
    ElMessage.success(t('project.memberDeleteSuccess'))
    fetchProject()
  } catch (error) {
    ElMessage.error(t('project.memberDeleteFailed'))
  }
}

onMounted(() => {
  fetchProject()
  fetchUsers()
})
</script>

<style lang="scss" scoped>
// 页面容器
.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #5a32a3;
    margin: 0;
    background: linear-gradient(135deg, #5a32a3 0%, #7b42f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  // 按钮样式
  .el-button {
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-1px);
    }

    // 返回按钮
    &:not(.el-button--primary) {
      border: 1px solid rgba(147, 112, 219, 0.3);
      color: #5a32a3;
      background: #ffffff;

      &:hover {
        border-color: #7b42f6;
        color: #7b42f6;
        background: rgba(123, 66, 246, 0.05);
      }
    }

    // 主要按钮
    &.el-button--primary {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;
      color: white;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

      &:hover {
        background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
      }
    }
  }
}

// 卡片容器
.card-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  flex: 1;
  padding: 24px;

  // Tabs 样式
  :deep(.el-tabs) {
    .el-tabs__header {
      margin-bottom: 24px;
      border-bottom: 1px solid rgba(147, 112, 219, 0.15);
    }

    .el-tabs__nav-wrap::after {
      background-color: rgba(147, 112, 219, 0.1);
    }

    .el-tabs__item {
      font-size: 15px;
      font-weight: 500;
      color: #666;
      padding: 0 24px;
      height: 44px;
      line-height: 44px;
      transition: all 0.3s ease;

      &:hover {
        color: #7b42f6;
      }

      &.is-active {
        color: #5a32a3;
        font-weight: 600;
      }
    }

    .el-tabs__active-bar {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      height: 3px;
      border-radius: 2px;
    }
  }

  // Descriptions 样式
  :deep(.el-descriptions) {
    .el-descriptions__label {
      background: linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%);
      color: #5a32a3;
      font-weight: 500;
      padding: 16px;
    }

    .el-descriptions__content {
      padding: 16px;
      color: #333;
    }

    .el-descriptions__cell {
      border: 1px solid rgba(147, 112, 219, 0.15);
    }
  }
}

// 成员和环境区域
.members-section, .environments-section {
  padding: 20px 0;

  .el-button {
    border-radius: 8px;
    transition: all 0.3s ease;

    &.el-button--primary {
      background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4);
      }
    }
  }
}

// 表格样式
:deep(.el-table) {
  background: transparent;
  border-radius: 8px;
  overflow: hidden;

  .el-table__header {
    th {
      background: linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%);
      color: #5a32a3;
      font-weight: 600;
      border-bottom: 1px solid rgba(147, 112, 219, 0.15);
      padding: 12px;
    }
  }

  .el-table__row {
    transition: all 0.3s ease;

    &:hover {
      background: rgba(147, 112, 219, 0.05);
    }

    td {
      border-bottom: 1px solid rgba(147, 112, 219, 0.08);
      padding: 12px;
    }
  }
}

// 标签样式
:deep(.el-tag) {
  border-radius: 4px;
  font-weight: 500;

  &.el-tag--success {
    background: rgba(103, 194, 58, 0.1);
    border-color: rgba(103, 194, 58, 0.3);
    color: #67c23a;
  }
}

// 对话框样式
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;

  .el-dialog__header {
    background: linear-gradient(135deg, #f8f7ff 0%, #f5f3ff 100%);
    padding: 20px 24px;
    margin: 0;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);

    .el-dialog__title {
      color: #5a32a3;
      font-weight: 600;
      font-size: 18px;
    }
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid rgba(147, 112, 219, 0.1);
  }
}

// 表单样式
:deep(.el-form) {
  .el-form-item__label {
    color: #5a32a3;
    font-weight: 500;
  }

  .el-input__wrapper,
  .el-select .el-input__wrapper {
    border-radius: 8px;
    border: 1px solid rgba(147, 112, 219, 0.3);
    box-shadow: none;

    &:hover, &.is-focus {
      border-color: #7b42f6;
      box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.1);
    }
  }
}
</style>