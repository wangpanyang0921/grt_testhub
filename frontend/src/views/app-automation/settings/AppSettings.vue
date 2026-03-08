<template>
  <div class="page-container">
    <div class="card-container">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
        class="config-form"
      >
        <el-form-item label="ADB 路径" prop="adb_path">
          <el-input
            v-model="form.adb_path"
            placeholder="例如: adb 或 D:\\Android\\platform-tools\\adb.exe"
            clearable
          />
          <div class="form-tip">
            Android Debug Bridge 工具路径。如果 ADB 在系统 PATH 中，填写 "adb" 即可
          </div>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button type="primary" class="save-btn" @click="handleSave" :loading="saving">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button class="reset-btn" @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card-container" v-if="currentConfig.adb_path">
      <div class="section-title">当前配置信息</div>
      <el-descriptions :column="1" border class="config-descriptions">
        <el-descriptions-item label="ADB 路径">
          <el-tag>{{ currentConfig.adb_path || 'adb' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatTime(currentConfig.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatTime(currentConfig.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, RefreshLeft } from '@element-plus/icons-vue'
import { getAppConfig, updateAppConfig } from '@/api/app-automation'
import { formatDateTime } from '@/utils/app-automation-helpers'

const formRef = ref(null)
const saving = ref(false)

const form = reactive({
  adb_path: 'adb'
})

const currentConfig = reactive({
  adb_path: '',
  created_at: '',
  updated_at: ''
})

const rules = {
  adb_path: [
    { required: true, message: '请输入 ADB 路径', trigger: 'blur' }
  ]
}

// 加载配置
const loadConfig = async () => {
  try {
    const res = await getAppConfig()
    if (res.data.success && res.data.data) {
      Object.assign(form, res.data.data)
      Object.assign(currentConfig, res.data.data)
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 保存配置
const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    const res = await updateAppConfig(form)
    if (res.data.success) {
      ElMessage.success('配置保存成功')
      await loadConfig()
    } else {
      ElMessage.error(res.data.message || '配置保存失败')
    }
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('保存配置失败:', error)
      ElMessage.error('保存配置失败')
    }
  } finally {
    saving.value = false
  }
}

// 重置表单
const handleReset = () => {
  Object.assign(form, currentConfig)
}

const formatTime = formatDateTime

onMounted(() => {
  loadConfig()
})
</script>

<style scoped lang="scss">
.page-container {
  margin: -20px;
  min-height: calc(100% + 40px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
  line-height: 24px;
  gap: 20px;
  width: calc(100% + 40px);
  box-sizing: border-box;
  padding: 24px;
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #262626;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;
  }
}

.config-form {
  .el-form-item {
    margin-bottom: 24px;

    :deep(.el-form-item__label) {
      font-weight: 500;
      color: #333;
    }

    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px #d9d9d9 inset;

      &:hover {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 1px #7b42f6 inset;
      }
    }

    :deep(.el-input-group__prepend) {
      background: #f5f5f5;
      border-color: #d9d9d9;
      color: #666;
    }
  }

  .form-actions {
    margin-bottom: 0;
    padding-top: 8px;
  }
}

.form-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 6px;
  line-height: 1.5;
}

.save-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4) !important;
  }

  .el-icon {
    margin-right: 6px;
  }
}

.reset-btn {
  font-weight: 500 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  border-color: #d9d9d9 !important;
  color: #595959 !important;
  background: #ffffff !important;

  &:hover {
    color: #7b42f6 !important;
    border-color: #7b42f6 !important;
    background: #f8f7ff !important;
  }

  .el-icon {
    margin-right: 6px;
  }
}

.config-descriptions {
  :deep(.el-descriptions__label) {
    font-weight: 500;
    color: #333;
    background: #fafafa;
    width: 140px;
  }

  :deep(.el-descriptions__content) {
    color: #595959;
  }
}
</style>
