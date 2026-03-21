<template>
  <div class="assistant-container">
    <!-- 内部左侧侧边栏 - 会话列表 -->
    <div class="session-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-title">历史会话</div>
        <el-button type="primary" class="new-chat-btn" @click="startNewChat" :icon="Plus" circle size="small" />
      </div>

      <div class="history-list">
        <div class="history-label" style="display: none;">{{ $t('assistant.historyChat') }}</div>
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
              <span class="delete-text" @click.stop="handleDeleteSession(session.id)">删除</span>
            </div>
          </div>
        </div>
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

          <div class="suggestion-chips" v-if="false">
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
          <div class="chat-header-left">
            <el-icon class="back-icon" @click="startNewChat"><ArrowLeft /></el-icon>
            <span class="chat-title">{{ currentSession?.title || $t('assistant.newChat') }}</span>
          </div>
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
              <div class="message-actions" v-if="message.role === 'assistant' && !message.isPending">
                <el-button type="primary" link size="small" @click="copyMessage(message.content)">
                  <el-icon><CopyDocument /></el-icon> 复制
                </el-button>
                <el-button type="primary" link size="small" @click="editMessage(message)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
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
import { Plus, Delete, ChatDotRound, User, Cpu, Promotion, Loading, ArrowLeft, CopyDocument, Edit } from '@element-plus/icons-vue'
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

// 计算属性
const historySessionsDescending = computed(() => {
  return [...historySessions.value].sort((a, b) =>
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
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

// 复制消息内容
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('复制成功')
  } catch (error) {
    console.error('Copy failed:', error)
    ElMessage.error('复制失败')
  }
}

// 编辑消息
const editMessage = (message) => {
  inputMessage.value = message.content
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
.assistant-container {
  display: flex;
  height: 100%;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  overflow: hidden;
  padding: 24px;
  gap: 20px;
}

/* 内部左侧侧边栏 - 会话列表 - 统一背景色 */
.session-sidebar {
  width: 280px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid rgba(147, 112, 219, 0.1);
    background: transparent;

    .sidebar-title {
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
    }

    .new-chat-btn {
      background: #7b42f6;
      border: none;
      transition: all 0.3s ease;

      &:hover {
        background: #6b35e0;
        transform: scale(1.05);
      }
    }
  }

  .history-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 16px;

    .history-label {
      padding: 0 8px 12px;
      font-size: 12px;
      color: #8c8c8c;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .session-scroll-area {
      flex: 1;
      overflow-y: auto;
      padding: 0;

      &::-webkit-scrollbar {
        width: 4px;
      }
      &::-webkit-scrollbar-thumb {
        background: rgba(147, 112, 219, 0.2);
        border-radius: 2px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
      }
    }

    .session-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      margin: 6px 0;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s ease;
      color: #595959;
      background: transparent;
      border: 1px solid transparent;

      &:hover {
        background: rgba(147, 112, 219, 0.08);
        color: #7b42f6;
        border-color: rgba(147, 112, 219, 0.15);

        .session-actions {
          opacity: 1;
        }
      }

      &.active {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        color: #7b42f6;
        font-weight: 500;
        border-color: rgba(147, 112, 219, 0.2);
        box-shadow: 0 2px 8px rgba(147, 112, 219, 0.1);

        .chat-icon {
          color: #7b42f6;
        }
      }

      .session-title-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
        flex: 1;
        overflow: hidden;

        .chat-icon {
          font-size: 16px;
          color: #d1d5db;
          flex-shrink: 0;
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
        flex-shrink: 0;

        .delete-text {
          font-size: 12px;
          color: #9ca3af;
          padding: 4px 8px;
          border-radius: 4px;
          transition: all 0.2s;
          cursor: pointer;

          &:hover {
            color: #f56c6c;
            background: #fef0f0;
          }
        }
      }
    }
  }
}

