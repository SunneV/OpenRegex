import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const robotsMeta = env.ROBOTS_META || env.VITE_ROBOTS_META || '__ROBOTS_META_PLACEHOLDER__'

  const apiUrl = env.VITE_API_URL || 'http://backend:8000';

  return {
    plugins: [
      react(),
      {
        name: 'html-transform',
        transformIndexHtml(html) {
          return html.replace('%ROBOTS_META%', robotsMeta)
        }
      }
    ],
    server: {
      host: true,
      port: 5000,
      proxy: {
        '/api': {
          target: apiUrl,
          changeOrigin: true,
          secure: false,
        }
      },
      watch: {
        usePolling: true,
      }
    }
  }
})