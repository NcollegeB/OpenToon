# This module implements the client-side distributed Cogdo battle bldg, handling network updates,
# presentation, and player interaction for Cogdo rooms, activities, entities, and rewards.

from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer
from toontown.battle import DistributedBattleBldg

class DistributedCogdoBattleBldg(DistributedBattleBldg.DistributedBattleBldg):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogdoBattleBldg')

    def __init__(self, cr):
        DistributedBattleBldg.DistributedBattleBldg.__init__(self, cr)

    def getBossBattleTaunt(self):
        return TTLocalizer.CogdoBattleBldgBossTaunt
