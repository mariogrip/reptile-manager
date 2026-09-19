<script setup>
import { useI18n } from '@/i18n'
import { ref, onMounted } from 'vue'
import { dashboard } from '@/api'
import { useRouter } from 'vue-router'
import { mediaUrl } from '@/utils/media'

const { t } = useI18n()

const router = useRouter()
const stats = ref(null)
const loading = ref(true)
const showFeedingModal = ref(false)

onMounted(async () => {
  try {
    const res = await dashboard.stats()
    stats.value = res.data
  } finally {
    loading.value = false
  }
})

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function fmtDateTime(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function foodLabel(f) {
  return [f.food_count > 1 ? `${f.food_count}×` : '', f.food_size, f.food_type].filter(Boolean).join(' ')
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
  <div>
    <h1 class="text-xl md:text-2xl font-bold text-slate-200 mb-5">{{ t('dashboard.title') }}</h1>

    <div v-if="loading" class="text-slate-500 text-center py-16">{{ t('common.loading') }}</div>

    <template v-else-if="stats">
      <!-- Stat cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <div class="stat-card cursor-pointer hover:border-brand-500 border border-surface-600 transition-colors"
             @click="router.push('/animals')">
          <span class="text-2xl">🦎</span>
          <span class="text-2xl md:text-3xl font-bold text-slate-200">{{ stats.active_animals }}</span>
          <span class="text-xs text-slate-500">{{ t('dashboard.active_animals') }}</span>
        </div>

        <div class="stat-card cursor-pointer hover:border-brand-500 border border-surface-600 transition-colors"
             @click="router.push('/feedings')">
          <span class="text-2xl">🍖</span>
          <span class="text-2xl md:text-3xl font-bold text-slate-200">{{ stats.feedings_this_month }}</span>
          <span class="text-xs text-slate-500">{{ t('dashboard.feedings_month') }}</span>
        </div>

        <div class="stat-card cursor-pointer hover:border-brand-500 border border-surface-600 transition-colors"
             @click="router.push('/sheddings')">
          <span class="text-2xl">🐚</span>
          <span class="text-2xl md:text-3xl font-bold text-slate-200">{{ stats.sheddings_this_month }}</span>
          <span class="text-xs text-slate-500">{{ t('dashboard.sheddings_month') }}</span>
        </div>

        <!-- Clickable warning card -->
        <div class="stat-card cursor-pointer border transition-colors"
             :class="stats.animals_not_fed_7days > 0
               ? 'border-yellow-600 hover:border-yellow-400 bg-yellow-900/20'
               : 'border-surface-600 hover:border-brand-500'"
             @click="stats.animals_not_fed_7days > 0 && (showFeedingModal = true)">
          <span class="text-2xl">{{ stats.animals_not_fed_7days > 0 ? '⚠️' : '✅' }}</span>
          <span class="text-2xl md:text-3xl font-bold"
                :class="stats.animals_not_fed_7days > 0 ? 'text-yellow-400' : 'text-slate-200'">
            {{ stats.animals_not_fed_7days }}
          </span>
          <span class="text-xs text-slate-500">
            {{ stats.animals_not_fed_7days > 0 ? t('dashboard.not_fed') + ' — ' + t('dashboard.click_for_details') : t('dashboard.all_fed') }}
          </span>
        </div>
      </div>

      <!-- Recent activity -->
      <div class="grid md:grid-cols-2 gap-4">
        <!-- Recent feedings -->
        <div class="card">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-semibold text-slate-200 text-sm md:text-base">{{ t('dashboard.recent_feedings') }}</h2>
            <button class="text-xs text-brand-400 hover:text-brand-500" @click="router.push('/feedings')">{{ t('common.all') }} →</button>
          </div>
          <div v-if="!stats.recent_feedings.length" class="text-slate-500 text-sm">{{ t('feeding.noEntries') }}</div>
          <div v-for="f in stats.recent_feedings" :key="f.id"
               class="flex items-center gap-2 py-2 border-b border-surface-600 last:border-0">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="text-sm font-medium text-slate-200 truncate">{{ f.animal_name }}</span>
                <span :class="f.accepted ? 'badge-green' : 'badge-red'" class="text-xs">
                  {{ f.accepted ? t('feeding.accepted_label') : t('feeding.rejected_label') }}
                </span>
              </div>
              <span class="text-xs text-slate-500">{{ foodLabel(f) }} · {{ fmtDate(f.date) }}</span>
            </div>
          </div>
        </div>

        <!-- Recent sheddings -->
        <div class="card">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-semibold text-slate-200 text-sm md:text-base">{{ t('dashboard.recent_sheddings') }}</h2>
            <button class="text-xs text-brand-400 hover:text-brand-500" @click="router.push('/sheddings')">{{ t('common.all') }} →</button>
          </div>
          <div v-if="!stats.recent_sheddings.length" class="text-slate-500 text-sm">{{ t('shedding.noEntries') }}</div>
          <div v-for="s in stats.recent_sheddings" :key="s.id"
               class="flex items-center gap-2 py-2 border-b border-surface-600 last:border-0">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="text-sm font-medium text-slate-200 truncate">{{ s.animal_name }}</span>
                <span :class="s.complete ? 'badge-green' : 'badge-yellow'" class="text-xs">
                  {{ s.complete ? t('shedding.complete_label') : t('shedding.incomplete_label') }}
                </span>
              </div>
              <span class="text-xs text-slate-500">{{ fmtDate(s.date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Feeding Alert Modal ─────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showFeedingModal"
             class="fixed inset-0 z-50 flex items-end md:items-center justify-center p-4"
             @click.self="showFeedingModal = false">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-black/70" @click="showFeedingModal = false" />

          <!-- Modal -->
          <div class="relative bg-surface-700 rounded-2xl border border-yellow-700 w-full max-w-md
                      max-h-[80vh] flex flex-col shadow-2xl">
            <!-- Header -->
            <div class="flex items-center justify-between p-5 border-b border-surface-600">
              <div class="flex items-center gap-2">
                <span class="text-xl">⚠️</span>
                <h2 class="font-semibold text-slate-200">{{ t('dashboard.feeding_modal_title') }}</h2>
              </div>
              <button @click="showFeedingModal = false"
                      class="text-slate-500 hover:text-slate-200 text-xl w-8 h-8 flex items-center justify-center">
                ✕
              </button>
            </div>

            <!-- Animal list -->
            <div class="overflow-y-auto flex-1 p-2">
              <div v-for="a in stats?.animals_needing_feeding" :key="a.id"
                   class="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-600 cursor-pointer transition-colors"
                   @click="showFeedingModal = false; router.push(`/animals/${a.id}`)">
                <!-- Avatar -->
                <div class="w-12 h-12 rounded-xl bg-surface-600 flex-shrink-0 overflow-hidden
                            flex items-center justify-center border border-surface-500">
                  <img v-if="a.photo_url" :src="mediaUrl(a.photo_url)" :alt="a.name"
                       class="w-full h-full object-cover" />
                  <span v-else class="text-2xl opacity-40">🦎</span>
                </div>

                <!-- Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-1.5">
                    <span class="font-medium text-slate-200 truncate">{{ a.name }}</span>
                    <span :class="sexClass(a.sex)" class="text-sm font-bold flex-shrink-0">
                      {{ sexNotation(a.sex) }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-500 italic truncate">{{ a.species }}</p>
                  <p v-if="a.morph" class="text-xs text-brand-400 truncate">{{ a.morph }}</p>
                </div>

                <!-- Days indicator -->
                <div class="flex-shrink-0 text-right">
                  <div class="text-lg font-bold text-yellow-400">
                    {{ a.days_since_feeding !== null && a.days_since_feeding !== undefined
                       ? a.days_since_feeding + 'd'
                       : '—' }}
                  </div>
                  <div class="text-xs text-slate-500">{{ t('dashboard.days_no_food') }}</div>
                  <div class="text-xs text-slate-600">{{ t('dashboard.threshold') }}: {{ a.threshold_days }}d</div>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="p-4 border-t border-surface-600">
              <button class="btn-primary w-full justify-center"
                      @click="showFeedingModal = false; router.push('/feedings')">
                {{ t('dashboard.to_feedings') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
