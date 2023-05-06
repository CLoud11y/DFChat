<template>
  <component :is="currentView.view"  @loggedIn="handleLoggedIn"></component>
</template>
<script>
import ChatWindow from './components/ChatWindow.vue'
import LoginView from './components/LoginView.vue'
import { createApp, reactive } from 'vue'

export default {
  setup() {
    const username = localStorage.getItem('username');
    const expirationDate = localStorage.getItem('expirationDate');
    const currentDate = new Date();
    let currentView = reactive({"view":LoginView}
    )

    if (username && expirationDate && currentDate < new Date(expirationDate)) {
      currentView.view = ChatWindow
    } else {
      localStorage.removeItem('jwtToken')
      localStorage.removeItem('username')
      localStorage.removeItem('expirationDate')
    }
    return { currentView }
  },
  methods: {
    handleLoggedIn() {
      this.currentView.view = ChatWindow
    },
  },
  components: {
    ChatWindow,
    LoginView
  }
}
</script>
<style>
</style>