import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // Le indicamos a Vite exactamente qué archivos mapear para la criptografía
      '@noble/curves/ed25519': '@noble/curves/ed25519.js',
      '@noble/curves/abstract/utils': '@noble/curves/abstract/utils.js'
    }
  }
})
