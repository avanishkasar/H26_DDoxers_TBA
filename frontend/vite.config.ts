import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // Read the shared repo-root .env so the whole stack has one config file.
  const env = loadEnv(mode, '..', '')
  return {
    envDir: '..',
    plugins: [react(), tailwindcss()],
    server: {
      port: 5173,
      proxy: {
        '/api': { target: env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000', changeOrigin: true },
      },
    },
  }
})
