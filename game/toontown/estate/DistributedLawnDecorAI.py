# This module implements the authoritative AI-server side of lawn decor, handling validated state
# and synchronized gameplay for estates, houses, gardens, mailboxes, closets, and banks.

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedLawnDecorAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedLawnDecorAI')
