CODENAMES_EXTRACTION_PROMPT = """Analyze this Codenames game screenshot and extract the game data.

IMPORTANT - Determining the winner:
- Look at the team panels on the left (Blue) and right (Red) sides
- The team with PLAYER NAMES listed in the Operatives/Spymasters sections is the LOSING team (the person who took this screenshot)
- The team with EMPTY Operatives/Spymasters sections is the WINNING team
- If you see "OPPOSING TEAM WINS!" banner, it means the team WITHOUT players listed won
- If you see "YOUR TEAM WINS!" banner, it means the team WITH players listed won

Return ONLY a JSON object with this structure:
{
  "blue_team": {
    "operatives": ["name1", "name2"],
    "spymasters": ["name3"]
  },
  "red_team": {
    "operatives": ["name4", "name5"],
    "spymasters": ["name6"]
  },
  "winner": "Blue" or "Red"
}

Return ONLY the JSON, no other text."""