# This module defines shared constants, configuration values, and lookup tables for diving game
# within trolley minigame rules, presentation, and synchronization.

from toontown.toonbase import ToontownGlobals
ENDLESS_GAME = config.GetBool('endless-maze-game', 0)
NUM_SPAWNERS = 6
GAME_DURATION = 60.0
CollideMask = ToontownGlobals.CatchGameBitmask
