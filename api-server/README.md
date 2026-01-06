# Codenames Stats API Server

FastAPI-based REST API that manages the Codenames statistics database.

## Features

- RESTful HTTP API
- Automatic database initialization
- Interactive API documentation (Swagger UI)
- CORS support for web frontend
- Health check endpoints
- Player statistics aggregation
- Team combination tracking

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (or copy `.env.example`):

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/codenames
API_PORT=8000  # Optional, defaults to 8000
```

## Running

**Development (with auto-reload):**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
python main.py
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Or see the complete [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) in the root directory.

## Endpoints

### Statistics (GET)
- `/api/stats/players` - Overall player stats
- `/api/stats/players/by-role` - Stats by role (Operative/Spymaster)
- `/api/stats/team-combinations` - Team combination stats
- `/api/stats/total-games` - Total game count

### Game Management (POST/PUT)
- `POST /api/games` - Create new game
- `PUT /api/games/{game_id}` - Update existing game

### Health
- `GET /` - API status
- `GET /health` - Health check with database connectivity

## Files

- `main.py` - FastAPI application and endpoints
- `database.py` - Database operations and schema

## Database

The API uses PostgreSQL and will automatically create tables on startup if they don't exist.

### Schema
- **games** - Game records with date, winner, raw data
- **players** - Player registry
- **game_participants** - Many-to-many relationship with roles
- **team_combinations** - Precomputed team statistics

## Dependencies

- fastapi - Web framework
- uvicorn - ASGI server
- psycopg2-binary - PostgreSQL driver
- pydantic - Data validation
- python-dotenv - Environment variables