import os
import discord
import httpx

API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://localhost:8000')


def format_stats_embed():
    """Create a Discord embed with formatted stats"""
    embed = discord.Embed(
        title="📊 Codenames Statistics",
        color=discord.Color.blue()
    )

    try:
        # Use synchronous httpx client
        with httpx.Client(timeout=10.0) as client:
            # Get total games
            response = client.get(f"{API_SERVER_URL}/api/stats/total-games")
            response.raise_for_status()
            total_games = response.json()['total_games']
            embed.description = f"Total games played: **{total_games}**"

            # Overall stats
            response = client.get(f"{API_SERVER_URL}/api/stats/players")
            response.raise_for_status()
            overall_stats = response.json()

            if overall_stats:
                leaderboard = "\n".join([
                    f"{i + 1}. **{stat['name']}**: {stat['wins']}-{stat['losses']} ({stat['win_rate']}%)"
                    for i, stat in enumerate(overall_stats[:10])
                ])
                embed.add_field(
                    name="🏆 Overall Leaderboard",
                    value=leaderboard or "No games yet",
                    inline=False
                )

            # Stats by role
            response = client.get(f"{API_SERVER_URL}/api/stats/players/by-role")
            response.raise_for_status()
            role_stats = response.json()

            # Group by role
            operative_stats = [s for s in role_stats if s['role'] == 'Operative']
            spymaster_stats = [s for s in role_stats if s['role'] == 'Spymaster']

            if operative_stats:
                operative_text = "\n".join([
                    f"**{stat['name']}**: {stat['wins']}/{stat['total_games']} ({stat['win_rate']}%)"
                    for stat in operative_stats[:10]
                ])
                embed.add_field(
                    name="🎯 Operative Win Rates",
                    value=operative_text,
                    inline=True
                )

            if spymaster_stats:
                spymaster_text = "\n".join([
                    f"**{stat['name']}**: {stat['wins']}/{stat['total_games']} ({stat['win_rate']}%)"
                    for stat in spymaster_stats[:10]
                ])
                embed.add_field(
                    name="🕵️ Spymaster Win Rates",
                    value=spymaster_text,
                    inline=True
                )

            # Team combination stats
            response = client.get(f"{API_SERVER_URL}/api/stats/team-combinations", params={"min_games": 1})
            response.raise_for_status()
            team_combos = response.json()

            if team_combos:
                combo_text = "\n".join([
                    f"**{combo['player_names'].replace(',', ' + ')}**: {combo['wins']}-{combo['losses']} ({combo['win_rate']}%)"
                    for combo in team_combos[:10]
                ])
                embed.add_field(
                    name="🤝 Best Team Combinations (2+ games)",
                    value=combo_text or "Not enough games yet",
                    inline=False
                )

    except Exception as e:
        embed.description = f"⚠️ Error fetching stats: {str(e)}"

    embed.set_footer(text="Stats update automatically after each game")

    return embed