# This module implements the authoritative AI-server side of NPC flippy in Toon hall, handling
# validated state and synchronized gameplay for player Toon avatars, NPCs, inventory, and
# presentation.

from .DistributedNPCToonAI import *

class DistributedNPCFlippyInToonHallAI(DistributedNPCToonAI):

    def __init__(self, air, npcId, questCallback = None, hq = 0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
