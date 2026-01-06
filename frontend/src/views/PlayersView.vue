<script setup lang="ts">
import PlayerLeaderboard from '@/components/PlayerLeaderboard.vue'
import TeamLeaderboard from '@/components/TeamLeaderboard.vue'
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Leaderboards</h1>
      <p class="text-muted-foreground mt-2">Player and team performance statistics</p>
    </div>

    <PlayerLeaderboard />
    <TeamLeaderboard />
  </div>
</template>
