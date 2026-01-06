import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import os

def get_db_connection():
    """Get database connection from environment variable"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not set in environment")
    return psycopg2.connect(database_url)

def get_or_create_player(name, cursor=None):
    """Get player ID, create if doesn't exist"""
    close_conn = False
    if cursor is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True

    cursor.execute('SELECT id FROM players WHERE name = %s', (name,))
    result = cursor.fetchone()

    if result:
        player_id = result[0]
    else:
        cursor.execute('INSERT INTO players (name) VALUES (%s) RETURNING id', (name,))
        player_id = cursor.fetchone()[0]
        if close_conn:
            conn.commit()

    if close_conn:
        conn.close()
    return player_id

def get_player_stats():
    """Get overall stats for all players"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            p.name,
            COUNT(*) as total_games,
            SUM(CASE WHEN gp.won = TRUE THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN gp.won = FALSE THEN 1 ELSE 0 END) as losses,
            ROUND(100.0 * SUM(CASE WHEN gp.won = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate
        FROM players p
        JOIN game_participants gp ON p.id = gp.player_id
        GROUP BY p.name
        ORDER BY win_rate DESC, wins DESC
    ''')

    results = cursor.fetchall()
    conn.close()
    return results

def get_player_stats_by_role():
    """Get stats broken down by role (Operative vs Spymaster)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            p.name,
            gp.role,
            COUNT(*) as total_games,
            SUM(CASE WHEN gp.won = TRUE THEN 1 ELSE 0 END) as wins,
            ROUND(100.0 * SUM(CASE WHEN gp.won = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate
        FROM players p
        JOIN game_participants gp ON p.id = gp.player_id
        GROUP BY p.name, gp.role
        ORDER BY gp.role, win_rate DESC
    ''')

    results = cursor.fetchall()
    conn.close()
    return results

def get_total_games():
    """Get total number of games"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM games')
    result = cursor.fetchone()[0]
    conn.close()
    return result


def init_database():
    """Create tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Games table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS games
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       date
                       TIMESTAMP
                       NOT
                       NULL,
                       winner
                       TEXT
                       NOT
                       NULL,
                       raw_data
                       TEXT
                       NOT
                       NULL
                   )
                   ''')

    # Players table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS players
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       UNIQUE
                       NOT
                       NULL
                   )
                   ''')

    # Game participants table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS game_participants
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       game_id
                       INTEGER
                       NOT
                       NULL,
                       player_id
                       INTEGER
                       NOT
                       NULL,
                       team
                       TEXT
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL,
                       won
                       BOOLEAN
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       game_id
                   ) REFERENCES games
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       player_id
                   ) REFERENCES players
                   (
                       id
                   )
                       )
                   ''')

    # Team combinations table - stores all possible combinations
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS team_combinations
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       player_names
                       TEXT
                       NOT
                       NULL,
                       wins
                       INTEGER
                       DEFAULT
                       0,
                       losses
                       INTEGER
                       DEFAULT
                       0,
                       UNIQUE
                   (
                       player_names
                   )
                       )
                   ''')

    conn.commit()
    conn.close()


def get_all_combinations(players):
    """Generate all possible combinations of players (2+)"""
    from itertools import combinations

    # Sort players to ensure consistent ordering
    players = sorted(players)

    combos = []
    # Generate combinations of size 2 to len(players)
    for r in range(2, len(players) + 1):
        for combo in combinations(players, r):
            combos.append(','.join(sorted(combo)))

    return combos


def update_team_combinations(player_names, won, cursor=None):
    """Update win/loss for all combinations of these players"""
    close_conn = False
    if cursor is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True

    combos = get_all_combinations(player_names)

    for combo_str in combos:
        # Get or create combination
        cursor.execute('''
                       INSERT INTO team_combinations (player_names, wins, losses)
                       VALUES (%s, 0, 0) ON CONFLICT (player_names) DO NOTHING
                       ''', (combo_str,))

        # Update wins or losses
        if won:
            cursor.execute('''
                           UPDATE team_combinations
                           SET wins = wins + 1
                           WHERE player_names = %s
                           ''', (combo_str,))
        else:
            cursor.execute('''
                           UPDATE team_combinations
                           SET losses = losses + 1
                           WHERE player_names = %s
                           ''', (combo_str,))

    if close_conn:
        conn.commit()
        conn.close()


def save_game(game_data):
    """Save a game to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert game
    cursor.execute('''
                   INSERT INTO games (date, winner, raw_data)
                   VALUES (%s, %s, %s) RETURNING id
                   ''', (datetime.now(), game_data['winner'], json.dumps(game_data)))

    game_id = cursor.fetchone()[0]

    # Insert participants and track team combinations
    for team_color in ['blue', 'red']:
        team_data = game_data[f'{team_color}_team']
        won = (game_data['winner'].lower() == team_color)

        # Collect all player names for this team
        all_team_players = team_data['operatives'] + team_data['spymasters']

        # Operatives
        for player_name in team_data['operatives']:
            player_id = get_or_create_player(player_name, cursor)
            cursor.execute('''
                           INSERT INTO game_participants (game_id, player_id, team, role, won)
                           VALUES (%s, %s, %s, %s, %s)
                           ''', (game_id, player_id, team_color.capitalize(), 'Operative', won))

        # Spymasters
        for player_name in team_data['spymasters']:
            player_id = get_or_create_player(player_name, cursor)
            cursor.execute('''
                           INSERT INTO game_participants (game_id, player_id, team, role, won)
                           VALUES (%s, %s, %s, %s, %s)
                           ''', (game_id, player_id, team_color.capitalize(), 'Spymaster', won))

        # Update team combinations for this team
        if all_team_players:
            update_team_combinations(all_team_players, won, cursor)

    conn.commit()
    conn.close()
    return game_id


def update_game(game_id, game_data):
    """Update an existing game with new data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get old game data to reverse team combination stats
    cursor.execute('SELECT raw_data FROM games WHERE id = %s', (game_id,))
    old_data = json.loads(cursor.fetchone()[0])

    # Reverse old team combinations
    for team_color in ['blue', 'red']:
        old_team_data = old_data[f'{team_color}_team']
        old_won = (old_data['winner'].lower() == team_color)
        all_old_players = old_team_data['operatives'] + old_team_data['spymasters']

        if all_old_players:
            combos = get_all_combinations(all_old_players)
            for combo_str in combos:
                if old_won:
                    cursor.execute('UPDATE team_combinations SET wins = wins - 1 WHERE player_names = %s', (combo_str,))
                else:
                    cursor.execute('UPDATE team_combinations SET losses = losses - 1 WHERE player_names = %s',
                                   (combo_str,))

    # Update game
    cursor.execute('''
                   UPDATE games
                   SET winner   = %s,
                       raw_data = %s
                   WHERE id = %s
                   ''', (game_data['winner'], json.dumps(game_data), game_id))

    # Delete old participants
    cursor.execute('DELETE FROM game_participants WHERE game_id = %s', (game_id,))

    # Insert new participants and update team combinations
    for team_color in ['blue', 'red']:
        team_data = game_data[f'{team_color}_team']
        won = (game_data['winner'].lower() == team_color)

        all_team_players = team_data['operatives'] + team_data['spymasters']

        # Operatives
        for player_name in team_data['operatives']:
            player_id = get_or_create_player(player_name, cursor)
            cursor.execute('''
                           INSERT INTO game_participants (game_id, player_id, team, role, won)
                           VALUES (%s, %s, %s, %s, %s)
                           ''', (game_id, player_id, team_color.capitalize(), 'Operative', won))

        # Spymasters
        for player_name in team_data['spymasters']:
            player_id = get_or_create_player(player_name, cursor)
            cursor.execute('''
                           INSERT INTO game_participants (game_id, player_id, team, role, won)
                           VALUES (%s, %s, %s, %s, %s)
                           ''', (game_id, player_id, team_color.capitalize(), 'Spymaster', won))

        # Update new team combinations
        if all_team_players:
            update_team_combinations(all_team_players, won, cursor)

    conn.commit()
    conn.close()


def delete_game(game_id):
    """Delete a game and reverse all associated stats"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get game data to reverse team combination stats
    cursor.execute('SELECT raw_data FROM games WHERE id = %s', (game_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise ValueError(f"Game {game_id} not found")

    game_data = json.loads(result[0])

    # Reverse team combinations
    for team_color in ['blue', 'red']:
        team_data = game_data[f'{team_color}_team']
        won = (game_data['winner'].lower() == team_color)
        all_team_players = team_data['operatives'] + team_data['spymasters']

        if all_team_players:
            combos = get_all_combinations(all_team_players)
            for combo_str in combos:
                if won:
                    cursor.execute('UPDATE team_combinations SET wins = wins - 1 WHERE player_names = %s', (combo_str,))
                else:
                    cursor.execute('UPDATE team_combinations SET losses = losses - 1 WHERE player_names = %s', (combo_str,))

    # Delete game participants
    cursor.execute('DELETE FROM game_participants WHERE game_id = %s', (game_id,))

    # Delete the game
    cursor.execute('DELETE FROM games WHERE id = %s', (game_id,))

    conn.commit()
    conn.close()


def get_team_combination_stats(min_games=2):
    """Get stats for team combinations with at least min_games played"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT player_names,
                          wins,
                          losses,
                          wins + losses                            as total_games,
                          ROUND(100.0 * wins / (wins + losses), 1) as win_rate
                   FROM team_combinations
                   WHERE wins + losses >= %s
                   ORDER BY win_rate DESC, total_games DESC LIMIT 20
                   ''', (min_games,))

    results = cursor.fetchall()
    conn.close()
    return results


