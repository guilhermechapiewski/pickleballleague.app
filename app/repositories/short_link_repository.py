from .base import BaseRepository
from app.models import ShortLink, SeriesShortLink

class ShortLinkRepository(BaseRepository):
    entity_name = "ShortLink"
    model_class = ShortLink

    @classmethod
    def get_short_link(cls, short_link: str) -> 'ShortLink':
        return cls.get(short_link)
    
    @classmethod
    def save_short_link(cls, short_link: 'ShortLink'):
        cls.save(short_link, short_link.link)

class SeriesShortLinkRepository(BaseRepository):
    entity_name = "SeriesShortLink"
    model_class = SeriesShortLink

    @classmethod
    def get_short_link(cls, short_link: str) -> 'SeriesShortLink':
        return cls.get(short_link)
    
    @classmethod
    def save_short_link(cls, short_link: 'SeriesShortLink'):
        cls.save(short_link, short_link.link) 