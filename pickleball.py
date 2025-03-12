from itertools import combinations
import random

class League:
    def __init__(self, player_names: str):
        self.players = [player.strip() for player in player_names.split(",")]
        self.schedule = []

    def generate_schedule(self, rounds: int = 7):
        # Reset schedule
        self.schedule = []
        
        # Get all possible combinations of 4 players
        all_possible_games = list(combinations(self.players, 4))
        
        # Shuffle the list of possible games to randomize schedule generation
        random.shuffle(all_possible_games)
        
        # Generate rounds
        for _ in range(rounds):
            round = []
            available_players = set(self.players)
            
            # Keep adding games until we can't add more
            while len(available_players) >= 4:
                # Find a valid game from remaining combinations
                for game in all_possible_games:
                    # Check if all players in this game are still available
                    if all(player in available_players for player in game):
                        round.append(list(game))

                        all_possible_games.remove(game)
                        
                        # Remove used players from available pool
                        for player in game:
                            available_players.remove(player)
                        break
            
            if round:  # Only add non-empty rounds
                self.schedule.append(round)
        
        return self.schedule

    def get_template_data(self):
        return {
            "players": self.players,
            "schedule": self.schedule,
            "width": 80/len(self.players)
        }