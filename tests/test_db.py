import unittest
from db import LeagueRepository
from pickleball import League

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