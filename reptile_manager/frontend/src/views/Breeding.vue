<script setup>
import { ref, onMounted } from 'vue'
import { breeding as breedingApi, animals as animalsApi } from '@/api'
import { bulk } from '@/api'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const list = ref([])
const allAnimals = ref([])
const loading = ref(true)
const showForm = ref(false)
const saving = ref(false)
const editId = ref(null)
const form = ref({
  female_id: '', male_id: '',
  date_paired: '', date_separated: '',
  copulation_observed: false,
  date_eggs_or_birth: '',
  clutch_size: '', fertile_count: '',
  success: null, notes: ''
})

onMounted(async () => {
  const [bRes, aRes] = await Promise.all([
    breedingApi.list({ limit: 200 }),
    animalsApi.list({ active_only: false, limit: 500 })
  ])
  list.value = bRes.data
  allAnimals.value = aRes.data
  loading.value = false
})

function resetForm() {
  form.value = { female_id: '', male_id: '', date_paired: '', date_separated: '', copulation_observed: false, date_eggs_or_birth: '', clutch_size: '', fertile_count: '', success: null, notes: '' }
  editId.value = null
  showForm.value = false
}

async function save() {
  saving.value = true
  try {
    const payload = { ...form.value, female_id: parseInt(form.value.female_id), male_id: parseInt(form.value.male_id) }
    if (!payload.date_paired) payload.date_paired = null
    if (!payload.date_separated) payload.date_separated = null
    if (!payload.date_eggs_or_birth) payload.date_eggs_or_birth = null
    if (!payload.clutch_size) payload.clutch_size = null
    if (!payload.fertile_count) payload.fertile_count = null

    if (editId.value) {
      const res = await breedingApi.update(editId.value, payload)
      const idx = list.value.findIndex(e => e.id === editId.value)
      if (idx !== -1) list.value[idx] = res.data
    } else {
      const res = await breedingApi.create(payload)
      list.value.unshift(res.data)
    }
    resetForm()
  } finally {
    saving.value = false
  }
}

function edit(event) {
  editId.value = event.id
  form.value = {
    female_id: event.female_id,
    male_id: event.male_id,
    date_paired: event.date_paired ?? '',
    date_separated: event.date_separated ?? '',
    copulation_observed: event.copulation_observed,
    date_eggs_or_birth: event.date_eggs_or_birth ?? '',
    clutch_size: event.clutch_size ?? '',
    fertile_count: event.fertile_count ?? '',
    success: event.success,
    notes: event.notes ?? ''
  }
  showForm.value = true
}

async function remove(id) {
  if (!confirm(t('breeding.confirmDelete'))) return
  await breedingApi.delete(id)
  list.value = list.value.filter(e => e.id !== id)
}

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('de-DE') : '—' }

// Bulk offspring
const showBulkModal  = ref(false)
const bulkEvent      = ref(null)
const bulkQty        = ref(1)
const bulkDob        = ref(new Date().toISOString().slice(0, 10))
const bulkSex        = ref('unknown')
const bulkNotes      = ref('')
const savingBulk     = ref(false)

function openBulk(event) {
  bulkEvent.value = event
  showBulkModal.value = true
  bulkQty.value = 1
  bulkDob.value = new Date().toISOString().slice(0, 10)
  bulkSex.value = 'unknown'
  bulkNotes.value = ''
}

