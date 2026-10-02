import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Match the FastAPI bind address exactly. On macOS, `localhost` can
        // resolve to IPv6 while the backend is listening only on IPv4.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
