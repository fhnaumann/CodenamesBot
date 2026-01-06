import base64
import json
import os

import anthropic
import discord
import httpx
from dotenv import load_dotenv

from prompts import CODENAMES_EXTRACTION_PROMPT
from stats_formatter import format_stats_embed
from views import EditGameButton

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TARGET_CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
DISCORD_KEY = os.getenv('DISCORD_KEY')
CLAUDE_KEY = os.getenv('CLAUDE_KEY')
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://localhost:8000')

anthropic_client = anthropic.Anthropic(api_key=CLAUDE_KEY)

stats_message_id = None

@client.event
async def on_ready():
    # Check API server health
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.get(f"{API_SERVER_URL}/health")
            if response.status_code == 200:
                print(f'API server is healthy: {response.json()}')
            else:
                print(f'Warning: API server returned status {response.status_code}')
        except Exception as e:
            print(f'Warning: Could not connect to API server: {e}')

    print(f'We have logged in as {client.user}')


async def update_stats_message(channel):
    """Update or create the pinned stats message"""
    global stats_message_id

    embed = format_stats_embed()

    if stats_message_id:
        try:
            msg = await channel.fetch_message(stats_message_id)
            await msg.edit(embed=embed)
            return
        except:
            stats_message_id = None

    # Create new message
    msg = await channel.send(embed=embed)
    await msg.pin()
    stats_message_id = msg.id

def extract_game_data_with_claude(image_path):
    """Use Claude Vision to extract game data from screenshot"""

    # Read and encode image
    # with open(image_path, 'rb') as f:
    #     image_data = base64.b64encode(f.read()).decode('utf-8')
    #
    # # Call Claude
    # message = anthropic_client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=1024,
    #     messages=[{
    #         "role": "user",
    #         "content": [
    #             {
    #                 "type": "image",
    #                 "source": {
    #                     "type": "base64",
    #                     "media_type": "image/png",
    #                     "data": image_data
    #                 }
    #             },
    #             {
    #                 "type": "text",
    #                 "text": CODENAMES_EXTRACTION_PROMPT
    #             }
    #         ]
    #     }]
    # )
    #
    # # Parse response
    # response_text = message.content[0].text.strip()
    # print(f"Claude response: {response_text}")
    #
    # # Extract JSON (in case Claude adds markdown formatting)
    # if "```json" in response_text:
    #     response_text = response_text.split("```json")[1].split("```")[0].strip()
    # elif "```" in response_text:
    #     response_text = response_text.split("```")[1].split("```")[0].strip()
    #
    # return json.loads(response_text)
    return {
  "blue_team": {
    "operatives": [
      "Felix", "Julia"
    ],
    "spymasters": ["Diana", "Nabi"]
  },
  "red_team": {
    "operatives": [],
    "spymasters": []
  },
  "winner": "Red"
}


def parse_embed_to_game_data(embed):
    """Parse a Discord embed back into game_data format"""
    game_data = {
        'blue_team': {'operatives': [], 'spymasters': []},
        'red_team': {'operatives': [], 'spymasters': []},
        'winner': None
    }

    # Extract winner from first field
    for field in embed.fields:
        if field.name == "🏆 Winner":
            game_data['winner'] = field.value.replace('**', '').replace(' Team', '').strip()

        elif field.name == "🔵 Blue Team":
            lines = field.value.split('\n')
            for line in lines:
                if line.startswith('Operatives:'):
                    ops = line.replace('Operatives:', '').strip()
                    if ops and ops != 'None':
                        game_data['blue_team']['operatives'] = [p.strip() for p in ops.split(',')]
                elif line.startswith('Spymasters:'):
                    spy = line.replace('Spymasters:', '').strip()
                    if spy and spy != 'None':
                        game_data['blue_team']['spymasters'] = [p.strip() for p in spy.split(',')]

        elif field.name == "🔴 Red Team":
            lines = field.value.split('\n')
            for line in lines:
                if line.startswith('Operatives:'):
                    ops = line.replace('Operatives:', '').strip()
                    if ops and ops != 'None':
                        game_data['red_team']['operatives'] = [p.strip() for p in ops.split(',')]
                elif line.startswith('Spymasters:'):
                    spy = line.replace('Spymasters:', '').strip()
                    if spy and spy != 'None':
                        game_data['red_team']['spymasters'] = [p.strip() for p in spy.split(',')]

    return game_data

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # Only listen to specific channel
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    # Check if message has attachments (images)
    if message.attachments:
        for attachment in message.attachments:
            # Check if it's an image
            if attachment.content_type and attachment.content_type.startswith('image/'):
                print(f'Image detected: {attachment.filename}')

                # React to show we're processing
                await message.add_reaction('⏳')

                try:
                    image_path = f'temp_{attachment.filename}'
                    await attachment.save(image_path)

                    game_data = extract_game_data_with_claude(image_path)
                    print("Extracted game data:", json.dumps(game_data, indent=2))

                    # Save to database via API
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{API_SERVER_URL}/api/games",
                            json=game_data,
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()
                        game_id = result['game_id']
                        print(f"Saved game #{game_id}")

                    # Send immediate response with game result
                    result_embed = discord.Embed(
                        title=f"🎮 Game #{game_id} Recorded",
                        color=discord.Color.blue() if game_data['winner'] == 'Blue' else discord.Color.red()
                    )

                    result_embed.add_field(
                        name="🏆 Winner",
                        value=f"**{game_data['winner']} Team**",
                        inline=False
                    )

                    blue_ops = ", ".join(game_data['blue_team']['operatives']) or "None"
                    blue_spy = ", ".join(game_data['blue_team']['spymasters']) or "None"
                    result_embed.add_field(
                        name="🔵 Blue Team",
                        value=f"Operatives: {blue_ops}\nSpymasters: {blue_spy}",
                        inline=True
                    )

                    red_ops = ", ".join(game_data['red_team']['operatives']) or "None"
                    red_spy = ", ".join(game_data['red_team']['spymasters']) or "None"
                    result_embed.add_field(
                        name="🔴 Red Team",
                        value=f"Operatives: {red_ops}\nSpymasters: {red_spy}",
                        inline=True
                    )

                    # Add the edit button
                    view = EditGameButton(game_id, game_data, update_stats_message)

                    await message.reply(embed=result_embed, view=view)

                    # Update pinned stats message
                    await update_stats_message(message.channel)

                    os.remove(image_path)

                    await message.remove_reaction('⏳', client.user)
                    await message.add_reaction('✅')

                except Exception as e:
                    print(f"Error: {e}")
                    import traceback
                    traceback.print_exc()
                    await message.remove_reaction('⏳', client.user)
                    await message.add_reaction('❌')
                    await message.reply(f"❌ Error processing game: {str(e)}")

client.run(DISCORD_KEY)
