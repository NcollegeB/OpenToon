# This module implements the authoritative AI-server side of mint suit, handling validated state and
# synchronized gameplay for Cog and boss actors, behavior, and combat support.

from toontown.suit import DistributedFactorySuitAI
from direct.directnotify import DirectNotifyGlobal

class DistributedMintSuitAI(DistributedFactorySuitAI.DistributedFactorySuitAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMintSuitAI')

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return self.boss

    def isVirtual(self):
        return 0
