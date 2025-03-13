from itertools import combinations
import random
import math
import uuid

class Player:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other_player):
        return self.name < other_player.name
    
    def to_object(self):
        return {"name": self.name}

class Game:
    def __init__(self, players: list[Player]):
        if len(players) != 4:
            raise ValueError("Game must have 4 players")
        self.players = players
    
    def __str__(self):
        return f"{self.players[0]}/{self.players[1]} vs. {self.players[2]}/{self.players[3]}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other_game):
        this_game_sides = set()
        this_game_sides.add(tuple(sorted(self.players[:2])))
        this_game_sides.add(tuple(sorted(self.players[2:])))
        other_game_sides = set()
        other_game_sides.add(tuple(sorted(other_game.players[:2])))
        other_game_sides.add(tuple(sorted(other_game.players[2:])))
        return this_game_sides == other_game_sides
    
    def to_object(self):
        return {"players": [player.to_object() for player in self.players]}

class LeagueRound:
    def __init__(self, number: int, games: list[Game], players_out: list[Player]):
        self.number = number
        self.games = games
        self.players_out = players_out
    
    def number_of_games(self):
        return len(self.games)
    
    def add_player_out(self, player: Player):
        self.players_out.append(player)
    
    def __str__(self):
        return f"Round {self.number}: {', '.join([str(game.players) for game in self.games])}"
    
    def to_object(self):
        return {
            "number": self.number,
            "games": [game.to_object() for game in self.games],
            "players_out": [player.to_object() for player in self.players_out]
        }

class League:
    def __init__(self, name: str="", player_names: list[str]=[]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.players = [Player(player.strip()) for player in player_names.split(",")] if player_names else []
        self.schedule = []

    def reset_schedule(self):
        self.schedule = []
    
    def add_round(self, round: LeagueRound):
        self.schedule.append(round)

    def calculate_max_possible_unique_pairs(self):
        n = len(self.players)
        if n < 4:
            return 0
        r = 2
        return math.factorial(n) // (math.factorial(r) * math.factorial(n-r))
    
    def generate_schedule(self, rounds: int=7):
        max_unique_pairs = self.calculate_max_possible_unique_pairs()
        if rounds > max_unique_pairs:
            raise ValueError(f"This number of rounds is not possible with the current number of players.")

        # Reset schedule
        self.reset_schedule()

        while len(self.schedule) != rounds:
            # Get all possible combinations of 4 players
            all_possible_players_combinations = list(combinations(self.players, 4))
            
            # Shuffle the list of possible games to randomize schedule generation
            random.shuffle(all_possible_players_combinations)
            
            # Generate rounds
            for i in range(rounds):
                round_games = []
                remaining_available_players = set(self.players)
                
                # Keep adding games until we can't add more
                while len(remaining_available_players) >= 4:
                    # If we run out of possible combinations, start over
                    if len(all_possible_players_combinations) == 0:
                        all_possible_players_combinations = list(combinations(self.players, 4))
                        random.shuffle(all_possible_players_combinations)
                    
                    # Find a valid game from remaining combinations
                    for players_combination in all_possible_players_combinations:
                        # Check if all players in this game are still available
                        if all(player in remaining_available_players for player in players_combination):
                            players = list(players_combination)
                            random.shuffle(players)
                            round_games.append(Game(players))

                            all_possible_players_combinations.remove(players_combination)
                            
                            # Remove used players from available pool
                            for player in players_combination:
                                remaining_available_players.remove(player)
                            break
                
                # Only add non-empty rounds
                if round_games:
                    # if the round has only one game, and that game is already in the schedule, skip this round
                    if len(round_games) == 1 and round_games[0] in [round.games[0] for round in self.schedule]:
                        continue
                        
                    self.add_round(LeagueRound(i + 1, round_games, remaining_available_players))
        
        return self.schedule
    
    def to_object(self):
        return {
            "id": self.id,
            "name": self.name,
            "players": [player.to_object() for player in self.players],
            "schedule": [round.to_object() for round in self.schedule]
        }