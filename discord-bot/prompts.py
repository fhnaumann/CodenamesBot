CODENAMES_EXTRACTION_PROMPT = """Analyze this Codenames game screenshot and extract the game data.

IMPORTANT - Determining the winner:
- Look at the team panels on the left (Blue) and right (Red) sides
- There are two numbers: One on the left and one on the right. The team where the number is smaller than the other number has won the game. So if the left number is smaller, the blue team won. If the right number is smaller, the red team won.
- If the black word was selected (one exists per game) don't look at the numbers at all. Instead look at the background color of the image. If it's blue then that means that the blue team selected the black word and therefore lost. If the background is red then that means that the red team selected the black word and therefore lost.
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