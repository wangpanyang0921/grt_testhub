<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">{{ $t('testcase.create') }}</h2>
      <div class="header-actions">
        <el-button type="primary" class="action-btn edit-btn" @click="handleSubmit" :loading="submitting">
          <el-icon><Check /></el-icon>
          <span>{{ $t('testcase.createCase') }}</span>
        </el-button>
      </div>
    </div>

    <!-- 表单卡片 -->
    <div class="card-container">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="testcase-form">
        <!-- 属性设置区域 -->
        <div class="form-section">
          <h3 class="section-title">{{ $t('testcase.properties') }}</h3>

          <el-row :gutter="20" class="form-row">
            <el-col :span="12">
              <el-form-item :label="$t('testcase.project')" prop="category_path">
                <el-input
                  v-model="form.category_path"
                  :placeholder="$t('testcase.categoryPathPlaceholder')"
                  maxlength="500"
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item :label="$t('testcase.moduleLabel')" prop="module">
                <el-input
                  v-model="form.module"
                  :placeholder="$t('testcase.modulePlaceholder')"
                  maxlength="200"
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item :label="$t('testcase.priority')" prop="priority">
                <el-select v-model="form.priority" :placeholder="$t('testcase.selectPriority')">
                  <el-option label="P0" value="critical">
                    <span class="priority-option critical">P0</span>
                  </el-option>
                  <el-option label="P1" value="high">
                    <span class="priority-option high">P1</span>
                  </el-option>
                  <el-option label="P2" value="medium">
                    <span class="priority-option medium">P2</span>
                  </el-option>
                  <el-option label="P3" value="low">
                    <span class="priority-option low">P3</span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 测试内容区域 -->
        <div class="form-section">
          <h3 class="section-title">{{ $t('testcase.testContent') }}</h3>

          <el-form-item :label="$t('testcase.caseTitle')" prop="title">
            <el-input
              v-model="form.title"
              :placeholder="$t('testcase.caseTitlePlaceholder')"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item :label="$t('testcase.preconditions')" prop="preconditions">
            <el-input
              v-model="form.preconditions"
              type="textarea"
              :rows="3"
              :placeholder="$t('testcase.preconditionsPlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="$t('testcase.steps')" prop="steps">
            <el-input
              v-model="form.steps"
              type="textarea"
              :rows="6"
              maxlength="1000"
              show-word-limit
              :placeholder="$t('testcase.stepsPlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="$t('testcase.expectedResult')" prop="expected_result">
            <el-input
              v-model="form.expected_result"
              type="textarea"
              :rows="6"
              :placeholder="$t('testcase.expectedResultPlaceholder')"
            />
          </el-form-item>
        </div>

        <!-- 底部操作按钮已隐藏，创建按钮移至页面顶部 -->
        <!--
        <div class="form-actions">
          <el-button @click="$router.back()" class="action-btn cancel-btn">
            <el-icon><ArrowLeft /></el-icon>
            <span>{{ $t('common.cancel') }}</span>
          </el-button>
          <el-button type="primary" class="action-btn edit-btn" @click="handleSubmit" :loading="submitting">
            <el-icon><Check /></el-icon>
            <span>{{ $t('testcase.createCase') }}</span>
          </el-button>
        </div>
        -->
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check } from '@element-plus/icons-vue'
import api from '@/utils/api'

const { t } = useI18n()
const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  category_path: '',
  module: '',
  priority: 'medium',
  test_type: 'text',
  preconditions: '',
  steps: '',
  expected_result: '',
  version_ids: []
})

