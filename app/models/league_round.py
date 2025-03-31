from typing import List
from .player import Player
from .match import Match

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