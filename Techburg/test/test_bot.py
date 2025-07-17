# Techburg/test_bots.py
import unittest
from grid import Grid
from agents.survivor_bot import SurvivorBot, PlayerBot
from entities import SparePart, RechargeStation

class TestSurvivorBot(unittest.TestCase):

    def setUp(self):
        """Set up a grid and a bot for testing."""
        self.grid = Grid(width=10, height=10)
        self.bot = SurvivorBot('test_bot', 5, 5, 100)
        self.grid.add_entity(self.bot)

    def test_initial_state(self):
        """Test the bot's initial properties."""
        self.assertEqual(self.bot.energy, 100)
        self.assertIsNone(self.bot.carrying_part)
        self.assertIsNone(self.bot.target_entity)

    def test_find_nearest_part(self):
        """Test if the bot correctly identifies the nearest spare part."""
        part1 = SparePart('small', 5, 6) # distance 1
        part2 = SparePart('medium', 0, 0) # distance > 1
        self.grid.add_entity(part1)
        self.grid.add_entity(part2)
        
        self.bot.get_new_goal(self.grid)
        self.assertIsNotNone(self.bot.target_entity)
        self.assertEqual(self.bot.target_entity, part1)

    def test_pickup_part(self):
        """Test if the bot can pick up a part."""
        part = SparePart('small', 5, 5)
        self.grid.add_entity(part)
        
        self.bot.handle_arrival(part, self.grid)
        self.assertIsNotNone(self.bot.carrying_part)
        self.assertEqual(self.bot.carrying_part, part)
        self.assertNotIn(part, self.grid.entities) # Part should be removed from grid

    def test_recharge_at_station(self):
        """Test if the bot recharges its energy at a station."""
        station = RechargeStation(5, 5)
        self.grid.add_entity(station)
        self.bot.energy = 20 # Lower the bot's energy
        
        self.bot.handle_arrival(station, self.grid)
        self.assertEqual(self.bot.energy, self.bot.max_energy)

if __name__ == '__main__':
    unittest.main()