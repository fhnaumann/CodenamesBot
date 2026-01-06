from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from database import (
    init_database,
    get_player_stats,
    get_player_stats_by_role,
    get_total_games,
    get_team_combination_stats,
    get_team_combination_stats_with_roles,
    get_all_games,
    save_game,
    update_game,
    delete_game,
    get_db_connection
)

load_dotenv()

app = FastAPI(
    title="Codenames Stats API",
    description="API for managing Codenames game statistics",
    version="1.0.0"
)

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class TeamData(BaseModel):
    operatives: List[str]
    spymasters: List[str]


class GameData(BaseModel):
    blue_team: TeamData
    red_team: TeamData
    winner: str


class GameResponse(BaseModel):
    game_id: int
    message: str


class PlayerStat(BaseModel):
    name: str
    total_games: int
    wins: int
    losses: int
    win_rate: float


class PlayerRoleStat(BaseModel):
    name: str
    role: str
    total_games: int
    wins: int
    win_rate: float


class TeamCombinationStat(BaseModel):
    player_names: str
    wins: int
    losses: int
    total_games: int
    win_rate: float


class TeamCombinationWithRoles(BaseModel):
    spymasters: List[str]
    operatives: List[str]
    wins: int
    losses: int
    total_games: int
    win_rate: float


class TotalGamesResponse(BaseModel):
    total_games: int


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()


# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "Codenames Stats API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


# Stats endpoints
@app.get("/api/stats/players", response_model=List[PlayerStat])
async def get_players_stats():
    """Get overall statistics for all players"""
    try:
        stats = get_player_stats()
        return [
            PlayerStat(
                name=name,
                total_games=total,
                wins=wins,
                losses=losses,
                win_rate=win_rate
            )
            for name, total, wins, losses, win_rate in stats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/players/by-role", response_model=List[PlayerRoleStat])
async def get_players_stats_by_role():
    """Get statistics for all players broken down by role (Operative vs Spymaster)"""
    try:
        stats = get_player_stats_by_role()
        return [
            PlayerRoleStat(
                name=name,
                role=role,
                total_games=total,
                wins=wins,
                win_rate=win_rate
            )
            for name, role, total, wins, win_rate in stats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/team-combinations", response_model=List[TeamCombinationStat])
async def get_team_combinations(min_games: int = 2):
    """
    Get statistics for team combinations

    Query parameters:
    - min_games: Minimum number of games played together (default: 2)
    """
    try:
        stats = get_team_combination_stats(min_games)
        return [
            TeamCombinationStat(
                player_names=names,
                wins=wins,
                losses=losses,
                total_games=total,
                win_rate=win_rate
            )
            for names, wins, losses, total, win_rate in stats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/team-combinations-with-roles", response_model=List[TeamCombinationWithRoles])
async def get_team_combinations_with_role_info(min_games: int = 2):
    """
    Get statistics for team combinations with role information

    Query parameters:
    - min_games: Minimum number of games played together (default: 2)
    """
    try:
        stats = get_team_combination_stats_with_roles(min_games)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/total-games", response_model=TotalGamesResponse)
async def get_total_games_count():
    """Get the total number of games played"""
    try:
        total = get_total_games()
        return TotalGamesResponse(total_games=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/games")
async def get_games():
    """Get all games with their details"""
    try:
        games = get_all_games()
        return games
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Game management endpoints
@app.post("/api/games", response_model=GameResponse)
async def create_game(game_data: GameData):
    """
    Create a new game record

    Request body should include:
    - blue_team: Team data with operatives and spymasters
    - red_team: Team data with operatives and spymasters
    - winner: "Blue" or "Red"
    """
    try:
        # Validate winner
        if game_data.winner not in ["Blue", "Red"]:
            raise HTTPException(status_code=400, detail="Winner must be 'Blue' or 'Red'")

        # Convert to dict format expected by database.py
        game_dict = {
            "blue_team": {
                "operatives": game_data.blue_team.operatives,
                "spymasters": game_data.blue_team.spymasters
            },
            "red_team": {
                "operatives": game_data.red_team.operatives,
                "spymasters": game_data.red_team.spymasters
            },
            "winner": game_data.winner
        }

        game_id = save_game(game_dict)
        return GameResponse(game_id=game_id, message=f"Game #{game_id} created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/games/{game_id}", response_model=GameResponse)
async def update_game_data(game_id: int, game_data: GameData):
    """
    Update an existing game record

    Path parameters:
    - game_id: The ID of the game to update

    Request body should include:
    - blue_team: Team data with operatives and spymasters
    - red_team: Team data with operatives and spymasters
    - winner: "Blue" or "Red"
    """
    try:
        # Validate winner
        if game_data.winner not in ["Blue", "Red"]:
            raise HTTPException(status_code=400, detail="Winner must be 'Blue' or 'Red'")

        # Convert to dict format expected by database.py
        game_dict = {
            "blue_team": {
                "operatives": game_data.blue_team.operatives,
                "spymasters": game_data.blue_team.spymasters
            },
            "red_team": {
                "operatives": game_data.red_team.operatives,
                "spymasters": game_data.red_team.spymasters
            },
            "winner": game_data.winner
        }

        update_game(game_id, game_dict)
        return GameResponse(game_id=game_id, message=f"Game #{game_id} updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/games/{game_id}", response_model=GameResponse)
async def delete_game_data(game_id: int):
    """
    Delete an existing game record

    Path parameters:
    - game_id: The ID of the game to delete
    """
    try:
        delete_game(game_id)
        return GameResponse(game_id=game_id, message=f"Game #{game_id} deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)