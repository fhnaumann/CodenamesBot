<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'
import type { Game, PlayerStat } from '@/types/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

interface PlayerFilter {
  id: number
  playerName: string
  role: 'Operative' | 'Spymaster' | 'Any'
}

const games = ref<Game[]>([])
const allPlayers = ref<string[]>([])
const loading = ref(true)
const filters = ref<PlayerFilter[]>([])
let nextFilterId = 1

const addFilter = () => {
  filters.value.push({
    id: nextFilterId++,
    playerName: '',
    role: 'Any',
  })
}

const removeFilter = (id: number) => {
  filters.value = filters.value.filter((f) => f.id !== id)
}

const resetFilters = () => {
  filters.value = []
  nextFilterId = 1
  addFilter()
}

onMounted(async () => {
  try {
    const [gamesData, playerStats] = await Promise.all([api.getAllGames(), api.getPlayerStats()])

    games.value = gamesData
    allPlayers.value = playerStats.map((p: PlayerStat) => p.name).sort()

    // Start with one empty filter
    addFilter()
  } catch (e) {
    console.error('Failed to load data:', e)
  } finally {
    loading.value = false
  }
})

const activeFilters = computed(() => {
  return filters.value.filter((f) => f.playerName !== '')
})

const filteredGames = computed(() => {
  if (activeFilters.value.length === 0) {
    return []
  }

  return games.value.filter((game) => {
    // All filters must match for the game to be included
    return activeFilters.value.every((filter) => {
      // Check both teams for this filter
      for (const teamColor of ['blue', 'red']) {
        const team = teamColor === 'blue' ? game.raw_data.blue_team : game.raw_data.red_team

        const inOperatives = team.operatives.includes(filter.playerName)
        const inSpymasters = team.spymasters.includes(filter.playerName)

        if (filter.role === 'Any' && (inOperatives || inSpymasters)) {
          return true
        } else if (filter.role === 'Operative' && inOperatives) {
          return true
        } else if (filter.role === 'Spymaster' && inSpymasters) {
          return true
        }
      }
      return false
    })
  })
})

