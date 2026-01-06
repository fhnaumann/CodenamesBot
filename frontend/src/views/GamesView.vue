<script setup lang="ts">
import GameLog from '@/components/GameLog.vue'
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Game History</h1>
      <p class="text-muted-foreground mt-2">All games played with team compositions and results</p>
    </div>

    <GameLog />
  </div>
</template>
