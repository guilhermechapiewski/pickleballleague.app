class Player:
    def __init__(self, name: str):
        if name is None or len(name) == 0:
            raise ValueError("Player name cannot be empty")
        # Only allow letters, numbers and spaces in player names
        if not all(c.isalnum() or c.isspace() for c in name):
            raise ValueError("Player name can only contain letters, numbers and spaces")
        self.name = name

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other_player):
        return self.name < other_player.name
    
    def __gt__(self, other_player):
        return self.name > other_player.name
    
    def __le__(self, other_player):
        return self.name <= other_player.name
    
    def __ge__(self, other_player):
        return self.name >= other_player.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other_player):
        return self.name == other_player.name
    
    def to_object(self):
        return {"name": self.name}
    
    @staticmethod
    def from_object(object: dict):
        return Player(object["name"])