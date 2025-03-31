from .base import BaseRepository
from app.models import League

class LeagueRepository(BaseRepository):
    entity_name = "League"
    model_class = League

    @classmethod
    def get_league(cls, league_id: str) -> 'League':
        return cls.get(league_id)
    
    @classmethod
    def save_league(cls, league: 'League'):
        league.refresh_version()
        cls.save(league, league.id)
    
    @classmethod
    def delete_league(cls, league_id: str):
        cls.delete(league_id) 