import uuid
import random
import math
import logging
from datetime import datetime
from .player import Player
from .match import Match
from .league_round import LeagueRound
from .scoring_system import ScoringSystem
from .user import User

logger = logging.getLogger(__name__)

class League:
    def __init__(self, name: str="", player_names: list[str]=[]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.versioning_timestamp = datetime.now().timestamp()
        self.players = [Player(player.strip()) for player in player_names.split(",")] if player_names else []
        self.schedule = []
        self.scoring_system = ScoringSystem.NONE
        self.template = "ricky"
        self.owner = None
        self.contributors = []
        self.short_link = None #string only
        
    def set_id(self, id: str):
        self.id = id

    def refresh_version(self):
        self.versioning_timestamp = datetime.now().timestamp()
    
    def get_version(self):
        return self.versioning_timestamp
    
    def get_seconds_since_version_update(self):
        if self.versioning_timestamp == 0.0:
            self.versioning_timestamp = datetime.now().timestamp() - (24 * 60 * 60)
        return int(datetime.now().timestamp() - self.versioning_timestamp)

    def set_schedule(self, schedule: list[LeagueRound]):
        self.schedule = schedule
    
    def set_players(self, players: list[Player]):
        self.players = players
    
    def get_players_sorted(self):
        return sorted(self.players, key=lambda x: x.name)

    def set_scoring_system(self, scoring_system: ScoringSystem):
        self.scoring_system = scoring_system
        for round in self.schedule:
            for match in round.matches:
                match.set_scoring_system(scoring_system)
    
    def add_round(self, round: LeagueRound):
        self.schedule.append(round)
    
    def number_of_matches(self):
        return sum([round.number_of_matches() for round in self.schedule])

    def set_template(self, template: str):
        if template not in ["ricky"]:
            raise ValueError("Invalid template name.")
        self.template = template
    
    def set_short_link(self, short_link: str):
        if short_link is not None and len(short_link) > 0:
            self.short_link = short_link

    def set_date_created(self, date_created: str):
        self.date_created = date_created

    def reset_schedule(self):
        self.schedule = []

    def calculate_max_possible_unique_pairs(self):
        n = len(self.players)
        if n < 4:
            return 0
        r = 2
        return math.factorial(n) // (math.factorial(r) * math.factorial(n-r))

    def generate_round(self, number: int, roster: list[Player]):
        if roster is None or len(roster) == 0:
            raise ValueError("Roster cannot be empty")
        if len(roster) < 4:
            raise ValueError("Roster must have at least 4 players")
        
        num_players_out = len(roster) % 4

        # Split players into players out and players in
        players_out = roster[:num_players_out]
        players_in = roster[num_players_out:]
        random.shuffle(players_in)

        # Generate matches
        matches = []
        for _ in range(len(players_in) // 4):
            matches.append(Match(players_in[:4], self.scoring_system))
            players_in = players_in[4:]
        
        return LeagueRound(number=number, matches=matches, players_out=players_out)
    
    def generate_schedule(self, rounds: int=7):
        max_unique_pairs = self.calculate_max_possible_unique_pairs()
        if rounds > max_unique_pairs:
            raise ValueError(f"This number of rounds is not possible with the current number of players.")

        # Shuffle players
        roster = self.players.copy()
        random.shuffle(roster)

        # calculate total number of pairs this league will have
        total_pairs = rounds * len(roster) // 2
        can_repeat_pairs = total_pairs > max_unique_pairs
        logger.info(f"Total pairs: {total_pairs}, Max unique pairs: {max_unique_pairs}, Can repeat pairs: {can_repeat_pairs}")
        
        num_players_out_per_round = len(roster) % 4
        generated_rounds = []

        while len(generated_rounds) < rounds:
            round = self.generate_round(len(generated_rounds) + 1, roster)
            
            # Check if the round is unique and add to generated rounds if yes
            # and then rotate roster to change players out
            valid_round = True
            
            for existing_round in generated_rounds:
                if not can_repeat_pairs and round.has_repeated_pairs(existing_round):
                    valid_round = False
                    break
            
            if valid_round:
                generated_rounds.append(round)
            
                # get the first n players (num_players_out_per_round) and move to the end of the list
                roster = roster[num_players_out_per_round:] + roster[:num_players_out_per_round]

        self.schedule = generated_rounds
        return self.schedule

    def get_player_rankings(self):
        rankings = []
        
        for player in self.players:
            rankings.append({
                "name": player.name,
                "points_won": 0,
                "points_against": 0,
                "points_difference": 0,
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
                                    rankings[player_idx]["points_won"] += match.score[0] if match.score and len(match.score) > 0 else 0
                                    rankings[player_idx]["points_against"] += match.score[1] if match.score and len(match.score) > 1 else 0
                                else:  # Team 2
                                    rankings[player_idx]["points_won"] += match.score[1] if match.score and len(match.score) > 1 else 0
                                    rankings[player_idx]["points_against"] += match.score[0] if match.score and len(match.score) > 0 else 0
                            
                            # Add win/loss
                            if (i < 2 and winner_team == 1) or (i >= 2 and winner_team == 2):
                                rankings[player_idx]["wins"] += 1
                            else:
                                rankings[player_idx]["losses"] += 1
        
        # Calculate win percentage and points difference for each player
        for player in rankings:
            total_matches = player["wins"] + player["losses"]
            player["win_percentage"] = (player["wins"] / total_matches * 100) if total_matches > 0 else 0
            player["points_difference"] = player["points_won"] - player["points_against"]
        
        # Sort rankings by win percentage (descending), points difference (descending), wins (descending) and then by points won (descending)
        rankings.sort(key=lambda x: (x["win_percentage"], x["points_difference"], x["wins"], x["points_won"]), reverse=True)

        return rankings
    
    def set_owner(self, owner: User):
        self.owner = owner
    
    def add_contributor(self, contributor: User):
        self.contributors.append(contributor)
    
    def can_edit(self, email: str):
        if self.owner is None:
            return True
        return self.owner.email == email or email in [contributor.email for contributor in self.contributors]
    
    def to_object(self):
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created,
            "versioning_timestamp": self.versioning_timestamp,
            "owner": self.owner.to_object() if self.owner else None,
            "contributors": [contributor.to_object() for contributor in self.contributors],
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
        league.versioning_timestamp = float(object.get("versioning_timestamp", 0.0))
        if object.get("owner") is not None and isinstance(object.get("owner"), dict) and "email" in object.get("owner"):
            user = User(object["owner"]["email"])
            league.set_owner(user)
        for contributor in object.get("contributors", []):
            user = User(contributor["email"])
            league.add_contributor(user)
        league.set_players([Player.from_object(player) for player in object["players"]])
        league.set_schedule([LeagueRound.from_object(round) for round in object["schedule"]])
        league.set_scoring_system(ScoringSystem(object["scoring_system"]))
        league.set_template(object["template"])
        if "short_link" in object and object.get("short_link") is not None:
            league.set_short_link(object.get("short_link"))
        return league