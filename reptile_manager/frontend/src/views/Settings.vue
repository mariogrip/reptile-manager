<script setup>
import { ref, onMounted, computed } from 'vue'
import { ha } from '@/api'
import { useI18n } from '@/i18n'

const { t } = useI18n()
const config = ref(null)
const haToken = ref('')
const saving = ref(false)
const testing = ref(false)
const syncing = ref(false)
const testResult = ref(null)
const saved = ref(false)
const loading = ref(true)
const currentApiUrl = computed(() => window.__REPTILE_API__ || import.meta.env.VITE_API_URL || '(Auto-detect via Ingress)')

onMounted(async () => {
  try {
    const res = await ha.getConfig()
    config.value = res.data
  } finally {
    loading.value = false
  }
})

async function saveConfig() {
  saving.value = true
  saved.value = false
  try {
    const payload = { ...config.value }
    if (haToken.value) payload.ha_token = haToken.value
    const res = await ha.updateConfig(payload)
    config.value = res.data
    haToken.value = ''
    saved.value = true
    setTimeout(() => saved.value = false, 3000)
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    const res = await ha.test()
    testResult.value = res.data
  } finally {
    testing.value = false
  }
}

async function syncNow() {
  syncing.value = true
  try {
    await ha.sync()
    alert(t('settings.sync_success'))
  } catch (e) {
    alert(t('settings.sync_failed') + (e.response?.data?.detail ?? e.message))
  } finally {
    syncing.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl">
    <h1 class="text-2xl font-bold text-slate-200 mb-6">{{ t('settings.title') }}</h1>

    <div v-if="loading" class="text-slate-500 text-center py-16">{{ t('common.loading') }}</div>

    <div v-else-if="config" class="space-y-6">

      <!-- API URL Info -->
      <div class="card border border-surface-600">
        <div class="flex items-center gap-3 mb-3">
          <span class="text-xl">🔌</span>
          <div>
            <h2 class="font-semibold text-slate-200">{{ t('settings.api_title') }}</h2>
            <p class="text-xs text-slate-500">{{ t('settings.api_config_hint') }}</p>
          </div>
        </div>
        <div class="bg-surface-900 rounded-lg p-3 text-xs font-mono text-slate-300 break-all">
          {{ currentApiUrl }}
        </div>
        <p class="text-xs text-slate-500 mt-2">
          {{ t('settings.api_network_hint') }}
        </p>
      </div>

      <!-- Züchter/Verkäufer Profil -->
      <div class="card">
        <h2 class="font-semibold text-slate-200 mb-1">{{ t('settings.breeder_profile') }}</h2>
        <p class="text-sm text-slate-500 mb-4">
          {{ t('settings.breeder_hint') }}
        </p>
        <div class="grid sm:grid-cols-2 gap-4">
          <div><label>{{ t('settings.breeder_name') }}</label><input v-model="config.breeder_name"     placeholder="Max Mustermann" /></div>
          <div><label>{{ t('settings.breeder_phone') }}</label><input v-model="config.breeder_phone" placeholder="+49 …" /></div>
          <div><label>{{ t('settings.breeder_street') }}</label><input v-model="config.breeder_street"   placeholder="Musterstraße 1" /></div>
          <div><label>{{ t('settings.breeder_zip') }}</label><input v-model="config.breeder_zip_city" placeholder="12345 Musterstadt" /></div>
        </div>
      </div>

      <!-- HA Integration -->
      <div class="card">
        <div class="flex items-center gap-3 mb-5">
          <span class="text-2xl">🏠</span>
          <div>
            <h2 class="font-semibold text-slate-200">{{ t('settings.ha') }}</h2>
            <p class="text-xs text-slate-500">{{ t('settings.ha_subtitle') }}</p>
          </div>
          <div class="ml-auto">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="config.enabled" class="w-4 h-4" />
              <span class="text-sm text-slate-300">{{ t('common.enabled') }}</span>
            </label>
          </div>
        </div>

        <form @submit.prevent="saveConfig" class="space-y-4">
          <div>
            <label>{{ t('settings.ha_url') }}</label>
            <input v-model="config.ha_url" type="url" placeholder="http://homeassistant.local:8123" />
            <p class="text-xs text-slate-500 mt-1">{{ t('settings.ha_url_hint') }}</p>
          </div>

          <div>
            <label>{{ t('settings.ha_token') }}</label>
            <input v-model="haToken" type="password" :placeholder="t('settings.token_placeholder')" />
            <p class="text-xs text-slate-500 mt-1">
              {{ t('settings.token_hint') }}
            </p>
          </div>

          <div>
            <label>{{ t('settings.webhook_id') }}</label>
            <input v-model="config.webhook_id" placeholder="reptile_manager_events" />
            <p class="text-xs text-slate-500 mt-1">
              {{ t('settings.webhook_hint') }}
            </p>
          </div>

          <div>
            <label>{{ t('settings.reminder_days') }}</label>
            <input type="number" v-model="config.feeding_reminder_days" min="1" max="90" />
          </div>

          <hr class="border-surface-500" />

          <div>
            <h3 class="text-sm font-medium text-slate-400 mb-3">{{ t('settings.notify') }}</h3>
            <div class="space-y-2">
              <label class="flex items-center gap-2 cursor-pointer text-sm">
                <input type="checkbox" v-model="config.notify_feeding" class="w-4 h-4" /> {{ t('settings.notify_feeding') }}
              </label>
              <label class="flex items-center gap-2 cursor-pointer text-sm">
                <input type="checkbox" v-model="config.notify_shedding" class="w-4 h-4" /> {{ t('settings.notify_shedding') }}
              </label>
              <label class="flex items-center gap-2 cursor-pointer text-sm">
                <input type="checkbox" v-model="config.notify_breeding" class="w-4 h-4" /> {{ t('settings.notify_breeding') }}
              </label>
            </div>
          </div>

          <div class="flex gap-3 flex-wrap pt-2">
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? t('common.saving') : t('common.save') }}
            </button>
            <button type="button" class="btn-secondary" :disabled="testing" @click="testConnection">
              {{ testing ? t('settings.testing') : t('settings.test') }}
            </button>
            <button type="button" class="btn-secondary" :disabled="syncing || !config.enabled" @click="syncNow">
              {{ syncing ? t('settings.syncing') : t('settings.sync') }}
            </button>
          </div>

          <div v-if="saved" class="text-brand-400 text-sm">{{ t('settings.saved') }}</div>

          <div v-if="testResult" :class="testResult.success ? 'text-brand-400' : 'text-red-400'" class="text-sm">
            {{ testResult.success ? '✓ ' + testResult.message : '✗ ' + testResult.error }}
          </div>
        </form>
      </div>

      <!-- HA YAML snippet -->
      <div class="card">
        <h2 class="font-semibold text-slate-200 mb-3">{{ t('settings.yaml_title') }}</h2>
        <p class="text-sm text-slate-400 mb-3">
          {{ t('settings.yaml_hint') }}
        </p>
        <pre v-pre class="bg-surface-900 rounded-lg p-4 text-xs text-slate-300 overflow-x-auto"><code># Schritt 1: REST-Sensor (einen Datenpunkt laden)
