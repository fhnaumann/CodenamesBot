# Codenames Stats API Documentation

## Overview

The Codenames Stats API is a RESTful HTTP API built with FastAPI that provides access to game statistics and allows for game management. The API serves as the data layer between the Discord bot and the PostgreSQL database, and will also serve the frontend website.

## Base URL

Local development: `http://localhost:8000`

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (via psycopg2)
- **Protocol**: HTTP/REST
- **Response Format**: JSON

## Why HTTP Instead of WebSockets?

HTTP is sufficient for this use case because:
- Stats updates happen after each game (not continuous streaming)
- 1-5 second delay is acceptable for stat updates
- Simpler architecture and easier to deploy
- Frontend can poll or use periodic refresh
- Lower complexity for both server and clients

## API Endpoints

### Health Check

#### `GET /`
Root endpoint returning API status.

**Response:**
```json
{
  "status": "ok",
  "message": "Codenames Stats API"
}
```

#### `GET /health`
Health check endpoint that verifies database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### Statistics Endpoints

These endpoints are primarily used by the frontend to display statistics.

#### `GET /api/stats/players`
Get overall statistics for all players.

**Response:**
```json
[
  {
    "name": "Felix",
    "total_games": 25,
    "wins": 15,
    "losses": 10,
    "win_rate": 60.0
  },
  {
    "name": "Julia",
    "total_games": 20,
    "wins": 12,
    "losses": 8,
    "win_rate": 60.0
  }
]
```

#### `GET /api/stats/players/by-role`
Get statistics broken down by role (Operative vs Spymaster).

**Response:**
```json
[
  {
    "name": "Felix",
    "role": "Operative",
    "total_games": 15,
    "wins": 10,
    "win_rate": 66.7
  },
  {
    "name": "Felix",
    "role": "Spymaster",
    "total_games": 10,
    "wins": 5,
    "win_rate": 50.0
  }
]
```

#### `GET /api/stats/team-combinations`
Get statistics for team combinations (players who played together).

**Query Parameters:**
- `min_games` (integer, default: 2) - Minimum number of games played together

**Example Request:**
```
GET /api/stats/team-combinations?min_games=3
```

**Response:**
```json
[
  {
    "player_names": "Diana,Felix,Julia,Nabi",
    "wins": 8,
    "losses": 2,
    "total_games": 10,
    "win_rate": 80.0
  },
  {
    "player_names": "Felix,Julia",
    "wins": 12,
    "losses": 8,
    "total_games": 20,
    "win_rate": 60.0
  }
]
```

**Note:** Limited to top 20 combinations, sorted by win rate then total games.

#### `GET /api/stats/total-games`
Get the total number of games played.

**Response:**
```json
{
  "total_games": 42
}
```

---

### Game Management Endpoints

These endpoints are primarily used by the Discord bot to create and update games.

#### `POST /api/games`
Create a new game record.

**Request Body:**
```json
{
  "blue_team": {
    "operatives": ["Felix", "Julia"],
    "spymasters": ["Diana"]
  },
  "red_team": {
    "operatives": ["Alice", "Bob"],
    "spymasters": ["Charlie"]
  },
  "winner": "Blue"
}
```

**Validation:**
- `winner` must be either "Blue" or "Red"
- Team lists can be empty
- Player names are case-sensitive

**Response:**
```json
{
  "game_id": 42,
  "message": "Game #42 created successfully"
}
```

**Status Codes:**
- `200 OK` - Game created successfully
- `400 Bad Request` - Invalid winner value
- `500 Internal Server Error` - Database error

#### `PUT /api/games/{game_id}`
Update an existing game record.

**Path Parameters:**
- `game_id` (integer) - The ID of the game to update

**Request Body:**
Same format as POST /api/games

**Example Request:**
```
PUT /api/games/42
```

**Response:**
```json
{
  "game_id": 42,
  "message": "Game #42 updated successfully"
}
```

**Status Codes:**
- `200 OK` - Game updated successfully
- `400 Bad Request` - Invalid winner value
- `500 Internal Server Error` - Database error

---

## Data Models

### GameData
```python
{
  "blue_team": TeamData,
  "red_team": TeamData,
  "winner": str  # "Blue" or "Red"
}
```

### TeamData
```python
{
  "operatives": List[str],
  "spymasters": List[str]
}
```

---

## Database Schema

### Tables

**games**
- `id` (SERIAL PRIMARY KEY)
- `date` (TIMESTAMP) - When the game was recorded
- `winner` (TEXT) - "Blue" or "Red"
- `raw_data` (TEXT) - JSON string of complete game data

**players**
- `id` (SERIAL PRIMARY KEY)
- `name` (TEXT UNIQUE) - Player name

**game_participants**
- `id` (SERIAL PRIMARY KEY)
- `game_id` (INTEGER) - Foreign key to games
- `player_id` (INTEGER) - Foreign key to players
- `team` (TEXT) - "Blue" or "Red"
- `role` (TEXT) - "Operative" or "Spymaster"
- `won` (BOOLEAN) - Whether this participant won

**team_combinations**
- `id` (SERIAL PRIMARY KEY)
- `player_names` (TEXT UNIQUE) - Comma-separated, sorted player names
- `wins` (INTEGER)
- `losses` (INTEGER)

---

## Running the API Server

### Installation

```bash
cd api-server
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `api-server` directory:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/codenames
API_PORT=8000  # Optional, defaults to 8000
```

### Starting the Server

**Development (with auto-reload):**
```bash
cd api-server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
cd api-server
python bot.py
```

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## CORS Configuration

The API currently allows all origins (`allow_origins=["*"]`). In production, update the CORS middleware in `api-server/main.py` to restrict access:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)
```

---

## Error Handling

All endpoints return standard HTTP status codes:
- `200 OK` - Successful request
- `400 Bad Request` - Invalid request data
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Database connection failed

Error responses include a detail message:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently not implemented. Consider adding rate limiting in production to prevent abuse.

---

## Frontend Integration

### Recommended Approach

For the frontend, you can:

1. **Polling**: Fetch stats every 5-10 seconds
   ```javascript
   setInterval(() => {
     fetch('http://localhost:8000/api/stats/players')
       .then(response => response.json())
       .then(data => updateUI(data));
   }, 5000);
   ```

2. **On-demand refresh**: Add a refresh button that fetches latest stats

3. **Initial load**: Fetch all stats on page load, display immediately

### Example Fetch Requests

```javascript
// Get player stats
const players = await fetch('http://localhost:8000/api/stats/players')
  .then(res => res.json());

// Get team combinations
const teams = await fetch('http://localhost:8000/api/stats/team-combinations?min_games=2')
  .then(res => res.json());

// Get total games
const total = await fetch('http://localhost:8000/api/stats/total-games')
  .then(res => res.json());
```

---

## Discord Bot Integration

The Discord bot now communicates with the API instead of directly accessing the database. All database operations go through the API endpoints.

---

## Future Enhancements

Potential improvements for future versions:

1. **Authentication**: Add API keys for write operations
2. **Pagination**: Support for large datasets
3. **Filtering**: Filter stats by date range, specific players, etc.
4. **Caching**: Add Redis for frequently accessed stats
5. **WebSockets**: Real-time updates for live leaderboards
6. **Delete endpoint**: `DELETE /api/games/{game_id}` for removing games
7. **Player management**: Endpoints to rename or merge players
8. **Historical stats**: Track stats over time (weekly, monthly, all-time)

---

## Support

For issues or questions, please refer to the main project README or create an issue in the repository.