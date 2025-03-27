import os
import logging
from app.pickleball import League, Series
from app.user import User
from app.links import ShortLink
from google.cloud import datastore

DEV_ENVIRONMENT = os.environ.get("DEV_ENVIRONMENT") == "true"

class DevLocalDB:
    directory = "_dev_database/"
    logger = logging.getLogger(__name__)

    @classmethod
    def save_object(cls, type: type, identifier: str, object: str):
        filename = f"{type.__qualname__}_{identifier}.txt"
        cls.logger.info(f"DEV MEMORY DB: Saving object {filename}")
        os.makedirs(cls.directory, exist_ok=True)
        with open(cls.directory + filename, "wb") as f:
            f.write(str(object).encode('utf-8'))
    
    @classmethod
    def get_object(cls, type: type, identifier: str):
        filename = f"{type.__qualname__}_{identifier}.txt"
        cls.logger.info(f"DEV MEMORY DB: Getting object {filename}")
        try:
            with open(cls.directory + filename, "rb") as f:
                return eval(f.read().decode('utf-8'))
        except FileNotFoundError:
            return None
    
    @classmethod
    def delete_object(cls, type: type, identifier: str):
        filename = f"{type.__qualname__}_{identifier}.txt"
        try:
            os.remove(cls.directory + filename)
        except FileNotFoundError:
            cls.logger.info(f"DEV MEMORY DB: Object {filename} not found")
    
    @classmethod
    def clear_db(cls):
        if os.path.exists(cls.directory):
            for filename in os.listdir(cls.directory):
                os.remove(os.path.join(cls.directory, filename))
            os.rmdir(cls.directory)

class LeagueRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_league(cls, league_id: str) -> 'League':
        if DEV_ENVIRONMENT:
            league = DevLocalDB.get_object(League, league_id)
            if league:
                return League.from_object(league)
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
        league.refresh_version()
        if DEV_ENVIRONMENT:
            DevLocalDB.save_object(League, league.id, league.to_object())
        else:
            client = datastore.Client()
            complete_key = client.key("League", league.id)
            persistent_league = datastore.Entity(key=complete_key)
            persistent_league.update(league.to_object())
            client.put(persistent_league)
    
    @classmethod
    def delete_league(cls, league_id: str):
        if DEV_ENVIRONMENT:
            DevLocalDB.delete_object(League, league_id)
        else:
            client = datastore.Client()
            client.delete(client.key("League", league_id))

class SeriesRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_series(cls, series_id: str) -> 'Series':
        if DEV_ENVIRONMENT:
            series = DevLocalDB.get_object(Series, series_id)
            if series:
                return Series.from_object(series)
            else:
                return None
        else:
            client = datastore.Client()
            key = client.key("Series", series_id)
            series = client.get(key)
            if series:
                return Series.from_object(series)
            else:
                return None
    
    @classmethod
    def save_series(cls, series: 'Series'):
        if DEV_ENVIRONMENT:
            DevLocalDB.save_object(Series, series.id, series.to_object())
        else:
            client = datastore.Client()
            complete_key = client.key("Series", series.id)
            persistent_series = datastore.Entity(key=complete_key)
            persistent_series.update(series.to_object())
            client.put(persistent_series)
    
    @classmethod
    def delete_series(cls, series_id: str):
        if DEV_ENVIRONMENT:
            DevLocalDB.delete_object(Series, series_id)
        else:
            client = datastore.Client()
            client.delete(client.key("Series", series_id))

class UserRepository:
    logger = logging.getLogger(__name__)
    stored_objects = {}

    @classmethod
    def get_user(cls, email: str) -> 'User':
        if DEV_ENVIRONMENT:
            user = DevLocalDB.get_object(User, email)
            if user:
                return User.from_object(user)
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
            DevLocalDB.save_object(User, user.email, user.to_object())
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
            short_link = DevLocalDB.get_object(ShortLink, link)
            if short_link:
                return ShortLink.from_object(short_link)
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
            DevLocalDB.save_object(ShortLink, short_link.link, short_link.to_object())
        else:
            client = datastore.Client()
            complete_key = client.key("ShortLink", short_link.link)
            persistent_short_link = datastore.Entity(key=complete_key)
            persistent_short_link.update(short_link.to_object())
            client.put(persistent_short_link)
