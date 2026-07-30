# This module represents a server-side gag-shop interior by storing and exposing its zone and
# building-block identifiers.

from direct.distributed import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal

class DistributedGagshopInteriorAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, block, air, zoneId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.block = block
        self.zoneId = zoneId

    def getZoneIdAndBlock(self):
        r = [
         self.zoneId, self.block]
        return r
