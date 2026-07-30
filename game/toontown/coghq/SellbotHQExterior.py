# This module manages the client location lifecycle, state transitions, and interactions for Sellbot
# HQ exterior within Cog HQ facilities, bosses, rooms, and level entities.

from direct.directnotify import DirectNotifyGlobal
from toontown.coghq import CogHQExterior

class SellbotHQExterior(CogHQExterior.CogHQExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('SellbotHQExterior')

    def enter(self, requestStatus):
        CogHQExterior.CogHQExterior.enter(self, requestStatus)
        self.loader.hood.startSky()

    def exit(self):
        self.loader.hood.stopSky()
        CogHQExterior.CogHQExterior.exit(self)
