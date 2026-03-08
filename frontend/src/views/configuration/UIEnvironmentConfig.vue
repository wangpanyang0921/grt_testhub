<template>
  <div class="page-container">
    <div class="card-container">
      <div class="os-check-section">
        <div class="os-info">
          <div class="os-label">{{ $t('configuration.uiEnv.operatingSystem') }}</div>
          <div class="os-name">{{ environmentData?.os || '-' }}</div>
        </div>
        <div class="check-action">
          <el-button type="primary" class="check-btn" @click="checkEnvironment" :loading="checking">
            <el-icon><Refresh /></el-icon>
            {{ $t('configuration.uiEnv.checkEnvironment') }}
          </el-button>
          <div v-if="lastCheckTime" class="last-check">
            {{ $t('configuration.uiEnv.lastCheckTime') }}: {{ lastCheckTime }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="environmentData" class="card-container">
      <!-- 系统浏览器 (Selenium) -->
      <div class="section-title">
        {{ $t('configuration.uiEnv.systemBrowsers') }}
      </div>
      <div class="browser-cards">
        <div v-for="browser in environmentData.system_browsers" :key="browser.name" class="browser-card">
          <div class="browser-content">
            <div class="browser-icon">
              <img :src="getBrowserIcon(browser.name)" :alt="browser.name" />
            </div>
            <div class="browser-info">
              <h3>{{ formatBrowserName(browser.name) }}</h3>
              <div class="status-row">
                <el-tag :type="browser.installed ? 'success' : 'info'" effect="dark">
                  {{ browser.installed ? (browser.version || $t('configuration.uiEnv.installed')) : $t('configuration.uiEnv.notInstalled') }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Playwright 浏览器 -->
      <div class="section-title">
        {{ $t('configuration.uiEnv.playwrightBrowsers') }}
      </div>
      <div class="browser-cards">
        <div v-for="browser in environmentData.playwright_browsers" :key="browser.name" class="browser-card">
          <div class="browser-content">
            <div class="browser-icon">
              <img :src="getBrowserIcon(browser.name)" :alt="browser.name" />
            </div>
            <div class="browser-info">
              <h3>{{ formatBrowserName(browser.name) }}</h3>
              <div class="status-row">
                <el-tag :type="browser.installed ? 'success' : 'warning'" effect="dark">
                  {{ browser.installed ? (browser.version || $t('configuration.uiEnv.installed')) : $t('configuration.uiEnv.notInstalled') }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const { t } = useI18n()

const checking = ref(false)
const lastCheckTime = ref('')
const environmentData = ref(null)

const getBrowserIcon = (name) => {
  const iconMap = {
    'chrome': 'https://raw.githubusercontent.com/alrra/browser-logos/main/src/chrome/chrome_48x48.png',
    'firefox': 'https://raw.githubusercontent.com/alrra/browser-logos/main/src/firefox/firefox_48x48.png',
    'safari': 'https://raw.githubusercontent.com/alrra/browser-logos/main/src/safari/safari_48x48.png',
    'edge': 'https://raw.githubusercontent.com/alrra/browser-logos/main/src/edge/edge_48x48.png',
    'chromium': 'https://raw.githubusercontent.com/alrra/browser-logos/main/src/chromium/chromium_48x48.png',
    'webkit': 'https://raw.githubusercontent.com/alrra/browser-logos/main/src/webkit/webkit_48x48.png'
  }
  return iconMap[name] || ''
}

const formatBrowserName = (name) => {
  return name.charAt(0).toUpperCase() + name.slice(1)
}

const checkEnvironment = async () => {
  checking.value = true
  try {
    const response = await api.get('/ui-automation/config/environment/check_environment/')
    environmentData.value = response.data
    lastCheckTime.value = new Date().toLocaleString()
    ElMessage.success(t('configuration.uiEnv.messages.checkSuccess'))
  } catch (error) {
    console.error('Environment check failed:', error)
    ElMessage.error(t('configuration.uiEnv.messages.checkFailed'))
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  checkEnvironment()
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
    margin-top: 32px;
    margin-bottom: 20px;

    &:first-child {
      margin-top: 0;
    }
  }
}

.os-check-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;

  .os-info {
    display: flex;
    align-items: baseline;
    gap: 12px;

    .os-label {
      font-size: 14px;
      color: #8c8c8c;
    }

    .os-name {
      font-size: 20px;
      font-weight: 600;
      color: #7b42f6;
    }
  }

  .check-action {
    display: flex;
    align-items: center;
    gap: 16px;

    .last-check {
      font-size: 12px;
      color: #8c8c8c;
    }
  }
}

.check-btn {
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

.browser-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.browser-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(147, 112, 219, 0.08);
  border: 1px solid rgba(147, 112, 219, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(147, 112, 219, 0.15);
  }
}

.browser-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.browser-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    width: 48px;
    height: 48px;
    object-fit: contain;
  }
}

.browser-info {
  width: 100%;
  text-align: center;

  h3 {
    margin: 0 0 10px;
    color: #262626;
    font-size: 16px;
    font-weight: 600;
  }
}

.status-row {
  display: flex;
  justify-content: center;
}
</style>
