# This module defines the base server-side holiday object, storing the AI repository and holiday
# identifier and exposing start and stop hooks for subclasses.

from direct.directnotify import DirectNotifyGlobal
import random
from direct.task import Task
from toontown.effects import DistributedFireworkShowAI

class HolidayBaseAI:

    def __init__(self, air, holidayId):
        self.air = air
        self.holidayId = holidayId

    def start(self):
        pass

    def stop(self):
        pass
