<!--
  @author beishi
  @date 2026/6/9
  @description Theme switcher button - cycles through Dracula, Amber, Slate themes
-->
<script setup>
import { useTheme } from '../composables/useTheme'

const { currentTheme, cycleTheme } = useTheme()

const themeIcons = {
  dracula: '&#9790;',   // moon
  amber: '&#9728;',     // sun
  slate: '&#9729;',     // cloud
}
</script>

<template>
  <button
    class="theme-switcher"
    @click="cycleTheme"
    :title="`Switch theme (current: ${currentTheme})`"
    :aria-label="`Switch theme, current: ${currentTheme}`"
  >
    <span class="theme-icon" v-html="themeIcons[currentTheme]" />
    <span class="theme-label">{{ currentTheme }}</span>
  </button>
</template>

<style scoped>
.theme-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.theme-switcher:hover {
  background: var(--bg-card);
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.theme-icon {
  font-size: 1.1rem;
}

.theme-label {
  text-transform: capitalize;
}
</style>
