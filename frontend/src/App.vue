<!--
  @author beishi
  @date 2026/6/9
  @description Root application component with Navbar and router-view
-->
<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { trackPageView } from './api/index.js'

const route = useRoute()
watch(() => route.path, (path) => {
  if (!path.startsWith('/admin')) {
    trackPageView(path).catch(() => {})
  }
}, { immediate: true })
</script>

<template>
  <div class="app">
    <Navbar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>
