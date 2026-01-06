<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const games = ref<Game[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// Dialog state
const dialogOpen = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingGameId = ref<number | null>(null)

// Form state
const formData = ref({
  blueOperatives: '',
  blueSpymasters: '',
  redOperatives: '',
  redSpymasters: '',
  winner: 'Blue',
})

const loadGames = async () => {
  loading.value = true
  error.value = null
  try {
    games.value = await api.getAllGames()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load games'
  } finally {
    loading.value = false
  }
}

onMounted(loadGames)

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
  }
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  editingGameId.value = null
  formData.value = {
    blueOperatives: '',
    blueSpymasters: '',
    redOperatives: '',
    redSpymasters: '',
    winner: 'Blue',
  }
  dialogOpen.value = true
}

const openEditDialog = (game: Game) => {
  dialogMode.value = 'edit'
  editingGameId.value = game.id
  formData.value = {
    blueOperatives: game.raw_data.blue_team.operatives.join(', '),
    blueSpymasters: game.raw_data.blue_team.spymasters.join(', '),
    redOperatives: game.raw_data.red_team.operatives.join(', '),
    redSpymasters: game.raw_data.red_team.spymasters.join(', '),
    winner: game.winner,
  }
  dialogOpen.value = true
}

const parsePlayerList = (input: string): string[] => {
  return input
    .split(',')
    .map((name) => name.trim())
    .filter((name) => name.length > 0)
}

const handleSave = async () => {
  try {
    const gameData = {
      blue_team: {
        operatives: parsePlayerList(formData.value.blueOperatives),
        spymasters: parsePlayerList(formData.value.blueSpymasters),
      },
      red_team: {
        operatives: parsePlayerList(formData.value.redOperatives),
        spymasters: parsePlayerList(formData.value.redSpymasters),
      },
      winner: formData.value.winner,
    }

    if (dialogMode.value === 'create') {
      await api.createGame(gameData)
    } else if (editingGameId.value !== null) {
      await api.updateGame(editingGameId.value, gameData)
    }

    dialogOpen.value = false
    loadGames()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to save game')
  }
}

const handleDelete = async (gameId: number) => {
  if (!confirm(`Are you sure you want to delete game #${gameId}?`)) {
    return
  }

  try {
    await api.deleteGame(gameId)
    loadGames()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to delete game')
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Admin Panel</h1>
        <p class="text-muted-foreground mt-2">Manage game records</p>
      </div>
      <Button @click="openCreateDialog">+ Add New Game</Button>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>All Games</CardTitle>
        <CardDescription>View, edit, and delete game records</CardDescription>
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
            </div>
          </div>
        </div>

        <div v-else-if="error" class="text-red-500 py-4">{{ error }}</div>

        <div v-else-if="games.length === 0" class="text-muted-foreground py-4">
          No games found. Add your first game!
        </div>

        <div v-else class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[80px]">ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Blue Team</TableHead>
                <TableHead>Red Team</TableHead>
                <TableHead>Winner</TableHead>
                <TableHead class="text-right">Actions</TableHead>
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
                    <div v-if="formatTeam(game.raw_data.blue_team).spymasters" class="text-sm">
                      <span class="font-semibold text-purple-600">SM:</span>
                      {{ formatTeam(game.raw_data.blue_team).spymasters }}
                    </div>
                    <div v-if="formatTeam(game.raw_data.blue_team).operatives" class="text-sm">
                      <span class="font-semibold text-blue-600">OP:</span>
                      {{ formatTeam(game.raw_data.blue_team).operatives }}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="space-y-1">
                    <div v-if="formatTeam(game.raw_data.red_team).spymasters" class="text-sm">
                      <span class="font-semibold text-purple-600">SM:</span>
                      {{ formatTeam(game.raw_data.red_team).spymasters }}
                    </div>
                    <div v-if="formatTeam(game.raw_data.red_team).operatives" class="text-sm">
                      <span class="font-semibold text-red-600">OP:</span>
                      {{ formatTeam(game.raw_data.red_team).operatives }}
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
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button @click="openEditDialog(game)" variant="outline" size="sm">
                      Edit
                    </Button>
                    <Button @click="handleDelete(game.id)" variant="destructive" size="sm">
                      Delete
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="dialogOpen">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {{ dialogMode === 'create' ? 'Add New Game' : 'Edit Game' }}
          </DialogTitle>
          <DialogDescription>
            Enter player names separated by commas (e.g., "Alice, Bob, Charlie")
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <!-- Blue Team -->
          <div class="space-y-3">
            <h3 class="text-sm font-semibold text-blue-600">Blue Team</h3>
            <div class="space-y-2">
              <Label for="blue-spymasters">Spymasters</Label>
              <Input
                id="blue-spymasters"
                v-model="formData.blueSpymasters"
                placeholder="Alice, Bob"
              />
            </div>
            <div class="space-y-2">
              <Label for="blue-operatives">Operatives</Label>
              <Input
                id="blue-operatives"
                v-model="formData.blueOperatives"
                placeholder="Charlie, Diana"
              />
            </div>
          </div>

          <!-- Red Team -->
          <div class="space-y-3">
            <h3 class="text-sm font-semibold text-red-600">Red Team</h3>
            <div class="space-y-2">
              <Label for="red-spymasters">Spymasters</Label>
              <Input
                id="red-spymasters"
                v-model="formData.redSpymasters"
                placeholder="Eve, Frank"
              />
            </div>
            <div class="space-y-2">
              <Label for="red-operatives">Operatives</Label>
              <Input
                id="red-operatives"
                v-model="formData.redOperatives"
                placeholder="Grace, Henry"
              />
            </div>
          </div>

          <!-- Winner -->
          <div class="space-y-2">
            <Label for="winner">Winner</Label>
            <Select v-model="formData.winner">
              <SelectTrigger id="winner">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Blue">Blue</SelectItem>
                <SelectItem value="Red">Red</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button @click="dialogOpen = false" variant="outline">Cancel</Button>
          <Button @click="handleSave">Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
