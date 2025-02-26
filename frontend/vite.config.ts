import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  server: {
    host:"0.0.0.0", // "127.0.0.1"
    port: 5173,
    strictPort: true,
    allowedHosts: [
      //"127.0.0.1",
      //"localhost",
      "roughy-measured-ghastly.ngrok-free.app",
      "https://b824-2a02-2149-8adf-6f00-9090-8539-7394-77e5.ngrok-free.app",  // CHANGE
    ],
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  },
})