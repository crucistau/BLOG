// @author beishi
// @date 2026/6/9
// @description Theme composable - manages current theme with localStorage persistence
import { ref, watch } from 'vue'

const THEMES = ['dracula', 'amber', 'slate']
const STORAGE_KEY = 'devlog-theme'

const currentTheme = ref(localStorage.getItem(STORAGE_KEY) || 'dracula')

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem(STORAGE_KEY, theme)
}

applyTheme(currentTheme.value)

watch(currentTheme, (newTheme) => {
  applyTheme(newTheme)
})

export function useTheme() {
  function cycleTheme() {
    const currentIndex = THEMES.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % THEMES.length
    currentTheme.value = THEMES[nextIndex]
  }

  function setTheme(theme) {
    if (THEMES.includes(theme)) {
      currentTheme.value = theme
    }
  }

  return {
    currentTheme,
    cycleTheme,
    setTheme,
    themes: THEMES,
  }
}
