# This module implements the authoritative AI-server side of Donald's Dreamland treasure, handling
# validated state and synchronized gameplay for playgrounds, treasures, and safe-zone activities.

from . import DistributedSZTreasureAI

class DistributedDLTreasureAI(DistributedSZTreasureAI.DistributedSZTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedSZTreasureAI.DistributedSZTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
