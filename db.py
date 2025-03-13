from pickleball import League

class LeagueRepository:
    leagues = {}

    @classmethod
    def get_league(cls, league_id: str) -> 'League':
        return cls.leagues[league_id]
    
    @classmethod
    def save_league(cls, league: 'League'):
        cls.leagues[league.id] = league
