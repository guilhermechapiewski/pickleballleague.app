from app.pickleball import League

class User:
    def __init__(self, google_id: str, email: str):
        self.google_id = google_id
        self.email = email
        self.league_ids = []

    def add_league(self, league_id: str):
        self.league_ids.append(league_id)

    def get_leagues(self):
        return self.league_ids
    
    def to_object(self):
        return {
            "google_id": self.google_id,
            "email": self.email,
            "league_ids": self.league_ids
        }

    @staticmethod
    def from_object(object: dict):
        user = User(object["google_id"], object["email"])
        for league_id in object["league_ids"]:
            user.add_league(league_id)
        return user
