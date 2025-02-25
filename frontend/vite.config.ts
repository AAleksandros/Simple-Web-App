import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    allowedHosts: [
      "roughy-measured-ghastly.ngrok-free.app",
      "https://8a6d-2a02-2149-8adf-6f00-76c9-7476-af5e-d6a4.ngrok-free.app",  // CHANGE
    ],
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  },
})