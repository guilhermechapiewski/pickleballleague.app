import unittest
from app.models import League, ScoringSystem, Series, User

class TestSeries(unittest.TestCase):
    def test_series(self):
        league1 = League(name="Test League 1", player_names="GC, Juliano, Fariba, Galina")
        league1.set_scoring_system(ScoringSystem.SCORE)
        league2 = League(name="Test League 2", player_names="GC2, Juliano2, Fariba2, Galina2")
        league2.set_scoring_system(ScoringSystem.SCORE)
        series = Series(name="Test Series")
        series.add_league(league1)
        series.add_league(league2)
        self.assertEqual(series.name, "Test Series")
        self.assertEqual(len(series.league_ids), 2)
        self.assertEqual(series.league_ids[0], league1.id)
        self.assertEqual(series.league_ids[1], league2.id)
    
    def test_series_add_league_with_invalid_id(self):
        league = League(name="Test League", player_names="GC, Juliano, Fariba, Galina")
        series = Series(name="Test Series")
        with self.assertRaises(ValueError):
            series.add_league("")

    def test_series_add_league_with_same_id_twice(self):
        league = League(name="Test League", player_names="GC, Juliano, Fariba, Galina")
        league.set_scoring_system(ScoringSystem.SCORE)
        series = Series(name="Test Series")
        series.add_league(league)
        self.assertEqual(len(series.league_ids), 1)
        self.assertEqual(series.league_ids[0], league.id)
        with self.assertRaises(ValueError):
            series.add_league(league)
        self.assertEqual(len(series.league_ids), 1)
        self.assertEqual(series.league_ids[0], league.id)

    def test_series_add_league(self):
        league1 = League(name="Test League 1", player_names="GC, Juliano, Fariba, Galina")
        league1.set_scoring_system(ScoringSystem.SCORE)
        league2 = League(name="Test League 2", player_names="GC2, Juliano2, Fariba2, Galina2")
        league2.set_scoring_system(ScoringSystem.SCORE)
        series = Series(name="Test Series")
        self.assertEqual(len(series.league_ids), 0)
        series.add_league(league1)
        series.add_league(league2)
        self.assertEqual(len(series.league_ids), 2)
        self.assertEqual(series.league_ids[0], league1.id)
        self.assertEqual(series.league_ids[1], league2.id)

    def test_series_to_object(self):
        league1 = League(name="Test League 1", player_names="GC, Juliano, Fariba, Galina")
        league1.set_scoring_system(ScoringSystem.SCORE)
        league2 = League(name="Test League 2", player_names="GC2, Juliano2, Fariba2, Galina2")
        league2.set_scoring_system(ScoringSystem.SCORE)
        series = Series(name="Test Series")
        series.add_league(league1)
        series.add_league(league2)
        self.assertEqual(len(series.league_ids), 2)
        self.assertEqual(series.league_ids[0], league1.id)
        self.assertEqual(series.league_ids[1], league2.id)

        series_object = series.to_object()
        self.assertEqual(series_object["id"], series.id)
        self.assertEqual(series_object["name"], "Test Series")
        self.assertEqual(len(series_object["league_ids"]), 2)
        self.assertEqual(series_object["league_ids"][0], league1.id)
        self.assertEqual(series_object["league_ids"][1], league2.id)
        self.assertEqual(series_object["scoring_system"], "score")
    
    def test_series_from_object(self):
        league1 = League(name="Test League 1", player_names="GC, Juliano, Fariba, Galina")
        league1.set_scoring_system(ScoringSystem.SCORE)
        league2 = League(name="Test League 2", player_names="GC2, Juliano2, Fariba2, Galina2")
        league2.set_scoring_system(ScoringSystem.SCORE)
        series = Series(name="Test Series")
        series.add_league(league1)
        series.add_league(league2)
        self.assertEqual(len(series.league_ids), 2)
        series_object = series.to_object()
        self.assertEqual(series_object["id"], series.id)
        self.assertEqual(series_object["name"], "Test Series")
        self.assertEqual(len(series_object["league_ids"]), 2)
        self.assertEqual(series_object["league_ids"][0], league1.id)
        self.assertEqual(series_object["league_ids"][1], league2.id)
        self.assertEqual(series_object["scoring_system"], "score")
    
    def test_series_add_league_with_different_scoring_system(self):
        league1 = League(name="Test League 1", player_names="GC, Juliano, Fariba, Galina")
        league1.set_scoring_system(ScoringSystem.SCORE)
        
        league2 = League(name="Test League 2", player_names="GC2, Juliano2, Fariba2, Galina2")
        league2.set_scoring_system(ScoringSystem.W_L)

        series = Series(name="Test Series")
        series.set_scoring_system(ScoringSystem.SCORE)

        self.assertEqual(len(series.league_ids), 0)
        
        series.add_league(league1)
        self.assertEqual(len(series.league_ids), 1)
        
        with self.assertRaises(ValueError, msg="Series should not allow adding a league with a different scoring system"):
            series.add_league(league2)
        
        self.assertEqual(len(series.league_ids), 1)
    
    def test_series_remove_league(self):
        league1 = League(name="Test League 1", player_names="GC, Juliano, Fariba, Galina")
        league1.set_scoring_system(ScoringSystem.SCORE)
        league2 = League(name="Test League 2", player_names="GC2, Juliano2, Fariba2, Galina2")
        league2.set_scoring_system(ScoringSystem.SCORE)
        series = Series(name="Test Series")
        series.add_league(league1)

    def test_series_set_owner(self):
        series = Series(name="Test Series")
        user = User("123", "test@test.com")
        series.set_owner(user)
        self.assertEqual(series.owner, user)

    def test_series_contributors_can_also_edit(self):
        series = Series(name="Test Series")
        user = User("123", "test@test.com")
        self.assertTrue(series.can_edit(user.email), "User should be able to edit series since there is no owner")
        series.set_owner(user)
        self.assertTrue(series.can_edit(user.email), "User should be able to edit series since he is the owner")
        
        another_user = User("456", "another@test.com")
        self.assertFalse(series.can_edit(another_user.email), "User should not be able to edit series since he is not the owner or a contributor")
        series.add_contributor(another_user)
        self.assertTrue(series.can_edit(another_user.email), "User should be able to edit series since he is a contributor")

    def test_series_to_object_with_owner_and_contributors(self):
        series = Series(name="Test Series")
        user = User("123", "test@test.com")
        series.set_owner(user)
        another_user = User("456", "another@test.com")
        series.add_contributor(another_user)
        
        generated_series_object = series.to_object()
        series_object = {
            "id": series.id,
            "name": "Test Series",
            "owner": {
                "id": user.id
            },
            "contributors": [
                {
                    "id": another_user.id,
                    "email": another_user.email
                }
            ],
            "league_ids": [],
            "scoring_system": "score"
        }
        
        self.assertEqual(generated_series_object["id"], series_object["id"])
        self.assertEqual(generated_series_object["name"], series_object["name"])
        self.assertEqual(generated_series_object["owner"]["id"], series_object["owner"]["id"])
        self.assertEqual(generated_series_object["contributors"][0]["id"], series_object["contributors"][0]["id"])
        self.assertEqual(generated_series_object["contributors"][0]["email"], series_object["contributors"][0]["email"])
        self.assertEqual(generated_series_object["league_ids"], series_object["league_ids"])
        self.assertEqual(generated_series_object["scoring_system"], series_object["scoring_system"])

    def test_series_from_object_with_owner(self):
        series = Series.from_object({
            "id": "123",
            "name": "Test Series",
            "owner": {
                "email": "test@test.com"
            },
            "contributors": [],
            "league_ids": [],
            "scoring_system": "score"
        })
        self.assertEqual(series.id, "123")
        self.assertEqual(series.name, "Test Series")
        self.assertEqual(series.owner.email, "test@test.com")
        self.assertEqual(len(series.league_ids), 0)
        self.assertEqual(series.scoring_system.value, "score")