<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  // [{ t: ms timestamp, v: number }] oldest first
  points: { type: Array, required: true },
  unit: { type: String, default: '' },
  locale: { type: String, default: 'en-GB' },
  height: { type: Number, default: 48 },
})

const LINE = '#4ade80'      // brand-400
const SURFACE = '#1c2230'   // surface-700 (card background)
const W = 200               // viewBox width; the SVG stretches to the container
const PAD = 5               // room for the end marker

const geo = computed(() => {
  const p = props.points
  if (p.length < 2) return null
  const tMin = p[0].t, tMax = Math.max(p[p.length - 1].t, tMin + 86400000)
  let lo = Math.min(...p.map(x => x.v)), hi = Math.max(...p.map(x => x.v))
  if (lo === hi) { lo -= 1; hi += 1 }
  const x = t => PAD + ((t - tMin) / (tMax - tMin)) * (W - 2 * PAD)
  const y = v => PAD + (1 - (v - lo) / (hi - lo)) * (props.height - 2 * PAD)
  const d = p.map((pt, i) => `${i ? 'L' : 'M'}${x(pt.t).toFixed(1)},${y(pt.v).toFixed(1)}`).join('')
  return { x, y, d }
})

const hover = ref(null)
function onMove(ev) {
  const g = geo.value
  if (!g) return
  const rect = ev.currentTarget.getBoundingClientRect()
  const mx = ((ev.clientX - rect.left) / rect.width) * W
  let best = null, bestD = Infinity
  for (const p of props.points) {
    const d = Math.abs(g.x(p.t) - mx)
    if (d < bestD) { bestD = d; best = p }
  }
  hover.value = best
}

const last = computed(() => props.points[props.points.length - 1])
const marker = computed(() => hover.value ?? last.value)
function fmt(p) {
  return `${new Date(p.t).toLocaleDateString(props.locale, { day: '2-digit', month: 'short', year: '2-digit' })} · ${+p.v.toFixed(1)} ${props.unit}`
}
</script>

<template>
  <div class="relative">
    <svg v-if="geo" :viewBox="`0 0 ${W} ${height}`" preserveAspectRatio="none" class="block w-full overflow-visible"
         :style="{ height: height + 'px' }" @mousemove="onMove" @mouseleave="hover = null" role="img" :aria-label="fmt(last)">
      <path :d="geo.d" fill="none" :stroke="LINE" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"
            vector-effect="non-scaling-stroke" />
      <line v-if="hover" :x1="geo.x(hover.t)" :x2="geo.x(hover.t)" y1="0" :y2="height"
            stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3" vector-effect="non-scaling-stroke" />
      <rect x="0" y="0" :width="W" :height="height" fill="transparent" />
    </svg>
    <!-- Marker drawn in HTML so it stays round when the SVG is stretched -->
    <div v-if="geo" class="absolute w-2.5 h-2.5 rounded-full pointer-events-none -translate-x-1/2 -translate-y-1/2"
         :style="{ left: (geo.x(marker.t) / W * 100) + '%', top: geo.y(marker.v) + 'px', background: LINE, boxShadow: `0 0 0 2px ${SURFACE}` }" />
    <div v-if="hover" class="absolute -top-7 right-0 pointer-events-none bg-surface-800 border border-surface-500 rounded px-2 py-0.5 text-xs text-slate-200 whitespace-nowrap">
      {{ fmt(hover) }}
    </div>
    <div v-if="!geo" class="flex items-center text-xs text-slate-600" :style="{ height: height + 'px' }">—</div>
  </div>
</template>
