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

def init_database():
    """Create tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP NOT NULL,
            winner TEXT NOT NULL,
            raw_data TEXT NOT NULL
        )
    ''')

    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Game participants table (links games to players)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_participants (
            id SERIAL PRIMARY KEY,
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            team TEXT NOT NULL,
            role TEXT NOT NULL,
            won BOOLEAN NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_or_create_player(name):
    """Get player ID, create if doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM players WHERE name = %s', (name,))
    result = cursor.fetchone()

    if result:
        player_id = result[0]
    else:
        cursor.execute('INSERT INTO players (name) VALUES (%s) RETURNING id', (name,))
        player_id = cursor.fetchone()[0]
        conn.commit()

    conn.close()
    return player_id

def save_game(game_data):
    """Save a game to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert game
    cursor.execute('''
        INSERT INTO games (date, winner, raw_data)
        VALUES (%s, %s, %s)
        RETURNING id
    ''', (datetime.now(), game_data['winner'], json.dumps(game_data)))

    game_id = cursor.fetchone()[0]

    # Insert participants
    for team_color in ['blue', 'red']:
        team_data = game_data[f'{team_color}_team']
        won = (game_data['winner'].lower() == team_color)

        # Operatives
        for player_name in team_data['operatives']:
            player_id = get_or_create_player(player_name)
            cursor.execute('''
                INSERT INTO game_participants (game_id, player_id, team, role, won)
                VALUES (%s, %s, %s, %s, %s)
            ''', (game_id, player_id, team_color.capitalize(), 'Operative', won))

        # Spymasters
        for player_name in team_data['spymasters']:
            player_id = get_or_create_player(player_name)
            cursor.execute('''
                INSERT INTO game_participants (game_id, player_id, team, role, won)
                VALUES (%s, %s, %s, %s, %s)
            ''', (game_id, player_id, team_color.capitalize(), 'Spymaster', won))

    conn.commit()
    conn.close()
    return game_id

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


def update_game(game_id, game_data):
    """Update an existing game with new data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update game
    cursor.execute('''
                   UPDATE games
                   SET winner   = %s,
                       raw_data = %s
                   WHERE id = %s
                   ''', (game_data['winner'], json.dumps(game_data), game_id))

    # Delete old participants
    cursor.execute('DELETE FROM game_participants WHERE game_id = %s', (game_id,))

    # Insert new participants
    for team_color in ['blue', 'red']:
        team_data = game_data[f'{team_color}_team']
        won = (game_data['winner'].lower() == team_color)

        # Operatives
        for player_name in team_data['operatives']:
            player_id = get_or_create_player(player_name)
            cursor.execute('''
                           INSERT INTO game_participants (game_id, player_id, team, role, won)
                           VALUES (%s, %s, %s, %s, %s)
                           ''', (game_id, player_id, team_color.capitalize(), 'Operative', won))

        # Spymasters
        for player_name in team_data['spymasters']:
            player_id = get_or_create_player(player_name)
            cursor.execute('''
                           INSERT INTO game_participants (game_id, player_id, team, role, won)
                           VALUES (%s, %s, %s, %s, %s)
                           ''', (game_id, player_id, team_color.capitalize(), 'Spymaster', won))

    conn.commit()
    conn.close()