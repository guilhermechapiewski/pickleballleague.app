from typing import List
from .player import Player
from .scoring_system import ScoringSystem

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