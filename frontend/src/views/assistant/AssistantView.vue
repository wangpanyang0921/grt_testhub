<template>
  <div class="assistant-layout">
    <!-- 左侧侧边栏 -->
    <div class="sidebar">
      <div class="new-chat-btn-wrapper">
        <el-button type="primary" class="new-chat-btn" @click="startNewChat" :icon="Plus">
          {{ $t('assistant.newChat') }}
        </el-button>
      </div>
      
      <div class="history-list">
        <div class="history-label">{{ $t('assistant.historyChat') }}</div>
        <div class="session-scroll-area">
          <div 
            v-for="session in historySessionsDescending" 
            :key="session.id"
            :class="['session-item', { active: currentSession?.id === session.id }]"
            @click="switchToSession(session)"
          >
            <div class="session-title-wrapper">
              <el-icon class="chat-icon"><ChatDotRound /></el-icon>
              <span class="session-title" :title="session.title">{{ session.title || $t('assistant.newChat') }}</span>
            </div>
            <div class="session-actions" @click.stop>
              <el-icon class="delete-icon" @click.stop="handleDeleteSession(session.id)"><Delete /></el-icon>
            </div>
          </div>
        </div>
      </div>
      
      <div class="user-profile">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" :src="userStore.user?.avatar || ''" :icon="UserFilled" />
            <span class="username">{{ userStore.user?.username || $t('assistant.user') }}</span>
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="home">{{ $t('assistant.goHome') }}</el-dropdown-item>
              <el-dropdown-item command="logout" divided>{{ $t('assistant.logout') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 右侧主内容区 -->
    <div class="main-content">
      <!-- 场景1：新会话（居中输入框） -->
      <div v-if="isNewChatMode" class="welcome-screen">
        <div class="welcome-content">
          <div class="logo-area">
            <div class="logo-circle">
              <el-icon><Cpu /></el-icon>
            </div>
            <h1>{{ $t('assistant.title') }}</h1>
            <p>{{ $t('assistant.subtitle') }}</p>
          </div>
          
          <div class="center-input-wrapper">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              :placeholder="$t('assistant.inputPlaceholder')"
              class="center-input"
              resize="none"
              @keydown.enter.exact.prevent="handleEnter"
            />
            <div class="input-actions">
              <el-button 
                type="primary" 
                circle 
                :icon="Promotion" 
                :disabled="!inputMessage.trim()"
                @click="sendMessage"
              />
            </div>
          </div>
          
          <div class="suggestion-chips">
            <div class="chip" @click="useSuggestion($t('assistant.suggestions.apiTestQuestion'))">{{ $t('assistant.suggestions.apiTest') }}</div>
            <div class="chip" @click="useSuggestion($t('assistant.suggestions.performancePlanQuestion'))">{{ $t('assistant.suggestions.performancePlan') }}</div>
            <div class="chip" @click="useSuggestion($t('assistant.suggestions.testTheoryQuestion'))">{{ $t('assistant.suggestions.testTheory') }}</div>
            <div class="chip" @click="useSuggestion($t('assistant.suggestions.automationDebugQuestion'))">{{ $t('assistant.suggestions.automationDebug') }}</div>
          </div>
        </div>
      </div>

      <!-- 场景2：对话界面 -->
      <div v-else class="chat-screen">
        <div class="chat-header">
          <span class="chat-title">{{ currentSession?.title || $t('assistant.newChat') }}</span>
          <span class="chat-time" v-if="currentSession">{{ formatDate(currentSession.updated_at) }}</span>
        </div>
        
        <div class="messages-container" ref="messagesContainer">
          <div 
            v-for="(message, index) in messages" 
            :key="message.id || index"
            :class="['message-row', message.role]"
          >
            <div class="avatar">
              <el-avatar v-if="message.role === 'user'" :size="36" :src="userStore.user?.avatar || ''" :icon="User" class="user-avatar" />
              <el-avatar v-else :size="36" :icon="Cpu" class="ai-avatar" />
            </div>
            <div class="message-bubble">
              <div class="message-content" v-html="formatMessageContent(message.content)"></div>
              <div class="message-status" v-if="message.isPending">
                <el-icon class="is-loading"><Loading /></el-icon> {{ $t('assistant.thinking') }}
              </div>
            </div>
          </div>
          
          <!-- 底部占位，确保滚动到底部 -->
          <div style="height: 20px;"></div>
        </div>

        <div class="chat-footer">
          <div class="input-box">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="1"
              :autosize="{ minRows: 1, maxRows: 5 }"
              :placeholder="$t('assistant.chatInputPlaceholder')"
              resize="none"
              @keydown.enter.exact.prevent="handleEnter"
            />
            <el-button 
              type="primary" 
              class="send-btn"
              :disabled="!inputMessage.trim() || sending"
              @click="sendMessage"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, ChatDotRound, User, Cpu, Promotion, Loading, UserFilled, ArrowDown } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const userStore = useUserStore()
const { t, locale } = useI18n()

// 状态
const historySessions = ref([])
const currentSession = ref(null)
const messages = ref([])
const inputMessage = ref('')
const sending = ref(false)
const messagesContainer = ref(null)

const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'home') {
    router.push('/home')
  }
}

