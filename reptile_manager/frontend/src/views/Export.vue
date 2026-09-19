<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '@/i18n'
import { animals as animalsApi, exportApi, buildBaseURL } from '@/api'

const { t }  = useI18n()
const route  = useRoute()

const allAnimals      = ref([])
const filteredAnimals = ref([])
const loading         = ref(true)
const genInv          = ref(false)
const genHkn          = ref(false)
const exportError     = ref('')

const selectedIds   = ref([])
const buyer         = ref({ name: '', street: '', zip_city: '', phone: '' })
const originType    = ref('nachzucht')
const citesNr       = ref('')
const einfuhrNr     = ref('')
const sonstigesText = ref('')
const ort           = ref('')
const blanko        = ref(false)
const searchTerm    = ref('')

onMounted(async () => {
  try {
    const res = await animalsApi.list({ active_only: true, limit: 500 })
    allAnimals.value      = res.data
    filteredAnimals.value = res.data
    if (route.query.ids) {
      selectedIds.value = String(route.query.ids).split(',').map(Number).filter(Boolean)
    }
  } finally {
    loading.value = false
  }
})

function applySearch() {
  const q = searchTerm.value.toLowerCase()
  filteredAnimals.value = q
    ? allAnimals.value.filter(a =>
        a.name.toLowerCase().includes(q) ||
        a.species.toLowerCase().includes(q) ||
        (a.morph || '').toLowerCase().includes(q))
    : allAnimals.value
}

function toggleAnimal(id) {
  const i = selectedIds.value.indexOf(id)
  if (i >= 0) selectedIds.value.splice(i, 1)
  else selectedIds.value.push(id)
}

function getDownloadUrl(path) {
  const base  = buildBaseURL().replace(/\/api\/?$/, '/api')
  const token = localStorage.getItem('access_token') || ''
  return `${base}${path}?token=${encodeURIComponent(token)}`
}

async function downloadInventory() {
  genInv.value = true
  const a = document.createElement('a')
  a.href = getDownloadUrl('/export/inventory')
  a.target = '_blank'
  a.rel = 'noopener'
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
  setTimeout(() => { genInv.value = false }, 1500)
}

async function downloadHkn() {
  exportError.value = ''
  if (!selectedIds.value.length) {
    exportError.value = t('export.select_hint')
    return
  }
  genHkn.value = true
  try {
    const res = await exportApi.herkunftsnachweis({
      animal_ids:     selectedIds.value,
      buyer_name:     blanko.value ? '' : buyer.value.name,
      buyer_street:   blanko.value ? '' : buyer.value.street,
      buyer_zip_city: blanko.value ? '' : buyer.value.zip_city,
      buyer_phone:    blanko.value ? '' : buyer.value.phone,
      origin_type:    originType.value,
      cites_nr:       citesNr.value,
      einfuhr_nr:     einfuhrNr.value,
      sonstiges_text: sonstigesText.value,
      ort_datum:      blanko.value ? '' : ort.value,
      blanko:         blanko.value,
    })
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href = url
    a.download = `herkunftsnachweis${blanko.value ? '_blanko' : ''}_${new Date().toISOString().slice(0,10)}.pdf`
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(url), 2000)
  } catch (e) {
    if (e.response?.data instanceof Blob) {
      const text = await e.response.data.text()
      try { exportError.value = JSON.parse(text)?.detail || text } catch { exportError.value = text }
    } else {
      exportError.value = `HTTP ${e.response?.status || 'Network Error'}: ${e.message}`
    }
  } finally { genHkn.value = false }
}


function sexNotation(sex) {
  if (sex === 'male')   return '1.0.0'
  if (sex === 'female') return '0.1.0'
  return '0.0.1'
}

function sexIcon(sex) {
  return sex === 'male' ? '♂' : sex === 'female' ? '♀' : '?'
}
function sexClass(sex) {
  return sex === 'male' ? 'text-blue-400' : sex === 'female' ? 'text-pink-400' : 'text-slate-500'
}
</script>

