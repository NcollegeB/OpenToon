# This module defines two d walk and its supporting behavior for trolley minigame rules,
# presentation, and synchronization.

from .OrthoWalk import *

class TwoDWalk(OrthoWalk):
    notify = DirectNotifyGlobal.directNotify.newCategory('TwoDWalk')
    BROADCAST_POS_TASK = 'TwoDWalkBroadcastPos'

    def doBroadcast(self, task):
        dt = globalClock.getDt()
        self.timeSinceLastPosBroadcast += dt
        if self.timeSinceLastPosBroadcast >= self.broadcastPeriod:
            self.timeSinceLastPosBroadcast = 0
            self.lt.cnode.broadcastPosHprFull()
        return Task.cont
