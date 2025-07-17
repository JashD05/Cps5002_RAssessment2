import unittest
from Techburg.grid import Grid
from Techburg.agents.survivor_bot import SurvivorBot

class TestSurvivorBot(unittest.TestCase):
    def test_initial_state(self):
        bot = SurvivorBot('test_bot', 5, 5, 100)
        self.assertEqual(bot.energy, 100)