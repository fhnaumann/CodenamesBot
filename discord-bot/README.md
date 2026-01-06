# Codenames Discord Bot

Discord bot that processes Codenames game screenshots and tracks statistics.

## Features

- Listens for image uploads in a specified Discord channel
- Uses Claude AI to extract game data from screenshots
- Submits game data to the API server
- Displays stats in a pinned message
- Provides inline editing for game corrections

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (or copy `.env.example`):

```bash
DISCORD_KEY=your_discord_bot_token
CHANNEL_ID=your_channel_id
CLAUDE_KEY=your_claude_api_key
API_SERVER_URL=http://localhost:8000
```

## Running

```bash
python main.py
```

## Usage

1. Upload a Codenames game result screenshot to the configured Discord channel
2. The bot will:
   - React with ⏳ while processing
   - Extract game data using Claude AI
   - Submit to the API server
   - Reply with the game result
   - Update the pinned stats message
   - React with ✅ on success or ❌ on error

3. Click "✏️ Edit Game" button to correct any extraction errors

## Files

- `main.py` - Main bot logic and message handling
- `views.py` - Discord UI components (edit button/modal)
- `stats_formatter.py` - Formats stats into Discord embeds
- `prompts.py` - Claude AI prompts for extraction

## Dependencies

- discord.py - Discord API wrapper
- anthropic - Claude AI API
- httpx - HTTP client for API calls
- python-dotenv - Environment variable management