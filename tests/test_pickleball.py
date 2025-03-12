import unittest
from pickleball import League, Player, Game, LeagueRound

class TestGame(unittest.TestCase):
    def test_game(self):
        game = Game(["John", "Jane", "Jim", "Jill"])
        self.assertEqual(game.players, ["John", "Jane", "Jim", "Jill"])
    
    def test_game_must_have_4_players(self):
        with self.assertRaises(ValueError):
            Game(["John", "Jane", "Jim"])

class TestLeague(unittest.TestCase):
    def test_league(self):
        league = League("John,Jane,Jim,Jill")
        self.assertTrue([str(player) for player in league.players] == ["John", "Jane", "Jim", "Jill"])

        league = League("GC, Juliano, Fariba, Galina, Igor, Igor 2, Peter, Yuri")
        self.assertTrue([str(player) for player in league.players] == ["GC", "Juliano", "Fariba", "Galina", "Igor", "Igor 2", "Peter", "Yuri"])

    def test_generate_schedule(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark")
        schedule = league.generate_schedule(rounds=5)

        # 5 rounds should have been generated
        self.assertEqual(len(schedule), 5)

        for round in schedule:
            # with 8 players,each round has 2 games
            self.assertEqual(round.number_of_games(), 2)

            # each game has 4 players
            for game in round.games:
                self.assertEqual(len(game.players), 4)
                self.assertEqual(len(set(game.players)), 4)
        
    def test_generate_schedule_with_9_players(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
        schedule = league.generate_schedule(rounds=5)
        self.assertEqual(len(schedule), 5)

        for round in schedule:
            self.assertEqual(round.number_of_games(), 2)
    
    def test_schedule_rounds_start_with_one(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
        schedule = league.generate_schedule(rounds=5)
        self.assertEqual(schedule[0].number, 1)
