from itertools import combinations
import random
import math
import uuid
from enum import Enum
from datetime import datetime
from app.user import User
import logging
logger = logging.getLogger(__name__)

class ScoringSystem(Enum):
    W_L = "w_l"
    SCORE = "score"
    NONE = "none"

class Player:
    def __init__(self, name: str):
        if name is None or len(name) == 0:
            raise ValueError("Player name cannot be empty")
        # Only allow letters, numbers and spaces in player names
        if not all(c.isalnum() or c.isspace() for c in name):
            raise ValueError("Player name can only contain letters, numbers and spaces")
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
    
    def has_repeated_pairs(self, other_round: "LeagueRound"):
        for match in self.matches:
            for other_match in other_round.matches:
                this_match_side1 = sorted(match.players[:2])
                this_match_side2 = sorted(match.players[2:])
                other_match_side1 = sorted(other_match.players[:2])
                other_match_side2 = sorted(other_match.players[2:])
                if this_match_side1 == other_match_side1 or this_match_side2 == other_match_side2 or \
                    this_match_side1 == other_match_side2 or this_match_side2 == other_match_side1:
                    return True
        return False

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
    
class Series:
    def __init__(self, name: str=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.league_ids = []
        self.scoring_system = ScoringSystem.SCORE
        self.owner = None
        self.contributors = []
        self.short_link = None #string only
    
    def set_id(self, id: str):
        self.id = id

    def add_league(self, league: League):
        if type(league) != League:
            raise ValueError("League parameter must be a League object")
        if league.id is None or len(league.id) == "":
            raise ValueError("League ID cannot be empty")
        if league.id in self.league_ids:
            raise ValueError("League ID already exists in series")
        if league.scoring_system != self.scoring_system:
            raise ValueError("Leagues in a series must have the same scoring system")
        self.league_ids.append(league.id)
    
    def remove_league(self, league_id: str):
        if league_id in self.league_ids:
            self.league_ids.remove(league_id)

    def set_scoring_system(self, scoring_system: ScoringSystem):
        if scoring_system not in [ScoringSystem.SCORE, ScoringSystem.W_L]:
            raise ValueError("Series can only have score or win/loss scoring system")
        self.scoring_system = scoring_system
    
    def set_owner(self, owner: User):
        self.owner = owner
    
    def add_contributor(self, contributor: User):
        self.contributors.append(contributor)
    
    def can_edit(self, email: str):
        if self.owner is None:
            return True
        return self.owner.email == email or email in [contributor.email for contributor in self.contributors]

    def get_all_players(self):
        from app.db import LeagueRepository
        players = []
        for league_id in self.league_ids:
            league = LeagueRepository.get_league(league_id)
            if league and league.players and len(league.players) > 0:
                for player in league.players:
                    if player not in players:
                        players.append(player)
        return players
    
    def get_leagues(self):
        from app.db import LeagueRepository
        leagues = []
        for league_id in self.league_ids:
            league = LeagueRepository.get_league(league_id)
            if league:
                leagues.append(league)
        return leagues

    def get_player_rankings(self):
        rankings = []
        
        for league in self.get_leagues():
            league_rankings = league.get_player_rankings()
            for ranking in league_rankings:
                if ranking["name"] not in [r["name"] for r in rankings]:
                    rankings.append(ranking)
                else:
                    idx = next((i for i, r in enumerate(rankings) if r["name"] == ranking["name"]), None)
                    if idx is not None:
                        rankings[idx]["points_won"] += ranking["points_won"]
                        rankings[idx]["points_against"] += ranking["points_against"]
                        rankings[idx]["wins"] += ranking["wins"] 
                        rankings[idx]["losses"] += ranking["losses"]

        # Calculate total matches and win percentage for each player
        for player in rankings:
            total_matches = player["wins"] + player["losses"]
            player["total_matches"] = total_matches
            player["win_percentage"] = (player["wins"] / total_matches * 100) if total_matches > 0 else 0
            player["points_difference"] = player["points_won"] - player["points_against"]
            player["normalized_points_difference"] = player["points_difference"] / total_matches if total_matches > 0 else 0

        # Sort rankings by win percentage (descending), normalized points difference (descending)
        rankings.sort(key=lambda x: (x["win_percentage"], x["normalized_points_difference"]), reverse=True)

        return rankings
    
    def set_short_link(self, short_link: str):
        if short_link is not None and len(short_link) > 0:
            self.short_link = short_link
    
    def to_object(self):
        return {
            "id": self.id,
            "name": self.name,
            "league_ids": self.league_ids,
            "scoring_system": self.scoring_system.value,
            "owner": self.owner.to_object() if self.owner else None,
            "contributors": [contributor.to_object() for contributor in self.contributors],
            "short_link": self.short_link if self.short_link else None
        }
    
    @staticmethod
    def from_object(object: dict):
        series = Series(object["name"])
        series.set_id(object["id"])
        series.set_scoring_system(ScoringSystem(object["scoring_system"]))
        series.league_ids = object["league_ids"]
        if object.get("owner") is not None and isinstance(object.get("owner"), dict) and "email" in object.get("owner"):
            user = User(object["owner"]["email"])
            series.set_owner(user)
        for contributor in object.get("contributors", []):
            user = User(contributor["email"])
            series.add_contributor(user)
        if "short_link" in object and object.get("short_link") is not None:
            series.set_short_link(object.get("short_link"))
        return series