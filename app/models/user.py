import uuid

class User:
    def __init__(self, email: str="", google_id: str=""):
        self.id = str(uuid.uuid4())
        self.google_id = google_id
        self.email = email
        self.league_ids = []
        self.series_ids = []
    
    def add_league(self, league_id: str):
        self.league_ids.append(league_id)

    def get_leagues(self):
        return self.league_ids
    
    def remove_league(self, league_id: str):
        self.league_ids.remove(league_id)

    def add_series(self, series_id: str):
        self.series_ids.append(series_id)

    def get_series(self):
        return self.series_ids
    
    def remove_series(self, series_id: str):
        self.series_ids.remove(series_id)
    
    def to_object(self):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "email": self.email,
            "league_ids": self.league_ids,
            "series_ids": self.series_ids
        }

    @staticmethod
    def from_object(object: dict):
        user = User()
        user.id = object["id"] if "id" in object else ""
        user.google_id = object["google_id"] if "google_id" in object else ""
        user.email = object["email"]
        if "league_ids" in object and object["league_ids"] is not None:
            for league_id in object["league_ids"]:
                user.add_league(league_id)
        if "series_ids" in object and object["series_ids"] is not None:
            for series_id in object["series_ids"]:
                user.add_series(series_id)
        return user
