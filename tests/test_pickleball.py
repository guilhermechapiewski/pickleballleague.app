import unittest
from pickleball import League

class TestLeague(unittest.TestCase):

    def test_league(self):
        league = League("John,Jane,Jim,Jill")
        self.assertEqual(league.players, ["John", "Jane", "Jim", "Jill"])

        league = League("GC, Juliano, Fariba, Galina, Igor, Igor 2, Peter, Yuri")
        self.assertEqual(league.players, ["GC", "Juliano", "Fariba", "Galina", "Igor", "Igor 2", "Peter", "Yuri"])

    def test_generate_schedule(self):
        league = League("GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark")
        schedule = league.generate_schedule(rounds=5)

        # 5 rounds should have been generated
        self.assertEqual(len(schedule), 5)

        for round in schedule:
            # with 8 players,each round has 2 games
            self.assertEqual(len(round), 2)

            # each game has 4 players
            for game in round:
                self.assertEqual(len(game), 4)
                self.assertEqual(len(set(game)), 4)
        
