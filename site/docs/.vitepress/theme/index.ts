import DefaultTheme from 'vitepress/theme'
import './custom.css'  // 🔥 Подключаем стили
import AiChat from './AiChat.vue'
import ArticleList from './ArticleList.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('AiChat', AiChat)
    app.component('ArticleList', ArticleList)
  }
}