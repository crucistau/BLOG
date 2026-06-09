<!--
  @author beishi
  @date 2026/6/9
  @description Admin login page - form with username/password, JWT token storage
-->
<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { adminLogin } from '../../api'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''

  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = 'Please fill in both fields'
    return
  }

  loading.value = true
  try {
    const res = await adminLogin({
      username: username.value,
      password: password.value,
    })
    const token = res.data.access_token || res.data.token
    if (token) {
      appStore.setToken(token)
      const redirect = route.query.redirect || '/admin'
      router.push(redirect)
    } else {
      errorMsg.value = 'Invalid response from server'
    }
  } catch (err) {
    console.error('Login.handleLogin - error:', err.message)
    errorMsg.value = err.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">Admin Login</h1>
      <p class="login-subtitle">Sign in to manage your blog</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter username"
            autocomplete="username"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  padding: 40px 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
}

.login-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.login-subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 28px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input {
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  border-color: var(--accent);
  outline: none;
}

.error-msg {
  font-size: 0.85rem;
  color: #ef4444;
  text-align: center;
}

.login-btn {
  padding: 12px;
  border-radius: 8px;
  background: var(--accent);
  color: var(--bg);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 4px;
}

.login-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
