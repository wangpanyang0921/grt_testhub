<template>
  <div class="home-container">
    <div class="content-wrapper">

      <h1 class="main-title">{{ $t('home.title') }}</h1>
      <p class="subtitle">{{ $t('home.subtitle') }}</p>

      <div class="cards-container">
        <!-- AI用例 -->
        <div class="nav-card" @click="handleNavigate('ai')" role="button" tabindex="0">
          <div class="card-icon ai-icon">
            <el-icon><MagicStick /></el-icon>
          </div>
          <h3>{{ $t('home.aiCase') }}</h3>
          <p>{{ $t('home.aiCaseDesc') }}</p>
        </div>

        <!-- AI智能 -->
        <div class="nav-card" @click="handleNavigate('ai-intelligent')" role="button" tabindex="0">
          <div class="card-icon ai-intelligent-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <h3>{{ $t('home.aiIntelligent') }}</h3>
          <p>{{ $t('home.aiIntelligentDesc') }}</p>
        </div>

        <!-- Web自动化 -->
        <div class="nav-card" @click="handleNavigate('ui')" role="button" tabindex="0">
          <div class="card-icon ui-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <h3>Web自动化</h3>
          <p>可视化的Web UI自动化测试</p>
        </div>

        <!-- 数据工厂 -->
        <div class="nav-card" @click="handleNavigate('data')" role="button" tabindex="0">
          <div class="card-icon data-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <h3>{{ $t('home.dataFactory') }}</h3>
          <p>{{ $t('home.dataFactoryDesc') }}</p>
        </div>

        <!-- AI知识库 -->
        <div class="nav-card" @click="handleNavigate('assistant')" role="button" tabindex="0">
          <div class="card-icon assistant-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3>{{ $t('home.aiKnowledgeBase') }}</h3>
          <p>{{ $t('home.aiKnowledgeBaseDesc') }}</p>
        </div>

        <!-- 接口测试 -->
        <div class="nav-card" @click="handleNavigate('api')" role="button" tabindex="0">
          <div class="card-icon api-icon">
            <el-icon><Link /></el-icon>
          </div>
          <h3>{{ $t('home.apiTesting') }}</h3>
          <p>{{ $t('home.apiTestingDesc') }}</p>
        </div>

        <!-- APP自动化 -->
        <div class="nav-card" @click="handleNavigate('app')" role="button" tabindex="0">
          <div class="card-icon app-icon">
            <el-icon><Cellphone /></el-icon>
          </div>
          <h3>APP自动化</h3>
          <p>可视化的Android App自动化测试</p>
        </div>

        <!-- 配置中心 -->
        <div class="nav-card" @click="handleNavigate('config')" role="button" tabindex="0">
          <div class="card-icon config-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <h3>{{ $t('home.configCenter') }}</h3>
          <p>{{ $t('home.configCenterDesc') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Link, Monitor, DataLine, Cpu, Setting, ChatDotRound, UserFilled, ArrowDown, Cellphone } from '@element-plus/icons-vue'

const router = useRouter()
const { t } = useI18n()
const appStore = useAppStore()

const handleNavigate = (type) => {
  const routes = {
    'ai': '/ai-generation/requirement-analysis',
    'api': '/api-testing/dashboard',
    'ui': '/ui-automation/dashboard',
    'app': '/app-automation/dashboard',
    'ai-intelligent': '/ai-intelligent-mode/testing',
    'assistant': '/ai-generation/assistant',
    'config': '/configuration/ai-model',
    'data': '/data-factory'
  }

  if (routes[type]) {
    const routeData = router.resolve({ path: routes[type] })
    window.open(routeData.href, '_blank')
  }
}
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.content-wrapper {
  max-width: 1400px;
  width: 100%;
  text-align: center;
}

.main-title {
  font-size: 42px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 16px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 18px;
  color: #5a6c7d;
  margin-bottom: 50px;
  font-weight: 400;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 0 20px;
}

.nav-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 32px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 1);
  }

  &:active {
    transform: translateY(-4px);
  }

  .card-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
    font-size: 28px;
    transition: all 0.3s ease;

    &.ai-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    &.api-icon {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
    }

    &.ui-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: white;
    }

    &.data-icon {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      color: white;
    }

    &.app-icon {
      background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      color: white;
    }

    &.ai-intelligent-icon {
      background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
      color: #5a6c7d;
    }

    &.assistant-icon {
      background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
      color: #5a6c7d;
    }

    &.config-icon {
      background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
      color: #5a6c7d;
    }
  }

  &:hover .card-icon {
    transform: scale(1.1);
  }

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 10px;
  }

  p {
    font-size: 14px;
    color: #5a6c7d;
    line-height: 1.5;
    margin: 0;
  }
}

@media (max-width: 1200px) {
  .cards-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .cards-container {
    grid-template-columns: 1fr;
  }

  .main-title {
    font-size: 32px;
  }
}
</style>