const handleLogout = () => {
  ElMessageBox.confirm(t('assistant.logoutConfirm'), t('assistant.logoutTitle'), {
    confirmButtonText: t('assistant.confirm'),
    cancelButtonText: t('assistant.cancel'),
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
    ElMessage.success(t('assistant.loggedOut'))
  }).catch(() => {})
}

// 计算属性
const historySessionsDescending = computed(() => {
  return [...historySessions.value].sort((a, b) => 
    new Date(b.updated_at) - new Date(a.updated_at)
  )
})

const isNewChatMode = computed(() => {
  // 如果没有当前会话，或者当前会话没有消息且没有ID（临时会话），则显示新会话模式
  return !currentSession.value || (!currentSession.value.id && messages.value.length === 0)
})

// 方法
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const localeCode = locale.value === 'zh-cn' ? 'zh-CN' : 'en-US'
  // 如果是今天，只显示时间
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString(localeCode, { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString(localeCode, { month: '2-digit', day: '2-digit' })
}

const formatMessageContent = (content) => {
  if (!content) return ''
  // 简单的 markdown 处理，实际项目中建议使用 markdown-it
  return content
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 开启新会话
const startNewChat = () => {
  currentSession.value = { title: t('assistant.newChat') } // 临时会话对象
  messages.value = []
  inputMessage.value = ''
}

// 切换会话
const switchToSession = async (session) => {
  if (currentSession.value?.id === session.id) return
  
  try {
    currentSession.value = { ...session }
    const response = await api.get(`/assistant/sessions/${session.id}/messages/`)
    messages.value = response.data
    scrollToBottom()
  } catch (error) {
    console.error('Load messages failed:', error)
    ElMessage.error(t('assistant.messages.loadMessageFailed'))
  }
}

// 删除会话
const handleDeleteSession = (sessionId) => {
  ElMessageBox.confirm(t('assistant.deleteSessionConfirm'), t('common.tips'), {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }).then(() => {
    deleteSession(sessionId)
  }).catch(() => {
    // 用户取消删除
  })
}

const deleteSession = async (sessionId) => {
  try {
    await api.delete(`/assistant/sessions/${sessionId}/`)
    historySessions.value = historySessions.value.filter(s => s.id !== sessionId)

    if (currentSession.value?.id === sessionId) {
      startNewChat()
    }
    ElMessage.success(t('assistant.messages.sessionDeleted'))
  } catch (error) {
    console.error('Delete session failed:', error)
    ElMessage.error(t('assistant.messages.deleteSessionFailed'))
  }
}

// 使用建议
const useSuggestion = (text) => {
  inputMessage.value = text
  sendMessage()
}

// 处理回车发送
const handleEnter = (e) => {
  if (!e.shiftKey && !sending.value) {
    sendMessage()
  }
}

// 发送消息
const sendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text || sending.value) return
  
  inputMessage.value = ''
  sending.value = true
  
  // 1. 立即上屏用户消息
  const tempUserMsg = {
    role: 'user',
    content: text,
    created_at: new Date().toISOString()
  }
  messages.value.push(tempUserMsg)
  
  // 2. 添加一个临时的"思考中"消息
  const tempAiMsg = {
    role: 'assistant',
    content: '',
    isPending: true
  }
  messages.value.push(tempAiMsg)
  scrollToBottom()
  
  try {
    // 如果是新会话（没有ID），先创建会话
    let sessionId = currentSession.value?.id
    let isFirstMessage = false
    
    if (!sessionId) {
      isFirstMessage = true
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`
      // 智能生成标题（取前10个字）
      const title = text.length > 10 ? text.substring(0, 10) + '...' : text
      
      const sessionRes = await api.post('/assistant/sessions/', {
        session_id: newSessionId,
        title: title
      })
      
      currentSession.value = sessionRes.data
      sessionId = currentSession.value.session_id // 注意：后端返回的是对象，这里需要用 session_id 字段
      
      // 立即添加到历史列表
      historySessions.value.unshift(currentSession.value)
    } else {
      // 如果是已有会话，使用 session_id 字段
      sessionId = currentSession.value.session_id
    }
    
    // 3. 发送请求
    const response = await api.post('/assistant/chat/send_message/', {
      session_id: sessionId,
      message: text
    }, {
      timeout: 60000
    })
    
    // 4. 替换临时消息为真实消息
    messages.value.pop() // 移除思考中
    messages.value.pop() // 移除临时用户消息（因为后端返回了完整的用户消息对象）
    
    messages.value.push(response.data.user_message)
    messages.value.push(response.data.assistant_message)
    
    // 更新会话的 conversation_id
    if (response.data.conversation_id && currentSession.value) {
      currentSession.value.conversation_id = response.data.conversation_id
    }
    
    // 如果是第一次对话，更新历史列表中的会话信息（比如 updated_at）
    if (!isFirstMessage) {
      const index = historySessions.value.findIndex(s => s.id === currentSession.value.id)
      if (index !== -1) {
        historySessions.value[index] = { ...currentSession.value, updated_at: new Date().toISOString() }
        // 重新排序（移到最前）
        const updatedSession = historySessions.value.splice(index, 1)[0]
        historySessions.value.unshift(updatedSession)
      }
    }
    
  } catch (error) {
    console.error('Send failed:', error)
    // 移除临时消息，显示错误
    messages.value.pop() // 移除思考中
    ElMessage.error(error.response?.data?.error || t('assistant.messages.sendFailed'))
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

// 加载历史
const loadHistory = async () => {
  try {
    const response = await api.get('/assistant/sessions/')
    historySessions.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Load history failed:', error)
  }
}

onMounted(async () => {
  console.log('开始初始化用户信息...')
  await userStore.initAuth()
  console.log('用户信息初始化完成:', userStore.user)
  console.log('用户头像:', userStore.user?.avatar)
  loadHistory()
  startNewChat()
})
</script>

<style scoped lang="scss">
.assistant-layout {
  display: flex;
  height: 100vh;
  background: #fff;
  overflow: hidden;
}

/* 左侧侧边栏 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #f8f5ff 0%, #f0ebfa 50%, #e8e3f5 100%);
  border-right: 1px solid rgba(123, 66, 246, 0.12);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  color: #5a32a3;
  box-shadow: 4px 0 16px rgba(123, 66, 246, 0.08);

  .new-chat-btn-wrapper {
    padding: 20px;

    .new-chat-btn {
        width: 100%;
        height: 42px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 500;
        background: linear-gradient(135deg, #7b42f6 0%, #9f7aea 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.3);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(123, 66, 246, 0.4);
        }

        &:active {
          transform: translateY(0);
        }
      }
  }
  
  .history-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    
    .history-label {
      padding: 0 20px 10px;
      font-size: 12px;
      color: rgba(90, 50, 163, 0.6);
    }
    
    .session-scroll-area {
      flex: 1;
      overflow-y: auto;
      padding: 0 10px;
      
      &::-webkit-scrollbar {
        width: 4px;
      }
      &::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
      }
    }
    
    .session-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      margin: 6px 12px;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s ease;
      color: #5a32a3;
      background: rgba(255, 255, 255, 0.7);
      box-shadow: 0 2px 8px rgba(123, 66, 246, 0.06);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(123, 66, 246, 0.08);

      &:hover {
        background: rgba(255, 255, 255, 0.95);
        color: #7b42f6;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(123, 66, 246, 0.12);
        transform: translateX(4px);

        .session-actions {
          opacity: 1;
        }
      }

      &.active {
        background: linear-gradient(135deg, #7b42f6 0%, #9f7aea 100%);
        color: white;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(123, 66, 246, 0.35);
        border-color: transparent;
      }
      
      .session-title-wrapper {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        overflow: hidden;
        
        .chat-icon {
          font-size: 16px;
        }
        
        .session-title {
          font-size: 14px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }
      
      .session-actions {
        opacity: 0;
        transition: opacity 0.2s;
        
        .delete-icon {
          font-size: 14px;
          color: rgba(90, 50, 163, 0.6);
          &:hover {
            color: #ff4d4f;
          }
        }
      }
    }
  }
  
  .user-profile {
    padding: 12px 16px;
    border-top: 1px solid rgba(123, 66, 246, 0.1);
    margin-top: auto;

    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 12px;
      transition: all 0.3s ease;
      background: rgba(255, 255, 255, 0.5);

      &:hover {
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 8px rgba(123, 66, 246, 0.1);
      }

      .username {
        margin: 0 8px;
        font-size: 14px;
        color: #5a32a3;
        font-weight: 500;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .el-icon {
        color: #9f7aea;
      }
    }
  }
}

/* 右侧主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 50%, #f0edff 100%);
}

/* 场景1：欢迎页（新会话） */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 100px;
  
  .welcome-content {
    width: 100%;
    max-width: 800px;
    padding: 0 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .logo-area {
    text-align: center;
    margin-bottom: 40px;

    .logo-circle {
      width: 88px;
      height: 88px;
      background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 24px;
      box-shadow: 0 8px 32px rgba(123, 66, 246, 0.25);
      border: 3px solid rgba(255, 255, 255, 0.5);

      .el-icon {
        font-size: 44px;
        color: #7b42f6;
      }
    }

    h1 {
      font-size: 32px;
      color: #5a32a3;
      margin: 0 0 12px;
      font-weight: 700;
      letter-spacing: 1px;
    }

    p {
      color: #7c6f9c;
      font-size: 16px;
      margin: 0;
      font-weight: 400;
    }
  }
  
  .center-input-wrapper {
    width: 100%;
    position: relative;
    margin-bottom: 30px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 20px;
    padding: 8px;
    box-shadow: 0 4px 20px rgba(123, 66, 246, 0.1);
    border: 1px solid rgba(123, 66, 246, 0.1);
    transition: all 0.3s ease;

    &:focus-within {
      box-shadow: 0 4px 24px rgba(123, 66, 246, 0.18);
      border-color: rgba(123, 66, 246, 0.2);
      background: #fff;
    }

    .center-input {
      :deep(.el-textarea__inner) {
        border-radius: 12px;
        padding: 16px 50px 16px 16px;
        font-size: 16px;
        border: none !important;
        background: transparent;
        box-shadow: none !important;
        outline: none !important;

        &:focus {
          box-shadow: none !important;
          border: none !important;
          outline: none !important;
        }
      }
    }

    .input-actions {
      position: absolute;
      right: 16px;
      bottom: 16px;

      .el-button {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #7b42f6 0%, #9f7aea 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(123, 66, 246, 0.35);
        transition: all 0.3s ease;
        border-radius: 12px;

        &:hover {
          background: linear-gradient(135deg, #6d33e6 0%, #8b5cf6 100%);
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(123, 66, 246, 0.45);
        }

        &:active {
          transform: translateY(0);
        }

        &.is-disabled {
          background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
          box-shadow: none;
        }

        .el-icon {
          font-size: 20px;
          color: white;
        }
      }
    }
  }
  
  .suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;

    .chip {
      padding: 10px 20px;
      background: rgba(255, 255, 255, 0.8);
      border-radius: 24px;
      font-size: 14px;
      color: #6b5b8a;
      cursor: pointer;
      transition: all 0.3s ease;
      border: 1px solid rgba(123, 66, 246, 0.1);
      box-shadow: 0 2px 8px rgba(123, 66, 246, 0.06);
      font-weight: 500;

      &:hover {
        background: linear-gradient(135deg, #7b42f6 0%, #9f7aea 100%);
        color: #fff;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(123, 66, 246, 0.25);
        border-color: transparent;
      }
    }
  }
}

/* 场景2：对话页 */
.chat-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .chat-header {
    height: 64px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.15);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    flex-shrink: 0;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 12px rgba(147, 112, 219, 0.08);

    .chat-title {
      font-size: 17px;
      font-weight: 600;
      color: #5a32a3;
      letter-spacing: 0.5px;
    }

    .chat-time {
      font-size: 12px;
      color: #9370db;
      background: rgba(147, 112, 219, 0.1);
      padding: 4px 10px;
      border-radius: 12px;
      border: 1px solid rgba(147, 112, 219, 0.15);
    }
  }
  
  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);

    .message-row {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      align-items: flex-start;

      &.user {
        flex-direction: row-reverse;

        .message-bubble {
          background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
          color: #fff;
          border-radius: 16px 16px 4px 16px;
          box-shadow: 0 4px 12px rgba(123, 66, 246, 0.25);

          :deep(pre) {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
          }

          :deep(code) {
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
          }

          :deep(p) {
            color: #fff;
          }
        }
      }

      &.assistant {
        .message-bubble {
          background: #fff;
          color: #303133;
          border-radius: 16px 16px 16px 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid rgba(147, 112, 219, 0.1);
        }
      }

      .avatar {
        flex-shrink: 0;
        margin-top: 4px;

        .user-avatar {
          background: linear-gradient(135deg, #c0c4cc 0%, #a8abb2 100%);
          border: 2px solid #fff;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .ai-avatar {
          background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
          color: #5a6c7d;
          border-radius: 10px;
          border: 2px solid #fff;
          box-shadow: 0 2px 8px rgba(252, 182, 159, 0.3);
        }
      }

      .message-bubble {
        max-width: 75%;
        padding: 14px 18px;
        font-size: 14px;
        line-height: 1.7;
        position: relative;
        transition: all 0.3s ease;
        
        .message-content {
          word-wrap: break-word;
          
          :deep(p) {
            margin: 0 0 8px 0;
            &:last-child { margin: 0; }
          }
          
          :deep(pre) {
            background: #282c34;
            color: #abb2bf;
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 8px 0;
          }
          
          :deep(code) {
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
          }
        }
        
        .message-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: #909399;
          
          .is-loading {
            animation: rotating 2s linear infinite;
          }
        }
      }
    }
  }
  
  .chat-footer {
    padding: 20px 28px;
    border-top: 1px solid rgba(147, 112, 219, 0.15);
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    box-shadow: 0 -2px 12px rgba(147, 112, 219, 0.06);

    .input-box {
      position: relative;
      border: 1px solid rgba(147, 112, 219, 0.25);
      border-radius: 16px;
      padding: 10px;
      background: rgba(255, 255, 255, 0.9);
      transition: all 0.3s;
      box-shadow: 0 2px 12px rgba(147, 112, 219, 0.1);

      &:focus-within {
        border-color: #7b42f6;
        box-shadow: 0 0 0 3px rgba(123, 66, 246, 0.15), 0 4px 16px rgba(123, 66, 246, 0.15);
        background: #fff;
      }

      :deep(.el-textarea__inner) {
        border: none !important;
        box-shadow: none !important;
        padding: 8px 50px 8px 8px;
        background: transparent;
        outline: none !important;
      }

      .send-btn {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        width: 32px;
        height: 32px;
        padding: 0;
        border-radius: 8px;
        background: linear-gradient(135deg, #7b42f6 0%, #5a32a3 100%);
        border: none;
        box-shadow: 0 2px 8px rgba(123, 66, 246, 0.3);
        transition: all 0.3s ease;

        &:hover {
          background: linear-gradient(135deg, #6d33e6 0%, #4a249c 100%);
          box-shadow: 0 4px 12px rgba(123, 66, 246, 0.4);
        }

        &:active {
          transform: translateY(-50%) scale(0.95);
        }

        &.is-disabled {
          background: linear-gradient(135deg, #c0c4cc 0%, #a8abb2 100%);
          box-shadow: none;
        }

        .el-icon {
          color: white;
          font-size: 14px;
        }
      }
    }
    
    .footer-tip {
      text-align: center;
      font-size: 12px;
      color: #c0c4cc;
      margin-top: 8px;
    }
  }
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>