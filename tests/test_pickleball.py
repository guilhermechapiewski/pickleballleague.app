import unittest
from pickleball import League, Player, Game, LeagueRound

class TestGame(unittest.TestCase):
    def test_game(self):
        game = Game(["John", "Jane", "Jim", "Jill"])
        self.assertEqual(game.players, ["John", "Jane", "Jim", "Jill"])
    
    def test_game_must_have_4_players(self):
        with self.assertRaises(ValueError):
            Game(["John", "Jane", "Jim"])
    
    def test_game_equality(self):
        game1 = Game(["John", "Jane", "Jim", "Jill"])
        game2 = Game(["Jane", "John", "Jim", "Jill"])
        self.assertTrue(game1 == game2)

        game3 = Game(["John", "Jim", "Jane", "Jill"])
        self.assertFalse(game1 == game3)

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
        
    def test_generate_schedule_with_4_players(self):
        league = League("GC, Juliano, Fariba, Galina")
        schedule = league.generate_schedule(rounds=2)
        self.assertEqual(len(schedule), 2)

        for round in schedule:
            self.assertEqual(round.number_of_games(), 1)
            self.assertEqual(len(round.players_out), 0)
    
    def test_impossible_to_generate_schedule_with_4_players_and_10_rounds(self):
        league = League("GC, Juliano, Fariba, Galina")
        
        # try to generate 10 rounds, but only 3 rounds should be possible given the number of players
        try:
            schedule = league.generate_schedule(rounds=10)
        except ValueError as e:
            self.assertEqual(str(e), "This number of rounds is not possible with the current number of players.")
        else:
            self.fail("Expected ValueError to be raised")
    
    def test_generate_schedule_with_4_players_and_there_are_no_equal_games_across_rounds(self):
        league = League("GC, Juliano, Fariba, Galina")
        schedule = league.generate_schedule(rounds=3)

        self.assertEqual(len(schedule), 3)

        # check that no two games are equal across all rounds
        for i in range(len(schedule)):
            for this_game in schedule[i].games:
                # Check against all games in subsequent rounds
                for j in range(i + 1, len(schedule)):
                    for another_game in schedule[j].games:
                        self.assertFalse(this_game == another_game, 
                            f"Found equal games:\nRound {i+1}: {this_game}\nRound {j+1}: {another_game}")

    def test_generate_schedule_with_9_players(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
        schedule = league.generate_schedule(rounds=5)
        self.assertEqual(len(schedule), 5)

        for round in schedule:
            self.assertEqual(round.number_of_games(), 2)
            self.assertEqual(len(round.players_out), 1)
            
            player_out = round.players_out.pop()
            self.assertTrue(player_out in league.players)
            self.assertFalse(player_out in round.games[0].players)
            self.assertFalse(player_out in round.games[1].players)
    
    def test_generate_schedule_with_10_players(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John, Jane")
        schedule = league.generate_schedule()
        self.assertEqual(len(schedule), 7)

        for round in schedule:
            self.assertEqual(round.number_of_games(), 2)
            self.assertEqual(len(round.players_out), 2)

            for player_out in round.players_out:
                self.assertTrue(player_out in league.players)
                self.assertFalse(player_out in round.games[0].players)
                self.assertFalse(player_out in round.games[1].players)
        
    def test_schedule_rounds_start_with_one(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
        schedule = league.generate_schedule(rounds=5)
        self.assertEqual(schedule[0].number, 1)
    
    def test_calculate_max_possible_rounds(self):
        # 5 players
        league = League("GC, Juliano, Fariba, Galina, Igor")
        self.assertEqual(league.calculate_max_possible_unique_pairs(), 10)

        # 6 players
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri")
        self.assertEqual(league.calculate_max_possible_unique_pairs(), 15)
