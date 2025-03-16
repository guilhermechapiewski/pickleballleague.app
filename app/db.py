import os
import logging
from app.pickleball import League
from app.user import User
from app.links import ShortLink
from google.cloud import datastore

DEV_ENVIRONMENT = os.environ.get("DEV_ENVIRONMENT") == "true"

class LeagueRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_league(cls, league_id: str) -> 'League':
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Getting league {league_id}")
            if league_id in cls.stored_objects.keys():
                league = League.from_object(cls.stored_objects[league_id])
                cls.logger.info(f"DEV MEMORY DB: Retrieved league: {league}")
                return league
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
            if email in cls.stored_objects.keys():
                user = User.from_object(cls.stored_objects[email])
                cls.logger.info(f"DEV MEMORY DB: Retrieved user: {user}")
                return user
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

class ShortLinkRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_short_link(cls, link: str) -> 'ShortLink':
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Getting short link {link}")
            if link in cls.stored_objects.keys():
                short_link = ShortLink.from_object(cls.stored_objects[link])
                cls.logger.info(f"DEV MEMORY DB: Retrieved short link: {short_link}")
                return short_link
            else:
                return None
        else:
            client = datastore.Client()
            key = client.key("ShortLink", link)
            short_link = client.get(key)
            if short_link:
                return ShortLink.from_object(short_link)
            else:
                return None
    
    @classmethod
    def save_short_link(cls, short_link: 'ShortLink'):
        if DEV_ENVIRONMENT:
            cls.logger.info(f"DEV MEMORY DB: Saving short link {short_link.link}")
            cls.stored_objects[short_link.link] = short_link.to_object()
        else:
            client = datastore.Client()
            complete_key = client.key("ShortLink", short_link.link)
            persistent_short_link = datastore.Entity(key=complete_key)
            persistent_short_link.update(short_link.to_object())
            client.put(persistent_short_link)