async function createBulk() {
  if (!bulkEvent.value) return
  savingBulk.value = true
  try {
    const ev = bulkEvent.value
    await bulk.createAnimals(bulkQty.value, {
      name: `${ev.female.species} NZ ${new Date().getFullYear()}`,
      species: ev.female.species,
      common_name: ev.female.common_name || null,
      sex: bulkSex.value,
      date_of_birth: bulkDob.value || null,
      origin: 'captive bred',
      mother_id: ev.female_id,
      father_id: ev.male_id,
      notes: bulkNotes.value || null,
      status: 'active',
    })
    showBulkModal.value = false
    alert(`${bulkQty.value} ${t('breeding.bulkSuccess')}`)
  } catch (e) {
    alert(t('common.error') + ': ' + (e.response?.data?.detail || e.message))
  } finally {
    savingBulk.value = false
  }
}
const males   = () => allAnimals.value.filter(a => a.sex !== 'female')
const females = () => allAnimals.value.filter(a => a.sex !== 'male')
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-slate-200">{{ t('breeding.title') }}</h1>
      <button class="btn-primary btn-sm" @click="showForm = !showForm; if(!showForm) resetForm()">
        {{ showForm ? t('common.cancel') : '+ ' + t('breeding.add') }}
      </button>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="card mb-6">
      <h3 class="font-medium text-slate-200 mb-4">{{ editId ? t('common.edit') + ' ' + t('breeding.add') : t('breeding.add') }}</h3>
      <form @submit.prevent="save" class="grid sm:grid-cols-2 gap-4">
        <div>
          <label>{{ t('breeding.female') }} *</label>
          <select v-model="form.female_id" required>
            <option value="">{{ t('common.choose') }}</option>
            <option v-for="a in females()" :key="a.id" :value="a.id">{{ a.name }} – {{ a.morph ?? a.species }}</option>
          </select>
        </div>
        <div>
          <label>{{ t('breeding.male') }} *</label>
          <select v-model="form.male_id" required>
            <option value="">{{ t('common.choose') }}</option>
            <option v-for="a in males()" :key="a.id" :value="a.id">{{ a.name }} – {{ a.morph ?? a.species }}</option>
          </select>
        </div>
        <div><label>{{ t('breeding.paired') }}</label><input type="date" v-model="form.date_paired" /></div>
        <div><label>{{ t('breeding.separated') }}</label><input type="date" v-model="form.date_separated" /></div>
        <div class="flex items-end pb-2">
          <label class="flex items-center gap-2 cursor-pointer text-sm">
            <input type="checkbox" v-model="form.copulation_observed" class="w-4 h-4" />
            {{ t('breeding.copulation') }}
          </label>
        </div>
        <div><label>{{ t('breeding.birth') }}</label><input type="date" v-model="form.date_eggs_or_birth" /></div>
        <div><label>{{ t('breeding.clutch_size') }}</label><input type="number" v-model="form.clutch_size" min="0" placeholder="8" /></div>
        <div><label>{{ t('breeding.fertile') }}</label><input type="number" v-model="form.fertile_count" min="0" /></div>
        <div>
          <label>{{ t('breeding.success') }}</label>
          <select v-model="form.success">
            <option :value="null">{{ t('breeding.successLabels.null') }}</option>
            <option :value="true">{{ t('breeding.successLabels.true') }}</option>
            <option :value="false">{{ t('breeding.successLabels.false') }}</option>
          </select>
        </div>
        <div class="sm:col-span-2"><label>{{ t('breeding.notes') }}</label><textarea v-model="form.notes" rows="2" /></div>
        <div class="sm:col-span-2 flex gap-2">
          <button type="submit" class="btn-primary btn-sm" :disabled="saving">
            {{ saving ? t('common.saving') : editId ? t('common.save') : t('breeding.add') }}
          </button>
          <button type="button" class="btn-secondary btn-sm" @click="resetForm">{{ t('common.cancel') }}</button>
        </div>
      </form>
    </div>

    <!-- List -->
    <div v-if="loading" class="text-slate-500 text-center py-16">{{ t('common.loading') }}</div>
    <div v-else-if="!list.length" class="text-center py-16 text-slate-500">
      <div class="text-4xl mb-3">🥚</div>
      <p>{{ t('breeding.noEntries') }}</p>
    </div>
    <div v-else class="space-y-3">
      <div v-for="e in list" :key="e.id" class="card">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex items-center gap-3 flex-wrap">
              <span class="font-semibold text-slate-200">
                <span class="text-slate-300"><span class="text-slate-500 font-mono text-xs">0.1.0</span> {{ e.female.name }}</span>
                <span class="text-slate-500 mx-2">×</span>
                <span class="text-slate-300"><span class="text-slate-500 font-mono text-xs">1.0.0</span> {{ e.male.name }}</span>
              </span>
              <span v-if="e.success === true" class="badge-green">{{ t('breeding.successLabels.true') }}</span>
              <span v-else-if="e.success === false" class="badge-red">{{ t('breeding.successLabels.false') }}</span>
              <span v-else class="badge-gray">{{ t('breeding.successLabels.null') }}</span>
            </div>
            <div class="text-xs text-slate-500 mt-1 flex flex-wrap gap-3">
              <span v-if="e.female.morph" class="text-pink-300/60">{{ e.female.morph }}</span>
              <span v-if="e.male.morph" class="text-blue-300/60">{{ e.male.morph }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button class="btn-secondary btn-sm text-xs" @click="openBulk(e)" :title="t('breeding.addOffspring')">🐣</button>
            <button class="btn-secondary btn-sm text-xs" @click="edit(e)">✏️</button>
            <button class="btn-danger btn-sm text-xs" @click="remove(e.id)">🗑</button>
          </div>
        </div>

        <div class="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <span class="text-slate-500">{{ t('breeding.paired') }}</span>
            <div class="text-slate-300">{{ fmtDate(e.date_paired) }}</div>
          </div>
          <div>
            <span class="text-slate-500">{{ t('breeding.separated') }}</span>
            <div class="text-slate-300">{{ fmtDate(e.date_separated) }}</div>
          </div>
          <div>
            <span class="text-slate-500">{{ t('breeding.birth') }}</span>
            <div class="text-slate-300">{{ fmtDate(e.date_eggs_or_birth) }}</div>
          </div>
          <div>
            <span class="text-slate-500">{{ t('breeding.birth') }}</span>
            <div class="text-slate-300">
              {{ e.clutch_size != null ? e.clutch_size : '—' }}
              <span v-if="e.fertile_count != null"> ({{ e.fertile_count }} {{ t('breeding.fertile').toLowerCase() }})</span>
            </div>
          </div>
        </div>
        <div v-if="e.notes" class="mt-2 text-xs text-slate-500">{{ e.notes }}</div>
      </div>
    </div>

    <!-- Bulk offspring modal -->
    <Teleport to="body">
      <div v-if="showBulkModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/70" @click="showBulkModal = false" />
        <div class="relative bg-surface-700 rounded-2xl border border-surface-500 w-full max-w-md shadow-2xl p-6">
          <h2 class="font-semibold text-slate-200 mb-4">
            🐣 {{ t('breeding.addOffspring') }}
            <span v-if="bulkEvent" class="text-sm text-slate-400 font-normal ml-1">
              — {{ bulkEvent.female.species }}
            </span>
          </h2>
          <div class="space-y-4">
            <div>
              <label>{{ t('breeding.quantity') }}</label>
              <input type="number" v-model.number="bulkQty" min="1" max="500" />
              <p class="text-xs text-slate-500 mt-1">{{ t('breeding.bulkHint') }}</p>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div><label>{{ t('animal.dob') }}</label><input type="date" v-model="bulkDob" /></div>
              <div>
                <label>{{ t('animal.sex') }}</label>
                <select v-model="bulkSex">
                  <option value="unknown">{{ t('animal.sexes.unknown') }}</option>
                  <option value="male">{{ t('animal.sexes.male') }}</option>
                  <option value="female">{{ t('animal.sexes.female') }}</option>
                </select>
              </div>
            </div>
            <div>
              <label>{{ t('breeding.notes') }}</label>
              <textarea v-model="bulkNotes" rows="2" :placeholder="t('breeding.notes_placeholder')" />
            </div>
            <div class="flex gap-3">
              <button class="btn-primary flex-1" :disabled="savingBulk" @click="createBulk">
                {{ savingBulk ? t('common.saving') : `${bulkQty} ${t('breeding.bulkCreate')}` }}
              </button>
              <button class="btn-secondary" @click="showBulkModal = false">{{ t('common.cancel') }}</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
