import unittest
from app.models import Player, Match, ScoringSystem

class TestMatch(unittest.TestCase):
    def test_match(self):
        match = Match(["John", "Jane", "Jim", "Jill"], ScoringSystem.NONE)
        self.assertEqual(match.players, ["John", "Jane", "Jim", "Jill"])
    
    def test_match_must_have_4_players(self):
        with self.assertRaises(ValueError):
            Match(["John", "Jane", "Jim"], ScoringSystem.NONE)
    
    def test_match_equality(self):
        match1 = Match(["John", "Jane", "Jim", "Jill"], ScoringSystem.NONE)
        match2 = Match(["Jane", "John", "Jim", "Jill"], ScoringSystem.NONE)
        self.assertTrue(match1 == match2)

        match3 = Match(["John", "Jim", "Jane", "Jill"], ScoringSystem.NONE)
        self.assertFalse(match1 == match3)

        match4 = Match(["Galina", "GC", "Fariba", "Juliano"], ScoringSystem.NONE)
        self.assertFalse(match1 == match4)

        match5 = Match(["Fariba", "Juliano", "GC", "Galina"], ScoringSystem.NONE)
        self.assertTrue(match4 == match5)
    
    def test_match_to_object(self):
        match = Match([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")], ScoringSystem.NONE)
        self.assertEqual(match.to_object(), {"players": [
            {"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}
        ], "scoring_system": "none", "score": [0, 0], "winner_team": 0})
    
    def test_match_from_object(self):
        match = Match.from_object({"players": [
            {"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}
        ], "scoring_system": "none", "score": [0, 0], "winner_team": 0})
        self.assertEqual([player.name for player in match.players], ["John", "Jane", "Jim", "Jill"])
    
    def test_match_score(self):
        match = Match([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")], ScoringSystem.NONE)
        self.assertEqual(match.get_score(), [0, 0])
        self.assertEqual(match.get_winner_team(), 0)
        self.assertEqual(match.get_winner_team_players(), [])
        
        match.set_score([11, 2])
        self.assertEqual(match.get_score(), [11, 2])
        self.assertEqual(match.get_winner_team(), 1)
        self.assertEqual([player.name for player in match.get_winner_team_players()], ["John", "Jane"])

        match.set_score([1, 11])
        self.assertEqual(match.get_score(), [1, 11])
        self.assertEqual(match.get_winner_team(), 2)
        self.assertEqual([player.name for player in match.get_winner_team_players()], ["Jim", "Jill"])
    
    def test_match_winner_based_on_score(self):
        match = Match([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")], ScoringSystem.NONE)
        self.assertEqual(match.get_winner_team(), 0)

        match.set_score([10, 2])
        self.assertEqual(match.get_winner_team(), 0)
        self.assertEqual(match.get_winner_team_players(), [])
        
        match.set_score([11, 2])
        self.assertEqual(match.get_winner_team(), 1)
        self.assertEqual([player.name for player in match.get_winner_team_players()], ["John", "Jane"])
    
    def test_match_winner_is_reverted_if_score_is_reverted_below_11(self):
        match = Match([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")], ScoringSystem.SCORE)
        match.set_score([11, 2])
        self.assertEqual(match.get_winner_team(), 1)
        self.assertEqual([player.name for player in match.get_winner_team_players()], ["John", "Jane"])
        
        match.set_score([10, 2])
        self.assertEqual(match.get_winner_team(), 0)
        self.assertEqual(match.get_winner_team_players(), [])