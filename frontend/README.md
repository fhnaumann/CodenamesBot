# Codenames Statistics Frontend

A Vue 3 application for tracking and analyzing Codenames game statistics.

## Features

### 1. Game History
- View all games played with detailed team compositions
- Shows which players were on each team and their roles (Operative/Spymaster)
- Displays game outcomes with color-coded winner badges
- Sortable table with game IDs and timestamps

### 2. Player Leaderboards
- **Overall Leaderboard**: Rankings by win rate with games played, wins, and losses
- **Role-Specific Stats**: Performance breakdown by Operative vs Spymaster roles
- Color-coded win rates for easy identification of top performers
- Badges for top 3 ranked players

### 3. Team Combinations
- Analyzes which team lineups perform best together
- Filterable by minimum games played (1+, 2+, 3+, 5+, 10+)
- Shows win/loss records and win rates for each combination
- Limited to top 20 combinations for better performance

### 4. Custom Query
- Filter games by specific players and roles
- Support for multi-player queries (e.g., "Player A as Spymaster while Player B was Operative")
- Real-time win rate calculations based on filter criteria
- Lists all matching games with outcomes

## Tech Stack

- **Framework**: Vue 3 with TypeScript
- **UI Components**: shadcn-vue (based on Radix UI)
- **Styling**: Tailwind CSS v4
- **Routing**: Vue Router
- **State Management**: Pinia
- **Build Tool**: Vite

## Setup

### Prerequisites
- Node.js 20.19.0+ or 22.12.0+
- API server running (see `../api-server/README.md`)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure the API URL:
```bash
cp .env.example .env
# Edit .env and set VITE_API_URL to your API server URL
# Default: http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
npm run preview  # Preview the production build
```

## Project Structure

```
src/
├── components/          # Reusable Vue components
│   ├── ui/             # shadcn-vue UI components
│   ├── GameLog.vue     # Game history table
│   ├── PlayerLeaderboard.vue
│   ├── TeamLeaderboard.vue
│   └── CustomQuery.vue
├── views/              # Page components
│   ├── HomeView.vue
│   ├── GamesView.vue
│   ├── PlayersView.vue
│   └── QueryView.vue
├── services/           # API service layer
│   └── api.ts
├── types/              # TypeScript type definitions
│   └── api.ts
├── router/             # Vue Router configuration
│   └── index.ts
├── App.vue             # Root component
└── main.ts             # Application entry point
```

## API Integration

The frontend communicates with the FastAPI backend through the API service layer (`src/services/api.ts`). All API calls are centralized here for easy maintenance.

### Available Endpoints
- `GET /api/games` - Fetch all games
- `GET /api/stats/players` - Player statistics
- `GET /api/stats/players/by-role` - Role-specific stats
- `GET /api/stats/team-combinations` - Team combination stats
- `GET /api/stats/total-games` - Total game count

## Development Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Run TypeScript type checking
- `npm run lint` - Lint and fix code
- `npm run format` - Format code with Prettier
- `npm run test:unit` - Run unit tests
- `npm run test:e2e` - Run end-to-end tests

## Customization

### Styling
The application uses Tailwind CSS with shadcn-vue's design system. You can customize the theme in:
- `src/styles.css` - Global styles and CSS variables
- `components.json` - shadcn-vue configuration

### Adding New Components
Use the shadcn-vue CLI to add new UI components:
```bash
npx shadcn-vue add [component-name]
```

## Notes

- The application expects the API server to be running and accessible
- CORS is configured on the API server to allow frontend access
- Data is fetched on component mount and can be refreshed by navigating away and back
- The custom query feature filters games client-side for better performance with small datasets