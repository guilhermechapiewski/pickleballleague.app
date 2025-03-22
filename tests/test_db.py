import unittest
from app.db import LeagueRepository, UserRepository, ShortLinkRepository, DevLocalDB, SeriesRepository
from app.pickleball import League, Series
from app.user import User
from app.links import ShortLink

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

class TestLeagueRepository(unittest.TestCase):
    def test_save_and_get_league(self):
        league_name = "Test League"
        league_player_names = "John, Jane, Jim, Jill"
        league = League(name=league_name, player_names=league_player_names)
        league_id = league.id

        LeagueRepository.save_league(league)
        
        retrieved_league = LeagueRepository.get_league(league_id)

        self.assertEqual(retrieved_league.name, league_name)
        for player in retrieved_league.players:
            self.assertTrue(player.name in league_player_names.split(", "))
    
    def test_get_league_that_does_not_exist(self):
        league = LeagueRepository.get_league("non-existent-id")
        self.assertIsNone(league)
    
    def test_delete_league(self):
        league = League(name="Test League", player_names="John, Jane, Jim, Jill")
        user = User(google_id="123", email="test@test.com")
        user.add_league(league.id)
        league.owner = user
        LeagueRepository.save_league(league)
        UserRepository.save_user(user)

        retrieved_league = LeagueRepository.get_league(league.id)
        retrieved_user = UserRepository.get_user(user.email)

        self.assertEqual(retrieved_league.name, league.name)
        self.assertEqual(retrieved_league.owner.email, user.email)
        self.assertEqual(retrieved_user.league_ids, [league.id])

        LeagueRepository.delete_league(league.id)

        retrieved_deleted_league = LeagueRepository.get_league(league.id)
        self.assertIsNone(retrieved_deleted_league)

class TestSeriesRepository(unittest.TestCase):
    def test_save_and_get_series(self):
        series_name = "Test Series"
        series = Series(name=series_name)
        series_id = series.id

        SeriesRepository.save_series(series)
        
        retrieved_series = SeriesRepository.get_series(series_id)

        self.assertEqual(retrieved_series.name, series_name)
        self.assertEqual(retrieved_series.league_ids, [])
        self.assertEqual(retrieved_series.scoring_system.value, "score")
    
    def test_get_series_that_does_not_exist(self):
        series = SeriesRepository.get_series("non-existent-id")
        self.assertIsNone(series)
    
    def test_delete_series(self):
        series = Series(name="Test Series")
        user = User(google_id="123", email="test@test.com")
        user.add_series(series.id)
        series.owner = user
        SeriesRepository.save_series(series)
        UserRepository.save_user(user)

        retrieved_series = SeriesRepository.get_series(series.id)
        retrieved_user = UserRepository.get_user(user.email)

        self.assertEqual(retrieved_series.name, series.name)
        self.assertEqual(retrieved_series.owner.email, user.email)
        self.assertEqual(retrieved_user.series_ids, [series.id])

        SeriesRepository.delete_series(series.id)

        retrieved_deleted_series = SeriesRepository.get_series(series.id)
        self.assertIsNone(retrieved_deleted_series)
    
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

class TestShortLinkRepository(unittest.TestCase):
    def test_save_and_get_short_link(self):
        self.assertIsNone(ShortLinkRepository.get_short_link("short-link-url"))

        short_link = ShortLink(link="short-link-url", destination_link="123-abc-456")
        ShortLinkRepository.save_short_link(short_link)

        retrieved_short_link = ShortLinkRepository.get_short_link("short-link-url")
        self.assertEqual(retrieved_short_link.link, "short-link-url")
        self.assertEqual(retrieved_short_link.destination_link, "123-abc-456")

    def test_get_short_link_that_does_not_exist(self):
        short_link = ShortLinkRepository.get_short_link("non-existent-id")
        self.assertIsNone(short_link)
        