import os
import logging
from typing import TypeVar, Type, Optional, Any

T = TypeVar('T')

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

class BaseRepository:
    DEV_ENVIRONMENT = os.environ.get("DEV_ENVIRONMENT") == "true"
    logger = logging.getLogger(__name__)
    entity_name: str = ""
    model_class: Type[T] = None

    @classmethod
    def get(cls, identifier: str) -> Optional[T]:
        if cls.DEV_ENVIRONMENT:
            obj = DevLocalDB.get_object(cls.model_class, identifier)
            if obj:
                return cls.model_class.from_object(obj)
            return None
        else:
            from google.cloud import datastore
            client = datastore.Client()
            key = client.key(cls.entity_name, identifier)
            obj = client.get(key)
            if obj:
                return cls.model_class.from_object(obj)
            return None

    @classmethod
    def save(cls, obj: T, identifier: str):
        if cls.DEV_ENVIRONMENT:
            DevLocalDB.save_object(cls.model_class, identifier, obj.to_object())
        else:
            from google.cloud import datastore
            client = datastore.Client()
            complete_key = client.key(cls.entity_name, identifier)
            persistent_obj = datastore.Entity(key=complete_key)
            persistent_obj.update(obj.to_object())
            client.put(persistent_obj)

    @classmethod
    def delete(cls, identifier: str):
        if cls.DEV_ENVIRONMENT:
            DevLocalDB.delete_object(cls.model_class, identifier)
        else:
            from google.cloud import datastore
            client = datastore.Client()
            client.delete(client.key(cls.entity_name, identifier)) 