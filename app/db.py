import os
import logging
from app.pickleball import League
from app.user import User
from google.cloud import datastore

DEV_ENVIRONMENT = os.environ.get("DEV_ENVIRONMENT") == "true"

class LeagueRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_league(cls, league_id: str) -> 'League':
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Getting league {league_id}")
            if league_id in cls.stored_objects:
                return League.from_object(cls.stored_objects[league_id])
            else:
                return None
        else:
            client = datastore.Client()
            key = client.key("League", league_id)
            league = client.get(key)
            if league:
                return League.from_object(league)
            else:
                return None
    
    @classmethod
    def save_league(cls, league: 'League'):
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Saving league {league.id}")
            cls.stored_objects[league.id] = league.to_object()
        else:
            client = datastore.Client()
            complete_key = client.key("League", league.id)
            persistent_league = datastore.Entity(key=complete_key)
            persistent_league.update(league.to_object())
            client.put(persistent_league)
    
    @classmethod
    def delete_league(cls, league_id: str):
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Deleting league {league_id}")
            del cls.stored_objects[league_id]
        else:
            client = datastore.Client()
            client.delete(client.key("League", league_id))
            
class UserRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_user(cls, email: str) -> 'User':
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Getting user {email}")
            if email in cls.stored_objects:
                return User.from_object(cls.stored_objects[email])
            else:
                return None
        else:
            client = datastore.Client()
            key = client.key("User", email)
            user = client.get(key)
            if user:
                return User.from_object(user)
            else:
                return None
            
    
    @classmethod
    def save_user(cls, user: 'User'):
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Saving user {user.email}")
            cls.stored_objects[user.email] = user.to_object()
        else:
            client = datastore.Client()
            complete_key = client.key("User", user.email)
            persistent_user = datastore.Entity(key=complete_key)
            persistent_user.update(user.to_object())
            client.put(persistent_user)
