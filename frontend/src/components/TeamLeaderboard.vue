<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import type { TeamCombinationWithRoles } from '@/types/api'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const teamStats = ref<TeamCombinationWithRoles[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const minGames = ref(2)

const loadTeamStats = async () => {
  loading.value = true
  try {
    teamStats.value = await api.getTeamCombinationsWithRoles(minGames.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load team stats'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTeamStats()
})

const formatWinRate = (winRate: number) => {
  return `${winRate.toFixed(1)}%`
}

const getWinRateColor = (winRate: number) => {
  if (winRate >= 70) return 'text-green-600 font-semibold'
  if (winRate >= 60) return 'text-blue-600 font-medium'
  if (winRate >= 50) return 'text-orange-600'
  return 'text-red-600'
}

const handleMinGamesChange = (value: any) => {
  if (value !== null && value !== undefined) {
    minGames.value = typeof value === 'string' ? parseInt(value) : Number(value)
    loadTeamStats()
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center justify-between">
        <div>
          <CardTitle>Team Combinations</CardTitle>
          <CardDescription>Best performing team combinations</CardDescription>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">Min games:</span>
          <Select :model-value="minGames.toString()" @update:model-value="handleMinGamesChange">
            <SelectTrigger class="w-[100px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1+</SelectItem>
              <SelectItem value="2">2+</SelectItem>
              <SelectItem value="3">3+</SelectItem>
              <SelectItem value="5">5+</SelectItem>
              <SelectItem value="10">10+</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
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

      <div v-else-if="teamStats.length === 0" class="text-muted-foreground py-4">
        No team combinations found with {{ minGames }}+ games.
      </div>

      <div v-else class="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[50px]">Rank</TableHead>
              <TableHead>Spymasters</TableHead>
              <TableHead>Operatives</TableHead>
              <TableHead class="text-right">Games</TableHead>
              <TableHead class="text-right">Wins</TableHead>
              <TableHead class="text-right">Losses</TableHead>
              <TableHead class="text-right">Win Rate</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow
              v-for="(team, index) in teamStats"
              :key="`${team.spymasters.join(',')}-${team.operatives.join(',')}`"
            >
              <TableCell class="font-medium">
                <Badge v-if="index === 0" variant="default">1st</Badge>
                <Badge v-else-if="index === 1" variant="secondary">2nd</Badge>
                <Badge v-else-if="index === 2" variant="outline">3rd</Badge>
                <span v-else class="text-muted-foreground">{{ index + 1 }}</span>
              </TableCell>
              <TableCell>
                <div class="space-y-1">
                  <div v-if="team.spymasters.length > 0">
                    <span
                      v-for="(spy, idx) in team.spymasters"
                      :key="spy"
                      class="font-semibold text-purple-600"
                    >
                      {{ spy }}{{ idx < team.spymasters.length - 1 ? ', ' : '' }}
                    </span>
                  </div>
                  <div v-else class="text-muted-foreground text-sm">None</div>
                </div>
              </TableCell>
              <TableCell>
                <div class="space-y-1">
                  <div v-if="team.operatives.length > 0">
                    <span
                      v-for="(op, idx) in team.operatives"
                      :key="op"
                      class="font-semibold text-blue-600"
                    >
                      {{ op }}{{ idx < team.operatives.length - 1 ? ', ' : '' }}
                    </span>
                  </div>
                  <div v-else class="text-muted-foreground text-sm">None</div>
                </div>
              </TableCell>
              <TableCell class="text-right">{{ team.total_games }}</TableCell>
              <TableCell class="text-right text-green-600">{{ team.wins }}</TableCell>
              <TableCell class="text-right text-red-600">{{ team.losses }}</TableCell>
              <TableCell class="text-right" :class="getWinRateColor(team.win_rate)">
                {{ formatWinRate(team.win_rate) }}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </CardContent>
  </Card>
</template>
