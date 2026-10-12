import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { initThemeFromStorage } from './composables/useTheme'

initThemeFromStorage()

createApp(App).mount('#app')
