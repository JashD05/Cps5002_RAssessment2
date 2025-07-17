# Techburg/test_threats.py
import unittest
from grid import Grid
from agents.survivor_bot import SurvivorBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm

class TestThreats(unittest.TestCase):

    def setUp(self):
        """Set up a grid for threat testing."""
        self.grid = Grid(width=10, height=10)

    def test_drone_movement(self):
        """Test if the drone moves towards a target."""
        drone = MalfunctioningDrone(0, 0)
        bot = SurvivorBot('target_bot', 5, 5, 100)
        self.grid.add_entity(drone)
        self.grid.add_entity(bot)
        
        drone.update(self.grid)
        # Drone should move one step closer to the bot
        self.assertEqual(drone.x, 1)
        self.assertEqual(drone.y, 1)

    def test_drone_attack(self):
        """Test if the drone damages a bot when adjacent."""
        drone = MalfunctioningDrone(5, 6)
        bot = SurvivorBot('target_bot', 5, 5, 100)
        self.grid.add_entity(drone)
        self.grid.add_entity(bot)
        
        initial_energy = bot.energy
        drone.update(self.grid)
        self.assertLess(bot.energy, initial_energy)
        
    def test_swarm_damage_field(self):
        """Test if the swarm's decay field damages a nearby bot."""
        swarm = ScavengerSwarm(5, 5, size=2)
        bot = SurvivorBot('target_bot', 6, 6, 100) # Within range
        self.grid.add_entity(swarm)
        self.grid.add_entity(bot)
        
        initial_energy = bot.energy
        swarm.update(self.grid)
        self.assertLess(bot.energy, initial_energy)

if __name__ == '__main__':
    unittest.main()