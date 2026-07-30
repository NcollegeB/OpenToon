# This module manages the client location lifecycle, state transitions, and interactions for Lawbot
# office exterior within Cog HQ facilities, bosses, rooms, and level entities.

from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toonbase import ToontownGlobals
from toontown.building import Elevator
from panda3d.core import *
from . import FactoryExterior

class LawbotOfficeExterior(FactoryExterior.FactoryExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('LawbotOfficeExterior')

    def enterWalk(self, teleportIn = 0):
        FactoryExterior.FactoryExterior.enterWalk(self, teleportIn)
        self.ignore('teleportQuery')
        base.localAvatar.setTeleportAvailable(0)
