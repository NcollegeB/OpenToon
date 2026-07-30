# This module implements the authoritative AI-server side of fishing target, handling validated
# state and synchronized gameplay for ponds, fish, targets, rewards, and Bingo.

import math
import random

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.task import Task

from toontown.fishing import FishingTargetGlobals


class DistributedFishingTargetAI(DistributedNodeAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFishingTargetAI')

    def __init__(self, air, randomSource=None):
        DistributedNodeAI.__init__(self, air)
        self.random = randomSource or random
        self.pondDoId = 0
        self.stateIndex = FishingTargetGlobals.OFF
        self.startAngle = 0.0
        self.startRadius = 0.0
        self.angle = 0.0
        self.radius = 0.0
        self.moveTime = FishingTargetGlobals.StepTime
        self.stateTimestamp = globalClockDelta.getRealNetworkTime()
        self.active = False

    def generate(self):
        DistributedNodeAI.generate(self)
        pond = self.air.doId2do.get(self.pondDoId)
        if not pond:
            self.notify.warning('Fishing target %s generated without pond %s.' %
                                (self.doId, self.pondDoId))
            return

        pond.addTarget(self)
        self.active = True
        self._updateState()

    def delete(self):
        self.active = False
        taskMgr.remove(self.uniqueName('fishing-target-move'))
        pond = self.air.doId2do.get(self.pondDoId)
        if pond:
            pond.removeTarget(self)
        DistributedNodeAI.delete(self)

    def setPondDoId(self, pondDoId):
        self.pondDoId = pondDoId

    def getPondDoId(self):
        return self.pondDoId

    def setState(self, stateIndex, angle, radius, moveTime, timestamp):
        self.stateIndex = stateIndex
        self.angle = angle
        self.radius = radius
        self.moveTime = moveTime
        self.stateTimestamp = timestamp

    def getState(self):
        return [
            self.stateIndex,
            self.angle,
            self.radius,
            self.moveTime,
            self.stateTimestamp]

    def d_setState(self, stateIndex, angle, radius, moveTime, timestamp):
        self.sendUpdate(
            'setState',
            [stateIndex, angle, radius, moveTime, timestamp])

    def b_setState(self, stateIndex, angle, radius, moveTime, timestamp):
        self.setState(stateIndex, angle, radius, moveTime, timestamp)
        self.d_setState(stateIndex, angle, radius, moveTime, timestamp)

    def isActive(self):
        return self.active

    def getExpectedPosition(self):
        pond = self.air.doId2do.get(self.pondDoId)
        if not pond:
            return 0.0, 0.0, 0.0

        center = FishingTargetGlobals.getTargetCenter(pond.getArea())
        startX = self.startRadius * math.cos(self.startAngle) + center[0]
        startY = self.startRadius * math.sin(self.startAngle) + center[1]
        endX = self.radius * math.cos(self.angle) + center[0]
        endY = self.radius * math.sin(self.angle) + center[1]
        elapsed = max(
            0.0,
            globalClockDelta.localElapsedTime(self.stateTimestamp))
        if self.moveTime <= 0.0:
            progress = 1.0
        else:
            progress = min(1.0, elapsed / self.moveTime)
        # Panda's easeInOut blend follows a smoothstep curve.
        progress = progress * progress * (3.0 - 2.0 * progress)
        return (
            startX + (endX - startX) * progress,
            startY + (endY - startY) * progress,
            center[2])

    def _updateState(self, task=None):
        pond = self.air.doId2do.get(self.pondDoId)
        if not pond:
            self.active = False
            return Task.done if task is not None else None

        center = FishingTargetGlobals.getTargetCenter(pond.getArea())
        currentX = self.radius * math.cos(self.angle) + center[0]
        currentY = self.radius * math.sin(self.angle) + center[1]
        self.b_setPosHpr(currentX, currentY, center[2], 0, 0, 0)

        maxRadius = FishingTargetGlobals.getTargetRadius(pond.getArea())
        self.startAngle = self.angle
        self.startRadius = self.radius
        angle = self.random.uniform(0.0, math.pi * 2.0)
        radius = self.random.uniform(0.0, maxRadius)
        moveTime = self.random.uniform(5.0, 10.0)
        timestamp = globalClockDelta.getRealNetworkTime()
        self.b_setState(
            FishingTargetGlobals.MOVING,
            angle,
            radius,
            moveTime,
            timestamp)

        delay = moveTime + self.random.uniform(2.5, 5.0)
        taskMgr.doMethodLater(
            delay,
            self._updateState,
            self.uniqueName('fishing-target-move'))
        if task is not None:
            return Task.done
