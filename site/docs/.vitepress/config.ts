import { defineConfig } from 'vitepress'
import { resolve } from 'path'

// 🔗 Вычисляем корень проекта для корректных путей
const root = resolve(__dirname, '..', '..', '..')

export default defineConfig({
  // 🌐 Базовые настройки
  title: 'Knowledge Base',
  description: 'Персональная база знаний с RAG и локальным ИИ',
  lastUpdated: true,
  cleanUrls: true, // 🔥 Убирает .html из URL

  // 📁 Пути
  srcDir: resolve(__dirname, '..'),
  publicDir: resolve(__dirname, '..', 'public'),

  // 🤖 Markdown настройки
  markdown: {
    lineNumbers: true,
    excerpt: true,
  },

  // 🌐 Сервер + Прокси (ИСПРАВЛЕНО ДЛЯ СТРИМИНГА)
  vite: {
    server: {
      host: '0.0.0.0',
      allowedHosts: [
        'swinki.ru',
        'www.swinki.ru',
        'localhost',
        '127.0.0.1'
      ],
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
          
          // 🔥 КРИТИЧНО ДЛЯ СТРИМИНГА:
          // 1. Отключаем буферизацию ответов
          buffer: false,
          
          // 2. Пробрасываем заголовки для SSE / Nginx
          headers: {
            'X-Forwarded-Host': 'swinki.ru',
            'X-Accel-Buffering': 'no',  // 🔥 Отключает буфер Nginx (если проксируется)
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
          },
          
          // 3. Поддержка долгосрочных соединений
          ws: true,
          
          // 4. Не ждём конца ответа — отдаём чанки сразу
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

  // 🎨 Тема
  themeConfig: {
    logo: '/logo.png',

    nav: [
      { text: '🏠 Главная', link: '/' },
      { text: '📚 Статьи', link: '/articles/' },
      { text: '🤖 Чат', link: '/chat/' },
    ],

    sidebar: {
      '/articles/': [
        {
          text: 'Все статьи',
          items: []
        }
      ],
      '/': [
        {
          text: 'Навигация',
          items: [
            { text: '🏠 Главная', link: '/' },
            { text: '📚 Статьи', link: '/articles/' },
          ]
        }
      ]
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
              button: {
                buttonText: 'Поиск',
                buttonAriaLabel: 'Поиск по сайту'
              },
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

  // 🌍 Локализация
  locales: {
    root: {
      label: 'Русский',
      lang: 'ru'
    }
  },

  // 🚀 Meta-теги
  head: [
    ['meta', { name: 'theme-color', content: '#3eaf7c' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'ru_RU' }],
    ['meta', { property: 'og:site_name', content: 'Knowledge Base' }],
  ]
})