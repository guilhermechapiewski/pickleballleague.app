import unittest
from app.models import Player, Match, LeagueRound, ScoringSystem

class TestLeagueRound(unittest.TestCase):
    def test_league_round_to_object(self):
        round = LeagueRound(1, [Match([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")], ScoringSystem.NONE), Match([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")], ScoringSystem.NONE)], [])
        self.assertEqual(round.to_object(), {
            "number": 1,
            "matches": [
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}], "score": [0, 0], "winner_team": 0, "scoring_system": "none"},
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}], "score": [0, 0], "winner_team": 0, "scoring_system": "none"}
            ],
            "players_out": []
        })
        
        round.add_player_out(Player("GC"))
        self.assertEqual(round.to_object(), {
            "number": 1,
            "matches": [
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}], "score": [0, 0], "winner_team": 0, "scoring_system": "none"},
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}], "score": [0, 0], "winner_team": 0, "scoring_system": "none"}
            ],
            "players_out": [{"name": "GC"}]
        })
    
    def test_league_round_from_object(self):
        round = LeagueRound.from_object({
            "number": 1,
            "matches": [
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}], "score": [0, 0], "winner_team": 0, "scoring_system": "none"},
            ],
            "players_out": [{"name": "GC"}]
        })
        self.assertEqual(round.number, 1)
        self.assertEqual(len(round.matches), 1)
        self.assertEqual([player.name for player in round.matches[0].players], ["John", "Jane", "Jim", "Jill"])
        self.assertEqual(len(round.players_out), 1)
        self.assertEqual(round.players_out[0].name, "GC")