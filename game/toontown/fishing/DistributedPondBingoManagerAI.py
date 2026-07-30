# This module implements the authoritative AI-server side of pond Bingo, handling validated state
# and synchronized gameplay for ponds, fish, targets, rewards, and Bingo.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPondBingoManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPondBingoManagerAI')
