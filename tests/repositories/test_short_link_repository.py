import unittest
from app.repositories import LeagueRepository, UserRepository, ShortLinkRepository, DevLocalDB, SeriesRepository, SeriesShortLinkRepository
from app.models import League, Series, ShortLink, SeriesShortLink, User

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

class TestSeriesShortLinkRepository(unittest.TestCase):
    def test_save_and_get_short_link(self):
        self.assertIsNone(SeriesShortLinkRepository.get_short_link("short-link-url"))

        short_link = SeriesShortLink(link="short-link-url", destination_link="123-abc-456")
        SeriesShortLinkRepository.save_short_link(short_link)

        retrieved_short_link = SeriesShortLinkRepository.get_short_link("short-link-url")
        self.assertEqual(retrieved_short_link.link, "short-link-url")
        self.assertEqual(retrieved_short_link.destination_link, "123-abc-456")

    def test_get_short_link_that_does_not_exist(self):
        short_link = SeriesShortLinkRepository.get_short_link("non-existent-id")
        self.assertIsNone(short_link)