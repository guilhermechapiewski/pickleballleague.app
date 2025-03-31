import unittest
from app.repositories import UserRepository
from app.models import User
    
class TestUserRepository(unittest.TestCase):
    def test_save_and_get_user(self):
        user = User(google_id="123", email="test@test.com")
        user_id = user.id

        UserRepository.save_user(user)
        
        retrieved_user = UserRepository.get_user("test@test.com")

        print(retrieved_user.to_object())

        self.assertEqual(retrieved_user.id, user_id)
        self.assertEqual(retrieved_user.google_id, "123")
        self.assertEqual(retrieved_user.email, "test@test.com")

    def test_save_and_get_user_with_leagues(self):
        user = User(google_id="123", email="test@test.com")
        user_id = user.id
        user.add_league("123-abc-456")
        user.add_league("456-def-789")

        UserRepository.save_user(user)
        
        retrieved_user = UserRepository.get_user("test@test.com")

        print(retrieved_user.to_object())

        self.assertEqual(retrieved_user.id, user_id)
        self.assertEqual(retrieved_user.google_id, "123")
        self.assertEqual(retrieved_user.email, "test@test.com")
        self.assertEqual(retrieved_user.league_ids, ["123-abc-456", "456-def-789"])

    def test_save_and_get_user_with_series(self):
        user = User(google_id="123", email="test@test.com")
        user_id = user.id
        user.add_series("123-abc-456")
        user.add_series("456-def-789")

        UserRepository.save_user(user)
        
        retrieved_user = UserRepository.get_user("test@test.com")

        print(retrieved_user.to_object())

        self.assertEqual(retrieved_user.id, user_id)
        self.assertEqual(retrieved_user.google_id, "123")
        self.assertEqual(retrieved_user.email, "test@test.com")
        self.assertEqual(retrieved_user.series_ids, ["123-abc-456", "456-def-789"])

    def test_get_user_that_does_not_exist(self):
        user = UserRepository.get_user("non-existent-id")
        self.assertIsNone(user)