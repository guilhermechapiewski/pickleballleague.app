import unittest
from app.pickleball import League, Player, Match, LeagueRound, ScoringSystem
from app.user import User
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

class TestLeague(unittest.TestCase):
    def test_league(self):
        league = League(player_names="John,Jane,Jim,Jill")
        self.assertTrue([str(player) for player in league.players] == ["John", "Jane", "Jim", "Jill"])

        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Igor 2, Peter, Yuri")
        self.assertTrue([str(player) for player in league.players] == ["GC", "Juliano", "Fariba", "Galina", "Igor", "Igor 2", "Peter", "Yuri"])

    def test_league_player_names_cannot_be_empty(self):
        league = League(player_names="")
        self.assertEqual(len(league.players), 0)

        with self.assertRaises(ValueError):
            League(player_names="GC, , Fariba, Galina")
        with self.assertRaises(ValueError):
            League(player_names="GC, Juliano, Fariba, ")

    def test_generate_schedule(self):
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark")
        schedule = league.generate_schedule(rounds=5)

        # 5 rounds should have been generated
        self.assertEqual(len(schedule), 5)

        for round in schedule:
            # with 8 players,each round has 2 matches
            self.assertEqual(round.number_of_matches(), 2)

            # each match has 4 players
            for match in round.matches:
                self.assertEqual(len(match.players), 4)
                self.assertEqual(len(set(match.players)), 4)
        
    def test_generate_schedule_with_4_players(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
        schedule = league.generate_schedule(rounds=2)
        self.assertEqual(len(schedule), 2)

        for round in schedule:
            self.assertEqual(round.number_of_matches(), 1)
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
    
    def test_generate_schedule_with_4_players_and_there_are_no_equal_matches_across_rounds(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
        schedule = league.generate_schedule(rounds=3)

        self.assertEqual(len(schedule), 3)

        # check that no two matches are equal across all rounds
        for i in range(len(schedule)):
            for this_match in schedule[i].matches:
                # Check against all matches in subsequent rounds
                for j in range(i + 1, len(schedule)):
                    for another_match in schedule[j].matches:
                        self.assertFalse(this_match == another_match, 
                            f"Found equal matches:\nRound {i+1}: {this_match}\nRound {j+1}: {another_match}")

    def test_generate_schedule_with_9_players(self):
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John")
        schedule = league.generate_schedule(rounds=5)
        self.assertEqual(len(schedule), 5)

        for round in schedule:
            self.assertEqual(round.number_of_matches(), 2)
            self.assertEqual(len(round.players_out), 1)
            
            player_out = round.players_out.pop()
            self.assertTrue(player_out in league.players)
            self.assertFalse(player_out in round.matches[0].players)
            self.assertFalse(player_out in round.matches[1].players)
    
    def test_generate_schedule_with_10_players(self):
        league = League(player_names="GC, Juliano, Fariba, Galina, Igor, Yuri, Scott, Mark, John, Jane")
        schedule = league.generate_schedule()
        self.assertEqual(len(schedule), 7)

        for round in schedule:
            self.assertEqual(round.number_of_matches(), 2)
            self.assertEqual(len(round.players_out), 2)

            for player_out in round.players_out:
                self.assertTrue(player_out in league.players)
                self.assertFalse(player_out in round.matches[0].players)
                self.assertFalse(player_out in round.matches[1].players)
    
    def test_generate_schedule_with_4_players_and_very_short_names(self):
        league = League(player_names="a, b, c, d")
        schedule = league.generate_schedule(rounds=3)
        self.assertEqual(len(schedule), 3)

        for i, round in enumerate(schedule):
            self.assertEqual(round.number, i+1)
            self.assertEqual(round.number_of_matches(), 1)
        
        round_number = 1
        for round in schedule:
            self.assertEqual(round.number, round_number)
            round_number += 1

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
    
    def test_league_set_invalid_template(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
        with self.assertRaises(ValueError):
            league.set_template("invalid-template")
    
    def test_league_get_player_rankings(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
        league.set_scoring_system(ScoringSystem.SCORE)
        league.generate_schedule(rounds=2)
        
        league.schedule[0].matches[0].set_score([11, 0])
        league.schedule[1].matches[0].set_score([11, 0])

        match_winner_team_players = []
        match_winner_team_players.extend(league.schedule[0].matches[0].get_winner_team_players())
        match_winner_team_players.extend(league.schedule[1].matches[0].get_winner_team_players())

        scores = {
            "GC": 0,
            "Juliano": 0,
            "Fariba": 0,
            "Galina": 0
        }

        for player in match_winner_team_players:
            scores[player.name] += 11

        scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        rankings = league.get_player_rankings()
        self.assertEqual(len(rankings), 4)
        self.assertEqual(rankings[0]["name"], scores[0][0])
        self.assertEqual(rankings[1]["name"], scores[1][0])
        self.assertEqual(rankings[2]["name"], scores[2][0])
        self.assertEqual(rankings[3]["name"], scores[3][0])

    def test_league_set_owner(self):
        league = League(player_names="GC, Juliano, Fariba, Galina")
        user = User("123", "test@test.com")
        league.set_owner(user)
        self.assertEqual(league.owner, user)

    def test_league_to_object(self):
        player_names="GC, Juliano, Fariba, Galina"
        league = League(name="Test League", player_names=player_names)
        league.generate_schedule(rounds=1)
        league.set_template("irina-fariba")
        
        generated_league_object = league.to_object()
        league_object = {
            "id": league.id,
            "name": "Test League",
            "date_created": league.date_created,
            "players": [ {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}],
            "schedule": [
                {
                    "number": 1,
                    "matches": [
                        {"players": [
                            {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}
                        ]}
                    ],
                    "players_out": []
                }
            ], "scoring_system": "none", "template": "irina-fariba"
        }
        
        self.assertEqual(generated_league_object["id"], league_object["id"])
        self.assertEqual(generated_league_object["name"], league_object["name"])
        self.assertEqual(generated_league_object["date_created"], league_object["date_created"])
        self.assertEqual(generated_league_object["players"], league_object["players"])
        
        self.assertEqual(generated_league_object["schedule"][0]["number"], league_object["schedule"][0]["number"])
        self.assertEqual(generated_league_object["schedule"][0]["players_out"], league_object["schedule"][0]["players_out"])

        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][0]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][1]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][2]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][3]["name"] in player_names.split(", "))

        self.assertEqual(generated_league_object["scoring_system"], league_object["scoring_system"])
        self.assertEqual(generated_league_object["template"], league_object["template"])
    
    def test_league_to_object_with_owner(self):
        player_names="GC, Juliano, Fariba, Galina"
        league = League(name="Test League", player_names=player_names)
        league.generate_schedule(rounds=1)
        league.set_template("irina-fariba")
        user = User("123", "test@test.com")
        league.set_owner(user)
        
        generated_league_object = league.to_object()
        league_object = {
            "id": league.id,
            "name": "Test League",
            "date_created": league.date_created,
            "owner": {
                "id": user.id
            },
            "players": [ {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}],
            "schedule": [
                {
                    "number": 1,
                    "matches": [
                        {"players": [
                            {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}
                        ]}
                    ],
                    "players_out": []
                }
            ], "scoring_system": "none", "template": "irina-fariba"
        }
        
        self.assertEqual(generated_league_object["id"], league_object["id"])
        self.assertEqual(generated_league_object["name"], league_object["name"])
        self.assertEqual(generated_league_object["date_created"], league_object["date_created"])
        self.assertEqual(generated_league_object["players"], league_object["players"])
        
        self.assertEqual(generated_league_object["schedule"][0]["number"], league_object["schedule"][0]["number"])
        self.assertEqual(generated_league_object["schedule"][0]["players_out"], league_object["schedule"][0]["players_out"])

        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][0]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][1]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][2]["name"] in player_names.split(", "))
        self.assertTrue(generated_league_object["schedule"][0]["matches"][0]["players"][3]["name"] in player_names.split(", "))

        self.assertEqual(generated_league_object["scoring_system"], league_object["scoring_system"])
        self.assertEqual(generated_league_object["template"], league_object["template"])

        self.assertEqual(generated_league_object["owner"]["id"], league_object["owner"]["id"])
    
    def test_league_from_object(self):
        league = League.from_object({
            "id": "123",
            "name": "Test League",
            "date_created": "2025-03-16 12:00:00",
            "players": [ {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}, {"name": "Aline"}],
            "schedule": [
                {
                    "number": 1,
                    "matches": [
                        {"players": [{"name": "Juliano"}, {"name": "Galina"}, {"name": "GC"}, {"name": "Fariba"}], "score": [0, 0], "winner_team": 0, "scoring_system": "w_l"}
                    ],
                    "players_out": [{"name": "Aline"}]
                }
            ],
            "scoring_system": "w_l",
            "template": "ricky"
        })
        self.assertEqual(league.id, "123")
        self.assertEqual(league.name, "Test League")
        self.assertEqual(league.date_created, "2025-03-16 12:00:00")
        self.assertEqual(len(league.players), 5)
        self.assertEqual(len(league.schedule), 1)
        self.assertEqual(league.schedule[0].number, 1)
        self.assertEqual(len(league.schedule[0].matches), 1)
        self.assertEqual(len(league.schedule[0].players_out), 1)
        self.assertEqual([player.name for player in league.schedule[0].matches[0].players], ["Juliano", "Galina", "GC", "Fariba"])
        self.assertEqual(league.schedule[0].players_out[0].name, "Aline")
        self.assertEqual(league.scoring_system.value, "w_l")
    
    def test_league_from_object_with_owner(self):
        league = League.from_object({
            "id": "123",
            "name": "Test League",
            "date_created": "2025-03-16 12:00:00",
            "owner": {
                "email": "test@test.com"
            },
            "players": [ {"name": "GC"}, {"name": "Juliano"}, {"name": "Fariba"}, {"name": "Galina"}, {"name": "Aline"}],
            "schedule": [
                {
                    "number": 1,
                    "matches": [
                        {"players": [{"name": "Juliano"}, {"name": "Galina"}, {"name": "GC"}, {"name": "Fariba"}], "score": [0, 0], "winner_team": 0, "scoring_system": "w_l"}
                    ],
                    "players_out": [{"name": "Aline"}]
                }
            ],
            "scoring_system": "w_l",
            "template": "ricky"
        })
        self.assertEqual(league.id, "123")
        self.assertEqual(league.name, "Test League")
        self.assertEqual(league.date_created, "2025-03-16 12:00:00")
        self.assertEqual(len(league.players), 5)
        self.assertEqual(len(league.schedule), 1)
        self.assertEqual(league.schedule[0].number, 1)
        self.assertEqual(len(league.schedule[0].matches), 1)
        self.assertEqual(len(league.schedule[0].players_out), 1)
        self.assertEqual([player.name for player in league.schedule[0].matches[0].players], ["Juliano", "Galina", "GC", "Fariba"])
        self.assertEqual(league.schedule[0].players_out[0].name, "Aline")
        self.assertEqual(league.scoring_system.value, "w_l")
        self.assertEqual(league.owner.email, "test@test.com")