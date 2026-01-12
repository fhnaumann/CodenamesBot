CODENAMES_EXTRACTION_PROMPT = """IMPORTANT - Extracting stats from screenshot:
- Look at the team panels on the left (Blue) and right (Red) sides to get the names of all participating players. Ignore potential spectators that are listed in the top middle.
- Here is a list of known player names: %PLAYERS%
- If an extracted name is very similar to an existing player name, assume that you made an extraction error and use the existing player name instead. 
- Ignore the text at the top that states who won. It displays either "YOUR TEAM WINS" or "OTHER TEAM WINS" (potentially in a different language). It may also be missing if the image cropped it out.
- Check if the black assassin word was selected (look for cards on the board):
  * ASSASSIN NOT SELECTED: If you can still see the text/word on the assassin card clearly visible, it has NOT been picked. This is a normal game end.
  * ASSASSIN SELECTED: If the assassin card is covered by a dark figure/artwork (the card image covers the text), then it WAS picked.
- If the assassin was selected (card covered by artwork):
  * Blue background on covered assassin = Blue team hit the assassin = Blue LOST = Red WON
  * Red background on covered assassin = Red team hit the assassin = Red LOST = Blue WON
  * The background color shows which team LOST by hitting the assassin, NOT which team won
  * Write the team that won because the other team selected the assassin into the "won_because_of_assassin" JSON field.
  * Write 0 into the two "count" fields.
- If no assassin was selected (text still visible on assassin card = normal game end):
  * Look at the numbers on each team panel
  * Write the number from the blue team (left side) into the count field in the JSON. Do the same thing for the red team (right side) and write it into their field in the JSON.
  * Leave the "won_because_of_assassin" empty/missing.

Return ONLY a JSON object with this structure:
{
  "blue_team": {
    "operatives": ["name1", "name2"],
    "spymasters": ["name3"],
    "count": 3
  },
  "red_team": {
    "operatives": ["name4", "name5"],
    "spymasters": ["name6"],
    "count": 2
  },
  "won_because_of_assassin": "blue" or "red" or omit this field entirely
}
Return ONLY the JSON, no other text."""