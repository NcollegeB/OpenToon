# This module provides AI-server logic for Cog page, coordinating authoritative simulation and state
# for Shticker Book pages, settings, and dialogs.

from direct.directnotify import DirectNotifyGlobal


class CogPageManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('CogPageManagerAI')

    def __init__(self, air):
        self.air = air

    def toonKilledCogs(self, toon, suitsKilled, zoneId):
        pass  # TODO

    def toonEncounteredCogs(self, toon, suitsEncountered, zoneId):
        pass  # TODO
