# This module implements the authoritative AI-server side of tag treasure, handling validated state
# and synchronized gameplay for trolley minigame rules, presentation, and synchronization.

from toontown.safezone import DistributedTreasureAI
from direct.distributed.ClockDelta import *

class DistributedTagTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
