# This module provides the AI-side party-manager stub; it currently rejects party purchases and
# implements no other party logic.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPartyManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyManagerAI')

    def canBuyParties(self):
        return False  # TODO
