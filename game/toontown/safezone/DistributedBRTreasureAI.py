# This module implements the authoritative AI-server side of Brrrgh treasure, handling validated
# state and synchronized gameplay for playgrounds, treasures, and safe-zone activities.

from . import DistributedSZTreasureAI

class DistributedBRTreasureAI(DistributedSZTreasureAI.DistributedSZTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedSZTreasureAI.DistributedSZTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