<template>
  <div class="max-w-4xl">
    <h1 class="text-xl md:text-2xl font-bold text-slate-200 mb-6">📄 {{ t('export.title') }}</h1>

    <!-- ── Bestandsliste / Inventory ──────────────────────────────────── -->
    <div class="card mb-6">
      <h2 class="font-semibold text-slate-200 mb-1">{{ t('export.inventory_title') }}</h2>
      <p class="text-sm text-slate-500 mb-4">{{ t('export.inventory_desc') }}</p>
      <button class="btn-primary" :disabled="genInv" @click="downloadInventory">
        {{ genInv ? t('export.generating') : t('export.inventory_btn') }}
      </button>
    </div>

    <!-- ── Herkunftsnachweis / Origin Certificate ──────────────────── -->
    <div class="card">
      <h2 class="font-semibold text-slate-200 mb-1">{{ t('export.hkn_title') }}</h2>
      <p class="text-sm text-slate-500 mb-5">{{ t('export.hkn_desc') }}</p>

      <div v-if="exportError" class="mb-4 bg-red-900/40 border border-red-700 text-red-300 rounded-lg px-4 py-3 text-sm">
        ⚠ {{ exportError }}
      </div>

      <div class="grid md:grid-cols-2 gap-6">

        <!-- Left: animal selection -->
        <div>
          <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
            {{ t('export.select_animals') }}
          </h3>
          <input v-model="searchTerm" @input="applySearch"
                 :placeholder="t('common.search')" class="mb-3" />
          <div class="max-h-72 overflow-y-auto border border-surface-500 rounded-xl divide-y divide-surface-600">
            <div v-if="loading" class="p-4 text-slate-500 text-sm text-center">{{ t('common.loading') }}</div>
            <div v-for="a in (searchTerm ? filteredAnimals : allAnimals)" :key="a.id"
                 class="flex items-center gap-3 px-3 py-2.5 hover:bg-surface-600 cursor-pointer transition-colors"
                 :class="selectedIds.includes(a.id) ? 'bg-brand-900/30' : ''"
                 @click="toggleAnimal(a.id)">
              <input type="checkbox" :checked="selectedIds.includes(a.id)" class="w-4 h-4 flex-shrink-0" readonly />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5">
                  <span class="text-sm font-medium text-slate-200 truncate">{{ a.name }}</span>
                  <span :class="sexClass(a.sex)" class="text-sm flex-shrink-0">{{ sexNotation(a.sex) }}</span>
                </div>
                <p class="text-xs text-slate-500 italic truncate">{{ a.species }}</p>
              </div>
              <span v-if="a.tracking_id" class="text-xs text-slate-600 flex-shrink-0">#{{ a.tracking_id }}</span>
            </div>
            <div v-if="!loading && allAnimals.length === 0" class="p-4 text-slate-500 text-sm text-center">
              {{ t('animal.noAnimals') }}
            </div>
          </div>
          <p class="text-xs text-slate-600 mt-2">{{ selectedIds.length }} {{ t('export.selected') }}</p>
        </div>

        <!-- Right: options -->
        <div class="space-y-4">

          <!-- Blanko toggle -->
          <label class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-colors"
                 :class="blanko ? 'border-brand-500 bg-brand-900/20' : 'border-surface-500 hover:border-surface-400'">
            <input type="checkbox" v-model="blanko" class="w-4 h-4 flex-shrink-0" />
            <div>
              <div class="text-sm font-medium text-slate-200">{{ t('export.blanko_label') }}</div>
              <div class="text-xs text-slate-500">{{ t('export.blanko_hint') }}</div>
            </div>
          </label>

          <!-- Buyer -->
          <div v-if="!blanko">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
              {{ t('export.buyer') }}
            </h3>
            <div class="space-y-2">
              <input v-model="buyer.name"     :placeholder="t('animal.name')" />
              <input v-model="buyer.street"   :placeholder="t('export.buyer_street')" />
              <input v-model="buyer.zip_city" :placeholder="t('export.buyer_zip')" />
              <input v-model="buyer.phone"    :placeholder="t('export.buyer_phone')" />
            </div>
          </div>

          <!-- Origin -->
          <div>
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
              {{ t('export.origin') }}
            </h3>
            <div class="space-y-2">
              <label v-for="[val, key] in [
                ['bestand',   'export.origins.bestand'],
                ['nachzucht', 'export.origins.nachzucht'],
                ['einfuhr',   'export.origins.einfuhr'],
                ['sonstiges', 'export.origins.sonstiges'],
              ]" :key="val" class="flex items-center gap-2 cursor-pointer text-sm text-slate-300">
                <input type="radio" :value="val" v-model="originType" class="w-4 h-4" />
                {{ t(key) }}
              </label>
              <div v-if="originType === 'einfuhr'" class="grid grid-cols-2 gap-2 mt-2 ml-6">
                <input v-model="citesNr"   :placeholder="t('export.cites_nr')" class="text-sm" />
                <input v-model="einfuhrNr" :placeholder="t('export.einfuhr_nr')" class="text-sm" />
              </div>
              <input v-if="originType === 'sonstiges'" v-model="sonstigesText"
                     :placeholder="t('export.sonstiges_placeholder')" class="ml-6 text-sm" />
            </div>
          </div>

          <!-- Location -->
          <div v-if="!blanko">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-2">
              {{ t('export.location') }}
            </h3>
            <input v-model="ort" :placeholder="t('export.location_placeholder')" />
            <p class="text-xs text-slate-600 mt-1">{{ t('export.location_hint') }}</p>
          </div>
        </div>
      </div>

      <div class="mt-6 pt-4 border-t border-surface-500 flex flex-wrap gap-3 items-center">
        <button class="btn-primary" :disabled="genHkn || !selectedIds.length" @click="downloadHkn">
          {{ genHkn ? t('export.generating') : (blanko ? t('export.blanko_btn') : t('export.generate_btn')) }}
        </button>
        <span class="text-xs text-slate-600">{{ t('export.legal_hint') }}</span>
      </div>
    </div>
  </div>
</template>
