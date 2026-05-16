import { defineConfig } from 'vitepress'
import { resolve } from 'path'

const root = resolve(__dirname, '..', '..', '..')

export default defineConfig({
  title: 'Knowledge Base',
  description: 'Персональная база знаний с RAG и локальным ИИ',
  lastUpdated: true,
  cleanUrls: true,
  srcDir: resolve(__dirname, '..'),
  publicDir: resolve(__dirname, '..', 'public'),
  markdown: { lineNumbers: true, excerpt: true },

  vite: {
    server: {
      host: '0.0.0.0',
      allowedHosts: ['swinki.ru', 'www.swinki.ru', 'localhost', '127.0.0.1'],
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
          buffer: false,
          headers: {
            'X-Forwarded-Host': 'swinki.ru',
            'X-Accel-Buffering': 'no',
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
          },
          ws: true,
          selfHandleResponse: false,
        }
      }
    },
    resolve: {
      alias: {
        '@': resolve(root, 'site/docs'),
        '@data': resolve(root, 'data'),
      }
    }
  },

  themeConfig: {
    nav: [
      { text: '🏠 Главная', link: '/' },
      { text: '📚 Статьи', link: '/articles/' },
      { text: '🤖 Чат', link: '/chat/' },
    ],
    sidebar: {
      '/articles/': [{ text: 'Все статьи', items: [] }],
      '/': [{ text: 'Навигация', items: [
        { text: '🏠 Главная', link: '/' },
        { text: '📚 Статьи', link: '/articles/' },
        { text: '🤖 Чат', link: '/chat/' },
      ]}],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/svyatoylol/knowledgebse' }
    ],
    outline: { level: [2, 3], label: 'На этой странице' },
    editLink: {
      pattern: 'https://github.com/svyatoylol/knowledgebse/edit/main/site/docs/:path',
      text: 'Редактировать эту страницу'
    },
    footer: {
      message: 'Работает на VitePress + Ollama + Qdrant',
      copyright: '© 2026 svyatoylol'
    },
    search: {
      provider: 'local',
      options: {
        locales: {
          ru: {
            translations: {
              button: { buttonText: 'Поиск', buttonAriaLabel: 'Поиск по сайту' },
              modal: {
                displayDetails: 'Показать детали',
                noResultsText: 'Ничего не найдено',
                resetButtonTitle: 'Сбросить поиск'
              }
            }
          }
        }
      }
    }
  },

  locales: { root: { label: 'Русский', lang: 'ru' } },
  head: [
    ['meta', { name: 'theme-color', content: '#6366f1' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'ru_RU' }],
    ['meta', { property: 'og:site_name', content: 'Knowledge Base' }],
  ]
})