<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/i18n'

const router = useRouter()
const auth = useAuthStore()
const { t } = useI18n()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = t('login.error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-surface-900 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="text-6xl mb-4">🦎</div>
        <h1 class="text-2xl font-bold text-slate-200">Reptile Manager</h1>
        <p class="text-slate-500 text-sm mt-1">{{ t('login.subtitle') }}</p>
      </div>

      <div class="card">
        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label>{{ t('login.username') }}</label>
            <input v-model="username" type="text" placeholder="admin" required autofocus />
          </div>
          <div>
            <label>{{ t('login.password') }}</label>
            <input v-model="password" type="password" placeholder="••••••••" required />
          </div>

          <div v-if="error" class="text-red-400 text-sm text-center py-1">{{ error }}</div>

          <button type="submit" class="btn-primary w-full justify-center" :disabled="loading">
            <span v-if="loading">{{ t('login.submitting') }}</span>
            <span v-else>{{ t('login.submit') }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
