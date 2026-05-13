import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        // Не следовать редиректам автоматически,
        // чтобы прокси мог переписать Location заголовок
        followRedirects: false,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('[Proxy Error]', err.message, req.url)
          })
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('[Proxy]', req.method, req.url, '-> http://backend:8000' + req.url)
          })
        }
      }
    }
  }
})