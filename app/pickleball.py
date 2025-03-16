from itertools import combinations
import random
import math
import uuid
from enum import Enum
from datetime import datetime
from app.user import User

class ScoringSystem(Enum):
    W_L = "w_l"
    SCORE = "score"
    NONE = "none"

class Player:
    def __init__(self, name: str):
        if name is None or len(name) == 0:
            raise ValueError("Player name cannot be empty")
        self.name = name

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other_player):
        return self.name < other_player.name
    
    def __gt__(self, other_player):
        return self.name > other_player.name
    
    def __le__(self, other_player):
        return self.name <= other_player.name
    
    def __ge__(self, other_player):
        return self.name >= other_player.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other_player):
        return self.name == other_player.name
    
    def to_object(self):
        return {"name": self.name}
    
    @staticmethod
    def from_object(object: dict):
        return Player(object["name"])

class Match:
    def __init__(self, players: list[Player], scoring_system: ScoringSystem):
        if len(players) != 4:
            raise ValueError("Match must have 4 players")
        self.players = players
        self.scoring_system = scoring_system
        self.score = [0, 0]
        self.winner_team = 0

    def __str__(self):
        return f"{self.players[0]}/{self.players[1]} vs. {self.players[2]}/{self.players[3]}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other_match):
        this_match_side1 = sorted(self.players[:2])
        this_match_side2 = sorted(self.players[2:])
        other_match_side1 = sorted(other_match.players[:2])
        other_match_side2 = sorted(other_match.players[2:])
        return (this_match_side1 == other_match_side1 and this_match_side2 == other_match_side2) or \
            (this_match_side1 == other_match_side2 and this_match_side2 == other_match_side1)
    
    def set_score(self, score: list[int]):
        if len(score) != 2:
            raise ValueError("Score must have 2 values")
        
        self.score = score
        
        if score[0] >= 11 or score[1] >= 11:
            if score[0] > score[1]:
                self.set_winner_team(1)
            elif score[0] < score[1]:
                self.set_winner_team(2)
            else:
                self.set_winner_team(0)

    def get_score(self):
        return self.score
    
    def set_winner_team(self, winner_team: int):
        if winner_team not in [1, 2, 0]:
            raise ValueError("Winner team must be 1 or 2 (or 0 for draw/no winner)")
        self.winner_team = winner_team
    
    def get_winner_team(self):
        return self.winner_team

    def get_winner_team_players(self):
        if self.get_winner_team() == 1:
            return [self.players[0], self.players[1]]
        elif self.get_winner_team() == 2:
            return [self.players[2], self.players[3]]
        else:
            return []
    
    def set_scoring_system(self, scoring_system: ScoringSystem):
        self.scoring_system = scoring_system

    def to_object(self):
        return {
            "players": [player.to_object() for player in self.players], 
            "scoring_system": self.scoring_system.value,
            "score": self.score,
            "winner_team": self.winner_team
        }
    
    @staticmethod
    def from_object(object: dict):
        match = Match([Player.from_object(player) for player in object["players"]], ScoringSystem(object["scoring_system"]))
        match.set_score(object["score"])
        match.set_winner_team(object["winner_team"])
        return match

class LeagueRound:
    def __init__(self, number: int, matches: list[Match], players_out: list[Player]):
        self.number = number
        self.matches = matches
        self.players_out = players_out
    
    def number_of_matches(self):
        return len(self.matches)
    
    def add_player_out(self, player: Player):
        self.players_out.append(player)
    
    def __str__(self):
        return f"Round {self.number}: {', '.join([str(match.players) for match in self.matches])}"
    
    def to_object(self):
        return {
            "number": self.number,
            "matches": [match.to_object() for match in self.matches],
            "players_out": [player.to_object() for player in self.players_out]
        }
    
    @staticmethod
    def from_object(object: dict):
        return LeagueRound(object["number"], [Match.from_object(match) for match in object["matches"]], [Player.from_object(player) for player in object["players_out"]])

