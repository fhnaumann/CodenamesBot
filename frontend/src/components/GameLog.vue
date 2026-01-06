<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'
import type { Game } from '@/types/api'
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

const games = ref<Game[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    games.value = await api.getAllGames()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load games'
  } finally {
    loading.value = false
  }
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatTeam = (team: { operatives: string[]; spymasters: string[] }) => {
  const operatives = team.operatives.length > 0 ? team.operatives.join(', ') : ''
  const spymasters = team.spymasters.length > 0 ? team.spymasters.join(', ') : ''

  return {
    operatives,
    spymasters,
    all: [...team.operatives, ...team.spymasters].join(', '),
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Game History</CardTitle>
      <CardDescription>All games played, showing teams, roles, and outcomes</CardDescription>
    </CardHeader>
    <CardContent>
      <div v-if="loading" class="space-y-4">
        <div class="rounded-md border">
          <div class="p-4 space-y-3">
            <Skeleton class="h-8 w-full" />
            <Skeleton class="h-16 w-full" />
            <Skeleton class="h-16 w-full" />
            <Skeleton class="h-16 w-full" />
            <Skeleton class="h-16 w-full" />
            <Skeleton class="h-16 w-full" />
          </div>
        </div>
      </div>

      <div v-else-if="error" class="text-red-500 py-4">{{ error }}</div>

      <div v-else-if="games.length === 0" class="text-muted-foreground py-4">
        No games found. Start playing to see game history!
      </div>

      <div v-else class="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[100px]">Game #</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Blue Team</TableHead>
              <TableHead>Red Team</TableHead>
              <TableHead>Winner</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="game in games" :key="game.id">
              <TableCell class="font-medium">{{ game.id }}</TableCell>
              <TableCell class="text-sm text-muted-foreground">
                {{ formatDate(game.date) }}
              </TableCell>
              <TableCell>
                <div class="space-y-1">
                  <div v-if="formatTeam(game.raw_data.blue_team).operatives" class="text-sm">
                    <span class="font-semibold text-blue-600">Operatives:</span>
                    {{ formatTeam(game.raw_data.blue_team).operatives }}
                  </div>
                  <div v-if="formatTeam(game.raw_data.blue_team).spymasters" class="text-sm">
                    <span class="font-semibold text-blue-600">Spymasters:</span>
                    {{ formatTeam(game.raw_data.blue_team).spymasters }}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div class="space-y-1">
                  <div v-if="formatTeam(game.raw_data.red_team).operatives" class="text-sm">
                    <span class="font-semibold text-red-600">Operatives:</span>
                    {{ formatTeam(game.raw_data.red_team).operatives }}
                  </div>
                  <div v-if="formatTeam(game.raw_data.red_team).spymasters" class="text-sm">
                    <span class="font-semibold text-red-600">Spymasters:</span>
                    {{ formatTeam(game.raw_data.red_team).spymasters }}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <Badge
                  :variant="game.winner === 'Blue' ? 'default' : 'destructive'"
                  class="font-semibold"
                >
                  {{ game.winner }}
                </Badge>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </CardContent>
  </Card>
</template>
