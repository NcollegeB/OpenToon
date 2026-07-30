# This module implements the authoritative AI-server side of e flying treasure, handling validated
# state and synchronized gameplay for playgrounds, treasures, and safe-zone activities.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedEFlyingTreasureAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedEFlyingTreasureAI')
