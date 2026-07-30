# This module defines shared constants, configuration values, and lookup tables for pattern game
# within trolley minigame rules, presentation, and synchronization.

from . import MinigameGlobals
INITIAL_ROUND_LENGTH = 2
ROUND_LENGTH_INCREMENT = 2
NUM_ROUNDS = 4
TOONTOWN_WORK = 1
InputTime = 10
ClientsReadyTimeout = 5 + MinigameGlobals.latencyTolerance
InputTimeout = InputTime + MinigameGlobals.latencyTolerance
