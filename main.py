import base64
import json
import os

import anthropic
import discord
from PIL import Image
from dotenv import load_dotenv
from pytesseract import pytesseract

from database import save_game
from prompts import CODENAMES_EXTRACTION_PROMPT
from stats_formatter import format_stats_embed

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Add this line!

client = discord.Client(intents=intents)

TARGET_CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
DISCORD_KEY = os.getenv('DISCORD_KEY')
CLAUDE_KEY = os.getenv('CLAUDE_KEY')

anthropic_client = anthropic.Anthropic(api_key=CLAUDE_KEY)

@client.event
async def on_ready():
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
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Call Claude
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": CODENAMES_EXTRACTION_PROMPT
                }
            ]
        }]
    )

    # Parse response
    response_text = message.content[0].text.strip()
    print(f"Claude response: {response_text}")

    # Extract JSON (in case Claude adds markdown formatting)
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    return json.loads(response_text)
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

                # Download image
                image_path = f'temp_{attachment.filename}'
                await attachment.save(image_path)

                # Extract data
                game_data = extract_game_data_with_claude(image_path)
                print("Extracted game data:", json.dumps(game_data, indent=2))

                # Save to database
                game_id = save_game(game_data)
                print(f"Saved game #{game_id}")

                # Update stats message
                await update_stats_message(message.channel)

                # Clean up
                os.remove(image_path)

                await message.remove_reaction('⏳', client.user)
                await message.add_reaction('✅')

client.run(DISCORD_KEY)
