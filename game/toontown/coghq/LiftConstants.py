# This module defines shared constants, configuration values, and lookup tables for lift within Cog
# HQ facilities, bosses, rooms, and level entities.

Down = 0
Up = 1

def oppositeState(state):
    if state is Down:
        return Up
    else:
        return Down
