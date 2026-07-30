# This module implements the authoritative AI-server side of Cogdo battle bldg, handling validated
# state and synchronized gameplay for Cogdo rooms, activities, entities, and rewards.

from direct.directnotify import DirectNotifyGlobal
from toontown.battle import DistributedBattleBldgAI

class DistributedCogdoBattleBldgAI(DistributedBattleBldgAI.DistributedBattleBldgAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogdoBattleBldgAI')

    def __init__(self, air, zoneId, roundCallback = None, finishCallback = None, maxSuits = 4, bossBattle = 0):
        DistributedBattleBldgAI.DistributedBattleBldgAI.__init__(self, air, zoneId, roundCallback, finishCallback, maxSuits, bossBattle)
