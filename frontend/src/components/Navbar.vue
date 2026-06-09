<!--
  @author beishi
  @date 2026/6/9
  @description Sticky navigation bar with logo, nav links, and theme switcher
-->
<script setup>
import ThemeSwitcher from './ThemeSwitcher.vue'
</script>

<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="logo">
        <span class="logo-bracket">&lt;/&gt;</span>
        <span class="logo-text"> devlog</span>
      </router-link>

      <div class="nav-links">
        <router-link to="/" exact-active-class="router-link-active">
          Home
        </router-link>
        <router-link to="/posts" active-class="router-link-active">
          Posts
        </router-link>
        <router-link to="/tags" active-class="router-link-active">
          Tags
        </router-link>
      </div>

      <div class="nav-actions">
        <ThemeSwitcher />
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--nav-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  gap: 2px;
}

.logo:hover {
  color: var(--text-primary);
}

.logo-bracket {
  color: var(--accent);
  font-family: 'Fira Code', 'Cascadia Code', monospace;
}

.logo-text {
  color: var(--text-primary);
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-links a {
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.nav-links a:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.nav-links a.router-link-active {
  color: var(--accent);
  background: var(--bg-hover);
}

.nav-actions {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .navbar-inner {
    padding: 0 16px;
  }

  .nav-links a {
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .logo {
    font-size: 1rem;
  }
}
</style>
