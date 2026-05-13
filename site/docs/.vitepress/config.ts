import { defineConfig } from 'vitepress'

export default defineConfig({
  vite: {
    server: {
      host: '0.0.0.0',  // ← Слушать все интерфейсы (для туннеля)
      allowedHosts: [   // ← Разрешить эти домены
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
        }
      }
    }
  }
})