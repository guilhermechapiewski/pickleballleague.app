import os
import logging
from app.pickleball import League
from google.cloud import datastore

class LeagueRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_league(cls, league_id: str) -> 'League':
        if os.environ.get("DEV_ENVIRONMENT") == "true":
            cls.logger.info(f"DEV MEMORY DB: Getting league {league_id}")
            return League.from_object(cls.stored_objects[league_id])
        else:
            client = datastore.Client()
            key = client.key("League", league_id)
            league = client.get(key)
            return League.from_object(league)
    
    @classmethod
    def save_league(cls, league: 'League'):
        if os.environ.get("DEV_ENVIRONMENT") == "true":
            cls.logger.info(f"DEV MEMORY DB: Saving league {league.id}")
            cls.stored_objects[league.id] = league.to_object()
        else:
            client = datastore.Client()
            complete_key = client.key("League", league.id)
            persistent_league = datastore.Entity(key=complete_key)
            persistent_league.update(league.to_object())
            client.put(persistent_league)
