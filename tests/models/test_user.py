import unittest
from app.models import User

class TestUser(unittest.TestCase):
    def test_user(self):
        user = User("test@test.com", "123")
        self.assertEqual(user.google_id, "123")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.get_leagues(), [])

    def test_user_to_object(self):
        user = User("test@test.com", "123")
        user.add_league("456")
        user.add_series("789")
        self.assertEqual(user.to_object(), {"id": user.id, "google_id": "123", "email": "test@test.com", "league_ids": ["456"], "series_ids": ["789"]})

    def test_user_from_object(self):
        user = User.from_object({"id": "123-abc-456", "google_id": "123", "email": "test@test.com", "league_ids": ["456", "789"], "series_ids": ["abc-123-456"]})
        self.assertEqual(user.id, "123-abc-456")
        self.assertEqual(user.google_id, "123")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.get_leagues(), ["456", "789"])
        self.assertEqual(user.get_series(), ["abc-123-456"])
    
    def test_user_remove_league(self):
        user = User("test@test.com", "123")
        user.add_league("456")
        user.add_league("789")
        self.assertEqual(user.get_leagues(), ["456", "789"])
        user.remove_league("456")
        self.assertEqual(user.get_leagues(), ["789"])
        user.remove_league("789")
        self.assertEqual(user.get_leagues(), [])

    def test_user_remove_series(self):
        user = User("test@test.com", "123")
        user.add_series("456")
        user.add_series("789") 
        self.assertEqual(user.get_series(), ["456", "789"])
        user.remove_series("456")
        self.assertEqual(user.get_series(), ["789"])
        user.remove_series("789")
        self.assertEqual(user.get_series(), [])
    
    def test_user_add_series(self):
        user = User("test@test.com", "123")
        user.add_series("456")
        self.assertEqual(user.get_series(), ["456"])
        
