<template>
  <div class="home-container">
    <!-- 顶部用户信息 -->
    <div class="header-bar">
      <div class="user-dropdown">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-info">
            <template v-if="!isLoggingOut">
              <el-avatar
                :size="40"
                :src="userAvatar"
                class="user-avatar"
              >
                {{ userInitials }}
              </el-avatar>
              <span class="username">{{ userName }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </template>
            <template v-else>
              <div class="logout-placeholder"></div>
            </template>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="user-dropdown-menu">
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="content-wrapper">
      <h1 class="main-title">{{ $t('home.title') }}</h1>
      <p class="subtitle">{{ $t('home.subtitle') }}</p>

      <div class="cards-container">
        <!-- AI智能用例 -->
        <div class="nav-card" @click="handleNavigate('ai')" role="button" tabindex="0">
          <div class="card-icon ai-icon">
            <el-icon><MagicStick /></el-icon>
          </div>
          <h3>{{ $t('home.aiCase') }}</h3>
          <p>{{ $t('home.aiCaseDesc') }}</p>
        </div>

        <!-- AI智能测试 -->
        <div class="nav-card" @click="handleNavigate('ai-intelligent')" role="button" tabindex="0">
          <div class="card-icon ai-intelligent-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <h3>{{ $t('home.aiIntelligent') }}</h3>
          <p>{{ $t('home.aiIntelligentDesc') }}</p>
        </div>

        <!-- 数据工具箱 -->
        <div class="nav-card" @click="handleNavigate('data')" role="button" tabindex="0">
          <div class="card-icon data-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <h3>{{ $t('home.dataFactory') }}</h3>
          <p>{{ $t('home.dataFactoryDesc') }}</p>
        </div>

        <!-- 配置中心 -->
        <div class="nav-card" @click="handleNavigate('config')" role="button" tabindex="0">
          <div class="card-icon config-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <h3>{{ $t('home.configCenter') }}</h3>
          <p>{{ $t('home.configCenterDesc') }}</p>
        </div>

        <!-- AI知识库 -->
        <div class="nav-card" @click="handleNavigate('assistant')" role="button" tabindex="0">
          <div class="card-icon assistant-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3>{{ $t('home.aiKnowledgeBase') }}</h3>
          <p>{{ $t('home.aiKnowledgeBaseDesc') }}</p>
        </div>

        <!-- Web自动化 -->
        <div class="nav-card" @click="handleNavigate('ui')" role="button" tabindex="0">
          <div class="card-icon ui-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <h3>Web自动化</h3>
          <p>可视化的Web UI自动化测试</p>
        </div>

        <!-- APP自动化 -->
        <div class="nav-card" @click="handleNavigate('app')" role="button" tabindex="0">
          <div class="card-icon app-icon">
            <el-icon><Cellphone /></el-icon>
          </div>
          <h3>APP自动化</h3>
          <p>可视化的Android App自动化测试</p>
        </div>

        <!-- 接口测试 -->
        <div class="nav-card" @click="handleNavigate('api')" role="button" tabindex="0">
          <div class="card-icon api-icon">
            <el-icon><Link /></el-icon>
          </div>
          <h3>{{ $t('home.apiTesting') }}</h3>
          <p>{{ $t('home.apiTestingDesc') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Link, Monitor, DataLine, Cpu, Setting, ChatDotRound, Cellphone, ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const { t } = useI18n()
const appStore = useAppStore()
const userStore = useUserStore()

// 退出登录中标志，用于隐藏头像避免闪烁默认图
const isLoggingOut = ref(false)

// 用户信息
const userName = computed(() => {
  return userStore.user?.username || userStore.user?.first_name || '用户'
})

const userAvatar = computed(() => {
  // 退出登录过程中不显示头像
  if (isLoggingOut.value) {
    return ''
  }
  return userStore.user?.avatar || ''
})

const userInitials = computed(() => {
  const name = userStore.user?.username || userStore.user?.first_name || 'U'
  return name.charAt(0).toUpperCase()
})

// 下拉菜单命令处理
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      // 可以跳转到个人中心页面
      ElMessage.info('个人中心功能开发中')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录
const handleLogout = async () => {
  // 设置退出登录标志，避免头像闪烁默认图
  isLoggingOut.value = true
  await userStore.logout()
}

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
  flex-direction: column;
  padding: 20px 40px 40px;
  position: relative;
}

// 顶部栏
.header-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
}

// 用户下拉菜单
.user-dropdown {
  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 12px;
    border-radius: 24px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }

    .user-avatar {
      border: 2px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .username {
      font-size: 14px;
      font-weight: 500;
      color: #374151;
      transition: color 0.3s ease;
    }

    .dropdown-arrow {
      font-size: 12px;
      color: #6b7280;
      transition: transform 0.3s ease, color 0.3s ease;
    }

    .logout-placeholder {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(123, 66, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
    }

    &:hover {
      .username {
        color: #111827;
      }
      .dropdown-arrow {
        color: #4b5563;
        transform: rotate(180deg);
      }
    }
  }
}

// 下拉菜单样式
:deep(.user-dropdown-menu) {
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);

  // 覆盖所有子元素的默认蓝色
  * {
    color: inherit !important;
  }

  .el-dropdown-menu__item {
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s ease;
    color: #374151 !important;

    &.el-dropdown-menu__item--active,
    &:focus,
    &:hover,
    &:active {
      background: rgba(139, 92, 246, 0.1) !important;
      color: #7c3aed !important;
    }

    // 覆盖所有可能的颜色状态
    &:not(.is-disabled) {
      color: #374151 !important;
    }

    &:not(.is-disabled):hover,
    &:not(.is-disabled):focus,
    &:not(.is-disabled):active,
    &:not(.is-disabled).el-dropdown-menu__item--active {
      background: rgba(139, 92, 246, 0.1) !important;
      color: #7c3aed !important;
    }

    .el-icon {
      font-size: 16px;
      color: #6b7280 !important;
      transition: color 0.2s ease;
    }

    &:hover .el-icon,
    &:focus .el-icon,
    &:active .el-icon,
    &.el-dropdown-menu__item--active .el-icon {
      color: #7c3aed !important;
    }

    &.is-disabled {
      color: #9ca3af !important;
    }

    // 强制覆盖链接样式
    a,
    a:link,
    a:visited,
    a:hover,
    a:active {
      color: inherit !important;
      text-decoration: none !important;
    }

    // 覆盖 span 标签
    span {
      color: inherit !important;
    }
  }

  .el-dropdown-menu__item--divided {
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    margin: 6px 0;
    padding-top: 6px;
  }
}

// 额外的全局覆盖，确保完全覆盖
:deep(.el-dropdown-menu__item) {
  &:not(.is-disabled) {
    color: #374151 !important;
  }
  
  &:hover,
  &:focus,
  &:active,
  &.el-dropdown-menu__item--active {
    color: #7c3aed !important;
    background: rgba(139, 92, 246, 0.1) !important;
  }
}

.content-wrapper {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.main-title {
  font-size: 52px;
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
  .home-container {
    padding: 16px 20px 40px;
  }

  .header-bar {
    padding: 0;
    margin-bottom: 16px;
  }

  .user-dropdown .user-info {
    padding: 4px 10px;
    gap: 6px;

    .username {
      font-size: 13px;
    }
  }

  .cards-container {
    grid-template-columns: 1fr;
    padding: 0;
  }

  .main-title {
    font-size: 36px;
  }
}
</style>
