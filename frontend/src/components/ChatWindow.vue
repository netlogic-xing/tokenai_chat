<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>AI Chat助手</h1>
      <button @click="clearChat" class="clear-btn">清除对话</button>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="message in messages" :key="message.id" 
           :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']">
        <div class="avatar-container">
          <div class="avatar" v-html="message.role === 'user' ? userAvatarSvg : aiAvatarSvg"></div>
        </div>
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="isLoading" class="message ai-message typing-indicator">
        <div class="avatar-container">
          <div class="avatar" v-html="aiAvatarSvg"></div>
        </div>
        <div class="message-content">
          <span>AI正在思考</span>
          <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <div class="input-avatar">
        <div class="avatar small" v-html="userAvatarSvg"></div>
      </div>
      <textarea 
        v-model="userInput" 
        @keydown.enter.prevent="handleSendMessage"
        placeholder="输入您的消息..."
        :disabled="isLoading"
        rows="1"
        ref="textArea"
        @input="adjustTextareaHeight"
        class="no-scrollbar"
      ></textarea>
      <button 
        class="send-button" 
        @click="handleSendMessage"
        :disabled="isLoading || !userInput.trim()"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { useChatStore } from '../stores/chat'
import { mapState, mapActions } from 'pinia'
import { nextTick } from 'vue'

export default {
  name: 'ChatWindow',
  data() {
    return {
      userInput: '',
      // 内联SVG图标
      userAvatarSvg: `
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="20" fill="#4f46e5"/>
          <circle cx="20" cy="15" r="5" fill="white"/>
          <path d="M30 32C30 27.5817 25.5228 24 20 24C14.4772 24 10 27.5817 10 32V40H30V32Z" fill="white"/>
        </svg>
      `,
      aiAvatarSvg: `
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="20" fill="#10b981"/>
          <circle cx="20" cy="15" r="5" fill="white"/>
          <path d="M25 25L15 25L15 30C15 31.1046 15.8954 32 17 32L23 32C24.1046 32 25 31.1046 25 30L25 25Z" fill="white"/>
          <rect x="15" y="20" width="10" height="2" fill="white"/>
        </svg>
      `
    }
  },
  computed: {
    ...mapState(useChatStore, ['messages', 'isLoading'])
  },
  methods: {
    ...mapActions(useChatStore, ['sendMessage', 'clearMessages']),
    
    async handleSendMessage() {
      if (!this.userInput.trim() || this.isLoading) return
      
      const message = this.userInput.trim()
      this.userInput = ''
      this.adjustTextareaHeight()
      
      await this.sendMessage(message)
      
      // 等待DOM更新后滚动到底部
      await nextTick()
      this.scrollToBottom()
    },
    
    clearChat() {
      this.clearMessages()
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    adjustTextareaHeight() {
      const textarea = this.$refs.textArea
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  },
  mounted() {
    this.scrollToBottom()
    
    // 添加欢迎消息
    if (this.messages.length === 0) {
      this.messages.push({
        id: Date.now(),
        role: 'assistant',
        content: '您好！我是AI助手，很高兴为您服务。请问有什么可以帮您的？',
        timestamp: new Date()
      })
    }
  },
  watch: {
    messages: {
      handler() {
        this.scrollToBottom()
      },
      deep: true
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.chat-container {
  width: 100%;
  height: 100%;
  /* max-width: 800px;
  max-height: 700px; */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 15px 20px;
  background-color: #4f46e5;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.clear-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 0.9rem;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 100%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  flex-direction: row-reverse;
}

.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar.small {
  width: 36px;
  height: 36px;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.4;
  position: relative;
}

.user-message .message-content {
  background-color: #4f46e5;
  color: white;
  border-bottom-right-radius: 5px;
}

.ai-message .message-content {
  background-color: #f3f4f6;
  color: #333;
  border-bottom-left-radius: 5px;
}

.message-text {
  margin-bottom: 5px;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  text-align: right;
}

.ai-message .message-time {
  text-align: left;
}

.typing-indicator {
  align-items: center;
}

.typing-indicator .message-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.typing-dots {
  display: flex;
  gap: 3px;
}

.typing-dot {
  width: 6px;
  height: 6px;
  background-color: #9ca3af;
  border-radius: 50%;
  animation: typingAnimation 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingAnimation {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-3px); }
}

.chat-input {
  padding: 15px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.input-avatar {
  flex-shrink: 0;
}

.chat-input textarea {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #d1d5db;
  border-radius: 20px;
  resize: none;
  outline: none;
  font-size: 16px;
  max-height: 120px;
  transition: border-color 0.3s;
  line-height: 1.4;
}

.chat-input textarea:focus {
  border-color: #4f46e5;
}

.send-button {
  padding: 10px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
  width: 40px;
  height: 40px;
}

.send-button svg {
  width: 20px;
  height: 20px;
}

.send-button:hover {
  background-color: #4338ca;
}

.send-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .chat-container {
    max-height: 100%;
    border-radius: 0;
  }
  
  .message-content {
    max-width: 80%;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
  }
}
/* 隐藏滚动条但保留滚动功能 */
.no-scrollbar {
  overflow: auto; /* 确保内容可滚动 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 和 Edge */
}

.no-scrollbar::-webkit-scrollbar {
  display: none; /* Chrome, Safari 和 Opera */
}
</style>