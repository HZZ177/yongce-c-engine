import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3007,
    host: '0.0.0.0',
    proxy: {
      '/closeApp': {
        target: 'http://localhost:17771',
        changeOrigin: true
      },
      '/roadApp': {
        target: 'http://localhost:17771',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
}) 