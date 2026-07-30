# This module implements the authoritative AI-server side of anim building, handling validated state
# and synchronized gameplay for buildings, interiors, doors, elevators, and boarding.

from direct.directnotify import DirectNotifyGlobal
from toontown.building import DistributedBuildingAI
from toontown.building import DistributedAnimDoorAI
from toontown.building import DoorTypes

class DistributedAnimBuildingAI(DistributedBuildingAI.DistributedBuildingAI):

    def __init__(self, air, blockNumber, zoneId, trophyMgr):
        DistributedBuildingAI.DistributedBuildingAI.__init__(self, air, blockNumber, zoneId, trophyMgr)

    def createExteriorDoor(self):
        result = DistributedAnimDoorAI.DistributedAnimDoorAI(self.air, self.block, DoorTypes.EXT_ANIM_STANDARD)
        return result
