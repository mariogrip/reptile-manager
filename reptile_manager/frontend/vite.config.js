import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { readFileSync } from 'fs'

// Single source of truth for the version: the add-on's config.yaml
function addonVersion() {
  try {
    const yaml = readFileSync(resolve(__dirname, '../config.yaml'), 'utf8')
    return yaml.match(/^version:\s*["']?([^"'\s]+)/m)?.[1] ?? 'dev'
  } catch {
    return 'dev'
  }
}

export default defineConfig({
  plugins: [vue()],
  base: './',   // relative paths — required for HA Ingress
  define: {
    __APP_VERSION__: JSON.stringify(addonVersion()),
  },
  resolve: {
    alias: { '@': resolve(__dirname, 'src') }
  }
})
