from .base import BaseRepository
from app.models import Series

class SeriesRepository(BaseRepository):
    entity_name = "Series"
    model_class = Series

    @classmethod
    def get_series(cls, series_id: str) -> 'Series':
        return cls.get(series_id)
    
    @classmethod
    def save_series(cls, series: 'Series'):
        cls.save(series, series.id)
    
    @classmethod
    def delete_series(cls, series_id: str):
        cls.delete(series_id) 