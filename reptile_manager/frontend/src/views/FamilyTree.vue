<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { animals as animalsApi } from '@/api'
import { useI18n } from '@/i18n'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const treeData = ref(null)
const loading = ref(true)

onMounted(async () => {
  const res = await animalsApi.tree(route.params.id)
  treeData.value = res.data
  loading.value = false
})

function sexIcon(sex) {
  return sex === 'male' ? '1.0.0' : sex === 'female' ? '0.1.0' : '?'
}
function sexClass(sex) {
  return sex === 'male' ? 'text-blue-400' : sex === 'female' ? 'text-pink-400' : 'text-slate-500'
}

function hasParents(node) {
  return node?.mother || node?.father
}
</script>

<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">{{ t('common.back') }}</button>
      <h1 class="text-2xl font-bold text-slate-200">{{ t('tree.title') }}</h1>
    </div>

    <div v-if="loading" class="text-slate-500 text-center py-16">{{ t('common.loading') }}</div>

    <div v-else-if="treeData" class="overflow-x-auto pb-6">

      <!-- Legend -->
      <div class="flex gap-4 mb-6 text-xs text-slate-500">
        <span class="flex items-center gap-1"><span class="font-mono text-xs text-slate-400">0.1.0</span></span>
        <span class="flex items-center gap-1"><span class="font-mono text-xs text-slate-400">1.0.0</span></span>
        <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-brand-500 inline-block"></span> {{ t('tree.selected') }}</span>
      </div>

      <!-- Tree structure -->
      <div class="flex flex-col items-center">

        <!-- Grandparents row -->
        <div v-if="hasParents(treeData.animal.mother) || hasParents(treeData.animal.father)" class="flex gap-24 mb-2">
          <!-- Maternal grandparents -->
          <div class="flex gap-8">
            <div v-if="treeData.animal.mother?.mother" class="tree-node bg-surface-700">
              <div class="flex items-center gap-1">
                <span :class="sexClass(treeData.animal.mother.mother.sex)" class="font-bold">{{ sexIcon(treeData.animal.mother.mother.sex) }}</span>
                <span class="font-medium text-slate-200">{{ treeData.animal.mother.mother.name }}</span>
              </div>
              <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ treeData.animal.mother.mother.morph ?? treeData.animal.mother.mother.species }}</span>
            </div>
            <div v-else class="tree-node-empty"></div>
            <div v-if="treeData.animal.mother?.father" class="tree-node bg-surface-700">
              <div class="flex items-center gap-1">
                <span :class="sexClass(treeData.animal.mother.father.sex)" class="font-bold">{{ sexIcon(treeData.animal.mother.father.sex) }}</span>
                <span class="font-medium text-slate-200">{{ treeData.animal.mother.father.name }}</span>
              </div>
              <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ treeData.animal.mother.father.morph ?? treeData.animal.mother.father.species }}</span>
            </div>
            <div v-else class="tree-node-empty"></div>
          </div>
          <!-- Paternal grandparents -->
          <div class="flex gap-8">
            <div v-if="treeData.animal.father?.mother" class="tree-node bg-surface-700">
              <div class="flex items-center gap-1">
                <span :class="sexClass(treeData.animal.father.mother.sex)" class="font-bold">{{ sexIcon(treeData.animal.father.mother.sex) }}</span>
                <span class="font-medium text-slate-200">{{ treeData.animal.father.mother.name }}</span>
              </div>
              <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ treeData.animal.father.mother.morph ?? treeData.animal.father.mother.species }}</span>
            </div>
            <div v-else class="tree-node-empty"></div>
            <div v-if="treeData.animal.father?.father" class="tree-node bg-surface-700">
              <div class="flex items-center gap-1">
                <span :class="sexClass(treeData.animal.father.father.sex)" class="font-bold">{{ sexIcon(treeData.animal.father.father.sex) }}</span>
                <span class="font-medium text-slate-200">{{ treeData.animal.father.father.name }}</span>
              </div>
              <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ treeData.animal.father.father.morph ?? treeData.animal.father.father.species }}</span>
            </div>
            <div v-else class="tree-node-empty"></div>
          </div>
        </div>

        <!-- Connector line to parents -->
        <div v-if="treeData.animal.mother || treeData.animal.father"
             class="w-px h-6 bg-surface-500 mb-0"></div>

        <!-- Parents row -->
        <div v-if="treeData.animal.mother || treeData.animal.father"
             class="flex gap-16 mb-0 relative">
          <div class="absolute top-1/2 left-0 right-0 h-px bg-surface-500 -translate-y-1/2"></div>

          <div v-if="treeData.animal.mother"
               class="tree-node bg-surface-700 cursor-pointer hover:border-pink-400 z-10"
               @click="router.push(`/animals/${treeData.animal.mother.id}`)">
            <div class="flex items-center gap-1">
              <span class="text-pink-400 font-bold">♀</span>
              <span class="font-medium text-slate-200">{{ treeData.animal.mother.name }}</span>
            </div>
            <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ treeData.animal.mother.morph ?? treeData.animal.mother.species }}</span>
          </div>
          <div v-else class="tree-node-empty z-10"></div>

          <div v-if="treeData.animal.father"
               class="tree-node bg-surface-700 cursor-pointer hover:border-blue-400 z-10"
               @click="router.push(`/animals/${treeData.animal.father.id}`)">
            <div class="flex items-center gap-1">
              <span class="text-blue-400 font-bold">♂</span>
              <span class="font-medium text-slate-200">{{ treeData.animal.father.name }}</span>
            </div>
            <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ treeData.animal.father.morph ?? treeData.animal.father.species }}</span>
          </div>
          <div v-else class="tree-node-empty z-10"></div>
        </div>

        <!-- Connector to subject -->
        <div class="w-px h-6 bg-surface-500"></div>

        <!-- Subject (this animal) -->
        <div class="tree-node !border-brand-500 !bg-brand-500/10 !border-2 min-w-[180px]">
          <div class="flex items-center gap-1">
            <span :class="sexClass(treeData.animal.sex)" class="font-bold text-lg">{{ sexIcon(treeData.animal.sex) }}</span>
            <span class="font-bold text-slate-100 text-lg">{{ treeData.animal.name }}</span>
          </div>
          <span class="text-xs text-brand-400 italic">{{ treeData.animal.morph ?? treeData.animal.species }}</span>
        </div>

        <!-- Offspring -->
        <template v-if="treeData.offspring.length">
          <div class="w-px h-6 bg-surface-500"></div>
          <div class="text-xs text-slate-500 mb-2">{{ t('tree.offspring') }} ({{ treeData.offspring.length }})</div>
          <div class="flex flex-wrap gap-3 justify-center max-w-2xl">
            <div
              v-for="child in treeData.offspring" :key="child.id"
              class="tree-node bg-surface-700 cursor-pointer hover:border-brand-500"
              @click="router.push(`/animals/${child.id}`)"
            >
              <div class="flex items-center gap-1">
                <span :class="sexClass(child.sex)" class="font-bold">{{ sexIcon(child.sex) }}</span>
                <span class="font-medium text-slate-200">{{ child.name }}</span>
              </div>
              <span class="text-xs text-slate-500 italic truncate max-w-[120px]">{{ child.morph ?? child.species }}</span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tree-node {
  @apply flex flex-col px-3 py-2 rounded-lg border border-surface-500 transition-colors min-w-[130px];
}
.tree-node-empty {
  @apply w-[130px] min-w-[130px];
}
</style>