class League:
    def __init__(self, name: str="", player_names: list[str]=[]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.players = [Player(player.strip()) for player in player_names.split(",")] if player_names else []
        self.schedule = []
        self.scoring_system = ScoringSystem.NONE
        self.template = "ricky"
        self.owner = None
        self.short_link = None #string only
        
    def set_id(self, id: str):
        self.id = id

    def set_schedule(self, schedule: list[LeagueRound]):
        self.schedule = schedule
    
    def set_players(self, players: list[Player]):
        self.players = players

    def set_scoring_system(self, scoring_system: ScoringSystem):
        self.scoring_system = scoring_system
        for round in self.schedule:
            for match in round.matches:
                match.set_scoring_system(scoring_system)

    def reset_schedule(self):
        self.schedule = []
    
    def add_round(self, round: LeagueRound):
        self.schedule.append(round)

    def calculate_max_possible_unique_pairs(self):
        n = len(self.players)
        if n < 4:
            return 0
        r = 2
        return math.factorial(n) // (math.factorial(r) * math.factorial(n-r))
    
    def set_template(self, template: str):
        if template not in ["ricky", "irina-fariba"]:
            raise ValueError("Invalid template name.")
        self.template = template
    
    def set_short_link(self, short_link: str):
        if short_link is not None and len(short_link) > 0:
            self.short_link = short_link

    def set_date_created(self, date_created: str):
        self.date_created = date_created

    def generate_schedule(self, rounds: int=7):
        max_unique_pairs = self.calculate_max_possible_unique_pairs()
        if rounds > max_unique_pairs:
            raise ValueError(f"This number of rounds is not possible with the current number of players.")

        # Reset schedule
        self.reset_schedule()

        while len(self.schedule) != rounds:
            # Get all possible combinations of 4 players
            all_possible_players_combinations = list(combinations(self.players, 4))
            
            # Shuffle the list of possible  matches to randomize schedule generation
            random.shuffle(all_possible_players_combinations)
            
            generated_rounds = []

            # Generate rounds
            while len(generated_rounds) < rounds:
                round_matches = []
                remaining_available_players = set(self.players)
                
                # Keep adding matches until we can't add more
                while len(remaining_available_players) >= 4:
                    # If we run out of possible combinations, start over
                    if len(all_possible_players_combinations) == 0:
                        all_possible_players_combinations = list(combinations(self.players, 4))
                        random.shuffle(all_possible_players_combinations)
                    
                    # Find a valid match from remaining combinations
                    for players_combination in all_possible_players_combinations:
                        # Check if all players in this match are still available
                        if all(player in remaining_available_players for player in players_combination):
                            players = list(players_combination)
                            random.shuffle(players)
                            round_matches.append(Match(players, self.scoring_system))

                            all_possible_players_combinations.remove(players_combination)
                            
                            # Remove used players from available pool
                            for player in players_combination:
                                remaining_available_players.remove(player)
                            break
                
                # Only add non-empty, non-duplicate rounds
                if round_matches:
                    is_duplicate = False
                    for existing_round_matches, _ in generated_rounds:
                        for existing_round_match in existing_round_matches:
                            for new_match in round_matches:
                                if existing_round_match == new_match:
                                    is_duplicate = True
                                    break
                        if is_duplicate:
                            break
                    
                    if not is_duplicate:
                        generated_rounds.append((round_matches, remaining_available_players))
            
            # Add rounds to schedule
            round_number = 1
            for round_matches, remaining_available_players in generated_rounds:
                self.add_round(LeagueRound(round_number, round_matches, remaining_available_players))
                round_number += 1
    
        return self.schedule

    def get_player_rankings(self):
        rankings = []
        
        for player in self.players:
            rankings.append({
                "name": player.name,
                "total_score": 0,
                "wins": 0,
                "losses": 0,
                "win_percentage": 1
            })

        # Calculate scores and wins for each player
        for round in self.schedule:
            for match in round.matches:
                winner_team = match.get_winner_team()
                if winner_team:
                    for i, player in enumerate(match.players):
                        player_idx = next((idx for idx, p in enumerate(rankings) if p["name"] == player.name), None)
                        if player_idx is not None:
                            # Add score
                            if self.scoring_system == ScoringSystem.SCORE:
                                if i < 2:  # Team 1
                                    rankings[player_idx]["total_score"] += match.score[0] if match.score and len(match.score) > 0 else 0
                                else:  # Team 2
                                    rankings[player_idx]["total_score"] += match.score[1] if match.score and len(match.score) > 1 else 0
                            
                            # Add win/loss
                            if (i < 2 and winner_team == 1) or (i >= 2 and winner_team == 2):
                                rankings[player_idx]["wins"] += 1
                            else:
                                rankings[player_idx]["losses"] += 1
        
        # Calculate win percentage for each player
        for player in rankings:
            total_matches = player["wins"] + player["losses"]
            player["win_percentage"] = (player["wins"] / total_matches * 100) if total_matches > 0 else 0
        
        # Sort rankings by wins (descending) and then by total score (descending)
        rankings.sort(key=lambda x: (x["wins"], x["total_score"]), reverse=True)

        return rankings
    
    def set_owner(self, owner: User):
        self.owner = owner
    
    def to_object(self):
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created,
            "owner": self.owner.to_object() if self.owner else None,
            "players": [player.to_object() for player in self.players],
            "schedule": [round.to_object() for round in self.schedule],
            "scoring_system": self.scoring_system.value,
            "template": self.template,
            "short_link": self.short_link if self.short_link else None
        }
    
    @staticmethod
    def from_object(object: dict):
        league = League(name=object["name"])
        league.set_id(object["id"])
        league.set_date_created(object["date_created"])
        if "owner" in object and object["owner"] is not None and "email" in object["owner"]:
            user = User(object["owner"]["email"])
            league.set_owner(user)
        league.set_players([Player.from_object(player) for player in object["players"]])
        league.set_schedule([LeagueRound.from_object(round) for round in object["schedule"]])
        league.set_scoring_system(ScoringSystem(object["scoring_system"]))
        league.set_template(object["template"])
        if "short_link" in object and object["short_link"] is not None:
            league.set_short_link(object["short_link"])
        return league