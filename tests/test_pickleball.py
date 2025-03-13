import unittest
from pickleball import League, Player, Game, LeagueRound

class TestPlayer(unittest.TestCase):
    def test_player(self):
        player = Player("John")
        self.assertEqual(player.name, "John")
    
    def test_player_comparison(self):
        player1 = Player("Amanda")
        player2 = Player("GC")
        self.assertTrue(player1 < player2)
        self.assertFalse(player1 > player2)
        self.assertFalse(player1 == player2)
    
    def test_player_to_object(self):
        player = Player("John")
        self.assertEqual(player.to_object(), {"name": "John"})
    
    def test_player_from_object(self):
        player = Player.from_object({"name": "John"})
        self.assertEqual(player.name, "John")

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
    
    def test_game_to_object(self):
        game = Game([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")])
        self.assertEqual(game.to_object(), {"players": [
            {"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}
        ]})
    
    def test_game_from_object(self):
        game = Game.from_object({"players": [
            {"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}
        ]})
        self.assertEqual([player.name for player in game.players], ["John", "Jane", "Jim", "Jill"])

class TestLeagueRound(unittest.TestCase):
    def test_league_round_to_object(self):
        round = LeagueRound(1, [Game([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")]), Game([Player("John"), Player("Jane"), Player("Jim"), Player("Jill")])], [])
        self.assertEqual(round.to_object(), {
            "number": 1,
            "games": [
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}]},
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}]}
            ],
            "players_out": []})
        
        round.add_player_out(Player("GC"))
        self.assertEqual(round.to_object(), {
            "number": 1,
            "games": [
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}]},
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}]}
            ],
            "players_out": [{"name": "GC"}]})
    
    def test_league_round_from_object(self):
        round = LeagueRound.from_object({
            "number": 1,
            "games": [
                {"players": [{"name": "John"}, {"name": "Jane"}, {"name": "Jim"}, {"name": "Jill"}]}
            ],
            "players_out": [{"name": "GC"}]
        })
        self.assertEqual(round.number, 1)
        self.assertEqual(len(round.games), 1)
        self.assertEqual([player.name for player in round.games[0].players], ["John", "Jane", "Jim", "Jill"])
        self.assertEqual(len(round.players_out), 1)
        self.assertEqual(round.players_out[0].name, "GC")

class TestLeague(unittest.TestCase):
    def test_league(self):
        league = League(player_names="John,Jane,Jim,Jill")
        self.assertTrue([str(player) for player in league.players] == ["John", "Jane", "Jim", "Jill"])

        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Igor 2, Peter, Yuri")
        self.assertTrue([str(player) for player in league.players] == ["GC", "Juliano", "Fariba", "Galina", "Igor", "Igor 2", "Peter", "Yuri"])

    def test_generate_schedule(self):
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark")
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
        league = League(player_names="GC, Juliano, Fariba, Galina")
        schedule = league.generate_schedule(rounds=2)
        self.assertEqual(len(schedule), 2)

        for round in schedule:
            self.assertEqual(round.number_of_games(), 1)
            self.assertEqual(len(round.players_out), 0)
    
    def test_impossible_to_generate_schedule_with_4_players_and_10_rounds(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
        
        # try to generate 10 rounds, but only 3 rounds should be possible given the number of players
        try:
            schedule = league.generate_schedule(rounds=10)
        except ValueError as e:
            self.assertEqual(str(e), "This number of rounds is not possible with the current number of players.")
        else:
            self.fail("Expected ValueError to be raised")
    
    def test_generate_schedule_with_4_players_and_there_are_no_equal_games_across_rounds(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
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
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
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
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John, Jane")
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
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
        schedule = league.generate_schedule(rounds=5)
        self.assertEqual(schedule[0].number, 1)
    
    def test_calculate_max_possible_rounds(self):
        # 5 players
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor")
        self.assertEqual(league.calculate_max_possible_unique_pairs(), 10)

        # 6 players
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri")
        self.assertEqual(league.calculate_max_possible_unique_pairs(), 15)
    
    def test_league_to_object(self):
        player_names="GC, Juliano, Fariba, Galina"
        league = League(name="Test League", player_names=player_names)
        league.generate_schedule(rounds=1)
        
        generated_league_object = league.to_object()
        league_object = {
            "id": league.id,
            "name": "Test League",
            "players": [ {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}],
            "schedule": [
                {
                    "number": 1,
                    "games": [
                        {"players": [
                            {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}
                        ]}
                    ],
                    "players_out": []
                }
            ]
        }
        
        self.assertEqual(generated_league_object["id"], league_object["id"])
        self.assertEqual(generated_league_object["name"], league_object["name"])
        self.assertEqual(generated_league_object["players"], league_object["players"])
        
        self.assertEqual(generated_league_object["schedule"][0]["number"], league_object["schedule"][0]["number"])
        self.assertEqual(generated_league_object["schedule"][0]["players_out"], league_object["schedule"][0]["players_out"])

        self.assertTrue(generated_league_object["schedule"][0]["games"][0]["players"][0]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["games"][0]["players"][1]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["games"][0]["players"][2]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["games"][0]["players"][3]["name"] in player_names.split(", "))
    
    def test_league_from_object(self):
        league = League.from_object({
            "id": "123",
            "name": "Test League",
            "players": [ {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}, {"name": "Aline"}],
            "schedule": [
                {
                    "number": 1,
                    "games": [
                        {"players": [{"name": "Juliano"}, {"name": "Galina"}, {"name": "GC"}, {"name": "Fariba"}]}
                    ],
                    "players_out": [{"name": "Aline"}]
                }
            ]
        })
        self.assertEqual(league.id, "123")
        self.assertEqual(league.name, "Test League")
        self.assertEqual(len(league.players), 5)
        self.assertEqual(len(league.schedule), 1)
        self.assertEqual(league.schedule[0].number, 1)
        self.assertEqual(len(league.schedule[0].games), 1)
        self.assertEqual(len(league.schedule[0].players_out), 1)
        self.assertEqual([player.name for player in league.schedule[0].games[0].players], ["Juliano", "Galina", "GC", "Fariba"])
        self.assertEqual(league.schedule[0].players_out[0].name, "Aline")
