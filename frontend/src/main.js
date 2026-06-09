// @author beishi
// @date 2026/6/9
// @description Application entry point - mounts Vue app with Pinia and Router
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
