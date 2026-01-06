<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

const totalGames = ref(0)
const loading = ref(true)

onMounted(async () => {
  try {
    const result = await api.getTotalGames()
    totalGames.value = result.total_games
  } catch (e) {
    console.error('Failed to load total games:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-4xl font-bold tracking-tight">Codenames Statistics</h1>
      <p class="text-muted-foreground mt-2">
        Track your game history, player performance, and team combinations
      </p>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total Games</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="loading">
            <Skeleton class="h-8 w-16 mb-1" />
            <Skeleton class="h-4 w-24" />
          </div>
          <div v-else>
            <div class="text-2xl font-bold">{{ totalGames }}</div>
            <p class="text-xs text-muted-foreground">Games played</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Game Log</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm text-muted-foreground">View all game history with teams and roles</p>
          <router-link to="/games" class="text-sm text-primary hover:underline mt-2 inline-block">
            View Games →
          </router-link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Player Stats</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm text-muted-foreground">Check player rankings and performance</p>
          <router-link
            to="/players"
            class="text-sm text-primary hover:underline mt-2 inline-block"
          >
            View Leaderboard →
          </router-link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Custom Query</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-sm text-muted-foreground">Filter games by players and roles</p>
          <router-link to="/query" class="text-sm text-primary hover:underline mt-2 inline-block">
            Run Query →
          </router-link>
        </CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Welcome to Codenames Stats</CardTitle>
        <CardDescription>Your comprehensive game tracking dashboard</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <p>
          This dashboard helps you track and analyze your Codenames games. Here's what you can do:
        </p>
        <ul class="list-disc list-inside space-y-2 text-sm text-muted-foreground">
          <li>
            <strong>Game Log:</strong> View all games with detailed team compositions and outcomes
          </li>
          <li>
            <strong>Player Leaderboard:</strong> See overall and role-specific statistics for all
            players
          </li>
          <li>
            <strong>Team Combinations:</strong> Discover which team lineups perform best together
          </li>
          <li>
            <strong>Custom Query:</strong> Filter games by specific players and roles to analyze
            win rates
          </li>
        </ul>
      </CardContent>
    </Card>
  </div>
</template>
