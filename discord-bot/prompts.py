CODENAMES_EXTRACTION_PROMPT = """IMPORTANT - Determining the winner:
- Look at the team panels on the left (Blue) and right (Red) sides to get the names of all participating players. Ignore potential spectators that are listed in the top middle.
- Here is a list of known player names: %PLAYERS%
- If an extracted name is very similar to an existing player name, assume that you made an extraction error and use the existing player name instead. 
- Ignore the text at the top that states who won. It displays either "YOUR TEAM WINS" or "OTHER TEAM WINS" (potentially in a different language). It may also be missing if the image cropped it out.
- Check if the black assassin word was selected (look for the dark assassin figure on the board)
- If the assassin was selected:
  * Blue background = Blue team hit the assassin = Blue LOST = Red WON
  * Red background = Red team hit the assassin = Red LOST = Blue WON
  * The background color shows which team LOST by hitting the assassin, NOT which team won
- If no assassin was selected (normal game end):
  * Look at the numbers on each team panel
  * The team with 0 remaining cards is the WINNER
  * Example: Blue shows "1" and Red shows "0" → Red won

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