sensor:
  - platform: rest
    resource: http://DEIN_SERVER:8000/api/ha/sensors
    scan_interval: 300
    name: reptile_manager_data
    json_attributes:
      - summary
      - animals

# Schritt 2: Template-Sensoren daraus ableiten
template:
  - sensor:
      - name: "Reptilien aktiv"
        state: "{{ state_attr('sensor.reptile_manager_data', 'summary')['active_animals'] | default(0) }}"
        unit_of_measurement: "Tiere"
        icon: mdi:snake

      - name: "Reptilien nicht gefüttert"
        state: "{{ state_attr('sensor.reptile_manager_data', 'summary')['animals_not_fed'] | default(0) }}"
        unit_of_measurement: "Tiere"
        icon: mdi:food-off

# Schritt 3: Automation
automation:
  - alias: "Reptilien Fütterungswarnung"
    trigger:
      - platform: numeric_state
        entity_id: sensor.reptilien_nicht_gefuettert
        above: 0
    action:
      - service: notify.mobile_app_dein_handy
        data:
          message: >
            {{ states('sensor.reptilien_nicht_gefuettert') }}
            Reptilien brauchen Futter!</code></pre>
      </div>

      <!-- Webhook info -->
      <div class="card">
        <h2 class="font-semibold text-slate-200 mb-3">{{ t('settings.webhook_title') }}</h2>
        <p class="text-sm text-slate-400 mb-3">
          {{ t('settings.webhook_desc') }}
        </p>
        <div class="space-y-2">
          <div v-for="ev in [
            { type: 'reptile_feeding', desc: t('settings.webhook_feeding'), fields: 'animal_name, food_type, food_size, accepted' },
            { type: 'reptile_shedding', desc: t('settings.webhook_shedding'), fields: 'animal_name, complete, in_one_piece' },
            { type: 'reptile_breeding', desc: t('settings.webhook_breeding'), fields: 'female_name, male_name, date_paired' },
          ]" :key="ev.type" class="bg-surface-900 rounded-lg p-3">
            <div class="flex items-center gap-2">
              <code class="text-brand-400 text-xs">{{ ev.type }}</code>
              <span class="text-xs text-slate-500">·</span>
              <span class="text-xs text-slate-500">{{ ev.desc }}</span>
            </div>
            <div class="text-xs text-slate-600 mt-0.5">{{ t('settings.fields') }} {{ ev.fields }}</div>
          </div>
        </div>
      </div>

      <!-- About -->
      <div class="card">
        <h2 class="font-semibold text-slate-200 mb-4">{{ t('settings.about_title') }}</h2>
        <div class="flex items-center gap-4 mb-5">
          <div class="text-5xl">🦎</div>
          <div>
            <div class="text-lg font-bold text-slate-200">Reptile Manager</div>
            <div class="text-sm text-slate-400">Version 1.1.1</div>
            <div class="text-xs text-slate-600 mt-0.5">Self-hosted reptile husbandry management for Home Assistant</div>
          </div>
        </div>
        <p class="text-sm text-slate-400 mb-4 leading-relaxed">
          {{ t('settings.about_text') }}
        </p>
        <div class="grid grid-cols-2 gap-3 text-sm mb-5">
          <div class="bg-surface-600 rounded-lg p-3">
            <div class="text-xs text-slate-500 mb-1">{{ t('settings.author') }}</div>
            <div class="text-slate-300 font-medium">demrios-de</div>
          </div>
          <div class="bg-surface-600 rounded-lg p-3">
            <div class="text-xs text-slate-500 mb-1">{{ t('settings.license') }}</div>
            <div class="text-slate-300 font-medium">MIT</div>
          </div>
          <div class="bg-surface-600 rounded-lg p-3">
            <div class="text-xs text-slate-500 mb-1">{{ t('settings.backend') }}</div>
            <div class="text-slate-300 font-medium">FastAPI + SQLite</div>
          </div>
          <div class="bg-surface-600 rounded-lg p-3">
            <div class="text-xs text-slate-500 mb-1">{{ t('settings.frontend') }}</div>
            <div class="text-slate-300 font-medium">Vue 3 + Tailwind</div>
          </div>
        </div>
        <div class="flex flex-wrap gap-3">
          <a href="https://github.com/demrios-de/reptile-manager"
             target="_blank" rel="noopener"
             class="btn-secondary btn-sm text-xs flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            GitHub
          </a>
          <a href="https://github.com/demrios-de/reptile-manager/blob/main/CHANGELOG.md"
             target="_blank" rel="noopener"
             class="btn-secondary btn-sm text-xs">
            📋 Changelog
          </a>
          <a href="https://github.com/demrios-de/reptile-manager/issues"
             target="_blank" rel="noopener"
             class="btn-secondary btn-sm text-xs">
            {{ t('settings.report_bug') }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
