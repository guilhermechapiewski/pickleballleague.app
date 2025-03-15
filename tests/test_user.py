import unittest
from app.user import User

class TestUser(unittest.TestCase):
    def test_user(self):
        user = User("123", "test@test.com")
        self.assertEqual(user.google_id, "123")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.get_leagues(), [])

    def test_user_to_object(self):
        user = User("123", "test@test.com")
        user.add_league("456")
        self.assertEqual(user.to_object(), {"google_id": "123", "email": "test@test.com", "league_ids": ["456"]})

    def test_user_from_object(self):
        user = User.from_object({"google_id": "123", "email": "test@test.com", "league_ids": ["456", "789"]})
        self.assertEqual(user.google_id, "123")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.get_leagues(), ["456", "789"])