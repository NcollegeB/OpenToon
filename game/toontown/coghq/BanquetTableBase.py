# This module provides shared banquet table behavior and data used by related implementations in Cog
# HQ facilities, bosses, rooms, and level entities.

class BanquetTableBase:
    HUNGRY = 1
    DEAD = 0
    EATING = 2
    ANGRY = 3
    HIDDEN = 4
    INACTIVE = 5
