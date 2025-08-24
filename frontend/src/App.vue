<template>
  <div id="app">
    <header>
      <h1>TokenAI ChatBot</h1>
      <p>自适应智能知识库</p>
    </header>
    <main>
      <ChatWindow />
    </main>
  </div>
</template>

<script>
import ChatWindow from './components/ChatWindow.vue'

export default {
  name: 'App',
  components: {
    ChatWindow
  }
}
</script>

<style>
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

header h1 {
  color: #2c3e50;
  margin-bottom: 8px;
}

header p {
  color: #7f8c8d;
  margin: 0;
}
</style>