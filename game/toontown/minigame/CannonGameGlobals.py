# This module defines shared constants, configuration values, and lookup tables for cannon game
# within trolley minigame rules, presentation, and synchronization.

TowerYRange = 200
GameTime = 90
MAX_SCORE = 23
MIN_SCORE = 5
FUSE_TIME = 0.0
CANNON_ROTATION_MIN = -20
CANNON_ROTATION_MAX = 20
CANNON_ROTATION_VEL = 15.0
CANNON_ANGLE_MIN = 10
CANNON_ANGLE_MAX = 85
CANNON_ANGLE_VEL = 15.0

def calcScore(t):
    range = MAX_SCORE - MIN_SCORE
    score = MAX_SCORE - range * (float(t) / GameTime)
    return int(score + 0.5)
