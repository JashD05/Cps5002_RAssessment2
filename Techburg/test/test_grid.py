# Techburg/test_grid.py
import unittest
from grid import Grid
from agents.survivor_bot import SurvivorBot

class TestGrid(unittest.TestCase):

    def setUp(self):
        """Set up a new grid for each test."""
        self.grid = Grid(width=30, height=20)

    def test_grid_initialization(self):
        """Test if the grid is initialized with correct dimensions."""
        self.assertEqual(self.grid.width, 30)
        self.assertEqual(self.grid.height, 20)
        self.assertEqual(len(self.grid.entities), 0)

    def test_add_and_get_entity(self):
        """Test adding and retrieving an entity from the grid."""
        bot = SurvivorBot('test_bot', 5, 10, 100)
        self.grid.add_entity(bot)
        retrieved_entity = self.grid.get_entity(5, 10)
        self.assertIsNotNone(retrieved_entity)
        self.assertEqual(retrieved_entity.bot_id, 'test_bot')

    def test_wrap_around_movement(self):
        """Test the grid's wrap-around logic."""
        bot = SurvivorBot('test_bot', 29, 19, 100)
        self.grid.add_entity(bot)

        # Move right, should wrap to x=0
        self.grid.move_entity(bot, 30, 19)
        self.assertEqual(bot.x, 0)
        self.assertEqual(bot.y, 19)
        
        # Move down, should wrap to y=0
        self.grid.move_entity(bot, 0, 20)
        self.assertEqual(bot.x, 0)
        self.assertEqual(bot.y, 0)

        # Move left, should wrap to x=29
        self.grid.move_entity(bot, -1, 0)
        self.assertEqual(bot.x, 29)
        self.assertEqual(bot.y, 0)

    def test_populate_world(self):
        """Test if the world populates with the correct number of entities."""
        self.grid.populate_world(
            num_parts=10, num_stations=2, num_drones=3,
            num_swarms=2, num_gatherers=4, num_repair_bots=2
        )
        # Total entities = 1 player + 10 + 2 + 3 + 2 + 4 + 2 = 24
        self.assertEqual(len(self.grid.entities), 24)

if __name__ == '__main__':
    unittest.main()