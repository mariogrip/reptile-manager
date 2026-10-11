<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from '@/i18n'

const props = defineProps({
  // [{ date, [field] }] in any order
  entries: { type: Array, default: () => [] },
  field: { type: String, required: true },  // 'weight_g' | 'length_cm'
  unit: { type: String, required: true },   // 'g' | 'cm'
  ns: { type: String, required: true },     // i18n namespace: 'weight' | 'length'
})

const { t, locale } = useI18n()

const LINE = '#4ade80'      // brand-400
const SURFACE = '#1c2230'   // surface-700 (card background)
const GRID = '#2d3a50'      // surface-500
const AXIS_TEXT = '#64748b' // slate-500
const HEIGHT = 240
const PAD = { top: 28, right: 16, bottom: 28, left: 48 }

const range = ref('all')
const ranges = [
  { id: '3m', months: 3 },
  { id: '6m', months: 6 },
  { id: '1y', months: 12 },
  { id: 'all', months: null },
]

const wrap = ref(null)
const width = ref(600)
let ro
onMounted(() => {
  ro = new ResizeObserver(([e]) => { width.value = Math.max(280, e.contentRect.width) })
  ro.observe(wrap.value)
})
onBeforeUnmount(() => ro?.disconnect())

const sorted = computed(() =>
  props.entries
    .map(e => ({ ...e, t: new Date(e.date).getTime(), v: e[props.field] }))
    .sort((a, b) => a.t - b.t)
)

const points = computed(() => {
  const r = ranges.find(x => x.id === range.value)
  if (!r.months) return sorted.value
  const cutoff = new Date()
  cutoff.setMonth(cutoff.getMonth() - r.months)
  return sorted.value.filter(p => p.t >= cutoff.getTime())
})

const stats = computed(() => {
  const p = points.value
  if (!p.length) return null
  const first = p[0], last = p[p.length - 1]
  const diff = last.v - first.v
  const pct = first.v ? (diff / first.v) * 100 : 0
  const ws = p.map(x => x.v)
  return { current: last.v, diff, pct, first, min: Math.min(...ws), max: Math.max(...ws) }
})

// "Nice" tick step for the y-axis
function niceStep(span, count) {
  const raw = span / count
  const mag = Math.pow(10, Math.floor(Math.log10(raw)))
  const n = raw / mag
  return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * mag
}

const scales = computed(() => {
  const p = points.value
  const innerW = width.value - PAD.left - PAD.right
  const innerH = HEIGHT - PAD.top - PAD.bottom
  if (p.length < 2) return null

  let lo = Math.min(...p.map(x => x.v))
  let hi = Math.max(...p.map(x => x.v))
  if (lo === hi) { lo -= 1; hi += 1 }
  const pad = (hi - lo) * 0.1
  const step = niceStep(hi - lo + 2 * pad, 4)
  const yMin = Math.max(0, Math.floor((lo - pad) / step) * step)
  const yMax = Math.ceil((hi + pad) / step) * step
  const yTicks = []
  for (let v = yMin; v <= yMax + step / 2; v += step) yTicks.push(+v.toFixed(6))

  const tMin = p[0].t, tMax = Math.max(p[p.length - 1].t, tMin + 86400000)
  const x = v => PAD.left + ((v - tMin) / (tMax - tMin)) * innerW
  const y = v => PAD.top + (1 - (v - yMin) / (yMax - yMin)) * innerH

  const nX = Math.max(2, Math.min(6, Math.floor(innerW / 90)))
  const xTicks = Array.from({ length: nX }, (_, i) => tMin + ((tMax - tMin) * i) / (nX - 1))

  return { x, y, yTicks, xTicks, innerW, innerH, tMin, tMax }
})

const path = computed(() => {
  const s = scales.value
  if (!s) return ''
  return points.value.map((p, i) => `${i ? 'L' : 'M'}${s.x(p.t).toFixed(1)},${s.y(p.v).toFixed(1)}`).join('')
})

const spanDays = computed(() => scales.value ? (scales.value.tMax - scales.value.tMin) / 86400000 : 0)
const loc = computed(() => locale.value === 'de' ? 'de-DE' : 'en-GB')
function fmtTick(ts) {
  const opts = spanDays.value > 400 ? { month: 'short', year: '2-digit' } : { day: 'numeric', month: 'short' }
  return new Date(ts).toLocaleDateString(loc.value, opts)
}
function fmtDate(ts) { return new Date(ts).toLocaleDateString(loc.value, { day: '2-digit', month: 'short', year: 'numeric' }) }
function fmtVal(v) { return `${+v.toFixed(1)} ${props.unit}` }

// ── Hover: nearest point by x ────────────────────────────────────────────────
const hover = ref(null)
function onMove(ev) {
  const s = scales.value
  if (!s) return
  const rect = ev.currentTarget.getBoundingClientRect()
  const mx = ((ev.clientX - rect.left) / rect.width) * width.value
  let best = null, bestD = Infinity
  for (const p of points.value) {
    const d = Math.abs(s.x(p.t) - mx)
    if (d < bestD) { bestD = d; best = p }
  }
  hover.value = best
}
const tip = computed(() => {
  const s = scales.value, h = hover.value
  if (!s || !h) return null
  const idx = points.value.indexOf(h)
  const prev = idx > 0 ? points.value[idx - 1] : null
  const px = s.x(h.t)
  return {
    x: px, y: s.y(h.v),
    left: px > width.value / 2,
    date: fmtDate(h.t),
    value: fmtVal(h.v),
    delta: prev ? h.v - prev.v : null,
  }
})
</script>