def get_all_games():
    """Get all games with their details"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute('''
                   SELECT
                       g.id,
                       g.date,
                       g.winner,
                       g.raw_data
                   FROM games g
                   ORDER BY g.date DESC
                   ''')

    games = cursor.fetchall()
    conn.close()

    # Parse raw_data JSON for each game
    result = []
    for game in games:
        game_dict = dict(game)
        game_dict['raw_data'] = json.loads(game_dict['raw_data'])
        result.append(game_dict)

    return result


def get_team_combination_stats_with_roles(min_games=2):
    """Get stats for team combinations with role information"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get all unique winning team configurations from actual games
    cursor.execute('''
        WITH team_games AS (
            SELECT
                g.id as game_id,
                g.winner,
                gp.team,
                gp.won,
                ARRAY_AGG(
                    CASE WHEN gp.role = 'Spymaster' THEN p.name ELSE NULL END
                    ORDER BY p.name
                ) FILTER (WHERE gp.role = 'Spymaster') as spymasters,
                ARRAY_AGG(
                    CASE WHEN gp.role = 'Operative' THEN p.name ELSE NULL END
                    ORDER BY p.name
                ) FILTER (WHERE gp.role = 'Operative') as operatives
            FROM games g
            JOIN game_participants gp ON g.id = gp.game_id
            JOIN players p ON gp.player_id = p.id
            GROUP BY g.id, g.winner, gp.team, gp.won
        ),
        team_combos AS (
            SELECT
                COALESCE(ARRAY_TO_STRING(spymasters, ','), '') || '|' ||
                COALESCE(ARRAY_TO_STRING(operatives, ','), '') as team_key,
                spymasters,
                operatives,
                won,
                COUNT(*) as game_count
            FROM team_games
            WHERE ARRAY_LENGTH(spymasters, 1) > 0 OR ARRAY_LENGTH(operatives, 1) > 0
            GROUP BY team_key, spymasters, operatives, won
        )
        SELECT
            spymasters,
            operatives,
            SUM(CASE WHEN won THEN game_count ELSE 0 END) as wins,
            SUM(CASE WHEN NOT won THEN game_count ELSE 0 END) as losses,
            SUM(game_count) as total_games,
            ROUND(100.0 * SUM(CASE WHEN won THEN game_count ELSE 0 END) / SUM(game_count), 1) as win_rate
        FROM team_combos
        GROUP BY team_key, spymasters, operatives
        HAVING SUM(game_count) >= %s
        ORDER BY win_rate DESC, total_games DESC
        LIMIT 20
    ''', (min_games,))

    results = cursor.fetchall()
    conn.close()

    # Convert to list of dicts with formatted data
    formatted_results = []
    for row in results:
        formatted_results.append({
            'spymasters': row['spymasters'] or [],
            'operatives': row['operatives'] or [],
            'wins': row['wins'],
            'losses': row['losses'],
            'total_games': row['total_games'],
            'win_rate': float(row['win_rate'])
        })

    return formatted_results

