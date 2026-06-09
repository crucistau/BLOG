// @author beishi
// @date 2026/6/9
// @description Pinia app store - manages auth token and user state with localStorage persistence
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const TOKEN_KEY = 'devlog-token'

export const useAppStore = defineStore('app', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }

  function setUser(userData) {
    user.value = userData
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return {
    token,
    user,
    isLoggedIn,
    setToken,
    setUser,
    logout,
  }
})
