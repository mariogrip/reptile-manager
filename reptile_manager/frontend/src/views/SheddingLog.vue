<script setup>
import { useI18n } from '@/i18n'
import { ref, onMounted, watch } from 'vue'
import { sheddings as sheddingsApi, animals as animalsApi } from '@/api'

const { t } = useI18n()

const list = ref([])
const allAnimals = ref([])
const filterAnimal = ref('')
const loading = ref(true)
const showForm = ref(false)
const saving = ref(false)
const form = ref({
  animal_id: '', date: new Date().toISOString().slice(0,16),
  complete: true, in_one_piece: true, pre_shed_days: '', notes: ''
})

onMounted(async () => {
  const [sRes, aRes] = await Promise.all([
    sheddingsApi.list({ limit: 200 }),
    animalsApi.list({ active_only: false, limit: 500 })
  ])
  list.value = sRes.data
  allAnimals.value = aRes.data
  loading.value = false
})

watch(filterAnimal, async () => {
  loading.value = true
  const params = filterAnimal.value ? { animal_id: filterAnimal.value, limit: 200 } : { limit: 200 }
  list.value = (await sheddingsApi.list(params)).data
  loading.value = false
})

async function addShedding() {
  saving.value = true
  try {
    const payload = { ...form.value, animal_id: parseInt(form.value.animal_id) }
    if (!payload.pre_shed_days) payload.pre_shed_days = null
    const res = await sheddingsApi.create(payload)
    const animal = allAnimals.value.find(a => a.id === res.data.animal_id)
    list.value.unshift({ ...res.data, animal_name: animal?.name })
    showForm.value = false
    form.value = { animal_id: '', date: new Date().toISOString().slice(0,16), complete: true, in_one_piece: true, pre_shed_days: '', notes: '' }
  } finally {
    saving.value = false
  }
}

async function deleteShedding(id) {
  if (!confirm(t('shedding.confirmDelete'))) return
  await sheddingsApi.delete(id)
  list.value = list.value.filter(s => s.id !== id)
}

function fmtDate(d) {
  return d ? new Date(d).toLocaleString('de-DE', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) : '—'
}
</script>

<template>
  <div>
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <h1 class="text-2xl font-bold text-slate-200">{{ t('shedding.title') }}</h1>
      <button class="btn-primary btn-sm" @click="showForm = !showForm">+ {{ t('shedding.add') }}</button>
    </div>

    <div class="mb-5">
      <select v-model="filterAnimal" class="max-w-xs">
        <option value="">{{ t('common.all') }}</option>
        <option v-for="a in allAnimals" :key="a.id" :value="a.id">{{ a.name }}</option>
      </select>
    </div>

    <div v-if="showForm" class="card mb-5">
      <h3 class="font-medium text-slate-200 mb-3">{{ t('shedding.add') }}</h3>
      <form @submit.prevent="addShedding" class="grid sm:grid-cols-2 gap-3">
        <div>
          <label>{{ t('feeding.animal') }} *</label>
          <select v-model="form.animal_id" required>
            <option value="">{{ t('feeding.select_animal') }}</option>
            <option v-for="a in allAnimals.filter(a => a.is_active)" :key="a.id" :value="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div><label>{{ t('shedding.date') }}</label><input type="datetime-local" v-model="form.date" required /></div>
        <div><label>{{ t('shedding.pre_shed_days') }}</label><input type="number" v-model="form.pre_shed_days" min="0" placeholder="7" /></div>
        <div class="flex gap-5 items-end pb-2">
          <label class="flex items-center gap-2 cursor-pointer text-sm">
            <input type="checkbox" v-model="form.complete" class="w-4 h-4" /> {{ t('shedding.complete') }}
          </label>
          <label class="flex items-center gap-2 cursor-pointer text-sm">
            <input type="checkbox" v-model="form.in_one_piece" class="w-4 h-4" /> {{ t('shedding.in_one_piece') }}
          </label>
        </div>
        <div class="sm:col-span-2"><label>{{ t('shedding.notes') }}</label><textarea v-model="form.notes" rows="2" /></div>
        <div class="sm:col-span-2 flex gap-2">
          <button type="submit" class="btn-primary btn-sm" :disabled="saving">{{ saving ? t('common.saving') : t('shedding.add') }}</button>
          <button type="button" class="btn-secondary btn-sm" @click="showForm = false">{{ t('common.cancel') }}</button>
        </div>
      </form>
    </div>

    <div class="card overflow-x-auto -mx-1">
      <div v-if="loading" class="text-slate-500 text-center py-8">{{ t('common.loading') }}</div>
      <div v-else-if="!list.length" class="text-slate-500 text-center py-8">{{ t('shedding.noEntries') }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500 border-b border-surface-600">
            <th class="pb-2 pr-4">{{ t('feeding.animal') }}</th>
            <th class="pb-2 pr-4">{{ t('shedding.date') }}</th>
            <th class="pb-2 pr-4">{{ t('shedding.pre_shed_days') }}</th>
            <th class="pb-2 pr-4">{{ t('animal.status') }}</th>
            <th class="pb-2 pr-4">{{ t('shedding.notes') }}</th>
            <th class="pb-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in list" :key="s.id" class="table-row">
            <td class="py-2 pr-4 font-medium text-slate-200">{{ s.animal_name }}</td>
            <td class="py-2 pr-4 text-slate-400 whitespace-nowrap">{{ fmtDate(s.date) }}</td>
            <td class="py-2 pr-4 text-slate-400">{{ s.pre_shed_days != null ? `${s.pre_shed_days} ${t('common.days')}` : '—' }}</td>
            <td class="py-2 pr-4">
              <span :class="s.complete ? 'badge-green' : 'badge-yellow'" class="mr-1">
                {{ s.complete ? t('shedding.complete_label') : t('shedding.incomplete_label') }}
              </span>
              <span v-if="!s.in_one_piece" class="badge-red">{{ t('shedding.torn') }}</span>
            </td>
            <td class="py-2 pr-4 text-slate-500 max-w-[150px] truncate">{{ s.notes }}</td>
            <td class="py-2">
              <button @click="deleteShedding(s.id)" class="text-slate-600 hover:text-red-400 transition-colors">🗑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
