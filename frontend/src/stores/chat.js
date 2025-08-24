import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const conversationId = ref(null)
  
  // 添加消息到历史记录
  const addMessage = (role, content) => {
    messages.value.push({
      id: Date.now(),
      role,
      content,
      timestamp: new Date()
    })
  }
  
  // 更新最后一条消息（用于流式输出）
  const updateLastMessage = (content) => {
    if (messages.value.length > 0) {
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage.role === 'assistant') {
        lastMessage.content += content
      }
    }
  }
  
  // 发送消息到后端
  const sendMessage = async (content) => {
    isLoading.value = true
    error.value = null
    
    // 添加用户消息
    addMessage('user', content)
    
    // 添加空的AI消息（用于流式填充）
    addMessage('assistant', '')
    
    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: content,
          conversation_id: conversationId.value 
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // 处理流式响应
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        console.log(lines) 
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              break
            }
            
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                updateLastMessage(parsed.content)
              }
            } catch (e) {
              console.error('解析错误:', e)
            }
          }
        }
      }
    } catch (err) {
      console.error('发送消息失败:', err)
      error.value = err.message
      // 移除空的AI消息
      messages.value.pop()
      // 添加错误消息
      addMessage('assistant', `抱歉，发生了错误：${err.message}`)
    } finally {
      isLoading.value = false
    }
  }
  
  // 清除聊天记录
  const clearMessages = () => {
    messages.value = []
    conversationId.value = Date.now().toString() // 生成新的会话ID
  }
  
  // 初始化会话ID
  conversationId.value = Date.now().toString()
  
  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearMessages
  }
})