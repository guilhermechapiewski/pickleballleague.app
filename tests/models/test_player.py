import unittest
from app.models import Player

class TestPlayer(unittest.TestCase):
    def test_player(self):
        player = Player("John")
        self.assertEqual(player.name, "John")
    
    def test_player_comparison(self):
        player1 = Player("Amanda")
        player2 = Player("GC")
        self.assertTrue(player1 < player2)
        self.assertFalse(player1 > player2)
        self.assertFalse(player1 == player2)
    
    def test_player_to_object(self):
        player = Player("John")
        self.assertEqual(player.to_object(), {"name": "John"})
    
    def test_player_from_object(self):
        player = Player.from_object({"name": "John"})
        self.assertEqual(player.name, "John")
    
    def test_player_name_can_only_contain_letters_numbers_and_spaces(self):
        Player("John Doe")
        Player("John Doe 2")
        Player("GC")
        with self.assertRaises(ValueError):
            Player("John, Doe")
        with self.assertRaises(ValueError):
            Player("John-Doe")
        with self.assertRaises(ValueError):
            Player("S.B")
        with self.assertRaises(ValueError):
            Player("S.B.")
        with self.assertRaises(ValueError):
            Player("S.B. 2")