/* 右侧主内容区 - 统一背景色 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #f8f7ff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(147, 112, 219, 0.1);
  border: 1px solid rgba(147, 112, 219, 0.1);
  overflow: hidden;
}

/* 场景1：欢迎页（新会话） */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  min-height: 0;

  .welcome-content {
    width: 100%;
    max-width: 720px;
    padding: 0 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: -40px;
  }

  .logo-area {
    text-align: center;
    margin-bottom: 36px;

    .logo-circle {
      width: 72px;
      height: 72px;
      background: #7b42f6;
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 24px;
      box-shadow: 0 8px 24px rgba(123, 66, 246, 0.25);

      .el-icon {
        font-size: 36px;
        color: #ffffff;
      }
    }

    h1 {
      font-size: 28px;
      color: #1f2937;
      margin: 0 0 12px;
      font-weight: 600;
      letter-spacing: -0.5px;
    }

    p {
      color: #6b7280;
      font-size: 15px;
      margin: 0;
      font-weight: 400;
    }
  }

  .center-input-wrapper {
    width: 100%;
    max-width: 640px;
    position: relative;
    background: #ffffff;
    border-radius: 16px;
    padding: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(147, 112, 219, 0.15);
    transition: all 0.3s ease;

    &:focus-within {
      box-shadow: 0 4px 24px rgba(123, 66, 246, 0.15);
      border-color: #7b42f6;
    }

    .center-input {
      :deep(.el-textarea__inner) {
        border-radius: 12px;
        padding: 12px 48px 12px 16px;
        font-size: 15px;
        border: none !important;
        background: transparent;
        box-shadow: none !important;
        outline: none !important;
        min-height: 52px !important;

        &::placeholder {
          color: #9ca3af;
        }

        &:focus {
          box-shadow: none !important;
          border: none !important;
          outline: none !important;
        }
      }
    }

    .input-actions {
      position: absolute;
      right: 14px;
      bottom: 14px;

      .el-button {
        width: 36px;
        height: 36px;
        background: #7b42f6;
        border: none;
        transition: all 0.3s ease;
        border-radius: 10px;

        &:hover {
          transform: translateY(-2px);
          background: #6b35e0;
        }

        &:active {
          transform: translateY(0);
        }

        &.is-disabled {
          background: #e5e7eb;
        }

        .el-icon {
          font-size: 18px;
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
    margin-top: 24px;

    .chip {
      padding: 10px 18px;
      background: #ffffff;
      border-radius: 20px;
      font-size: 14px;
      color: #4b5563;
      cursor: pointer;
      transition: all 0.3s ease;
      border: 1px solid #e5e7eb;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      font-weight: 500;

      &:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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
  background: transparent;

  .chat-header {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    flex-shrink: 0;
    background: transparent;

    .chat-header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .back-icon {
        font-size: 20px;
        color: #6b7280;
        cursor: pointer;
        padding: 8px;
        border-radius: 8px;
        transition: all 0.2s;

        &:hover {
          background: #f3f4f6;
          color: #7b42f6;
        }
      }

      .chat-title {
        font-size: 16px;
        font-weight: 600;
        color: #1f2937;
        letter-spacing: 0.3px;
      }
    }

    .chat-time {
      font-size: 13px;
      color: #9ca3af;
      font-weight: 500;
    }
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
    background: transparent;
    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
      display: none;
    }

    .message-row {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      align-items: flex-start;

      &.user {
        flex-direction: row-reverse;

        .message-bubble {
          background: transparent;
          color: #374151;
          border-radius: 0;
          box-shadow: none;

          :deep(pre) {
            background: #1f2937;
            border: none;
          }

          :deep(code) {
            background: #f3f4f6;
            color: #ef4444;
          }

          :deep(p) {
            color: #374151;
          }
        }
      }

      &.assistant {
        .message-bubble {
          background: transparent;
          color: #374151;
          border-radius: 0;
          box-shadow: none;
          border: none;
        }
      }

      .avatar {
        flex-shrink: 0;
        margin-top: 2px;

        .user-avatar {
          background: #e5e7eb;
          border: 2px solid #fff;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }

        .ai-avatar {
          background: #7b42f6;
          color: #fff;
          border-radius: 10px;
          border: 2px solid #fff;
          box-shadow: 0 1px 3px rgba(123, 66, 246, 0.2);
        }
      }

      .message-bubble {
        max-width: 80%;
        padding: 0;
        font-size: 15px;
        line-height: 1.6;
        position: relative;
        transition: all 0.3s ease;

        .message-content {
          word-wrap: break-word;

          :deep(p) {
            margin: 0 0 10px 0;
            &:last-child { margin: 0; }
          }

          :deep(pre) {
            background: #1f2937;
            color: #e5e7eb;
            padding: 14px;
            border-radius: 10px;
            overflow-x: auto;
            margin: 10px 0;
            font-size: 13px;
          }

          :deep(code) {
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            padding: 2px 6px;
            background: #f3f4f6;
            border-radius: 4px;
            color: #ef4444;
          }
        }

        .message-status {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #9ca3af;
          margin-top: 8px;

          .is-loading {
            animation: rotating 2s linear infinite;
          }
        }

        .message-actions {
          display: flex;
          gap: 8px;
          margin-top: 12px;
          padding-top: 8px;
          border-top: 1px solid #e5e7eb;

          .el-button {
            font-size: 12px;
            color: #6b7280;

            &:hover {
              color: #7b42f6;
            }

            .el-icon {
              color: inherit;
            }
          }
        }
      }
    }
  }

  .chat-footer {
    padding: 16px 24px 20px;
    background: transparent;

    .input-box {
      position: relative;
      border: 1px solid rgba(147, 112, 219, 0.15);
      border-radius: 16px;
      padding: 8px;
      background: #ffffff;
      transition: all 0.3s;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
      max-width: 900px;
      margin: 0 auto;

      &:focus-within {
        border-color: #7b42f6;
        box-shadow: 0 4px 20px rgba(123, 66, 246, 0.12);
      }

      :deep(.el-textarea__inner) {
        border: none !important;
        box-shadow: none !important;
        padding: 10px 48px 10px 14px;
        background: transparent;
        outline: none !important;
        font-size: 15px;
        min-height: 44px !important;

        &::placeholder {
          color: #9ca3af;
        }
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
        background: #7b42f6;
        border: none;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-50%) scale(1.05);
          background: #6b35e0;
        }

        &:active {
          transform: translateY(-50%) scale(0.95);
        }

        &.is-disabled {
          background: #e5e7eb;
        }

        .el-icon {
          color: white;
          font-size: 14px;
        }
      }
    }
  }
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
