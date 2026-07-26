from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.fishing import FishingTargetGlobals
from toontown.fishing.DistributedFishingTargetAI import DistributedFishingTargetAI


class DistributedFishingPondAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFishingPondAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.area = 0
        self.targets = {}
        self.spots = {}
        self._targetsGenerated = False

    def delete(self):
        for target in list(self.targets.values()):
            target.requestDelete()
        self.targets.clear()
        self.spots.clear()
        DistributedObjectAI.delete(self)

    def setArea(self, area):
        self.area = area

    def getArea(self):
        return self.area

    def generateTargets(self):
        if self._targetsGenerated:
            return
        self._targetsGenerated = True
        for unused in range(FishingTargetGlobals.getNumTargets(self.area)):
            target = DistributedFishingTargetAI(self.air)
            target.setPondDoId(self.doId)
            target.generateWithRequired(self.zoneId)

    # Historical entry point.
    start = generateTargets

    def addTarget(self, target):
        if target.getPondDoId() != self.doId:
            self.notify.warning('Rejected target %s registered to pond %s.' %
                                (target.doId, target.getPondDoId()))
            return
        self.targets[target.doId] = target

    def removeTarget(self, target):
        if self.targets.get(target.doId) is target:
            del self.targets[target.doId]

    def addSpot(self, spot):
        if spot.getPondDoId() != self.doId:
            self.notify.warning('Rejected spot %s registered to pond %s.' %
                                (spot.doId, spot.getPondDoId()))
            return
        self.spots[spot.doId] = spot

    def removeSpot(self, spot):
        if self.spots.get(spot.doId) is spot:
            del self.spots[spot.doId]

    def hasToon(self, avId):
        fishManager = getattr(self.air, 'fishManager', None)
        if fishManager:
            spot = fishManager.getSpotForAvatar(avId)
            if spot and spot.getPondDoId() == self.doId:
                return spot

        for spot in self.spots.values():
            if spot.avId == avId:
                return spot
        return None

    def hitTarget(self, targetDoId):
        avId = self.air.getAvatarIdFromSender()
        target = self.targets.get(targetDoId)
        if target is None or not target.isActive():
            self.air.writeServerEvent(
                'suspicious',
                avId,
                'Toon tried to hit a nonexistent fishing target.')
            return

        spot = self.hasToon(avId)
        if not spot:
            self.air.writeServerEvent(
                'suspicious',
                avId,
                'Toon tried to catch a fish while not fishing.')
            return

        spot.considerReward(target)
