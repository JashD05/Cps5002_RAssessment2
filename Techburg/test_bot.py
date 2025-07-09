import unittest
# Assuming your bot classes are in a file named 'agents.py'
# from agents import SurvivorBot, SmallPart 

# Mock classes for testing since we don't have the real ones
class MockPart:
    def __init__(self, value):
        self.value = value
        self.type = 'mock_part'

class SurvivorBot:
    def __init__(self, energy=100):
        self.energy = energy
        self.carrying = None
        self.energy_depletion_rate = 5 # Depletes 5% per move

    def move(self):
        """Simulates the bot moving one step."""
        self.energy -= self.energy_depletion_rate
        if self.energy < 0:
            self.energy = 0
    
    def pickup_part(self, part):
        """Picks up a spare part."""
        if self.carrying is None:
            self.carrying = part
            return True
        return False
        
    def consume_part_for_energy(self):
        """Consumes a carried part to restore energy."""
        if self.carrying:
            self.energy += self.carrying.value
            self.carrying = None


class TestSurvivorBot(unittest.TestCase):
    """
    Test suite for the SurvivorBot class.
    """

    def setUp(self):
        """Set up a new bot before each test."""
        self.bot = SurvivorBot(energy=100)

    def test_initial_energy(self):
        """Test that the bot initializes with the correct energy."""
        self.assertEqual(self.bot.energy, 100)

    def test_movement_depletes_energy(self):
        """Test that a single movement correctly depletes energy."""
        initial_energy = self.bot.energy
        self.bot.move()
        self.assertEqual(self.bot.energy, initial_energy - self.bot.energy_depletion_rate)

    def test_energy_does_not_go_below_zero(self):
        """Test that energy level does not become negative."""
        self.bot.energy = 3 # Less than depletion rate
        self.bot.move()
        self.assertEqual(self.bot.energy, 0)
    
    def test_pickup_part_when_empty_handed(self):
        """Test that the bot can pick up a part when not carrying anything."""
        part = MockPart(value=10)
        can_pick_up = self.bot.pickup_part(part)
        self.assertTrue(can_pick_up)
        self.assertIsNotNone(self.bot.carrying)
        self.assertEqual(self.bot.carrying.value, 10)

    def test_pickup_part_when_already_carrying(self):
        """Test that the bot cannot pick up a part if it's already carrying one."""
        part1 = MockPart(value=10)
        part2 = MockPart(value=20)
        self.bot.pickup_part(part1) # Pick up the first part
        
        can_pick_up_again = self.bot.pickup_part(part2) # Attempt to pick up another
        self.assertFalse(can_pick_up_again)
        self.assertEqual(self.bot.carrying.value, 10) # Should still be carrying the first part

    def test_consuming_part_restores_energy(self):
        """Test that consuming a part restores energy and removes the part."""
        self.bot.energy = 50
        part = MockPart(value=30)
        self.bot.pickup_part(part)
        
        self.bot.consume_part_for_energy()
        self.assertEqual(self.bot.energy, 80)
        self.assertIsNone(self.bot.carrying)


# This allows running the tests directly from the command line
if __name__ == '__main__':
    unittest.main()