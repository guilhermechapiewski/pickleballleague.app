from .base import BaseRepository
from app.models import User

class UserRepository(BaseRepository):
    entity_name = "User"
    model_class = User

    @classmethod
    def get_user(cls, email: str) -> 'User':
        return cls.get(email)
    
    @classmethod
    def save_user(cls, user: 'User'):
        cls.save(user, user.email) 