<template>
  <div class="card mb-4">
    <!-- Range filter + summary -->
    <div class="flex flex-wrap items-start justify-between gap-3 mb-3">
      <div v-if="stats" class="flex flex-wrap gap-x-6 gap-y-1">
        <div>
          <div class="text-xs text-slate-500">{{ t(ns + '.current') }}</div>
          <div class="text-2xl font-bold text-slate-200">{{ fmtVal(stats.current) }}</div>
        </div>
        <div v-if="points.length > 1">
          <div class="text-xs text-slate-500">{{ t(ns + '.change') }} <span class="opacity-70">({{ t(ns + '.since') }} {{ fmtDate(stats.first.t) }})</span></div>
          <div class="text-lg font-semibold text-slate-200 mt-1">
            <span aria-hidden="true">{{ stats.diff > 0 ? '▲' : stats.diff < 0 ? '▼' : '■' }}</span>
            {{ stats.diff > 0 ? '+' : '' }}{{ fmtVal(stats.diff) }}
            <span class="text-sm text-slate-400">({{ stats.pct > 0 ? '+' : '' }}{{ stats.pct.toFixed(1) }}%)</span>
          </div>
        </div>
        <div v-if="points.length > 1">
          <div class="text-xs text-slate-500">{{ t(ns + '.min') }} / {{ t(ns + '.max') }}</div>
          <div class="text-lg font-semibold text-slate-200 mt-1">{{ fmtVal(stats.min) }} / {{ fmtVal(stats.max) }}</div>
        </div>
      </div>
      <div class="flex gap-1 bg-surface-800 rounded-lg p-1 ml-auto" role="group">
        <button v-for="r in ranges" :key="r.id" type="button" @click="range = r.id; hover = null"
          :aria-pressed="range === r.id"
          :class="range === r.id ? 'bg-surface-500 text-slate-200' : 'text-slate-500 hover:text-slate-300'"
          class="px-2.5 py-1 text-xs rounded-md transition-colors">
          {{ t(ns + '.range_' + r.id) }}
        </button>
      </div>
    </div>

    <!-- Chart -->
    <div ref="wrap" class="relative w-full">
      <div v-if="!scales" class="flex items-center justify-center text-sm text-slate-500" :style="{ height: HEIGHT + 'px' }">
        {{ t(ns + '.chartEmpty') }}
      </div>
      <svg v-else :width="width" :height="HEIGHT" :viewBox="`0 0 ${width} ${HEIGHT}`" class="block select-none"
           role="img" :aria-label="t(ns + '.title')"
           @mousemove="onMove" @mouseleave="hover = null"
           @touchstart.passive="e => onMove(e.touches[0] ? { clientX: e.touches[0].clientX, currentTarget: e.currentTarget } : e)"
           @touchmove.passive="e => onMove({ clientX: e.touches[0].clientX, currentTarget: e.currentTarget })">
        <!-- Grid + y labels -->
        <g v-for="v in scales.yTicks" :key="'y' + v">
          <line :x1="PAD.left" :x2="width - PAD.right" :y1="scales.y(v)" :y2="scales.y(v)" :stroke="GRID" stroke-width="1" />
          <text :x="PAD.left - 8" :y="scales.y(v)" text-anchor="end" dominant-baseline="middle" :fill="AXIS_TEXT" font-size="11">{{ +v.toFixed(1) }}</text>
        </g>
        <text :x="PAD.left - 8" :y="PAD.top - 16" text-anchor="end" :fill="AXIS_TEXT" font-size="10">{{ unit }}</text>
        <!-- X labels -->
        <text v-for="(ts, i) in scales.xTicks" :key="'x' + i"
              :x="scales.x(ts)" :y="HEIGHT - 8" :fill="AXIS_TEXT" font-size="11"
              :text-anchor="i === 0 ? 'start' : i === scales.xTicks.length - 1 ? 'end' : 'middle'">{{ fmtTick(ts) }}</text>

        <!-- Line -->
        <path :d="path" fill="none" :stroke="LINE" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />

        <!-- Markers (only when sparse enough to read) -->
        <template v-if="points.length <= 60">
          <circle v-for="p in points" :key="p.id ?? p.t" :cx="scales.x(p.t)" :cy="scales.y(p.v)" r="4"
                  :fill="LINE" :stroke="SURFACE" stroke-width="2" />
        </template>

        <!-- Crosshair -->
        <g v-if="tip" pointer-events="none">
          <line :x1="tip.x" :x2="tip.x" :y1="PAD.top" :y2="HEIGHT - PAD.bottom" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3" />
          <circle :cx="tip.x" :cy="tip.y" r="5" :fill="LINE" :stroke="SURFACE" stroke-width="2" />
        </g>

        <!-- Hit area -->
        <rect :x="PAD.left" :y="PAD.top" :width="scales.innerW" :height="scales.innerH" fill="transparent" />
      </svg>

      <!-- Tooltip -->
      <div v-if="tip"
           class="absolute pointer-events-none bg-surface-800 border border-surface-500 rounded-lg px-3 py-2 text-xs shadow-lg whitespace-nowrap"
           :style="{ top: Math.max(0, tip.y - 56) + 'px', left: tip.left ? 'auto' : (tip.x + 12) + 'px', right: tip.left ? (width - tip.x + 12) + 'px' : 'auto' }">
        <div class="text-slate-400">{{ tip.date }}</div>
        <div class="text-slate-200 font-semibold text-sm">{{ tip.value }}</div>
        <div v-if="tip.delta !== null" class="text-slate-400">
          {{ tip.delta > 0 ? '▲ +' : tip.delta < 0 ? '▼ ' : '■ ' }}{{ fmtVal(tip.delta) }}
        </div>
      </div>
    </div>
  </div>
</template>
