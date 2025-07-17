import unittest
from Techburg.grid import Grid
from Techburg.agents.survivor_bot import SurvivorBot

class TestGrid(unittest.TestCase):
    def test_initialization(self):
        grid = Grid(30, 20)
        self.assertEqual(grid.width, 30)
        self.assertEqual(grid.height, 20)