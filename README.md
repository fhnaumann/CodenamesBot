# Codenames Stats Bot

A comprehensive system for tracking Codenames game statistics, consisting of a Discord bot, REST API, and web frontend.

## Architecture

This project is split into three main components:

```
CodenamesBot/
├── discord-bot/     # Discord bot that processes game screenshots
├── api-server/      # FastAPI REST API that wraps the database
├── frontend/        # Web frontend for displaying stats (to be implemented)
└── API_DOCUMENTATION.md  # Complete API documentation
```

### Components

1. **Discord Bot** (`discord-bot/`)
   - Listens for game screenshot uploads in Discord
   - Uses Claude AI to extract game data from images
   - Submits game results to the API
   - Displays stats in a pinned Discord message
   - Provides editing functionality for game corrections

2. **API Server** (`api-server/`)
   - FastAPI-based REST API
   - Manages PostgreSQL database operations
   - Provides endpoints for stats retrieval and game management
   - Serves both the Discord bot and web frontend

3. **Frontend** (`frontend/`)
   - Web-based statistics dashboard (to be implemented)
   - Will consume the REST API to display stats

## Quick Start

### Prerequisites

- Python 3.14+
- PostgreSQL database
- Discord bot token
- Anthropic Claude API key

### Setup

1. **Set up the database:**
   ```bash
   # Create a PostgreSQL database
   createdb codenames
   ```

2. **Start the API server:**
   ```bash
   cd api-server
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your DATABASE_URL
   python bot.py
   ```

3. **Start the Discord bot:**
   ```bash
   cd discord-bot
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your Discord, Claude, and API server settings
   python bot.py
   ```

4. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Or read: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Environment Variables

Each service has its own `.env` file. See `.env.example` in each directory for required variables.

## Development

Each component can be developed independently:
- The API server runs standalone and can be tested via the interactive docs
- The Discord bot communicates with the API over HTTP
- The frontend will also communicate with the API over HTTP

## Technology Stack

- **Discord Bot**: discord.py, Anthropic Claude API, httpx
- **API Server**: FastAPI, PostgreSQL (psycopg2), uvicorn
- **Frontend**: TBD (React, Vue, or vanilla JS)

## Features

- Automatic game result extraction from screenshots using Claude AI
- Player statistics (overall, by role, team combinations)
- Edit functionality for correcting extracted data
- RESTful API for data access
- Automatic stats updates in Discord

## Database Schema

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete database schema.

## License

MIT (or specify your license)