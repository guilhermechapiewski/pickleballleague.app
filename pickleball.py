from itertools import combinations
import random

class Player:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class Game:
    def __init__(self, players: list[Player]):
        if len(players) != 4:
            raise ValueError("Game must have 4 players")
        self.players = players
    
    def __str__(self):
        return f"{self.players[0]}/{self.players[1]} vs. {self.players[2]}/{self.players[3]}"

class LeagueRound:
    def __init__(self, number: int, games: list[Game], players_out: list[Player]):
        self.number = number
        self.games = games
        self.players_out = players_out
    
    def number_of_games(self):
        return len(self.games)
    
    def __str__(self):
        return f"Round {self.number}: {', '.join([str(game.players) for game in self.games])}"

class League:
    def __init__(self, player_names: str):
        self.players = [Player(player.strip()) for player in player_names.split(",")]
        self.schedule = []
    
    def reset_schedule(self):
        self.schedule = []
    
    def add_round(self, round: LeagueRound):
        self.schedule.append(round)

    def generate_schedule(self, rounds: int = 7):
        # Reset schedule
        self.reset_schedule()
        
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
                # Find a valid game from remaining combinations
                for players_combination in all_possible_players_combinations:
                    # Check if all players in this game are still available
                    if all(player in remaining_available_players for player in players_combination):
                        round_games.append(Game(list(players_combination)))

                        all_possible_players_combinations.remove(players_combination)
                        
                        # Remove used players from available pool
                        for player in players_combination:
                            remaining_available_players.remove(player)
                        break
            
            if round_games:  # Only add non-empty rounds
                self.add_round(LeagueRound(i + 1, round_games, remaining_available_players))
        
        return self.schedule

    def get_template_data(self):
        return {
            "players": self.players,
            "schedule": self.schedule,
            "width": 80/len(self.players)
        }