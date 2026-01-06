# Frontend Setup Complete

The Codenames Statistics frontend has been successfully built using Vue 3 and shadcn-vue.

## What Was Built

### 1. API Layer
- **Location**: `frontend/src/services/api.ts`
- **Purpose**: Centralized API communication with the FastAPI backend
- **Features**: TypeScript interfaces for all API responses

### 2. Components Created

#### GameLog.vue
Displays all games in a table format showing:
- Game ID and date
- Blue team players and roles
- Red team players and roles
- Winner with color-coded badges

#### PlayerLeaderboard.vue
Shows two leaderboards:
- Overall player statistics (wins, losses, win rate)
- Role-specific statistics (Operative vs Spymaster performance)
- Top 3 players get special badges

#### TeamLeaderboard.vue
Displays team combination statistics:
- Win/loss records for player combinations
- Filterable by minimum games played
- Top 20 combinations shown

#### CustomQuery.vue
Advanced filtering system:
- Select up to 2 players with specific roles
- Filter games by criteria like "Player A as Spymaster while Player B was Operative"
- Shows win statistics and matching games
- Real-time filtering

### 3. Pages/Views
- **HomeView**: Dashboard with overview and navigation cards
- **GamesView**: Full game history
- **PlayersView**: Player and team leaderboards
- **QueryView**: Custom query interface

### 4. Navigation & Layout
- Responsive header with navigation links
- Clean, modern design using Tailwind CSS
- Footer with branding

## API Enhancements

Added new endpoint to `api-server/`:
- `GET /api/games` - Returns all games with full details
- Added `get_all_games()` function to `database.py`

## How to Run

### Start the API Server (Terminal 1)
```bash
cd api-server
python bot.py
```

### Start the Frontend Dev Server (Terminal 2)
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn-vue components
│   │   ├── GameLog.vue
│   │   ├── PlayerLeaderboard.vue
│   │   ├── TeamLeaderboard.vue
│   │   └── CustomQuery.vue
│   ├── views/
│   │   ├── HomeView.vue
│   │   ├── GamesView.vue
│   │   ├── PlayersView.vue
│   │   └── QueryView.vue
│   ├── services/
│   │   └── api.ts           # API service layer
│   ├── types/
│   │   └── api.ts           # TypeScript types
│   ├── router/
│   │   └── index.ts         # Vue Router config
│   ├── App.vue              # Main app component
│   └── main.ts              # Entry point
├── .env                     # Environment config
├── .env.example             # Example env file
└── components.json          # shadcn-vue config
```

## Tech Stack

- **Vue 3** with Composition API
- **TypeScript** for type safety
- **shadcn-vue** for UI components
- **Tailwind CSS v4** for styling
- **Vue Router** for navigation
- **Vite** for fast development

## Features Implemented

✅ Game log with detailed team compositions
✅ Player leaderboard (overall and by role)
✅ Team combinations leaderboard
✅ Custom query with advanced filtering
✅ Responsive design
✅ TypeScript support
✅ Clean, modern UI
✅ Color-coded win rates
✅ Real-time data from API

## Next Steps (Optional Enhancements)

1. **Auto-refresh**: Add polling to automatically fetch new data every 5-10 seconds
2. **Charts**: Add visualizations using Chart.js or similar
3. **Date filtering**: Filter games by date range
4. **Player profiles**: Individual player detail pages
5. **Export data**: Download statistics as CSV/JSON
6. **Dark mode toggle**: Allow users to switch themes
7. **Search**: Search players and games
8. **Pagination**: For large datasets
9. **Sorting**: Allow sorting by different columns
10. **Mobile navigation**: Hamburger menu for mobile devices

## Notes

- The custom query feature filters games client-side for better performance
- All data is fetched fresh on component mount
- The API must be running for the frontend to work
- CORS is already configured on the API server
