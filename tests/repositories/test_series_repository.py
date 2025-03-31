import unittest
from app.repositories import SeriesRepository, UserRepository
from app.models import Series, User

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