# This module implements the authoritative AI-server side of fishing spot, handling validated state
# and synchronized gameplay for playgrounds, treasures, and safe-zone activities.

import math

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task
from panda3d.core import ClockObject

from toontown.fishing import FishGlobals
from toontown.fishing import FishingTargetGlobals
from toontown.toonbase import ToontownGlobals


class DistributedFishingSpotAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFishingSpotAI')
    vZeroMax = 25.0
    angleMax = 30.0
    gravity = 32.2
    bobStartY = 3.0
    bobStartZ = 8.5
    targetHitTolerance = 4.0

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.pondDoId = 0
        self.posHpr = [0, 0, 0, 0, 0, 0]
        self.avId = None
        self.cast = False
        self.castPower = 0.0
        self.castHeading = 0.0
        self.castStartTime = 0.0
        self.lastFish = [FishGlobals.Nothing, 0, 0, 0]

    def generate(self):
        DistributedObjectAI.generate(self)
        pond = self.air.doId2do.get(self.pondDoId)
        if pond:
            pond.addSpot(self)
        else:
            self.notify.warning('Fishing spot %s generated without pond %s.' %
                                (self.doId, self.pondDoId))

    def delete(self):
        self._clearTasks()
        if self.avId is not None:
            self._releaseAvatar(sendUpdate=False)
        pond = self.air.doId2do.get(self.pondDoId)
        if pond:
            pond.removeSpot(self)
        DistributedObjectAI.delete(self)

    def setPondDoId(self, pondDoId):
        self.pondDoId = pondDoId

    def getPondDoId(self):
        return self.pondDoId

    def setPosHpr(self, x, y, z, h, p, r):
        self.posHpr = [x, y, z, h, p, r]

    def getPosHpr(self):
        return self.posHpr

    def setOccupied(self, avId):
        self.avId = avId or None

    def d_setOccupied(self, avId):
        self.sendUpdate('setOccupied', [avId])

    def b_setOccupied(self, avId):
        self.setOccupied(avId)
        self.d_setOccupied(avId)

    def _taskName(self, suffix):
        return self.uniqueName('fishing-%s' % suffix)

    def _clearTasks(self):
        taskMgr.remove(self._taskName('cancel-movie'))
        taskMgr.remove(self._taskName('timeout'))
        taskMgr.remove(self._taskName('remove'))

    def _resetTimeout(self):
        taskMgr.remove(self._taskName('timeout'))
        taskMgr.doMethodLater(
            FishGlobals.CastTimeout + 2.5,
            self.removeFromFishingSpotWithAnim,
            self._taskName('timeout'))

    def _cancelMovieLater(self):
        taskMgr.remove(self._taskName('cancel-movie'))
        taskMgr.doMethodLater(
            2.0,
            self._cancelMovie,
            self._taskName('cancel-movie'))

    def _cancelMovie(self, task):
        if self.avId is not None:
            self.d_setMovie(FishGlobals.NoMovie, 0, 0, 0, 0, 0, 0)
        return Task.done

    def _writeSuspicious(self, avId, message):
        self.air.writeServerEvent('suspicious', avId, message)
        self.notify.warning(message)

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
            return

        if self.avId is not None:
            if self.avId == avId:
                self._writeSuspicious(avId, 'Toon requested to enter a fishing spot twice.')
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
            return

        if getattr(av, 'zoneId', self.zoneId) != self.zoneId:
            self._writeSuspicious(avId, 'Toon requested a fishing spot from another zone.')
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
            return

        if getattr(av, 'hp', 1) <= 0:
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
            return

        if not self.air.fishManager.claimSpot(avId, self):
            self._writeSuspicious(avId, 'Toon requested a second fishing spot.')
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
            return

        self.acceptOnce(
            self.air.getAvatarExitEvent(avId),
            self._handleUnexpectedExit)
        self.b_setOccupied(avId)
        self.cast = False
        self.lastFish = [FishGlobals.Nothing, 0, 0, 0]
        self.d_setMovie(FishGlobals.EnterMovie, 0, 0, 0, 0, 0, 0)
        self._cancelMovieLater()
        self._resetTimeout()

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        if self.avId != avId:
            self._writeSuspicious(
                avId,
                "Toon requested to exit a fishing spot they are not using.")
            return

        self.ignore(self.air.getAvatarExitEvent(avId))
        self.removeFromFishingSpotWithAnim()

    def doCast(self, power, heading):
        avId = self.air.getAvatarIdFromSender()
        if self.avId != avId:
            self._writeSuspicious(
                avId,
                "Toon tried to cast from a fishing spot they are not using.")
            return

        av = self.air.doId2do.get(avId)
        if not av:
            self._releaseAvatar()
            return

        if self.cast:
            self._writeSuspicious(avId, 'Toon tried to cast twice before collecting a catch.')
            return

        if (not math.isfinite(power) or not math.isfinite(heading) or
                power < 0.0 or power > 1.0 or
                heading < -360.0 or heading > 360.0):
            self._writeSuspicious(avId, 'Toon sent invalid fishing cast parameters.')
            return

        rodId = av.getFishingRod()
        if rodId < 0 or rodId > FishGlobals.MaxRodId:
            self._writeSuspicious(avId, 'Toon tried to cast with an invalid fishing rod.')
            return

        cost = FishGlobals.getCastCost(rodId)
        if av.getMoney() < cost:
            self._writeSuspicious(avId, 'Toon tried to cast without enough jellybeans.')
            return

        if len(av.fishTank) >= av.getMaxFishTank():
            self._writeSuspicious(avId, 'Toon tried to cast with a full fish tank.')
            return

        if not av.takeMoney(cost, False):
            self._writeSuspicious(avId, 'Fishing cast payment failed.')
            return

        self.cast = True
        self.castPower = power
        self.castHeading = heading
        self.castStartTime = ClockObject.getGlobalClock().getRealTime()
        self.d_setMovie(FishGlobals.CastMovie, 0, 0, 0, 0, power, heading)
        self._cancelMovieLater()
        self._resetTimeout()

    def sellFish(self):
        avId = self.air.getAvatarIdFromSender()
        if self.avId != avId:
            self._writeSuspicious(
                avId,
                "Toon tried to sell fish at a fishing spot they are not using.")
            return

        pond = self.air.doId2do.get(self.pondDoId)
        if not pond or pond.getArea() != ToontownGlobals.MyEstate:
            self._writeSuspicious(
                avId,
                'Toon tried to sell fish outside their estate pond.')
            return

        av = self.air.doId2do.get(avId)
        if not av:
            self._releaseAvatar()
            return

        trophyResult = self.air.fishManager.creditFishTank(av)
        self.sendUpdateToAvatarId(
            avId,
            'sellFishComplete',
            [int(trophyResult), len(av.fishCollection)])
        self._resetTimeout()

    def sellFishComplete(self, trophyResult, numFishCaught):
        # Client response field; the AI initiates this update.
        pass

    def setMovie(self, mode, code, itemDesc1, itemDesc2, itemDesc3, power, heading):
        # Broadcast-only state; retained for DC completeness.
        pass

    def d_setMovie(self, mode, code, itemDesc1, itemDesc2, itemDesc3, power, heading):
        self.sendUpdate(
            'setMovie',
            [mode, code, itemDesc1, itemDesc2, itemDesc3, power, heading])

    def _getCastLanding(self):
        pond = self.air.doId2do.get(self.pondDoId)
        if not pond:
            return None

        spotX, spotY, spotZ, spotH, unusedP, unusedR = self.posHpr
        waterLevel = FishingTargetGlobals.getWaterLevel(pond.getArea())
        velocity = self.castPower * self.vZeroMax
        elevation = math.radians(self.castPower * self.angleMax)
        verticalVelocity = velocity * math.sin(elevation)
        heightAboveWater = spotZ + self.bobStartZ - waterLevel
        discriminant = (
            verticalVelocity * verticalVelocity +
            2.0 * self.gravity * heightAboveWater)
        if discriminant < 0.0:
            return None

        flightTime = (
            verticalVelocity + math.sqrt(discriminant)) / self.gravity
        forwardDistance = (
            self.bobStartY +
            velocity * math.cos(elevation) * flightTime)
        worldHeading = math.radians(spotH + self.castHeading)
        landingX = spotX - math.sin(worldHeading) * forwardDistance
        landingY = spotY + math.cos(worldHeading) * forwardDistance
        return landingX, landingY, waterLevel, flightTime

    def _isTargetInRange(self, target):
        landing = self._getCastLanding()
        if landing is None:
            return False

        landingX, landingY, unusedZ, flightTime = landing
        preFlightDelay = 0.2 + 0.3 * self.castPower
        elapsed = (
            ClockObject.getGlobalClock().getRealTime() -
            self.castStartTime)
        if elapsed + 0.25 < preFlightDelay + flightTime:
            return False

        targetX, targetY, unusedTargetZ = target.getExpectedPosition()
        deltaX = targetX - landingX
        deltaY = targetY - landingY
        return (
            deltaX * deltaX + deltaY * deltaY <=
            self.targetHitTolerance * self.targetHitTolerance)

    def considerReward(self, target):
        if not self.cast or self.avId is None:
            self._writeSuspicious(
                self.avId or 0,
                'Toon tried to collect a fishing target without a pending cast.')
            return False

        pond = self.air.doId2do.get(self.pondDoId)
        av = self.air.doId2do.get(self.avId)
        if not pond or not av or target.getPondDoId() != self.pondDoId:
            self._writeSuspicious(
                self.avId,
                'Toon tried to collect a fishing target from another pond.')
            return False

        if not self._isTargetInRange(target):
            self._writeSuspicious(
                self.avId,
                'Toon reported a fishing target outside the cast landing area.')
            return False

        catch = self.air.fishManager.generateCatch(av, pond.getArea())
        self.lastFish = catch
        self.cast = False
        self.castStartTime = 0.0
        self.d_setMovie(
            FishGlobals.PullInMovie,
            catch[0], catch[1], catch[2], catch[3], 0, 0)
        self._resetTimeout()
        return True

    # Historical name used by some server forks.
    rewardIfValid = considerReward

    def _handleUnexpectedExit(self, *args):
        self._releaseAvatar()

    def _releaseAvatar(self, sendUpdate=True):
        avId = self.avId
        if avId is None:
            return

        self._clearTasks()
        self.ignore(self.air.getAvatarExitEvent(avId))
        self.air.fishManager.releaseSpot(avId, self)
        self.cast = False
        self.castPower = 0.0
        self.castHeading = 0.0
        self.castStartTime = 0.0
        self.setOccupied(0)
        if sendUpdate:
            self.d_setMovie(FishGlobals.NoMovie, 0, 0, 0, 0, 0, 0)
            self.d_setOccupied(0)

    def removeFromFishingSpot(self, task=None):
        self._releaseAvatar()
        if task is not None:
            return Task.done

    # Historical name retained for compatibility.
    removeFromPier = removeFromFishingSpot

    def removeFromFishingSpotWithAnim(self, task=None):
        if self.avId is not None:
            self.cast = False
            taskMgr.remove(self._taskName('cancel-movie'))
            taskMgr.remove(self._taskName('timeout'))
            self.d_setMovie(FishGlobals.ExitMovie, 0, 0, 0, 0, 0, 0)
            taskMgr.doMethodLater(
                1.5,
                self.removeFromFishingSpot,
                self._taskName('remove'))
        if task is not None:
            return Task.done

    # Historical name retained for compatibility.
    removeFromPierWithAnim = removeFromFishingSpotWithAnim
