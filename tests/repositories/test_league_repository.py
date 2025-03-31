import unittest
from app.repositories import LeagueRepository, UserRepository
from app.models import League, User

class TestLeagueRepository(unittest.TestCase):
    def test_save_and_get_league(self):
        league_name = "Test League"
        league_player_names = "John, Jane, Jim, Jill"
        league = League(name=league_name, player_names=league_player_names)
        league_id = league.id

        LeagueRepository.save_league(league)
        
        retrieved_league = LeagueRepository.get_league(league_id)

        self.assertEqual(retrieved_league.name, league_name)
        for player in retrieved_league.players:
            self.assertTrue(player.name in league_player_names.split(", "))
    
    def test_get_league_that_does_not_exist(self):
        league = LeagueRepository.get_league("non-existent-id")
        self.assertIsNone(league)
    
    def test_delete_league(self):
        league = League(name="Test League", player_names="John, Jane, Jim, Jill")
        user = User(google_id="123", email="test@test.com")
        user.add_league(league.id)
        league.owner = user
        LeagueRepository.save_league(league)
        UserRepository.save_user(user)

        retrieved_league = LeagueRepository.get_league(league.id)
        retrieved_user = UserRepository.get_user(user.email)

        self.assertEqual(retrieved_league.name, league.name)
        self.assertEqual(retrieved_league.owner.email, user.email)
        self.assertEqual(retrieved_user.league_ids, [league.id])

        LeagueRepository.delete_league(league.id)

        retrieved_deleted_league = LeagueRepository.get_league(league.id)
        self.assertIsNone(retrieved_deleted_league)