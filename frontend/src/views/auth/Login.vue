<template>
  <div class="login-container">
    <!-- 背景装饰元素 - 浮动小球在整个页面 -->
    <div class="floating-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
      <div class="shape shape-5"></div>
      <div class="shape shape-6"></div>
    </div>

    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 顶部 Logo -->
      <div class="brand-header">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <img src="@/assets/images/grt.png" alt="TestHub Logo" class="logo-image" />
          </div>
          <h1 class="brand-title">国人通 TestHub</h1>
        </div>
      </div>

      <!-- 登录表单卡片 -->
      <div class="login-card">
        <div class="form-header">
          <h2>{{ $t('auth.welcomeBack') }}</h2>
          <p>{{ $t('auth.loginSubtitle') }}</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              :placeholder="$t('auth.usernamePlaceholder')"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              :placeholder="$t('auth.passwordPlaceholder')"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              class="login-button"
            >
              <span v-if="!loading">{{ $t('auth.login') }}</span>
              <span v-else>{{ $t('auth.loggingIn') }}</span>
            </el-button>
          </el-form-item>

          <div class="form-footer">
            <router-link to="/register" class="register-link">
              {{ $t('auth.noAccount') }}<span>{{ $t('auth.signUpNow') }}</span>
            </router-link>
          </div>
        </el-form>
      </div>

      <!-- 底部信息 -->
      <div class="bottom-info">
        <p>人真正的动力 源于内心深处 对于快乐和兴趣的追求</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: computed(() => t('auth.usernameRequired')), trigger: 'blur' }
  ],
  password: [
    { required: true, message: computed(() => t('auth.passwordRequired')), trigger: 'blur' },
    { min: 6, message: computed(() => t('auth.passwordLength')), trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        console.log('Starting login...')
        const result = await userStore.login(form)
        console.log('Login result:', result)
        console.log('User store state:', {
          token: userStore.token,
          user: userStore.user,
          isAuthenticated: userStore.isAuthenticated
        })

        ElMessage.success(t('auth.loginSuccess'))
        console.log('Preparing to redirect to /home')

        // Use replace instead of push to prevent returning to login page
        await router.replace('/home')
        console.log('Redirect completed')

      } catch (error) {
        console.error('Login failed:', error)
        ElMessage.error(error.response?.data?.error || t('auth.loginFailed'))
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
  position: relative;
  overflow: hidden;
}

/* 浮动装饰元素 - 在整个页面悬浮 */
.floating-shapes {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
  pointer-events: none;

  .shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 20s infinite ease-in-out;

    &.shape-1 {
      width: 300px;
      height: 300px;
      top: -100px;
      left: -100px;
      animation-delay: 0s;
    }

    &.shape-2 {
      width: 200px;
      height: 200px;
      bottom: -50px;
      right: -50px;
      animation-delay: 5s;
    }

    &.shape-3 {
      width: 150px;
      height: 150px;
      top: 40%;
      right: 10%;
      animation-delay: 10s;
    }

    &.shape-4 {
      width: 100px;
      height: 100px;
      bottom: 30%;
      left: 20%;
      animation-delay: 15s;
    }

    &.shape-5 {
      width: 180px;
      height: 180px;
      top: 20%;
      left: 60%;
      animation-delay: 7s;
    }

    &.shape-6 {
      width: 120px;
      height: 120px;
      bottom: 20%;
      right: 30%;
      animation-delay: 12s;
    }
  }
}

/* 页面内容 */
.page-content {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  min-height: 100vh;
}

/* 顶部 Logo */
.brand-header {
  margin-bottom: 40px;
  animation: fadeInDown 0.8s ease-out;

  .logo-wrapper {
    display: flex;
    align-items: center;
    gap: 16px;

    .logo-icon {
      width: 56px;
      height: 56px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      backdrop-filter: blur(10px);
      overflow: hidden;

      .logo-image {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 4px;
      }
    }

    .brand-title {
      font-size: 32px;
      font-weight: 700;
      margin: 0;
      color: white;
      letter-spacing: -1px;
    }
  }
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: fadeInUp 0.8s ease-out;
  animation-delay: 0.2s;
  animation-fill-mode: both;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;

  h2 {
    font-size: 28px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 16px 0;
  }

  p {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
  }
}

.login-form {
  :deep(.el-input__wrapper) {
    padding: 8px 16px;
    box-shadow: 0 0 0 1px #e5e7eb inset;
    transition: all 0.3s ease;
    border-radius: 12px;

    &:hover {
      box-shadow: 0 0 0 1px #8b5cf6 inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 1px #8b5cf6 inset;
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  .login-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    border: none;
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

.form-footer {
  text-align: center;
  margin-top: 24px;

  .register-link {
    color: #6b7280;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.3s ease;

    span {
      color: #8b5cf6;
      font-weight: 600;
    }

    &:hover {
      color: #8b5cf6;

      span {
        text-decoration: underline;
      }
    }
  }
}

/* 底部信息 */
.bottom-info {
  margin-top: 40px;
  text-align: center;
  animation: fadeIn 1s ease-out;
  animation-delay: 0.4s;
  animation-fill-mode: both;

  p {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.85);
    margin: 0;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    letter-spacing: 1px;
  }
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(30px, -30px) rotate(90deg);
  }
  50% {
    transform: translate(-20px, 20px) rotate(180deg);
  }
  75% {
    transform: translate(20px, 10px) rotate(270deg);
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .page-content {
    padding: 24px 16px;
  }

  .brand-header {
    margin-bottom: 32px;

    .logo-wrapper {
      .logo-icon {
        width: 48px;
        height: 48px;
      }

      .brand-title {
        font-size: 24px;
      }
    }
  }

  .login-card {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .form-header {
    h2 {
      font-size: 24px;
    }
  }
}
</style>
