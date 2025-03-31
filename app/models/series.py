import uuid
from .scoring_system import ScoringSystem
from .league import League
from .user import User

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
        from app.repositories import LeagueRepository
        players = []
        for league_id in self.league_ids:
            league = LeagueRepository.get_league(league_id)
            if league and league.players and len(league.players) > 0:
                for player in league.players:
                    if player not in players:
                        players.append(player)
        return players
    
    def get_leagues(self):
        from app.repositories import LeagueRepository
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