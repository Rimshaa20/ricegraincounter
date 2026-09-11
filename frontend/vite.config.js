import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward API requests to the FastAPI backend during development
      '/count-rice': {
        target: 'https://ricegraincounter.onrender.com',
        changeOrigin: true,
      },
    },
  },
})
