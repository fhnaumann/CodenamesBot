<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'
import type { PlayerStat, PlayerRoleStat } from '@/types/api'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

const playerStats = ref<PlayerStat[]>([])
const playerRoleStats = ref<PlayerRoleStat[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const [stats, roleStats] = await Promise.all([
      api.getPlayerStats(),
      api.getPlayerStatsByRole(),
    ])
    playerStats.value = stats
    playerRoleStats.value = roleStats
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load player stats'
  } finally {
    loading.value = false
  }
})

const spymasterStats = computed(() => {
  return playerRoleStats.value.filter((stat) => stat.role === 'Spymaster')
})

const operativeStats = computed(() => {
  return playerRoleStats.value.filter((stat) => stat.role === 'Operative')
})

const formatWinRate = (winRate: number) => {
  return `${winRate.toFixed(1)}%`
}

const getWinRateColor = (winRate: number) => {
  if (winRate >= 60) return 'text-green-600 font-semibold'
  if (winRate >= 50) return 'text-blue-600 font-medium'
  if (winRate >= 40) return 'text-orange-600'
  return 'text-red-600'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Overall Player Stats -->
    <Card>
      <CardHeader>
        <CardTitle>Player Leaderboard</CardTitle>
        <CardDescription>Overall statistics for all players</CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="loading" class="space-y-4">
          <div class="rounded-md border">
            <div class="p-4 space-y-3">
              <Skeleton class="h-8 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
            </div>
          </div>
        </div>

        <div v-else-if="error" class="text-red-500 py-4">{{ error }}</div>

        <div v-else-if="playerStats.length === 0" class="text-muted-foreground py-4">
          No player statistics available yet.
        </div>

        <div v-else class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[50px]">Rank</TableHead>
                <TableHead>Player</TableHead>
                <TableHead class="text-right">Games</TableHead>
                <TableHead class="text-right">Wins</TableHead>
                <TableHead class="text-right">Losses</TableHead>
                <TableHead class="text-right">Win Rate</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="(player, index) in playerStats" :key="player.name">
                <TableCell class="font-medium">
                  <Badge v-if="index === 0" variant="default">1st</Badge>
                  <Badge v-else-if="index === 1" variant="secondary">2nd</Badge>
                  <Badge v-else-if="index === 2" variant="outline">3rd</Badge>
                  <span v-else class="text-muted-foreground">{{ index + 1 }}</span>
                </TableCell>
                <TableCell class="font-semibold">{{ player.name }}</TableCell>
                <TableCell class="text-right">{{ player.total_games }}</TableCell>
                <TableCell class="text-right text-green-600">{{ player.wins }}</TableCell>
                <TableCell class="text-right text-red-600">{{ player.losses }}</TableCell>
                <TableCell class="text-right" :class="getWinRateColor(player.win_rate)">
                  {{ formatWinRate(player.win_rate) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Spymaster Stats -->
    <Card>
      <CardHeader>
        <CardTitle>Spymaster Leaderboard</CardTitle>
        <CardDescription>Performance as Spymaster</CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="loading" class="space-y-4">
          <div class="rounded-md border">
            <div class="p-4 space-y-3">
              <Skeleton class="h-8 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
            </div>
          </div>
        </div>

        <div v-else-if="error" class="text-red-500 py-4">{{ error }}</div>

        <div v-else-if="spymasterStats.length === 0" class="text-muted-foreground py-4">
          No spymaster statistics available yet.
        </div>

        <div v-else class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[50px]">Rank</TableHead>
                <TableHead>Player</TableHead>
                <TableHead class="text-right">Games</TableHead>
                <TableHead class="text-right">Wins</TableHead>
                <TableHead class="text-right">Win Rate</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="(stat, index) in spymasterStats" :key="stat.name">
                <TableCell class="font-medium">
                  <Badge v-if="index === 0" variant="default">1st</Badge>
                  <Badge v-else-if="index === 1" variant="secondary">2nd</Badge>
                  <Badge v-else-if="index === 2" variant="outline">3rd</Badge>
                  <span v-else class="text-muted-foreground">{{ index + 1 }}</span>
                </TableCell>
                <TableCell class="font-semibold">{{ stat.name }}</TableCell>
                <TableCell class="text-right">{{ stat.total_games }}</TableCell>
                <TableCell class="text-right text-green-600">{{ stat.wins }}</TableCell>
                <TableCell class="text-right" :class="getWinRateColor(stat.win_rate)">
                  {{ formatWinRate(stat.win_rate) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Operative Stats -->
    <Card>
      <CardHeader>
        <CardTitle>Operative Leaderboard</CardTitle>
        <CardDescription>Performance as Operative</CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="loading" class="space-y-4">
          <div class="rounded-md border">
            <div class="p-4 space-y-3">
              <Skeleton class="h-8 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
            </div>
          </div>
        </div>

        <div v-else-if="error" class="text-red-500 py-4">{{ error }}</div>

        <div v-else-if="operativeStats.length === 0" class="text-muted-foreground py-4">
          No operative statistics available yet.
        </div>

        <div v-else class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[50px]">Rank</TableHead>
                <TableHead>Player</TableHead>
                <TableHead class="text-right">Games</TableHead>
                <TableHead class="text-right">Wins</TableHead>
                <TableHead class="text-right">Win Rate</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="(stat, index) in operativeStats" :key="stat.name">
                <TableCell class="font-medium">
                  <Badge v-if="index === 0" variant="default">1st</Badge>
                  <Badge v-else-if="index === 1" variant="secondary">2nd</Badge>
                  <Badge v-else-if="index === 2" variant="outline">3rd</Badge>
                  <span v-else class="text-muted-foreground">{{ index + 1 }}</span>
                </TableCell>
                <TableCell class="font-semibold">{{ stat.name }}</TableCell>
                <TableCell class="text-right">{{ stat.total_games }}</TableCell>
                <TableCell class="text-right text-green-600">{{ stat.wins }}</TableCell>
                <TableCell class="text-right" :class="getWinRateColor(stat.win_rate)">
                  {{ formatWinRate(stat.win_rate) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
