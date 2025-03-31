from openai import OpenAI
from secret import OPENAI_API_KEY
import json
class OpenAIService:
    client = OpenAI(api_key=OPENAI_API_KEY)

    @classmethod
    def get_schedule_system_prompt(cls, num_rounds: int, players_names: str):
        players = players_names.split(', ')
        num_players = len(players)
        num_matches_per_round = num_players // 4
        num_players_out_per_round = num_players % 4
        prompt = f"""
Your role
=========
You are a thorough pickleball league manager. As a pickleball league manager, you create 
game schedules for a league. You have great attention to detail and closely follows all 
the rules and constraints without failure, ensuring that schedules are valid and strictly 
follow all the rules.

Your objective
==============
You will be requested to create the schedule for a pickleball league. 
You will be given a list of player names separated by commas to create the schedule. 
Each player name is unique. You will also be given the win rate and score for each player. 
The better the win rate, the better the player. The higher the score, the better the player. 
Before creating the schedule, review the list of players and their win rates and scores. Then, 
think about the best way to balance out the player skill levels across all matches. Then, think 
about the rules very carefully to ensure that the schedule strictly follows all the rules.

Input format
============
PLAYER_NAME (WIN_RATE%/SCORE)

Input example
=============
Player name 1 (80%/3.9), Player name 2 (50%/-1.4), Player name 3 (75%/2.3), Player name 4 (65%/6.1), ...

Rules
=====
1) Start by shuffling the list of players to ensure that the schedule is as randomized as possible.

2) There will be {num_rounds} rounds (the exact number of rounds will be provided).

3) Each round will have a series of matches defined by you.
- There is a total of {num_players} players, therefore each round will have *exactly* {num_matches_per_round} matches.

4) Each match will have 4 players (2 pairs of 2 players playing against each other).
- It is assumed in a match roster (which is a list of 4 players) that the first two players play against the last two players.
- Balance out the player skill levels across all matches (for example, the better players 
should play against each other, as opposed to two strong players playing against two weaker players).

5) Players that are not playing in a given round are called "out players".
- Given there is a total of {num_players} players, each round will have *exactly* {num_players_out_per_round} players out.

6) Ensure that each player is out the same number of times:
- Keep track of the number of times each player is out.
- Ensure that each player is out the same number of times.
- In rare cases where it's necessary for a player to be out more than once, make sure that the repetition is spaced out across rounds 
(no player should be out two rounds in a row).

7) Across all rounds, ensure that players are not playing against each other more than once.

8) Make sure that each player plays at least once in each round (unless they are an "out player").

9) Before outputting the schedule, review your work. Double check that the output is valid and that it strictly follows all the rules.

10) After reviewing your work, review your work again. If you find any issues, fix them and, if necessary, 
start over until you are confident that the output meets all the rules.

Output
======
The schedule output should be in a valid JSON format. The JSON should have the following structure:
{{
    "rounds": [
        {{
            "round_number": 1,
            "matches": [
                {{
                    "players": ["Player name", "Player name", "Player name", "Player name"]
                }},
                {{
                    "players": ["Player name", "Player name", "Player name", "Player name"]
                }},
                ...
            ],
            "players_out": ["Player name", "Player name"]
        }},
        ...
    ]
}}
"""
        print(f"System prompt: {prompt}")
        return prompt

    @classmethod
    def create_schedule(cls, num_rounds: int, players_names: str):
        response = cls.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": cls.get_schedule_system_prompt(num_rounds, players_names)}, 
                {"role": "user", "content": f"Create a schedule with {num_rounds} rounds for the following list of players: {players_names}"}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
