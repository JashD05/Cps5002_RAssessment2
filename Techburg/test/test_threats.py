import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.drone import MalfunctioningDrone

class TestThreats(unittest.TestCase):
    def test_drone_initialization(self):
        drone = MalfunctioningDrone(10, 10)
        self.assertEqual(drone.x, 10)
        self.assertEqual(drone.y, 10)