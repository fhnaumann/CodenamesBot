export interface TeamData {
  operatives: string[]
  spymasters: string[]
}

export interface GameData {
  blue_team: TeamData
  red_team: TeamData
  winner: string
}

export interface Game {
  id: number
  date: string
  winner: string
  raw_data: GameData
}

export interface PlayerStat {
  name: string
  total_games: number
  wins: number
  losses: number
  win_rate: number
}

export interface PlayerRoleStat {
  name: string
  role: string
  total_games: number
  wins: number
  win_rate: number
}

export interface TeamCombinationStat {
  player_names: string
  wins: number
  losses: number
  total_games: number
  win_rate: number
}

export interface TeamCombinationWithRoles {
  spymasters: string[]
  operatives: string[]
  wins: number
  losses: number
  total_games: number
  win_rate: number
}

export interface TotalGamesResponse {
  total_games: number
}
