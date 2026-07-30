# This module provides AI-server logic for holiday, coordinating authoritative simulation and state
# for district startup, holidays, events, and shared AI managers.

from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals


class HolidayManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('HolidayManagerAI')

    def __init__(self, air):
        self.air = air
        self.currentHolidays = {}

    def isHolidayRunning(self, holidayId):
        return holidayId in self.currentHolidays

    def isMoreXpHolidayRunning(self):
        return ToontownGlobals.MORE_XP_HOLIDAY in self.currentHolidays