const winStats = computed(() => {
  if (filteredGames.value.length === 0) {
    return {
      totalGames: 0,
      wins: 0,
      losses: 0,
      winRate: 0,
    }
  }

  const total = filteredGames.value.length
  let wins = 0

  // For each game, check if ALL the filtered players won
  filteredGames.value.forEach((game) => {
    const allPlayersWon = activeFilters.value.every((filter) => {
      // Find which team this player was on
      const blueTeam = game.raw_data.blue_team
      const redTeam = game.raw_data.red_team

      const inBlueOperatives = blueTeam.operatives.includes(filter.playerName)
      const inBlueSpymasters = blueTeam.spymasters.includes(filter.playerName)
      const inRedOperatives = redTeam.operatives.includes(filter.playerName)
      const inRedSpymasters = redTeam.spymasters.includes(filter.playerName)

      const onBlueTeam = inBlueOperatives || inBlueSpymasters
      const onRedTeam = inRedOperatives || inRedSpymasters

      // Check if this player won
      if (onBlueTeam && game.winner === 'Blue') return true
      if (onRedTeam && game.winner === 'Red') return true
      return false
    })

    if (allPlayersWon) wins++
  })

  const losses = total - wins

  return {
    totalGames: total,
    wins,
    losses,
    winRate: (wins / total) * 100,
  }
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const isPlayerHighlighted = (playerName: string, role: string) => {
  return activeFilters.value.some((filter) => {
    if (filter.playerName !== playerName) return false
    if (filter.role === 'Any') return true
    return filter.role === role
  })
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Custom Query</CardTitle>
      <CardDescription>
        Filter games by specific players and roles to see win statistics
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div class="space-y-3">
          <Skeleton class="h-20 w-full" />
          <Skeleton class="h-20 w-full" />
        </div>
        <Skeleton class="h-10 w-32" />
      </div>

      <!-- Filters -->
      <div v-else class="space-y-4">
        <div class="space-y-3">
          <!-- Player Filters -->
          <div
            v-for="filter in filters"
            :key="filter.id"
            class="flex items-end gap-3 p-3 border rounded-lg bg-muted/30"
          >
            <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-2">
                <label class="text-sm font-medium">Player</label>
                <Select v-model="filter.playerName">
                  <SelectTrigger>
                    <SelectValue placeholder="Select player..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="player in allPlayers" :key="player" :value="player">
                      {{ player }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium">Role</label>
                <Select v-model="filter.role">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Any">Any Role</SelectItem>
                    <SelectItem value="Operative">Operative</SelectItem>
                    <SelectItem value="Spymaster">Spymaster</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              @click="removeFilter(filter.id)"
              variant="outline"
              size="icon"
              class="shrink-0"
              :disabled="filters.length === 1"
            >
              <span class="text-lg">×</span>
            </Button>
          </div>
        </div>

        <div class="flex gap-2">
          <Button @click="addFilter" variant="outline">
            <span class="mr-1">+</span> Add Player
          </Button>
          <Button @click="resetFilters" variant="outline">Reset All</Button>
        </div>
      </div>

      <!-- Results -->
      <div v-if="!loading && activeFilters.length > 0" class="space-y-4">
        <div class="rounded-lg border bg-muted/50 p-6">
          <h3 class="text-lg font-semibold mb-4">Results</h3>

          <div v-if="filteredGames.length === 0" class="text-muted-foreground">
            No games found matching these criteria.
          </div>

          <div v-else class="space-y-4">
            <!-- Stats Summary -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center">
                <div class="text-2xl font-bold">{{ winStats.totalGames }}</div>
                <div class="text-sm text-muted-foreground">Total Games</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ winStats.wins }}</div>
                <div class="text-sm text-muted-foreground">Wins</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ winStats.losses }}</div>
                <div class="text-sm text-muted-foreground">Losses</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-primary">
                  {{ winStats.winRate.toFixed(1) }}%
                </div>
                <div class="text-sm text-muted-foreground">Win Rate</div>
              </div>
            </div>

            <!-- Active Filters Display -->
            <div class="pt-2">
              <h4 class="text-sm font-semibold mb-2">Filtering by:</h4>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="filter in activeFilters" :key="filter.id" variant="secondary">
                  {{ filter.playerName }}
                  <span v-if="filter.role !== 'Any'" class="ml-1 opacity-70">
                    ({{ filter.role }})
                  </span>
                </Badge>
              </div>
            </div>

            <!-- Game List -->
            <div class="space-y-3">
              <h4 class="text-sm font-semibold">Matching Games:</h4>
              <div class="space-y-3 max-h-[500px] overflow-y-auto">
                <div
                  v-for="game in filteredGames"
                  :key="game.id"
                  class="p-4 rounded-md bg-background border space-y-3"
                >
                  <!-- Game Header -->
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <span class="font-semibold">Game #{{ game.id }}</span>
                      <span class="text-sm text-muted-foreground">
                        {{ formatDate(game.date) }}
                      </span>
                    </div>
                    <Badge
                      :variant="game.winner === 'Blue' ? 'default' : 'destructive'"
                      class="font-semibold"
                    >
                      {{ game.winner }} Won
                    </Badge>
                  </div>

                  <!-- Teams -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Blue Team -->
                    <div
                      class="p-3 rounded-md border-2"
                      :class="game.winner === 'Blue' ? 'border-blue-500 bg-blue-50' : 'border-border'"
                    >
                      <div class="font-semibold text-blue-600 mb-2">Blue Team</div>
                      <div class="space-y-1 text-sm">
                        <!-- Spymasters -->
                        <div v-if="game.raw_data.blue_team.spymasters.length > 0">
                          <span class="text-muted-foreground">Spymasters:</span>
                          <div class="ml-2">
                            <span
                              v-for="(spy, idx) in game.raw_data.blue_team.spymasters"
                              :key="spy"
                              :class="
                                isPlayerHighlighted(spy, 'Spymaster')
                                  ? 'font-bold text-purple-700 bg-purple-100 px-1 rounded'
                                  : ''
                              "
                            >
                              {{ spy }}{{ idx < game.raw_data.blue_team.spymasters.length - 1 ? ', ' : '' }}
                            </span>
                          </div>
                        </div>
                        <!-- Operatives -->
                        <div v-if="game.raw_data.blue_team.operatives.length > 0">
                          <span class="text-muted-foreground">Operatives:</span>
                          <div class="ml-2">
                            <span
                              v-for="(op, idx) in game.raw_data.blue_team.operatives"
                              :key="op"
                              :class="
                                isPlayerHighlighted(op, 'Operative')
                                  ? 'font-bold text-blue-700 bg-blue-100 px-1 rounded'
                                  : ''
                              "
                            >
                              {{ op }}{{ idx < game.raw_data.blue_team.operatives.length - 1 ? ', ' : '' }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Red Team -->
                    <div
                      class="p-3 rounded-md border-2"
                      :class="game.winner === 'Red' ? 'border-red-500 bg-red-50' : 'border-border'"
                    >
                      <div class="font-semibold text-red-600 mb-2">Red Team</div>
                      <div class="space-y-1 text-sm">
                        <!-- Spymasters -->
                        <div v-if="game.raw_data.red_team.spymasters.length > 0">
                          <span class="text-muted-foreground">Spymasters:</span>
                          <div class="ml-2">
                            <span
                              v-for="(spy, idx) in game.raw_data.red_team.spymasters"
                              :key="spy"
                              :class="
                                isPlayerHighlighted(spy, 'Spymaster')
                                  ? 'font-bold text-purple-700 bg-purple-100 px-1 rounded'
                                  : ''
                              "
                            >
                              {{ spy }}{{ idx < game.raw_data.red_team.spymasters.length - 1 ? ', ' : '' }}
                            </span>
                          </div>
                        </div>
                        <!-- Operatives -->
                        <div v-if="game.raw_data.red_team.operatives.length > 0">
                          <span class="text-muted-foreground">Operatives:</span>
                          <div class="ml-2">
                            <span
                              v-for="(op, idx) in game.raw_data.red_team.operatives"
                              :key="op"
                              :class="
                                isPlayerHighlighted(op, 'Operative')
                                  ? 'font-bold text-blue-700 bg-blue-100 px-1 rounded'
                                  : ''
                              "
                            >
                              {{ op }}{{ idx < game.raw_data.red_team.operatives.length - 1 ? ', ' : '' }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="text-center text-muted-foreground py-8">
        Select at least one player to see results
      </div>
    </CardContent>
  </Card>
</template>
