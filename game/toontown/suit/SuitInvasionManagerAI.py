# This module provides AI-server logic for suit invasion, coordinating authoritative simulation and
# state for Cog and boss actors, behavior, and combat support.

from direct.directnotify import DirectNotifyGlobal

class SuitInvasionManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitInvasionManagerAI')

    def __init__(self, air):
        self.air = air

    def getInvadingCog(self):
        return None, 0

    def getInvading(self):
        return False
