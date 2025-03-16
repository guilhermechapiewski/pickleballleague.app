import unittest
from app.db import LeagueRepository, UserRepository
from app.pickleball import League
from app.user import User

class TestLeagueRepository(unittest.TestCase):
    def test_save_and_get_league(self):
        league_name = "Test League"
        league_player_names = "John, Jane, Jim, Jill"
        league = League(name=league_name, player_names=league_player_names)
        league_id = league.id

        LeagueRepository.save_league(league)
        
        retrieved_league = LeagueRepository.get_league(league_id)

        print(retrieved_league.to_object())

        self.assertEqual(retrieved_league.name, league_name)
        for player in retrieved_league.players:
            self.assertTrue(player.name in league_player_names.split(", "))
    
    def test_get_league_that_does_not_exist(self):
        with self.assertRaises(KeyError):
            league = LeagueRepository.get_league("non-existent-id")
            self.assertIsNone(league)
    
class TestUserRepository(unittest.TestCase):
    def test_save_and_get_user(self):
        user = User(google_id="123", email="test@test.com")
        user_id = user.id

        UserRepository.save_user(user)
        
        retrieved_user = UserRepository.get_user("test@test.com")

        print(retrieved_user.to_object())

        self.assertEqual(retrieved_user.id, user_id)
        self.assertEqual(retrieved_user.google_id, "123")
        self.assertEqual(retrieved_user.email, "test@test.com")

    def test_save_and_get_user_with_leagues(self):
        user = User(google_id="123", email="test@test.com")
        user_id = user.id
        user.add_league("123-abc-456")
        user.add_league("456-def-789")

        UserRepository.save_user(user)
        
        retrieved_user = UserRepository.get_user("test@test.com")

        print(retrieved_user.to_object())

        self.assertEqual(retrieved_user.id, user_id)
        self.assertEqual(retrieved_user.google_id, "123")
        self.assertEqual(retrieved_user.email, "test@test.com")
        self.assertEqual(retrieved_user.league_ids, ["123-abc-456", "456-def-789"])
        
    def test_get_user_that_does_not_exist(self):
        with self.assertRaises(KeyError):
            user = UserRepository.get_user("non-existent-id")
            self.assertIsNone(user)