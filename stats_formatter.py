import discord
from database import get_player_stats, get_player_stats_by_role, get_total_games


def format_stats_embed():
    """Create a Discord embed with formatted stats"""
    embed = discord.Embed(
        title="📊 Codenames Statistics",
        color=discord.Color.blue()
    )

    total_games = get_total_games()
    embed.description = f"Total games played: **{total_games}**"

    # Overall stats
    overall_stats = get_player_stats()
    if overall_stats:
        leaderboard = "\n".join([
            f"{i + 1}. **{name}**: {wins}-{losses} ({win_rate}%)"
            for i, (name, total, wins, losses, win_rate) in enumerate(overall_stats)
        ])
        embed.add_field(
            name="🏆 Overall Leaderboard",
            value=leaderboard or "No games yet",
            inline=False
        )

    # Stats by role
    role_stats = get_player_stats_by_role()

    # Group by role
    operative_stats = [s for s in role_stats if s[1] == 'Operative']
    spymaster_stats = [s for s in role_stats if s[1] == 'Spymaster']

    if operative_stats:
        operative_text = "\n".join([
            f"**{name}**: {wins}/{total} ({win_rate}%)"
            for name, role, total, wins, win_rate in operative_stats[:10]
        ])
        embed.add_field(
            name="🎯 Operative Win Rates",
            value=operative_text,
            inline=True
        )

    if spymaster_stats:
        spymaster_text = "\n".join([
            f"**{name}**: {wins}/{total} ({win_rate}%)"
            for name, role, total, wins, win_rate in spymaster_stats[:10]
        ])
        embed.add_field(
            name="🕵️ Spymaster Win Rates",
            value=spymaster_text,
            inline=True
        )

    embed.set_footer(text="Stats update automatically after each game")

    return embed