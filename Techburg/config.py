# Techburg/config.py
"""
Central configuration file for the Techburg Simulation.
Tune all game balance and parameters from here.
"""

# --- Grid & UI ---
GRID_WIDTH = 40
GRID_HEIGHT = 30
CELL_SIZE = 20
SIMULATION_SPEED_MS = 150  # Delay in milliseconds per tick (higher is slower)

# --- Entity Counts ---
NUM_PARTS = 50
NUM_STATIONS = 5
NUM_DRONES = 5
NUM_SWARMS = 4
NUM_GATHERERS = 6
NUM_REPAIR_BOTS = 3

# --- Survivor Bot Parameters ---
BOT_BASE_ENERGY = 200
BOT_ENERGY_DEPLETION_RATE = 0.1
BOT_RECHARGE_THRESHOLD = 0.5  # Seek energy when below 50%
BOT_THREAT_DETECTION_RADIUS = 6
ENHANCEMENT_DECAY_RATE = 0.1

# --- Recharge Station Parameters ---
STATION_CAPACITY = 5
GATHERER_CREATION_CHANCE = 0.002  # 0.2% chance per tick
REPAIRER_CREATION_CHANCE = 0.001  # 0.1% chance per tick
BOT_CREATION_ENERGY_COST = 50

# --- Spare Part Parameters ---
PART_CORROSION_RATE = 0.999  # Loses 0.1% of value per tick
PART_DISPOSAL_THRESHOLD = 1.0 # Becomes useless below 1% value

# --- Drone Parameters ---
DRONE_MAX_ENERGY = 500
DRONE_ENERGY_DEPLETION_MOVE = 0.5
DRONE_VISION_RANGE = 12
DRONE_SHOCK_DAMAGE = 30
DRONE_DISABLE_DAMAGE = 60

# --- Swarm Parameters ---
SWARM_DECAY_FIELD_RADIUS = 1.5
SWARM_ENERGY_DRAIN_PERCENT = 0.03 # Drains 3% of max energy
SWARM_REPLICATION_CHANCE = 0.02
SWARM_REPLICATION_THRESHOLD = 8