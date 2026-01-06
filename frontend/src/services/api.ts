import type {
  Game,
  PlayerStat,
  PlayerRoleStat,
  TeamCombinationStat,
  TeamCombinationWithRoles,
  TotalGamesResponse,
} from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options)
  console.log(response)
  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`)
  }
  return response.json()
}

export const api = {
  // Get all games
  async getAllGames(): Promise<Game[]> {
    return fetchAPI<Game[]>('/api/games')
  },

  // Get player statistics
  async getPlayerStats(): Promise<PlayerStat[]> {
    return fetchAPI<PlayerStat[]>('/api/stats/players')
  },

  // Get player statistics by role
  async getPlayerStatsByRole(): Promise<PlayerRoleStat[]> {
    return fetchAPI<PlayerRoleStat[]>('/api/stats/players/by-role')
  },

  // Get team combination statistics
  async getTeamCombinations(minGames: number = 2): Promise<TeamCombinationStat[]> {
    return fetchAPI<TeamCombinationStat[]>(`/api/stats/team-combinations?min_games=${minGames}`)
  },

  // Get team combination statistics with role information
  async getTeamCombinationsWithRoles(
    minGames: number = 2,
  ): Promise<TeamCombinationWithRoles[]> {
    return fetchAPI<TeamCombinationWithRoles[]>(
      `/api/stats/team-combinations-with-roles?min_games=${minGames}`,
    )
  },

  // Get total games count
  async getTotalGames(): Promise<TotalGamesResponse> {
    return fetchAPI<TotalGamesResponse>('/api/stats/total-games')
  },

  // Create a new game
  async createGame(gameData: {
    blue_team: { operatives: string[]; spymasters: string[] }
    red_team: { operatives: string[]; spymasters: string[] }
    winner: string
  }): Promise<{ game_id: number; message: string }> {
    return fetchAPI('/api/games', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(gameData),
    })
  },

  // Update an existing game
  async updateGame(
    gameId: number,
    gameData: {
      blue_team: { operatives: string[]; spymasters: string[] }
      red_team: { operatives: string[]; spymasters: string[] }
      winner: string
    },
  ): Promise<{ game_id: number; message: string }> {
    return fetchAPI(`/api/games/${gameId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(gameData),
    })
  },

  // Delete a game
  async deleteGame(gameId: number): Promise<{ game_id: number; message: string }> {
    return fetchAPI(`/api/games/${gameId}`, {
      method: 'DELETE',
    })
  },
}
