import os
import discord
import httpx

API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://localhost:8000')


class EditGameButton(discord.ui.View):
    def __init__(self, game_id, game_data, update_stats_callback):
        super().__init__(timeout=None)
        self.game_id = game_id
        self.game_data = game_data
        self.update_stats_callback = update_stats_callback

    @discord.ui.button(label="✏️ Edit Game", style=discord.ButtonStyle.secondary)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EditGameModal(self.game_id, self.game_data, self.update_stats_callback)
        await interaction.response.send_modal(modal)


class EditGameModal(discord.ui.Modal, title="Edit Game Data"):
    def __init__(self, game_id, game_data, update_stats_callback):
        super().__init__()
        self.game_id = game_id
        self.update_stats_callback = update_stats_callback

        # Winner
        self.winner_input = discord.ui.TextInput(
            label="Winner (Blue or Red)",
            default=game_data['winner'],
            max_length=4
        )

        # Blue team operatives
        blue_ops = ", ".join(game_data['blue_team']['operatives'])
        self.blue_ops_input = discord.ui.TextInput(
            label="Blue Operatives (comma separated)",
            default=blue_ops,
            required=False,
            max_length=200
        )

        # Blue team spymasters
        blue_spy = ", ".join(game_data['blue_team']['spymasters'])
        self.blue_spy_input = discord.ui.TextInput(
            label="Blue Spymasters (comma separated)",
            default=blue_spy,
            required=False,
            max_length=200
        )

        # Red team operatives
        red_ops = ", ".join(game_data['red_team']['operatives'])
        self.red_ops_input = discord.ui.TextInput(
            label="Red Operatives (comma separated)",
            default=red_ops,
            required=False,
            max_length=200
        )

        # Red team spymasters
        red_spy = ", ".join(game_data['red_team']['spymasters'])
        self.red_spy_input = discord.ui.TextInput(
            label="Red Spymasters (comma separated)",
            default=red_spy,
            required=False,
            max_length=200
        )

        self.add_item(self.winner_input)
        self.add_item(self.blue_ops_input)
        self.add_item(self.blue_spy_input)
        self.add_item(self.red_ops_input)
        self.add_item(self.red_spy_input)

    async def on_submit(self, interaction: discord.Interaction):
        # MUST respond within 3 seconds - defer first
        await interaction.response.defer(ephemeral=True)

        try:
            # Parse input
            winner = self.winner_input.value.strip().capitalize()

            if winner not in ['Blue', 'Red']:
                await interaction.followup.send("❌ Winner must be 'Blue' or 'Red'", ephemeral=True)
                return

            # Build updated game data
            game_data = {
                'winner': winner,
                'blue_team': {
                    'operatives': [p.strip() for p in self.blue_ops_input.value.split(',') if p.strip()],
                    'spymasters': [p.strip() for p in self.blue_spy_input.value.split(',') if p.strip()]
                },
                'red_team': {
                    'operatives': [p.strip() for p in self.red_ops_input.value.split(',') if p.strip()],
                    'spymasters': [p.strip() for p in self.red_spy_input.value.split(',') if p.strip()]
                }
            }

            # Update database via API
            async with httpx.AsyncClient() as http_client:
                response = await http_client.put(
                    f"{API_SERVER_URL}/api/games/{self.game_id}",
                    json=game_data,
                    timeout=10.0
                )
                response.raise_for_status()

            # Update the embed
            new_embed = discord.Embed(
                title=f"🎮 Game #{self.game_id} Recorded (Updated)",
                color=discord.Color.blue() if game_data['winner'] == 'Blue' else discord.Color.red()
            )

            new_embed.add_field(
                name="🏆 Winner",
                value=f"**{game_data['winner']} Team**",
                inline=False
            )

            blue_ops = ", ".join(game_data['blue_team']['operatives']) or "None"
            blue_spy = ", ".join(game_data['blue_team']['spymasters']) or "None"
            new_embed.add_field(
                name="🔵 Blue Team",
                value=f"Operatives: {blue_ops}\nSpymasters: {blue_spy}",
                inline=True
            )

            red_ops = ", ".join(game_data['red_team']['operatives']) or "None"
            red_spy = ", ".join(game_data['red_team']['spymasters']) or "None"
            new_embed.add_field(
                name="🔴 Red Team",
                value=f"Operatives: {red_ops}\nSpymasters: {red_spy}",
                inline=True
            )

            # Edit original message with updated button
            await interaction.message.edit(
                embed=new_embed,
                view=EditGameButton(self.game_id, game_data, self.update_stats_callback)
            )

            # Update stats message
            await self.update_stats_callback(interaction.channel)

            # Send success message
            await interaction.followup.send("✅ Game updated successfully!", ephemeral=True)

        except Exception as e:
            print(f"Error updating game: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)