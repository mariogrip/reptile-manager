<script setup>
import { ref } from 'vue'
import { useI18n, fmtDateTime } from '@/i18n'
import MeasurementChart from '@/components/MeasurementChart.vue'

const props = defineProps({
  animalId: { type: [Number, String], required: true },
  entries: { type: Array, required: true },  // newest first
  api: { type: Object, required: true },     // { create, delete }
  field: { type: String, required: true },   // 'weight_g' | 'length_cm'
  unit: { type: String, required: true },    // 'g' | 'cm'
  ns: { type: String, required: true },      // i18n namespace: 'weight' | 'length'
})
const emit = defineEmits(['update:entries'])

const { t } = useI18n()

const emptyForm = () => ({ date: new Date().toISOString().slice(0,16), value: '', notes: '' })
const form = ref(emptyForm())
const showForm = ref(false)
const saving = ref(false)

const byDateDesc = (a, b) => new Date(b.date) - new Date(a.date)


async function add() {
  saving.value = true
  try {
    const res = await props.api.create({
      animal_id: parseInt(props.animalId),
      date: form.value.date,
      notes: form.value.notes,
      [props.field]: parseFloat(form.value.value),
    })
    emit('update:entries', [res.data, ...props.entries].sort(byDateDesc))
    showForm.value = false
    form.value = emptyForm()
  } finally {
    saving.value = false
  }
}

async function remove(id) {
  if (!confirm(t(props.ns + '.confirmDelete'))) return
  await props.api.delete(id)
  emit('update:entries', props.entries.filter(e => e.id !== id))
}

// Change vs. the previous (older) entry; list is sorted newest first
function delta(i) {
  const next = props.entries[i + 1]
  return next ? props.entries[i][props.field] - next[props.field] : null
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-3">
      <span class="text-sm text-slate-500">{{ entries.length }} {{ t('common.entries') }}</span>
      <button class="btn-primary btn-sm" @click="showForm = !showForm">+ {{ t(ns + '.add') }}</button>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="card mb-4">
      <h3 class="font-medium text-slate-200 mb-3">{{ t(ns + '.add') }}</h3>
      <form @submit.prevent="add" class="grid sm:grid-cols-2 gap-3">
        <div><label>{{ t(ns + '.date') }}</label><input type="datetime-local" v-model="form.date" required /></div>
        <div><label>{{ t(ns + '.value') }}</label><input type="number" v-model="form.value" step="0.1" min="0.1" required autofocus /></div>
        <div class="sm:col-span-2"><label>{{ t(ns + '.notes') }}</label><textarea v-model="form.notes" rows="2" /></div>
        <div class="sm:col-span-2 flex gap-2">
          <button type="submit" class="btn-primary btn-sm" :disabled="saving">
            {{ saving ? t('common.saving') : t('common.save') }}
          </button>
          <button type="button" class="btn-secondary btn-sm" @click="showForm = false">{{ t('common.cancel') }}</button>
        </div>
      </form>
    </div>

    <MeasurementChart v-if="entries.length" :entries="entries" :field="field" :unit="unit" :ns="ns" />

    <!-- List -->
    <div class="card">
      <div v-if="!entries.length" class="text-slate-500 text-center py-8">{{ t(ns + '.noEntries') }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-left text-slate-500 border-b border-surface-600">
            <th class="pb-2 pr-4">{{ t(ns + '.date') }}</th>
            <th class="pb-2 pr-4">{{ t(ns + '.value') }}</th>
            <th class="pb-2 pr-4">{{ t(ns + '.change') }}</th>
            <th class="pb-2 pr-4">{{ t(ns + '.notes') }}</th>
            <th class="pb-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(e, i) in entries" :key="e.id" class="table-row">
            <td class="py-2 pr-4 whitespace-nowrap text-slate-400">{{ fmtDateTime(e.date) }}</td>
            <td class="py-2 pr-4 text-slate-200">{{ e[field] }} {{ unit }}</td>
            <td class="py-2 pr-4 text-slate-400 whitespace-nowrap">
              <template v-if="delta(i) !== null">
                {{ delta(i) > 0 ? '▲ +' : delta(i) < 0 ? '▼ ' : '■ ' }}{{ +delta(i).toFixed(1) }} {{ unit }}
              </template>
              <template v-else>—</template>
            </td>
            <td class="py-2 pr-4 text-slate-500 max-w-[150px] truncate">{{ e.notes }}</td>
            <td class="py-2">
              <button @click="remove(e.id)" class="text-slate-600 hover:text-red-400 transition-colors">🗑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
