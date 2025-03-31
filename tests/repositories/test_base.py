import unittest
from app.repositories import DevLocalDB
from app.models import League

class TestDevLocalDB(unittest.TestCase):
    def test_save_and_get_object(self):
        DevLocalDB.save_object(League, "123-abc-456", League(name="Test League", player_names="John, Jane, Jim, Jill").to_object())
        retrieved_league = League.from_object(DevLocalDB.get_object(League, "123-abc-456"))
        self.assertEqual(retrieved_league.name, "Test League")

    def test_delete_object(self):
        DevLocalDB.save_object(League, "123-abc-456", League(name="Test League", player_names="John, Jane, Jim, Jill").to_object())
        DevLocalDB.delete_object(League, "123-abc-456")
        retrieved_league = DevLocalDB.get_object(League, "123-abc-456")
        self.assertIsNone(retrieved_league)

    def test_clear_db(self):
        DevLocalDB.save_object(League, "123-abc-456", League(name="Test League", player_names="John, Jane, Jim, Jill").to_object())
        retrieved_league = DevLocalDB.get_object(League, "123-abc-456")
        self.assertIsNotNone(retrieved_league)
        DevLocalDB.clear_db()
        retrieved_league = DevLocalDB.get_object(League, "123-abc-456")
        self.assertIsNone(retrieved_league)