const rules = {
  title: [
    { required: true, message: computed(() => t('testcase.titleRequired')), trigger: 'blur' },
    { min: 5, max: 500, message: computed(() => t('testcase.titleLength')), trigger: 'blur' }
  ],
  expected_result: [
    { required: true, message: computed(() => t('testcase.expectedResultRequired')), trigger: 'blur' }
  ],
  steps: [
    { max: 1000, message: computed(() => t('testcase.stepsMaxLength')), trigger: 'blur' }
  ],
  category_path: [
    { required: true, message: '请输入归属目录', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await api.post('/testcases/', form)
        ElMessage.success(t('testcase.createSuccess'))
        router.push('/ai-generation/testcases')
      } catch (error) {
        ElMessage.error(t('testcase.createFailed'))
        console.error('Submit error:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  // 组件挂载时的初始化逻辑
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  display: flex;
  flex-direction: column;
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

  .header-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
}

.card-container {
  background: #ffffff;
  border: 1px solid rgba(147, 112, 219, 0.12);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.08);
  padding: 32px;
  flex: 1;
}

.testcase-form {
  .form-section {
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);

    &:last-of-type {
      border-bottom: none;
      margin-bottom: 0;
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-left: 10px;
    border-left: 4px solid #7b42f6;
    color: #5a32a3;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .el-form-item {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    :deep(.el-form-item__label) {
      color: #5a32a3;
      font-weight: 500;
      font-size: 14px;
    }

    :deep(.el-input__wrapper),
    :deep(.el-textarea__inner),
    :deep(.el-select .el-input__wrapper) {
      box-shadow: 0 2px 8px rgba(147, 112, 219, 0.08);
      border-radius: 8px;
      border: 1px solid rgba(147, 112, 219, 0.15);
      background: #ffffff;
      transition: all 0.3s ease;

      &:hover,
      &:focus,
      &.is-focus {
        border-color: #7b42f6;
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15), 0 0 0 3px rgba(123, 66, 246, 0.1);
      }
    }

    :deep(.el-input__inner),
    :deep(.el-textarea__inner) {
      color: #333;
      font-size: 14px;

      &::placeholder {
        color: #999;
      }
    }

    :deep(.el-textarea__inner) {
      padding: 12px 16px;
      line-height: 1.6;
    }

    :deep(.el-input__count) {
      color: #999;
      font-size: 12px;
      background: transparent;
    }
  }

  .el-row {
    margin-bottom: 0;
  }

  .form-row {
    margin-bottom: 20px;

    &:last-child {
      margin-bottom: 0;
    }

    .el-form-item {
      margin-bottom: 0;
    }
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid rgba(147, 112, 219, 0.1);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 24px !important;
  border-radius: 8px;
  transition: all 0.3s ease;
  min-width: auto !important;

  .el-icon {
    font-size: 16px;
  }

  span {
    font-size: 14px;
  }

  &.edit-btn {
    background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;

    &:hover {
      background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4) !important;
    }

    &:active {
      transform: translateY(0);
    }

    .el-icon,
    span {
      color: #ffffff !important;
    }
  }

  &.cancel-btn {
    border: 1px solid rgba(147, 112, 219, 0.3) !important;
    color: #5a32a3 !important;
    background: #ffffff !important;

    &:hover {
      border-color: #7b42f6 !important;
      color: #7b42f6 !important;
      background: rgba(123, 66, 246, 0.05) !important;
      transform: translateY(-1px);
    }

    .el-icon,
    span {
      color: #5a32a3 !important;
    }
  }
}

.priority-option {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  line-height: 20px;

  &.low {
    background: #f6ffed;
    color: #52c41a;
  }

  &.medium {
    background: #fff7e6;
    color: #fa8c16;
  }

  &.high {
    background: #fff1f0;
    color: #f5222d;
  }

  &.critical {
    background: #fff1f0;
    color: #cf1322;
    font-weight: 600;
  }
}

// 响应式布局
@media (max-width: 1200px) {
  .page-container {
    padding: 16px;
  }

  .page-header {
    padding: 20px;

    .page-title {
      font-size: 20px;
    }
  }

  .card-container {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;

    .page-title {
      font-size: 18px;
    }

    .header-actions {
      width: 100%;
    }
  }

  .card-container {
    padding: 16px;
  }

  .testcase-form {
    .el-row {
      .el-col {
        width: 100%;
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }

  .form-actions {
    flex-direction: column;

    .action-btn {
      width: 100%;
      justify-content: center;
    }
  }
}
</style>
