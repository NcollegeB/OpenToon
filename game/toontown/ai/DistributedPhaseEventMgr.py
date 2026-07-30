# This module implements the client-side distributed phase event, handling network updates,
# presentation, and player interaction for district startup, holidays, events, and shared AI
# managers.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
import datetime

class DistributedPhaseEventMgr(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPhaseEventMgr')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.holidayDates = []

    def setIsRunning(self, isRunning):
        self.isRunning = isRunning

    def setNumPhases(self, numPhases):
        self.numPhases = numPhases

    def setCurPhase(self, curPhase):
        self.curPhase = curPhase

    def getIsRunning(self):
        return self.isRunning

    def getNumPhases(self):
        return self.numPhases

    def getCurPhase(self):
        return self.curPhase

    def setDates(self, holidayDates):
        for holidayDate in holidayDates:
            self.holidayDates.append(datetime.datetime(holidayDate[0], holidayDate[1], holidayDate[2], holidayDate[3], holidayDate[4], holidayDate[5]))
