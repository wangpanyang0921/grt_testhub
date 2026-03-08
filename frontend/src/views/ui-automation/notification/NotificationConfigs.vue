<template>
  <div class="page-container">
    <!-- 页面头部 + Tab切换 -->
    <div class="page-header-card">
      <div class="page-header-content">
        <h1>{{ $t('uiAutomation.notification.configs.pageTitle') }}</h1>
      </div>
      <div class="header-tabs">
        <div
          class="header-tab-item"
          :class="{ active: activeTab === 'feishu' }"
          @click="activeTab = 'feishu'"
        >
          {{ $t('uiAutomation.notification.configs.feishuBot') }}
        </div>
        <div
          class="header-tab-item"
          :class="{ active: activeTab === 'wechat' }"
          @click="activeTab = 'wechat'"
        >
          {{ $t('uiAutomation.notification.configs.wechatBot') }}
        </div>
        <div
          class="header-tab-item"
          :class="{ active: activeTab === 'dingtalk' }"
          @click="activeTab = 'dingtalk'"
        >
          {{ $t('uiAutomation.notification.configs.dingtalkBot') }}
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="card-container">
      <div class="tab-content-wrapper">

        <!-- 飞书机器人 -->
        <div v-show="activeTab === 'feishu'" class="tab-panel">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="feishuFormRef"
                  :model="webhookBots.feishu"
                  label-position="left"
                  label-width="140px"
                  class="config-form inline-form"
              >
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.botName')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.feishu.name"
                          :placeholder="$t('uiAutomation.notification.configs.feishuBotNamePlaceholder')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.webhookUrl')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.feishu.webhook_url"
                          :placeholder="$t('uiAutomation.notification.configs.webhookPlaceholder')"
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.feishuUrlHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item class="all-switches-item">
                      <div class="switches-row">
                        <div class="switch-item">
                          <span class="switch-label">机器人启用状态</span>
                          <el-switch v-model="webhookBots.feishu.enabled"/>
                        </div>
                        <div class="switch-item">
                          <span class="switch-label">{{ $t('uiAutomation.notification.configs.uiAutomationTest') }}</span>
                          <el-switch v-model="webhookBots.feishu.enable_ui_automation" />
                        </div>
                        <div class="switch-item">
                          <span class="switch-label">{{ $t('uiAutomation.notification.configs.apiTest') }}</span>
                          <el-switch v-model="webhookBots.feishu.enable_api_testing" />
                        </div>
                      </div>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" class="save-btn" @click="saveWebhookBot('feishu')">
                    {{ $t('uiAutomation.notification.configs.saveFeishuConfig') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </div>

        <!-- 企业微信机器人 -->
        <div v-show="activeTab === 'wechat'" class="tab-panel">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="wechatFormRef"
                  :model="webhookBots.wechat"
                  label-position="left"
                  label-width="140px"
                  class="config-form inline-form"
              >
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.botName')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.wechat.name"
                          :placeholder="$t('uiAutomation.notification.configs.wechatBotNamePlaceholder')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.webhookUrl')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.wechat.webhook_url"
                          :placeholder="$t('uiAutomation.notification.configs.webhookPlaceholder')"
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.wechatUrlHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item class="all-switches-item">
                      <div class="switches-row">
                        <div class="switch-item">
                          <span class="switch-label">机器人启用状态</span>
                          <el-switch v-model="webhookBots.wechat.enabled"/>
                        </div>
                        <div class="switch-item">
                          <span class="switch-label">{{ $t('uiAutomation.notification.configs.uiAutomationTest') }}</span>
                          <el-switch v-model="webhookBots.wechat.enable_ui_automation" />
                        </div>
                        <div class="switch-item">
                          <span class="switch-label">{{ $t('uiAutomation.notification.configs.apiTest') }}</span>
                          <el-switch v-model="webhookBots.wechat.enable_api_testing" />
                        </div>
                      </div>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" class="save-btn" @click="saveWebhookBot('wechat')">
                    {{ $t('uiAutomation.notification.configs.saveWechatConfig') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </div>

        <!-- 钉钉机器人 -->
        <div v-show="activeTab === 'dingtalk'" class="tab-panel">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="dingtalkFormRef"
                  :model="webhookBots.dingtalk"
                  label-position="left"
                  label-width="140px"
                  class="config-form inline-form"
              >
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.botName')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.dingtalk.name"
                          :placeholder="$t('uiAutomation.notification.configs.dingtalkBotNamePlaceholder')"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.webhookUrl')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.dingtalk.webhook_url"
                          :placeholder="$t('uiAutomation.notification.configs.webhookPlaceholder')"
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.dingtalkUrlHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item :label="$t('uiAutomation.notification.configs.signatureSecret')" class="inline-form-item">
                      <el-input
                          v-model="webhookBots.dingtalk.secret"
                          :placeholder="$t('uiAutomation.notification.configs.signatureSecretPlaceholder')"
                          type="password"
                          show-password
                      />
                      <div class="form-item-hint">
                        {{ $t('uiAutomation.notification.configs.signatureSecretHint') }}
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item class="all-switches-item">
                      <div class="switches-row">
                        <div class="switch-item">
                          <span class="switch-label">机器人启用状态</span>
                          <el-switch v-model="webhookBots.dingtalk.enabled"/>
                        </div>
                        <div class="switch-item">
                          <span class="switch-label">{{ $t('uiAutomation.notification.configs.uiAutomationTest') }}</span>
                          <el-switch v-model="webhookBots.dingtalk.enable_ui_automation" />
                        </div>
                        <div class="switch-item">
                          <span class="switch-label">{{ $t('uiAutomation.notification.configs.apiTest') }}</span>
                          <el-switch v-model="webhookBots.dingtalk.enable_api_testing" />
                        </div>
                      </div>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" class="save-btn" @click="saveWebhookBot('dingtalk')">
                    {{ $t('uiAutomation.notification.configs.saveDingtalkConfig') }}
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {
  getUnifiedNotificationConfigs,
  createUnifiedNotificationConfig,
  updateUnifiedNotificationConfig
} from '@/api/core.js'
import { useI18n } from 'vue-i18n'

export default {
  name: 'NotificationConfigs',
  setup() {
    const { t } = useI18n()

    // 数据状态
    const feishuFormRef = ref(null)
    const wechatFormRef = ref(null)
    const dingtalkFormRef = ref(null)
    const activeTab = ref('feishu')

    // Webhook机器人配置
    const webhookBots = reactive({
      feishu: {
        name: '',
        webhook_url: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      },
      wechat: {
        name: '',
        webhook_url: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      },
      dingtalk: {
        name: '',
        webhook_url: '',
        secret: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      }
    })

    // 获取config_type映射
    const getConfigType = (botType) => {
      const configTypeMap = {
        'feishu': 'webhook_feishu',
        'wechat': 'webhook_wechat',
        'dingtalk': 'webhook_dingtalk'
      }
      return configTypeMap[botType]
    }

    // 获取机器人显示名称
    const getBotDisplayName = (botType) => {
      const displayNameMap = {
        'feishu': t('uiAutomation.notification.configs.platforms.feishu'),
        'wechat': t('uiAutomation.notification.configs.platforms.wechatWork'),
        'dingtalk': t('uiAutomation.notification.configs.platforms.dingtalk')
      }
      return displayNameMap[botType] || botType
    }

    // 保存Webhook机器人配置
    const saveWebhookBot = async (botType) => {
      const formRef = botType === 'feishu' ? feishuFormRef.value :
          botType === 'wechat' ? wechatFormRef.value :
              dingtalkFormRef.value

      if (!formRef) return

      try {
        const configType = getConfigType(botType)
        const botDisplayName = getBotDisplayName(botType)

        // 检查是否已存在对应类型的机器人配置
        let webhookConfigId = null
        try {
          const response = await getUnifiedNotificationConfigs({ config_type: configType })
          if (response.data.results && response.data.results.length > 0) {
            webhookConfigId = response.data.results[0].id
          }
        } catch (error) {
          console.log(t('uiAutomation.notification.configs.messages.noExistingConfig'))
        }

        const botConfig = webhookBots[botType]
        let requestData

        if (webhookConfigId) {
          // 更新现有配置 - 需要先获取现有配置，然后更新webhook_bots
          const configResponse = await getUnifiedNotificationConfigs({ config_type: configType })
          const existingConfig = configResponse.data.results[0]

          // 合并现有的webhook_bots和其他字段
          const updatedWebhookBots = existingConfig.webhook_bots || {}
          const botData = {
            name: botConfig.name || `${botType}机器人`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          // 钉钉机器人需要额外保存secret字段
          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          updatedWebhookBots[botType] = botData

          requestData = {
            name: existingConfig.name || `${botDisplayName}${t('uiAutomation.notification.configs.title')}`,
            config_type: configType,
            webhook_bots: updatedWebhookBots,
            is_active: true
          }

          // 更新现有配置
          await updateUnifiedNotificationConfig(webhookConfigId, requestData)
          const successMsgKey = botType === 'feishu' ? 'feishuUpdateSuccess' :
              botType === 'wechat' ? 'wechatUpdateSuccess' : 'dingtalkUpdateSuccess'
          ElMessage.success(t(`uiAutomation.notification.configs.messages.${successMsgKey}`))
        } else {
          // 创建新配置
          const botData = {
            name: botConfig.name || `${botType}机器人`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          // 钉钉机器人需要额外保存secret字段
          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          requestData = {
            name: `${botDisplayName}${t('uiAutomation.notification.configs.title')}`,
            config_type: configType,
            webhook_bots: {
              [botType]: botData
            },
            is_active: true
          }

          await createUnifiedNotificationConfig(requestData)
          const successMsgKey = botType === 'feishu' ? 'feishuCreateSuccess' :
              botType === 'wechat' ? 'wechatCreateSuccess' : 'dingtalkCreateSuccess'
          ElMessage.success(t(`uiAutomation.notification.configs.messages.${successMsgKey}`))
        }

        // 重新加载数据以确保状态同步
        fetchWebhookConfig(botType)
      } catch (error) {
        console.error('保存Webhook机器人配置失败:', error)
        const failedMsgKey = botType === 'feishu' ? 'feishuSaveFailed' :
            botType === 'wechat' ? 'wechatSaveFailed' : 'dingtalkSaveFailed'
        ElMessage.error(t(`uiAutomation.notification.configs.messages.${failedMsgKey}`) + ': ' + (error.response?.data?.detail || error.message))
      }
    }

    // 获取Webhook机器人配置
    const fetchWebhookConfig = async (botType) => {
      try {
        const configType = getConfigType(botType)
        const response = await getUnifiedNotificationConfigs({ config_type: configType })
        if (response.data.results && response.data.results.length > 0) {
          const config = response.data.results[0]

          if (config.webhook_bots && config.webhook_bots[botType]) {
            const bot = config.webhook_bots[botType]
            webhookBots[botType].name = bot.name || ''
            webhookBots[botType].webhook_url = bot.webhook_url || ''
            webhookBots[botType].enabled = bot.enabled !== false
            webhookBots[botType].enable_ui_automation = bot.enable_ui_automation !== false
            webhookBots[botType].enable_api_testing = bot.enable_api_testing !== false
            // 钉钉机器人需要额外读取secret字段
            if (botType === 'dingtalk' && bot.secret) {
              webhookBots[botType].secret = bot.secret
            }
          }
        }
      } catch (error) {
        console.error(t('uiAutomation.notification.configs.messages.getConfigFailed'), error)
      }
    }

    // 获取所有Webhook机器人配置
    const fetchAllWebhookConfigs = async () => {
      try {
        // 遍历所有机器人类型，分别获取配置
        for (const botType of Object.keys(webhookBots)) {
          await fetchWebhookConfig(botType)
        }
      } catch (error) {
        console.error(t('uiAutomation.notification.configs.messages.getAllConfigFailed'), error)
      }
    }

    // 组件挂载时获取数据
    onMounted(async () => {
      try {
        console.log('NotificationConfigs 组件开始初始化')
        await fetchAllWebhookConfigs()
        console.log('NotificationConfigs 组件初始化完成')
      } catch (error) {
        console.error('NotificationConfigs 组件初始化失败:', error)
      }
    })

    return {
      feishuFormRef,
      wechatFormRef,
      dingtalkFormRef,
      activeTab,
      webhookBots,
      saveWebhookBot,
      fetchWebhookConfig,
      fetchAllWebhookConfigs
    }
  }
}
</script>

<style scoped lang="scss">
:root {
  --primary-color: #7b42f6;
  --primary-dark: #5a32a3;
  --primary-light: #f8f7ff;
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

.config-form {
  :deep(.el-form-item) {
    .el-form-item__label {
      text-align: right !important;
      width: 140px !important;
      padding-right: 20px !important;
      line-height: 36px !important;
      font-size: 14px !important;
      color: #606266 !important;
      font-weight: 500 !important;
      justify-content: flex-end !important;
    }
  }
}

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

.page-header-card {
  padding: 24px 28px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(147, 112, 219, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;

  .page-header-content {
    display: flex;
    align-items: center;

    h1 {
      font-size: 20px;
      font-weight: 600;
      color: #262626;
      margin: 0;
    }
  }

  .header-tabs {
    display: flex;
    gap: 8px;
    background: #f5f3ff;
    padding: 4px;
    border-radius: 10px;

    .header-tab-item {
      padding: 10px 24px;
      font-size: 14px;
      font-weight: 500;
      color: #595959;
      cursor: pointer;
      border-radius: 8px;
      transition: all 0.3s ease;

      &:hover {
        color: #7b42f6;
        background: rgba(123, 66, 246, 0.08);
      }

      &.active {
        color: #ffffff;
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);
      }
    }
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
}

.tab-content-wrapper {
  padding: 0;
}

.tab-content {
  min-height: 500px;
  padding: 24px;
}

.config-section {
  padding: 20px 0;

  h3 {
    margin: 0 0 20px 0;
    font-size: 18px;
    font-weight: 600;
    color: #5a32a3;
  }
}

.form-item-hint {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.inline-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;

    &.inline-form-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 24px;

      .el-form-item__content {
        flex: 1;
        margin-left: 0 !important;

        .el-input {
          width: 100%;
        }

        .form-item-hint {
          margin-left: 0;
          height: 20px;
          line-height: 20px;
        }
      }
    }

    &.all-switches-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 24px;

      .el-form-item__label {
        width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
      }

      .el-form-item__content {
        margin-left: 0 !important;
        padding-left: 0 !important;
      }
    }
  }
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.save-btn {
  background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 10px 24px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3) !important;
  transition: all 0.3s ease !important;

  &:hover {
    background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(123, 66, 246, 0.4) !important;
  }
}

.enable-switch-item {
  :deep(.el-form-item__label) {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  :deep(.el-form-item__content) {
    display: flex;
    align-items: center;
  }
}

.switches-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0;

  .switch-item {
    display: flex;
    align-items: center;
    gap: 12px;

    .switch-label {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
      line-height: 36px;
      width: 140px;
      flex-shrink: 0;
      text-align: right;
      padding-right: 20px;
    }
  }
}

/* 自定义复选框样式 - 与头部紫色一致 */
:deep(.el-checkbox) {
  margin-right: 24px;

  .el-checkbox__input {
    .el-checkbox__inner {
      width: 18px;
      height: 18px;
      border-radius: 4px;
      border: 2px solid #d9d9d9;
      transition: all 0.3s ease;

      &::after {
        width: 5px;
        height: 9px;
        left: 5px;
        top: 2px;
      }
    }

    &.is-checked {
      .el-checkbox__inner {
        background-color: #7b42f6;
        border-color: #7b42f6;

        &:hover {
          background-color: #5a32a3;
          border-color: #5a32a3;
        }
      }
    }

    &.is-focus {
      .el-checkbox__inner {
        border-color: #7b42f6;
      }
    }
  }

  .el-checkbox__label {
    font-size: 15px;
    color: #595959;
    padding-left: 10px;
    transition: all 0.3s ease;
  }

  &.is-checked {
    .el-checkbox__label {
      color: #7b42f6;
      font-weight: 500;
    }
  }

  &:hover {
    .el-checkbox__inner {
      border-color: #7b42f6;
    }
  }
}

/* 自定义开关样式 - 与头部紫色一致 */
:deep(.el-switch.is-active .el-switch__core) {
  background-color: #7b42f6 !important;
}

:deep(.el-switch.is-active .el-switch__core:hover) {
  background-color: #5a32a3 !important;
}

/* 自定义开关滑块颜色 */
:deep(.el-switch__core .el-switch__button) {
  background-color: white !important;
}

/* 确保开关激活状态的边框和背景都是紫色 */
:deep(.el-switch.is-active) {
  --el-switch-on-color: #7b42f6 !important;
  --el-switch-on-border-color: #7b42f6 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-configs-container {
    padding: 16px;
  }

  .page-header {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .notification-tabs :deep(.el-tabs__item) {
    padding: 12px 20px;
    font-size: 14px;
  }

  .tab-content {
    padding: 16px;
  }
}
</style>
