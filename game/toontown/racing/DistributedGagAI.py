# This module implements the authoritative AI-server side of gag, handling validated state and
# synchronized gameplay for kart races, tracks, pads, projectiles, scores, and leaderboards.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DistributedGagAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedGagAI')

    def __init__(self, air, ownerId, race, _, x, y, z, gagType):
        DistributedObjectAI.__init__(self, air)
        self.ownerId = ownerId
        self.race = race
        self.pos = (x, y, z)
        self.gagType = gagType
        self.initTime = globalClockDelta.getFrameNetworkTime()
        self.activateTime = 0

    def getInitTime(self):
        return self.initTime

    def getActivateTime(self):
        return self.activateTime

    def getPos(self):
        return self.pos

    def getRace(self):
        return self.race.getDoId()

    def getOwnerId(self):
        return self.ownerId

    def getType(self):
        return self.gagType

    def hitSomebody(self, avId, time):
        self.race.thrownGags.remove(self)
        self.requestDelete()
